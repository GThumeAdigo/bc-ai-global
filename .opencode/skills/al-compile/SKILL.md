---
name: al-compile
description: Compile an explicit AL app with analyzers and reproducible input/diagnostic evidence. Use for builds, diagnostics and baseline comparisons. Does not trigger unrelated reviews.
---

# AL compile

Run `bash .opencode/skills/al-compile/scripts/compile.sh "<app>" [ruleset]`.
The app must contain app.json. Omitted app discovery rejects zero/multiple results.
Build dependencies first, pass each app explicitly, and refresh dependent symbol
packages. Serena diagnostics do not replace this build.

## Toolchain and analyzer selection

- `AL_COMPILER_EXTENSION_PATH` selects an explicit installed AL extension.
  Otherwise the newest installed extension is used and its path/hash is recorded.
- `AL_ANALYZER_PROFILE` selects a JSON file with `analyzers`, a nonempty list of
  DLL basenames in that extension's analyzer directory. Derive it from the app's
  actual CI/settings. Without it the legacy ten-DLL house set remains the default.
- AppSourceCop is not in the default set. Select it explicitly for AppSource
  verification. Do not claim CI parity until the app's actual set is compared.
- Ruleset precedence remains explicit argument, app/folder/workspace settings,
  then parent `.codeAnalysis/ADIGO.ruleset.json`. The resolver supports JSONC and
  rejects ambiguous workspaces, unsupported variables and missing rulesets.
- Missing compiler, analyzer or ruleset is failure, never a silent clean fallback.

## Evidence and result

The wrapper writes package/log/evidence to a fresh temporary directory and prints
their paths. `evidence.json` records source hashes/revision, compiler hash/path,
analyzers, ruleset, symbol packages, exact invocation, compiler exit and diagnostics.
Keep its path in validation; copy required evidence into the app's durable private
evidence location before temporary cleanup. Diagnostic locations are 1-based.

Default exit preserves compiler failure/success, except failed evidence production
also fails. Compiler success with warnings is not a clean build. Report errors,
warnings, infos and their baseline classification. App CI determines thresholds.

## Isolated comparison

Compile baseline and candidate in separate source checkouts with identical
compiler, analyzers, ruleset and dependency packages. Never use stash as the
normal baseline mechanism. A Git worktree alone does not isolate shared runtime.

Set `AL_BASELINE_EVIDENCE` to the baseline JSON to compare normalized diagnostic
identities and multiplicities, not just counts. Line shifts are ignored; changed
messages/paths are not. Incompatible toolchain/ruleset/packages are reported as
incomparable. With `AL_VERIFY_NEW_DIAGNOSTICS=1`, any new diagnostic fails with
exit 3; without a baseline, any diagnostic fails. This strict mode is opt-in and
does not redefine every app's CI policy.

The evidence hashes normal app AL files, manifest and packages. Generated AL
outside the app or source linked from external directories needs separately
recorded inputs; do not claim full reproducibility for unrecorded external code.
Compile/test evidence precedes applicable SDD review. A build-only request ends
with the build result, without a mandatory reviewer or documentation sequence.
