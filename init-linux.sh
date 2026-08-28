#!/usr/bin/env bash

set -euo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly EXCLUDE_BLOCK_START="# BEGIN bc-ai-global local excludes"
readonly EXCLUDE_BLOCK_END="# END bc-ai-global local excludes"
readonly -a SCAFFOLD_PATHS=(
    ".opencode"
    "AGENTS.md"
    "CLAUDE.md"
    "opencode.json"
)
readonly -a APP_LOCAL_PATHS=(
    "APP_CONTEXT.md"
    "DOCS"
    "specs"
)

usage() {
    printf 'Usage: %s <AL-app-folder> [<AL-app-folder> ...]\n' "$(basename "$0")"
}

link_scaffold_path() {
    local app_root="$1"
    local scaffold_path="$2"
    local source_path="$SCRIPT_DIR/$scaffold_path"
    local target_path="$app_root/$scaffold_path"

    if [[ -L "$target_path" ]]; then
        if [[ "$(readlink -f -- "$target_path")" == "$source_path" ]]; then
            return
        fi

        printf 'Refusing to replace existing symlink: %s\n' "$target_path" >&2
        return 1
    fi

    if [[ -e "$target_path" ]]; then
        printf 'Refusing to replace existing path: %s\n' "$target_path" >&2
        return 1
    fi

    ln -s -- "$source_path" "$target_path"
}

copy_app_local_path() {
    local app_root="$1"
    local local_path="$2"
    local source_path="$SCRIPT_DIR/$local_path"
    local target_path="$app_root/$local_path"

    if [[ -L "$target_path" ]]; then
        return
    fi

    if [[ -d "$source_path" ]]; then
        mkdir -p -- "$target_path"
        cp -R --no-clobber -- "$source_path"/. "$target_path"/
        return
    fi

    if [[ -e "$target_path" ]]; then
        return
    fi

    cp -- "$source_path" "$target_path"
}

extract_exclude_block() {
    local exclude_path="$1"

    awk -v start="$EXCLUDE_BLOCK_START" -v end="$EXCLUDE_BLOCK_END" '
        $0 == end { inside = 0 }
        inside { print }
        $0 == start { inside = 1 }
    ' "$exclude_path"
}

append_exclude_block() {
    local exclude_path="$1"
    local temporary_path

    temporary_path="$(mktemp "${exclude_path}.XXXXXX")"
    cat -- "$exclude_path" > "$temporary_path"
    printf '\n%s\n' "$EXCLUDE_BLOCK_START" >> "$temporary_path"
    cat -- "$SCRIPT_DIR/exclude" >> "$temporary_path"
    printf '%s\n' "$EXCLUDE_BLOCK_END" >> "$temporary_path"
    mv -- "$temporary_path" "$exclude_path"
}

# Rewrites the block in place, so template changes reach repositories that were
# initialised earlier. Lines outside the markers, and the position of the block
# itself, are preserved.
resync_exclude_block() {
    local exclude_path="$1"
    local temporary_path

    temporary_path="$(mktemp "${exclude_path}.XXXXXX")"
    awk -v start="$EXCLUDE_BLOCK_START" -v end="$EXCLUDE_BLOCK_END" -v template="$SCRIPT_DIR/exclude" '
        $0 == start {
            print
            while ((getline template_line < template) > 0) {
                print template_line
            }
            close(template)
            inside = 1
            next
        }
        $0 == end && inside {
            print
            inside = 0
            next
        }
        inside { next }
        { print }
    ' "$exclude_path" > "$temporary_path" || {
        rm -f -- "$temporary_path"
        return 1
    }
    mv -- "$temporary_path" "$exclude_path"
}

apply_local_excludes() {
    local exclude_path="$1"

    mkdir -p -- "$(dirname -- "$exclude_path")"
    touch -- "$exclude_path"

    if ! grep -Fqx -- "$EXCLUDE_BLOCK_START" "$exclude_path"; then
        append_exclude_block "$exclude_path"
        printf 'Added local excludes to %s\n' "$exclude_path"
        return
    fi

    if ! grep -Fqx -- "$EXCLUDE_BLOCK_END" "$exclude_path"; then
        printf 'Refusing to touch a malformed exclude block (start marker without end marker): %s\n' "$exclude_path" >&2
        return 1
    fi

    if diff -q -- <(extract_exclude_block "$exclude_path") "$SCRIPT_DIR/exclude" > /dev/null; then
        return
    fi

    resync_exclude_block "$exclude_path"
    printf 'Updated local excludes in %s\n' "$exclude_path"
}

initialise_repository() {
    local app_argument="$1"
    local app_root
    local exclude_path
    local repository_root
    local scaffold_path
    local app_local_path

    app_root="$(cd -- "$app_argument" && pwd -P)" || {
        printf 'Not an accessible app folder: %s\n' "$app_argument" >&2
        return 1
    }

    if [[ ! -f "$app_root/app.json" ]]; then
        printf 'No app.json in app folder: %s\n' "$app_root" >&2
        return 1
    fi

    repository_root="$(git -C "$app_root" rev-parse --show-toplevel 2>/dev/null)" || {
        printf 'Not inside a Git repository: %s\n' "$app_root" >&2
        return 1
    }

    exclude_path="$(git -C "$app_root" rev-parse --path-format=absolute --git-path info/exclude 2>/dev/null)" || {
        printf 'Cannot resolve Git exclusion path for: %s\n' "$app_root" >&2
        return 1
    }
    exclude_path="$(realpath -m -- "$exclude_path")"

    apply_local_excludes "$exclude_path"

    for scaffold_path in "${SCAFFOLD_PATHS[@]}"; do
        link_scaffold_path "$app_root" "$scaffold_path"
    done

    for app_local_path in "${APP_LOCAL_PATHS[@]}"; do
        copy_app_local_path "$app_root" "$app_local_path"
    done

    printf 'Initialized %s (Git repository: %s)\n' "$app_root" "$repository_root"
}

if (( $# == 0 )); then
    usage >&2
    exit 1
fi

for app_argument in "$@"; do
    initialise_repository "$app_argument"
done
