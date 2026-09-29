---
description: Review a feature specification in specs/features/ for constitution-consistency, testable acceptance criteria, and resolved open questions.
agent: al-sdd-reviewer
---

Run the spec gate (the `al-spec-feature` skill) for $ARGUMENTS. Resolve the
repository root, feature id, `specs/features/<id>/spec.md`, constitution files,
`APP_CONTEXT.md`, and roadmap entry from the current checkout. Do not expect
hidden dispatcher inputs. Freshly execute the canonical
`python3 .opencode/skills/sdd/scripts/artifact_hash.py` on the current spec path
and include sdd-artifact-v1 digest execution evidence in the report. Missing
execution is partial/block, never pass. Emit the skill's local governance
findings report. Human approval remains a hard stop after a passing review.
