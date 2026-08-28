# Feature Spec: <feature name>

> Reviewed by `/al-spec-feature`. The what and why for one feature. No AL, no object
> names yet (those belong in `plan.md`). Stop for human review before planning.

- **Feature id:** <NNN-slug>
- **Roadmap item:** <link or row in specs/roadmap.md>
- **Status:** spec
- **Automated tests:** yes | no
- **Test decision owner/date:** <name, YYYY-MM-DD>
- **Test decision reason:** <why tests are or are not included>

## Problem

What user problem does this feature solve? Why now?

## Users and roles

Who uses it, and in what role.

## Scope

What this feature includes. Bullet the user-visible capabilities.

## Out of scope

What it deliberately does not include (so the plan stays bounded).

## User flow

The main path, step by step, as the user experiences it. Note key alternates.

## Acceptance criteria

Testable, unambiguous. The automated-test decision above is required and remains
the durable source of truth for this feature. When set to `yes`, each criterion
becomes at least one test in the Implement step. Either way, each criterion must
be concrete enough to verify.

- [ ] Given ... when ... then ...
- [ ] ...

## Data and rules

Business rules, validations, state transitions, and the data the feature reads
or writes (in business terms).

## Telemetry and audit

What protected operations must emit telemetry (house rule).

## Open questions

Anything blocking a clean plan. Resolve with the owner before `/al-plan-feature`.
