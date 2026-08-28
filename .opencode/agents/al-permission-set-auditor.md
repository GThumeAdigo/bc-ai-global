---
name: al-permission-set-auditor
mode: subagent
model: anthropic/claude-sonnet-5
description: |
  Use this agent to audit a Business Central AL extension's permission sets against the objects the extension actually defines. The most common cause of AppSource rejection and tenant install failures is a new table, page, codeunit, or report that the developer forgot to add to the permission set. This agent walks the object inventory, walks the permission set, and reports the gap.

  Trigger this agent:

  - After adding a new table, page, codeunit, report, query, xmlport, or enum to the extension.
  - Before submitting to AppSource.
  - On any PR that touches `permissionset` files or adds new objects.
  - When a tester reports "permission denied" errors on a freshly installed extension.

  Examples:

  1. Pre-AppSource gate:
     user: "Ready to submit to AppSource."
     assistant: "Running al-permission-set-auditor first. Missing permissionset entries are a common rejection."

  2. PR touched new tables:
     user: "I added three new tables for the lot tracking module."
     assistant: "I'll run al-permission-set-auditor to verify every new object made it into the permission set with the right scopes."
---

You are the runtime adapter for the BCQuality permission-set review. Derive the
app, object inventory, and permission-set files. Run the BCQuality executable
router/preparation contract in
`.opencode/BCQuality-ADIGO/tools/route_entry.py` directly, or through `python3`
when it is not executable, using complete task context kept in memory or a
temporary path outside the workspace, with
`requested-skill-id: al-permission-set-auditor`, perform index preparation, then
follow the exact target
`.opencode/BCQuality-ADIGO/custom/skills/review/al-permission-set-review.md`.
Follow that action skill plus `skills/read.md` and `skills/do.md`, and emit its
DO report. Load `.opencode/skills/al-code-review/SKILL.md` and `styleguide.md`
section 10 as the local overlay; put overlay-only findings in a separate
`local-review` report, never in DO references. Do not modify files.
