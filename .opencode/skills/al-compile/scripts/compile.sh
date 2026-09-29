#!/usr/bin/env bash
# Compiles one AL app with alc.exe from the installed VS Code AL extension,
# the full house analyzer set, and the repo ruleset. Output (log and .app)
# goes to a fresh temp dir so the repo stays clean.
#
# Usage: compile.sh [app-folder] [ruleset-path]
#   app-folder   folder containing app.json. Optional; discovered from the
#                current directory. Fails if discovery is ambiguous.
#   ruleset-path optional, relative to the current directory. Otherwise use
#                app settings, applicable workspace settings, then ADIGO.

set -u

APP="${1:-}"

if [ -z "$APP" ]; then
    mapfile -t FOUND < <(find . -maxdepth 3 -name app.json -not -path '*/node_modules/*' -not -path '*/.alpackages/*' -exec dirname {} \;)
    if [ "${#FOUND[@]}" -eq 0 ]; then
        echo "error: no app.json found under $(pwd); pass an app folder" >&2
        exit 2
    fi
    if [ "${#FOUND[@]}" -gt 1 ]; then
        echo "error: ambiguous app discovery, pass one app folder explicitly:" >&2
        printf '  %s\n' "${FOUND[@]}" >&2
        exit 2
    fi
    APP="${FOUND[0]}"
fi
if [ ! -d "$APP" ] || [ ! -f "$APP/app.json" ]; then
    echo "error: invalid app folder (requires app.json): $APP" >&2
    exit 2
fi
APP=$(cd -- "$APP" && pwd) || exit 2
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd) || exit 2
RULESET=$(python3 "$SCRIPT_DIR/resolve_ruleset.py" "$APP" "${@:2}") || exit 2

ALEXT="${AL_COMPILER_EXTENSION_PATH:-}"
if [ -z "$ALEXT" ]; then
    ALEXT=$(ls -d ~/.vscode/extensions/ms-dynamics-smb.al-* | sort -V | tail -1)
fi
ALC="$ALEXT/bin/linux/alc"
ANALYZERS="$ALEXT/bin/Analyzers"
if [ -x "$ALC" ]; then
    COMPILER=("$ALC")
    COMPILER_FILE="$ALC"
elif [ -f "$ALEXT/bin/alc.dll" ] && command -v dotnet >/dev/null 2>&1; then
    COMPILER=(dotnet "$ALEXT/bin/alc.dll")
    COMPILER_FILE="$ALEXT/bin/alc.dll"
    ANALYZERS="$ALEXT/bin"
else
    echo "error: no runnable AL compiler found under $ALEXT/bin" >&2
    exit 2
fi

ANALYZER_DLLS=(
    Microsoft.Dynamics.Nav.CodeCop.dll
    Microsoft.Dynamics.Nav.UICop.dll
    Microsoft.Dynamics.Nav.PerTenantExtensionCop.dll
    ALCops.ApplicationCop.dll
    ALCops.DocumentationCop.dll
    ALCops.FormattingCop.dll
    ALCops.LinterCop.dll
    ALCops.PlatformCop.dll
    ALCops.TestAutomationCop.dll
    ALCops.Common.dll
)

if [ -n "${AL_ANALYZER_PROFILE:-}" ]; then
    PROFILE=$(python3 -c 'import json,sys; from pathlib import Path; x=json.load(open(sys.argv[1]))["analyzers"]; assert isinstance(x,list) and x and all(isinstance(n,str) and Path(n).name == n and n.endswith(".dll") for n in x); print("\n".join(x))' "$AL_ANALYZER_PROFILE") || exit 2
    mapfile -t ANALYZER_DLLS <<< "$PROFILE"
fi
ANALYZER_PATHS=()

ARGS=(
    /project:"$APP"
    /packagecachepath:"$APP/.alpackages"
)
for dll in "${ANALYZER_DLLS[@]}"; do
    if [ ! -f "$ANALYZERS/$dll" ]; then
        echo "error: analyzer missing: $ANALYZERS/$dll" >&2
        exit 2
    fi
    ARGS+=("/analyzer:$ANALYZERS/$dll")
    ANALYZER_PATHS+=("$ANALYZERS/$dll")
done

ARGS+=("/ruleset:$RULESET")

OUT=$(mktemp -d /tmp/alcompile.XXXXXX)
APPFILE="$OUT/$(basename "$APP").app"

"${COMPILER[@]}" "${ARGS[@]}" /out:"$APPFILE" > "$OUT/compile.log" 2>&1
COMPILE_EXIT=$?

ERRORS=$(grep -cE ': error' "$OUT/compile.log" || true)
WARNINGS=$(grep -cE ': warning' "$OUT/compile.log" || true)
INFOS=$(grep -cE ': info' "$OUT/compile.log" || true)

echo "app:    $APP"
echo "log:    $OUT/compile.log"
echo "output: $APPFILE"
echo "exit=$COMPILE_EXIT errors=$ERRORS warnings=$WARNINGS infos=$INFOS"

python3 "$SCRIPT_DIR/build_evidence.py" "$APP" "$OUT" "$COMPILER_FILE" "$RULESET" "$COMPILE_EXIT" "${ANALYZER_PATHS[@]}"
EVIDENCE_EXIT=$?
if [ "$COMPILE_EXIT" -eq 0 ] && [ "$EVIDENCE_EXIT" -ne 0 ]; then
    exit "$EVIDENCE_EXIT"
fi

exit "$COMPILE_EXIT"
