# AGENTS.md

The contract between you and every agent that works in this repository. This is
the canonical guidance file. opencode loads it automatically via `opencode.json`;
`CLAUDE.md` is kept as a bridge for Claude Code sessions.

## What this repo is

An OpenCode-based prototype for agentic Business Central product development at
ADIGO. It packages a curated set of AI agents, skills, and BCQuality guidance and
is driven by Spec-Driven Development. It is not yet a production-ready template
or a complete AL application.

## How we build here: Spec-Driven Development

**The spec is the brain, the agent is the muscle.** You do not write production
AL until an approved spec exists for the feature. Specs are durable artifacts
under `specs/`; a chat session is not. The developer architects the decisions in
the spec; the agent executes them.

### The constitution (read first, every session)

- `specs/brief.md` — customer requirements and business processes (the what and why).
- `specs/tech-design.md` — implementation strategy: which standard BC modules to
  reuse, and where custom code is genuinely needed.
- `specs/roadmap.md` — ordered list of features with status.
- `AGENTS.md` (this file) — conventions, quality gates, and the workflow.

### The per-feature loop

For each feature: **Feature Spec -> Plan -> Implement -> Test -> Docs -> Merge**,
then replan the next feature. Use one chat session per feature, and start it by
reading the constitution.

1. **Spec.** Draft `specs/features/<id>/spec.md`: the problem, the users, scope,
   acceptance criteria, what is out of scope, and the durable automated-test
   decision. Then run `/al-spec-feature` to review it against the constitution
   and confirm the acceptance criteria are testable. Stop for human review. No
   code yet.
2. **Plan.** Draft `plan.md` and `tasks.md` next to the spec: the BC objects to
   add or extend, the object ID range, the data model, integration points, and an
   ordered task list. Then run `/al-plan-feature` to review them against the
   approved spec. Stop for human review.
3. **Implement.** Before writing any AL, read the house rules and style guide in
   `.opencode/skills/al-code-review/` (`SKILL.md` plus `styleguide.md`) and let
   them shape the code as you write it, not just at review. Work the tasks in
   order, applying the house rules and citing BCQuality. Then run
   `/al-implement-feature` to review the implementation against its spec, plan,
   and tasks.
4. **Test.** Building the app triggers the post-build hook, which prompts the
   mandatory verifier agents and a BCQuality review. Resolve every finding.
   Whether automated tests are written is governed by the **Testing policy**
   below and recorded in the feature spec and plan. When the feature touches the
   UI, also drive it in a live sandbox with `bc-webclient-runner`, see **Verify
   in the web client** below.
5. **Docs and Merge.** Update the feature docs, tick the roadmap item, open a PR.

### Testing policy (tests are opt-in)

Automated tests are **not** written by default in this repo. Every feature spec
and plan must record `Automated tests: yes | no`, the decision owner/date, and
the reason. The plan must match the approved spec. If the decision is absent,
the agent must ask the developer and update both artifacts before proceeding.
Chat history alone is not a durable testing decision.

- If the developer says **no** (the default when unstated): skip all test
  writing. A missing test is **not** a finding. `al-test-writer`,
  `al-userguide-test-writer`, `al-test-coverage-validator/-enforcer`,
  `al-test-validator`, and `al-test-runner` are not run. The plan states that no
  automated test artifacts or test verifiers apply, and test tasks are removed.
- If the developer says **yes**: the full test discipline applies. Every
  acceptance criterion gets a covering test, and the test verifiers run as part
  of the mandatory set.

This is a house rule and, per "When sources conflict, house rules win," it
overrides any "test per acceptance criterion" or "missing test is a
blocker/major" wording elsewhere in the workflow skills or templates.

### Deployment policy (nothing is in production yet)

None of the apps in this repo are installed in a production tenant. Until that
changes, **schema changes are free**. Treat a breaking schema change as a normal
edit, not as an event that needs a migration path.

- Remove a field, table, enum value, or procedure outright when it is no longer
  needed. Do **not** mark it `ObsoleteState = Pending` first, and do not carry
  `ObsoleteReason` or `ObsoleteTag` for the sake of process.
- Do **not** write an upgrade codeunit for existing data. Rows written by an
  earlier version may be left stale, unreadable, or orphaned. Re-import or
  re-create the data instead.
- A missing obsolete marking and a missing upgrade path are **not** findings.
  `al-obsolete-tracker` and `al-upgrade-checker` are not part of any mandatory
  set. If one is run anyway, downgrade its migration findings to info.
- Do still **record** the breaking change in the feature plan: what breaks, what
  a consumer must do, and why it was taken. The reasoning is the durable part,
  the migration code is not.

This is a house rule and it overrides any obsolete-discipline or
upgrade-safety wording in the agents, skills, or BCQuality `upgrade` domain.
Revisit it the moment the first app ships to a production tenant, because every
bullet above inverts at that point.

