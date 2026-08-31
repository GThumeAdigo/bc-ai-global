---
name: al-code-review
kind: governance-skill
id: al-code-review
version: 1
title: AL code review (house rules)
description: Review AL code for Business Central extensions against project and Microsoft conventions, including the AL performance checklist and Copilot PromptDialog rules.
inputs: [pr-diff, file-path]
outputs: [local-review]
bc-version: [all]
technologies: [al]
countries: [w1]
application-area: [all]
---

# AL Code Review

## When to use

Reviewing AL code in any BC extension, including AppSource submissions, custom extensions, and per-tenant work.

## Sources

This skill synthesises:

1. The project style guide (`styleguide.md` in this skill folder)
2. The project AL guidelines document
3. `alguidelines.dev`
4. Microsoft CAL guidelines (legacy patterns to be aware of)
5. The `microsoft/alguidelines` repository

When sources conflict, project house rules win.

## Style guide

The project's authoritative AL style guide lives beside this skill at
[`styleguide.md`](styleguide.md). There is exactly one copy of it in the repo.
Read it and apply every rule it defines, in addition to the house rules and core
checks below.

Precedence, highest first:

1. `styleguide.md` (the numbered sections)
2. The house rules in this file
3. BCQuality knowledge files
4. `alguidelines.dev` and Microsoft guidance

Where a check below restates a style guide rule, the style guide's wording is
the one that binds, and the local finding names the style guide section.

Emit style-guide and house-rule findings in a separate local reviewer report
with `severity: block | warn | info`, a
`house:styleguide-<section>-<slug>` rule, message, and location. Do not put
scaffold paths in BCQuality DO `references`; this local skill does not emit the
BCQuality DO shape.

The style guide uses this project's identifiers as examples (the `GOX`/`GOXOUT`
object prefix, the `GOXFOU Error` handler, the `ADIGO.ITS.*` namespace root).
In a repo with a different prefix, namespace root, or foundation app, enforce the
pattern and substitute the local identifier. Do not flag correct local names just
because they are not `GOX*`.

## House rules

1. **Never include `ODataKeyFields` in BC API query definitions.** This is a strict rule. Flag any API query that adds it.
2. Use object IDs from the project's assigned range. Never hardcode IDs outside the assigned range. (§2.1 also caps object names at 30 characters, prefix included.)
3. Capture telemetry on every protected operation using the project's standard telemetry pattern.
4. All user-facing labels go through `Label` declarations. Populate `Comment` whenever the label carries placeholders (`%1`, `%2`) or the meaning is ambiguous out of context, and set `Locked = true` on non-translatable text such as URLs and API field names (§9.1).
5. Raise errors through the foundation error handler (`GOXFOU Error`, `FOUError.Call(...)`), not bare `Error()` (§11).
6. **One codeunit, one responsibility, exactly one public procedure.** A codeunit with two or more public (`procedure` / `internal procedure`) members is a finding unless it is a *helper* codeunit. Fix it by demoting the publics that have no external caller, by moving a second job to its own codeunit, or by merging variants of the same procedure (§7.1).
7. **A helper codeunit must carry the `Helper` name suffix, and only a helper may.** A helper groups small, related helping procedures for one process or topic where each alone is too small for its own codeunit; none of them orchestrates the others. A multi-public codeunit without the suffix is a finding, and so is a `… Helper` that is really a state machine, a lifecycle, or a bag of leftovers from several processes (§7.2).
8. **Banned codeunit name suffixes: `Mgt`, `Mgt.`, `Management`, `Manager`, `Utils`, `Utilities`, `Misc`, `Common`, `General`, `Functions`, `Library`, `Tools`.** They name custody of a topic instead of a job, so nothing is ever out of scope for them. Name the job (`Create Entry`, `Cancel Import`, `Resolve Project`). `Helper` is the only permitted grouping suffix (§2.1).
9. **Codeunit size budget:** over 600 lines is a finding, split it; 400 to 600 needs a stated justification. Split by responsibility cluster with a name per cluster, never at an arbitrary line count into `…Part1`/`…Part2`. A wide dispatch `case` and a large block of stateless lookups are the two shapes that most often hide inside a long codeunit (§7.1).
10. Avoid regular comments (`//`, `/* */`). The code explains itself through its structure and its object, procedure, and variable names; extract a named `local procedure` or a named variable instead of commenting. Required `///` XML documentation on internal and global procedures is exempt and must be left in place; a `local procedure` gets no `///` block at all (§14.1). The only regular-comment exception is a comment that justifies a compiler pragma. A `#pragma warning disable` must carry that justification and be closed with `#pragma warning restore`. Put other rationale in the feature plan or the nearest permitted `///` block. Never leave commented-out code (§14.2).
11. **Procedure complexity thresholds:** flag cyclomatic complexity above 10,
    more than 80 lines, nesting at five levels or deeper, or fan-out to more than
    ten codeunits. The plan must name a testable responsibility seam before
    implementation when the proposed design is likely to cross a threshold.
