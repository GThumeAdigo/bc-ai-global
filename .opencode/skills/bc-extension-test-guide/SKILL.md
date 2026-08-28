---
name: bc-extension-test-guide
description: Reviews a Business Central extension's QA test guide for exhaustive category coverage of every page, field, relation, state, and permission in the AL source, and emits a findings report.
---

# bc-extension-test-guide

The authoritative content for this reusable action skill is maintained in the
`GThumeAdigo/BCQuality-ADIGO` custom layer and vendored here. Microsoft-authored
corpus content has `microsoft/BCQuality` as its canonical upstream. Build complete
task context in memory or a temporary path outside the workspace. Run
`.opencode/BCQuality-ADIGO/tools/route_entry.py` directly, or through `python3`
when it is not executable, with `requested-skill-id: al-bc-extension-test-guide`.
Never fuzzy-route or require a workspace task-context file. Then
complete its index preparation, then read and follow the exact target:

`.opencode/BCQuality-ADIGO/custom/skills/testing/al-bc-extension-test-guide.md`

Do not edit guidance inline here. Update and merge the custom action skill in
`GThumeAdigo/BCQuality-ADIGO`, then bump this scaffold's submodule commit. This
pointer only makes the skill discoverable.
