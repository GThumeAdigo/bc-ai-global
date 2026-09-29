# Scaffold maintainer contract

This repository maintains shared Business Central agent workflows. It is not an
AL app. Consumer instructions live in `runtime/AGENTS.md`; blank product context
and specs live in `templates/`. Do not fill those with scaffold facts.

- Read the approved plan under `plans/` for substantial workflow changes.
- Inspect Git status and preserve user work. Implement in a separate checkout
  when consumers still link to the original source directory.
- Keep native OpenCode agents and skills under `.opencode/`. Use one authority
  for each policy; commands and documentation link rather than repeat it.
- Never edit `.opencode/BCQuality-ADIGO/` in place. It is a pinned submodule.
- Use file editing tools for changes and read governed artifacts back.
- Run `python3 scripts/verify-scaffold`. Fixtures do not prove product AL behavior.
- Test installation with a temporary app and an explicit release/state root.
  Do not change global host settings or live consumers without authorization.
- Report unavailable checks separately from failures and successful executions.
- Model/runtime files are loaded at startup. Restart the host to test changes.
- Commit only intended changes when requested. Never infer permission to push,
  merge, discard user work, or migrate a live consumer from plan approval alone.
- Keep prompts and docs direct, with no em dashes. Review notes may be German.

Run-local/private logs are not source. `plans/` holds maintainer decisions and
redacted evidence and is never installed into consumer apps.
