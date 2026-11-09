# Agent workflow migration execution

Owner approved option B and section 12 defaults on 2026-09-29.

## Baseline

- Source: `f696dc480b8ee8df8bbbba7c694747aafe6e5f19`.
- Baseline ref: `baseline/agent-workflows-2026-09-29`.
- Corpus: `dcc2f1fa8271f8fb70711d62a08fb33435e1ce36`.
- Isolated branch: `refactor/agent-workflows`.
- During isolated implementation, the original checkout and installed consumers
  were not migration targets. The subsequent requested checkout handover is below.
- Observed tool versions: OpenCode 1.18.33, global ALTool 17.0.34.45391,
  extension 18.0.2732683 / ALTool 18.0.41.45789, Node 24.18.1, Python 3.13.15.
- Baseline host-generated plugin dependency: `@opencode-ai/plugin` 1.18.23.
  Baseline npm MCP versions were not pinned; a reproducible task comparison must
  provision identical explicit versions rather than claim the Git ref freezes them.
- No credentials or global authentication databases are copied.

## Progress

### Requested checkout handover, 2026-09-29

The owner explicitly requested switching the original repository to the new
branch after editing files on `master`. The three modified tracked files and
the untracked older plan were saved in stash commit
`6aca6616bba554c6bb61ddc45517883942db7def` before switching. The stash is retained.

The branch now resides in `/home/greg/Repos/AI/bc-ai-global`. The temporary
worktree remains detached at `02cc0c6`. The owner's object-declaration check and
real-subagent dispatch rule were ported into the new implementer/SDD files and
`runtime/AGENTS.md`, preserving their consumer scope. These edits remain
uncommitted. No old workflow file was restored over the refactored version.

Existing app symlinks into the original checkout now resolve against the new
branch. Their targets were not rewritten; this branch switch is not a completed
consumer installation migration. Root `AGENTS.md` and `opencode.json` now describe
scaffold maintenance, while consumer configuration lives under `runtime/`.

### Implementation stages

- M0: baseline ref and isolated worktree created; approval recorded.
- M1: aggregate suites, dependency locks, reference/model/permission contracts,
  installer/approval/build fixtures and schema checker implemented.
- M2: committed release export, prebuilt corpus index, read-only checksummed
  snapshots, explicit profiles, app-local runtime, backups and rollback implemented.
- M3: Direct/Compact/Critical routing, compact artifacts and approval snapshots
  implemented. Old artifacts remain legacy; no automatic approval conversion.
- M4: new design/change/test review roles, main-session implementation, centralized
  model policy, narrowed authoring overlay and optional Hunk implemented.
- M5: explicit AL project launcher, optional pinned MCPs, capability doctor,
  compiler/analyzer profile selection and JSON baseline evidence implemented.
- M6 infrastructure: passing checks below. Product comparisons and live pilot
  remain **pending**, requiring authorized apps/task refs and an execution budget.

## Executed validation, 2026-09-29

Functional candidate verified: `da31f3c` (the full commit is available on
`refactor/agent-workflows`). Later evidence-only commits do not change these inputs.

| Command/check | Actual result |
|---|---|
| `python3 scripts/verify-scaffold` | Four suites passed: 36 infrastructure tests, 28 compile/evidence fixtures, seven legacy plugin tests, six legacy installer fixture functions |
| `.venv/bin/python scripts/check-config opencode.json runtime/opencode.json` | Both source configurations passed published-schema validation |
| Published schema digest | `e8cb6e287a3852ee3403f4803be5ad6b19db94948037eaa9672125c333427922` |
| `python3 scripts/smoke-install --host` | Committed release installed in two temporary apps; update/rollback of one preserved the other's config; no maintainer plans or auto-loaded post-build plugin installed |
| Isolated OpenCode 1.18.33 loader | `al-change-reviewer` loaded with `gpt-6-sol` / `high`; native SDD skill found; external sentinel skill excluded |
| `scripts/doctor` with installed extension ALTool 18 and `--probe-mcp` | Initialize/tools-list passed; 16 advertised tools, including `al_run_tests`; no behavioral invocation |
| `git diff --check` | Passed |
| npm lock creation with scripts disabled | Completed; dependency lock tracked |

The schema check deliberately validates model identifiers as strings and does
not mistake a public catalog for proof of provider availability. The host loader
test proves effective configuration, not execution by the selected model.

## Defects caught during implementation

- Installer permission keys also needed placeholder rendering, not only values.
  Added a regression test and an installed-config unresolved-token assertion.
- The doctor initially parsed `v24.18.1` as `18.1`. Corrected version extraction
  and added a regression fixture.
- Full OpenCode debug inventories were truncated when captured through a pipe.
  Capturing them through a regular temporary file provided complete parseable
  output. The host smoke test now uses that path and validates actual skill names.
- Rollback/write-failure tests cover already-applied paths, user edits, legacy
  links, quoted app paths, workspace suffix collisions and private template symlinks.
- Build baseline comparison now reports external un-hashed source directories
  as incomplete rather than claiming full input identity.

## Deliberate compatibility choices

- Native paths and legacy named agents/gates remain available during migration.
  The old workflow is retained as an unloaded reference. Full legacy feature
  execution belongs to its recorded baseline runtime until explicit migration.
- The old hook and installer are retained under legacy paths and tested, not
  auto-loaded or used as the new installation default.
- Existing legacy exclusion blocks are not removed automatically: unregistered
  consumers may still depend on them. New exclusions are app-scoped.
- Individual rollback of an initial multi-app batch retains shared exclusion
  entries to avoid exposing another app's private files. A single-app rollback
  refuses an externally changed exclusion file rather than overwriting it.
- `--dry-run` may create a checksummed release cache, but does not mutate apps.
- Doctor multi-app input uses repeated `--app`; it does not guess a selected
  workspace. Workspace output is an explicit installer option.
