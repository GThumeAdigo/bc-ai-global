---
name: sdd
kind: workflow-skill
id: sdd
version: 1
title: Spec-Driven Development workflow
description: The house Spec-Driven Development workflow for AL features, the constitution, the per-feature loop (Spec, Plan, Implement, Test, Docs, Merge), the testing policy (opt-in), and the deployment policy (schema changes free). Use when starting, continuing, or reviewing feature work, when asked to run a feature through the SDD loop, and before writing any production AL for a feature. Do not load for quick fixes that are not feature work.
inputs: [feature-id, feature-path]
outputs: [spec, plan, tasks, approvals, validation, implementation]
bc-version: [all]
technologies: [al]
countries: [w1]
application-area: [all]
---

# Spec-Driven Development

**The spec is the brain, the agent is the muscle.** You do not write production
AL until an approved spec exists for the feature. Specs are durable artifacts
under `specs/`; a chat session is not. The developer architects the decisions in
the spec; the agent executes them.

This skill is the authoritative workflow. AGENTS.md keeps only a pointer to it.
If this skill and anything else disagree, this skill wins for workflow questions.

## Load discipline

The workflow must stay in context for the whole feature loop:

- Load this skill at the start of feature work and after every auto-compaction.
  Re-loading after compaction is mandatory, not optional: a summary of the
  workflow is not the workflow.
- One chat session per feature. On the first pass, read the complete constitution
  listed below. During later steps and after compaction, selectively re-read the
  sections that govern the current task rather than loading every file again.
- Not every task is a feature. Bug fixes, tweaks, and questions do not need
  this skill; do not create spec artifacts for them.
- On resume, whether after compaction or in a fresh session, read
  `specs/roadmap.md` and the feature's `approvals.md` Loop State section
  first. Resume from the recorded stage instead of reconstructing state from
  chat history.
- Read specs by section, not by whole file. Specs are durable and on disk, so
  they survive compaction and can be re-read at any time; treat the context
  window as scarce. When a spec is long, grep for the section header you need
  and read from there; the acceptance criteria and the task list are the usual
  targets. After auto-compaction, re-read the one section the current task
  depends on rather than reconstructing context from memory. Implementing a
  feature needs its approved `spec.md`, `plan.md`, and `tasks.md` plus
  `APP_CONTEXT.md`; it rarely needs the full brief again. Keep specs
  structured so this works: one feature per folder, stable section headers,
  and current-only content, with history in the approvals change log and git.

## Keep the main session small

The main session coordinates and delegates substantial specialist work.

- **Delegate where it reduces context or needs a pin.** Implementation goes to
  `custom-al-implementer`; document gates go to `al-sdd-reviewer`, with the
  plan gate's mechanical stage going to `al-sdd-mechanical-reviewer` first;
  semantic
  implementation conformance goes to `al-implement-feature-reviewer`; and
  mechanical reviews go to verifier agents. Open-ended exploration can go to a
  general subagent instructed to navigate AL with Serena. The spec, plan and
  task artifacts are also authored by the delegated implementer, not by the
  coordinator (see the per-feature loop). The coordinator may route, ask
  decisions, perform short lookups, update status, and synthesise results.
  Each gate agent follows its full local governance
  skill in `.opencode/skills/`; its frontmatter owns the model pin.
- **Reuse the house agents and skills where handy** instead of improvising:
  the review gates (`/al-spec-feature`, `/al-plan-feature`,
  `/al-implement-feature`, which dispatch the reviewer subagents), the
  mandatory verifier set, `al-compile`, and the house rules in
  `al-code-review` all exist for this loop.
- **Approval gates are hard stops.** Resolve every finding and rerun the same
  gate to `outcome: pass` before requesting the developer's Spec or Plan
  approval. Persist review and approval evidence in the app-local feature
  `approvals.md`, never inside the files being hashed. Never enter Plan without
  a matching approved full `spec.md` SHA-256, dispatch the implementer without
  matching approved canonical `plan.md` and `tasks.md` SHA-256 values, or enter Test
  until semantic implementation conformance has passed.
- **Keep the Loop State current.** The coordinator updates the `Loop State`
  section at the top of `approvals.md` at every stage transition and after
  every gate run. It is the resume point for a fresh or compacted session, so
  a stale state misdirects the next session.
