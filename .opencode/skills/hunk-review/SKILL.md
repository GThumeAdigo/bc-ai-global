---
name: hunk-review
description: Optional German inline explanations or findings in an existing matching Hunk session. Use for a requested walkthrough or a useful stable review checkpoint, not as a completion gate.
---

# Hunk review presentation

Resolve the installed CLI's authoritative instructions with
`"$HOME/.hunk/bin/hunk" skill path`, then read that file. Do not launch a TUI on
the user's behalf or copy the CLI documentation into the scaffold.

The coordinator owns publication. Match `session list --json` to the exact
checkout and reviewed revision. If no matching session exists, defer without
blocking work or requiring the owner to open another tool.

Inspect existing notes and live hunk anchors before publishing. Batch useful
German notes, distinguishing actionable defects from intent/tradeoff explanations.
There is no quota. Avoid obvious restatements of the diff. Publish without moving
the viewport unless the owner requested a walkthrough.

Read notes back and check whether agent notes are visible. After a relevant code
change, refresh only this task's notes and preserve human/unrelated notes. Report
published count or the deferral reason once. Hunk does not prove build, tests or
rendered UI behavior and never replaces their evidence.
