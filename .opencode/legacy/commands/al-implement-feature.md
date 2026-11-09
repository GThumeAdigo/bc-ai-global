---
description: Legacy pre-Test implementation gate. V2 final review uses al-change-reviewer.
agent: al-implement-feature-reviewer
---

Check the workflow declaration first. For v2, return a routing notice to the
primary conversation to select its v2 final review; do not run this pre-Test gate
or require legacy artifacts. Unknown format requires coordinator classification.

Review the legacy feature implementation for $ARGUMENTS. Resolve the repository root,
feature artifacts including `approvals.md`, planned object inventory, task list, and implemented source
from the current checkout. Do not expect hidden dispatcher inputs or require a
pre-supplied diff. Freshly execute the canonical
`python3 .opencode/skills/sdd/scripts/artifact_hash.py` on current `spec.md`,
`plan.md`, and `tasks.md` paths using sdd-artifact-v1 and require each to match
its review and human-approval digest. Report execution evidence. Missing or
failed execution is partial/block, never pass; recorded-only agreement is insufficient.
Follow `al-implement-feature` and emit its local governance
findings report. Do not perform Test-step verification or closeout checks.
