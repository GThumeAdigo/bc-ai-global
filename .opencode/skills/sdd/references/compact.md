# Compact SDD

1. Create `specs/features/<id>/spec.md` from the compact template. Capture outcome,
   scope/non-goals, acceptance scenarios, short approach, risks and verification.
   Use relevant existing product context; do not repeat the entire constitution.
2. Resolve material questions together and request one human approval. Record an
   immutable approval snapshot and its path in `validation.md`.
3. Implement after checking approval. Keep progress in validation, not the spec.
4. Compile with analyzers; run applicable existing tests and opted-in new tests.
   Execute UI checks only when acceptance depends on rendered behavior.
5. Dispatch one independent `al-change-reviewer` on the final code and evidence.
   Apply the router's finding and bounded confirmation rules.
6. Record outcomes and relevant product documentation changes. Two Markdown files
   normally suffice: spec and validation. No separate tasks or approvals file.
