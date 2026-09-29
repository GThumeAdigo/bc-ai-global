# Critical SDD

Investigate the actual control/data paths and failure behavior before designing.
Use a compact spec for intent and a focused plan for invariants, public contracts,
transaction/data lifecycle, compatibility baseline, authorization/company scope,
dependencies, performance and recovery. Include only relevant risk sections.

Ask `al-design-reviewer` to challenge load-bearing assumptions against source and
platform evidence. Settle decisions with the owner and approve the coherent
spec/plan packet once. Separate approvals only when there are genuinely distinct
unresolved decisions. Record snapshots; check them before implementation/resume.

Implement in verifiable increments. Compile and run relevant regression/failure
tests before final independent change review. Use distinct specialist scopes
where warranted, for example transaction rollback versus permission/company
isolation. Test review checks assertions and coverage, not a second style audit.
Missing required execution stays blocked/partial until resolved or an adequate
owner-approved alternative is recorded. Common repair budgets still apply.

Keep results, current progress and approval references in `validation.md`.
Do not create a mandatory fifth document or a reviewer for every listed risk.
