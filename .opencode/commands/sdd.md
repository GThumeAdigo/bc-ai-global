---
description: Run the Spec-Driven Development workflow for one step or the full Spec, Plan, Implement, Test, Docs, and Merge loop.
---

Use the `sdd` skill and execute the following request through it. Identify the
feature from the arguments (a feature id, a path under `specs/features/`, or a
short description that maps to the roadmap); if none is given, read
`specs/roadmap.md`, propose the next feature, and confirm before starting.

Use pinned subagents for the work assigned to them: `al-sdd-reviewer` for each
document gate, `custom-al-implementer` for approved implementation tasks,
`al-implement-feature-reviewer` for pre-Test semantic conformance, and the
applicable verifier agents during Test. The coordinator may do short routing,
artifact drafting, status updates, and result synthesis itself. The approval
gates after spec and plan review are hard stops, so normal flow does not share
reviewer context across them.

If OpenCode exposes a prior Task `task_id`, resume that specific single-gate
review only when continuation is intended; otherwise dispatch a fresh gate.
Never claim ordinary subagent invocations share context.

$ARGUMENTS
