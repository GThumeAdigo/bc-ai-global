---
name: ai-agent-sdk
description: Reviews AL source that defines and registers a custom Business Central agent with the AI Agent SDK and emits a findings report.
---

# ai-agent-sdk

The authoritative content for this reusable action skill is maintained in the
`GThumeAdigo/BCQuality-ADIGO` custom layer and vendored here. Microsoft-authored
corpus content has `microsoft/BCQuality` as its canonical upstream. Build complete
task context in memory or a temporary path outside the workspace. Run
`.opencode/BCQuality-ADIGO/tools/route_entry.py` directly, or through `python3`
when it is not executable, with `requested-skill-id: al-ai-agent-sdk`. Never
fuzzy-route or require a workspace task-context file. Complete its
index preparation. Execute only on `outcome: routed`, using returned
`dispatch[].skill.path` relative to `.opencode/BCQuality-ADIGO/`. On `no-match`
or `failed`, return the dispatch record without a review-pass claim or static
fallback. Before execution, match the expected target below; on mismatch, stop
and report the record and mismatch. Expected-target guard:

`.opencode/BCQuality-ADIGO/custom/skills/copilot/al-ai-agent-sdk.md`

Do not edit guidance inline here. Update and merge the custom action skill in
`GThumeAdigo/BCQuality-ADIGO`, then bump this scaffold's submodule commit. This
pointer only makes the skill discoverable.