- **Be precise and efficient in conversation.** One topic per message, short
  questions, short answers, findings with `file:line` references instead of
  prose. Batch clarifying questions into one round trip rather than trickling
  them. The conversation history is resent on every turn, so a session that
  wanders pays for the wandering all feature long.

## Model policy (which step runs on which model)

Installed agents use the model and variant from `runtime/model-policy.json`
rather than the session default. The installer applies this policy to every
agent in the consumer configuration:

- **Semantic SDD reviews use the shared model policy.** `al-sdd-reviewer` runs the
  specification, semantic plan, and constitution gates.
  `al-implement-feature-reviewer`
  compares approved intent with implemented behavior before Test. Normal hard-stop
  flow dispatches fresh gates and does not imply shared subagent context.
- **Implementation and mechanical checks use the same policy.** These include
  `custom-al-implementer`, `al-sdd-mechanical-reviewer` (the deterministic
  stage of the plan gate), the mandatory verifiers, test writers and
  validators, and specialist auditors. Their work is execution or structured
  rule-checking rather than semantic intent reconciliation.

The SDD gate commands (`/al-spec-feature`, `/al-plan-feature`,
`/al-implement-feature`, `/al-spec-init`) are thin dispatchers: their
frontmatter names the reviewer agent and carries no model pin. Change models
in `runtime/model-policy.json` and permissions in agent frontmatter; do not
reintroduce model pins on agents or commands.

Do not unpin an agent ad hoc for a single run. If a verifier systematically
misses a class of finding on its pinned variant, change the shared model policy
in the scaffolding repo rather than overriding it per session.

## The constitution (initial read, every feature)

- `APP_CONTEXT.md`: local app identity, conventions, dependencies, and
  environment-specific verification facts.
- `specs/brief.md`: customer requirements and business processes (the what and why).
- `specs/tech-design.md`: implementation strategy: which standard BC modules to
  reuse, and where custom code is genuinely needed.
- `specs/roadmap.md`: ordered list of features with status.
- `AGENTS.md`: the shared operational contract: project discovery, building,
  house-rule pointers, and the non-SDD path.

## Canonical artifact digests: sdd-artifact-v1

Use only the Python standard-library CLI from the repository root:

```bash
python3 .opencode/skills/sdd/scripts/artifact_hash.py specs/features/<id>/spec.md
python3 .opencode/skills/sdd/scripts/artifact_hash.py specs/features/<id>/plan.md specs/features/<id>/tasks.md
```

Outside the root, invoke the resolved absolute helper path and artifact paths.
The CLI is read-only and prints one SHA-256 and path per file, in sha256sum-like
format; any read error exits nonzero and invalidates the run. `--version` prints
`sdd-artifact-v1`. Store that recipe version with review evidence.

`spec.md` and `plan.md` are hashed as raw bytes. Only a file whose basename is
`tasks.md` normalizes task checkbox state: at the start of a line, zero to three
spaces, a list marker (`-`, `+`, `*`, or digits followed by `.` or `)`),
spaces/tabs, then `[ ]`, `[x]`, or `[X]` followed by a space/tab or line end.
Only the single state byte becomes a space. Backtick or tilde fences of at least
three characters, including indented fences, protect their entire contents;
closing fences must use the same character with at least the opening length
and only trailing spaces/tabs. Unclosed fences protect through EOF. Inline
checkbox literals, prose, fenced/indented examples, indentation, line endings, encoding,
and every other substantive byte are preserved. No trimming or newline conversion.

Each digest reviewer freshly executes the helper on current files, compares
required review/approval/current digests, and records execution evidence in its
report. Missing or failed execution yields `outcome: partial` with a blocking
finding, never pass. Agreement between recorded values alone is insufficient.
Before Plan drafting check Spec; before implementation check all three artifacts.
Keep executable tasks at zero to three spaces of indentation as in the template.
Deeper or tab-indented lines remain byte-for-byte significant to protect code
examples; the helper deliberately does not infer nested Markdown list structure.
Checkbox-only progress on supported task lines does not invalidate tasks approval.