### Bootstrapping

At the start of a project (or when the high-level requirements change), draft
`brief.md`, `tech-design.md`, and `roadmap.md`, then run `/al-spec-init` once to
review the constitution for completeness and consistency before any feature work.

## Layout

- `specs/`: the constitution and per-feature specs (the source of truth for what to build).
- `.opencode/agents/`: focused reviewer and verifier subagents for AL code.
- `.opencode/skills/`: invocable review skills, including the SDD review gates above.
  Most are thin pointers: the authoritative content lives in BCQuality
  (the single source of truth) as `action-skill` (review) files under
  `.opencode/BCQuality-ADIGO/custom/skills/<category>/`, and each pointer mirrors the
  upstream skill's frontmatter (the BCQuality `kind`/`id`/`version`/`title`/
  `inputs`/`outputs` and dimension schema) plus the `name`/`description` the
  runtime needs to discover and trigger it.
  Edit the skill upstream in EquerraNZ/community-BCQuality and re-vendor, not the
  pointer. Two skills are exceptions. `al-code-review` stays a full local skill
  because it carries this project's house rules. `hunk-review` points outward
  rather than at BCQuality: its authoritative content ships with the Hunk CLI and
  is resolved at runtime through `hunk skill path`, so the local file holds only
  the repo-specific notes.
