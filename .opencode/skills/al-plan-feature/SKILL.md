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

## Source verification (do it in the first pass)

Source-verification depth is a first-pass duty, not something later runs
discover. On the FIRST run of a gate, verify against the AL source and the
declared metadata every load-bearing claim the plan makes, including: that
each allocated object id is genuinely free for its type (`rg` over `src` plus
a compile probe where cheap); the actual field-id tails of every extended
table; band-map claims against `tech-design.md`; rename and reference counts
the plan asserts; interaction points (call sites, events, page areas) the plan
names; and the permission/sweep/upgrade consequences of every schema change.
The findings report must state which claims were verified in source and which
could not be reached, so a later pass cannot silently deepen what the first
pass asserted.

## Rerun discipline

On a rerun, verify the prior resolutions and the areas the fixes touched (the
coordinator supplies a statements-touched list), and re-verify any source
claim a fix invalidated. Do not expand the review to fresh scope beyond what
the fixes reach; new scope belongs to the first pass. The one exception that
justifies a new finding on a rerun is a contradiction a fix itself introduced
or a source fact a fix invalidated, and the finding must say which fix
surfaced it.

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
