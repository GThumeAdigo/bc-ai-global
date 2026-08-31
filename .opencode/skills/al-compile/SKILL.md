---
name: al-compile
kind: action-skill
id: al-compile
version: 2
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
  warning lists. The recipe is in this skill under "Baseline comparison
  recipe".
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

Run the script in `scripts/compile.sh` (relative to this skill's base
directory). Do not retype the full `alc` invocation inline; retyping the long
analyzer list is error-prone, and a mistyped or empty `/analyzer:` argument
fails with `AL1007`.

```sh
bash .opencode/skills/al-compile/scripts/compile.sh "<app folder>"
```

The script takes an optional second argument to override the ruleset. It
resolves the newest installed AL extension, runs `alc` once with the full
analyzer set and ruleset, writes the log and the `.app` to a fresh temp dir,
and prints `app:`, `log:`, `output:`, and an `exit=<n> errors=<n>
warnings=<n> infos=<n>` summary line. Its exit code is the compiler exit
code. Infos are counted too: the house standard is zero infos, so a clean
compile means 0 errors, 0 warnings, and 0 infos.

In a multi-app workspace, compile **once per app folder**, in dependency order
(read `dependencies` in each `app.json`), and report per app. Never pass the
repo root as the project folder: it has no `app.json` and the compile silently
does nothing.

What the script does, for reference:

- Analyzer set: the three Microsoft cops (CodeCop, UICop,
  PerTenantExtensionCop) first, then the seven ALCops DLLs, matching the
  workspace settings so output diffs stay stable. The script fails fast with a
  clear message if the compiler or any analyzer DLL is missing.
- Ruleset: defaults to `.codeAnalysis/ADIGO.ruleset.json` one level above the
  app folder (repo root). If a repo uses a different ruleset name, the script
  falls back to the `al.ruleSetPath` value in a sibling `.code-workspace`
  file. Compiling without a ruleset prints a note and is not a valid CI-parity
  check.
- `/packagecachepath` points at the app's own `.alpackages`. A stale package
  cache is the most common cause of phantom errors after a dependency changed;
  if errors reference missing symbols from a workspace sibling app, rebuild
  that app first and copy its `.app` into this `.alpackages`.

## Reading the result

The script prints the log path in its `log:` line. Use it for the detail:

```sh
LOG=<log path from the script's log: line>
grep -E ": error" "$LOG"
grep -E ": warning" "$LOG"
grep -E ": info" "$LOG"
```

- `exit=0` with warnings is still a CI failure (`failOn: warning`). Report the
  warning count, not just the exit code. Infos do not fail CI, but the house
  standard is zero infos, so list and resolve them like warnings.
- Diagnostic lines are `path(line,col): <severity> <RULE>: message`. Paths in
  the log are relative to the app folder; line numbers are **1-based** (Serena
  is 0-based, translate before jumping to a symbol).
- Classify findings before reporting: which are new and which are baseline.
  Read known app-specific warnings and justified suppressions from
  `APP_CONTEXT.md`, the app's ruleset, and analyzer configuration. This shared
  skill does not define a consumer-app baseline or suppression list. When a
  build, analyzer, or verifier reports something odd, compare the same command
  on the unmodified tree when it is safe to do so (the recipe below). Record
  app-specific known warnings, analyzer quirks, and baseline counts in
  `APP_CONTEXT.md`, not in the shared contract, and state which findings are
  new and which are baseline.

## Baseline comparison recipe

When a warning count looks wrong, prove it is pre-existing before touching
code:

```sh
bash .opencode/skills/al-compile/scripts/compile.sh "<app folder>"
OUT_A=<log path from the first run>
git stash -u
bash .opencode/skills/al-compile/scripts/compile.sh "<app folder>"
OUT_B=<log path from the second run>
git stash pop
diff <(grep -oE "[A-Z]{2,}[0-9]{4}" "$OUT_A" | sort | uniq -c) \
     <(grep -oE "[A-Z]{2,}[0-9]{4}" "$OUT_B" | sort | uniq -c)
```

Report which rule counts are yours and which were already there.

## After the compile

A successful build triggers the post-build hook, which prompts the remaining
verifier work: during the SDD Test step that is the mandatory verifier set
defined there (`al-code-quality-reviewer` and `al-readability-checker`, plus
the test verifiers when tests are opted in); outside the SDD loop it is the
two always-on reviewers per "Outside the SDD loop" in `AGENTS.md`. Run them.
The compile alone is not the quality gate.
