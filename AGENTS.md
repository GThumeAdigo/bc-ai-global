# AGENTS.md

The shared contract for agents working in AL apps initialized from this scaffold.
It is symlinked from the shared scaffold and supplies reusable workflow,
conventions, and quality gates. OpenCode loads it via `opencode.json`; `CLAUDE.md`
is kept as a bridge for Claude Code sessions.

Every initialized app also has a local `APP_CONTEXT.md`, copied rather than
symlinked. Read it first, then read the app's constitution under `specs/`. Do not
put an app name, object range, namespace, sandbox detail, baseline finding, or
other app-specific fact in this shared file.

## Spec-Driven Development

**The spec is the brain, the agent is the muscle.** Production AL for a feature
is written only against an approved spec. The full workflow lives in the `sdd`
skill, not here: the constitution, the per-feature loop, the testing policy
(opt-in), and the deployment policy. Load
[`.opencode/skills/sdd/SKILL.md`](.opencode/skills/sdd/SKILL.md) (or run
`/sdd`) before any feature work, and re-load it after every auto-compaction
during feature work. Quick fixes and questions are not feature work and do not
need it.

### Model policy (which step runs on which model)

Models are pinned per step, not left to the session default, because the
subscription's weekly limit tracks Opus separately from other models. Semantic
intent review uses Opus; execution and mechanical verification use Sonnet:

- **Semantic SDD reviews run on Opus 5 high.** `al-sdd-reviewer` runs the
  specification, plan, and constitution gates. `al-implement-feature-reviewer`
  compares approved intent with implemented behavior before Test. Both agents
  pin `model: anthropic/claude-opus-5` and `variant: high`. Normal hard-stop
  flow dispatches fresh gates and does not imply shared subagent context.
- **Implementation and mechanical verifiers run on Sonnet 5.** These include
  `custom-al-implementer`, the mandatory verifiers, test writers and validators,
  and specialist auditors. Their work is execution or structured rule-checking
  rather than semantic intent reconciliation.

The SDD gate commands (`/al-spec-feature`, `/al-plan-feature`,
`/al-implement-feature`, `/al-spec-init`) are thin dispatchers: their
frontmatter names the reviewer agent and carries no model pin. The agent
frontmatter is the single place to change a gate's model or permissions; do
not reintroduce pins on the commands.

Do not unpin an agent ad hoc for a single run. If a verifier systematically
misses a class of finding on Sonnet, that is a reason to change the pin in the
agent file (globally, in the scaffolding repo), not to override it per session.

## Layout

- `specs/`: the constitution and per-feature specs (the source of truth for what to build).
- `.opencode/agents/`: focused reviewer and verifier subagents for AL code.
- `.opencode/skills/`: invocable review and workflow skills. Reusable BCQuality
  reviews are thin runtime pointers whose authoritative content is in
  `action-skill` files under
  `.opencode/BCQuality-ADIGO/custom/skills/<category>/`. Each pointer keeps only
  the `name` and `description` OpenCode needs for discovery; action metadata
  remains authoritative in the vendored skill.
  To change reusable review policy, update the custom action skill in
  `GThumeAdigo/BCQuality-ADIGO`, merge it there, then bump the submodule commit.
  Full scaffold-local skills are a separate category: the four SDD governance
  gates, `sdd`, `al-code-review`, `al-compile`, and `al-pre-pr-cleanup`.
  `hunk-review` is an external runtime bridge whose authority ships with Hunk.
