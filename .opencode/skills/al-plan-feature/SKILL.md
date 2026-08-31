---
name: al-plan-feature
kind: governance-skill
id: al-plan-feature
version: 1
title: Feature Plan Review
description: Reviews a Business Central feature plan and task list for semantic conformance with its approved spec, design completeness, and house-policy preflights, and emits a findings report. The deterministic stage runs separately in al-plan-mechanical.
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

This is the semantic stage of the plan gate. The mechanical stage
(`al-plan-mechanical`) must have passed for the current revision before this
gate is dispatched, on the first pass and on every rerun. Do not redo its
deterministic checks; the one exception is the approved Spec digest recompute
below, kept as cheap defense in depth.

## Checks

- The freshly recomputed full `spec.md` SHA-256 matches both Spec review and
  approval digests in `approvals.md`. Spec open questions are resolved, and
  the plan maps each acceptance criterion without changing approved intent.
- The plan reuses standard BC first and justifies each custom-code gap.
- Every planned object has a purpose.
- Approach, standard BC reused, AL object inventory, data model, integrations,
  cross-cutting concerns, risks and decisions, and test strategy are complete.
- Permissions, telemetry, performance, security/privacy, translations,
  integration behavior, and schema consequences are addressed when relevant.
- The design preflights applicable hard rules from `al-code-review`: no planned
  `ODataKeyFields`, least-privilege permissions and an
  intentional public surface, plus applicable page/codeunit/event/API,
  integration, error-handling, telemetry, and testability seams.
- Schema and compatibility decisions use the explicit app-local compatibility
  fields in `APP_CONTEXT.md`. A release tag alone never overrides `no`. When
  compatibility is `yes`, require the trusted released baseline ref and design
  against it; a missing baseline makes compatibility review partial. Do not mix
  this house boundary into the portable BCQuality action.
- The plan's test strategy is coherent with the approved spec's explicit test
  decision, and the task list covers the planned design completely, including
  permission and telemetry work where relevant. Presence, absence, and shape
  of test tasks were already verified mechanically.

## Source verification (do it in the first pass)

Source-verification depth is a first-pass duty, not something later runs
discover. On the FIRST run of a gate, verify against the AL source and the
declared metadata every load-bearing claim the plan makes, including: the
actual field-id tails of every extended
table; band-map claims against `tech-design.md`; rename and reference counts
the plan asserts; interaction points (call sites, events, page areas) the plan
names; and the permission/sweep/upgrade consequences of every schema change.
Object-ID freeness and range conformance are the mechanical stage's duty; do
not duplicate them. The findings report must state which claims were verified
in source and which could not be
reached, so a later pass cannot silently deepen what the first pass asserted.

## Rerun discipline

The mechanical stage reruns before every semantic rerun; a mechanical failure
is fixed before a semantic run is spent. On a rerun, verify the prior
resolutions and the areas the fixes touched (the
coordinator supplies a statements-touched list), and re-verify any source
claim a fix invalidated. Do not expand the review to fresh scope beyond what
the fixes reach; new scope belongs to the first pass. The one exception that
justifies a new finding on a rerun is a contradiction a fix itself introduced
or a source fact a fix invalidated, and the finding must say which fix
surfaced it.

## Findings

Use `block` for an unapproved or contradictory spec, an unresolved required
decision, or a design that contradicts approved intent. Use `warn` for an
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
