# ADIGO Agentic Business Central Development

This repository is a prototype for agentic Microsoft Dynamics 365 Business
Central product development at ADIGO. It is intended for use with
[OpenCode](https://opencode.ai) and is not yet a production-ready development
template.

The prototype combines Spec-Driven Development, focused AL review agents, and a
vendored BCQuality knowledge base. Its purpose is to explore a repeatable way for
ADIGO developers and AI agents to design, implement, and review Business Central
product features without treating chat history as the source of truth.

## Quick start with an existing BC repository

Install the scaffold into the AL app folder that contains `app.json`. For a
multi-app repository, select one app folder, not the Git repository root. Do not
put the BC repository inside this template repository or add this template as a
Git submodule. Nested repositories make Git status, diffs, hooks, builds, and
agent path discovery less reliable.

1. Keep this template clone at a stable local path. It can live anywhere, but do
   not move or delete it after installation because the app folder links to it.

   Initialize the vendored BCQuality submodule before installing the scaffold:

   ```bash
   git -C /path/to/bc-ai-global submodule update --init
   ```

   ```text
   /path/to/bc-ai-global/
   /path/to/MultiAppRepo/
   |-- .git/
   |-- App1/
   `-- App2/
       |-- app.json
       `-- src/
   ```

2. Initialize the selected AL app folder. The script creates symlinks in that
   folder and adds the template's local exclusions to the enclosing Git
   repository's `.git/info/exclude`, so the AI scaffold does not appear in
   commits.

   ```bash
   /path/to/bc-ai-global/init-linux.sh /path/to/MultiAppRepo/App2
   ```

   Pass multiple AL app folders to initialize several apps at once:

   ```bash
   /path/to/bc-ai-global/init-linux.sh /path/to/MultiAppRepo/App1 /path/to/MultiAppRepo/App2
   ```

   The script creates symlinks for the shared agent runtime, but copies
   `APP_CONTEXT.md`, `specs/`, and `DOCS/` as app-local starting points.
   `APP_CONTEXT.md` holds each app's name, namespaces, object ranges,
   dependencies, and verification environment; `AGENTS.md` remains a reusable
   shared contract. Fill in the context file before feature work. You can create
   and edit `specs/features/` and `DOCS/` from the app folder without changing
   this template or any other app. Re-running the script adds newly introduced
   scaffold files under existing `specs/` and `DOCS/` directories without
   overwriting local files; an existing `APP_CONTEXT.md` remains untouched. It
   requires every supplied folder to contain an `app.json`.

   The initialized app folder should resemble:

   ```text
   MultiAppRepo/
   |-- .git/
   |-- App1/
   `-- App2/
   |-- .opencode/ -> /path/to/bc-ai-global/.opencode/
   |-- APP_CONTEXT.md
   |-- DOCS/
   |-- specs/
   |-- AGENTS.md
   |-- CLAUDE.md
   |-- opencode.json
   |-- app.json
   `-- src/
   ```

   Each app folder carries its own `app.json`, `.alpackages`, analyzer settings,
   and AI scaffold. Agents discover all app folders dynamically and compile each
   one separately; see the AL project path section in `AGENTS.md`.

3. The installer uses `.git/info/exclude`, which is local to the clone and is
   never committed. It applies every rule from this template's [exclude](exclude)
   file, including the app-local `APP_CONTEXT.md`, `specs/`, and `DOCS/`
   content. This keeps app context, feature specifications, and documentation
   private to the local app checkout. The installer resolves this file through
   `git rev-parse --git-path info/exclude`, so normal repositories and linked
   worktrees update the correct common Git exclusion file before scaffold paths
   are created. This also means app-local `specs/` and
   `DOCS/` are Git-excluded and are not protected by commits, stash, checkout,
   or ordinary Git recovery. Back them up deliberately.

4. Fill in `APP_CONTEXT.md`, including the explicit deployment status,
   production/persisted-data compatibility yes/no decision, and trusted released
   baseline ref. Fill in `specs/brief.md`, `specs/tech-design.md`, and
   `specs/roadmap.md`. A release tag alone does not enable compatibility. Do not
   start production AL work while these files still contain unresolved placeholders.

5. Start OpenCode from the initialized AL app folder, not from this template
   repository.

   ```bash
   cd /path/to/MultiAppRepo/App2
   opencode
   ```

6. Run `/al-spec-init`, resolve its findings, and rerun it to pass. For each
   feature, use `/sdd spec <id>`, `/sdd plan <id>`, and `/sdd implement <id>`.
   The `/al-spec-feature`, `/al-plan-feature`, and `/al-implement-feature`
   commands are review-only gates invoked by those stages; they do not draft or
   implement the feature. The plan gate runs in two stages: a mechanical
   review (`al-plan-mechanical`, Sonnet) before the semantic review
   (`/al-plan-feature`, Opus). Resolve findings and rerun each gate to pass
   before the required human approval or Test entry.

7. Keep this template clone as the update source. Symlinked runtime files are
   updated on disk immediately, but OpenCode loads configuration-time files only
   at startup. Quit and restart OpenCode after changes to `opencode.json`,
   agents, commands, skills, or plugins. App-local `specs/` and `DOCS/` do not update
   automatically, so deliberate template updates must be copied into an app only
    when wanted.

Before compilation, install the Microsoft AL Language extension, download the
Business Central symbols required by `app.json` into the app's `.alpackages`,
make every declared dependency available in dependency order, and ensure the
workspace analyzer ruleset and analyzer DLLs referenced by `al-compile` exist.
In a multi-app workspace, compile shared apps first and copy their fresh `.app`
packages into each dependent app's `.alpackages`.

## Hands-on tutorial: build one small feature

This example adds an optional customer reference to an existing document. Use
your real paths, names, and object range.

1. Initialize the AL app and start OpenCode from that folder:

   ```bash
   git -C /path/to/bc-ai-global submodule update --init
   /path/to/bc-ai-global/init-linux.sh /path/to/MyBcRepo/MyApp
   cd /path/to/MyBcRepo/MyApp
   opencode
   ```

2. Replace every placeholder in `APP_CONTEXT.md`. Fill in `specs/brief.md` and
   `specs/tech-design.md`, then add `001-customer-reference` with status `todo`
   to `specs/roadmap.md`. Review this project constitution:

   ```text
   /al-spec-init
   ```

    Resolve every `block` and `warn`, then rerun the command to `outcome: pass`.

3. Draft and review the feature spec, including the durable test decision:

   ```text
   /sdd spec 001-customer-reference

   Add an optional Customer Reference that a sales user can enter on the
   document card. It remains visible after reopening the document.
   Automated tests: no. Owner/date: <name>, <YYYY-MM-DD>.
   Reason: verify this prototype with the sandbox manual recipe.
   ```

   Check `specs/features/001-customer-reference/spec.md`. Create `approvals.md`
   from `specs/templates/feature-approvals.md`. Resolve findings and rerun the
   Spec gate to pass. Without changing `spec.md`, run `sha256sum spec.md` and
   record the review outcome, reviewer/date, and digest in `approvals.md`. Spec
   approval is a hard stop:

   ```text
   I approve the feature spec. Continue to Plan.
   ```

   Record the human approver/date and repeat the exact same Spec digest in
   `approvals.md`. Recompute it before Plan; a mismatch invalidates approval and
   requires review, hashing, and approval again.

4. Draft and review the technical plan:

   ```text
   /sdd plan 001-customer-reference
   ```

   Check `plan.md` and `tasks.md`. Verify that object IDs are in range, standard
   BC is reused, and the task list matches the no-tests decision. The mechanical
   stage checks the deterministic parts first; resolve findings and rerun the
   Plan gate (mechanical, then semantic) to pass. Without changing either file,
   run
   `sha256sum plan.md tasks.md` and record the review, reviewers/dates, and the
   two
   separate digests in `approvals.md`. Plan approval is the second hard stop:

   ```text
   I approve the plan and tasks. Continue to Implement.
   ```

   Record the human approver/date and repeat both exact digests in
   `approvals.md`. Recompute all approved digests before implementation. Any
   later edit invalidates the affected review and approval evidence.

5. Implement the approved tasks and run the pre-Test semantic review:

   ```text
   /sdd implement 001-customer-reference
   ```

6. Create `specs/features/001-customer-reference/validation.md` from
   `specs/templates/feature-validation.md`, then compile and run the applicable
   verifiers:

   ```text
   Use the al-compile skill for this app and classify every diagnostic against
   the existing baseline.
   ```

   Record the initial pre-Test semantic reviewer/date, outcome, and
   implementation revision in `validation.md`. For this no-tests example, run `al-code-quality-reviewer` and
   `al-readability-checker` in parallel. Resolve their findings and run both
   again. For an opted-in test feature, run `al-test-runner` immediately after
   compile and require every selected test to execute and pass before the test
   coverage and quality verifiers. The runtime runner may use AL MCP
   `al_run_tests`. `tests=no` means no runner; `tests=yes` with no runner is a
   blocking failure or partial result, not a skip. Preserve the runner's
   BCQuality outcome and `summary.execution.status` verbatim. For a UI feature, choose a quick manual
   recipe or, after publishing to a non-production sandbox, opt into
   `bc-webclient-runner`.

7. Execute the selected manual or web-client verification and record a passing
   result in `validation.md`. Complete both verifier runs and record post-Test-fix
   semantic reruns separately from the initial gate
   after production fixes, update affected documentation, then move the roadmap
   item to `done` and review the AL diff before creating the app repository's
   PR. A recipe that was offered but not executed is not a passing Test result.

`APP_CONTEXT.md`, `specs/`, and the scaffold are normally excluded from the app
repository. Restart OpenCode whenever shared agents, commands, skills, plugins,
or `opencode.json` change.

## Prototype status

This repository is in the prototype stage. Its workflows, prompts, agents, and
quality gates are still being validated and may change. It currently provides the
agentic development scaffold, not a complete Business Central app or a configured
AL-Go pipeline.

Do not assume that this repository can build, test, publish, or deploy an AL app
without first adding the product's `app.json`, AL source, dependencies, and CI/CD
configuration.

## Development model

The spec is the brain, and the agent is the muscle. Durable decisions live under
`specs/`; OpenCode reads those artifacts and performs the implementation and
review work.

Each feature follows this sequence:

1. **Feature spec:** define the problem, scope, user flow, acceptance criteria,
   and the durable automated-test decision; bind review and human approval to
   the full-file SHA-256 in `approvals.md`.
2. **Plan:** validate the approved Spec digest, define the standard BC
   functionality to reuse, custom AL objects, object IDs, data model,
   integrations, risks, and test strategy, then bind Plan and tasks approval to
   separate full-file SHA-256 values.
3. **Implement:** write AL only after the spec and plan have been reviewed and
   approved.
4. **Test:** build the app; run opted-in tests; run the exact applicable
   verifier set twice; rerun semantic conformance after production fixes; and
   execute a passing manual or web-client check, all recorded in `validation.md`.
5. **Document:** update feature documentation and the roadmap.
6. **Merge:** review closeout and prepare the PR when requested.

The complete workflow and agent contract are in [AGENTS.md](AGENTS.md).

## Repository contents

- `specs/`: project constitution, roadmap, feature artifacts, and templates.
- `.opencode/agents/`: focused Business Central reviewers and verifiers.
- `.opencode/skills/`: OpenCode skills, including the SDD review gates.
- `.opencode/skills/al-code-review/`: the ADIGO house rules (`SKILL.md`) and the AL style guide (`styleguide.md`), which agents read when writing and reviewing AL.
- `.opencode/commands/`: OpenCode slash commands for the SDD workflow.
- `.opencode/BCQuality-ADIGO/`: vendored BCQuality knowledge and review skills.
- `.opencode/plugins/`: OpenCode automation, including the post-build verifier reminder.
- `opencode.json`: project-level OpenCode configuration.

## OpenCode workflow

Install the [OpenCode CLI](https://opencode.ai), start it from the repository root,
and describe the Business Central product or feature to develop. OpenCode loads
`AGENTS.md`, the local skills, agents, commands, and plugins through
`opencode.json`.

The main workflow command is `/sdd spec|plan|implement <feature-id>`. The
following `/al-*` commands are review-only gates:

- `/al-spec-init`: review `specs/brief.md`, `specs/tech-design.md`, and `specs/roadmap.md`.
- `/al-spec-feature`: review a feature specification against the constitution.
- `/al-plan-feature`: review a feature plan and task list against its specification. It is the semantic stage; the deterministic stage (`al-plan-mechanical`, agent and skill, no slash command) runs first.
- `/al-implement-feature`: review an implementation against its approved artifacts.

OpenCode may also select the matching skill or verifier from a natural-language
request. After an AL build, the post-build plugin reminds the agent to run the
mandatory verifier set. Test agents run only when the feature's durable test
decision is `yes`.

## House rules and the AL style guide

`.opencode/skills/al-code-review/SKILL.md` holds the ADIGO house rules, and
`.opencode/skills/al-code-review/styleguide.md` holds the AL style guide. There is
exactly one copy of each; agents read them both when authoring AL and when
reviewing it, and they outrank BCQuality when the two disagree. Each agent that
writes or reviews AL names the style guide sections it enforces in its own
agent file under `.opencode/agents/`.

The style guide uses ADIGO identifiers in its examples (the `GOX`/`GOXOUT` object
prefix, the `GOXFOU Error` handler, the `ADIGO.ITS.*` namespaces). When adopting
the template in a repo with different conventions, replace those identifiers; the
rules themselves still apply.

## BCQuality

BCQuality supplies machine-readable Business Central guidance that agents cite in
their findings. Reusable runtime review pointers under `.opencode/skills/` point
to authoritative vendored content under `.opencode/BCQuality-ADIGO/`. Full local
governance skills remain in the scaffold. ADIGO-specific house rules remain in
`.opencode/skills/al-code-review/` and take precedence when rules conflict.

The canonical upstream corpus is
[`microsoft/BCQuality`](https://github.com/microsoft/BCQuality). This scaffold
pins the [`GThumeAdigo/BCQuality-ADIGO`](https://github.com/GThumeAdigo/BCQuality-ADIGO)
fork as a submodule because its `custom/` layer is authoritative for ADIGO's
reusable action skills. Update corpus or custom guidance in that fork, merge it
there, then bump the submodule commit in this scaffold. Never edit the vendored
submodule in place as part of a scaffold change.

### Corpus layout and file format

Knowledge files live under `.opencode/BCQuality-ADIGO/<layer>/knowledge/<domain>/`.
The Microsoft layer vendors the domains `performance`, `privacy`, `security`,
`style`, `testing`, `ui`, and `upgrade`. The `community/` layer adds `performance`
and `security` rules. The `custom/` layer adds `api`, `integration`, `operations`,
`performance`, and `process` knowledge plus review and testing skills.

Each rule is an atomic markdown file `<slug>.md` with YAML frontmatter
(`bc-version`, `domain`, `keywords`, `technologies`, `countries`,
`application-area`) and optional `<slug>.good.al.txt` and `<slug>.bad.al.txt`
sibling samples. The samples carry a `.txt` suffix on purpose: `.opencode/` is
symlinked into the AL project folder and `alc` compiles every `*.al` it finds
there, following symlinks, with no exclude mechanism anywhere in the toolchain. A
sample named `*.al` would land in the app's build as a few hundred phantom
warnings. Keep the suffix when re-vendoring from upstream BCQuality, and rename
any new sample to match.

### How agents consume and cite it

An adapter invokes `.opencode/BCQuality-ADIGO/skills/entry.md` first with a
`requested-skill-id`, including its index preparation. Entry takes that exact
route rather than fuzzy-selecting a predetermined target. The action skill uses
READ (`skills/read.md`) for applicability and precedence, follows Source,
Relevance, Worklist, and Action, then emits DO (`skills/do.md`) output.

For a knowledge-backed finding, `id` equals the primary reference's
corpus-relative path, for example `microsoft/knowledge/<domain>/<slug>.md`.
Every `references[].path` stays corpus-relative to `.opencode/BCQuality-ADIGO/`;
do not prefix it with the checkout path. Do not paraphrase a rule you can cite.

House-policy findings are not BCQuality knowledge findings. Emit them in a
separate local governance or reviewer report with `severity: block | warn |
info`, a `house:` rule, message, and location. Do not place scaffold paths in a
BCQuality DO `references` array and do not invent a corpus citation for a house
rule. An adapter that applies both sources returns the action skill's DO report
and, only when needed, a separately labelled local report.

Runtime agents with corresponding custom action skills are thin adapters. They
build complete task context in memory or a temporary path outside the workspace,
then run `.opencode/BCQuality-ADIGO/tools/route_entry.py` directly, or through
`python3` when it is not executable, with an exact `requested-skill-id`. They
never create a workspace context file or fuzzy-route. Each follows only its
routed action skill and READ/DO, loads the local house-rule overlay when its
role requires it, and does not carry duplicate review checklists or legacy JSON
contracts in its prompt.

Implementing agents consume the corpus directly instead: they search the
knowledge folders by frontmatter keywords, follow the `good.al.txt` samples,
avoid the `bad.al.txt` patterns, and cite corpus-relative paths. This applies in
non-SDD sessions too. The `microsoft-learn` MCP server is the companion source
for platform API behavior; verify before relying, the same way.

## Serena infrastructure

Serena is wired in as an opencode MCP server in this scaffold's project-level
`opencode.json` (which is symlinked into every initialized AL app) with
`--context ide --project-from-cwd`, so it applies to every AL repo initialized
from this scaffold. The other AL MCP servers (`al-mcp`, `microsoft-learn`,
`alcops`, `al-dependency`, `nab-al-tools`, `playwright`) are registered in the
same file, so non-AL sessions start without them. It provides LSP-backed AL symbol
tools plus project memories under `.serena/memories`.

- The AL extension binaries come from the installed VS Code AL extension
  (`ms-dynamics-smb.al-*`); if that is absent, Serena downloads a pinned
  version to `~/.serena/ls_resources/`. Optional `AL_EXTENSION_PATH` override
  or `ls_specific_settings.al.al_extension_version` for a different version.
- The AL language server expects an `app.json` at the project root and the
  workspace root has none, so the `al/manifestMissing` warning on startup is
  expected and harmless. Symbol extraction is per-file (each `.al` file is
  opened before symbol requests), so document symbols and indexing work
  regardless. `get_symbols_overview` on a non-AL file such as `app.json` errors
  by design; that is not a misconfiguration.
- The index is pre-built and Serena refreshes it as files change. After a
  rebuild of the worktree or a large branch switch, re-run
  `serena project index` from the **workspace root**.
- `.serena/` is listed in `.git/info/exclude`, matching the scaffolding
  policy. The global dashboard stays off (`web_dashboard_open_on_launch:
  false` in `~/.serena/serena_config.yml`) so MCP starts do not open a
  browser. Open it manually at `http://localhost:24282/dashboard/`.

## Intended use

This prototype is specifically intended for ADIGO's Business Central product
development. It contains ADIGO conventions and should not be treated as a generic
community template without first replacing those conventions.

## License

The vendored BCQuality content carries its license under
`.opencode/BCQuality-ADIGO/LICENSE`.
