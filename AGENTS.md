# AGENTS.md

The shared contract for agents working in AL apps initialized from this scaffold.
It is symlinked from the shared scaffold and carries the operational rules every
session needs: how to find the AL project, how to build, and where the
specialized workflow, review, and knowledge content lives. OpenCode loads it via
`opencode.json`; `CLAUDE.md` is kept as a bridge for Claude Code sessions.
OpenCode loads this file into the main session only; subagents get their
contract from their own files under `.opencode/agents/` and the dispatch prompt.

Every initialized app also has a local `APP_CONTEXT.md`, copied rather than
symlinked. Read it first, then read the app's constitution under `specs/`. Do not
put an app name, object range, namespace, sandbox detail, baseline finding, or
other app-specific fact in this shared file.

## Spec-Driven Development

**The spec is the brain, the agent is the muscle.** Production AL for a feature
is written only against an approved spec. The authoritative workflow lives in
the `sdd` skill, not here: the constitution, the per-feature loop (Spec, Plan,
Implement, Test, Docs, Merge), the approval hard stops with digest-bound
evidence in `approvals.md`, the model policy, the testing policy (opt-in), the
deployment and compatibility policy (decided app-local in `APP_CONTEXT.md`), the
amendment procedure, and the dispatch contracts. Load
[`.opencode/skills/sdd/SKILL.md`](.opencode/skills/sdd/SKILL.md) (or run
`/sdd`) before any feature work, and re-load it after every auto-compaction
during feature work. Quick fixes and questions are not feature work; use
"Outside the SDD loop" below.

## Layout

- `specs/`: the constitution and per-feature specs (the source of truth for what to build).
- `.opencode/agents/`: focused reviewer and verifier subagents for AL code.
- `.opencode/skills/`: invocable review and workflow skills: the four SDD
  governance gates, `sdd`, `al-code-review`, `al-compile`, and
  `al-pre-pr-cleanup`. Reusable BCQuality reviews are thin runtime pointers
  whose authoritative content lives in the vendored submodule.
