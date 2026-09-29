---
description: Run the Spec-Driven Development workflow for one step or the full Spec, Plan, Implement, Test, Docs, and Merge loop.
---

Use the `sdd` skill and execute the following request through it. Identify the
feature from the arguments (a feature id, a path under `specs/features/`, or a
short description that maps to the roadmap); if none is given, read
`specs/roadmap.md`, propose the next feature, and confirm before starting.

Use pinned subagents for the work assigned to them: `al-sdd-mechanical-reviewer`
for the mechanical stage of the plan gate, `al-sdd-reviewer` for each semantic
document gate, `custom-al-implementer` for drafting governed documents and for
approved implementation tasks, `al-implement-feature-reviewer` for pre-Test
semantic conformance, and the
applicable verifier agents during Test. The coordinator may do short routing,
status updates, and result synthesis itself; spec, plan, and task artifacts are
drafted by the delegated implementer, never by the coordinator. The approval
gates after spec and plan review are hard stops, so normal flow does not share
reviewer context across them.

Pass paths, not contents. Verifier dispatches require Serena-first AL navigation,
workspace-relative paths, and conversion of 0-based Serena lines to 1-based
report locations. Require fresh canonical sdd-artifact-v1 helper execution for
digest checks; unavailable execution is partial/block, never recorded-only pass.
If `/al-plan-feature` returns `mechanical-prerequisite-required`, the coordinator
runs mechanical then semantic, preserving the human approval stop.
One complete finding-free verifier pass on unchanged inputs suffices. Fixes,
waivers, or relevant input changes require the exact applicable set's
confirmation, adding newly triggered reviewers and never narrowing reruns.
Partial or API-failed results never pass. Use the SDD skill's independent
external-flow, Azure-artifact, and subscriber/publisher-signature triggers.

If OpenCode exposes a prior Task `task_id`, resume that specific single-gate
review only when continuation is intended; otherwise dispatch a fresh gate.
Never claim ordinary subagent invocations share context.

$ARGUMENTS