- ALTool/Serena replacement is deferred until a real-app semantic and runtime
  parity test. The fallback bridge remains; no submodule source was changed.
- The compact rule overlay replaces redundant generic checklists. The detailed
  style guide remains a scoped reference, with legacy examples largely preserved;
  this migration does not restyle product AL.

## Limits and remaining rollout gates

- No real AL product was compiled, no BC runtime test executed, no model task
  benchmark run, and no live consumer migrated. Build tests use fake compiler
  fixtures and are not a substitute for product execution.
- Core reviewer permissions are deny-by-default and their configuration is
  tested. Actual attempted tool writes and all retained specialist permissions
  have not been exercised in paid agent runs or an OS sandbox. Do not describe
  prompt-only legacy review restrictions as an OS security boundary.
- Risk routing, relevance selection and repair budgets remain explicit agent
  instructions. There is no new scheduler enforcing model turns. The supplied
  routing cases are evaluation inputs, not measured classifier accuracy.
- The universal mechanical model gate is absent from new paths. Approval
  freshness is executable; object/range diagnostics come from actual compile or
  symbol checks, not a new bespoke AL parser.
- Baseline global/npm state was observed, not fully frozen. Before A/B runs,
  provision matching explicit dependency/model/tool versions and retain the
  loaded-source inventories for both arms. Do not compare an accidentally broken
  baseline against a repaired candidate as workflow evidence.
- Success criteria concerning active human time, repeated task correctness,
  review precision and live-app compatibility are **not yet evaluated**.
- No matching Hunk session for this worktree was used; no notes published.

Next owner inputs: an authorized pilot app/clone and task/base refs, plus a
budget for the proposed paired comparisons. Until then this is a verified
infrastructure candidate, not an empirically validated replacement for all apps.

## Agent/command follow-up, 2026-09-29

On owner request, corrected the remaining role/dispatch inconsistencies:

- All 27 specialists remain subagents; `/sdd` coordinates in the current primary
  conversation, preserves Plan permissions, asks for an empty request and respects
  explicit stage scope. Native commands targeting subagents are valid child-task
  entry points, unlike selecting a subagent as a CLI primary agent.
- Old SDD gate descriptions and commands explicitly select legacy work and route
  v2/unknown artifacts back before demanding legacy prerequisites.
- Existing relevant test execution is independent of new-test authoring opt-in;
  legacy `tests=no` remains a legacy-only execution skip. Old coverage/quality
  agents are optional targeted audits, not an additional v2 mandatory set.
- Fifteen retained read-only specialist adapters now deny tools by default and
  allow reading, semantic lookup and exact router invocations. They consume a
  prepared corpus index and stdin task context instead of needing file writes.
  Test/browser runners deny direct source-edit tools but retain execution tools.
  These are host tool permissions, not an OS sandbox or a claim that arbitrary
  shell argument strings are safe.
- `python3 scripts/verify-scaffold`: 39 infrastructure tests, 28 compile fixtures,
  seven legacy hook tests and six legacy installer functions passed. This includes
  real stdin routing for all 15 restricted adapters. Existing Node module-type
  warning from the ignored local package file remains non-fatal.
- Isolated OpenCode metadata check on current uncommitted files: all 27 modes,
  current-agent `/sdd`, legacy command target, and a representative specialist's
  resolved permissions loaded successfully. No model or tool-action execution
  was claimed from this loader check.

Changes are uncommitted alongside the preserved owner edits. A restart is needed
to load changed agents/commands; installed immutable releases require an explicit
update before their consumers receive these changes.

## 2026-11-09 workflow slimming

Owner-requested after the first pilot period, to cut review loops and speed up tasks.

- Models: tiered `runtime/model-policy.json` (Sonnet 5.5 high default, Opus 5.5
  high for `al-spec-writer` and `al-design-reviewer`, Haiku 5.5 for rule audits,
  test execution and built-in `explore`). Primary agents keep the session model.
- Default chain: `al-spec-writer`, `custom-al-implementer` (reads style guide
  section 0 and touched sections first), then `al-review-fixer` for Compact (fixes
  behavior-neutral defects, rebuilds, escalates behavior findings) or read-only
  `al-change-reviewer` for Critical.
- Stop rules: one review pass and one repair pass per checkpoint, replacing initial
  plus two confirmation cycles. Fixer edits are verified by rebuild, not re-reviewed.
- Compact is one file: approved intent above a status marker, status and evidence
  below. `approval.py` hashes only the part above the marker; files without a
  marker and older `validation.md` features behave as before.
- Eight legacy gate agents, four `/al-*` commands and five gate skills moved to
  `.opencode/legacy` (not installed). `al-userguide-test-writer` merged into
  `al-test-writer`. The five legacy `feature-*.md` templates stay for old features
  and the legacy initializer. 27 agents became 20 (two new: `al-spec-writer`, `al-review-fixer`).
- Not merged: `al-test-reviewer` and `al-test-runner` (read-only judgment versus
  execution, different permissions and tiers).
- Checks: `python3 scripts/verify-scaffold` and `scripts/smoke-install` on the
  committed revision. No model execution of the new chain was run.

## 2026-11-09 legacy removal

Owner decision: the retired five-file workflow is no longer needed productively;
git history and ref `baseline/agent-workflows-2026-09-29` keep it. Removed
`.opencode/legacy` (gate agents, commands, skills, post-build hook), the SDD
`legacy.md` reference and `artifact_hash.py`, the legacy initializer
`scripts/legacy/init-linux.sh` with its fixture test, and the five `feature-*.md`
templates. `scripts/verify-scaffold` now runs the Python suites only. The installer's
`--migrate-legacy` stays for apps still linked to this source directory.
