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

ALEXT=$(ls -d ~/.vscode/extensions/ms-dynamics-smb.al-* | sort -V | tail -1)
ALC="$ALEXT/bin/linux/alc"
ANALYZERS="$ALEXT/bin/Analyzers"
if [ -x "$ALC" ]; then
    COMPILER=("$ALC")
elif [ -f "$ALEXT/bin/alc.dll" ] && command -v dotnet >/dev/null 2>&1; then
    COMPILER=(dotnet "$ALEXT/bin/alc.dll")
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

exit "$COMPILE_EXIT"