Do not rewrite existing approvals during migration. If a legacy recipe or
unversioned record does not match current canonical evidence, stop for explicit
revalidation: retain the old evidence, rerun the affected gates, record the new
recipe and digests, and request human re-approval. Never automatically reapprove
or relabel old evidence as a current canonical review.

## The per-feature loop

For each feature: **Feature Spec -> Plan -> Implement -> Test -> Docs -> Merge**,
then replan the next feature. Use one chat session per feature, and start it by
reading the complete constitution. Later steps re-read only the relevant
sections and approved feature artifacts.

1. **Spec.** The coordinator does not write the spec itself: dispatch
   `custom-al-implementer` to draft `specs/features/<id>/spec.md` from the
   constitution, the approved design inputs, and the owner's rulings; the
   coordinator supplies the inputs, sets the roadmap item from `todo` to
   `spec`, and reviews the draft, but the artifact is authored by the
   delegated agent. **The drafting dispatch must include the matching gate
   skill** (`.opencode/skills/al-spec-feature/SKILL.md`) **as a drafting
   checklist**, require the drafter to check every design input against
   `brief.md` and `tech-design.md` and surface any constitution conflict as
   an open question in the draft rather than inheriting it, and require a
   self-check against that checklist before the draft is returned (see
   `custom-al-implementer.md`, document-drafting mode). The spec carries: the
   problem, the users, scope, acceptance criteria, what is out of scope, and
   the durable automated-test decision. Then dispatch `al-sdd-reviewer` with
   the spec gate (or run `/al-spec-feature`, which dispatches the same agent)
   to review the spec against the constitution and confirm the acceptance
   criteria are testable.
   Create `approvals.md` from the feature approvals template. Resolve all
   findings per "Resolving gate findings" below and rerun the gate to pass.
   Without changing `spec.md`, run
   the canonical hash helper on `spec.md`, record the pass, reviewer/date, recipe version, and digest in
   `approvals.md`, then stop for human approval. The approver records name/date
   and repeats that same digest. No code yet.
2. **Plan.** After Spec approval, drafted the same way as the spec: dispatch
   `custom-al-implementer` to write `plan.md` and `tasks.md` next to the
   spec; the coordinator sets the roadmap item from `spec` to `planned` and
   supplies the approved spec and design inputs, **the plan gate skill**
   (`.opencode/skills/al-plan-feature/SKILL.md`) **as a drafting checklist**,
   and the drafter self-checks against it before returning. The plan carries:
   the BC objects to add or extend, the object ID range, the data model,
   integration points, and an ordered task list. Then run the plan gate in two
   stages, mechanical first. Dispatch `al-sdd-mechanical-reviewer` with
   `.opencode/skills/al-plan-mechanical/SKILL.md` for the deterministic
   checks: approved Spec digest, object-ID range and freeness, test-policy
   match, task-list shape, and grep-able hard rules. Only on a mechanical
   `pass`, dispatch `al-sdd-reviewer` with the semantic plan gate (or run
   `/al-plan-feature`, which dispatches the same agent) to review the plan
   against the approved spec; that gate recomputes the approved spec digest as
   defense in depth. On any rerun, mechanical first again. Resolve all
   findings per "Resolving gate findings" below and rerun both stages to pass.
   Without changing
   `plan.md` or `tasks.md`, run the canonical hash helper on both paths, record the pass,
   both reviewers/dates, recipe version, and separate digests in `approvals.md`,
   then stop for
   human approval. Only leading task checkbox state outside fenced examples is
   normalized, per the canonical recipe above. The approver records name/date
   and repeats both digests. Move
   `planned` to `in-progress` only after Plan approval. Any later substantive edit invalidates
   the affected evidence and requires the gate, hash, and approval sequence again.