- `.opencode/BCQuality-ADIGO/`: a git submodule pinned to the
  [`GThumeAdigo/BCQuality-ADIGO`](https://github.com/GThumeAdigo/BCQuality-ADIGO)
  fork. [`microsoft/BCQuality`](https://github.com/microsoft/BCQuality) is the
  canonical upstream for the Microsoft-authored corpus; the fork's `custom/`
  layer is authoritative for ADIGO reusable action skills. Run
  `git submodule update --init` when empty. To update it, make and merge changes
  in the appropriate upstream repository, update the fork, then bump the
  submodule pointer in this scaffold. Never edit vendored files in place.

## AL project path

An AL project is a folder containing `app.json`. Always discover it dynamically
rather than hardcoding a path, so the same config and agent context works across
repos:

```
find . -maxdepth 3 -name app.json -not -path '*/node_modules/*' -not -path '*/.alpackages/*' -exec dirname {} \;
```

When an MCP tool (alcops, al-mcp, nab-al-tools) requires an absolute
`projectPath`, resolve it from the discovered folder, never from a path used in
a previous session or repo.

Where the session is rooted matters, because the MCP servers inherit opencode's
working directory. When the scaffolding sits in an app folder, the session is
rooted there, `find .` discovers exactly that one app, and `al-mcp` resolves to
it deterministically. When the scaffolding sits at a multi-app workspace root,
`find .` returns several apps and any tool that picks the first match resolves
non-deterministically, so pass `projectPath` explicitly. Serena is the exception:
it activates the project at the **workspace root** regardless, so its
`relative_path` values are prefixed with the app folder name while alcops and
al-mcp paths are relative to the app. Do not paste a path from one into the
other.

### Multi-app workspaces

The repo root is **not** necessarily the AL project. A workspace may hold several
apps side by side, each with its own `app.json`: for example a main app, a test
app, and a shared foundation or library app, often listed as folders in a
`.code-workspace` file. The discovery command above returns one line per app, so
run it without `-quit` and treat the result as a list.

When more than one `app.json` is found:

- **Never** pass the repo root as `projectPath`. It has no `app.json`, so the
  analyzers silently do nothing and the compile never runs.
- Resolve every path (compile output, `.alpackages`, `.vscode/settings.json`,
  `Translations/`, `AppSourceCop.json`, `.netpackages`) relative to that app's
  own folder, not the repo root. Each app carries its own analyzer settings and
  its own ruleset; do not assume one app's configuration applies to another.
- **Compile and run the analyzers once per app folder**, and report findings per
  app. A clean main app says nothing about the test app.
- **Follow the dependency chain.** Read each app's `dependencies` in `app.json`.
  Build and publish in dependency order (foundation or library first, then the
  apps that depend on it, then the test app). A dependency that lives in the same
  workspace must be compiled and its `.app` copied into the dependent app's
  `.alpackages` before that app can compile, so a stale `.alpackages` is a common
  cause of phantom errors after a shared-app change.
- When a change touches a shared or foundation app, re-check **every** dependent
  app in the workspace, not just the one you edited. Breaking changes surface in
  the consumers.
- When a task is scoped to one app, say which app folder it applies to, and keep
  object ID ranges, prefixes, and namespaces per app as declared in that app's
  `app.json` and `AppSourceCop.json`.

If the app in scope is ambiguous, ask which app folder to work in rather than
guessing.

## Building and compiling

Three tools touch builds, and they are not interchangeable. Pick by job:

- **Compile with analyzers: use the `al-compile` skill.** It runs `alc.exe`
  from the installed VS Code AL extension directly, with the full house
  analyzer set (CodeCop, UICop, PerTenantExtensionCop plus the seven ALCops
  DLLs) and the workspace ruleset, and writes output to a temp dir so the repo
  stays clean. This is the default way to build. It works even when al-mcp is
  down, and it is the only way to do a clean baseline comparison (stash,
  compile, pop, compile, diff). Read
  [`.opencode/skills/al-compile/SKILL.md`](.opencode/skills/al-compile/SKILL.md)
  before running it: the analyzer list, the ruleset resolution, and the
  baseline recipe live there.
- **al-mcp earns its place for what alc cannot do:** `al_run_tests`,
  `al_symbolsearch` (searching inside compiled base-app packages), and
  `al_downloadsymbols`. Reach for al-mcp when the task is tests, base-app
  symbol lookup, or symbol download, not when it is a plain compile.
- **Serena never builds.** It is a language server: navigation and symbolic
  edits only. Do not ask it to compile, and do not treat its diagnostics as a
  build result.

A compile is not done when `alc` exits 0. CI fails on warnings
(`failOn: warning`), so report the warning count and classify findings against
the baseline (see "Establish the baseline" below). After any successful build,
the post-build hook prompts the mandatory verifier set; run it.

## BCQuality: the knowledge source agents cite

BCQuality is a remedial, machine-readable knowledge base for BC. Agents cite it
so that findings are backed by a vetted rule rather than paraphrased from memory.
Read [`.opencode/skills/bcquality-integration/SKILL.md`](.opencode/skills/bcquality-integration/SKILL.md)
for the full contract. The essentials:

- **Where it lives.** `.opencode/BCQuality-ADIGO/`. Knowledge files are under
  `.opencode/BCQuality-ADIGO/<layer>/knowledge/<domain>/`. The Microsoft layer vendors
  domains `performance`, `privacy`, `security`, `style`, `testing`, `ui`,
  `upgrade`. The `community/` layer adds `performance` and `security` rules, and
  the `custom/` layer adds `api`, `integration`, `operations`, `performance`,
  and `process` knowledge plus review and testing skills.
- **How it is consumed.** An adapter invokes
  `.opencode/BCQuality-ADIGO/skills/entry.md` first, including its index
  preparation. Entry routes to an action skill. The selected action skill uses
  READ (`skills/read.md`) for applicability and precedence, follows Source,
  Relevance, Worklist, and Action, then emits DO (`skills/do.md`) output.
- **Knowledge file format.** Atomic markdown with YAML frontmatter (`bc-version`,
  `domain`, `keywords`, `technologies`, `countries`, `application-area`). Each
  rule is `<slug>.md` with optional `<slug>.good.al.txt` and `<slug>.bad.al.txt` siblings.
  The samples carry a `.txt` suffix on purpose. `.opencode/` is symlinked into the
  AL project folder and `alc` compiles every `*.al` it finds there, following
  symlinks, with no exclude mechanism anywhere in the toolchain. A sample named
  `*.al` therefore lands in the app's build as a few hundred phantom warnings.
  Keep the suffix when re-vendoring from upstream BCQuality, and rename any new
  sample to match.

## How agents cite knowledge (the finding contract)

BCQuality action skills emit the DO findings shape. For a knowledge-backed
finding, set `id` equal to the primary reference's corpus-relative path, for
example `microsoft/knowledge/<domain>/<slug>.md`. Keep every
`references[].path` corpus-relative to `.opencode/BCQuality-ADIGO/`; do not
prefix it with the checkout path. Do not paraphrase a rule you can cite.

House-policy findings are not BCQuality knowledge findings. Emit them in a
separate local governance/reviewer report with `severity: block | warn | info`,
a `house:` rule, message, and location. Do not place scaffold paths in a
BCQuality DO `references` array and do not invent a corpus citation for a house
rule. An adapter that applies both sources returns the action skill's DO report
and, only when needed, a separately labelled local report.

Runtime agents with corresponding custom action skills are thin adapters. They
run Entry/index preparation, follow the selected exact action skill and READ/DO,
load the local house-rule overlay when their role requires it, and do not carry
duplicate review checklists or legacy JSON contracts in their prompts.

## Mandatory verifier set

During Test, after semantic implementation conformance passes and the app
builds, run the applicable mandatory verifiers in parallel and resolve their
findings:

- `al-code-quality-reviewer`
- `al-readability-checker`
- `al-test-coverage-validator` (only when tests are opted in, see the Testing policy in `.opencode/skills/sdd/SKILL.md`)
- `al-test-validator` (only when tests are opted in, see the Testing policy in `.opencode/skills/sdd/SKILL.md`)

When tests are not opted in for the feature, the mandatory set is just the first
two verifiers; the two test verifiers are skipped.

After an AL build or compile, the post-build hook reminds the agent to run the
applicable verifier set.

When an integration is touched (an inbound or outbound flow, a Business Event, a
staging endpoint, a Job Queue sender, or any Azure integration artifact), run
`al-integration-pattern-reviewer`, `azure-integration-validator`, and
`al-event-subscriber-auditor` in parallel.

## Verify in the web client

`bc-webclient-runner` drives a real browser against a live sandbox and walks a
user guide step by step. **It is optional, not a mandatory gate.** After
implementation, once the app can be published to a sandbox, offer the
developer the choice from the `sdd` skill's Test step: a quick manual test
recipe to click through by hand, or an autonomous verification run with the
runner. Do not run it unbidden. When the developer opts in, the runner
replaces them clicking through the app, so close with a result rather than a
request.

The coordinator's obligations are short:

- Run it in the Test step, after the mandatory verifiers pass and the app is
  published to a sandbox. Never against a production environment.
- Give it a user guide (or explicit steps with expected outcomes) and absolute
  paths for any file the flow uploads. Without expectations it degrades into
  screenshots.
- The one-time browser sign-in is a human step: if the agent reports a
  Microsoft login screen, ask for a sign-in rather than entering credentials.
- Classify mismatches rather than assuming the app is wrong: a single wrong
  caption is usually a guide error, a coherent block of them is usually an app
  defect. Confirm against the AL source before reporting a defect.

Everything else (inputs, the DO findings shape, delayed-insert and lookup
probing) lives in the authoritative BCQuality action skill referenced by the
thin `.opencode/agents/bc-webclient-runner.md` adapter. Environment values live
in the consuming app's `APP_CONTEXT.md`.

## Show diffs in Hunk

[Hunk](https://hunk.dev) is an interactive terminal diff viewer running in the
developer's own terminal. When there is a diff worth looking at (after an
implementation task, before a PR, when reporting findings that carry a
file and a line), put it in Hunk instead of pasting patch text into the chat.

Load [`.opencode/skills/hunk-review/SKILL.md`](.opencode/skills/hunk-review/SKILL.md)
before driving a session. The skill is authoritative: `hunk` is absent from
the agent PATH, this checkout is a git worktree, `hunk diff` and `hunk show`
are the developer's commands while agents drive an existing session through
`hunk session *`, and a missing session is a graceful fallback, never a
blocker. Hunk is a presentation layer: it does not compile, run the
analyzers, or replace the mandatory verifier set.

## House rules

Project-specific AL conventions (the `house:` rules) live in
[`.opencode/skills/al-code-review/SKILL.md`](.opencode/skills/al-code-review/SKILL.md),
and the project AL style guide lives beside it in
[`.opencode/skills/al-code-review/styleguide.md`](.opencode/skills/al-code-review/styleguide.md).
Both are the authority at two moments: while **authoring** AL (read them before
writing, see the Implement step) and while **reviewing** it. They are applied in
addition to BCQuality, not instead of it. When sources conflict, house rules win.

There is exactly one copy of each. Do not duplicate the style guide elsewhere in
the repo; link to it.

### Comment policy (no prose comments in AL)

We do not want comments in the codebase. Exactly two things are allowed:

- **XML documentation (`///`) on `internal` and global procedures.** That is the
  object's callable surface, and it is required there. Never on a
  `local procedure`, a trigger, `OnRun`, or an event subscriber.
- **A comment that justifies a pragma.** A `#pragma warning disable` must say
  why the suppression is justified, and the scope must be reopened with
  `#pragma warning restore`.

Everything else goes. No `//` banner, no step-by-step narration, no
commented-out code, and no "genuine why" prose comment either. When you feel the
urge to explain something in AL:

- **Name the thing.** Extract the block into a `local procedure` whose name says
  what the comment would have said.
- **Name the value.** Replace the magic value or opaque expression with a named
  local variable or a `Label`.
- **Put the reasoning in the spec.** A rationale that genuinely cannot be
  expressed in code (a platform quirk, a rejected alternative, an accepted
  trade-off) belongs in the feature `plan.md` amendment or in the `///` block of
  the nearest internal procedure, where it is durable and reviewable. It does not
  belong inline next to the statement.

This matches style guide §14.2: pragma justification is the only regular-comment
exception. Where the two disagree, this section wins.

### Which agents read the style guide

Every agent that writes or reviews AL loads the style-guide overlay appropriate
to its role. The ownership map is:

| Agent | Style guide sections it enforces |
|---|---|
| `al-readability-checker` | 2 naming, 3 organization, 4 declaration order, 9 labels, 14 documentation and comments, 15 formatting |
| `al-code-quality-reviewer` | 5 tables, 6 pages, 7 codeunits, 10 permissions, 11 error handling, 13 SOLID |
| `al-performance-reviewer` | 12 performance |
| `al-table-refactorer` | 5 tables, 3.2 regions, 14 documentation and comments |
| `al-event-subscriber-auditor` | 7.3 subscriber codeunits |
| `al-permission-set-auditor` | 10 permissions |
| `al-translation-auditor` | 8 enums, 9 labels |
| `al-test-writer`, `al-userguide-test-writer`, `al-test-validator` | 2 naming, 3.2 regions, 9 labels, 15 formatting, applied to test AL |

The style guide contains project placeholders (the `GOX`/`GOXOUT` object prefix,
the `GOXFOU Error` handler, the `ADIGO.ITS.*` namespaces). When a repo uses a
different prefix, namespace root, or foundation app, the rule still applies; only
the identifier changes. Agents enforce the pattern, not the literal name.

## Working efficiently in this repo

Learned the hard way. Read this before a session that changes existing AL.

### Settle the design before writing code

When a request changes behavior that an approved feature already specified, the
expensive mistakes are decisions, not typos. Surface them as explicit questions
first, then write. For a change to stored data the recurring three are: how wide
is the change (everywhere, or only in one branch of the data), what happens to
the schema the old behavior needed, and what happens to rows already written.
Asking costs one round trip. Guessing costs a rewrite plus a spec amendment.

### Amend a closed feature, do not rewrite it

A feature marked `done` keeps its history. Add a dated amendment section to
`spec.md` and `plan.md`, add a new numbered task to `tasks.md`, and add a
validation block to `validation.md`. Leave the superseded text in place and say
which amendment supersedes it. The amendment carries the decision owner and
date, what changed, why, what was rejected, and what was accepted as a loss.
The reasoning is the durable artifact; the diff is not.

### Shared and app-local scaffolding

`.git/info/exclude` lists `AGENTS.md`, `APP_CONTEXT.md`, `CLAUDE.md`,
`opencode.json`, `specs/`, `.opencode/`, `DOCS/`, and `.serena/`. Everything that
governs how agents work, and every spec, is therefore invisible to the BC repo's `git status`,
`git stash -u`, and `git diff`. Only the AL apps are versioned there.

Untracked by the BC repo does not mean unversioned. `AGENTS.md`, `CLAUDE.md`,
`opencode.json` and `.opencode/` are **symlinks into a shared scaffolding repo**
(`bc-ai-global`), which tracks them and is where their history lives.
`APP_CONTEXT.md`, `specs/`, and `DOCS/` are copied into the app and are local.
Two consequences follow, and they pull in opposite directions:

- **Editing a symlinked file is global.** An agent, skill, or house-rule change
  lands in every BC repo that links the same scaffolding, not just this one. Say
  so when you make one. It is also recoverable: check `git status` **in the
  scaffolding repo**, not here.
- **`specs/`, `DOCS/` and `.serena/` are real local directories with no commit
  behind them.** Git will not protect that work, so do not rely on stash or
  checkout around it.

Either way, a clean working tree in the BC repo says nothing about whether the
specs or the house rules were edited. Verify an edit to any of those paths by
reading the file back rather than by looking at the diff.

### Establish the baseline before you trust a tool result

When a build, analyzer, or verifier reports something odd, compare the same
command on the unmodified tree when it is safe to do so. Record app-specific
known warnings, analyzer quirks, and baseline counts in `APP_CONTEXT.md`, not in
this shared file. State which findings are new and which are baseline.

### Verify platform API assumptions, do not reason from the name

An AL platform API often does less than its name promises. The example that cost
a review round: `XmlReadOptions.PreserveWhitespace(false)` does **not** remove
all whitespace, because the parser still reports whitespace-only CDATA and
anything under `xml:space="preserve"` as significant. Confirm behavior against
Microsoft Learn (`microsoft_docs_search`, `microsoft_docs_fetch`) before writing
a guarantee into a spec, and add the backstop in code when the platform only
gets you part of the way.

### Run the verifiers twice

The mandatory verifiers earn their cost. Run them, apply the findings, then run
the same verifier again with the previous findings and the fix applied to each
listed in the prompt. The second pass confirms resolution and catches the common
failure where a fix moved the problem instead of removing it. Do not mark work
complete on the first pass.

### Read specs by section, not by whole file

Specs are durable and on disk, which means they survive compaction and can be
re-read at any time. Treat the context window as scarce and the spec folder as
the source of truth that outlives it:

- The first pass for a feature reads the full constitution as required by the
  `sdd` skill. Later steps read only the constitution sections that govern the
  task. Implementing a feature needs its approved `spec.md`, `plan.md`, and
  `tasks.md` plus `APP_CONTEXT.md`; it rarely needs the full brief again.
- When a spec is long, grep for the section header you need and read from
  there instead of loading the whole file. The acceptance criteria and the
  task list are the usual targets.
- After auto-compaction, do not reconstruct context from memory. Re-read the
  one spec section the current task depends on. That is cheaper and more
  accurate than a summary of a summary.
- Keep specs structured so this works: one feature per folder, stable section
  headers, amendments appended rather than woven in. The agent can only read
  selectively when the document advertises where things are.

### Delegate open-ended exploration

The main session holds the spec and the plan; that context is expensive. When
a question needs more than two or three lookups to answer ("how does X work
across these objects?", "where is Y used?"), hand it to a subagent and say in
the prompt that it navigates AL with Serena and treats `grep`/`rg` as the
fallback, per the Serena section below. The subagent's exploration transcript
stays out of the main context; only the answer returns. This is the same
reason `custom-al-implementer` pins a cheaper model: the coordinator's context
is the bottleneck, not the tokens spent elsewhere. Direct Serena use from the
main session remains the default for anything a single symbol lookup answers.

## Serena (semantic symbol MCP server)

Serena is wired in as an opencode MCP server (registered globally under
`~/.config/opencode/opencode.json` with `--context ide --project-from-cwd`, so
it applies to every AL repo on this machine). It provides LSP-backed AL symbol
tools: `get_symbols_overview`, `find_symbol`, `find_referencing_symbols`,
`replace_symbol_body`, `rename_symbol`, and `search_for_pattern`, plus project
memories under `.serena/memories`.

- Serena activates the nearest configured workspace root. In a multi-app
  checkout, its relative paths may therefore include an app-folder prefix;
  confirm the active root rather than assuming a fixed layout.
- The AL language server expects an `app.json` at the project root and the
  workspace root has none, so the `al/manifestMissing` warning on startup is
  expected and harmless. Symbol extraction is per-file (each `.al` file is
  opened before symbol requests), so document symbols and indexing work
  regardless. `get_symbols_overview` on a non-AL file such as `app.json` errors
  by design; that is not a misconfiguration.
- The AL extension binaries come from the installed VS Code AL extension
  (`ms-dynamics-smb.al-*`); if that is absent, Serena downloads a pinned
  version to `~/.serena/ls_resources/`. Optional `AL_EXTENSION_PATH` override
  or `ls_specific_settings.al.al_extension_version` for a different version.
- The index is pre-built and Serena refreshes it as files change. After a
  rebuild of the worktree or a large branch switch, re-run
  `serena project index` from the **workspace root**.
- `.serena/` is listed in `.git/info/exclude`, matching the scaffolding
  policy. The global dashboard stays off (`web_dashboard_open_on_launch:
  false` in `~/.serena/serena_config.yml`) so MCP starts do not open a
  browser. Open it manually at `http://localhost:24282/dashboard/`.

### Use it before grepping or reading files

Serena is the cheap way to explore a large AL workspace, and it is the default
navigation tool for AL, ahead of `grep`, `glob`, and shell `rg`. Reach for it
first. A grep returns matching lines and leaves you to reconstruct the structure
around them, which in practice means reading whole files to find out what a match
belongs to. Serena returns the symbol, its container, and its references
directly, so the same question costs fewer calls and far fewer tokens.

Use `get_symbols_overview` to learn a file, `find_symbol` (with `depth` and
`include_body=False` first) to locate a definition, `find_referencing_symbols` to
find callers, and `search_for_pattern` when you genuinely need a text match
rather than a symbol.

Fall back to the plain search tools only for what Serena does not cover:
non-AL files (`app.json`, `.xlf`, `.json`, `.ruleset`, markdown), file-name
discovery, counting occurrences, and reading git or build output.

**This outranks the Task-tool search default.** The general tool-usage guidance
prefers handing file search to a subagent to save context. That decides *who*
runs the search, not *which* tool it uses, so it is not a licence to grep. For
AL, drive Serena yourself for anything a symbol lookup answers, and when you do
delegate a broader exploration, state in the prompt that the subagent navigates
AL with Serena and treats `grep`/`rg` as the fallback. Delegation remains right
for genuinely open-ended, multi-round investigations and for chewing through
large tool output, where a separate context is the point. Where the two still
read as conflicting, this section wins, per "When sources conflict, house rules
win."

Note that Serena's line numbers are 0-based while the AL compiler and the
analyzers report 1-based, so translate before citing a finding as `file:line`.
Prefer `rename_symbol` and `safe_delete_symbol` over hand-edits when changing an
existing symbol: they are reference-aware across the active workspace.

### Memories

When onboarding has been performed, the memory graph is project-local and
untracked. Read its root memory first in a session that touches unfamiliar code.
Keep per-app facts in app-local memories or `APP_CONTEXT.md`; use
`serena memories check` from the active workspace root to report broken links.

The memories are a **navigational summary**, not a second source of truth. This
file and the house rules under `.opencode/skills/al-code-review/` remain
authoritative for conventions and workflow; when the two disagree, fix the
memory. Memories may carry workspace navigation facts that do not belong in
this shared contract.

## Runtime reloads

OpenCode loads `opencode.json`, agent files, commands, skills, and plugins at
startup. After any config-time change, quit and restart OpenCode; an existing
session continues using the previously loaded configuration.

## Style

Agent prompts and docs in this repo use a direct, practical voice and avoid em
dashes (use commas, colons, or periods instead). Keep that convention in any new
agent, skill, or spec so the content stays consistent.
