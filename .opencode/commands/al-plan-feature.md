---
description: Review a legacy plan after its mechanical gate. New work uses /sdd.
agent: al-sdd-reviewer
---

Check the workflow declaration before any prerequisite checks. For v2 work,
return a routing notice to the primary conversation to use `/sdd`; do not demand
legacy hashes, tasks or mechanical-gate evidence. Unknown format needs coordinator
classification, not creation of legacy artifacts.

Run the legacy semantic plan gate (the `al-plan-feature` skill) for $ARGUMENTS. The
mechanical stage (`al-plan-mechanical`) must already have passed for the
current revision; if there is no passing mechanical report, return
`mechanical-prerequisite-required` with `outcome: partial` to the coordinator.
You cannot dispatch another agent. The coordinator runs
`al-sdd-mechanical-reviewer` first and then dispatches this semantic gate. Resolve the
repository root, feature id, `spec.md`, `plan.md`, `tasks.md`, `approvals.md`,
project context, manifest, and object-range configuration from the current checkout.
Freshly execute `python3 .opencode/skills/sdd/scripts/artifact_hash.py` on current
spec, plan, and tasks paths using sdd-artifact-v1. Require the Spec digest to match both Spec review and
approval digests before reviewing Plan. Do not require Plan's own not-yet-written
approval evidence. Do not expect hidden dispatcher inputs. Emit the local
governance report with digest execution evidence. Missing or failed execution
is partial/block, never pass; recorded-only agreement is insufficient. A clean
complete pass suffices on unchanged inputs; fixes, waivers, or relevant input
changes require mechanical then semantic confirmation. Human approval remains
a hard stop after a passing Plan gate.
