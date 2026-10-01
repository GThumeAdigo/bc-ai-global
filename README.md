# ADIGO agentic Business Central development

A shared OpenCode/Linux scaffold for risk-adaptive AL development. SDD preserves
product intent; executable checks provide verification; independent reviewers
focus on the risks of the actual change. This remains a prototype until its
product-task comparison and live pilot are completed.

## Work paths

| Work | Path |
|---|---|
| Clear bounded fix to existing behavior, no affected critical invariant | Direct implementation and applicable checks |
| Bounded new behavior in known architecture | Compact spec, one approval, checks and one independent change review |
| Posting, transactions, effective permissions, company/tenant boundaries, released data, public contracts or broad performance impact | Critical intent/design and scoped independent risk review |

The authority is [the SDD skill](.opencode/skills/sdd/SKILL.md), including
approval, test-authoring policy, review confirmations and stopping. Few changed
lines do not imply low risk. Main-session implementation is allowed.

## Source versus installed content

- `AGENTS.md`, `opencode.json`: this scaffold's maintainer environment, not an AL app.
- `runtime/`: consumer bootstrap, configuration template and model policy.
- `templates/`: blank app context, product specs and optional guide starter.
- `.opencode/agents`, `.opencode/skills`, `.opencode/commands`: maintained native
  adapters and domain/workflow entry points.
- `.opencode/BCQuality-ADIGO`: separately versioned corpus submodule.
- `scripts/`: install/rollback, capability doctor and infrastructure verification.
- `plans/`: maintainer decisions and redacted evidence, never copied into apps.

Installed `.opencode/` is a real app-local directory. Its managed content links
into an immutable release selected by commit. Host package artifacts are local.
App results, install metadata and browser state live under `.agent-state/`.
Editing the source repo no longer updates new-style consumers automatically.

## Prerequisites

- Linux, Git, Python 3.12+ and PyYAML. Node 24+ for infrastructure tests.
- OpenCode; configuration and host smoke tests were run with 1.18.33.
- For AL work: the app's symbols, compiler/analyzers, ruleset and dependency chain.
  Install the appropriate Microsoft AL extension or ALTool separately.
- Serena must be on PATH for the default semantic-navigation integration.
- Optional npm MCPs use explicit versions in `runtime/opencode.json`.

Initialize the corpus and a local development environment in this source clone:

```bash
git submodule update --init
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

No script installs credentials or modifies user-wide OpenCode/Claude settings.
Compiler availability does not imply a functioning BC test environment.

## Install into an app

Use an AL app folder containing `app.json`, including for multi-app repositories:

```bash
.venv/bin/python scripts/install /path/to/repository/MyApp \
  --revision <scaffold-commit> --dry-run
.venv/bin/python scripts/install /path/to/repository/MyApp \
  --revision <scaffold-commit>
```

`init-linux.sh <app>...` remains a forwarding entry point when `python3` has the
required dependencies. Install uses committed source, not uncommitted edits.
Dry-run validates targets and can populate the release cache, but changes no app.

Release storage defaults to `$XDG_DATA_HOME/bc-ai-global/releases/<commit>`
(or `~/.local/share/...`). `--store` overrides it. The selected Git revision and
submodule content are exported, the corpus generates its knowledge index, and
the snapshot is made read-only and checksummed. Reuse checks its integrity.

The installer preflights all supplied apps before changing them. Unmanaged paths
or modified managed files cause refusal. It preserves existing app context,
specs and docs, adding only missing templates. It never follows a template target
symlink into another checkout. `.agent-state/install.json` records ownership and
the rollback journal. Updates of existing installs are intentionally one app at
a time; initial multi-app installs are supported.

Optional profiles:

```bash
.venv/bin/python scripts/install /path/to/MyApp --revision <commit> \
  --profile translation --profile browser
