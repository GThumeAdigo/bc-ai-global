---
name: al-spec-init
kind: governance-skill
id: al-spec-init
version: 1
title: SDD Constitution Review
description: Reviews a Business Central project's Spec-Driven Development constitution (brief, tech design, roadmap) for completeness and consistency, and emits a findings report.
inputs: [repository, app-context, constitution-paths]
outputs: [governance-findings]
bc-version: [all]
technologies: [al]
countries: [w1]
application-area: [all]
---

# SDD Constitution Review

This scaffold-local governance skill reviews the project constitution before
feature work. It is not a BCQuality action skill.

## Inputs

Resolve the repository root and read `APP_CONTEXT.md`, `AGENTS.md`,
`specs/brief.md`, `specs/tech-design.md`, and `specs/roadmap.md`. Preserve valid
existing decisions when reviewing an update and never invent app-specific facts.

One complete finding-free pass on unchanged review inputs suffices. Fixes,
waivers, or relevant input changes require confirmation by the same applicable
gate set. Missing coverage or API-failed review is `outcome: partial` with a
blocking finding, never pass. This constitution gate has no artifact digest
approval prerequisite.

## Checks

- `APP_CONTEXT.md` identifies the app, workspace dependencies, AL conventions,
  assigned object range, and verification environment without placeholders.
- `specs/brief.md` defines customer context, goals, non-goals, business
  processes, constraints, and measurable success without prescribing AL.
- `specs/tech-design.md` identifies the standard BC capabilities to reuse,
  justifies custom-code gaps, and defines architecture, data, integrations,
  cross-cutting concerns, and object-ID governance.
- `specs/roadmap.md` is an ordered, numbered feature list with explicit status,
  using ids that can map to `specs/features/<NNN-slug>/`, and defines the exact
  transitions `todo -> spec` on Spec draft, `spec -> planned` on Plan draft,
  `planned -> in-progress` after Plan approval, and `in-progress -> done` only
  after Test and Docs pass.
- The three documents agree and make open decisions visible for human review.

Use `block` for a missing constitution document, unresolved placeholder needed
for feature work, absent object-ID governance, or direct contradiction. Use
`warn` for incomplete coverage or inconsistent roadmap structure. Use `info`
sparingly. Return the local governance shape defined by `al-spec-feature`, with
`gate: "al-spec-init"`; do not emit BCQuality DO references.
