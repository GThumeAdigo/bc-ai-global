---
description: Legacy constitution review. For new risk-adaptive work use /sdd.
agent: al-sdd-reviewer
---

Only run for an explicitly requested legacy constitution review. For v2/new work,
return a routing notice to the primary conversation to use `/sdd`; do not require
a legacy constitution gate. This command does not migrate a project.

Run the constitution gate (the `al-spec-init` skill). Resolve the repository
root from the current checkout and read `APP_CONTEXT.md`, `AGENTS.md`,
`specs/brief.md`, `specs/tech-design.md`, and `specs/roadmap.md`. Do not expect
hidden dispatcher inputs. Emit the local governance findings report.

$ARGUMENTS
