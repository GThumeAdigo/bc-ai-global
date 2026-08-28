#!/usr/bin/env bash
# Compiles one AL app with alc.exe from the installed VS Code AL extension,
# the full house analyzer set, and the repo ruleset. Output (log and .app)
# goes to a fresh temp dir so the repo stays clean.
#
# Usage: compile.sh [app-folder] [ruleset-path]
#   app-folder   folder containing app.json. Optional; discovered from the
#                current directory. Fails if discovery is ambiguous.
#   ruleset-path optional. Defaults to ../.codeAnalysis/ADIGO.ruleset.json
#                relative to the app folder, then falls back to al.ruleSetPath
#                in a sibling .code-workspace file.

set -u

APP="${1:-}"
RULESET="${2:-}"

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
APP=$(cd "$APP" && pwd)

ALEXT=$(ls -d ~/.vscode/extensions/ms-dynamics-smb.al-* | sort -V | tail -1)
ALC="$ALEXT/bin/linux/alc"
ANALYZERS="$ALEXT/bin/Analyzers"
if [ ! -x "$ALC" ]; then
    echo "error: alc not found at $ALC" >&2
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

if [ -z "$RULESET" ]; then
    DEFAULT_RULESET="$APP/../.codeAnalysis/ADIGO.ruleset.json"
    if [ -f "$DEFAULT_RULESET" ]; then
        RULESET="$DEFAULT_RULESET"
    else
        WORKSPACE=$(find "$APP/.." -maxdepth 1 -name '*.code-workspace' | head -1)
        if [ -n "$WORKSPACE" ]; then
            RULESET=$(grep -oE '"al\.ruleSetPath"\s*:\s*"[^"]+"' "$WORKSPACE" | head -1 | sed 's/.*:\s*"//; s/"$//')
            [ -n "$RULESET" ] && RULESET=$(cd "$APP" && realpath -m "$RULESET")
        fi
    fi
fi
if [ -n "$RULESET" ] && [ -f "$RULESET" ]; then
    ARGS+=("/ruleset:$RULESET")
else
    echo "note: no ruleset found, compiling without one" >&2
fi

OUT=$(mktemp -d /tmp/alcompile.XXXXXX)
APPFILE="$OUT/$(basename "$APP").app"

"$ALC" "${ARGS[@]}" /out:"$APPFILE" > "$OUT/compile.log" 2>&1
COMPILE_EXIT=$?

ERRORS=$(grep -cE ': error' "$OUT/compile.log" || true)
WARNINGS=$(grep -cE ': warning' "$OUT/compile.log" || true)
INFOS=$(grep -cE ': info' "$OUT/compile.log" || true)

echo "app:    $APP"
echo "log:    $OUT/compile.log"
echo "output: $APPFILE"
echo "exit=$COMPILE_EXIT errors=$ERRORS warnings=$WARNINGS infos=$INFOS"

exit "$COMPILE_EXIT"
