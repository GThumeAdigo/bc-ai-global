# Compact SDD

Target: spec, implement, one review-fix pass. Three agent runs plus builds.

1. Dispatch `al-spec-writer` (or draft yourself) to create
   `specs/features/<id>/spec.md` from the compact template. It captures outcome,
   scope/non-goals, acceptance scenarios, short approach, risks, verification and
   the style sections to load. Resolve its batched owner questions together and
   request one human approval. Record an immutable approval snapshot with its
   path in the spec's status section (below the status marker).
2. Check approval, then dispatch `custom-al-implementer` with the spec path. It
   writes to the style guide, compiles and runs the applicable existing tests and
   opted-in new tests. Execute UI checks only when acceptance depends on rendered
   behavior. Keep progress in the status section.
3. Dispatch `al-review-fixer` once with spec, changed scope and evidence. It
   corrects behavior-neutral defects itself and rebuilds. Behavior findings come
   back; send them to the implementer in one batch, rerun affected checks, and
   stop. The fixer's own edits are not reviewed again.
4. Record evidence, the fixer's change log and outcome in the status section.
   One Markdown file normally suffices. No separate tasks or approvals file.