3. **Implement.** Before writing any AL, read the house rules and style guide in
   `.opencode/skills/al-code-review/` (`SKILL.md` plus `styleguide.md`) and let
   them shape the code as you write it, not just at review. Work the tasks in
   order, applying the house rules and citing BCQuality, dispatched to the
   `custom-al-implementer` subagent, which pins GPT-6 Sol high
   while the coordinator stays on the session's default model.
   Write all opted-in test artifacts during Implement, before semantic review
   and compilation; omit them when tests are `no`.
   Then dispatch `al-implement-feature-reviewer` (or run
   `/al-implement-feature`, which dispatches the same agent) to review the
   implementation semantically against its spec, plan, tasks, and acceptance
   criteria. This is a pre-Test conformance gate only: it does not compile,
   duplicate mechanical verifier checks, inspect test results, or require docs,
   roadmap, or PR closeout. Resolve all findings and rerun this same gate to
   `outcome: pass` before entering Test. The `custom-` prefix
   distinguishes the house agents; the prefix is part of the name, so dispatch
   `custom-al-implementer`, not `al-implementer`.
   At the stable implementation checkpoint, the coordinator follows
   `hunk-review` to publish short German explanations of non-obvious changes
   to the matching live diff, including when no defect was found.
4. **Test.** Create or update `validation.md` from the feature validation
   template. Compile the app with analyzers and record the command, result,
   warning count, and baseline classification. A successful Bash-detected build
   triggers the post-build reminder, but the coordinator remains responsible
   for the remaining sequence. When automated tests are `yes`, dispatch
   `al-test-runner` immediately after compile and before test coverage or quality
   validation. Any failed test count, runner failure or partial outcome, or
   required test left unexecuted blocks Test regardless of finding severity.
   Resolve the cause and rerun the tests after every relevant fix until the full
    required selection passes. Then run the applicable mandatory verifier agents
    in parallel and resolve their findings:
    - `al-code-quality-reviewer`
    - `al-readability-checker`
    - `al-test-coverage-validator` (only when tests are opted in)
    - `al-test-validator` (only when tests are opted in)
    When tests are not opted in, the mandatory set is just the first two
     verifiers. Evaluate these specialist triggers independently:
     - `al-integration-pattern-reviewer`: changed actual BC external flows,
       including inbound/outbound flows, Business Events, staging endpoints,
       or Job Queue senders that communicate with external systems.
     - `azure-integration-validator`: changed Azure integration artifacts only.
     - `al-event-subscriber-auditor`: changed subscribers or affected publisher
       signatures only.
    Each verifier owns its own execution of
    `.opencode/BCQuality-ADIGO/tools/route_entry.py` with an exact
    `requested-skill-id`, followed by its routed action's READ/DO flow. Use the
    `python3` fallback when the router is not executable. Never add a generic or
    fuzzy aggregate BCQuality run. Resolve every finding or record a durable,
     explicitly approved waiver with owner and date. One complete finding-free
     pass on unchanged review inputs suffices. Fixes, waivers, or relevant input
     changes require confirmation by the exact applicable verifier set, never
     an opportunistically narrowed subset. Retain the original set and add any
     newly triggered reviewers. Partial or API-failed reviews never pass.
     A casual acknowledgement is
    not resolution. If any Test fix changes production behavior, rerun the
    `al-implement-feature-reviewer` semantic gate, resolve its findings, and rerun
     it to `outcome: pass` before Test closes. Record the initial verifier pass and
     every required rerun in `validation.md`, each semantic rerun separately from the
    initial pre-Test gate's reviewer/date, outcome, and implementation revision.
    The coordinator also publishes actionable verifier findings through
    `hunk-review`, then refreshes this task's notes after fixes. Preserve human
    notes, verify publication, and distinguish unresolved findings from resolved
    explanations. Hunk is a presentation step, not another approval gate.
    For opted-in tests, preserve the runner's BCQuality outcome and
    `summary.execution.status` verbatim. When the app can be published to a
    sandbox, close
    the step by
    offering the developer two verification paths and asking which they want:
    - **A quick manual test recipe** for this change: which page to open, which
      steps to click, and what to expect at each, so they can verify by hand in
      the client in a few minutes.
    - **An autonomous verification run** with `bc-webclient-runner`, which walks
      a documented user guide section by section in a real browser and reports
      structured findings. Its thin agent adapter points to the authoritative
      BCQuality action skill; app environment values come from `APP_CONTEXT.md`.
      The coordinator's obligations when the developer opts in: run it in this
      step, after the mandatory verifiers pass and the app is published to a
      non-production sandbox; give it a user guide (or explicit steps with
      expected outcomes) and absolute paths for any file the flow uploads,
      because without expectations it degrades into screenshots; treat the
      one-time browser sign-in as a human step, so if the agent reports a
      Microsoft login screen, ask for a sign-in rather than entering
      credentials; and classify mismatches rather than assuming the app is
      wrong, since a single wrong caption is usually a guide error while a
      coherent block of them is usually an app defect, confirmed against the
      AL source before reporting a defect.
    Do not run the runner unbidden; it is the developer's call per feature.
    Execute the selected manual recipe or web-client run and record a passing
    result; offering the paths without a result does not close Test.
