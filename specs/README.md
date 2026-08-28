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
      approvals.md  # digest-bound Spec and Plan review/approval evidence
      validation.md # compile, tests, two verifier runs, client result, Test outcome
```

## Workflow (Spec-Driven Development)

At each stage you draft the artifact, with the agent's help, then run the
matching skill as a review gate before moving on:

1. `/sdd spec`: drafts the spec, then `/al-spec-feature` reviews it. Resolve findings and rerun to pass. Hash the unchanged full `spec.md`; record review and human approval against that same digest in `approvals.md`.
2. `/sdd plan`: first validates the approved Spec digest, then drafts and reviews the plan and tasks. Resolve findings and rerun to pass. Hash unchanged full `plan.md` and `tasks.md` separately; record review and human approval against those same digests in `approvals.md`.
3. `/sdd implement`: implements approved work, then `/al-implement-feature` reviews semantic conformance. Resolve findings and rerun to pass before Test.
4. Test: record compile/baseline evidence in `validation.md`; when opted in, execute tests before coverage/quality validation; run the applicable verifier set twice; rerun semantic conformance after production fixes; and record a passing manual or web-client result.
5. Docs and Merge: complete validation and documentation, move the roadmap item to done, then prepare the PR when requested.

The `/al-*` commands are review-only gates. Use `/sdd spec|plan|implement` to
perform workflow stages. Copy `templates/feature-approvals.md` to each feature as
`approvals.md`, and copy `templates/feature-validation.md` as `validation.md`
when Test starts. Use `sha256sum spec.md` and `sha256sum plan.md tasks.md` from
the feature folder. Any edit after hashing invalidates the affected approval.

Roadmap transitions are `todo -> spec` on Spec draft, `spec -> planned` on Plan
draft, `planned -> in-progress` after Plan approval, and `in-progress -> done`
after Test and Docs pass.

One feature, one chat session. Always start by reading the constitution.

## Feature folder naming

`NNN-short-slug`, zero-padded and ordered (for example `001-first-feature`,
`002-overdue-notifications`). The number matches the roadmap order.
