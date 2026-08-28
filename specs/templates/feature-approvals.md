# Feature Approvals: <feature name>

- **Feature id:** <NNN-slug>

## Spec

- **Spec review outcome:** pass
- **Spec reviewed by/date:** <reviewer, YYYY-MM-DD>
- **Full spec.md SHA-256:** <64 lowercase hexadecimal characters>
- **Spec approved by/date:** <human approver, YYYY-MM-DD>
- **Approved spec.md SHA-256:** <same digest as the reviewed spec>

## Plan And Tasks

- **Plan review outcome:** pass
- **Plan reviewed by/date:** <reviewer, YYYY-MM-DD>
- **Full plan.md SHA-256:** <64 lowercase hexadecimal characters>
- **Full tasks.md SHA-256:** <64 lowercase hexadecimal characters>
- **Plan and tasks approved by/date:** <human approver, YYYY-MM-DD>
- **Approved plan.md SHA-256:** <same plan digest as the review>
- **Approved tasks.md SHA-256:** <same tasks digest as the review>

## Hash Workflow

Run the applicable gate until it returns `outcome: pass`, without requiring that
gate's own approval fields. Do not edit the reviewed files after that passing
run. From the feature folder, calculate full-file digests:

```bash
sha256sum spec.md
sha256sum plan.md tasks.md
```

Record the passing review, reviewer/date, and digest or digests here. The human
approver records their name/date and repeats the same digest values. Before the
next stage, recompute each digest and require an exact match. Any edit to a
reviewed file invalidates its review and approval: rerun the relevant gate,
recalculate the digest or digests, and replace that section's evidence.
