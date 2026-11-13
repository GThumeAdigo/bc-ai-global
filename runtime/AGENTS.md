# Business Central development contract

## Where you are

OpenCode starts either in an app folder (it contains `app.json`) or in a
repository root that holds several apps and no `app.json`. In a repository root,
read `REPO_CONTEXT.md` first, then identify the target app from the request. If
it is ambiguous, ask once. Read that app's `APP_CONTEXT.md` and the relevant
product decisions under its `specs/`. Specs, knowledge pages and handoff notes
belong to one app and live in its folder. A change spanning several apps lives in
the spec of the app that owns the main change and names the others. Never create
`specs/` or `APP_CONTEXT.md` at the repository root.

Manifest, ruleset and source own machine facts; do not invent missing app
identity, compatibility or environment details. If `specs/kb/index.md` exists in
the target app, read it and then only the pages the task touches; it describes
current behavior and rules. Search `specs/archive/` only when changing the area
it covers. When a change alters behavior a knowledge page describes, update that
page in the same change.

## Choose the work path

Use `.opencode/skills/sdd/SKILL.md` for implementation routing. Small clear fixes
can use Direct. Bounded behavior changes use Compact SDD. Posting, transaction,
authorization, company/tenant, released-data, public-contract or hot-path changes
need Critical SDD when their behavior is affected. Explain the selection once.
Line count alone does not determine risk. Questions do not need feature artifacts.

Main-session implementation is allowed for small work. Compact and Critical use
the SDD default chain: spec writer, implementer, then one review. Do not add
review rounds beyond the SDD stop rules.
When delegating, verify the actual agent identity using the SDD skill's dispatch
rule. A CLI fallback to the default primary agent is not a subagent result.

## Discover the app and tools

- The session may be rooted in an app or multi-app repository. Discover every
  `app.json` in the relevant workspace, excluding package caches and dependencies.
- Pass explicit absolute app paths to MCP/build tools. Never select the first
  result on an ambiguous workspace. Build dependencies before their consumers.
- Serena paths are relative to its activated workspace; report its 0-based
  locations as 1-based lines. Use semantic symbols/references for AL first.
  Text/file search remains appropriate when semantic tools cannot answer.
- Compile with `.opencode/skills/al-compile/SKILL.md`. Serena diagnostics are
  navigation feedback, not build proof. Capability names do not prove execution.
- Use the selected release's `scripts/doctor` for version/prerequisite evidence.
  Consult Microsoft Learn for uncertain platform behavior and target-version APIs.

## Rules and knowledge

Before authoring AL, read the authoring essentials in
`.opencode/skills/al-code-review/SKILL.md` and applicable style guide sections.
The style guide owns local conventions. BCQuality owns reusable domain guidance.
Do not duplicate either in feature documents. Standard BC reuse precedes custom code.

The corpus `.opencode/BCQuality-ADIGO/` is a read-only selected release snapshot.
Its index is prepared during installation. Follow the exact router and READ/DO
contract for selected specialist actions. If the index or tool is unavailable,
report that fact; do not mutate the shared release or claim a review passed.

## Verification and boundaries

The SDD skill owns review selection, stopping, approvals and test-authoring policy.
Run relevant existing executable checks; writing new tests requires explicit
task/app opt-in. Record actual command results and missing coverage. A recipe
offered but not executed is not a passing test. A build-only request ends with
build evidence; it does not trigger unrelated reviews or documentation.

Preserve user changes, private specs and previous approvals. No commit, push,
merge, deployment or destructive operation without authorization. Use editing
tools for governed documents and read changes back. Do not use stash as backup
for ignored files. Compatibility decisions require a trusted released baseline
when existing data or public consumers must be preserved.

## Installation and state

`.agent-state/install.json` records the selected release and rollback journal.
`.opencode/` sits in the folder where OpenCode starts, an app folder or a
repository root; its managed content links into an immutable release. In a
repository root it stays outside every AL project on purpose, because the corpus
ships `.al` sample code. Never link or copy it into an app folder. Do not edit
through those links. Change the scaffold in its own checkout, test, then
explicitly update this consumer. Private context/specs/docs are app-owned.
Runtime results go under `.agent-state/runs/`, not the shared source. Never
search the repository root for AL source; search inside the target app folders.

Configuration is startup-loaded. Quit and restart OpenCode after an installed
runtime update. Global config/skills can still affect a session; an isolated
worktree alone is not an isolated host. Hunk is optional review presentation,
never a correctness gate or prerequisite for routine work.