```

Profiles `dependency` and `analyzer-fixes` expose the additional symbol-package
and ALCops MCPs. They remain available without loading them into every session.
The core profile enables AL MCP, Microsoft Learn and Serena. The AL MCP launcher
takes explicit project paths, never an arbitrary first discovered app. Set
`ALTOOL_PATH` to a selected executable or DLL to override the global `al` command.
Use a pinned environment for reproducible comparisons.

Workspace output is optional with `--workspace /path/to/repo/main.code-workspace`.
The source must be at the repo root. JSONC is accepted, settings are preserved,
and a stable app-path hash avoids basename collisions. Unmanaged or edited output
is not overwritten. Without this flag no workspace file is generated.

Fill relevant `APP_CONTEXT.md` fields and product decisions, then start OpenCode
**from the installed app folder**. Run `/sdd <request>` or describe the change.
The app contract and SDD skill determine the path. Quit and restart OpenCode
after updating its installed runtime; running sessions retain old configuration.

`/sdd` coordinates in the current primary conversation (`build` or `plan`) and
preserves its permissions. With no arguments it asks for the task. Feature IDs,
descriptions and explicit stage requests such as `/sdd plan <id>` are accepted;
a stage request is not permission to execute the entire workflow.

Specialist agents remain subagents. Use a Task dispatch, an `@agent-name` request
or a native review command targeting that subagent. A command's `agent:` field
can invoke a child task; this differs from `opencode run --agent <subagent>`,
which is not a reliable way to select a specialist as the CLI primary agent.

## Existing consumers and rollback

Old apps linked to a mutable source directory stay on that directory. Changing
its branch still changes them, so develop migrations in a separate checkout.
The installer will not replace a whole-directory `.opencode` link without
`--migrate-legacy`. First test this option in an authorized clone, not a live app.

Before mutation, private app artifacts are backed up under
`$XDG_STATE_HOME/bc-ai-global/backups` (or `~/.local/state/...`), configurable with
`--backup-root`. These local backups do not replace off-machine backups.

```bash
.venv/bin/python scripts/install /path/to/MyApp --rollback
```

Rollback restores the previous managed state only if current content still
matches installer ownership. It refuses to discard user edits or extra runtime
artifacts. Private specs/docs and backups are retained. Single-app transactions
also restore their captured excludes; a batch install retains shared exclusions
on individual rollback to protect the other apps. An existing legacy exclude
block is left intact because it may protect unregistered consumers.

New excludes target managed files; they do not hide all PNG or XSD files. A
legacy block may still contain such broad patterns. Remove it only after checking
every old consumer it protects. Worktrees can share `.git/info/exclude`.

Legacy features with old five-file approvals stay on their baseline workflow.
New specs declare `workflow: risk-adaptive-v2`; no old approval is automatically
relabelled. The `/al-*` gate names and old templates remain compatibility surfaces,
not the default entry path for new work. Keep the original runtime available to
finish old features, or explicitly migrate their intent/evidence with the owner.

## Verification

```bash
.venv/bin/python scripts/verify-scaffold
.venv/bin/python scripts/check-config opencode.json runtime/opencode.json
.venv/bin/python scripts/smoke-install --revision <committed-candidate> --host
python3 scripts/doctor --altool /path/to/altool.dll --probe-mcp
```

The aggregate command runs hash/approval/installation/reference fixtures, compiler
wrapper fixtures, and retained legacy-hook/installer tests. The old hook is under
`.opencode/legacy`, not auto-loaded. These tests do not execute AL business logic.
Schema validation reports a schema digest; pass `--schema <saved-json>` for an
offline comparison. Model availability is checked separately from JSON validity.

Smoke installation uses temporary apps, release/backup roots and an isolated
HOME/XDG environment. It verifies two-app installation/update/rollback, native
agent/model configuration and exclusion of an external sentinel skill. Host debug
output is captured through a regular temporary file because the tested OpenCode
version can truncate large pipe output. This is a loader test, not a paid model
run or proof of every tool's runtime permission enforcement.

The doctor distinguishes available, unavailable and untested capabilities. MCP
probes only initialize/list tools and do not publish or run product tests. It
does not infer that a listed tool works on the app. ALTool 17 and the installed
extension's ALTool 18 have different capabilities; retain tested fallbacks until
replacement parity is established.

For actual AL builds, follow [al-compile](.opencode/skills/al-compile/SKILL.md).
`AL_COMPILER_EXTENSION_PATH` and `AL_ANALYZER_PROFILE` select inputs explicitly.
The wrapper emits JSON/log evidence and supports isolated diagnostic baseline
comparison. Consumer CI parity must be established from that app's configuration.

## Knowledge and conventions

The [house overlay](.opencode/skills/al-code-review/SKILL.md) selects relevant
sections of [the style guide](.opencode/skills/al-code-review/styleguide.md).
App architecture is not inferred from generic IDataAccess examples. The SDD
workflow classifies concrete defects separately from advisory preferences.

BCQuality is pinned to the `GThumeAdigo/BCQuality-ADIGO` fork. Its Microsoft layer
originates from `microsoft/BCQuality`; custom action skills remain maintained in
the fork. Update there, then bump the scaffold submodule. Never edit installed
or vendored guidance in place. Exact entry routing selects an action; it does
not execute its review. The corpus owns READ/DO output and index generation.
Use corpus-relative references for knowledge findings and separate house reports.
AL examples remain `*.al.txt` to avoid entering consumer compilations.

Model IDs/variants for installed agents come from `runtime/model-policy.json`.
Prompt frontmatter contains no model pins. The first candidate preserves the
baseline agent model/variant; model changes are a separate experiment.

Hunk notes are optional presentation at a useful stable checkpoint. They are not
a completion gate. Browser verification remains explicit and uses app-local state.
Claude Code currently receives a context bridge only; full harness parity is not
claimed.

## Migration evidence

- [Approved plan](plans/2026-09-29-agent-workflows.md)
- [Implementation and executed checks](plans/agent-workflows-implementation.md)

Product comparisons require authorized task/base refs, environments and a run
budget. No measured speed, cost or reliability improvement is claimed from the
infrastructure fixtures alone. No live consumer is migrated by these tests.
