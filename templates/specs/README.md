# Product intent and decisions

`brief.md` owns outcomes, `tech-design.md` owns durable architecture decisions,
and `roadmap.md` is the optional delivery index. Fill relevant product facts;
do not duplicate manifest values or agent workflow policy here.

The authoritative workflow is `.opencode/skills/sdd/SKILL.md`.
New bounded behavior uses `templates/compact-spec.md` and
`templates/change-validation.md`. Critical work adds `templates/critical-plan.md`.
Declare `path: critical` in its spec. Direct changes need no feature directory.

The old `feature-*.md` templates remain for legacy features only. Existing
approvals retain the old contract until explicitly migrated. Private specs are
not protected by product Git by default; keep deliberate backups. Approval
snapshots preserve intent even when working documents are later amended.