5. **Docs.** Complete `validation.md`, update end-user or technical documentation
   affected by the change, and move the roadmap item from `in-progress` to
   `done` only after both Test and Docs pass.
6. **Merge.** Review the final diff and closeout state, then create or update the
   PR when requested. The PR references the feature id and summarizes validation.
   Do not treat the pre-Test implementation review as a merge-readiness gate.
   Before final handoff, refresh useful Hunk notes on the current diff and report
   their publication status, or the reason for deferral, per `hunk-review`.

## Resolving gate findings

A complete finding-free first pass is sufficient while review inputs remain
unchanged. Do not repeat clean identical work. Fixes, waivers, or changes to
relevant artifacts, source, policy, or other review inputs require confirmation
by the same applicable gate/verifier set, adding newly triggered reviewers.
For Plan, this means mechanical then semantic again. Partial, unavailable, or
API-failed reviews never count as passes. The bookkeeping exception below
applies only to records that do not alter approval validity or review inputs.

This section governs how the spec and plan gates are rerun. It exists because
a twelve-round spec loop showed three failure modes: the drafter never saw the
gate's checklist, the reviewer deepened its source verification across rounds
instead of front-loading it, and fix applications moved problems rather than
removing them. The rules below attack each mode; they apply to the spec gate,
the plan gate, and the implementation conformance gate alike.

- **One dispatch applies all findings.** The implementing agent receives every
  finding of the failed run in a single dispatch, with the coordinator's
  resolution per finding (owner ruling, mechanical fix, or accepted with
  reason). Never spread one run's findings over several dispatches.
- **Global consistency sweep, not local edits.** For every finding that
  changes a rule, a name, an enumeration, or a routing decision, the applying
  agent must find and update EVERY statement of that rule in the artifact,
  not only the cited line, and must also re-check the statements adjacent to
  each fix for contradictions the fix introduces. The dominant historical
  failure is a pass-1 fix whose residue the next pass finds.
- **Statements-touched list.** The applying agent returns, per finding, the
  confirmation and the list of artifact locations the fix touched. The rerun
  dispatch passes this list to the reviewer so it verifies exactly where a
  moved problem would hide.
- **Decisions are batched, not trickled.** After the first failed run, the
  coordinator extracts every finding that needs an owner ruling or a design
  decision and asks for all of them in one round before dispatching fixes.
  Mechanical fixes proceed without waiting.
- **Round budget and escalation.** Target: the gate reaches `pass` within
  three runs. For the plan gate this budget counts semantic runs; mechanical
  failures are fixed before a semantic run is spent and do not consume it. A
  rerun may find (a) fix residues and (b) new facts from source
  verification the earlier pass had not reached; both are normal. If a run
  fails on neither, stop iterating and diagnose the process with the owner
  instead of dispatching round 4.
- **Accepted findings are recorded, not silently dropped.** A non-blocking
  finding the owner or coordinator declines is written into `approvals.md`
  with the reason at the pass record, so the next reader sees it was
  considered.
