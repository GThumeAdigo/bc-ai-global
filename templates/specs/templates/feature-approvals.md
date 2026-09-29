# Feature Approvals: <feature name>

- **Feature id:** <NNN-slug>

## Loop State

The coordinator updates this section at every stage transition and after every
gate run. A fresh or compacted session reads it plus `specs/roadmap.md` to
resume; do not reconstruct state from chat history.

- **Stage:** <spec | plan | implement | test | docs | merge>
- **Spec gate:** <not-run | fail | partial | pass> (<YYYY-MM-DD>)
- **Plan mechanical gate:** <not-run | fail | partial | pass> (<YYYY-MM-DD>)
- **Plan semantic gate:** <not-run | fail | partial | pass> (<YYYY-MM-DD>)
- **Implementation review:** <not-run | fail | partial | pass> (<YYYY-MM-DD>)
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
- **Canonical tasks.md SHA-256:** <64 lowercase hexadecimal characters; leading checkbox state normalized outside fences>
- **Plan and tasks approved by/date:** <human approver, YYYY-MM-DD>
- **Approved plan.md SHA-256:** <same plan digest as the review>
- **Approved tasks.md SHA-256:** <same tasks digest as the review>

## Hash Workflow

Run the applicable gate until it returns `outcome: pass` (for the plan gate:
both the mechanical and the semantic stage), without requiring that gate's own
approval fields. One complete finding-free pass on unchanged inputs suffices;
fixes, waivers, or relevant input changes require confirmation by the same
applicable set. Partial/API-failed reviews never pass. From the repository root,
freshly execute the canonical helper against the reviewed current files:

```bash
python3 .opencode/skills/sdd/scripts/artifact_hash.py specs/features/<id>/spec.md
python3 .opencode/skills/sdd/scripts/artifact_hash.py specs/features/<id>/plan.md specs/features/<id>/tasks.md
```

Recipe: **sdd-artifact-v1**, defined in `.opencode/skills/sdd/SKILL.md`. Spec and
plan are raw bytes; only leading task checkbox state outside fenced examples
is normalized for `tasks.md`. Inline literals and all other bytes, including
line endings, remain substantive. Use the absolute helper path if needed.

- **Digest recipe version:** <sdd-artifact-v1>
- **Fresh execution evidence per reviewer:** <command, artifact paths, output, date>

Record the passing reviews, reviewers/dates, and digest or digests here. The
human approver records their name/date and repeats the same digest values.
Before the next stage, each digest reviewer freshly executes the helper and
requires an exact match. Missing execution is partial/block, not pass;
recorded-only agreement is insufficient. Substantive edits invalidate the
affected review and approval; leading checkbox-only progress outside fences
does not. For legacy mismatches or changed inputs, retain prior evidence,
explicitly revalidate through the affected gates, recalculate canonical
digests, and stop for human re-approval. Never automatically overwrite or
reapprove existing approvals.

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
