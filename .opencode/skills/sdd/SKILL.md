---
name: sdd
description: Routes AL implementation by risk into Direct, Compact SDD or Critical SDD. Owns intent approval, relevant verification and bounded review. Load for changes, not general questions.
---

# Risk-adaptive SDD

The spec preserves intent; execution proves conformance. Use the least costly
path that addresses the actual risk. Read only the path reference you need.

## Route after bounded inspection

1. Read app policy and inspect affected code/callers. State the path and reason.
2. **Direct**: existing intent is explicit; impact is bounded and reversible;
   no affected critical invariant. Follow `references/direct.md`.
3. **Compact**: bounded new behavior with known architecture. Follow
   `references/compact.md`.
4. **Critical**: affected posting/accounting, transaction/retry boundary,
   permission elevation, company/tenant isolation, released data/upgrade, public
   contract, performance-sensitive path or broad dependent-app behavior; or an
   unresolved material architecture decision. Follow `references/critical.md`.
5. Uncertainty first gets focused investigation. Do not assume unknown data or
   callers disposable. Escalate when evidence reveals a risk, not merely because
   a file is long or its name includes Posting. A harmless local rename can be
   Direct even in a posting file; a one-line Commit change is Critical.

## Legacy boundary

New feature specs declare `workflow: risk-adaptive-v2`. A feature with old
`approvals.md`/five-file artifacts and no v2 declaration remains legacy. Do not
relabel it or weaken its approval requirements. `references/legacy.md` preserves
the old contract as reference. Resume such work in its recorded baseline runtime,
or obtain explicit migration approval and retain all prior artifacts/evidence.
Old `/al-*` gate commands remain available for legacy review and retain their
old evidence checks. They are not part of a v2 Direct/Compact route.

## Work ownership

The main agent may investigate, draft and implement. Delegate only where a
bounded separate context or an independent judgment adds value. Reviewers do not
modify the material they review. Use short path-based dispatches naming acceptance
criteria, changed scope, known risks and evidence. No mandatory same-model relay.

## Approval and progress

Compact/Critical intent needs human approval before implementation. Record the
owner's actual approval against an immutable snapshot of spec/plan using
`scripts/approval.py record`; list the record path in `validation.md`. Check it
before implementation and on resume using `scripts/approval.py check`.
The helper detects changed content, not human authenticity. Never infer approval
from a model report or invoke record before the user approves.

Spec and plan hold current intent; validation holds status/results/approval
references. Keep checkbox progress outside approved artifacts. Material changes
to behavior, scope or compatibility reopen approval. Internal refactoring inside
approved constraints does not automatically require a new plan approval.

## Checks and review

- Run compile/analyzers and relevant existing tests before final change review.
  Use identical toolchains for baseline comparison. Counts alone do not prove
  that findings are unchanged. Identify app/dependency scope and retain logs.
- **Existing relevant tests** may run independently of permission to create tests.
  **New tests** require explicit task/app opt-in. Do not silently infer an absent
  decision when new tests are needed; ask once and record it in the spec.
- Every changed behavior needs a verification method. Required tests that fail,
  skip required cases, fail to start or return incomplete results are not pass.
  Critical work without adequate executable proof needs an owner decision on
  an alternative. An explicit no never authorizes unsolicited test writing.
- UI execution is required for rendered-UI acceptance, not every headless change.
- Direct has no mandatory independent general reviewer. Compact uses one fresh
  `al-change-reviewer`. Critical adds `al-design-reviewer` before implementation
  and only distinct risk specialists. Complex new tests can use `al-test-reviewer`.
- Select specialists for actual risk: integration flow, subscriber contract,
  Azure artifacts, tenant/permission boundary, released compatibility or measured
  performance. Do not run umbrella and leaf reviewers over the same concerns.
- Blocking findings need concrete impact, source/execution evidence and an
  acceptance/platform/app-rule basis. Preferences and speculative abstractions
  are advisory. Report late real defects, identifying new evidence; do not hide
  them because an earlier pass missed them.

## Stop rules

One complete pass suffices on unchanged inputs. After a fix, rerun affected
executable checks and confirm affected review responsibilities. Retain unrelated
evidence with a short impact reason. If impact is unclear, rerun the whole
applicable set. Newly affected risks add checks.

Budget per checkpoint: initial review plus **two repair/confirmation cycles**,
including mechanical repairs. A repeated infrastructure/API failure gets **one
retry**, then blocked/partial. At exhaustion report unresolved evidence and ask
for a decision. Never pass on timeout or reset the budget by renaming a stage.
Only an explicit owner-approved scope/decision starts a new checkpoint.

## Closeout

Report what changed, executed checks, limitations and remaining risks. Update
product documentation only when behavior needs it. No documentation quota,
automatic PR or forced Hunk session. Optional Hunk notes explain non-obvious
intent at a stable checkpoint. Resume from intent and validation, not a retelling
of the entire previous conversation. Reload this router after compaction only
when the applicable obligations are no longer available in context.
