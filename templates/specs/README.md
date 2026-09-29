# specs/

This folder is the source of truth for **what** the solution does. Code is the
muscle; these specs are the brain. See `AGENTS.md` at the repo root for the full
contract.

## Layout

```
specs/
  brief.md          # constitution: customer requirements (the what and why)
  tech-design.md    # constitution: reuse standard BC, name the custom-code gaps
  roadmap.md        # constitution: ordered features with status
  templates/        # blank templates for each per-feature artifact
  features/
    <NNN-slug>/     # one folder per feature, e.g. 001-first-feature
      spec.md       # requirements, scope, acceptance criteria
      plan.md       # technical plan: objects/structure, ID range, data model
      tasks.md      # ordered, checkable implementation tasks
      approvals.md  # loop state, digest-bound review/approval evidence,
                    # change log, accepted findings
      validation.md # compile, tests, verifier pass and required reruns, client result, Test outcome
```

## Workflow (Spec-Driven Development)

At each stage you draft the artifact, with the agent's help, then run the
matching skill as a review gate before moving on:

1. `/sdd spec`: drafts the spec, then `/al-spec-feature` reviews it. Resolve findings and rerun to pass. Hash the unchanged full `spec.md`; record review and human approval against that same digest in `approvals.md`.
2. `/sdd plan`: first validates the approved Spec digest, then drafts and reviews the plan and tasks. The plan gate runs in two stages: `al-plan-mechanical` (deterministic: digests, object IDs, test-policy match, task-list shape) before `al-plan-feature` (semantic, GPT-6 Sol high). Resolve findings and rerun to pass. Hash unchanged `plan.md` and `tasks.md` separately with the canonical helper; record review and human approval against those same digests in `approvals.md`.
3. `/sdd implement`: implements approved work, including opted-in test artifacts before semantic review and compilation, then `/al-implement-feature` reviews semantic conformance. Resolve findings and rerun to pass before Test.
4. Test: record compile/baseline evidence in `validation.md`; when opted in, execute tests before coverage/quality validation; run the applicable verifier set; rerun semantic conformance after production fixes; and record a passing manual or web-client result. One complete finding-free pass on unchanged inputs suffices. Fixes, waivers, or relevant input changes require confirmation by the exact applicable set, adding new triggers and never narrowing reruns. Partial/API-failed reviews never pass.
5. Docs and Merge: complete validation and documentation, move the roadmap item to done, then prepare the PR when requested.

The `/al-*` commands are review-only gates. Use `/sdd spec|plan|implement` to
perform workflow stages. Copy `templates/feature-approvals.md` to each feature as
`approvals.md`, and copy `templates/feature-validation.md` as `validation.md`
when Test starts. From the repository root, use only:

```bash
python3 .opencode/skills/sdd/scripts/artifact_hash.py specs/features/<id>/spec.md
python3 .opencode/skills/sdd/scripts/artifact_hash.py specs/features/<id>/plan.md specs/features/<id>/tasks.md
```

The sdd-artifact-v1 recipe in `.opencode/skills/sdd/SKILL.md` hashes spec/plan
raw and normalizes only leading task checkbox state outside fenced examples in
`tasks.md`, preserving inline literals and other bytes and line endings. Every
digest reviewer must freshly execute it; missing execution is partial/block,
never a recorded-only pass. Substantive edits invalidate affected approvals;
checkbox-only progress does not. Legacy mismatches require explicit revalidation
and human re-approval while retaining prior evidence, never automatic overwrite.

Without a current mechanical pass, `/al-plan-feature` returns
`mechanical-prerequisite-required` to the coordinator, which runs mechanical
then semantic. The reviewer cannot dispatch the mechanical agent itself.

Evaluate specialist triggers independently: integration-pattern review for
changed actual BC external flows, Azure validation only for changed Azure
integration artifacts, and subscriber audit only for changed subscribers or
affected publisher signatures. Pass paths, not contents, in verifier dispatches;
require Serena-first AL navigation, workspace-relative paths, and conversion of
0-based Serena locations to 1-based report lines.

Specs, plans, and task lists are current-only. A change to approved intent is
an amendment: rewrite the artifact in place, delete the superseded text,
record what changed and why in the `approvals.md` change log, rerun the
affected gate, recompute the digests, and stop for human re-approval. Nothing
superseded is ever appended to an artifact; git history and the change log
carry the past.

Keep the `Loop State` section of `approvals.md` updated at every stage
transition. A fresh or compacted session resumes from it and the roadmap, not
from chat history.

Roadmap transitions are `todo -> spec` on Spec draft, `spec -> planned` on Plan
draft, `planned -> in-progress` after Plan approval, and `in-progress -> done`
after Test and Docs pass.

One feature, one chat session. Always start by reading the constitution.

## Feature folder naming

`NNN-short-slug`, zero-padded and ordered (for example `001-first-feature`,
`002-overdue-notifications`). The number matches the roadmap order.
