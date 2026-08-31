# Feature Plan: <feature name>

> Reviewed by the plan gate (mechanical stage, then `/al-plan-feature`) after drafting from an approved `spec.md`. The how. Inherits from
> `specs/tech-design.md` and the house rules and style guide in
> `.opencode/skills/al-code-review/` (`SKILL.md` and `styleguide.md`).
> Stop for human review before implementing.

- **Feature id:** <NNN-slug>
- **Spec:** ./spec.md
- **Status:** planned
- **Automated tests:** yes | no (must match `spec.md`)
- **Test decision owner/date:** <name, YYYY-MM-DD>
- **Test decision reason:** <copied from `spec.md`>

## Approach

The implementation strategy in two or three sentences. Reuse standard BC first;
state what is custom and why.

## Standard BC reused

- Module / object and how this feature builds on it.

## AL objects to add or extend

| Object | Type | ID | New/Extend | Purpose |
|---|---|---|---|---|
| <Name> | table/page/codeunit/enum/permissionset | 5xxxx | new | ... |

All IDs must sit inside the assigned range from `specs/tech-design.md`.

## Data model

New tables, key fields, keys, and relations to standard BC tables.

## Integration points

External calls, events subscribed/published, APIs. Note idempotency and auth.

## Cross-cutting

- Permissions: which permission set entries.
- Telemetry: which operations emit, and the event ids.
- Schema and compatibility: what changes, what existing consumers must do, and
  the explicit compatibility decision and trusted baseline from `APP_CONTEXT.md`.
  A release tag alone never enables compatibility requirements.
- Performance: hot paths to watch (filters, loops, FlowFields on lists).

## Risks and decisions

Trade-offs taken, and anything the reviewer should scrutinise.

## Test strategy

The test decision above must match `spec.md`. When it is `yes`, describe how each
acceptance criterion becomes a test (AL test codeunit, Page Scripting, etc.). When
it is `no`, state that no automated test artifacts or test verifiers will be used.
