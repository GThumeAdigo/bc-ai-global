# Feature Validation: <feature name>

- **Feature id:** <NNN-slug>
- **Final Test outcome:** pending | pass | fail
- **Validated by/date:** <name, YYYY-MM-DD>

## Initial Pre-Test Semantic Gate

- Reviewer/date:
- Outcome: pass | fail
- Implementation revision/hash:

## Compile and baseline

- App/project:
- Compile command:
- Result and warning count:
- Baseline command/evidence:
- New diagnostics versus baseline:

## Automated test execution

- Automated tests decision: yes | no
- Runner and selection:
- Required test count / executed / passed / failed:
- BCQuality outcome, verbatim:
- `summary.execution.status`, verbatim:
- No tests selected because tests=no: yes | no
- No supported runner available: yes | no
- Reruns after fixes:

When tests are `yes`, Test cannot pass with failures, a partial or failed runner,
or any required test left unexecuted.

## Verifier run 1

- Applicable mandatory set:
- Conditional integration trio applicable: yes | no
- Results and findings:

## Resolution and waivers

- Finding resolutions:
- Approved waivers: <rule/finding, reason, owner, approver, approval date; or none>

Only a resolved finding or a durable waiver with explicit owner and approval
date may proceed. An acknowledgement is not a waiver.

## Verifier run 2

- Exact rerun set:
- Results:
- Confirmation that first-run findings are resolved or waived:

## Post-Test-Fix Semantic Reruns

- Production behavior changed during Test: yes | no
- Reruns: <reviewer/date, outcome, implementation revision/hash; or none>

## Client verification

- Method: manual recipe | bc-webclient-runner
- Environment:
- Steps or guide section:
- Result and evidence:

## Final Test decision

- Outcome: pass | fail
- Decision owner/date:
- Blocking items or approved waivers:
