# Read-only specialist execution

Review source and existing evidence without editing them. The agent frontmatter
limits tools; this is not an OS sandbox and does not authorize shell redirection
or compound commands that write source.

For BCQuality exact routing, invoke `python3` with the known
`.opencode/BCQuality-ADIGO/tools/route_entry.py` path (absolute when needed),
`--root <corpus>` and `--task-context /dev/stdin`. Supply task-context JSON on
stdin, for example through a shell here-document. The caller may instead supply
an existing context file. This avoids needing file-write permissions just to
prepare routing input. The router reads context and emits its dispatch record;
it does not perform the review or generate the index.

Installed snapshots have a prepared index. Check that it is usable for the
selected corpus/layers. If it is missing/stale or the router fails, report
partial/failed and return preparation to the coordinator. Do not run an index
builder inside an immutable release, invent a pass, or bypass tool restrictions.
This execution boundary takes precedence over generic adapter wording about
creating a temporary context file or performing index preparation.

The SDD skill owns v2 review selection and confirmation. Existing legacy approval
contracts remain legacy; being available as a specialist is not a mandatory v2
trigger. A source-only review cannot substitute for required build/test evidence.
