# Read-only specialist execution

Review source and existing evidence without editing them. The agent frontmatter
limits tools; this is not an OS sandbox and does not authorize shell redirection
or compound commands that write source.

## Prepare scope and routing inputs

The coordinator supplies the app/repository path, scoped source paths or an
existing diff, and the baseline/current revisions when a comparison is required.
Read only the expected action skill's frontmatter before routing to identify its
declared `inputs`; this is preparation, not permission to execute that action.
Populate `inputs-available` with exact declared identifiers backed by inputs you
can actually inspect. For source-review actions accepting them:

- Use `file-path` when explicit scoped source files are available.
- Use `pr-diff` when an actual scoped diff was supplied or obtained.
- `repository`, `source-files`, feature documents and compilation logs do not
  substitute for either identifier. Do not advertise unavailable inputs.

Specialists may inspect Git in the supplied repository working directory using
`git status`, `git rev-parse`, and `git diff --no-ext-diff --no-textconv`, with
the requested refs and path filters. Use the Bash working-directory parameter
rather than `cd` or compound shell commands. Keep output in memory; do not use
redirection, `--output`, external diff drivers or textconv. Mutating Git commands
remain denied. If a required baseline or source input is missing, report the
specific missing input to the coordinator rather than inventing a comparison.

For example, a performance file review declares:

```json
{
  "requested-skill-id": "al-performance-reviewer",
  "inputs-available": ["file-path"],
  "technologies": ["al"]
}
```

The dispatch must also supply the actual AL file paths. This JSON declares their
availability; it does not contain the source or prove that it was reviewed.

## Route and execute

For BCQuality exact routing, invoke `python3` with the known
`.opencode/BCQuality-ADIGO/tools/route_entry.py` path (absolute when needed),
`--root <corpus>` and `--task-context /dev/stdin`. Supply task-context JSON on
stdin, for example through a shell here-document. The caller may instead supply
an existing context file. This avoids needing file-write permissions just to
prepare routing input. The router reads context and emits its dispatch record;
it does not perform the review or generate the index. A `no-match` record with
`inputs-unsatisfied` means the requested action rejected the supplied identifiers,
not that its file is absent. Return that record and identify the missing declared
input for a corrected coordinator dispatch; do not bypass the guard.

Installed snapshots have a prepared index. Check that it is usable for the
selected corpus/layers. If it is missing/stale or the router fails, report
partial/failed and return preparation to the coordinator. Do not run an index
builder inside an immutable release, invent a pass, or bypass tool restrictions.
This execution boundary takes precedence over generic adapter wording about
creating a temporary context file or performing index preparation.

The SDD skill owns v2 review selection and confirmation. Existing legacy approval
contracts remain legacy; being available as a specialist is not a mandatory v2
trigger. A source-only review cannot substitute for required build/test evidence.
