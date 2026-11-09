# Critical SDD

Target: spec and plan, design review, implement, one independent review. Five to
six agent runs plus builds.

Investigate the actual control/data paths and failure behavior before designing.
`al-spec-writer` drafts the spec for intent and a focused plan for invariants,
public contracts, transaction/data lifecycle, compatibility baseline,
authorization/company scope, dependencies, performance and recovery. Include only
relevant risk sections.

Run `al-design-reviewer` once to challenge load-bearing assumptions against source
and platform evidence. Apply its findings in one batch, settle decisions with the
owner and approve the coherent spec/plan packet once. Rerun the design reviewer
only on a changed load-bearing decision, scoped to it. Separate approvals only for
genuinely distinct unresolved decisions. Record snapshots; check them before
implementation and resume.

Implement through `custom-al-implementer` in verifiable increments, compiling and
running relevant regression/failure tests. Then run one read-only
`al-change-reviewer` on the final code and evidence. Add a distinct specialist
only for a named risk, for example transaction rollback versus permission/company
isolation; each runs once. Test review checks assertions and coverage, not a
second style audit. Send all findings to the implementer in one batch.
Missing required execution stays blocked/partial until resolved or an adequate
owner-approved alternative is recorded.

Keep results, current progress and approval references in the spec's status
section. No mandatory further document or a reviewer for every listed risk.
