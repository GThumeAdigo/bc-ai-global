---
description: Review a legacy feature spec under its existing approval contract. New work uses /sdd.
agent: al-sdd-reviewer
---

Check the feature's workflow declaration first. For `risk-adaptive-v2`, return a
routing notice to the primary conversation; do not require legacy artifacts or
run this gate. Missing workflow metadata is legacy only when existing legacy
artifacts establish that; otherwise ask the primary coordinator to classify it.

Run the legacy spec gate (the `al-spec-feature` skill) for $ARGUMENTS. Resolve the
repository root, feature id, `specs/features/<id>/spec.md`, constitution files,
`APP_CONTEXT.md`, and roadmap entry from the current checkout. Do not expect
hidden dispatcher inputs. Freshly execute the canonical
`python3 .opencode/skills/sdd/scripts/artifact_hash.py` on the current spec path
and include sdd-artifact-v1 digest execution evidence in the report. Missing
execution is partial/block, never pass. Emit the skill's local governance
findings report. Human approval remains a hard stop after a passing review.
