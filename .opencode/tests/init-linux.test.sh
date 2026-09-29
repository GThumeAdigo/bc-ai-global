#!/usr/bin/env bash

set -euo pipefail

readonly REPOSITORY_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)"
readonly INITIALIZER="$REPOSITORY_ROOT/scripts/legacy/init-linux.sh"
readonly FIXTURE_ROOT="$(mktemp -d /tmp/opencode/init-linux-tests.XXXXXX)"

cleanup() {
    rm -rf -- "$FIXTURE_ROOT"
}

trap cleanup EXIT

create_app() {
    local app_root="$1"

    mkdir -p -- "$app_root"
    printf '{}\n' > "$app_root/app.json"
}

assert_initialized() {
    local app_root="$1"

    test -L "$app_root/.opencode"
    test -f "$app_root/APP_CONTEXT.md"
    test -f "$app_root/specs/templates/feature-approvals.md"
    test -f "$app_root/specs/templates/feature-validation.md"
    test -f "$app_root/DOCS/USER_GUIDE.md"
    git -C "$app_root" check-ignore -q APP_CONTEXT.md
    git -C "$app_root" check-ignore -q specs/roadmap.md
    git -C "$app_root" check-ignore -q DOCS/USER_GUIDE.md
}

test_root_app() {
    local app_root="$FIXTURE_ROOT/root-app"

    create_app "$app_root"
    git -C "$app_root" init -q
    "$INITIALIZER" "$app_root"
    assert_initialized "$app_root"
}

test_normal_app() {
    local repository_root="$FIXTURE_ROOT/normal-repository"
    local app_root="$repository_root/main"

    mkdir -p -- "$repository_root"
    git -C "$repository_root" init -q
    create_app "$app_root"
    "$INITIALIZER" "$app_root"
    assert_initialized "$app_root"
}

test_nested_app() {
    local repository_root="$FIXTURE_ROOT/nested-repository"
    local app_root="$repository_root/apps/region/main"

    mkdir -p -- "$repository_root"
    git -C "$repository_root" init -q
    create_app "$app_root"
    "$INITIALIZER" "$app_root"
    assert_initialized "$app_root"
}

test_existing_directories() {
    local app_root="$FIXTURE_ROOT/existing-directories"

    create_app "$app_root"
    git -C "$app_root" init -q
    mkdir -p -- "$app_root/specs/templates" "$app_root/DOCS"
    printf 'local context\n' > "$app_root/APP_CONTEXT.md"
    printf 'local spec\n' > "$app_root/specs/custom.md"
    printf 'local docs\n' > "$app_root/DOCS/custom.md"

    "$INITIALIZER" "$app_root"
    "$INITIALIZER" "$app_root"

    test "$(<"$app_root/APP_CONTEXT.md")" = "local context"
    test "$(<"$app_root/specs/custom.md")" = "local spec"
    test "$(<"$app_root/DOCS/custom.md")" = "local docs"
    assert_initialized "$app_root"
}

test_linked_worktree() {
    local primary_root="$FIXTURE_ROOT/worktree-primary"
    local linked_root="$FIXTURE_ROOT/worktree-linked"
    local app_root="$linked_root/apps/main"
    local exclude_path

    mkdir -p -- "$primary_root"
    git -C "$primary_root" init -q
    git -C "$primary_root" config user.name Fixture
    git -C "$primary_root" config user.email fixture@example.invalid
    printf 'fixture\n' > "$primary_root/tracked.txt"
    git -C "$primary_root" add tracked.txt
    git -C "$primary_root" commit -qm fixture
    git -C "$primary_root" worktree add -q "$linked_root"
    create_app "$app_root"

    "$INITIALIZER" "$app_root"
    assert_initialized "$app_root"

    exclude_path="$(git -C "$app_root" rev-parse --path-format=absolute --git-path info/exclude)"
    test "$exclude_path" = "$(realpath -m -- "$primary_root/.git/info/exclude")"
    test -f "$exclude_path"
}

test_exclusion_failure_is_non_partial() {
    local app_root="$FIXTURE_ROOT/exclusion-failure"
    local exclude_path

    create_app "$app_root"
    git -C "$app_root" init -q
    exclude_path="$(git -C "$app_root" rev-parse --path-format=absolute --git-path info/exclude)"
    printf '# BEGIN bc-ai-global local excludes\n' > "$exclude_path"

    if "$INITIALIZER" "$app_root"; then
        printf 'Initializer unexpectedly accepted malformed exclusions\n' >&2
        return 1
    fi

    test ! -e "$app_root/.opencode"
    test ! -e "$app_root/APP_CONTEXT.md"
    test ! -e "$app_root/specs"
    test ! -e "$app_root/DOCS"
}

test_root_app
test_normal_app
test_nested_app
test_existing_directories
test_linked_worktree
test_exclusion_failure_is_non_partial

printf 'init-linux fixtures passed\n'
