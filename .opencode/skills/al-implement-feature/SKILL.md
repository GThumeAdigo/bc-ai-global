---
name: al-implement-feature
kind: governance-skill
id: al-implement-feature
version: 1
title: Feature Implementation Review
description: Reviews a Business Central feature implementation for semantic conformance with its approved spec, plan, tasks, and acceptance criteria before testing.
inputs: [repository, feature-id, implementation]
outputs: [governance-findings]
bc-version: [all]
technologies: [al]
countries: [w1]
application-area: [all]
---

# Feature Implementation Conformance Review

This scaffold-local semantic gate runs after implementation and before Test.
It compares approved intent with the implemented source. It is not a BCQuality
action skill and must not duplicate mechanical verifier work.

## Inputs

Resolve the repository and feature from the invocation. Read `APP_CONTEXT.md`,
`AGENTS.md`, the approved `spec.md`, `plan.md`, `tasks.md`, `approvals.md`, and every source file
identified by the plan's object inventory and tasks. A diff is useful supporting
evidence but is not a required hidden input and is not the full review scope.
Recompute the full-file SHA-256 for `spec.md`, `plan.md`, and `tasks.md`.
`approvals.md` must show passing Spec and Plan reviews, human approvals, and
matching review/approval/current digests for all three files. Require roadmap
status `in-progress`; otherwise implementation or Test entry is blocked.

## Checks

- Every implemented behavior satisfies the acceptance criteria and preserves
  the approved scope, business rules, user flow, and explicit non-goals.
- The implementation matches the planned object responsibilities, data model,
  integration contracts, state transitions, permissions intent, telemetry
  intent, and accepted trade-offs.
- Every implementation task is represented in source, and no material
  unplanned behavior or object was introduced without an approved amendment.
- When automated tests are opted in, the planned test artifacts exist. Their
  execution and quality are checked in Test, not here.

Do not compile, run analyzers, invoke BCQuality review agents, assess test
quality or coverage, require verifier results, inspect documentation/roadmap
closeout, or inspect a PR. Those occur after this gate in Test, Docs, and Merge.

Use `block` for behavior that contradicts or omits approved intent. Use `warn`
for a material plan/task divergence that does not yet prove wrong behavior. Use
`info` sparingly. Return the local governance shape defined by
`al-spec-feature`, with `gate: "al-implement-feature"`; do not emit BCQuality
DO references.

`outcome` must be `fail` while any `block` or `warn` remains. Resolve findings
and rerun this same gate to `outcome: pass` before Test. If Test fixes production
behavior, rerun this gate again against the resulting implementation before Test
closes.
