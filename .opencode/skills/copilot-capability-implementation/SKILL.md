---
name: copilot-capability-implementation
description: Reviews the AL implementation of a Business Central Copilot capability built on the System.AI Azure OpenAI module and emits a findings report.
---

# copilot-capability-implementation

The authoritative content for this reusable action skill is maintained in the
`GThumeAdigo/BCQuality-ADIGO` custom layer and vendored here. Microsoft-authored
corpus content has `microsoft/BCQuality` as its canonical upstream. Build complete
task context in memory or a temporary path outside the workspace. Run
`.opencode/BCQuality-ADIGO/tools/route_entry.py` directly, or through `python3`
when it is not executable, with `requested-skill-id: al-copilot-capability-implementation`.
Never fuzzy-route or require a workspace task-context file. Then
and complete its index preparation, then read and follow the exact target:

`.opencode/BCQuality-ADIGO/custom/skills/copilot/al-copilot-capability-implementation.md`

Do not edit guidance inline here. Update and merge the custom action skill in
`GThumeAdigo/BCQuality-ADIGO`, then bump this scaffold's submodule commit. This
pointer only makes the skill discoverable.
