# Feature Approvals: <feature name>

- **Feature id:** <NNN-slug>

## Loop State

The coordinator updates this section at every stage transition and after every
gate run. A fresh or compacted session reads it plus `specs/roadmap.md` to
resume; do not reconstruct state from chat history.

- **Stage:** <spec | plan | implement | test | docs | merge>
- **Spec gate:** <not-run | fail | pass> (<YYYY-MM-DD>)
- **Plan mechanical gate:** <not-run | fail | pass> (<YYYY-MM-DD>)
- **Plan semantic gate:** <not-run | fail | pass> (<YYYY-MM-DD>)
- **Implementation review:** <not-run | fail | pass> (<YYYY-MM-DD>)
- **Approved digests:** <artifact: digest, or "none">
- **Pending owner decisions:** <none | list>

## Spec

- **Spec review outcome:** pass
- **Spec reviewed by/date:** <reviewer, YYYY-MM-DD>
- **Full spec.md SHA-256:** <64 lowercase hexadecimal characters>
- **Spec approved by/date:** <human approver, YYYY-MM-DD>
- **Approved spec.md SHA-256:** <same digest as the reviewed spec>

## Plan And Tasks

- **Plan mechanical review outcome:** pass
- **Plan mechanical reviewed by/date:** <reviewer, YYYY-MM-DD>
- **Plan review outcome:** pass
- **Plan reviewed by/date:** <reviewer, YYYY-MM-DD>
- **Full plan.md SHA-256:** <64 lowercase hexadecimal characters>
- **Full tasks.md SHA-256:** <64 lowercase hexadecimal characters>
- **Plan and tasks approved by/date:** <human approver, YYYY-MM-DD>
- **Approved plan.md SHA-256:** <same plan digest as the review>
- **Approved tasks.md SHA-256:** <same tasks digest as the review>

## Hash Workflow

Run the applicable gate until it returns `outcome: pass` (for the plan gate:
both the mechanical and the semantic stage), without requiring that gate's own
approval fields. Do not edit the reviewed files after that passing run. From
the feature folder, calculate full-file digests:

```bash
sha256sum spec.md
sha256sum plan.md tasks.md
```

Record the passing reviews, reviewers/dates, and digest or digests here. The
human approver records their name/date and repeats the same digest values.
Before the next stage, recompute each digest and require an exact match. Any
edit to a reviewed file invalidates its review and approval: rerun the
relevant gate, recalculate the digest or digests, and replace that section's
evidence.

## Change Log

One entry per amendment to an approved artifact. Artifacts are rewritten in
place and superseded text is deleted, not appended; this log carries the
durable reasoning. An amendment also requires rerunning the affected gate,
recomputing digests, and human re-approval.

- **<YYYY-MM-DD> - <owner> - <artifact>:** what changed, why, what was
  rejected, and any accepted loss.

## Accepted Findings

A non-blocking finding the owner or coordinator declines is recorded here with
the reason at the pass record, so the next reader sees it was considered.

- **<gate, run date> - <finding rule>:** <reason it was declined>.
