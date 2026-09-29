# Feature Validation: <feature name>

- **Feature id:** <NNN-slug>
- **Final Test outcome:** pending | pass | fail
- **Validated by/date:** <name, YYYY-MM-DD>

## Initial Pre-Test Semantic Gate

- Reviewer/date:
- Outcome: pass | fail | partial
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
- Review input revision/evidence (source, artifacts, policy):
- Integration-pattern reviewer: changed actual BC external flows, yes | no, paths/reason:
- Azure validator: changed Azure integration artifacts, yes | no, paths/reason:
- Subscriber auditor: changed subscribers or affected publisher signatures, yes | no, paths/reason:
- Results and findings:
- Complete and finding-free on unchanged inputs: yes | no

## Resolution and waivers

- Finding resolutions:
- Approved waivers: <rule/finding, reason, owner, approver, approval date; or none>

Only a resolved finding or a durable waiver with explicit owner and approval
date may proceed. An acknowledgement is not a waiver.

## Required confirmation runs (or not required)

- Required because of fixes, waivers, or relevant input changes: <reason | not required: clean complete first pass, inputs unchanged>
- Exact applicable rerun set (retain original set, add new triggers):
- Review input revision/evidence:
- Results:
- Confirmation that first-run findings are resolved or waived:

One complete finding-free pass on unchanged review inputs suffices. Do not
repeat clean identical work. When confirmation is required, rerun the exact
applicable set, never a narrowed subset. Repeat this section for every required
run. Partial or API-failed reviews never count as passes.

## Post-Test-Fix Semantic Reruns

- Production behavior changed during Test: yes | no
- Reruns: <reviewer/date, outcome, implementation revision/hash; or none>

## Client verification

- Method: manual recipe | bc-webclient-runner
- Environment:
- Steps or guide section:
- Result and evidence:

## Hunk review notes

- Publication: <count and matching checkout | deferred with reason | no useful notes, reason>
- Read-back and visibility: <confirmed | hidden, developer notified | not applicable>

This records presentation status only. No matching live session does not block
Test; follow `.opencode/skills/hunk-review/SKILL.md` for publication and refresh.

## Final Test decision

- Outcome: pass | fail
- Decision owner/date:
- Blocking items or approved waivers:
