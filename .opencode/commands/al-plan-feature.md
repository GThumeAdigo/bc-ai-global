---
description: Review a feature plan and task list against its approved spec, object ID range, and verifier expectations.
agent: al-sdd-reviewer
---

Run the plan gate (the `al-plan-feature` skill) for $ARGUMENTS. Resolve the
repository root, feature id, approved `spec.md`, `plan.md`, `tasks.md`, project
context, manifest, and object-range configuration from the current checkout.
Do not expect hidden dispatcher inputs. Emit the local governance report.
