---
name: sdd
kind: workflow-skill
id: sdd
version: 1
title: Spec-Driven Development workflow
description: The house Spec-Driven Development workflow for AL features, the constitution, the per-feature loop (Spec, Plan, Implement, Test, Docs, Merge), the testing policy (opt-in), and the deployment policy (schema changes free). Use when starting, continuing, or reviewing feature work, when asked to run a feature through the SDD loop, and before writing any production AL for a feature. Do not load for quick fixes that are not feature work.
inputs: [feature-id, feature-path]
outputs: [spec, plan, tasks, validation, implementation]
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
- One chat session per feature. Start the session by reading the constitution
  below, then this skill stays loaded while the loop runs.
- Not every task is a feature. Bug fixes, tweaks, and questions do not need
  this skill; do not create spec artifacts for them.

## Keep the main session small

The main session coordinates; subagents do the work.

- **Run all tasks in subagents.** Implementation goes to `custom-al-implementer`,
  the document review gates (spec, plan, constitution) to `al-sdd-reviewer`,
  the implementation review gate to `al-implement-feature-reviewer`, other
  reviews to the verifier agents, open-ended exploration to a general subagent
  instructed to navigate AL with Serena (see AGENTS.md). The main session
  dispatches and reports; it does not read source files wholesale or run long
  tool output itself. Each gate agent reads and follows its skill in
  `.opencode/skills/`, which defers to BCQuality; the agent frontmatter owns
  the model pin, so change models there, not in the commands.
- **Reuse the house agents and skills where handy** instead of improvising:
  the review gates (`/al-spec-feature`, `/al-plan-feature`,
  `/al-implement-feature`, which dispatch the reviewer subagents), the
  mandatory verifier set, `al-compile`, and the house rules in
  `al-code-review` all exist for this loop.
- **Approval gates are hard stops.** After the spec review and after the plan
  review, the loop waits for the developer's explicit approval. Never dispatch
  the implementer before the plan is approved, and never draft the next step's
  artifacts while an earlier gate is still open.
- **Be precise and efficient in conversation.** One topic per message, short
  questions, short answers, findings with `file:line` references instead of
  prose. Batch clarifying questions into one round trip rather than trickling
  them. The conversation history is resent on every turn, so a session that
  wanders pays for the wandering all feature long.

## The constitution (read first, every feature)

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
reading the constitution.

1. **Spec.** Draft `specs/features/<id>/spec.md`: the problem, the users, scope,
   acceptance criteria, what is out of scope, and the durable automated-test
   decision. Then dispatch `al-sdd-reviewer` with the spec gate (or run
   `/al-spec-feature`, which dispatches the same agent) to review the spec
   against the constitution and confirm the acceptance criteria are testable.
   Stop for human review. No code yet.
2. **Plan.** Draft `plan.md` and `tasks.md` next to the spec: the BC objects to
   add or extend, the object ID range, the data model, integration points, and an
   ordered task list. Then dispatch `al-sdd-reviewer` with the plan gate (or
   run `/al-plan-feature`, which dispatches the same agent) to review them
   against the approved spec. Stop for human review.
3. **Implement.** Before writing any AL, read the house rules and style guide in
   `.opencode/skills/al-code-review/` (`SKILL.md` plus `styleguide.md`) and let
   them shape the code as you write it, not just at review. Work the tasks in
   order, applying the house rules and citing BCQuality, dispatched to the
   `custom-al-implementer` subagent, which pins a cheaper implementation model
   (Sonnet 5) while the coordinator stays on the session's default model.
   Then dispatch `al-implement-feature-reviewer` (or run
   `/al-implement-feature`, which dispatches the same agent) to review the
   implementation against its spec, plan, and tasks. The `custom-` prefix
   distinguishes the house agents; the prefix is part of the name, so dispatch
   `custom-al-implementer`, not `al-implementer`.
4. **Test.** Building the app triggers the post-build hook, which prompts the
   mandatory verifier agents (see the mandatory verifier set in AGENTS.md) and a
   BCQuality review. Resolve every finding. Whether automated tests are written
   is governed by the **Testing policy** below and recorded in the feature spec
   and plan. When the app can be published to a sandbox, close the step by
   offering the developer two verification paths and asking which they want:
   - **A quick manual test recipe** for this change: which page to open, which
     steps to click, and what to expect at each, so they can verify by hand in
     the client in a few minutes.
   - **An autonomous verification run** with `bc-webclient-runner`, which walks
     a documented user guide section by section in a real browser and reports
     structured findings. The runner agent's own definition carries the
     operational detail (inputs, environment, JSON shape).
   Do not run the runner unbidden; it is the developer's call per feature.
5. **Docs and Merge.** Update the feature docs, tick the roadmap item, open a PR.

## Testing policy (tests are opt-in)

Automated tests are **not** written by default. Every feature spec
and plan must record `Automated tests: yes | no`, the decision owner/date, and
the reason. The plan must match the approved spec. If the decision is absent,
the agent must ask the developer and update both artifacts before proceeding.
Chat history alone is not a durable testing decision.

- If the developer says **no** (the default when unstated): skip all test
  writing. A missing test is **not** a finding. `al-test-writer`,
  `al-userguide-test-writer`, `al-test-coverage-validator/-enforcer`,
  `al-test-validator`, and `al-test-runner` are not run. The plan states that no
  automated test artifacts or test verifiers apply, and test tasks are removed.
- If the developer says **yes**: the full test discipline applies. Every
  acceptance criterion gets a covering test, and the test verifiers run as part
  of the mandatory set.

This is a house rule and, per "When sources conflict, house rules win," it
overrides any "test per acceptance criterion" or "missing test is a
blocker/major" wording elsewhere in the workflow skills or templates.

## Deployment policy (nothing is in production yet)

Unless the local `APP_CONTEXT.md` says an app is installed in a production tenant,
**schema changes are free**. Treat a breaking schema change as a normal edit, not
as an event that needs a migration path.

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

This is a house rule and it overrides any obsolete-discipline or
upgrade-safety wording in the agents, skills, or BCQuality `upgrade` domain.
Revisit it the moment the first app ships to a production tenant, because every
bullet above inverts at that point.

## Bootstrapping

At the start of a project (or when the high-level requirements change), draft
`brief.md`, `tech-design.md`, and `roadmap.md`, then run `/al-spec-init` once
(dispatches `al-sdd-reviewer` with the constitution gate) to review the
constitution for completeness and consistency before any feature work.
