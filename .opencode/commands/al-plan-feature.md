---
description: Review a feature plan and task list against its approved spec, object ID range, and verifier expectations.
agent: al-sdd-reviewer
---

Run the semantic plan gate (the `al-plan-feature` skill) for $ARGUMENTS. The
mechanical stage (`al-plan-mechanical`) must already have passed for the
current revision; if there is no passing mechanical report, stop and dispatch
`al-sdd-mechanical-reviewer` first. Resolve the
repository root, feature id, `spec.md`, `plan.md`, `tasks.md`, `approvals.md`,
project context, manifest, and object-range configuration from the current checkout.
Recompute the full `spec.md` SHA-256 and require it to match both Spec review and
approval digests before reviewing Plan. Do not require Plan's own not-yet-written
approval evidence. Do not expect hidden dispatcher inputs. Emit the local
governance report.
