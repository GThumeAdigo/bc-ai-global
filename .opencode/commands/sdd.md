---
description: Route an AL change or continue approved work using risk-adaptive SDD.
---

Load `.opencode/skills/sdd/SKILL.md` and follow the selected path for $ARGUMENTS.
Coordinate in the current primary conversation, retaining its permissions. Do
not switch a Plan session into Build implicitly or delegate the entire workflow.
If invoked inside a specialist child session, return the request to its parent.

Resolve a feature id/path or a description from the request. With no arguments,
ask which change to work on; do not start the next roadmap item automatically.
Identify the target AL app before creating artifacts. Respect an explicit stage
such as `spec`, `plan` or `implement` as the requested scope, not permission to
run the whole loop. In v2 Compact, an approach can live inside the spec; a `plan`
request does not itself require a separate plan file.

Inspect the feature's workflow declaration before resuming existing work. Legacy
work stays on its recorded baseline or requires explicit migration. The skill
owns approval, review selection, verification and stopping; do not invent extra gates.
