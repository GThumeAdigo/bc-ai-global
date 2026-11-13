# Knowledge base

What the app does today, as rules and reasons. Not a history (delivered feature folders move to `../archive/`),
not an object catalogue (source and Serena answer that). Private like `specs/`.

## Page contract

One topic per file, at most 4 KB (hard cap 6 KB). Rewrite in place when behavior
changes; never append dated amendments. Frontmatter:

```
---
topic: <slug, equals the file name>
read-when: <one line: tasks that need this page>
verified-at: <app git commit the rules were checked against>
sources: [<feature ids the content came from>]
---
```

Sections, omit an empty one:

1. `# <Title>` and two or three lines of purpose.
2. `## Behavior` how it works now, in plain prose or a short list.
3. `## Rules` numbered with a stable id (`IMP-1`). Each: the rule, why it exists,
   what breaks if violated. Rules must be checkable against source.
4. `## Decisions` decision, reason, rejected alternative.
5. `## Touchpoints` object and procedure names (no IDs, no field lists) a change
   would touch.
6. `## Limits and pitfalls` known gaps, traps, unverified areas.

## Do not include

Acceptance criteria, task lists, verification logs, owner dialogue, dates of
rulings, object IDs, field-by-field inventories, anything derivable from source.
Every claim must be verified against the current source; mark the rest
"unverified" under Limits.

`index.md` lists every page with its `read-when` line. Load the index first, then
only the pages the task needs.
