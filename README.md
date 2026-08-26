# ADIGO Agentic Business Central Development

This repository is a prototype for agentic Microsoft Dynamics 365 Business
Central product development at ADIGO. It is intended for use with
[OpenCode](https://opencode.ai) and is not yet a production-ready development
template.

The prototype combines Spec-Driven Development, focused AL review agents, and a
vendored BCQuality knowledge base. Its purpose is to explore a repeatable way for
ADIGO developers and AI agents to design, implement, and review Business Central
product features without treating chat history as the source of truth.

## Quick start with an existing BC repository

The Business Central repository should remain the project root where OpenCode
runs. Do not put the BC repository inside this template repository, and do not
add this template as a Git submodule. Nested repositories make Git status, diffs,
hooks, builds, and agent path discovery less reliable.

1. Clone this template beside the existing Business Central repository.

   ```text
   Repos/
   |-- SDD_TEMPLATE/
   `-- my-bc-product/
   ```

2. Copy the agentic scaffold into the root of the BC repository.

   ```bash
   cp -R ../SDD_TEMPLATE/.opencode .
   cp -R ../SDD_TEMPLATE/specs .
   cp ../SDD_TEMPLATE/AGENTS.md .
   cp ../SDD_TEMPLATE/CLAUDE.md .
   cp ../SDD_TEMPLATE/opencode.json .
   ```

   The resulting repository should resemble:

   ```text
   my-bc-product/
   |-- app/
   |   `-- app.json
   |-- test/
   |   `-- app.json
   |-- .opencode/
   |-- specs/
   |-- AGENTS.md
   |-- CLAUDE.md
   `-- opencode.json
   ```

   Each app folder carries its own `app.json`, `.alpackages`, and analyzer
   settings. A single-app repo may instead have `app.json` at the root. Agents
   discover the app folders dynamically and compile each one separately; see the
   AL project path section in `AGENTS.md`.

3. Decide which scaffold files belong in the BC repository's Git history.
   The recommended approach is to commit `AGENTS.md` and `specs/`, because they
   contain durable product and architecture decisions, while keeping the
   personal OpenCode runtime files local.

   Copy this repository's ready-made `exclude` into place:

   ```bash
   cp ../SDD_TEMPLATE/exclude .git/info/exclude
   ```

   It excludes `.opencode/`, `CLAUDE.md`, and `opencode.json`. If the BC
   repository already has a `.git/info/exclude`, append instead of overwriting:

   ```bash
   cat ../SDD_TEMPLATE/exclude >> .git/info/exclude
   ```

   `.git/info/exclude` behaves like `.gitignore` but is local to the clone and is
   not committed. If none of the scaffold may be committed, uncomment the
   `AGENTS.md` and `specs/` lines at the end of the file. Be aware that ignored
   specs then exist only on the local machine and are not shared or protected by
   the BC repository.

4. Fill in `specs/brief.md`, `specs/tech-design.md`, and `specs/roadmap.md` for
   the product. Do not start production AL work while these files still contain
   unresolved placeholders.

5. Start OpenCode from the BC repository root, not from this template repository.

   ```bash
   cd /path/to/my-bc-product
   opencode
   ```

6. Run `/al-spec-init` and resolve its findings. For each feature, continue with
   `/al-spec-feature`, `/al-plan-feature`, and `/al-implement-feature`, stopping
   for human review between stages as required by `AGENTS.md`.

7. Keep this template clone as the update source. Re-copy deliberate changes to
   `.opencode/`, `opencode.json`, and `AGENTS.md` when the prototype evolves. Do
   not overwrite populated constitution files or feature specs with blank
   templates. A future installer or update script can automate this selective
   synchronization without requiring a submodule.

## Prototype status

This repository is in the prototype stage. Its workflows, prompts, agents, and
quality gates are still being validated and may change. It currently provides the
agentic development scaffold, not a complete Business Central app or a configured
AL-Go pipeline.

Do not assume that this repository can build, test, publish, or deploy an AL app
without first adding the product's `app.json`, AL source, dependencies, and CI/CD
configuration.

## Development model

The spec is the brain, and the agent is the muscle. Durable decisions live under
`specs/`; OpenCode reads those artifacts and performs the implementation and
review work.

Each feature follows this sequence:

1. **Feature spec:** define the problem, scope, user flow, acceptance criteria,
   and the durable automated-test decision.
2. **Plan:** define the standard BC functionality to reuse, custom AL objects,
   object IDs, data model, integrations, risks, and test strategy.
3. **Implement:** write AL only after the spec and plan have been reviewed and
   approved.
4. **Verify:** build the app and run the applicable code-quality, readability,
   integration, upgrade, and optional test verifiers.
5. **Document:** update feature documentation and the roadmap.

The complete workflow and agent contract are in [AGENTS.md](AGENTS.md).

## Repository contents

- `specs/`: project constitution, roadmap, feature artifacts, and templates.
- `.opencode/agents/`: focused Business Central reviewers and verifiers.
- `.opencode/skills/`: OpenCode skills, including the SDD review gates.
- `.opencode/skills/al-code-review/`: the ADIGO house rules (`SKILL.md`) and the AL style guide (`styleguide.md`), which agents read when writing and reviewing AL.
- `.opencode/commands/`: OpenCode slash commands for the SDD workflow.
- `.opencode/bcquality/`: vendored BCQuality knowledge and review skills.
- `.opencode/plugins/`: OpenCode automation, including the post-build verifier reminder.
- `opencode.json`: project-level OpenCode configuration.

## OpenCode workflow

Install the [OpenCode CLI](https://opencode.ai), start it from the repository root,
and describe the Business Central product or feature to develop. OpenCode loads
`AGENTS.md`, the local skills, agents, commands, and plugins through
`opencode.json`.

The main review commands are:

- `/al-spec-init`: review `specs/brief.md`, `specs/tech-design.md`, and `specs/roadmap.md`.
- `/al-spec-feature`: review a feature specification against the constitution.
- `/al-plan-feature`: review a feature plan and task list against its specification.
- `/al-implement-feature`: review an implementation against its approved artifacts.

OpenCode may also select the matching skill or verifier from a natural-language
request. After an AL build, the post-build plugin reminds the agent to run the
mandatory verifier set. Test agents run only when the feature's durable test
decision is `yes`.

## House rules and the AL style guide

`.opencode/skills/al-code-review/SKILL.md` holds the ADIGO house rules, and
`.opencode/skills/al-code-review/styleguide.md` holds the AL style guide. There is
exactly one copy of each; agents read them both when authoring AL and when
reviewing it, and they outrank BCQuality when the two disagree. Each agent that
writes or reviews AL names the style guide sections it enforces, listed in
[AGENTS.md](AGENTS.md#which-agents-read-the-style-guide).

The style guide uses ADIGO identifiers in its examples (the `GOX`/`GOXOUT` object
prefix, the `GOXFOU Error` handler, the `ADIGO.ITS.*` namespaces). When adopting
the template in a repo with different conventions, replace those identifiers; the
rules themselves still apply.

## BCQuality

BCQuality supplies machine-readable Business Central guidance that agents cite in
their findings. Runtime skills under `.opencode/skills/` point to the authoritative
vendored content under `.opencode/bcquality/`. ADIGO-specific house rules remain in
`.opencode/skills/al-code-review/` and take precedence when rules conflict.

## Intended use

This prototype is specifically intended for ADIGO's Business Central product
development. It contains ADIGO conventions and should not be treated as a generic
community template without first replacing those conventions.

## License

The vendored BCQuality content carries its license under
`.opencode/bcquality/LICENSE`.
