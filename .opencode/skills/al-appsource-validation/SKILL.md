---
name: al-appsource-validation
description: Reviews a Business Central extension against the AppSource marketplace submission checklist and emits a findings report.
---

# al-appsource-validation

The authoritative content for this reusable action skill is maintained in the
`GThumeAdigo/BCQuality-ADIGO` custom layer and vendored here. Microsoft-authored
corpus content has `microsoft/BCQuality` as its canonical upstream. Build complete
task context in memory or a temporary path outside the workspace. Run
`.opencode/BCQuality-ADIGO/tools/route_entry.py` directly, or through `python3`
when it is not executable, with `requested-skill-id: appsource-validation`.
Never fuzzy-route or require a workspace task-context file. Complete its
index preparation. Execute only on `outcome: routed`, using returned
`dispatch[].skill.path` relative to `.opencode/BCQuality-ADIGO/`. On `no-match`
or `failed`, return the dispatch record without a review-pass claim or static
fallback. Before execution, match the expected target below; on mismatch, stop
and report the record and mismatch. Expected-target guard:

`.opencode/BCQuality-ADIGO/custom/skills/appsource/al-appsource-validation.md`

Do not edit guidance inline here. Update and merge the custom action skill in
`GThumeAdigo/BCQuality-ADIGO`, then bump this scaffold's submodule commit. This
pointer only makes the skill discoverable.
