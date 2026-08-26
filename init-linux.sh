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

    if [[ -e "$target_path" || -L "$target_path" ]]; then
        return
    fi

    cp -R -- "$source_path" "$target_path"
}

apply_local_excludes() {
    local repository_root="$1"
    local exclude_path="$repository_root/.git/info/exclude"
    local temporary_path

    mkdir -p -- "$(dirname -- "$exclude_path")"
    touch -- "$exclude_path"

    if grep -Fqx -- "$EXCLUDE_BLOCK_START" "$exclude_path"; then
        return
    fi

    temporary_path="$(mktemp "${exclude_path}.XXXXXX")"
    cat "$exclude_path" > "$temporary_path"
    printf '\n%s\n' "$EXCLUDE_BLOCK_START" >> "$temporary_path"
    cat "$SCRIPT_DIR/exclude" >> "$temporary_path"
    printf '%s\n' "$EXCLUDE_BLOCK_END" >> "$temporary_path"
    mv -- "$temporary_path" "$exclude_path"
}

initialise_repository() {
    local app_argument="$1"
    local app_root
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

    for scaffold_path in "${SCAFFOLD_PATHS[@]}"; do
        link_scaffold_path "$app_root" "$scaffold_path"
    done

    for app_local_path in "${APP_LOCAL_PATHS[@]}"; do
        copy_app_local_path "$app_root" "$app_local_path"
    done

    apply_local_excludes "$repository_root"
    printf 'Initialized %s (Git repository: %s)\n' "$app_root" "$repository_root"
}

if (( $# == 0 )); then
    usage >&2
    exit 1
fi

for app_argument in "$@"; do
    initialise_repository "$app_argument"
done