- **No unverified design calls or asserted facts from the coordinator.** A
  resolution that changes a design decision — a routing rule, a data-model
  shape, a mechanism, a name the artifact carries — is either verified against
  AL source by the applying agent as part of the fix dispatch, or presented to
  the owner as named options. The coordinator never settles such a finding
  by its own unverified reasoning, because an invented resolution becomes
  the next run's block. The same applies to **facts**: when a resolution rests
  on a fact about the codebase, a standard, or a file inventory, the dispatch
  instructs the agent to derive it from source and cite the evidence, and never
  states it as given. A fact the coordinator asserts in passing ("the
  vocabulary is X", "the only cases are A and B") is the cheapest way to spend
  a gate round, because the gate checks it against source and the drafter does
  not.
- **Trip-wire before every ruling dispatch: is this an amendment?** Before
  dispatching an owner ruling as a findings fix, write one line: *does this
  ruling change a statement in the approved spec, and if so which one?* If it
  does, stop and run the amendment procedure instead; a ruling applied to the
  plan alone, when it changes what the spec says, is found later by a gate and
  costs the whole plan cycle that was built on it. This check is written, not
  assumed.
- **Governance-record findings do not block and do not force a rerun.** A gate
  finding about the feature's own `approvals.md` (run history, Loop State
  freshness, change-log wording) is the coordinator's bookkeeping, not a defect
  in the reviewed artifact. Fix it and continue; do not spend a gate round
  confirming it. The reviewer agents report these separately and never fail on
  them. Two things follow: the run-history entry for the run currently in
  flight cannot exist and its absence is never a finding, and a rerun is owed
   when a fix, waiver, or relevant review input changed. A digest mismatch or a
  missing human approval is not bookkeeping and still blocks.

## Settle the design before writing code

When a request changes behavior that an approved feature already specified, the
expensive mistakes are decisions, not typos. Surface them as explicit questions
first, then write. For a change to stored data the recurring three are: how wide
is the change (everywhere, or only in one branch of the data), what happens to
the schema the old behavior needed, and what happens to rows already written.
Asking costs one round trip. Guessing costs a rewrite and a re-approval.

## Amending approved artifacts

Findings resolution corrects execution detail without changing approved
intent. When approved intent itself turns out to be wrong or superseded, that
is an amendment. Artifacts are **current-only**: a spec, plan, or tasks file
never carries appended amendment sections or superseded text, because every
later reader, gate, and subagent pays for stale statements. The past lives in
git history and in the feature's `approvals.md` change log.

Triggers: an owner decision, or a Test, verifier, or gate finding that reveals
the approved spec or plan is wrong rather than the implementation drifting
from it. If a fix would change what the spec says, it is an amendment, not a
fix.

Procedure, in order:

1. The owner rules the change in one batched round, as with gate findings.
2. Dispatch `custom-al-implementer` in document-drafting mode to rewrite the
   artifact in place and delete the superseded content. The dispatch names the
   governing gate skill as the drafting checklist.
3. Append a change-log entry to `approvals.md`: decision owner and date, what
   changed, why, what was rejected, and any accepted loss. This entry is the
   durable reasoning; the superseded text is not.
4. Rerun the affected gate or gates to `pass`, mechanical stage first for the
   plan gate. A spec amendment re-opens the Spec gate; a plan amendment
   re-opens the plan gate. If the amendment invalidates later stages, say so
   explicitly rather than letting them stand silently.
5. Recompute canonical digests, record new review evidence while retaining the
   prior approval history in `approvals.md`, and stop for human re-approval.
   Never automatically replace an existing human approval. A changed spec or plan is a
   hard stop again; prior approval does not survive a digest change.
6. Update the roadmap status only if the amendment regresses the stage.

The same rule applies to features already marked `done`: rewrite in place,
delete superseded text, and record the change in the change log. Git history
preserves the old version; no artifact carries it forward.

## Dispatch contracts

Every dispatch to a subagent uses one of the standard contracts below. The
core rule: **pass paths and digests, never paste file contents.** Subagents
read from disk; the coordinator's context carries decisions, not documents.
Batch inputs; a dispatch that trickles information guarantees a second run.
Every verifier dispatch includes: navigate AL with Serena first, use
workspace-relative paths (including app prefixes), convert Serena's 0-based
locations to 1-based report lines, and receive paths rather than file contents.
Digest reviewers must freshly execute the canonical helper themselves against
current files. Missing execution means partial/block, never a recorded-only pass.

- **Draft dispatch** (spec, plan, or tasks): feature id; artifact path to
  write; the design inputs as paths (`APP_CONTEXT.md`, constitution files,
  approved spec) plus the owner's rulings and resolved open questions verbatim
  in the prompt; the governing gate skill path as a drafting checklist. The
  return contract: the written file, one line per checklist item confirming it
  was checked, the design-input overrides list, and remaining open questions.
