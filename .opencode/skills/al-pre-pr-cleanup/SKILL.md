---
name: al-pre-pr-cleanup
kind: action-skill
id: al-pre-pr-cleanup
version: 1
title: AL pre-PR comment and process-reference cleanup
description: Trims over-long XML doc comments and strips Spec-Driven Development process references (feature numbers, spec.md/plan.md/tasks.md/validation.md, roadmap, AC and task ids) out of production AL before a pull request. Use when preparing a branch for PR, cleaning up comments, or when asked to make summaries precise.
inputs: [pr-diff, file-path]
outputs: [findings-report, edits]
bc-version: [all]
technologies: [al]
countries: [w1]
application-area: [all]
---

# AL pre-PR cleanup

The work in this repo is spec-driven, and the specs are git-excluded. Both facts
leak into the AL: doc comments grow into essays because the reasoning was fresh
in a chat session, and they pick up references to feature numbers and spec files
a PR reviewer cannot open. This skill removes both, without losing anything that
was actually load-bearing.

## When to use

Before opening a PR. Also whenever the developer asks to clean up, shorten, or
make comments precise, or asks whether plans and feature numbers leaked into the
code.

## When not to use

This is an editorial pass over comments. It does not change behavior. If a
finding needs an AL statement to move, that is a separate task: report it and
stop.

## Scope the pass first

Work from the branch diff, not the whole app.

```
git diff --stat main...HEAD
git diff --name-only main...HEAD -- '*.al'
```

When the developer names specific objects instead, use those and say so in the
report. In a multi-app workspace, resolve each app folder from its own
`app.json` and keep the report per app.

## Pass 1: comment length

The target is precision, not brevity for its own sake. One or two sentences is
usually enough. More is fine when the thing is genuinely hard, and a public
integration contract is the clearest case where more is warranted.

**Cut on sight:**

- A sentence repeated on every procedure of a codeunit. If five procedures all
  say "the announced state is committed before the event is raised", it belongs
  in the codeunit summary once, or nowhere.
- A guard described on the wrong object. A publisher does not document its
  caller's transition rules; the caller does.
- An inventory of call sites, dependants, or affected callers. It is stale the
  day someone adds a caller. State the constraint ("this commit must not be
  removed without giving each caller their own") and drop the list.
- Narration of what the next statement does.
- Restated parameter docs. `<param>` already covers it.
- A rejected alternative, a decision history, or a "we chose X over Y". That is
  spec material.

**Keep:**

- What the procedure does, in the caller's terms.
- A constraint a caller can violate: cannot be called from a TryFunction, must
  be idempotent, must not write to X from this handler, call Y and commit first.
- A platform behavior that is not inferable from the signature, with its Learn
  link where one exists.
- A named hazard with a consequence, compressed to one sentence.

**Before deleting reasoning, check it survives somewhere.** The house rule is
that rationale lives in the feature `plan.md` or `validation.md`. Confirm it
does, do not assume:

```
grep -rln "<the identifier or mechanism>" specs/features/*/
```

If the reasoning exists only in the comment, move it into the relevant feature's
plan or validation file first, then trim the comment. Say in the report where it
landed. Never delete a rationale that exists nowhere else.

## Pass 2: process references

Production code and shipped docs must not reference the SDD artifacts. The specs
are git-excluded, so every one of these is a dangling pointer for a reviewer.

```
grep -rnIE "feature [0-9]|features/|spec\.md|plan\.md|tasks\.md|validation\.md|roadmap|specs/|tech-design|\bAC[0-9]" \
  --include='*.al' --include='*.json' --include='*.xlf' --include='*.md' <app-folder>
```

Rewrite each hit to state the fact without the citation:

| Before | After |
|---|---|
| `which feature 013 refused` | `which is why it is not done` |
| `because feature 022 made a source entry the identity of one typed row` | `because a source entry is the identity of one typed row` |
| `where feature 007 walks down` | `where the bill-of-quantities tree walks down` |
| `feature 023 plan.md D2 and D4 hold the reasoning` | (delete the clause) |
| `the ID window declared in specs/tech-design.md` | `the typed-table ID window` |
| `validation.md records their shared md5` | `compare their md5` |

**False positives to leave alone.** `feature` is an ordinary domain word:
"the specified feature of the project line" is not necessarily a spec
reference. `AC0017`, `AC0032` and friends are AppSourceCop rule ids inside
pragmas, not acceptance criteria. Read each hit before editing it.

**Check what actually ships.** `.git/info/exclude` hides `*/DOCS/*` and the
whole agent scaffolding, so a hit in an excluded path never reaches the PR. Run
`git check-ignore -v <path>` before treating one as a blocker, and say in the
report which hits were in excluded paths.

## Pass 3: house comment policy

Per the AL style guide §14.2, AL carries exactly two kinds of comment. Flag
violations found on
the way past, and fix the cheap ones:

- `///` XML documentation on `internal` and global procedures. Not on a
  `local procedure`, a trigger, `OnRun`, or an event subscriber.
- A comment justifying a `#pragma warning disable`, with a matching `restore`.
  Trim these for length like any other, but the justification and any Learn link
  stay.

Everything else goes: `//` banners, step narration, commented-out code, and
prose "why" comments. When one of those is carrying real information, extract a
`local procedure` or a named `Label` instead of keeping the comment.

## Verify

Comment-only edits cannot break a compile, but they can break an XML doc tag or
land next to a pre-existing failure and get blamed for it.

1. Compile the app: `al_compile` with `onlyErrors: true`.
2. If anything fails, establish the baseline before reading a line of it:

```
git stash push -m baseline -- <the files you touched>
# al_compile again
git stash pop
```

3. Compare the two diagnostic sets. Report which findings are yours and which
   were already there. Read app-specific known baseline findings from
   `APP_CONTEXT.md`; this shared skill carries no consumer-app warning list.

Style guide section 14 owns documentation and comments. Re-read it for the
touched files when the pass was large. No reviewer set is required for an
editorial pass.

## Report

State, in this order:

1. Line count removed and added, from `git diff --stat`.
2. Per object: what was cut and what was deliberately kept.
3. Where any moved reasoning now lives.
4. Process references removed, and any left alone with the reason.
5. Compile result, with baseline failures separated from new ones.
6. What was not done and why.

Offer the diff through `hunk-review` rather than pasting it.
