---
name: hunk-review
kind: action-skill
id: hunk-review
version: 1
title: Hunk interactive diff review
description: Publishes short German inline notes to a live Hunk diff session after substantial implementation or verifier findings, and guides interactive changeset reviews. Use proactively at implementation/review checkpoints, even when a clean change has no defects to report.
inputs: [pr-diff, file-path]
outputs: [review-narration, inline-notes]
bc-version: [all]
technologies: [al]
countries: [w1]
application-area: [all]
---

# hunk-review

Hunk is an interactive terminal diff viewer. The TUI belongs to the developer.
This skill is how an agent steers it: load a changeset, move the developer's
viewport to what matters, and leave notes pinned to exact lines.

## The authoritative content ships with the CLI

The real instructions are installed alongside the Hunk binary, not stored in
this repo. Resolve and read them first, every time:

```bash
"$HOME/.hunk/bin/hunk" skill path
```

Read the file that command prints and follow it. Do not paraphrase it from
memory, and do not copy it into this repo. It ships with the CLI and changes
when the CLI is upgraded, so a vendored copy would silently rot. This file only
carries the parts that are specific to this repo.

Never run `hunk diff` or `hunk show` directly. Those launch the interactive TUI,
which is the developer's, not yours. Agents drive a session that already exists
through `hunk session *`.

## Repo-specific notes

### Do not depend on the interactive shell's PATH

Use `"$HOME/.hunk/bin/hunk"` for every invocation. Non-interactive agent shells
do not necessarily inherit fish, Bash, or zsh startup settings. Resolve the
installed CLI this way rather than hardcoding a user's home directory.

### Publication belongs to the coordinator

Do not wait for an explicit request for Hunk comments. At the first stable
implementation checkpoint, after verifier findings arrive, and before final
handoff, the coordinator checks for a matching live session and publishes or
refreshes useful notes. Subagents return file/line evidence and candidate
explanations; they do not compete to navigate or reload the developer's TUI.

Keep a small useful set: normally two to five notes for a substantial change,
or one for a small non-obvious fix. This is a relevance target, not a quota.
Explain intent, important behavior, a tradeoff, or what to verify, including on
clean changes. Do not invent defects or annotate obvious renames just to fill
the target. If there is nothing useful to add, report that briefly.

### Publish and verify, do not stop at preparing notes

1. Run `session list --json`, select the exact checkout, then inspect
   `session review --include-notes --json`. Use the explicit session ID when
   several sessions match. Never attach notes to another checkout just because
   it is the only open session.
2. Check the loaded diff against the reviewed revision and changed paths.
   Reload a stale diff with the relevant pathspec before locating anchors.
   Never assume a source line occurs in the loaded hunk; verify both path and
   side. Removed code uses `oldLine`; additions and current code use `newLine`.
3. Inspect existing notes, deduplicate by path/side/line/topic, and prepare one
   JSON batch of new notes. Use a file under `/tmp/opencode/`, written with the
   file-editing tool, to avoid shell quoting errors. Apply it using `comment
   apply --stdin` with input redirection. For a walkthrough, navigate first
   and use `--focus`; background publication should not move the viewport.
4. Read back `comment list --type all --json` and confirm the expected notes
   exist. A prepared payload or successful reload is not proof of publication.
   Check `session context --json`: if `showAgentNotes` is false, tell the
   developer to enable agent notes in Hunk. Do not claim the comments are
   visible merely because they exist.
5. After fixes/reloads, re-check anchors and update only this task's agent
   notes. Remove or replace a resolved issue with a clearly marked explanation
   if still useful. Preserve human notes and unrelated agent notes; never use
   blanket `comment clear` to refresh a batch.
6. Report the outcome once: published count, intentionally no useful notes,
   or deferred with the reason. If the CLI is unavailable or no matching
   session exists, ask once for the developer to open Hunk in that checkout,
   keep the prepared batch under `/tmp/opencode/`, and continue the coding
   work. Retry when a matching session becomes available. Hunk availability
   is not a build or review gate.

### Selecting the session

`--repo .` from the workspace root resolves the session in the normal case.
Sibling worktrees are separate checkouts with their own `repoRoot`. Match the
actual checkout, not just the repository name. When more than one session
matches it, ask which to use and pass that explicit `<session-id>`.

