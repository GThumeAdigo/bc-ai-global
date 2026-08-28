---
description: Review a feature implementation for semantic conformance with its approved spec, plan, tasks, and acceptance criteria before testing.
agent: al-implement-feature-reviewer
---

Review the feature implementation for $ARGUMENTS. Resolve the repository root,
feature artifacts including `approvals.md`, planned object inventory, task list, and implemented source
from the current checkout. Do not expect hidden dispatcher inputs or require a
pre-supplied diff. Recompute full-file SHA-256 values for `spec.md`, `plan.md`,
and `tasks.md` and require each to match its review and human-approval digest.
Follow `al-implement-feature` and emit its local governance
findings report. Do not perform Test-step verification or closeout checks.
