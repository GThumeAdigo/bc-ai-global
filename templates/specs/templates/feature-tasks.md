# Feature Tasks: <feature name>

> Reviewed by the plan gate (mechanical stage, then `/al-plan-feature`) alongside `plan.md`. An ordered, checkable list the
> Implement step works top to bottom. Keep tasks small and verifiable. Tick each
> as it lands.
> Keep executable task markers at zero to three leading spaces. Deeper or
> tab-indented lines are literal content for the canonical digest.

- **Feature id:** <NNN-slug>
- **Plan:** ./plan.md
- **Status:** planned

## Common Tasks

- [ ] 1. <Object or change>: <what and the acceptance criterion it serves>
- [ ] 2. ...
- [ ] 3. Add permission set entries for every new object
- [ ] 4. Add telemetry on the protected operations named in the spec

## Write Automated Tests: Yes

Include this block only when `Automated tests: yes`. When tests are `no`, remove
this whole block and the opted-in execution block below. Renumber the remaining
tasks in order; add no replacement runner, coverage, validator, or writer task.

- [ ] 5. Write automated tests for every acceptance criterion before semantic review and compilation

## Semantic Review And Compile

- [ ] 6. Run `/al-implement-feature` to pass, resolving findings and confirming fixes when required; record the initial semantic gate in `validation.md`
- [ ] 7. In Test, compile and record the baseline comparison in `validation.md`

## Execute Automated Tests: Yes

Include this block only when `Automated tests: yes`.

- [ ] 8. Run `al-test-runner`; fix and rerun until every required test executes and passes, before the verifier set below

## Test And Docs

- [ ] 9. Run the applicable verifier set (including `al-test-coverage-validator` and `al-test-validator` only when tests are yes). One complete finding-free pass on unchanged inputs suffices; fixes, waivers, or relevant input changes require confirmation by the exact applicable set, adding new triggers and never narrowing reruns. Partial/API-failed reviews never pass
- [ ] 10. If Test changed production behavior, rerun `/al-implement-feature` to pass and record each rerun separately
- [ ] 11. Execute and record a passing manual recipe or web-client run
- [ ] 12. After Test passes, update feature docs and move the roadmap item to done

Evaluate specialist triggers independently: integration-pattern review for
changed actual BC external flows, Azure validation only for changed Azure
integration artifacts, and subscriber audit only for changed subscribers or
affected publisher signatures.

## Done when

Every acceptance criterion in `spec.md` is satisfied (and, when tests are opted
in, executed and covered by a passing test), the initial verifier pass and all
required confirmation passes are recorded,
manual or web-client verification passes, Docs is complete, and the roadmap item
is marked done.