12. **Telemetry must have an assertion seam.** Protected operations must route
    telemetry through a boundary that AL tests or the platform test telemetry
    facility can observe and assert. A direct, unobservable logging call does not
    satisfy the telemetry testability rule.
13. **Verify platform API assumptions, do not reason from the name.** An AL
    platform API often does less than its name promises. The example that cost a
    review round: `XmlReadOptions.PreserveWhitespace(false)` does **not** remove
    all whitespace, because the parser still reports whitespace-only CDATA and
    anything under `xml:space="preserve"` as significant. When authoring,
    confirm behavior against Microsoft Learn (`microsoft_docs_search`,
    `microsoft_docs_fetch`) before relying on it, and add the backstop in code
    when the platform only gets you part of the way. When reviewing, flag any
    guarantee that rests on unverified platform behavior.

## Core checks

### Naming

- Tables, pages, codeunits, and reports: PascalCase, descriptive, prefixed (§2.1).
- A codeunit name states the one job it does. Banned suffixes: `Mgt`, `Management`, `Manager`, `Utils`, `Misc`, `Common`, `General`, `Functions`, `Library`, `Tools`. `Helper` is permitted only on a genuine helper (§2.1, §7.2).
- Variables: PascalCase, no Hungarian notation, suffixed with the object name, `Temp` prefix on temporary records (§2.3).
- Procedures: PascalCase, verb first ("CalculateAmount" not "AmountCalculation"). Business operation codeunits use the single `Call(...)` entry point instead (§7.1).
- File name equals object name: `<ObjectName>.<ObjectType>.al` (§2.2).

### Structure

- Pages have a single purpose. Master, List, Card, Document, Worksheet, RoleCenter.
- Business logic lives in codeunits, not page triggers.
- One codeunit exposes exactly one public procedure, unless it is a `… Helper` (§7.1, §7.2). Count the `procedure` / `internal procedure` members at 4-space indent; that count is the cheapest SRP proxy in AL (§13.1).
- A codeunit over 600 lines is split by responsibility cluster; 400 to 600 is justified in writing (§7.1).
- One object per `.al` file.
- Namespace first, then `using`, at the top of every file (§3.3).
- Folders follow the feature, not the object type, and objects use the standard `#region` layout (§3.1, §3.2).
- Folder names alone must lead a stranger to any object. Numbers appear only on the top-level feature spine, ordered by data flow; subfolders are unnumbered topic names. A folder holding more than about five objects of one type wants a subfolder **only if a topic is genuinely findable** — flag the crowding, but do not invent a grouping, because a wrong one is worse than a long list. `Helpers/` is the usual split once a feature accrues four or more `… Helper` codeunits (§3.1, §7.2).

### Error handling

- Route user-facing failures through `GOXFOU Error` (`FOUError.Call(ErrorText)` or `FOUError.Call(TableCaption, Key)`), never bare `Error()` (§11.1 to §11.3).
- The handler already produces a collectible `ErrorInfo` with `ErrorType::Client`, so do not hand-roll an `ErrorInfo` envelope around it.
- Errors from external services that should not roll the caller back are stored on the record, not thrown (§11.4).
- `Confirm` only when the user can sensibly answer.
- Error text always comes from a `Label`, never a string literal (§11.5).

### API definitions

- Query objects use `APIPublisher`, `APIGroup`, `APIVersion`, `EntityName`, `EntitySetName`.
- Property `ODataKeyFields` is **forbidden** by project house rules.
- All API fields use `IncludeInDataSet = true` only where needed.

### Permissions

- Every codeunit that touches tables declares an explicit `Permissions` property with least privilege (§10).

### Performance

- Avoid record locking in loops. Use `LockTable` once, then iterate.
- Avoid `FindFirst`/`FindLast` where `Get` would do.
- Filter on indexed fields when possible.
- Set the `RunTrigger` parameter explicitly on every `Insert`, `Modify`, and `Delete` (§12.1).
- `SetLoadFields` before `Get`/`Find*`, filter before retrieving, and prefer `CalcSums`/`Count` over manual loops (§12.2).

## Event subscribers

