# Feature Tasks: <feature name>

> Reviewed by the plan gate (mechanical stage, then `/al-plan-feature`) alongside `plan.md`. An ordered, checkable list the
> Implement step works top to bottom. Keep tasks small and verifiable. Tick each
> as it lands.

- **Feature id:** <NNN-slug>
- **Plan:** ./plan.md
- **Status:** planned

## Common Tasks

- [ ] 1. <Object or change> — <what and the acceptance criterion it serves>
- [ ] 2. ...
- [ ] 3. Add permission set entries for every new object
- [ ] 4. Add telemetry on the protected operations named in the spec
- [ ] 5. Run `/al-implement-feature`, resolve findings, rerun it to pass, and record the initial semantic gate in `validation.md`
- [ ] 6. In Test, compile and record the baseline comparison in `validation.md`

## Automated Tests: Yes

Include this block only when `Automated tests: yes`. When tests are `no`, remove
this whole block and add no replacement runner, coverage, validator, writer, or
confirmation task.

- [ ] 7. Write automated tests for every acceptance criterion
- [ ] 8. Run `al-test-runner`; fix and rerun until every required test executes and passes
- [ ] 9. Run `al-test-coverage-validator` and `al-test-validator` in both verifier passes

## Test And Docs

- [ ] 10. Run the exact applicable verifier set, resolve findings or approved waivers, and rerun that set
- [ ] 11. If Test changed production behavior, rerun `/al-implement-feature` to pass and record each rerun separately
- [ ] 12. Execute and record a passing manual recipe or web-client run
- [ ] 13. After Test passes, update feature docs and move the roadmap item to done

## Done when

Every acceptance criterion in `spec.md` is satisfied (and, when tests are opted
in, executed and covered by a passing test), both verifier passes are recorded,
manual or web-client verification passes, Docs is complete, and the roadmap item
is marked done.
