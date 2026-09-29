# Agent workflow migration execution

Owner approved option B and section 12 defaults on 2026-09-29.

## Baseline

- Source: `f696dc480b8ee8df8bbbba7c694747aafe6e5f19`.
- Baseline ref: `baseline/agent-workflows-2026-09-29`.
- Corpus: `dcc2f1fa8271f8fb70711d62a08fb33435e1ce36`.
- Isolated branch: `refactor/agent-workflows`.
- Original checkout and installed consumers are not migration targets.
- Observed tool versions: OpenCode 1.18.33, global ALTool 17.0.34.45391,
  extension 18.0.2732683 / ALTool 18.0.41.45789, Node 24.18.1, Python 3.13.15.
- Baseline host-generated plugin dependency: `@opencode-ai/plugin` 1.18.23.
  Baseline npm MCP versions were not pinned; a reproducible task comparison must
  provision identical explicit versions rather than claim the Git ref freezes them.
- No credentials or global authentication databases are copied.

## Progress

- M0: baseline ref and isolated worktree created; approval recorded.
- M1–M5: pending.
- M6: infrastructure validation pending. Product task comparisons and live pilot
  await selection of authorized apps/tasks and an execution budget.