### An empty session is not an error

`fileCount: 0` with a clean working tree means nothing is loaded, not that
something failed. Load the changeset you actually want to discuss:

```bash
"$HOME/.hunk/bin/hunk" session reload --repo . -- show HEAD
"$HOME/.hunk/bin/hunk" session reload --repo . -- diff -- "<changed app path>"
"$HOME/.hunk/bin/hunk" session reload --repo . -- diff main...HEAD -- "<changed app path>"
```

### Scope the reload, do not load the whole branch

A branch can contain hundreds of unrelated changes. Narrow the review to one
commit, a short commit range, or a pathspec covering the objects under
discussion, and say which slice you loaded.

`hunk diff` includes untracked files by default. Reload with
`-- diff --exclude-untracked` when the developer wants tracked changes only.

### Turn verifier findings into pinned notes

This is the highest-value use of Hunk in this repo. The mandatory verifiers
(`al-code-quality-reviewer`, `al-readability-checker`, and the rest of the set
in the `sdd` skill's Test step) emit findings that already carry a file, a
line, a rule slug, and a
citation. Do not flatten that into a chat list. Batch it into one
`comment apply` so each finding lands on the line that triggered it:

Example payload, using the actual workspace-relative path and verified line:

```json
{"comments":[
  {"filePath":"<app>/src/Process.Codeunit.al","newLine":214,
   "summary":"Prüfen: Vor der FindSet-Schleife fehlt SetLoadFields.",
   "rationale":"Die Schleife liest sonst alle Felder. house:styleguide-12-setloadfields; .opencode/skills/al-code-review/styleguide.md §12."}
]}
```

Save the batch with the file-editing tool, then publish it:

```bash
"$HOME/.hunk/bin/hunk" session comment apply --repo . --stdin < /tmp/opencode/hunk-notes.json
"$HOME/.hunk/bin/hunk" session comment list --repo . --type all --json
```

For findings, put the rule slug and the BCQuality or style guide path in `rationale`, and
prefer one batch over many single `comment add` calls. Findings that are
informational or pre-existing baseline noise (the app's baseline list in
`APP_CONTEXT.md`) should say so in the note, so the developer is not sent
chasing them.

Explanatory notes do not need an invented rule citation. Distinguish them from
defects: `Hinweis: Die Daten werden vor dem Senden gespeichert, damit ein
Wiederholungsversuch dieselbe Nachricht nutzt.` An optional check can start
with `Test:` and a resolved defect with `Behoben:`. State the reason or effect,
not just what changed. A clean verifier result is no reason to omit useful
explanations of the implementation.

### Write the notes in German, and keep them short

The developer is a German native speaker. Hunk notes are the one place in this
repo where German is the working language, alongside the translation files.
Write `summary` and `rationale` in German.

Everything else stays English: AL code and identifiers, `Label` sources, `///`
documentation, spec files, commit messages, agent and skill files, and your
replies in the chat. Only the note bodies switch.

Keep them short and plain. A pinned note sits next to the code, so it does not
need to restate what the code already shows.

- `summary` is one sentence. Say the one thing the developer needs to know.
- `rationale` is one or two sentences, and often unnecessary. Leave it out when
  the summary already covers it.
- Use ordinary words. "Der Text steht jetzt doppelt drin" beats "Die
  Zeichenkette wird an dieser Stelle redundant dupliziert". Do not reach for the
  most formal word available.
- Keep identifiers, object names, rule slugs and file paths in their original
  form. Do not translate `SetLoadFields`, `GOXGAE Markup Renderer` or
  `house:styleguide-12-...`.
- Cut the filler. No "Nur ein kleiner Hinweis", no "Man könnte eventuell
  überlegen, ob".

### Narrate, do not dump

During a walkthrough, navigate before you comment so the developer is looking
at the code you are describing. Use `highlight add --focus` to light up the exact expression while
you explain it and `highlight clear` before moving on. Work in the order that
tells the clearest story, not file order, and skip the hunks the developer would
spot unaided: renames, moved folders, version bumps.

## What this does not replace

Hunk shows what the diff says. It cannot compile, run the analyzers, or observe
what the web client renders. It sits alongside the mandatory verifier set and
`bc-webclient-runner`, it does not stand in for either. A clean walkthrough in
Hunk is not a passing build.
