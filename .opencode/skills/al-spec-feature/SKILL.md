---
name: al-spec-feature
kind: governance-skill
id: al-spec-feature
version: 1
title: Feature Specification Review
description: Reviews a Business Central feature specification for constitution-consistency, testable acceptance criteria, and resolved open questions, and emits a findings report.
inputs: [repository, feature-id, spec-path]
outputs: [governance-findings]
bc-version: [all]
technologies: [al]
countries: [w1]
application-area: [all]
---

# Feature Specification Review

This scaffold-local governance skill reviews one feature specification before
the human Spec approval stop. It is not a BCQuality action skill and does not
emit the BCQuality DO shape.

## Inputs

Resolve the repository and feature from the invocation. Read `APP_CONTEXT.md`,
`AGENTS.md`, `specs/brief.md`, `specs/tech-design.md`, `specs/roadmap.md`, and
`specs/features/<id>/spec.md`. The spec gate does not require `plan.md` or
`tasks.md`, and it must not require its own not-yet-written review or approval
metadata in `approvals.md`.

## Checks

- The feature id and roadmap entry agree, and the roadmap status is `spec`.
- The spec is consistent with the constitution's goals, non-goals, business
  rules, constraints, and standard-BC direction.
- Problem, users and roles, scope, out of scope, user flow, acceptance
  criteria, data and rules, telemetry and audit, and open questions are present.
- Acceptance criteria are concrete and observable regardless of whether their
  verification will be automated.
- The durable `Automated tests: yes | no` decision, owner/date, and reason are
  explicit. An absent decision blocks approval; do not infer a default.
- Unresolved product decisions remain explicit open questions. The reviewer
  does not guess them away.
- The spec states what and why without prescribing AL object names or IDs.

## Source verification (do it in the first pass)

Source-verification depth is a first-pass duty, not something later runs
discover. On the FIRST run of a gate, verify against the AL source every
load-bearing claim the spec makes, including: cited object ids and the actual
field-id tail of each touched table; enum ordinals and their free slots; gate
flags, commit points and call paths the design rests on (read the actual
procedures, do not infer from names); interactions with sweeping or cascading
mechanisms (delete sweeps, re-population gates, upload filters); permission
and DataClassification patterns of the touched tables; and each acceptance
criterion's reachability through the product as it ships today. The findings
report must state which claims were verified in source and which could not be
reached, so a later pass cannot silently deepen what the first pass asserted.

## Rerun discipline

On a rerun, verify the prior resolutions and the areas the fixes touched (the
coordinator supplies a statements-touched list), and re-verify any source
claim a fix invalidated. Do not expand the review to fresh scope beyond what
the fixes reach; new scope belongs to the first pass. The one exception that
justifies a new finding on a rerun is a contradiction a fix itself introduced
or a source fact a fix invalidated, and the finding must say which fix
surfaced it.

## Findings

Use `block` for a missing or contradictory foundation, an absent test decision,
or an unresolved decision needed for planning. Use `warn` for a missing section,
untestable criterion, roadmap mismatch, or implementation detail in the spec.
Use `info` sparingly for a material non-blocking observation.

Return only:

```json
{
  "gate": "al-spec-feature",
  "outcome": "pass | fail",
  "summary": "string",
  "findings": [
    {
      "severity": "block | warn | info",
      "rule": "sdd:short-slug",
      "message": "problem and required correction",
      "location": { "file": "specs/features/<id>/spec.md", "line": 1 }
    }
  ]
}
```

`outcome` is `fail` when any `block` or `warn` remains. Local governance
findings do not carry BCQuality `references`; cite the governing scaffold file
directly in `message` only when useful.

Human approval may be requested only after this same gate has been rerun with
`outcome: pass`. With `spec.md` unchanged after that run, calculate its full-file
SHA-256 and write the passing review, reviewer/date, digest, human approver/date,
and the same approved digest to `approvals.md`. Chat-only approval is not
durable. This gate emits the pass; it does not require that evidence beforehand.
