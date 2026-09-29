# Risk-adaptive agent workflows: assessment and migration plan

Status: **approved by the repository owner on 2026-09-29**, including option B
and the five defaults in section 12. Approval: “ich gebe den plan frei”.

Implementation branch: `refactor/agent-workflows`, isolated checkout
`/tmp/opencode/bc-ai-agent-workflows`. Baseline ref:
`baseline/agent-workflows-2026-09-29` at the starting commit below.
The original source checkout remains at that baseline for linked consumers.

Prepared: 2026-09-29. Scope: the shared `bc-ai-global` scaffold, its installed
consumers, and the boundary with machine-local agent configuration.

For plan approval, start with [the recommendation](#2-recommendation-and-alternatives),
[target behavior](#7-target-behavior), [migration steps](#11-migration-sequence-and-commit-boundaries),
and [the five decisions](#12-compatibility-risks-and-approval-decisions).
Sections 3–6 retain the audit evidence; sections 8–10 are the implementation
inventory; sections 13–14 define comparison and acceptance.

## 1. Baseline and evidence boundaries

- Repository: `/home/greg/Repos/AI/bc-ai-global`.
- Branch: `master`, one commit ahead of the locally recorded `origin/master`.
- Starting commit: `f696dc480b8ee8df8bbbba7c694747aafe6e5f19`.
- BCQuality submodule: `dcc2f1fa8271f8fb70711d62a08fb33435e1ce36`.
- Initial tracked/untracked Git status was clean. No fetch, branch change,
  commit, push, merge, or change to an installed consumer was performed.
- `refactor/agent-workflows` was absent from local branches during assessment.
  Recheck local and known remote-tracking names before implementation. A remote
  name not fetched locally has not been checked.
- The root `APP_CONTEXT.md` and constitution are **consumer templates**, not a
  filled-in constitution for this infrastructure repository. There is no AL
  `app.json` here. Do not manufacture an AL feature or AL build for this work.
- This document deliberately lives in `plans/`, outside installer inputs.
  `init-linux.sh:14-18,48-68` recursively copies `specs/` and `DOCS/`; putting
  scaffold-maintenance plans there would distribute them into product apps.

Evidence labels used below:

- **S**: source/configuration fact, with baseline-relative file/line references.
- **E**: command executed in this assessment, with its actual result.
- **H**: hypothesis or plausible consequence, not measured in agent task runs.
- **P**: proposed behavior, test, or target, not an achieved result.

References describe the starting revision, even after files move. This assessment
is not a statistical evaluation of the old or proposed workflow. No session-cost,
review-precision, or human-time measurements were available.

## 2. Recommendation and alternatives

**Keep SDD, replace uniform orchestration with three risk-based paths, and
separate shared source from consumer runtime state.** Retain native OpenCode
agents/skills and the BCQuality corpus. Make executable checks the normal
verification foundation, with independent judgment concentrated where it adds
information. Do not build a new scheduling service, workflow DSL, or agent DAG.

| Option | Benefit | Cost and limitation | Decision |
|---|---|---|---|
| A. Trim prose and relax a few gates in place | Cheapest initial edit; commands and symlinks unchanged | Shared writable runtime, template/history problems, scattered policies and implicit tool versions remain | Useful first experiment, insufficient destination |
| B. Risk-adaptive workflows plus source/runtime separation | Addresses repeated reviews, excessive small-task process, reproducibility and safe distribution together | Installer migration and compatibility tests; moderate file movement | **Recommended**, staged so workflow effects can be measured separately |
| C. New harness-neutral orchestration engine and fully generated adapters | Could enforce all transitions and support several harnesses | New scheduler, state schema, permissions model and maintenance burden; unsupported by local benefit data | Reject for this iteration |

The recommendation does **not** assume that a stronger model makes controls
unnecessary. Keep approval for changed intent, semantic navigation, build/analyzer
evidence, truthful execution status, and risk-specific checks. Test reductions in
delegation, document duplication and generic reviewers against the same models.

## 3. Existing system inventory

### 3.1 Ownership and installation

| Component | Source or artifact | How used / distributed |
|---|---|---|
| `AGENTS.md`, `CLAUDE.md`, `opencode.json` | Tracked shared source here | Installer creates app-folder symlinks; editing source affects all linked apps |
| `.opencode/agents/` | 24 tracked agent prompts | Discovered by OpenCode; descriptions advertised, body used on dispatch; all on-disk pins currently `openai/gpt-6-sol`, `high` |
| `.opencode/skills/` | 26 tracked skills plus companion rules/scripts | Native discovery plus explicit `skills.paths`; descriptions are startup context, bodies loaded on demand |
| `.opencode/commands/` | Five tracked commands | `/sdd` coordinates; four `/al-*` commands invoke review agents |
| `.opencode/plugins/post-build-verify.ts` | One tracked plugin | Explicit registration and native plugin discovery; actual duplicate execution has not been demonstrated |
| `.opencode/BCQuality-ADIGO/` | Pinned Git submodule, separately maintained | Runtime review routing and domain knowledge; fork changes require a separate change and submodule bump |
| `.opencode/serena-al/bin/linux/Microsoft.Dynamics.Nav.EditorServices.Host` | **26-line shell bridge**, not a vendored Microsoft binary | Resolves installed extension host or DLL and executes it |
| `APP_CONTEXT.md`, `specs/`, `DOCS/` | Tracked blank templates here | Copied without overwriting existing regular files; existing symlinks are left alone |
| Consumer `SDD-*.code-workspace` | Generated by installer | Retains source settings, replaces folders with one app; overwritten on rerun |
| Consumer `.git/info/exclude` block | Local installation mutation | Managed marker block is inserted/resynchronized in the common Git directory |
| `.opencode/package.json`, lockfile, `node_modules/`, `.gitignore` | Present but Git-ignored installation artifacts | Plugin dependency is locally `@opencode-ai/plugin` 1.18.23; not a reproducible tracked dependency declaration |
| `.serena/project.yml` here | Tracked local scaffold project config | Selects TypeScript, not AL; installer does not distribute `.serena/` |
| `.alpackages/`, `.snapshots/`, browser artifacts | Local operational locations | Not authoritative policy or product requirements |

Evidence: `init-linux.sh:8-18,25-68,125-147,154-265`, `README.md:55-108,335-379`,
`opencode.json:3-8,133-218`, `.serena/project.yml:38-39`, Git inventory and status.

One consumer was positively verified by resolved symlink targets:
`/home/greg/Repos/ADIGO/BAU.ProjectConstruction/ADIGO.BAU.Interfaces.GAEB/{AGENTS.md,.opencode}`
points into this shared checkout. Other discovered `AGENTS.md` files did not
establish a link to this checkout. Hidden/excluded paths make that discovery
incomplete. There is no installer-maintained consumer registry. Do not claim
that the one confirmed app is the only consumer.

### 3.2 Supported environments and loaded content

**OpenCode is the implemented environment.** `README.md:3-6` names it;
`opencode.json` wires MCPs and the plugin. Claude Code has a ten-line
`CLAUDE.md` bridge importing `AGENTS.md`, but no tracked `.claude/` agent,
command, hook or MCP adapter. The shared contract still requires OpenCode-named
subagents. This is a documentation bridge, not demonstrated workflow parity.
VS Code workspace generation is supported; a complete Copilot adapter is absent.

Load/dispatch chain:

```text
Global/remote/managed host settings + project opencode.json
  -> AGENTS.md in main session
  -> advertised descriptions of agents, skills and connected MCP tools
  -> native commands and plugin registration
  -> request selects workflow / agent / tool

/sdd
  -> full sdd skill (545 lines, reloaded after compaction)
  -> constitution + app context on first feature entry
  -> delegated draft reads gate checklist
  -> separate gate reads artifacts and relevant source
  -> approval/loop-state records maintained by coordinator

BCQuality adapter
  -> exact-id router + separately required index preparation
  -> expected-target check
  -> routed action + READ/DO contracts
  -> applicable knowledge articles + local house overlay
  -> BCQuality JSON report, plus a separate house report if needed

successful Bash-recognized compile
  -> post-build plugin appends verifier/Hunk instructions
  -> coordinator is expected to dispatch and record checks
```

Sources: `AGENTS.md` sections Spec-Driven Development, Outside the SDD loop,
Runtime reloads; `sdd/SKILL.md:26-116,170-322,446-484` under `.opencode/skills/`;
`al-code-quality-reviewer.md:12-38` under `.opencode/agents/`;
`.opencode/plugins/post-build-verify.ts:93-136`.

Main-session startup context is more than `AGENTS.md`: agent descriptions contain
multi-paragraph triggers/examples, seven MCP servers are enabled, and external
skills are discoverable. The current session advertises the global `hf-cli`
skill. Global OpenCode directories also contain `herdr-agent-state.js` and
`notification.js`; their execution behavior was not audited. `opencode debug
config` was attempted twice with output filtering. It returned exactly 65,536
characters and truncated JSON, so a complete resolved-config inventory could
not be established. The visible top-level model was
`openrouter/z-ai/glm-5.3-flash`; that does not establish the model of this live
session or a dispatched reviewer. On-disk Sol pins also differ from some agent
descriptions advertised in this session. Restart and resolved-runtime checks
matter; do not infer actual model use from prose alone.

### 3.3 Workflow and minimum process

| Request | Current required path |
|---|---|
| Question / lookup | No SDD artifacts; semantic AL navigation first |
| Trivial one-line AL fix | Coordinator may edit; compile; both general reviewers still required |
| Other quick fix | Delegate implementer; compile; code-quality + readability; specialists as triggered; Hunk for non-obvious changes |
| Feature, including a small one | Delegated Spec draft; Spec review; human approval; delegated Plan/tasks draft; mechanical review; semantic review; second human approval; delegated implementation; semantic conformance; compile; two general reviewers; executed client verification; documentation and roadmap |
| Feature with tests=yes | Add test writing, runtime execution, coverage and test-quality reviews |
| Changed approved behavior | Amendment, artifact rewrite, relevant gates, fresh hashes and human reapproval |

On a clean, no-tests feature with an existing constitution, the prescribed flow
has **at least nine agent dispatches**: three authoring/implementation calls and
six reviews (Spec, mechanical Plan, semantic Plan, implementation, quality,
readability). This is a static count, not observed latency. Specialists, repairs,
API retries and UI automation add work. Each feature normally has five files:
`spec.md`, `plan.md`, `tasks.md`, `approvals.md`, `validation.md`.

The existing workflow already avoids repeating an identical clean pass. It also
has a three-run *target*. The issue is not an absence of all stop rules: mechanical
failures do not count against that target, full applicable sets must confirm
fixes, and the wording permits continued findings from additional source facts.
See `sdd/SKILL.md:269-284,324-398` and compare
`al-plan-feature/SKILL.md:86-97`, which restricts new rerun scope more tightly.

## 4. Findings with repository evidence

### F1. The short path is not proportional to risk (S, cost impact H)

`AGENTS.md`, Outside the SDD loop, ties delegation to a one-line threshold and
requires two reviewers even without tests. `custom-al-implementer.md:53-59`
avoids documents, but retains broad knowledge/report duties. There is no
explicit risk classifier distinguishing a caption correction from a one-line
`Commit`, permission or posting change. The binary feature/bug boundary can
over-process harmless changes and under-plan dangerous bug fixes.

**Action:** risk/uncertainty/scope routing, not line-count routing. Remove generic
mandatory delegation for small work; retain escalation when inspection reveals risk.

### F2. Cheap tool feedback comes after an expensive semantic gate (S)

`sdd/SKILL.md:234-248` and `al-implement-feature/SKILL.md:18-20,52-54` place
semantic implementation review before compile/test. A reviewer can inspect
unbuildable code and must return after behavior-changing Test fixes.

**Action:** compile and relevant executable tests before final semantic review.
An early architecture review remains useful on critical work, without pretending
to be final implementation verification.

### F3. Rerun fan-out and advisory findings can create avoidable loops (S, frequency H)

`sdd/SKILL.md:273-278,324-365` retains the exact original verifier set after
fixes/waivers. `al-plan-mechanical/SKILL.md:41-42` reruns everything every time.
`al-spec-feature/SKILL.md:99-113` gates on every block/warn. The general instruction
to resolve every finding or obtain a waiver can promote optional style judgments
into process obligations. BCQuality distinguishes capped agent judgments from
direct evidence (`custom/skills/review/al-code-quality-reviewer.md:55-61`).

**Action:** correctness/contract failures block; preferences do not. Confirm
changed evidence and affected review scope. Use a hard repair budget that counts
mechanical and semantic attempts, with no automatic pass when the budget expires.

### F4. Rules have one nominal authority but several maintained restatements (S)

Verifier/hash/approval policy is repeated in `AGENTS.md`, `README.md:302-333`,
`specs/README.md:25-78`, `.opencode/commands/sdd.md:10-31`, the SDD skill,
templates, and plugin strings. A change must keep all of them aligned. Model
policy lives in 24 frontmatters and is narrated in SDD/README/agent descriptions.
Several gate agents repeat record bookkeeping and digest instructions.

Concrete drift:

- `al-code-review/SKILL.md:81,155` bans `Management` names but recommends a
  Management/Handler codeunit in subscriber guidance.
- Its API-query-specific prohibition at line 74 broadens to all API definitions
  at line 134 and all plans in `al-plan-mechanical/SKILL.md:67`. An API page
  must not inherit a query-only check by accidental wording. Microsoft documents
  [ODataKeyFields as a Page property](https://learn.microsoft.com/dynamics365/business-central/dev-itpro/developer/properties/devenv-odatakeyfields-property)
  and [recommends it for custom API pages](https://learn.microsoft.com/dynamics365/business-central/dev-itpro/developer/devenv-develop-custom-api#creating-api-pages).
- `styleguide.md:674-677` recognizes stateful multi-public codeunit exceptions;
  `al-code-review/SKILL.md:79` mentions only helpers. Explicit precedence resolves
  the policy formally, but consumers still pay to reconcile the duplicate.
- `sdd/SKILL.md:415-416,442-444` and `specs/README.md:65-70` rely on Git history
  for rewritten specs, although `README.md:99-108` explicitly says those specs
  are excluded and not protected by Git.
- The SDD skill description still says schema changes are free, while its
  operative compatibility section makes this conditional on app-local policy.

**Action:** authoritative workflow files, a scoped AL house overlay, links in
commands/docs, and executable tests of routing and compatibility contracts.

### F5. Generic reviews overlap and can demand architecture not declared locally (S)

The two general reviewers have intentionally different remits, so they are not
complete duplicates. They still both inspect procedure size/nesting:
BCQuality `custom/skills/review/al-code-quality-reviewer.md:38-47` and
`al-readability-checker.md:38-43`. The common house overlay remains applicable
to both (`al-code-review/SKILL.md:38-44`). More importantly, the code-quality
worklist references a project's `IDataAccess` interface (`...reviewer.md:40,59`),
which the local app template does not establish. That can motivate unnecessary
abstractions if treated as universal. The 1,501-line style guide also mixes
portable conventions, product-specific examples, structural preferences and
platform behavior. Example code at `styleguide.md:719-743` includes direct record
modification and a bare `Error`, despite more restrictive generic rules.

**Action:** one bounded change reviewer for normal behavior changes; specialist
checks only for explicit risk. Convert architectural preferences into app-local
decisions or non-blocking advice. Check existing analyzer coverage before
inventing custom lint. Keep business correctness outside line-count heuristics.

### F6. Enforcement is mostly prompt-driven, despite mechanical terminology (S)

`al-plan-mechanical/SKILL.md:39-83` is a checklist executed by a frontier model,
not a deterministic program. `artifact_hash.py` computes hashes but does not
authenticate an owner, validate the approval ledger, or prevent edits. The
post-build plugin appends text (`post-build-verify.ts:109-133`); it neither runs
reviewers nor blocks completion. It matches only Bash command patterns, so it
does not cover MCP builds and has no task/revision state. Conversely it can
expand a build-only request into a review workflow.

**Action:** make a small verification command return machine-readable execution
results. Keep approvals semantic and human-owned. Do not call reminders hard
gates. Remove policy duplication from the hook rather than growing its regex parser.

### F7. Distribution couples unrelated consumers and weakens rollback (S)

`init-linux.sh:8-13,25-46` links all of `.opencode` to one mutable source tree.
Playwright output is `.opencode/webclient-runs` (`opencode.json:205-206`) and its
browser profile is one absolute user-wide path (`:203-204`). Package installs
inside `.opencode` share that target too. BCQuality index preparation writes into
the live corpus by default (`skills/entry.md:37-50`,
`tools/build_knowledge_index.py:157-162`). Parallel consumer interference is a
plausible risk, not an observed corruption incident.

The installer changes excludes and workspace output **before** it discovers
later path conflicts (`init-linux.sh:253-263`). Its workspace writer uses strict
`jq` JSON, while VS Code commonly uses JSONC; target names use only two segments
and are overwritten (`:158-218`). Existing tests do not exercise workspace
creation, name collisions or JSONC. `exclude:18,25` hides all XSD/PNG files,
not just generated agent artifacts.

**Action:** immutable release source, app-local runtime directories, explicit
consumer manifest, preflight before mutation, managed-file-only updates and
rollback. Preserve private app artifacts and back them up explicitly.

### F8. Tool setup is version-sensitive and not reproducible from the repository (S, E)

- `opencode.json:142` takes the first app at depth two with `-quit`, contrary to
  multi-app discovery in `AGENTS.md`; compile discovery rejects ambiguity at
  depth three (`compile.sh:16-32`). An installed app-root session usually avoids
  the problem, but workspace-root sessions do not.
- Seven MCPs are enabled globally for every scaffolded session. npm MCP commands
  are unpinned, Playwright explicitly uses `@latest` (`opencode.json:160-217`).
- Serena executable/extension bridge and browser profile use absolute personal
  paths (`opencode.json:183,190,204`), although README describes dynamic fallback.
- `compile.sh:37-61` chooses the newest installed compiler and a fixed ten-DLL
  list. The ruleset is resolved carefully, but the analyzer set is not actually
  read from each app's settings. `AGENTS.md` promises per-app settings and full
  parity more broadly than the wrapper establishes. No AL-Go pipeline exists
  here to demonstrate the asserted universal `failOn: warning` parity.
- Global ALTool 17 and extension ALTool 18 expose different commands (section 5).
  The Serena bridge is still used by the configured integration; newer LSP
  availability alone does not make that bridge obsolete.

**Action:** tool doctor and capability probes, explicit app set and toolchain
selection, version-pinned optional integrations. Keep wrapper/Serena until
replacement parity is tested. Separate tool replacement from workflow A/B tests.

### F9. Review-only and protected-file boundaries are inconsistent (S)

SDD gate agents declare deny-by-default permissions
(`.opencode/agents/al-sdd-reviewer.md:6-27`); general reviewers only say “do not
modify source” (`al-code-quality-reviewer.md:34`, `al-readability-checker.md:27`).
`opencode.json:25-28` denies corpus edits through the edit tool, but broad
`python3`, `sed`, `rm`, `git`, `fish` and `/tmp/*` shell permissions can still
write there (`:45,78,95,101,121-130`). These are not an OS write boundary.

**Action:** bounded read-only review tools and read-only source snapshots for
tests; avoid a sprawling command denylist presented as a sandbox. Reviewers that
need generated indexes receive prebuilt/run-local evidence. Preserve the owner's
explicit restrictions on commit, push, merge and destructive operations.

### F10. Useful execution contracts exist, but coverage and infrastructure gaps remain (S, E)

Positive assets include tested hash canonicalization, tested ruleset resolution,
failure-first build detection, exact BCQuality target guards, dependency-order
instructions, and the distinction between executed tests and a suggested recipe.
Do not discard these merely because they occupy files.

Gaps: there is no tracked aggregate verification command/CI, no executable
approval-transition validator, no demonstrated end-to-end MCP/reviewer permission
test, and no local AL product suite. The router imports PyYAML and routes only;
it does not prepare the knowledge index (`route_entry.py:11,207-216`), although
adapter wording can sound as if one command does both. Index preparation remains
a separate prompt obligation. The vendored test-runner action has inconsistent
no-runner wording (`custom/skills/testing/al-test-runner.md:50-52`); the scaffold
correctly overrides this with blocking required execution. Fix upstream rather
than copying a divergent runner contract locally.

## 5. Executed checks and technical observations

| Check executed on 2026-09-29 | Result | What it proves / does not prove |
|---|---|---|
| Git status, branch, HEAD, submodule status and tracked inventory | Clean baseline; refs in section 1 | Source baseline, not global installation reproducibility |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .opencode/tests -p 'test_*.py'` | **9 passed** | Artifact-hash fixtures |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .opencode/skills/al-compile/tests -p 'test_*.py'` | **22 passed** | Wrapper/ruleset fixtures using fake compiler/analyzer files, not real AL builds |
| `node --experimental-strip-types --test .opencode/tests/post-build-verify.test.ts` | **7 passed** | Command/result recognition and appended reminders, not actual reviewer execution |
| `bash .opencode/tests/init-linux.test.sh` | **Six fixture functions passed** | Root/nested/worktree installs, existing-file preservation, malformed exclusion failure; no real consumer installation |
| Node test startup | `MODULE_TYPELESS_PACKAGE_JSON` warning | Dependency/package metadata cleanup needed; test results remain passing |
| `opencode --version` | **1.18.33** | Local CLI version |
| `al --version` | **17.0.34.45391** | Global .NET tool version; `al version` was rejected |
| `al launchmcpserver --help` | STDIO and multiple project arguments supported | CLI surface only |
| `al launchlspserver --help` | General help, no such command in command inventory | No supported LSP launcher on this selected global version |
| ALTool 17 no-project STDIO handshake | Failed before initialize; “No projects specified” | This installed version differs from current no-project-start documentation |
| `dotnet <installed-extension>/bin/altool.dll --version` | **18.0.41.45789** from extension **18.0.2732683** | Separate installed toolchain |
| Extension ALTool `launchlspserver --help` | Supported; includes workspace/settings options | Launcher exists, semantic behavior not exercised |
| Extension ALTool 18 initialize + `tools/list`, no project | **Succeeded**, 16 tools | Server capability discovery only |
| ALTool 18 tool list | Includes `al_run_tests`, `al_symbolrelations`, `al_getnextobjectid`, `al_writetranslation`, build/diagnostics/symbol/auth/publish tools | Names exist; no test, symbol query, publish, or translation operation executed |
| Required compiler/analyzer directory inventory | Installed DLL layout includes the wrapper's requested ten DLLs | Presence, not analyzer compatibility or CI parity |
| Sanitized resolved-config probe | JSON truncated at 65,536 characters | Full merged configuration remains unverified |
| Hunk session discovery | One session in another app checkout | No matching scaffold session; no notes published or foreign viewport changed |

No AL code was compiled, no BC tests were run, no sandbox was published to,
and no agent-review accuracy was measured. Existing infrastructure tests wrote
temporary fixtures only. The MCP probe used an ephemeral script under
`/tmp/opencode/`, disabled telemetry and invoked only initialize/tools/list.
Machine-global auth/configuration files were not dumped. Tool startup may still
use the tools' ordinary local logging/cache behavior.

## 6. Research comparison

Primary pages were fetched on 2026-09-29. They are not assumed to be frozen at
the original research date. Distinguish author practice from controlled evidence.

| Source | Evidence type and relevant observation | Consequence here |
|---|---|---|
| [Waldo / iFacto](https://waldo.be/2026/06/29/the-waldo-way/) | Experience report: shared playbook improves adoption; explicit ownership/adoption tradeoff | Keep shared distribution and conventions, not every task-level ceremony |
| [Katson](https://katson.com/spec-driven-development-the-way-to-build-apps-with-agents/) | Experience/workshop report: durable constitution and feature Spec → Implement → Test → Docs → Merge | Preserve intent and persistence; no evidence for mandatory separate Plan/tasks or multiple draft reviewers on every feature |
| [Babić](https://vjeko.com/2026/07/21/i-dont-trust-my-agents-either/) | Experience report: elaborate orchestration, isolated meaningful red/green tests, distinct reviewers, bounded retries | Supports critical-task rigor. Does not establish that the same pipeline is cheapest for small changes. His text also favors relevant reruns rather than restarting the plan |
| [Bakkensen](https://fbakkensen.github.io/ai/development/2026/07/31/ai-software-factory-automate-execution-not-decisions.html) | Experience report: larger-feature factory; decisions human, execution automated; small changes distinguished | Route by decision density/risk. Do not infer that he recommends removing all reviews from bug fixes |
| [Claude Code best practices](https://code.claude.com/docs/en/best-practices) | Manufacturer guidance: plan unclear work, directly execute bounded fixes, keep startup rules short, verify with executable feedback; warns of over-engineering from reviewers asked to find gaps | Supports compact startup, direct lane, evidence-first and correctness-limited review. Not a causal benchmark of this scaffold |
| [Boris Tane](https://boristane.com/blog/how-i-use-claude-code/) | Experience report: written research/plan and 1–6 annotation rounds that inject owner knowledge; favors long sessions | Keep owner decisions and annotations. Rephrasing by fresh agents without new evidence is not equivalent. No universal session-length conclusion |
| [BC-Bench v1](https://arxiv.org/html/2608.20851v1), §§3.4–3.6,4.1,4.4,5.2 | 101 curated single-bug tasks, five runs; four matched model/harness comparisons; most analyzed failures were localization or semantic errors, not compile failures | Model improvement is a hypothesis to test locally. Build-only is insufficient. Neither feature planning, upgrades, this SDD process nor present model pins were tested |
| [Microsoft AL agent tools](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/al-agent-tools/al-agent-tools-overview), [ALTool](https://learn.microsoft.com/dynamics365/business-central/dev-itpro/developer/devenv-al-tool) | Platform documentation: extension 17+ overview, separate MCP and LSP surfaces, multi-project input, tools/list discovery | Use installed capability probes. Current overview omits some tools actually listed by local ALTool 18; its no-project behavior is not true of local ALTool 17 |
| [Hougaard](https://www.hougaard.com/how-to-use-the-altool-mcp-server-for-claude-code/) | Retrieved page links a video demonstrating integration; no transcript inspected | Feasibility pointer, not version/behavior proof |
| [OpenCode configuration](https://opencode.ai/docs/config/) | Manufacturer docs: merging of global/project/custom/managed config and external directories | A worktree or `OPENCODE_CONFIG` alone does not isolate experiments; verify the loaded sources |

Local evidence for historically useful controls is limited but real:
`sdd/SKILL.md:334-339` records a twelve-round spec-loop failure;
`al-code-review/SKILL.md:92-100` records an API-semantics mistake. These motivate
first-pass investigation and API verification, not an assumption that every
future task needs the entire historical response. No before/after data proves
that the current added rules solved those failures.

## 7. Target behavior

### 7.1 Routing: three paths, no numerical risk scoring system

At the start of implementation work, inspect the relevant code and state the
path with a one-sentence reason. The owner can choose a more rigorous path.
Reclassify when evidence changes. A few lines can still be critical.

| Path | Selection | Required artifacts and flow |
|---|---|---|
| **Direct** | Clear existing intent; bounded, reversible change; understood impact; no critical risk | Request/issue is sufficient intent. Inspect → implement in main session → applicable executable checks → focused self-check → concise result. No new SDD folder, compulsory delegate or general reviewer |
| **Compact SDD** | Bounded behavior change, known architecture, acceptance criteria can be settled | One `spec.md` with intent, non-goals, affected scope, brief approach, risks and verification; one human approval; implement → compile/relevant tests → one independent change review → closeout in `validation.md` |
| **Critical SDD** | Posting/accounting invariants, transaction/retry boundaries, tenant/company scope, effective permissions, released data/schema upgrades, public contract changes, hot-path performance, broad dependent-app impact, or material unresolved design | Investigate affected paths and invariants → `spec.md` + focused `plan.md` → independent design review → human approval → staged implementation → executable evidence → independent conformance/correctness review plus distinct risk specialists → `validation.md` |

Critical triggers are semantic: merely renaming a local variable in a posting
file need not become critical once references prove no behavior change. Conversely
altering one posting condition is critical. Unknown persisted-data or public
consumer impact cannot be routed Direct by assuming it away. Unclear but harmless
work first gets a bounded investigation, not automatic full critical governance.

Examples:

- Typo in a tooltip: Direct; compile if AL changed, translation coverage for the
  affected locale as applicable. No general design review.
- Local bug restoring already specified validation with understood callers:
  Direct if verification covers the behavior and no risk trigger applies.
- Optional document field and display behavior: Compact when persistence/public
  compatibility impact is understood; otherwise escalate. A schema addition is
  inspected, not automatically declared harmless.
- Moving `Commit`, changing permission elevation, invoice posting, breaking an
  external API, or transforming released data: Critical even for a tiny diff.

### 7.2 Artifacts, ownership and approvals

- Main agent may research, draft and implement. Delegate for bounded independent
  investigation, context savings or independent review, not as an obligatory
  hop to the same pinned model. Never let a reviewer silently fix its own findings.
- `APP_CONTEXT.md` owns app identity, deployment compatibility and environment
  defaults. Manifest/ruleset own machine facts such as IDs and versions; context
  links rather than maintaining parallel values where possible.
- `specs/brief.md` and `tech-design.md` retain durable product intent and architecture.
  Read relevant portions, not the entire constitution at every small task.
- Compact `spec.md` is normally one to two pages. This is a size expectation,
  not a gate that rejects a useful extra paragraph. Approach/tasks fit in it.
- Critical `plan.md` contains only decisions the spec cannot settle: invariants,
  transaction/data lifecycle, APIs/events, permissions, dependency impact,
  migration/recovery and a checkable implementation sequence. No separate
  `tasks.md` unless work distribution genuinely needs it.
- One approval over the coherent spec/plan packet by default. Separate product
  and technical approvals only when there really are two unresolved decisions.
  A behavior change still needs explicit approval; “looks good” from a model
  cannot approve intent.
- Record approval against the reviewed immutable artifact snapshot in
  `validation.md`: owner/date and content digest. Snapshot and hash once at the
  boundary, verify before implementation/resume, not independently in every
  reviewer. Do not hash progress bookkeeping together with approved intent.
- Material intent/compatibility changes reopen approval. Internal refactoring
  within approved boundaries does not automatically amend a technical inventory.
- Preserve old five-file features and `sdd-artifact-v1` evidence. Existing active
  features finish under the old contract unless explicitly migrated and approved.
  Never auto-convert old approvals into new approvals.
- Closeout records only relevant commands, results, scope and unresolved items.
  No user guide or roadmap edit solely to satisfy a generic task template.

### 7.3 Verification and testing policy

Separate **running existing checks** from **authoring new tests**. Proposal:
run applicable existing tests whenever feasible and relevant, even if no new
test writing was opted in. New automated test creation remains explicit opt-in,
inherited from an app default or decided for the task. This is an intentional
change from the present all-or-nothing `tests=no` behavior and needs plan approval.

For every changed behavior, select a verifiable outcome. A compile proves syntax,
types and configured analyzer checks, not financial correctness. Critical work
requires an executable regression/integration proof where practicable; if new
tests are declined or a runner is unavailable, record the remaining risk and
obtain an owner decision on an adequate alternative. Do not silently pass or
automatically write tests against an explicit no. A UI run is required when the
acceptance criteria concern rendered UI behavior, not on every headless feature.

Build evidence must identify app path, source revision/diff fingerprint, compiler
version, analyzer set/versions, ruleset digest, symbol/dependency inputs, command,
exit status and diagnostic counts. Compare new findings to an isolated baseline
with the same toolchain. Retain raw logs; do not equate unchanged rule counts
with identical findings. Avoid `stash -u` as the normal baseline mechanism.

### 7.4 Review boundaries and stopping

- Direct: no compulsory general independent review. Triggered specialist work
  either has a genuinely narrow scope or indicates escalation out of Direct.
- Compact: one fresh `al-change-reviewer` checks acceptance criteria, unexpected
  behavior, affected callers, and concrete maintainability obstacles. It reads
  execution evidence rather than repeating analyzer diagnostics.
- Critical: `al-design-reviewer` checks unresolved design assumptions before
  implementation; `al-change-reviewer` checks final behavior. Add only distinct
  risk checks: posting/transactions, permissions/tenant boundaries, released
  upgrade/API compatibility, actual integration/subscribers or measured performance.
  No umbrella and leaf review of the same risk in parallel.
- Test writing/running remain separate actions. Merge coverage and test-quality
  judgment into one optional test review when new complex tests warrant it;
  preserve “all required tests executed” as executable status, not opinion.
- Every blocking finding needs impact, evidence/location, and a connection to
  acceptance criteria, platform behavior, or an explicit app rule. Stylistic
  improvements and hypothetical abstractions are advisory. “No finding” is valid.
- One complete pass on the reviewed inputs is enough. Following a fix, rerun
  affected executable checks and confirm the affected review responsibilities.
  Retain unaffected evidence with an explicit impact reason. If impact cannot be
  bounded, rerun the whole applicable set. Changed risk triggers add checks.
- **Hard budget:** initial review plus at most two repair/confirmation cycles
  per checkpoint, counting mechanical and semantic repairs. Repeated tool/API
  failure gets one retry, then a blocked/partial result. At exhaustion stop with
  the unresolved evidence and a decision request, never declare success or reset
  the counter by renaming a stage. A new scope/decision starts a new checkpoint
  only with explicit owner agreement.
- Late verified defects must still be reported. A reviewer cannot suppress a
  real correctness issue merely because its first pass missed it; it must label
  the new evidence and the missed scope. This distinguishes defect discovery
  from endless unsolicited improvement.

## 8. Target source and installed structure

Preserve native skill/agent paths where they add value. Move only to establish
ownership or prevent accidental distribution.

```text
bc-ai-global/                         # maintained source repository
  AGENTS.md                          # short scaffold-maintainer contract
  README.md                          # install, support and three-path overview
  plans/                             # maintenance plans, never installed
  runtime/
    AGENTS.md                        # compact consumer bootstrap
    CLAUDE.md                        # explicitly limited compatibility bridge
    opencode.json                    # consumer runtime template and model roles
  templates/
    APP_CONTEXT.md
    specs/                           # product constitution + compact/critical templates
    DOCS/                            # optional product guide starter
  .opencode/
    agents/                          # bounded role adapters, short descriptions
    skills/
      sdd/SKILL.md                    # routing and common intent/approval rules
      sdd/references/{direct,compact,critical,legacy}.md
      al-code-review/{SKILL.md,styleguide.md}
      al-compile/                    # tested build implementation retained
      ...                            # on-demand specialist/knowledge entry points
    commands/                        # thin native dispatchers and legacy aliases
    BCQuality-ADIGO/                  # pinned corpus, unchanged ownership
    tests/
  scripts/
    verify-scaffold                  # one aggregate test/contract entry point
    doctor                           # toolchain and installation capabilities
    install                          # preflight, snapshot release, install/update/rollback
  init-linux.sh                      # compatible forwarding entry point
  opencode.json                      # scaffold-development config, no automatic BC stack
```

Installed app:

```text
<app>/
  AGENTS.md, CLAUDE.md, opencode.json # installer-managed consumer entry points
  APP_CONTEXT.md, specs/, DOCS/       # app-owned, preserved on updates
  .opencode/                         # real app-local directory, not a whole-dir symlink
    agents/, skills/, commands/      # links to an immutable selected release
    BCQuality-ADIGO/                 # selected prepared corpus snapshot
    package.json, node_modules/      # app-local host artifacts if the host creates them
  .agent-state/                      # excluded runtime results, local overrides, install manifest
    install.json
    runs/<run-id>/
```

Release storage is an immutable snapshot keyed by the scaffold commit and
submodule commit, under a configurable user-local data root. The installer
records source revision, real paths, managed file hashes and old link targets.
It is a copier/renderer for configuration and templates, not a prompt-generation
framework. Native prompts retain one maintained source. The entire release
source must be read-only during experiments; writable caches/indexes/results
are run-local or generated before freezing the release.

Do not immediately alter global `~/.config/opencode`, `~/.claude`, Serena
settings, browser authentication profiles, or other apps. A new release reaches
only explicitly selected consumers. `--link-dev` may support a deliberately
live development installation, clearly labelled and never the test default.

## 9. Component disposition and incremental value

Each row states the problem solved, evidence added, remaining need and removal risk.

| Existing component(s) | Disposition and concrete change | Incremental value / removal risk / evidence |
|---|---|---|
| Root `AGENTS.md` | Split maintainer vs `runtime/AGENTS.md`; consumer bootstrap target ≤120 nonblank lines | Keep scope, discovery, safe edits, workflow route. Detailed troubleshooting is occasional; permanent loading has no measured benefit |
| `CLAUDE.md` | Move consumer bridge to runtime; document limited support | Preserves context import; full Claude parity is not silently promised |
| `opencode.json` | Split scaffold-dev/consumer; parameterize paths; selected app set; optional MCP profiles; model settings in one config authority | Reproducible tools and reduced irrelevant discovery. Removing needed tools blindly risks regression |
| `sdd/SKILL.md` | Rewrite compact router/common rules; move path detail to references; keep legacy reference | Durable intent is valuable. Mandatory full-loop reload and delegated drafting supply little new independent evidence |
| Four `/al-*` commands and `/sdd` | Keep names as thin compatibility entry points; route by artifact version/path; avoid duplicated policy text | Existing users retain entry points. Legacy approval checks must remain intact |
| `al-sdd-reviewer`, `al-implement-feature-reviewer` | New core roles `al-design-reviewer`, `al-change-reviewer`; old names remain legacy adapters for one migration cycle | Independent intent checks retained for appropriate work; no mandatory draft review on Compact |
| `al-sdd-mechanical-reviewer`, `al-plan-mechanical` | Retire from new path after specific checks are executable; keep legacy support | Hash and metadata checks should not consume a model. Object-ID availability still needs compiler/symbol evidence, not naive grep |
| `custom-al-implementer` | Optional bounded worker; remove universal delegation and self-review prohibition | Useful context isolation on large tasks; same-model obligatory relay lacks comparative evidence |
| `al-code-quality-reviewer`, `al-readability-checker` | Merge new default remit into change review; old entry points optional/legacy | Avoid overlapping structure/style passes. Preserve correctness and code comprehensibility criteria |
| `al-code-review/SKILL.md`, `styleguide.md`, performance template | Deduplicate; short authoring essentials plus scoped reference sections; fix conflicting examples/rules; map analyzer-covered items | Conventions remain, blanket architecture preferences require app authority. Do not change all code styles during workflow migration |
| `al-integration-pattern-reviewer`, `al-event-subscriber-auditor`, `azure-integration-validator` | Keep, mutually bounded triggers; integration flow, subscriber contract, Azure artifacts | Distinct boundary risks justify specialist review; precision/added detection unmeasured locally |
| `al-multitenancy-reviewer`, `al-permission-set-auditor` | Keep risk modules; test real permission/company behavior and automate inventory where possible | Cross-tenant and authorization errors are not solved by a style review; object permission completeness is partly mechanical |
| `al-upgrade-checker`, `al-obsolete-tracker` | Keep conditional on explicit released compatibility; compare trusted baseline | High removal risk for persisted data/public consumers; no needless migration ceremony for explicitly disposable data |
| `al-performance-reviewer`, `al-table-refactorer` | Keep opt-in/hot-path specialist; metrics and concrete query evidence first | No universal full-table redesign; performance cannot be proved by naming/line counts |
| `al-appsource-validator`, `al-translation-auditor` | Keep release/localization triggers; executable inventory/analyzers first | Distribution/locales require separate evidence; not every local fix is an AppSource review |
| `al-test-writer`, `al-userguide-test-writer` | Keep explicit authoring actions | Useful when opted in; guide-derived TestPage tests are not compulsory scaffolding |
| `al-test-runner` | Keep callable action backed by discovered executable runner and parsed totals | Highest-value behavioral evidence; required skipped/unexecuted tests never become pass |
| `al-test-coverage-validator`, `al-test-coverage-enforcer`, `al-test-validator` | One new test-review role; legacy aliases preserve old behavior until retirement | Separate coverage versus assertion-quality questions retained in one bounded pass; no three generic review hops |
| `bc-webclient-runner`, Playwright | Optional UI profile, per-checkout/run outputs and profile | Rendered behavior needs UI evidence; always-enabled browser increases shared state/startup exposure without universal value |
| `hunk-review` | Keep on-demand presentation; one stable useful checkpoint, not repeated status obligation | Valuable owner annotations; does not add correctness proof. Do not require opening a TUI to finish routine work |
| `al-compile`, `compile.sh`, `resolve_ruleset.py` | Keep and harden; explicit toolchain/analyzer profile, structured evidence, isolated baseline | Already tested, reliable early feedback; replacing it before analyzer parity would discard useful execution |
| `artifact_hash.py` and tests | Keep v1 unchanged for legacy; use simple immutable approval snapshots for new paths | Detects stale approval, not human authenticity. No need for checkbox normalization when progress is separate |
| Post-build plugin | Remove automatic review expansion from default; optionally show only a link to task-local evidence if needed | Reminder is not enforcement; wrapper/results supply more reliable evidence. Test detection can remain legacy-only |
| BCQuality submodule, READ/DO/entry, pointer skills | Keep corpus and exact routing; prepare once per isolated release/context; no in-place vendor edits | Vetted knowledge and provenance valuable. Router is infrastructure, not an independent semantic check |
| AI/Copilot skills (`ai-*`, `copilot-*`), integration/product-MCP skills (`bc-integrations`, `bc-mcp-server-data`, `al-modern-integration-patterns`) | Keep on-demand pointers; remove restated API facts from generic house checks | Narrow domain knowledge; useful only on relevant implementation surfaces |
| Release/operations skills (`al-appsource-validation`, `al-major-release-governance`, `al-go-*`, `al-mcp-server`, `al-page-scripting-e2e`, `bc-extension-test-guide`, `bcquality-integration`) | Keep optional specialist/library entry points | No evidence that deletion improves correctness; keeping full bodies unloaded is inexpensive compared with mandatory invocation |
| Installer, `exclude`, generated workspaces | Replace whole-dir links with snapshot install; managed path exclusions; JSONC-aware, collision-safe optional workspace output | Prevents cross-app mutation and improves rollback; migration is the main compatibility cost |
| Root consumer templates / `specs/README.md` / README tutorial | Move to `templates/`; new compact/critical templates; legacy templates preserved; tutorial links rules rather than reproducing them | Avoid distribution of maintainer docs and stale local policy. Existing copies are not automatically overwritten |
| Local package artifacts and `.serena/project.yml` | Add tracked scaffold test dependency metadata at root; leave host-generated packages local; maintainer language config remains local | Reproducible tests without pretending generated dependencies are maintained source |

For rule changes, distinguish removal of a review *invocation* from removal of
the underlying quality criterion. A rule's future home is compiler/analyzer,
app architecture, domain knowledge or optional advice. It must not disappear
merely because its old reviewer was merged.

## 10. Concrete executable interfaces to add or improve

Keep these small. Do not encode semantic risk assessment or approval as a fake
deterministic score.

1. **`scripts/verify-scaffold`**: run existing suites, validate local links and
   command/agent/skill targets, schema-check configuration for the supported host,
   detect duplicate model pins and broken declared rule-owner references, check that install inputs exclude
   `plans/`. Nonzero on failures; report which suites actually ran. Tests assert
   behavior, not exact reminder prose. Semantic duplication between differently
   worded rules still requires review; do not claim a string check proves its absence.
2. **`scripts/doctor --app <absolute-path> [--workspace <path>]`**: read-only
   by default. Report tool versions, resolved project set, symbols/ruleset/analyzer
   prerequisites, MCP initialize/tools/list, semantic navigation probe status,
   installed release and mutable/global paths. `available`, `unavailable` and
   `untested` are distinct. Redact credentials, headers, tokens and provider options.
3. **Compile interface**: retain positional compatibility for `compile.sh <app>
   [ruleset]`; add explicit toolchain/profile selection and a JSON result alongside
   existing log/summary. Default exit remains compiler exit for compatibility;
   a verification mode can enforce app-configured new-diagnostic thresholds.
   AppSourceCop is selected for release targets, not assumed to be in the current
   ten-DLL set. Dependency orchestration calls the same per-app primitive.
4. **Approval/evidence check**: accept artifact paths plus saved approval snapshot;
   compare fingerprints and report stale/missing evidence. Owner approval is a
   recorded user action, never synthesized by a test. Reuse the hash helper rather
   than another parsing framework. Validate only machine-readable facts.
5. **Installer interface**: preserve `init-linux.sh <app>...`; new install engine
   supports `--dry-run`, explicit revision/profile, update of one consumer and
   rollback from its manifest. Validate every target before mutation. Refuse
   unmanaged path conflicts; back up managed originals before replacing links.
6. **MCP/LSP launch**: explicitly select binary version and all intended projects;
   reject ambiguous auto-discovery. ALTool 18 capabilities are candidates, not an
   immediate dependency bump. A task tool list and permission smoke test must
   prove symbol search, cross-app references, and required test tooling on the
   selected version before removing a fallback.

## 11. Migration sequence and commit boundaries

The owner approval of this plan precedes all steps below. Each step is one or a
small number of thematic commits using the repository's conventional style.
Do not push or merge. Update this plan only for material discoveries/decisions.

### M0. Freeze the baseline and isolate development

- Recheck status, current HEAD and branch conflicts. Preserve all existing work.
- Create an explicit baseline ref for `f696dc480b8ee8df8bbbba7c694747aafe6e5f19`
  without moving any existing ref; choose a nonconflicting name, for example
  `baseline/agent-workflows-2026-09-29`. Record it here.
- Create `refactor/agent-workflows` in a **separate checkout/worktree**. Leave the
  original shared checkout at the baseline because real apps link into it.
  A branch switch in that original directory would already affect consumers.
- Snapshot current runtime dependencies needed for baseline reproduction; a
  Git ref alone does not pin npm packages, global settings or Microsoft tools.
- Commit the approved plan on the implementation branch. No speculative AL
  production implementation is involved.

### M1. Establish a repeatable scaffold baseline

Commit theme: `test: add scaffold contract and capability checks`.

- Add aggregate verification with existing suites and tracked test dependencies.
- Add installer fixtures for JSONC workspace input, two app names with the same
  suffix, path conflicts after preflight, existing local symlinks, no `jq`,
  multiple apps, hidden directories and copied-template preservation.
- Add configuration/permission/adapter target smoke tests with redacted output.
- Capture the baseline toolchain and exact BCQuality routes. Document the
  difference between “router returned a target” and “review executed”.

### M2. Separate maintained source, release and consumer state

Commit themes: `refactor: separate consumer templates and runtime`;
`feat: add isolated scaffold installs and rollback`.

- Move root consumer templates to `templates/`; split maintainer/consumer
  entrypoints and configurations. Preserve old installer CLI.
- Build immutable release snapshots; install app-local `.opencode` directories
  linking only selected read-only content. State/output goes to `.agent-state`.
- Preflight the whole batch; update only managed paths, back up the old links,
  scope excludes to managed artifacts. Make workspace generation explicit,
  JSONC-aware, atomic, and collision-safe; retain known old output names where safe.
- Do not migrate the confirmed GAEB consumer automatically. Use temporary fixtures
  and an explicit pilot clone. Complete rollback test before touching any live app.

### M3. Introduce risk-adaptive SDD and compatible artifacts

Commit theme: `refactor: route work by risk and uncertainty`.

- Implement section 7 in the SDD entrypoint and path references.
- Add Compact/Critical templates and approval snapshots; retain legacy workflow
  and canonical hash tests. Make old `/sdd` and `/al-*` names explicit adapters.
- Remove process restatements from README, templates, command prompts and plugin.
- Document existing-test execution versus new-test authoring and the proposed
  owner-approved defaults. Add table-driven routing examples, including small
  critical changes and low-risk edits in critical files.

### M4. Reduce reviewers and consolidate quality ownership

Commit theme: `refactor: bound reviews to acceptance and risk`.

- Add design/change/test-review roles; shorten advertised descriptions.
- Remove mandatory worker delegation and the quality+readability pair from the
  new default path. Preserve legacy dispatch contracts until migration ends.
- Consolidate duplicated house rules, correct the conflicts in F4/F5, map
  deterministic checks to actual analyzer capabilities, and keep exceptions
  explicit. Do not simultaneously restyle consumer AL source.
- Set read-only reviewer permissions and executable artifact checks. Change
  model configuration ownership without changing the compared model/variant.
- Put BCQuality contract fixes in its own fork PR/commit before bumping the
  submodule. Do not patch vendored files in place. Defer nonessential corpus
  changes if the new path can remain correct without them.

### M5. Evidence-first verification and optional tools

Commit theme: `feat: report reproducible verification evidence`.

- Extend compile evidence, app-specific analyzer selection and baseline comparison.
- Replace automatic post-build review expansion with explicit workflow verification.
- Implement doctor/capability probes, explicit project launch, pinned npm tools,
  optional browser/translation profiles and per-run state.
- Evaluate ALTool 18 LSP/MCP as a separate capability experiment. Remove the
  Serena bridge or `al-dependency` only after feature/permission parity, not on
  documentation alone. Preserve a tested rollback path to the old toolchain.

### M6. Paired task evaluation, pilot and closeout

Commit themes: `docs: document risk-adaptive workflows and migration`;
`test: record workflow comparison and pilot evidence`.

- Run the comparisons in section 13, record failures and workload honestly.
- Select one explicitly authorized pilot consumer. Snapshot app-local artifacts,
  switch only its managed runtime to the candidate release, restart OpenCode,
  and verify commands/tools/approval resume behavior.
- Keep old consumers on their selected baseline; list tested and unknown users.
- Record whether success criteria passed, failed or remain inconclusive. Retire
  legacy aliases only after an announced migration boundary, not in this phase.

Dependencies: M0 → M1 → M2; M3/M4 are introduced and validated together because
the old reviewer/reminder policy would defeat the new short path. M5 relies on
M1/M2 evidence and isolation. M6 requires the candidate's functional checks.
Do not combine workflow simplification and tool replacement into one attribution
claim even when both are ultimately adopted.

## 12. Compatibility, risks and approval decisions

### Proposed defaults to approve

1. **OpenCode/Linux remains the supported execution platform.** Claude keeps an
   honest context bridge; full Claude/Copilot parity is deferred. If parity is
   required now, it materially expands adapter and isolation tests.
2. **Three paths as specified in section 7**, including no generic independent
   reviewer for Direct, one for Compact, and scoped reviewers for Critical.
3. **Existing relevant tests may run without permission to create new tests**;
   new test writing remains explicitly opted in. App defaults can avoid repeating
   the same question for every feature.
4. **Private app specs remain private by default.** Do not silently start
   committing them into product repositories or overwrite existing copies.
   Preserve approval snapshots and back up all unversioned app artifacts to a
   configurable external state/backup root before migration. Local backups do
   not replace off-machine backup. Versioning private specs in an approved repo
   is optional, not a hidden prerequisite for the workflow.
5. **Consumer updates become explicit, revision-pinned installs**, not implicit
   changes from editing a shared checkout. Live-link mode is opt-in.

These are architecture/behavior choices, not routine implementation questions.
Approval can accept them together or amend individual points. The pilot app and
benchmark task refs can be selected later, before any live installation or paid
comparison runs. No additional product decision is needed to start M0–M5 in isolation.

| Risk | Mitigation / stop condition |
|---|---|
| Direct path misses a semantic defect | Inspect callers/invariants before routing; existing execution checks; sample Direct outcomes in comparison; elevate ambiguous impact |
| Fewer reviewers lose useful independent coverage | Preserve distinct risk specialists; same-model paired evaluation; correctness regressions block rollout |
| Classification itself becomes ceremony | One reason, three paths, no scorecard/approval form for Direct |
| New style policy causes broad code churn | Consolidate prompt authority only; no consumer restyling; style advice never becomes unrequested refactor scope |
| Legacy approvals invalidated by template changes | Artifact version selects legacy workflow; keep v1 hashing and old evidence; explicit migration approval |
| Shared symlink changes leak into active apps | Separate development checkout; immutable releases; explicit consumer update and manifest rollback |
| Private specs are lost during migration | Preflight, external backup and hash verification; no overwrite or reliance on `stash -u` |
| Host/global settings contaminate a test | Isolated HOME/XDG/config/caches, read-only tool inputs, loaded-source inventory and sentinel tests |
| Current tool docs outpace installed binaries | Doctor probes actual commands/tools; no capability inferred from major version alone |
| Compile warning policy differs from consumer CI | Resolve real app analyzer settings/CI profile; report unverified parity rather than asserting it |
| Migration grows into a framework | Limit to native adapters, small scripts and Markdown; defer scheduler/full multi-harness support |

## 13. Validation and controlled comparison

### 13.1 Functional scaffold checks

Proposed tests, not yet executed:

- Clean temporary install, rerun, explicit update, rollback, and preservation of
  arbitrary user files/symlinks. Verify both Git-managed changes and excluded state.
- Multi-app and linked-worktree paths; no first-match selection. Dependency changes
  must include affected consumers in build selection.
- JSONC workspaces, ambiguous source workspaces, basename collisions and optional
  workspace output; no partial target after failure.
- Every advertised command/agent/skill resolves; legacy and new artifacts choose
  the correct flow; absent/stale approval cannot authorize implementation.
- Reviewer cannot mutate source through edit, shell or semantic-edit tools under
  the supported host configuration; report the boundary actually enforced.
- Compile success with warnings is represented accurately; baseline/new findings
  remain distinguishable; missing analyzer/ruleset is failure, not clean fallback.
- Required tests failed/skipped/unexecuted, missing runner and malformed results
  remain unsuccessful even if a reviewer returns no findings.
- Build-only requests do not cause unrelated reviewers, spec files or Hunk tasks.
- Fake tool failures consume bounded retries; no infinite gate loop and no
  automatic pass at the retry limit.
- Optional MCP profiles expose only intended tools; browser output and caches do
  not land in the source checkout or another app's directory.

### 13.2 Experimental design

Use two phases to avoid attributing a newer toolchain to a simpler workflow:

**A/B workflow test:** baseline policy versus candidate policy, same functioning
tool versions and tool availability, same explicit model ID and reasoning variant
for equivalent roles, same source/symbols/BC image, prompt, acceptance criteria,
test-authoring choice, credentials scope and environmental limits. Disable host
autoupdates. Baseline's absent capability is an infrastructure failure to fix or
report separately, not a free point for the candidate.

**Tool consolidation test:** winning/fixed workflow with old navigation stack
versus proposed ALTool replacement, otherwise unchanged. Measure semantic lookup
and full-task outcomes before retiring a fallback.

Run each arm in a fresh session and separately provisioned installation:

- Separate source worktrees/clones AND immutable scaffold snapshots, never both
  pointing at this live `.opencode` checkout.
- Separate HOME, XDG config/data/cache/state, `.claude`, `.agents`, OpenCode
  global/project config, Serena caches/memories, npm resolution, browser profile,
  app `.alpackages` and writable results. Mount identical compiler/symbol inputs
  read-only or copy them with checksums.
- Use tested host isolation switches where available; `OPENCODE_CONFIG` only
  merges configuration and is not isolation. Controlled HOME alone does not
  remove managed or remote configuration. Inventory the loaded sources and
  exported tool names. Add a harmless sentinel skill/plugin to the *excluded*
  global fixture and assert that neither arm loads it.
- Prefer a container or equivalent isolated user environment for repeatability.
  Pass only necessary credentials through secure environment injection; never
  copy auth databases into the repository or comparison report.
- Freeze a disposable BC test environment/data snapshot per run, or reset it
  between runs. A second run must not inherit state created by the first.
- Randomize/interleave arm order. Give the owner the same decision packet and
  scripted answers per task; count active time separately from waiting.
- Keep evaluation acceptance tests/checklists fixed and independent of generated
  tests. A task is not correct merely because the agent changed a test to pass.

### 13.3 Task set and repeats

Select actual completed/seeded tasks in authorized app clones, with reproducible
starting refs and independent acceptance criteria. Proposed small first set:

| Class | Two representative tasks | Verification |
|---|---|---|
| Direct | Caption/translation correction; bounded noncritical validation bug with known callers | Compile, locale/behavior checks, no scope creep |
| Compact | Optional field with reopen behavior; bounded filter/action behavior using existing architecture | Acceptance scenarios, compile, existing tests or explicitly opted-in new tests |
| Critical | Posting/transaction failure and rollback; released-data upgrade or public API/permission boundary across apps | Failure-path/rollback or upgrade tests, restricted-permission/company checks, dependent-app compile |

First run an infrastructure smoke task per arm. Then three paired runs per task
(six tasks × two arms × three runs = 36 task runs), subject to an explicit owner
budget before execution. If variance or a failure changes the choice, repeat the
affected tasks to five runs or add another representative task. Do not discard
failed runs or rerun silently until a desired result appears. Infrastructure
failures are labelled and counted separately, with any replacement run linked.
This is a practical pilot, not statistical proof of broad non-inferiority.

### 13.4 Measurements and result storage

Store redacted run metadata/results under `plans/evaluations/agent-workflows/`;
keep full private app logs in the selected private evidence root. For each run:

- Task/base refs, scaffold/submodule refs, model/reasoning and actual effective
  toolchain, loaded-source manifest, environment/symbol identifiers.
- Acceptance criteria satisfied/failed/unverified, independent evaluator notes.
- Build/analyzer and required test totals, skipped/unexecuted status, raw log paths.
- Active human time, wall time (including/excluding infrastructure wait), tokens
  and billed cost when available. Unavailable measurements are null, not zero.
- Draft/approval/review/repair counts and reason for each extra loop.
- Confirmed actionable findings, duplicates, false alarms and unresolved findings;
  classify against acceptance criteria/evidence, not just whether a fixer obeyed.
- Unrequested source changes, new document count/size and irrelevant tool use.
- A short owner assessment: can the route, rule authority and failed check be
  understood and changed without searching several policy copies?

Report per-task paired differences, medians and ranges, class-specific failure
counts and consistency across repeats. Do not hide a critical failure in an
overall average. A single fast green run is not sufficient rollout evidence.

## 14. Success criteria and rollback

The following are **proposed acceptance targets**, not measured improvements:

1. All existing infrastructure suites remain passing or have explicitly reviewed
   replacements preserving their useful contracts; new install/rollback and
   compatibility tests pass in an isolated environment.
2. Direct tasks produce no new SDD folder and no compulsory generic reviewer;
   Compact needs at most `spec.md` + `validation.md` and one human approval;
   Critical retains intent/design/risk evidence without five mandatory artifacts.
3. Consumer startup bootstrap ≤120 nonblank lines; common SDD router ≤150.
   Specialist bodies are loaded only when applicable. Source line counts are a
   maintainability guard, not a proxy for correctness or model token accounting.
4. Each policy has a named authoritative file. Commands, templates, hooks and
   README do not independently restate reviewer sets, retry policy or model pins.
5. Normal no-tests Compact work has one final independent reviewer, rather than
   the baseline's six review dispatches. Delegation beyond that has a stated
   information/context reason. Critical specialists remain risk-triggered.
6. No required check or missing tool is reported as pass; no unbounded repair
   loop; no unrelated documents or refactors added to satisfy generic prompts.
7. Candidate meets all independent acceptance criteria in the pilot, with no new
   critical correctness/compatibility defect. Any such defect blocks rollout
   until understood and retested. This does not claim guaranteed population-level
   reliability from a small sample.
8. Target ≥25% reduction in median active human time for Direct/Compact paired
   tasks, without lower acceptance success; also report wall time/usage honestly.
   Critical work is judged primarily on correctness and bounded intervention,
   not a mandatory speedup. Inconclusive noisy measurements do not count as success.
9. Install/update/rollback of one pilot does not change another consumer, the
   shared source, global settings, browser profile, or private spec contents.
10. A fresh session can determine selected release, workflow path, approved intent
    and remaining checks without reconstructing chat history.

Rollback is a consumer operation as well as a Git operation:

- Keep original source checkout/ref and immutable baseline release available.
- Stop/restart the consumer host around switching its managed links/config back
  using the installation manifest; restore only files still matching installer
  ownership hashes. Preserve later user edits and report conflicts.
- Restore the prior managed exclude block/workspace output from backup without
  replacing unrelated `.git/info/exclude` entries. Worktrees share that file.
- Restore app-local artifact backups only by explicit selection, never blanket
  replacement; preserve newer decisions and approval history.
- Restore any separately authorized global changes from their own captured
  before-state. A repository branch switch does not restore those settings.
- Verify loaded tools, one legacy command and a baseline compile/check after
  rollback. Preserve candidate logs for diagnosis. No force push, reset of user
  work, or automatic data rollback in a BC environment.

## 15. Approval stop

The assessment is complete enough to implement this plan in isolation. Approval
is requested for the recommended option B and the five explicit defaults in
section 12. The live pilot and paid comparison runs require their concrete
consumer/task selection and budget before execution.

Approval is recorded above. Implementation and its evidence are tracked in
`plans/agent-workflows-implementation.md`. Live consumer selection and comparison
budget remain separate prerequisites for the pilot and paid task runs.
