# ADIGO agentic Business Central development

A shared OpenCode/Linux scaffold for risk-adaptive AL development. SDD preserves
product intent; executable checks provide verification; independent reviewers
focus on the risks of the actual change. This remains a prototype until its
product-task comparison and live pilot are completed.

## Work paths

| Work | Path |
|---|---|
| Clear bounded fix to existing behavior, no affected critical invariant | Direct implementation and applicable checks |
| Bounded new behavior in known architecture | Compact spec (one file), one approval, implementer, checks and one review-and-fix pass |
| Posting, transactions, effective permissions, company/tenant boundaries, released data, public contracts or broad performance impact | Critical spec and plan, design review, implementer and one independent read-only review |

The authority is [the SDD skill](.opencode/skills/sdd/SKILL.md), including
approval, test-authoring policy and stopping. Few changed lines do not imply low
risk. The review budget is one review pass and one repair pass per checkpoint.
Default chain: `al-spec-writer` (Opus), `custom-al-implementer` (Sonnet, reads
the style guide first), then `al-review-fixer` (Compact: fixes behavior-neutral
defects itself) or `al-change-reviewer` (Critical: read-only). Main-session
implementation is allowed for small work.

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

## Runbook: set up a repository yourself

One-time, in this scaffold clone: `git submodule update --init`, then the venv
commands above (only needed for the tests, not for installing).

For each repository (a folder with several apps and no `app.json`, or a single app):

1. **Check the target.** Commit or stash your own work first; the installer only
   writes local files, but you want a clean `git status` to compare against.
   If the root already has an `AGENTS.md`, `CLAUDE.md` or `opencode.json` of your
   own, move its content into `REPO_CONTEXT.md` (after step 3) and rename or
   remove the old files. The installer refuses to overwrite them.
2. **Dry run**, then install. `--dry-run` also lists the apps it found:

   ```bash
   cd /path/to/bc-ai-global          # must be committed; HEAD is installed
   python3 scripts/install /path/to/Repo --dry-run
   python3 scripts/install /path/to/Repo --profile translation   # profiles optional
   ```

   If an app below the root already carries an older app-level install, add
   `--replace-app-installs`. Back up specs outside Git first (`specs/` is local only).
3. **Fill the context files.** `REPO_CONTEXT.md` at the root (apps, build order,
   CI, shared rules) and `APP_CONTEXT.md` in each app you will work on. Leave the
   other apps' templates blank until needed.
4. **Verify.** `git status` in the repository must stay clean (all installed files
   are locally excluded). Open the workspace in VS Code and check the Problems
   panel for errors from `.opencode`. Start OpenCode at the repository root and run
   `/sdd <request>`.
5. **Update later.** Commit your scaffold change, run the same `install` command
   again for each repository (one at a time), repeat the profiles you use, and
   restart OpenCode. `--rollback` returns a repository to its previous install.

Things that need your decision rather than the script: which profiles to enable,
`ALTOOL_PATH` if the global `al` command is not the one you want, and whether a
repository keeps its own `.serena/` project (it is excluded either way).

## Install into a repository or an app

Preferred: install at a **repository root that holds several apps** and has no
`app.json` itself (for example `ADIGO-Apps`, `ITS.IT-Services`). The runtime
(`.opencode/`, `AGENTS.md`, `opencode.json`, the knowledge corpus) then lies
outside every AL project, so the AL extension never compiles the corpus' `.al`
samples. OpenCode is started at the repository root; the agent picks the target
app per task. Apps are found below the root (depth 4, nested apps are not split);
each gets its own `APP_CONTEXT.md`, `specs/` and `DOCS/` (private, locally
excluded), the root gets `REPO_CONTEXT.md`. One AL MCP server covers all apps,
Serena runs once on the root.

```bash
python3 scripts/install /path/to/ITS.IT-Services --revision <scaffold-commit> --dry-run
python3 scripts/install /path/to/ITS.IT-Services --revision <scaffold-commit>
```

An earlier app-level install below the root is superseded only with
`--replace-app-installs`; it refuses if a managed file was edited, keeps
`APP_CONTEXT.md`, `specs/` and `DOCS/`, and rollback restores the old install.
Existing unmanaged `AGENTS.md`, `CLAUDE.md` or `opencode.json` at the root stop
the install: move their content into `REPO_CONTEXT.md` first.
Repository-specific MCP servers (for example a vendor documentation server) go into
`opencode.local.json` next to the root `opencode.json`: `{"mcp": {"<name>": {...}}}`.
The installer merges them into the rendered config on every install and update,
refuses names that collide with managed servers, and excludes the file locally.

App mode (an AL app folder containing `app.json`) remains available. Never put the
runtime inside an app folder if the corpus keeps `.al` samples:

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
The core profile enables AL MCP, Microsoft Learn, Serena and NAB AL Tools. The
`translation` profile remains accepted for existing install commands; NAB AL Tools
is already enabled by default. The AL MCP launcher
takes explicit project paths, never an arbitrary first discovered app. Set
`ALTOOL_PATH` to a selected executable or DLL to override the global `al` command.
Use a pinned environment for reproducible comparisons.

Workspace output is optional with `--workspace /path/to/repo/main.code-workspace`.
The source must be at the repo root. JSONC is accepted, settings are preserved,
and a stable app-path hash avoids basename collisions. Unmanaged or edited output
is not overwritten. Without this flag no workspace file is generated.

Fill relevant `APP_CONTEXT.md` fields and product decisions (and `REPO_CONTEXT.md`
in repository mode), then start OpenCode **from the folder you installed into**. Run `/sdd <request>` or describe the change.
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

Features from the retired five-file workflow are history or background; continue
open work as a new v2 change. The old gates and templates exist only in git ref
`baseline/agent-workflows-2026-09-29`.

## Verification

```bash
.venv/bin/python scripts/verify-scaffold
.venv/bin/python scripts/check-config opencode.json runtime/opencode.json
.venv/bin/python scripts/smoke-install --revision <committed-candidate> --host
python3 scripts/doctor --altool /path/to/altool.dll --probe-mcp
```

The aggregate command runs approval/installation/reference fixtures and compiler
wrapper fixtures. These tests do not execute AL business logic.
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
AL samples keep the upstream `.al` extension. Install the runtime outside AL project folders (repository root mode).

Model IDs/variants for installed agents come from `runtime/model-policy.json`.
Prompt frontmatter contains no model pins. The policy has a default tier
(Sonnet 5.5 high), a `spec` tier (Opus 5.5 high, `al-spec-writer` and
`al-design-reviewer`) and a `mechanical` tier (Haiku 5.5, rule audits, test
execution and the built-in `explore` agent). Primary agents keep the session model.

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
