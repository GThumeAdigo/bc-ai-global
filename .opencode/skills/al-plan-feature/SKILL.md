---
name: al-plan-feature
kind: governance-skill
id: al-plan-feature
version: 1
title: Feature Plan Review
description: Reviews a Business Central feature plan and task list against its approved spec, object ID range, and verifier expectations, and emits a findings report.
inputs: [repository, feature-id, spec-path, plan-path, tasks-path]
outputs: [governance-findings]
bc-version: [all]
technologies: [al]
countries: [w1]
application-area: [all]
---

# Feature Plan Review

This scaffold-local governance skill reviews `plan.md` and `tasks.md` before
the human Plan approval stop. It is not a BCQuality action skill.

## Inputs

Resolve the repository and feature from the invocation. Read `APP_CONTEXT.md`,
`AGENTS.md`, the constitution, the approved feature `spec.md`, `plan.md`, and
`tasks.md`, `approvals.md`, plus the relevant `app.json` and `AppSourceCop.json` when present.
Load `.opencode/skills/al-code-review/SKILL.md` as the design-level house-policy
overlay. Do not inspect implementation-only details that the plan cannot show.
Derive object ranges, prefixes, namespaces, dependencies, and test policy from
those files rather than assuming dispatcher-provided values.

## Checks

- `approvals.md` records a passing Spec gate and human approval with identical
  full `spec.md` SHA-256 values, and a freshly recomputed digest matches them.
  This Plan gate does not require its own not-yet-written Plan approval section.
  Spec open questions are resolved, and the plan maps each acceptance criterion
  without changing approved intent.
- The plan reuses standard BC first and justifies each custom-code gap.
- Every planned object has a purpose and, when applicable, an ID inside the
  app-local assigned range.
- Approach, standard BC reused, AL object inventory, data model, integrations,
  cross-cutting concerns, risks and decisions, and test strategy are complete.
- Permissions, telemetry, performance, security/privacy, translations,
  integration behavior, and schema consequences are addressed when relevant.
- The design preflights applicable hard rules from `al-code-review`: no planned
  `ODataKeyFields`, all object IDs in range, least-privilege permissions and an
  intentional public surface, plus applicable page/codeunit/event/API,
  integration, error-handling, telemetry, and testability seams.
- Schema and compatibility decisions use the explicit app-local compatibility
  fields in `APP_CONTEXT.md`. A release tag alone never overrides `no`. When
  compatibility is `yes`, require the trusted released baseline ref and design
  against it; a missing baseline makes compatibility review partial. Do not mix
  this house boundary into the portable BCQuality action.
- The plan and spec contain the same explicit automated-test decision. If it is
  `yes`, tasks map tests to acceptance criteria and include test verifiers. If
  it is `no`, test-writing and test-verifier tasks are absent. Never infer a
  default for an omitted decision.
- `tasks.md` is ordered, checkable, and includes implementation, permission and
  telemetry work where relevant, then semantic implementation review, then a
  Test-step build and applicable verifiers, then Docs and roadmap closeout.
- The roadmap status is `planned` while the plan is under review.

## Findings

Use `block` for an unapproved or contradictory spec, unresolved required
decision, test-policy mismatch, or out-of-range object ID. Use `warn` for an
incomplete design or task sequence. Use `info` sparingly.

Return the local governance shape defined by `al-spec-feature`, with
`gate: "al-plan-feature"`. `outcome` is `fail` when any `block` or `warn`
remains. Do not emit BCQuality DO references.

Human approval may be requested only after this same gate has been rerun with
`outcome: pass`. With `plan.md` and `tasks.md` unchanged after that run,
calculate separate full-file SHA-256 values and write the passing review,
reviewer/date, both digests, human approver/date, and the same approved digests
to `approvals.md`. Chat-only approval is not durable. This gate emits the pass;
it does not require its own Plan approval evidence beforehand.