- `.opencode/BCQuality-ADIGO/`: a vendored, Microsoft-authored subset of the
  [BCQuality](https://github.com/EquerraNZ/community-BCQuality) knowledge corpus.
  A git **submodule** (`GThumeAdigo/BCQuality-ADIGO`), pinned to a commit by the
  parent repo. Run `git submodule update --init` if the folder is empty, and
  never rename or move it, since `.gitmodules` maps it by path: correct the
  references instead. The `custom/skills/`
  layer holds this project's reusable `action-skill` review skills; the runtime pointers in
  `.opencode/skills/` defer to them.

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
- **How it is consumed.** An agent invokes `.opencode/BCQuality-ADIGO/skills/entry.md`
  first. Entry returns a dispatch record naming the action skill(s) to run.
  Action skills follow the four-step pattern (Source, Relevance, Worklist,
  Action) defined in `.opencode/BCQuality-ADIGO/skills/do.md`, reading `read.md` on demand.
- **Knowledge file format.** Atomic markdown with YAML frontmatter (`bc-version`,
  `domain`, `keywords`, `technologies`, `countries`, `application-area`). Each
  rule is `<slug>.md` with optional `<slug>.good.al` and `<slug>.bad.al` siblings.

## How agents cite knowledge (the finding contract)

Each verifier agent has a **Knowledge sources** section naming the BCQuality
folder it sources from. When a finding maps onto a BCQuality knowledge file:

- Set the finding `rule` (or `id`) to the knowledge file slug.
- Populate `references` with `[{ "path": ".opencode/BCQuality-ADIGO/microsoft/knowledge/<domain>/<slug>.md" }]`.
- Do not paraphrase a rule you can cite.

When a finding maps onto a rule in the project style guide or the house-rule
skill instead:

- Set the finding `rule` to `house:` plus a short slug, and add the style-guide
  section number when there is one, for example
  `house:styleguide-11-error-via-gox-fou-error`.
- Populate `references` with the house-rule path plus the section anchor, for
  example `[{ "path": ".opencode/skills/al-code-review/styleguide.md", "section": "11.1" }]`
  or `[{ "path": ".opencode/skills/al-code-review/SKILL.md" }]`.

When a finding maps onto neither, use a `rule` slug prefixed `house:` (or the
agent's own rule id, for example an `AS0xxx` AppSource rule) and leave
`references: []`. The only citable paths are files that exist under
`.opencode/BCQuality-ADIGO/` or under `.opencode/skills/al-code-review/`. Never cite
anything else.

## Agent-to-domain map

| Agent | BCQuality domain |
|---|---|
| `al-code-quality-reviewer` | performance, security, privacy |
| `al-readability-checker` | style, ui |
| `al-performance-reviewer` | performance |
| `al-upgrade-checker` | upgrade |
| `al-test-validator` | testing |
| `al-integration-pattern-reviewer` | performance, security (plus the `al-modern-integration-patterns` house rules) |

The integration validators source their rules from skills rather than a single
BCQuality domain. `al-integration-pattern-reviewer` cites the
`al-modern-integration-patterns` house rules and the mapped BCQuality
performance/security files named in that skill. `azure-integration-validator`
cites the `azure-integration-review` house rules with empty references, since no
BCQuality Azure domain is vendored.

Other agents (`al-appsource-validator`, `al-multitenancy-reviewer`,
`al-translation-auditor`, `al-permission-set-auditor`, `al-obsolete-tracker`,
`al-event-subscriber-auditor`, `azure-integration-validator`,
`al-test-coverage-validator`, `al-test-coverage-enforcer`) report against their
own rule ids with empty references until matching knowledge files land upstream.

## Mandatory verifier set

Before marking any BC development task (the Implement step of a feature)
complete, run these four verifiers in parallel and resolve their findings:

- `al-code-quality-reviewer`
- `al-readability-checker`
- `al-test-coverage-validator` (only when tests are opted in, see the Testing policy)
- `al-test-validator` (only when tests are opted in, see the Testing policy)

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
user guide step by step. Use it. The compilers, the analyzers, and every verifier
agent read source. They cannot see what the client actually renders, so a whole
class of defect is invisible to them and shows up only at runtime:

- a caption that silently falls back to the control name
- a list that does not refresh after an insert
- a `StyleExpr` that never turns red
- an action whose enabled state is wrong for the selected row
- a lookup that opens empty
- a page that throws on open

**What it replaces.** The developer clicking through the app to confirm a change
works. Do not close a UI-touching task with "please verify in the client". Run
the runner, report what it observed, and hand over a result rather than a
request. This is the point of the agent: verification moves off the human.

**When to run it.** In the Test step, after the mandatory verifiers pass and the
app is published to a sandbox. Run it whenever a change touches a page, an
action, a caption, a style expression, a field's visibility, or a flow a user
clicks through. A codeunit refactor with no UI surface does not need it.

**What it needs from you.**

- A published app on a non-production sandbox and its URL. The agent refuses an
  environment named Production. Leave `?company=` off unless you know the
  company; BC falls back to the user's default and the agent reports where it
  landed.
- A signed-in persistent browser profile. The one-time interactive sign-in is a
  human step. If the agent reports a Microsoft login screen, ask for a sign-in
  rather than entering credentials.
- A user guide, or an explicit list of steps with expected outcomes. Without
  documented expectations the run has nothing to assert against and degrades into
  screenshots.
- Absolute paths for any file the flow uploads, plus the value to compare against
  where one exists (a byte count, a row count). The Playwright MCP refuses paths
  outside the workspace, so copy a fixture from `/tmp` into a git-excluded folder
  under the repo before pointing the agent at it.
- `continue_on_fail: true` on a first run, so one pass yields the full picture
  instead of stopping at the first mismatch.

**Classify every mismatch, do not assume the app is wrong.** A user guide that
has never been executed is unverified in both directions. For each mismatch the
agent states whether it is *possibly-wrong-app*, *possibly-wrong-guide*, or
*unclear*, and why. Captions, field ordering, **Show more** placement, and part
or FactBox names are the details a hand-written guide most often gets wrong, so a
single wrong caption is usually a guide error. A whole coherent block of them is
usually an app defect. Confirm the call against the AL source before reporting it
as a defect: the runner sees symptoms, the source gives the mechanism, and the
two together turn an observation into an actionable fix.

**Do not assert file-dependent numbers.** Tell the agent which values vary with
the input (counts, sizes, totals) and have it capture them and assert their shape
and their relationships to each other instead of fixed values.

## Show diffs in Hunk

[Hunk](https://hunk.dev) is an interactive terminal diff viewer running in the
developer's own terminal. When there is a diff worth looking at, put it in Hunk
instead of pasting patch text into the chat. The developer gets a real viewer
with syntax highlighting and navigation, and your review notes land pinned to the
lines that provoked them rather than scrolling away in a transcript.

Load [`.opencode/skills/hunk-review/SKILL.md`](.opencode/skills/hunk-review/SKILL.md)
before driving a session. It resolves the authoritative instructions that ship
with the CLI (`hunk skill path`) and carries the repo-specific details: `hunk` is
absent from the agent PATH, this checkout is a git worktree, and how to turn
verifier findings into a single pinned `comment apply` batch.

**When to reach for it.** After finishing an implementation task, before opening
a PR, when reporting verifier findings that carry a file and a line, and any time
the developer asks to review, walk through, or look at changes. Prefer it to a
`git diff` dump in the response.

**When not to.** No code changed, or the task is a question rather than an edit.
Do not open the TUI yourself: `hunk diff` and `hunk show` are the developer's
commands. Agents drive an existing session through `hunk session *`.

**When no session is live.** `hunk session list` returning nothing means the
developer has not launched Hunk. Say so and carry on with the normal response.
Ask them to launch it if the diff is the point of the exchange. This is a
graceful fallback, not a blocker: never stall a task waiting for a viewer.

Hunk is a presentation layer over the diff. It does not compile, run the
analyzers, or see what the web client renders, so it neither replaces the
mandatory verifier set nor `bc-webclient-runner`.

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

This narrows the "narrow exceptions" list in style guide §14.2 to pragmas only.
Where the two disagree, this section wins.

### Which agents read the style guide

Every agent that writes or reviews AL names the style guide in its **Knowledge
sources** section and owns the sections closest to its job:

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

### The agent scaffolding is not tracked by the BC repo

`.git/info/exclude` lists `AGENTS.md`, `CLAUDE.md`, `opencode.json`, `specs/`,
`.opencode/`, `DOCS/`, and `.serena/`. Everything that governs how agents work,
and every spec, is therefore invisible to the BC repo's `git status`,
`git stash -u`, and `git diff`. Only the AL apps are versioned there.

Untracked by the BC repo does not mean unversioned. `AGENTS.md`, `CLAUDE.md`,
`opencode.json` and `.opencode/` are **symlinks into a shared scaffolding repo**
(`bc-ai-global`), which tracks them and is where their history lives. Two
consequences follow, and they pull in opposite directions:

- **Editing any of them is global.** An agent, skill, or house-rule change lands
  in every BC repo that links the same scaffolding, not just this one. Say so
  when you make one. It is also recoverable: check `git status` **in the
  scaffolding repo**, not here.
- **`specs/`, `DOCS/` and `.serena/` are real local directories with no commit
  behind them.** Git will not protect that work, so do not rely on stash or
  checkout around it.

Either way, a clean working tree in the BC repo says nothing about whether the
specs or the house rules were edited. Verify an edit to any of those paths by
reading the file back rather than by looking at the diff.

### Establish the baseline before you trust a tool result

The single highest-value technique in this repo: when a build, analyzer, or
verifier reports something odd, `git stash -u`, re-run the same command on the
unmodified tree, then `git stash pop`. Most of the noise here is pre-existing.
Known baseline, do not attempt to fix as part of an unrelated change:

- `al_build` on `ADIGO.BAU.Interfaces.GAEB` reports `CompilationFailed` with
  **zero** diagnostics. It reproduces on a clean checkout and is documented in
  that feature's `validation.md`. Use `al_compile` for validation, which is
  clean, and `al_build scope=all` when a package is actually needed. Do not
  chase the failure; do not conclude your change broke the build.
- LinterCop `LC0091` "missing translation" fires on fields that are fully
  translated, and the count moves when unrelated trans-units are added or
  removed. It matches positionally against a `.g.xlf` that only a successful
  package build regenerates. Verify translation completeness with
  `nab-al-tools refreshXlf` instead, and record the discrepancy rather than
  editing translations to satisfy the rule.
- `PC0037` and `LC0052` warnings exist across the GAEB app already.

State in the summary which findings are yours and which were already there.

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

## Serena (semantic symbol MCP server)

Serena is wired in as an opencode MCP server (registered globally under
`~/.config/opencode/opencode.json` with `--context ide --project-from-cwd`, so
it applies to every AL repo on this machine). It provides LSP-backed AL symbol
tools: `get_symbols_overview`, `find_symbol`, `find_referencing_symbols`,
`replace_symbol_body`, `rename_symbol`, and `search_for_pattern`, plus project
memories under `.serena/memories`.

- The Serena project is the **workspace root**, one level above this app
  folder, so it covers both AL apps and not just this one. There is
  deliberately no `.serena/` inside an app folder; `--project-from-cwd` walks
  up to find it. `project.yml` sets `language_servers: [al]`.
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

### Use it before reading files

Serena is the cheap way to explore 580-odd AL files. Reach for
`get_symbols_overview`, `find_symbol` (with `depth` and `include_body=False`
first), `find_referencing_symbols`, and `search_for_pattern` instead of reading
whole `.al` files. Note that Serena's line numbers are 0-based while the AL
compiler and the analyzers report 1-based, so translate before citing a finding
as `file:line`. Prefer `rename_symbol` and `safe_delete_symbol` over hand-edits
when changing an existing symbol: they are reference-aware across both apps.

### Memories

Onboarding has been performed. The memory graph is project-local and untracked,
same as the other scaffolding, and it is rooted at `core`. Read that first in a
session that touches unfamiliar code; it links out to `tech_stack`,
`suggested_commands`, `conventions`, `task_completion`, and the per-app
`gaeb/core` and `construction/core`. `memory_maintenance` defines the style and
reference conventions for writing new ones. `serena memories check` from the
workspace root reports broken references.

The memories are a **navigational summary**, not a second source of truth. This
file and the house rules under `.opencode/skills/al-code-review/` remain
authoritative for conventions and workflow; when the two disagree, fix the
memory. Memories do carry one thing this file cannot: workspace-level facts
covering `ADIGO.BAU.Projects.Construction`, which has no `AGENTS.md` of its own.

## Style

Agent prompts and docs in this repo use a direct, practical voice and avoid em
dashes (use commas, colons, or periods instead). Keep that convention in any new
agent, skill, or spec so the content stays consistent.
