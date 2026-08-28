# Feature Tasks: <feature name>

> Reviewed by `/al-plan-feature` alongside `plan.md`. An ordered, checkable list the
> Implement step works top to bottom. Keep tasks small and verifiable. Tick each
> as it lands.

- **Feature id:** <NNN-slug>
- **Plan:** ./plan.md
- **Status:** planned

## Tasks

- [ ] 1. <Object or change> — <what and the acceptance criterion it serves>
- [ ] 2. ...
- [ ] 3. Add permission set entries for every new object
- [ ] 4. Add telemetry on the protected operations named in the spec
- [ ] 5. (Tests opt-in, see Testing policy in `.opencode/skills/sdd/SKILL.md`) If tests are wanted: write AL tests for each acceptance criterion. Otherwise remove this task.
- [ ] 6. Run `/al-implement-feature` for semantic conformance before Test
- [ ] 7. In Test, build and run the applicable mandatory verifier set and BCQuality action skills twice; resolve findings
- [ ] 8. After Test passes, update feature docs and tick the roadmap item

## Done when

Every acceptance criterion in `spec.md` is satisfied (and, when tests are opted
in, covered by a passing test), the verifier set is clean, and the roadmap item
is marked done.
