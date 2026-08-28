---
description: Run the Spec-Driven Development workflow. Loads the SDD skill and executes the request, whether that is one loop step (spec, plan, implement, test, docs) or the full loop for a feature.
---

Use the `sdd` skill and execute the following request through it. Identify the
feature from the arguments (a feature id, a path under `specs/features/`, or a
short description that maps to the roadmap); if none is given, read
`specs/roadmap.md`, propose the next feature, and confirm before starting.

Run each loop step in its pinned subagent: `al-sdd-reviewer` (spec, plan, and
constitution gates; dispatch one gate at a time, or several together when
re-reviewing amended artifacts), `custom-al-implementer`,
`al-implement-feature-reviewer`, and the mandatory verifier agents. This
session coordinates and reports; it does not do the step's work itself. The
approval gates after the spec review and the plan review are hard stops.

$ARGUMENTS
