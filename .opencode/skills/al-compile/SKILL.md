---
name: al-compile
kind: action-skill
id: al-compile
version: 1
title: AL compile with the full analyzer set
description: Compiles an AL app with alc.exe directly, running CodeCop, UICop, PerTenantExtensionCop and the full ALCops analyzer set against the shared ADIGO ruleset. Use when asked to build, compile, or check an app for analyzer warnings without going through al-mcp, when al-mcp fails to start, or when a baseline-vs-changed comparison of warnings is needed.
inputs: [app-folder]
outputs: [findings-report, app-package]
bc-version: [all]
technologies: [al]
countries: [w1]
application-area: [all]
---

# AL compile with analyzers

Compiles one AL app folder with `alc.exe` from the installed VS Code AL
extension, with the same analyzer set and ruleset the workspace uses in
`.code-workspace`. This is the deterministic alternative to `al-mcp`'s
`al_compile`: same compiler, same analyzers, same rules, but no MCP server in
the loop and full control over output paths.

## When to use

- A build is needed and `al-mcp` is not running, fails to start (it needs a
  valid `app.json` and `.alpackages` present), or returns something odd.
- A baseline comparison is needed: stash, compile, pop, compile, diff the
  warning lists. See "Establish the baseline" in `AGENTS.md`.
- CI parity: the pipeline fails on warnings (`failOn: warning`), so the exact
  analyzer set matters. A compile without the ALCops set is not a valid check.

## When not to use

Do not use this as a substitute for reading analyzer output carefully. The
skill runs the compiler; interpreting findings against the baseline and the
house suppressions is still the agent's job.

## Paths

Resolve everything dynamically. Never hardcode an app folder or an extension
version.

```sh
# The AL compiler and analyzers come from the installed VS Code AL extension.
# Resolve the newest one:
ALEXT=$(ls -d ~/.vscode/extensions/ms-dynamics-smb.al-* | sort -V | tail -1)
ALC="$ALEXT/bin/linux/alc"
ANALYZERS="$ALEXT/bin/Analyzers"

# Discover the app folder(s) from the session working directory:
find . -maxdepth 3 -name app.json -not -path '*/node_modules/*' -not -path '*/.alpackages/*' -exec dirname {} \;
```

In a multi-app workspace the `find` returns one line per app. Compile **once
per app folder**, in dependency order (read `dependencies` in each `app.json`),
and report per app. Never pass the repo root as the project folder: it has no
`app.json` and the compile silently does nothing.

## The command

Run from the app folder (the one containing `app.json`):

```sh
APP=<app folder from find, e.g. ADIGO.BAU.Interfaces.GAEB>
OUT=$(mktemp -d /tmp/alcompile.XXXXXX)

time "$ALC" \
  /project:"$APP" \
  /packagecachepath:"$APP/.alpackages" \
  /analyzer:"$ANALYZERS/Microsoft.Dynamics.Nav.CodeCop.dll" \
  /analyzer:"$ANALYZERS/Microsoft.Dynamics.Nav.UICop.dll" \
  /analyzer:"$ANALYZERS/Microsoft.Dynamics.Nav.PerTenantExtensionCop.dll" \
  /analyzer:"$ANALYZERS/ALCops.ApplicationCop.dll" \
  /analyzer:"$ANALYZERS/ALCops.DocumentationCop.dll" \
  /analyzer:"$ANALYZERS/ALCops.FormattingCop.dll" \
  /analyzer:"$ANALYZERS/ALCops.LinterCop.dll" \
  /analyzer:"$ANALYZERS/ALCops.PlatformCop.dll" \
  /analyzer:"$ANALYZERS/ALCops.TestAutomationCop.dll" \
  /analyzer:"$ANALYZERS/ALCops.Common.dll" \
  /ruleset:"$APP/../.codeAnalysis/ADIGO.ruleset.json" \
  /out:"$OUT/$APP.app" \
  > "$OUT/compile.log" 2>&1

echo "exit=$?"
```

Notes on the flags:

- `/analyzer` is repeatable; every DLL gets its own flag. The order does not
  matter, but keep the Microsoft cops first and the ALCops set after, matching
  the workspace settings so output diffs stay stable.
- The ruleset lives **one level above the app folder** (repo root), in
  `.codeAnalysis/ADIGO.ruleset.json`. If a repo uses a different ruleset name,
  check the `al.ruleSetPath` value in the workspace file first and use that.
- `/packagecachepath` must point at the app's own `.alpackages`. A stale
  package cache is the most common cause of phantom errors after a dependency
  changed; if errors reference missing symbols from a workspace sibling app,
  rebuild that app first and copy its `.app` into this `.alpackages`.
- Write the log and the `.app` to a fresh temp dir, not into the repo. The
  repo's `git status` stays clean and reruns do not mix outputs.

## Reading the result

```sh
wc -l "$OUT/compile.log"
grep -cE "warning|error" "$OUT/compile.log"
grep -E "error" "$OUT/compile.log"
```

- `exit=0` with warnings is still a CI failure (`failOn: warning`). Report the
  warning count, not just the exit code.
- Diagnostic lines are `path(line,col): <severity> <RULE>: message`. Paths in
  the log are relative to the app folder; line numbers are **1-based** (Serena
  is 0-based, translate before jumping to a symbol).
- Classify findings before reporting: which are new, which are baseline. The
  known baseline for this house (LC0091 false positives, pre-existing PC0037
  and LC0052) is documented in `AGENTS.md` under "Establish the baseline".
  Suppressed with justification and never to be "fixed": `AS0051`, `AS0052`,
  `AS0081`, `AS0084`, `AS0092`, `PTE0012`, `AL1025`, `PC0037`, `DC0007`,
  `DC0009`.

## Baseline comparison recipe

When a warning count looks wrong, prove it is pre-existing before touching
code:

```sh
git stash -u
# run the compile command above into OUT_A
git stash pop
# run the compile command above into OUT_B
diff <(grep -oE "[A-Z]{2,}[0-9]{4}" "$OUT_A/compile.log" | sort | uniq -c) \
     <(grep -oE "[A-Z]{2,}[0-9]{4}" "$OUT_B/compile.log" | sort | uniq -c)
```

Report which rule counts are yours and which were already there.

## After the compile

A successful build triggers the post-build hook, which prompts the mandatory
verifier set from `AGENTS.md` (`al-code-quality-reviewer` and
`al-readability-checker`, plus the test verifiers when tests are opted in).
Run them. The compile alone is not the quality gate.
