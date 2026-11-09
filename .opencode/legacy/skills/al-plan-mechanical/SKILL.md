---
name: al-plan-mechanical
kind: governance-skill
id: al-plan-mechanical
version: 1
title: Feature Plan Mechanical Review
description: Runs the deterministic stage of the feature plan gate, covering digest verification, object ID range and freeness, test-policy match, task-list shape, roadmap status, and grep-able house hard rules, and emits a findings report.
inputs: [repository, feature-id, spec-path, plan-path, tasks-path]
outputs: [governance-findings]
bc-version: [all]
technologies: [al]
countries: [w1]
application-area: [all]
---

# Feature Plan Mechanical Review

This scaffold-local governance skill is the mechanical stage of the feature
plan gate. It runs before the semantic plan gate (`al-plan-feature`) on the
first pass and on every rerun, and after any amendment that touches `plan.md`
or `tasks.md`. It is not a BCQuality action skill.

## Inputs

Resolve the repository and feature from the invocation. Read `APP_CONTEXT.md`,
`AGENTS.md`, `approvals.md`, `spec.md`, `plan.md`, `tasks.md`,
`specs/roadmap.md`, plus `app.json` and `AppSourceCop.json` when present. Do
not read the constitution files and do not load house-policy overlays: every
check here is decidable from the artifacts and declared metadata alone.
Semantic review is the `al-plan-feature` gate's job and is out of scope.

Freshly execute `python3 .opencode/skills/sdd/scripts/artifact_hash.py` on current
spec, plan, and tasks paths, using the absolute helper path if needed. Follow
sdd-artifact-v1 in the SDD skill and report recipe, digests, and execution
evidence. Recorded-only agreement is insufficient; missing or failed execution
is partial/block, never pass. Legacy mismatches require explicit revalidation
and human re-approval, never automatic approval changes.

## Checks

Run the full checklist on every run, including reruns: the checks are
deterministic and cheap, so this stage never narrows to a delta.

- `approvals.md` records a passing Spec gate and human approval with identical
  full `spec.md` SHA-256 values, and a freshly recomputed digest matches them.
  This stage does not require Plan's own not-yet-written approval evidence.
- Every planned object carries an explicit ID or an explicit extends-existing
  statement, no ID is duplicated within the plan, and each ID is inside the
  app-local assigned range for its object type. Derive the range from
  `APP_CONTEXT.md`, `app.json`, and `AppSourceCop.json`; never assume it.
- Each allocated ID is genuinely free for its type: navigate AL with Serena
  first and search the entire source, including hidden directories, for the ID
  and object name. Use workspace-relative paths and report 1-based locations
  after converting Serena's 0-based lines. This read-only gate does not compile.
- Plan and spec state the same explicit `Automated tests: yes | no` decision
  with owner and date. If `yes`, tasks map tests to acceptance criteria, write
  them before semantic implementation review and compilation, and include the
  post-compile runner before test verifiers. If `no`, no test-writing or test-verifier task
  exists. Never infer a default for an omitted decision.
- `tasks.md` is ordered and checkable, and includes implementation, semantic
  implementation review, a Test-step build with applicable verifiers, and Docs
  with roadmap closeout. A complete finding-free verifier pass on unchanged
  inputs suffices; fixes, waivers, or relevant input changes require the exact
  applicable set's confirmation, adding new triggers, never narrowing it.
- `specs/roadmap.md` status for the feature is `planned` while the plan is
  under review.
- Grep-able house hard rules: no `ODataKeyFields` planned.

## Findings

Use `block` for a digest mismatch, an out-of-range, duplicated, or taken
object ID, a test-policy mismatch, or a missing required task-sequence item.
Use `warn` for a malformed or unordered task list. Use `info` sparingly.

Return the local governance shape defined by `al-spec-feature`, with
`gate: "al-plan-mechanical"`. The `summary` must list the checks run and the
source claims verified. `outcome` is `fail` when any `block` or `warn`
remains, or `partial` with a blocking finding for unavailable execution or
incomplete/API-failed review. Do not emit BCQuality DO references.

This gate passes independently of the semantic gate. The coordinator
dispatches `al-plan-feature` only after this report is `pass`, and repeats
this stage before every semantic rerun.
