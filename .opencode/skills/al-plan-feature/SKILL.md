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
`tasks.md`, plus the relevant `app.json` and `AppSourceCop.json` when present.
Derive object ranges, prefixes, namespaces, dependencies, and test policy from
those files rather than assuming dispatcher-provided values.

## Checks

- The spec is approved, its open questions are resolved, and the plan maps each
  acceptance criterion without changing approved intent.
- The plan reuses standard BC first and justifies each custom-code gap.
- Every planned object has a purpose and, when applicable, an ID inside the
  app-local assigned range.
- Approach, standard BC reused, AL object inventory, data model, integrations,
  cross-cutting concerns, risks and decisions, and test strategy are complete.
- Permissions, telemetry, performance, security/privacy, translations,
  integration behavior, and schema consequences are addressed when relevant.
- The plan and spec contain the same explicit automated-test decision. If it is
  `yes`, tasks map tests to acceptance criteria and include test verifiers. If
  it is `no`, test-writing and test-verifier tasks are absent. Never infer a
  default for an omitted decision.
- `tasks.md` is ordered, checkable, and includes implementation, permission and
  telemetry work where relevant, then semantic implementation review, then a
  Test-step build and applicable verifiers, then Docs and roadmap closeout.
- The roadmap status is `planned`.

## Findings

Use `block` for an unapproved or contradictory spec, unresolved required
decision, test-policy mismatch, or out-of-range object ID. Use `warn` for an
incomplete design or task sequence. Use `info` sparingly.

Return the local governance shape defined by `al-spec-feature`, with
`gate: "al-plan-feature"`. `outcome` is `fail` when any `block` or `warn`
remains. Do not emit BCQuality DO references.