- `.opencode/BCQuality-ADIGO/`: a git submodule pinned to the
  [`GThumeAdigo/BCQuality-ADIGO`](https://github.com/GThumeAdigo/BCQuality-ADIGO)
  fork. See the BCQuality section of `README.md` for the corpus layout and the
  update procedure. Never edit vendored files in place.

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
  stays clean. It is the default way to build, it works even when al-mcp is
  down, and it is the only way to do a clean baseline comparison. Read its
  skill before running it: the analyzer list, the ruleset resolution, the
  baseline discipline, and the baseline recipe live there.
- **al-mcp earns its place for what alc cannot do:** `al_run_tests`,
  `al_symbolsearch` (searching inside compiled base-app packages), and
  `al_downloadsymbols`. Reach for al-mcp when the task is tests, base-app
  symbol lookup, or symbol download, not when it is a plain compile.
- **Serena never builds.** It is a language server: navigation and symbolic
  edits only. Do not ask it to compile, and do not treat its diagnostics as a
  build result.

A compile is not done when `alc` exits 0. CI fails on warnings
(`failOn: warning`), so report the warning count and classify findings against
the baseline; the `al-compile` skill owns that discipline. After any successful
build, the post-build hook prompts the remaining verifier work; outside the SDD
loop that means the two always-on reviewers, see "Outside the SDD loop" below.

## BCQuality and Microsoft Learn

BCQuality is a remedial, machine-readable knowledge base for BC. Agents cite it
so that findings are backed by a vetted rule rather than paraphrased from
memory, in SDD and non-SDD sessions alike. The `microsoft-learn` MCP server is
the companion source for platform API behavior: verify before relying on an
API's name (house rule 13 in `.opencode/skills/al-code-review/SKILL.md`).

The runtime contract (entry routing, DO findings, corpus-relative citations,
house-report separation) is owned by the thin adapter agents under
`.opencode/agents/`. The corpus layout, knowledge file format, citation
contract, and submodule update procedure are documented in the BCQuality
section of `README.md`.

## House rules

Project-specific AL conventions (the `house:` rules) live in
[`.opencode/skills/al-code-review/SKILL.md`](.opencode/skills/al-code-review/SKILL.md),
and the project AL style guide lives beside it in
[`styleguide.md`](.opencode/skills/al-code-review/styleguide.md).
Both are the authority at two moments: while **authoring** AL (read them before
writing) and while **reviewing** it. They are applied in
addition to BCQuality, not instead of it. When sources conflict, house rules win.

There is exactly one copy of each; link to them, do not duplicate. The comment
policy is styleguide §14.2. Each agent file under `.opencode/agents/` names the
style guide sections that agent enforces.

## Outside the SDD loop

A bug fix, a compile-error cleanup, or a small change does not need the `sdd`
skill or spec artifacts. The path is:

1. Discover the app folder (above), read `APP_CONTEXT.md`, and read the house
   rules and style guide before editing anything.
2. Dispatch `custom-al-implementer` for anything beyond a trivial one-line
   edit; it runs in quick-fix mode, consults BCQuality and Microsoft Learn, and
   reports per its return contract. Single-symbol lookups and one-line edits
   the coordinator may do itself, with Serena first.
3. Compile with the `al-compile` skill and classify findings against the
   baseline.
4. Run `al-code-quality-reviewer` and `al-readability-checker` in parallel on
   the changed AL, resolve every finding or justify it explicitly, then rerun
   the same reviewers with the findings and fixes listed to confirm
   resolution. An acknowledged finding is neither resolved nor waived; do not
   mark the work complete on the first pass.
5. If the change reveals that behavior an approved feature specified is wrong,
   that is not a quick fix: load the `sdd` skill and use its amendment
   procedure.

## Shared and app-local scaffolding

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

## Serena (semantic symbol MCP server)

Serena provides LSP-backed AL symbol tools: `get_symbols_overview`,
`find_symbol`, `find_referencing_symbols`, `replace_symbol_body`,
`rename_symbol`, and `search_for_pattern`, plus project memories under
`.serena/memories`. Setup and infrastructure facts (registration, language
server binaries, startup warnings, index rebuilds, dashboard) are in the Serena
section of `README.md`.

- Serena is the default navigation tool for AL, ahead of `grep`, `glob`, and
  shell `rg`. A grep returns matching lines and leaves you to reconstruct the
  structure around them; Serena returns the symbol, its container, and its
  references directly, so the same question costs fewer calls and far fewer
  tokens. Use `get_symbols_overview` to learn a file, `find_symbol` (with
  `depth` and `include_body=False` first) to locate a definition,
  `find_referencing_symbols` to find callers, and `search_for_pattern` when you
  genuinely need a text match rather than a symbol. Fall back to the plain
  search tools only for what Serena does not cover: non-AL files (`app.json`,
  `.xlf`, `.json`, `.ruleset`, markdown), file-name discovery, counting
  occurrences, and reading git or build output.
- **This outranks the Task-tool search default.** The general tool-usage
  guidance prefers handing file search to a subagent to save context. That
  decides *who* runs the search, not *which* tool it uses, so it is not a
  licence to grep. For AL, drive Serena yourself for anything a single symbol
  lookup answers, and when you do delegate a broader exploration, state in the
  prompt that the subagent navigates AL with Serena and treats `grep`/`rg` as
  the fallback. Delegation remains right for genuinely open-ended, multi-round
  investigations and for chewing through large tool output, where a separate
  context is the point.
- In a multi-app checkout, Serena activates the workspace root, so its relative
  paths may include an app-folder prefix; confirm the active root rather than
  assuming a fixed layout.
- Serena's line numbers are 0-based while the AL compiler and the analyzers
  report 1-based, so translate before citing a finding as `file:line`. Prefer
  `rename_symbol` and `safe_delete_symbol` over hand-edits when changing an
  existing symbol: they are reference-aware across the active workspace.
- Memories: when onboarding has been performed, read the root memory first in a
  session that touches unfamiliar code. Keep per-app facts in app-local
  memories or `APP_CONTEXT.md`; use `serena memories check` from the active
  workspace root to report broken links. Memories are a **navigational
  summary**, not a second source of truth: this file and the house rules under
  `.opencode/skills/al-code-review/` remain authoritative, and when the two
  disagree, fix the memory.

## Runtime reloads

OpenCode loads `opencode.json`, agent files, commands, skills, and plugins at
startup. After any config-time change, quit and restart OpenCode; an existing
session continues using the previously loaded configuration.

## Style

Agent prompts and docs in this repo use a direct, practical voice and avoid em
dashes (use commas, colons, or periods instead). Keep that convention in any new
agent, skill, or spec so the content stays consistent.