The project has explicit rules for event subscribers, drawn from the AL Development Standards and §7.3 of the style guide.

- **Keep subscriber codeunits small and focused.** A new instance of the codeunit is created when an event fires. Multi-purpose subscriber codeunits create unnecessary overhead.
- **Group subscriptions by functionality.** Examples: `Subs-SalesPost` for sales posting events, `Subs-SalesHeaderLineEvents` for Sales Header and Sales Line table events.
- **Subscriber procedures are thin.** They call a Management/Handler codeunit that holds the business logic.
- **Consider `SingleInstance`** when shared cached state actually helps, but prefer stateless subscribers and avoid global variables.
- **Use `EventSubscriberInstance = Manual`** when events should only fire during a specific process and explicit control is needed.
- **Naming convention**: `ObjectName_EventName_ElementName`. Example: `Job_OnBeforeUpdateJobTaskDimension`.
- **Exit early.** Bail on temp records, wrong record type, `Session.CurrentExecutionMode <> Normal`, or any unmet precondition.
- **`SkipOnMissingLicense` / `SkipOnMissingPermission`**: for AppSource marketplace apps (BC21+), `true, true` may be acceptable. Discuss with the Product Owner. For non-marketplace/internal apps, use `false, false` so license and permission issues fail fast.

## AL performance checklist

For any PR that touches AL on a performance-sensitive path, apply the checklist captured in `templates/pr-performance-review.md`. Headlines:

- Correct data access method (`Get` > `Find` > `FindFirst` > `IsEmpty`, avoid `FindSet` unless necessary)
- Filters applied before loops, not inside
- `SetCurrentKey` when a non-primary index is required
- `ModifyAll` / `DeleteAll` instead of record-by-record loops
- Temporary tables for heavy looping or sorting
- Queries instead of nested loops
- Subscribers exit early and avoid hidden DB calls
- No auto-increment fields as primary keys
- No assumptions about small data sets

Use the PR template at `templates/pr-performance-review.md` (in this skill folder) for any PR with non-trivial AL performance impact.

## Anti-patterns to call out

- Stringly-typed option fields where an enum would be safer
- Direct DB access from pages instead of via codeunits
- Caught-and-ignored errors
- Magic strings for codes (use constants or enums)
- `FindSet` loop with `CalcFields` of a FlowField inside
- Event subscribers doing extra DB reads on the hot path
- Large multi-purpose subscriber codeunits
- Deprecated `Promoted`, `PromotedCategory`, or `PromotedIsBig` action properties instead of `area(Promoted)` with `actionref` (§6.3)
- `ToolTip` or `ApplicationArea` repeated on a page field that already inherits them from the table field (§5.3, §6.1)
- A comma inside an enum value caption (§8)
- An `enum` whose first value is not `value(0; " ") { Caption = ' ', Locked = true; }`, or whose values start at 1 with no blank state (§8)
- Secrets in plain table fields instead of `SecretText` plus `IsolatedStorage` (§5.7, §9.3)

## PromptDialog and Copilot review

For any AL changes that touch a `PageType = PromptDialog`, also enforce these rules from `copilot-promptdialog`:

- `Extensible = false` is mandatory. Customers cannot extend Copilot pages.
- `Image = Sparkle` or `SparkleFilled` only. Other icons are non-standard.
- No repeater controls inside `area(Prompt)` or `area(Content)`.
- `area(PromptOptions)` accepts only option-type fields.
- Only the five sanctioned system actions: `Generate`, `Regenerate`, `Attach`, `OK`, `Cancel`. Reject custom system action names.
- **No trailing whitespace in action names.** Silently breaks Copilot. Caption can have trailing space, Name cannot.
- `PromptGuide` actions should each set the input variable to a templated text. They render only when `PromptMode = Prompt`.

For the AOAI codeunit behind the Copilot capability (`copilot-capability-implementation`):

- API key field must be `SecretText` type, not `Text`. `SecretText` is excluded from the debugger.
- Credentials stored via `IsolatedStorage`, or via AppSource Key Vault for marketplace apps.
- `AzureOpenAI.SetCopilotCapability(...)` must be called before `GenerateChatCompletion`.
- `RegisterCapability` must be wrapped in `IsSaaSInfrastructure()` and `IsCapabilityRegistered()` guards.
- Use `SetPrimarySystemMessage` for the metaprompt, not `AddSystemMessage`. PrimarySystemMessage persists across chat history.

## Related skills

- `copilot-promptdialog` for the full PromptDialog standard
- `copilot-capability-implementation` for the AL Copilot capability rules
