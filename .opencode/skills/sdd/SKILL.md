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
  matching approved full `plan.md` and `tasks.md` SHA-256 values, or enter Test
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

## The constitution (initial read, every feature)

- `APP_CONTEXT.md`: local app identity, conventions, dependencies, and
  environment-specific verification facts.
- `specs/brief.md`: customer requirements and business processes (the what and why).
- `specs/tech-design.md`: implementation strategy: which standard BC modules to
  reuse, and where custom code is genuinely needed.
- `specs/roadmap.md`: ordered list of features with status.
- `AGENTS.md`: conventions, quality gates, and the model policy.

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
   `sha256sum spec.md`, record the pass, reviewer/date, and full-file digest in
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
   `plan.md` or `tasks.md`, run `sha256sum plan.md tasks.md`, record the pass,
   both reviewers/dates, and separate full-file digests in `approvals.md`,
   then stop for
   human approval. The approver records name/date and repeats both digests. Move
   `planned` to `in-progress` only after Plan approval. Any later edit invalidates
   the affected evidence and requires the gate, hash, and approval sequence again.
3. **Implement.** Before writing any AL, read the house rules and style guide in
   `.opencode/skills/al-code-review/` (`SKILL.md` plus `styleguide.md`) and let
   them shape the code as you write it, not just at review. Work the tasks in
   order, applying the house rules and citing BCQuality, dispatched to the
   `custom-al-implementer` subagent, which pins a cheaper implementation model
   (Sonnet 5) while the coordinator stays on the session's default model.
   Then dispatch `al-implement-feature-reviewer` (or run
   `/al-implement-feature`, which dispatches the same agent) to review the
   implementation semantically against its spec, plan, tasks, and acceptance
   criteria. This is a pre-Test conformance gate only: it does not compile,
   duplicate mechanical verifier checks, inspect test results, or require docs,
   roadmap, or PR closeout. Resolve all findings and rerun this same gate to
   `outcome: pass` before entering Test. The `custom-` prefix
   distinguishes the house agents; the prefix is part of the name, so dispatch
   `custom-al-implementer`, not `al-implementer`.
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
   (see AGENTS.md) in parallel, including the integration trio when applicable.
   Each verifier owns its own execution of
   `.opencode/BCQuality-ADIGO/tools/route_entry.py` with an exact
   `requested-skill-id`, followed by its routed action's READ/DO flow. Use the
   `python3` fallback when the router is not executable. Never add a generic or
   fuzzy aggregate BCQuality run. Resolve every finding or record a durable,
   explicitly approved waiver with owner and date, then rerun the exact same
   applicable verifier set to confirm resolution. A casual acknowledgement is
   not resolution. If any Test fix changes production behavior, rerun the Opus
   `al-implement-feature-reviewer` semantic gate, resolve its findings, and rerun
   it to `outcome: pass` before Test closes. Record both verifier runs and every
   rerun in `validation.md`. When the app can be published to a sandbox, close
   the step by
   offering the developer two verification paths and asking which they want:
   - **A quick manual test recipe** for this change: which page to open, which
     steps to click, and what to expect at each, so they can verify by hand in
     the client in a few minutes.
   - **An autonomous verification run** with `bc-webclient-runner`, which walks
     a documented user guide section by section in a real browser and reports
     structured findings. Its thin agent adapter points to the authoritative
     BCQuality action skill; app environment values come from `APP_CONTEXT.md`.
   Do not run the runner unbidden; it is the developer's call per feature.
   Execute the selected manual recipe or web-client run and record a passing
   result; offering the paths without a result does not close Test.
5. **Docs.** Complete `validation.md`, update end-user or technical documentation
   affected by the change, and move the roadmap item from `in-progress` to
   `done` only after both Test and Docs pass.
6. **Merge.** Review the final diff and closeout state, then create or update the
   PR when requested. The PR references the feature id and summarizes validation.
   Do not treat the pre-Test implementation review as a merge-readiness gate.

## Resolving gate findings

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
- **No unverified design calls from the coordinator.** A resolution that
  changes a design decision — a routing rule, a data-model shape, a
  mechanism, a name the artifact carries — is either verified against AL
  source by the applying agent as part of the fix dispatch, or presented to
  the owner as named options. The coordinator never settles such a finding
  by its own unverified reasoning, because an invented resolution becomes
  the next run's block.

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
5. Recompute the full-file digests, replace the affected approval evidence in
   `approvals.md`, and stop for human re-approval. A changed spec or plan is a
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

- **Draft dispatch** (spec, plan, or tasks): feature id; artifact path to
  write; the design inputs as paths (`APP_CONTEXT.md`, constitution files,
  approved spec) plus the owner's rulings and resolved open questions verbatim
  in the prompt; the governing gate skill path as a drafting checklist. The
  return contract: the written file, one line per checklist item confirming it
  was checked, the design-input overrides list, and remaining open questions.
- **Gate dispatch**: feature id and the gate name. The agent derives its own
  inputs per its skill. The return contract: the gate's structured findings
  report and nothing else.
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
directs the subagent to write it to a file outside the workspace and return
the path plus a short summary.

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
  both mandatory verifier passes.

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
