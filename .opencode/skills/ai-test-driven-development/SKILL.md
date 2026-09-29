---
name: ai-test-driven-development
description: Reviews Business Central Copilot and agent test suites against the Evaluation-tool TDD discipline and emits a findings report.
---

# ai-test-driven-development

The authoritative content for this reusable action skill is maintained in the
`GThumeAdigo/BCQuality-ADIGO` custom layer and vendored here. Microsoft-authored
corpus content has `microsoft/BCQuality` as its canonical upstream. Build complete
task context in memory or a temporary path outside the workspace. Run
`.opencode/BCQuality-ADIGO/tools/route_entry.py` directly, or through `python3`
when it is not executable, with `requested-skill-id: al-ai-test-driven-development`.
Never fuzzy-route or require a workspace task-context file. Complete its
index preparation. Execute only on `outcome: routed`, using returned
`dispatch[].skill.path` relative to `.opencode/BCQuality-ADIGO/`. On `no-match`
or `failed`, return the dispatch record without a review-pass claim or static
fallback. Before execution, match the expected target below; on mismatch, stop
and report the record and mismatch. Expected-target guard:

`.opencode/BCQuality-ADIGO/custom/skills/testing/al-ai-test-driven-development.md`

Do not edit guidance inline here. Update and merge the custom action skill in
`GThumeAdigo/BCQuality-ADIGO`, then bump this scaffold's submodule commit. This
pointer only makes the skill discoverable.