- **Gate dispatch**: feature id and the gate name. The agent derives its own
  inputs per its skill. The return contract: the gate's structured findings
  report and nothing else.
  `/al-plan-feature` runs inside the semantic reviewer and cannot dispatch the
  mechanical reviewer. Without current mechanical pass evidence it returns
  `mechanical-prerequisite-required`; the coordinator runs mechanical first,
  then semantic. The human Spec and Plan approval hard stops still apply.
- **Findings-fix dispatch**: feature id; artifact path; every finding of the
  failed run with the coordinator's resolution per finding (owner ruling,
  mechanical fix, or accepted with reason). The return contract: per finding,
  the confirmation plus the statements-touched list.
- **Implement dispatch**: feature id and the tasks in scope. The agent already
  carries the house rules and style guide. The return contract: per task, what
  was done with 1-based `file:line` references, then an open-questions list.
  No pasted diffs or file contents.

The coordinator reads return reports, never subagent transcripts. When a
return would be large (an open-ended exploration, a long log), the dispatch
directs a write-capable subagent to write it to a file outside the workspace and
return the path plus a short summary. Read-only gate reviewers return their
report directly; external evidence access does not grant write permission.

## Testing policy (tests are opt-in)

Automated tests are **not** written without an explicit `yes`. This is an
execution default, not permission to infer `no`: an absent decision is a hard
question for the developer. Every feature spec
and plan must record `Automated tests: yes | no`, the decision owner/date, and
the reason. The plan must match the approved spec. If the decision is absent,
the agent must ask the developer and update both artifacts before proceeding.
Chat history alone is not a durable testing decision.

- If the developer says **no**: skip all test
  writing. A missing test is **not** a finding. `al-test-writer`,
  `al-userguide-test-writer`, `al-test-coverage-validator/-enforcer`,
  `al-test-validator`, and `al-test-runner` are not run. The plan states that no
  automated test artifacts or test verifiers apply, and test tasks are removed.
- If the developer says **yes**: the full test discipline applies. Every
  acceptance criterion gets a covering test. After compile, `al-test-runner`
  executes every required test before coverage and test-quality validation. A
  zero-failure result is insufficient if the runner is partial or any required
  test was not executed. Tests rerun after fixes, and the test verifiers run in
  the initial applicable verifier pass and every required confirmation pass.

This is a house rule and, per "When sources conflict, house rules win," it
overrides any "test per acceptance criterion" or "missing test is a
blocker/major" wording elsewhere in the workflow skills or templates.

## Deployment and compatibility policy

The explicit `Production/persisted-data compatibility required: yes | no` field
in local `APP_CONTEXT.md` is the authority. Deployment status and release tags
are evidence, not overrides. A tag alone never changes `no` to `yes`.

When compatibility is `no`, **schema changes are free**. Treat a breaking schema
change as a normal edit, not as an event that needs a migration path.

- Remove a field, table, enum value, or procedure outright when it is no longer
  needed. Do **not** mark it `ObsoleteState = Pending` first, and do not carry
  `ObsoleteReason` or `ObsoleteTag` for the sake of process.
- Do **not** write an upgrade codeunit for existing data. Rows written by an
  earlier version may be left stale, unreadable, or orphaned. Re-import or
  re-create the data instead.
- A missing obsolete marking and a missing upgrade path are **not** findings.
  `al-obsolete-tracker` and `al-upgrade-checker` are not part of any mandatory
  set. If one is run anyway, downgrade its migration findings to info.
- Do still **record** the breaking change in the feature plan: what breaks, what
  a consumer must do, and why it was taken. The reasoning is the durable part,
  the migration code is not.

When compatibility is `yes`, `APP_CONTEXT.md` must provide a trusted released
baseline ref. Plan and specialist compatibility adapters compare against that
baseline. If it is missing or unavailable, return a partial compatibility result
instead of guessing. This is an app-local house boundary; it does not modify the
portable BCQuality action contract.

## Bootstrapping

At the start of a project (or when the high-level requirements change), draft
`specs/brief.md`, `specs/tech-design.md`, and `specs/roadmap.md`, then run `/al-spec-init` once
(dispatches `al-sdd-reviewer` with the constitution gate) to review the
constitution for completeness and consistency before any feature work.
