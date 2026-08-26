---
name: hunk-review
kind: action-skill
id: hunk-review
version: 1
title: Hunk interactive diff review
description: Drives a live Hunk interactive diff session from the CLI to walk the developer through a changeset, navigating files, hunks and lines, painting attention marks, and leaving inline review notes. Use whenever changes need to be shown or reviewed rather than pasted into chat.
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
export PATH="$HOME/.hunk/bin:$PATH"
hunk skill path
```

Read the file that command prints and follow it. Do not paraphrase it from
memory, and do not copy it into this repo. It ships with the CLI and changes
when the CLI is upgraded, so a vendored copy would silently rot. This file only
carries the parts that are specific to this repo.

Never run `hunk diff` or `hunk show` directly. Those launch the interactive TUI,
which is the developer's, not yours. Agents drive a session that already exists
through `hunk session *`.

## Repo-specific notes

### `hunk` is not on the agent's PATH

The installer appends the export to `~/.zshrc`, which covers the developer's
interactive shell and nothing else. Agent shells here are non-interactive and do
not source it, so a bare `hunk ...` fails with "command not found". Prefix every
invocation:

```bash
export PATH="$HOME/.hunk/bin:$PATH" && hunk session list --json
```

Use `$HOME/.hunk/bin`, not a hardcoded `/home/<user>/...` path, for the same
reason the AL project path is discovered rather than hardcoded.

### Selecting the session

`--repo .` from the workspace root resolves the session in the normal case. This
checkout is a **git worktree**, so sibling worktrees of the same repo are
separate directories and each gets its own session and its own `repoRoot`. When
`hunk session list` shows more than one, pass the explicit `<session-id>` instead
of guessing which `--repo` you want.

### An empty session is not an error

`fileCount: 0` with a clean working tree means nothing is loaded, not that
something failed. Load the changeset you actually want to discuss:

```bash
hunk session reload --repo . -- show HEAD              # the last commit
hunk session reload --repo . -- diff                   # uncommitted work
hunk session reload --repo . -- diff main...HEAD -- "app/GAE/06 Projects"
```

### Scope the reload, do not load the whole branch

A hotfix or feature branch here runs to hundreds of files and tens of thousands
of inserted lines, most of it folder moves and renames. `diff main...HEAD` with
no pathspec produces a review nobody can hold in their head. Narrow it to one
commit, a short commit range, or a pathspec covering the objects under
discussion, and say which slice you loaded.

`hunk diff` includes untracked files by default. Reload with
`-- diff --exclude-untracked` when the developer wants tracked changes only.

### Turn verifier findings into pinned notes

This is the highest-value use of Hunk in this repo. The mandatory verifiers
(`al-code-quality-reviewer`, `al-readability-checker`, and the rest of the set in
`AGENTS.md`) emit findings that already carry a file, a line, a rule slug, and a
citation. Do not flatten that into a chat list. Batch it into one
`comment apply` so each finding lands on the line that triggered it:

```bash
printf '%s' '{"comments":[
  {"filePath":"app/GAE/06 Projects/GOXGAEProjectMgt.Codeunit.al","newLine":214,
   "summary":"Vor der FindSet-Schleife fehlt SetLoadFields.",
   "rationale":"house:styleguide-12-setloadfields"}
]}' | hunk session comment apply --repo . --stdin --focus
```

Put the rule slug and the BCQuality or style guide path in `rationale`, and
prefer one batch over many single `comment add` calls. Findings that are
informational or pre-existing baseline noise (see the baseline list in
`AGENTS.md`) should say so in the note, so the developer is not sent chasing
them.

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

Navigate before you comment, so the developer is looking at the code you are
describing. Use `highlight add --focus` to light up the exact expression while
you explain it and `highlight clear` before moving on. Work in the order that
tells the clearest story, not file order, and skip the hunks the developer would
spot unaided: renames, moved folders, version bumps.

## What this does not replace

Hunk shows what the diff says. It cannot compile, run the analyzers, or observe
what the web client renders. It sits alongside the mandatory verifier set and
`bc-webclient-runner`, it does not stand in for either. A clean walkthrough in
Hunk is not a passing build.
