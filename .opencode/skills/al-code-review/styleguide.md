# AL Style Guide for Microsoft Dynamics 365 Business Central

A comprehensive coding style guide for the AL programming language. This guide consolidates project conventions, community best practices from [alguidelines.dev](https://alguidelines.dev/), and Microsoft recommendations.

---

## 0. Quick Rules

Critical constraints at a glance. Each links to its detailed section.

1. **Prefix** every custom object with the project prefix (e.g. `GOXOUT`); object names ≤ 30 chars. (§2.1)
2. **PascalCase** for objects, variables, and procedures; suffix variables with the type/object name; prefix temp records with `Temp`. (§2.3)
3. **File name = object name**: `<ObjectName>.<ObjectType>.al`. (§2.2)
4. **Namespace first**, then `using` statements, at the top of every file. (§3.3)
5. **Organize by feature**, not object type; use `#region` blocks consistently. (§3.1, §3.2)
5a. **Any object must be findable from folder names alone.** Number only the top-level feature spine, in data-flow order; subfolders are plain topic names. Subdivide a folder when it holds more than about five objects of one type **and** a real topic exists; if it does not, leave it flat and say why. (§3.1)
6. **Declare variables** in type order (Record → Codeunit → … → simple types). (§4)
7. **Table fields** own their `Caption` + `ToolTip`; pages inherit them — don't repeat on pages. (§5.2, §5.3)
8. Set `ApplicationArea` **at page level only**. (§6.1)
9. **Promoted actions**: `area(Promoted)` + `actionref` only — never deprecated `Promoted*` properties. (§6.3)
10. **One codeunit = one purpose = exactly ONE public procedure**, `local` procedures below; extensible operations follow the `OnBefore`/`IsHandled`/`Do…`/`OnAfter` skeleton. The sole exception is a **helper** codeunit, which groups small related procedures for one topic and **must** carry the `Helper` suffix. (§7.1, §7.2)
10a. **Never name a codeunit `… Mgt` / `… Management` / `… Utils`** or any other custody-of-a-topic word: name the job it does. `Helper` is the only permitted grouping suffix. (§2.1)
10b. **Split codeunits over 600 lines**, by responsibility cluster and never at an arbitrary line count; 400–600 needs a justification. (§7.1)
11. **Never hardcode UI strings** — use `Label` variables; every enum starts with `value(0; " ")` and no enum caption contains a comma. (§8, §9)
12. Store secrets with `SecretText` + `IsolatedStorage`; never in plain fields. (§5.7, §9.3)
13. Declare **explicit `Permissions`** (least privilege) on every codeunit that touches tables. (§10)
14. Raise errors via **`GOXFOU Error`** (`FOUError.Call(...)`), never bare `Error()`. (§11)
15. Always set the **`RunTrigger`** parameter explicitly on `Insert`/`Modify`/`Delete`. (§12.1)
16. Use **`SetLoadFields()`**, early filtering, and `CalcSums`/`Count` over manual loops. (§12.2)
17. **XML-document** all public/internal procedures; avoid regular `//` comments — let names and structure explain the code. Summaries are **1–2 sentences**; never reference specs, features, or tasks in docs. (§14)
18. **4-space indent**, lowercase keywords, compact `{ }` for property-less elements. (§15)
19. Compile with **zero warnings** (CodeCop + LinterCop); enable `NoImplicitWith` + `TranslationFile` in `app.json`. (§1)
20. `this` self-reference requires **runtime 13.0+** (BC 2024 wave 2). (§5.6)

---

## 1. General Principles

- Write **self-documenting code** through clear naming. Avoid regular `//` comments: extract a named procedure or variable instead. Keep the required `///` XML documentation on internal and global procedures, and keep it off `local procedure` (see Section 14).
- Follow **SOLID principles** adapted for AL (see Section 13).
- Prefer **extensibility** through events, interfaces, and table/page extensions over modifying base objects.
- Keep procedures **small and focused** — one responsibility per procedure.
- Always compile with **zero warnings** using CodeCop and LinterCop analyzers.
- Enable `NoImplicitWith` and `TranslationFile` in the `features` array of `app.json`.
- Use `area(Promoted)` with `actionref` for promoted actions — never the deprecated `Promoted*` action properties (see Section 6.3).

---

## 2. Naming Conventions

### 2.1 Object Names

- Use **PascalCase** for all object names.
- Prefix all custom objects with the project-specific prefix (e.g., `GOX`, `GOXOUT`).
- Object names must not exceed **30 characters** total (including prefix), leaving room for prefix + space.
- Use descriptive, business-oriented names — avoid abbreviations unless they are well-known BC terms.

```al
// Good
table 87700 "GOXOUT Setup"
page 87701 "GOXOUT Outlook Entry List"
codeunit 87707 "GOXOUT CreateEntry"
enum 87702 "GOXOUT Sensitivity"

// Bad
table 87700 "GOXOUT Setup Table Configuration"  // Too long
page 87701 "GOXOUT OEList"                       // Too abbreviated
```

#### Banned codeunit name suffixes

A codeunit name states **the one job the codeunit does**. Names that describe a
custodial relationship to a topic rather than an action are banned, because they
name no boundary and so nothing is ever out of scope for them. In practice they
become the file every new procedure gets appended to.

- **Never** `Mgt`, `Mgt.`, `Management`, `Manager`, `Mngt`.
- **Never** `Utils`, `Utilities`, `Misc`, `Common`, `General`, `Functions`,
  `Library`, `Tools`, `Stuff`.
- `Helper` is the **only** permitted grouping suffix, and it is not a
  free pass: it carries the specific meaning defined in §7.2 and is allowed
  only for codeunits that meet that definition.

```al
// Bad — names a topic to be curated, not a job to be done
codeunit 87707 "GOXOUT Entry Mgt"
codeunit 87708 "GOXOUT Outlook Management"
codeunit 87709 "GOXOUT Graph Utils"

// Good — names the job, one per codeunit
codeunit 87707 "GOXOUT Create Entry"
codeunit 87708 "GOXOUT Cancel Entry"
codeunit 87709 "GOXOUT Entry Lineage"

// Good — a genuine helper under §7.2, suffix required
codeunit 87710 "GOXOUT Graph Client Helper"
```

Prefer a **verb-led or noun-phrase-of-one-job** name: `Create Entry`,
`Cancel Import`, `Resolve Project`, `BoQ View Builder`, `Markup Renderer`.
If you cannot name the codeunit without a banned suffix, that is the signal that
it has more than one responsibility. Split it (§7.1) instead of naming around it.

### 2.2 File Names

- Pattern: `<ObjectName>.<ObjectType>.al`
- The file name must match the AL object name within the file.
- Use PascalCase for file names, matching the object name exactly.

```
GOXOUTSetup.Table.al
GOXOUTOutlookEntryList.Page.al
GOXOUTCreateEntry.Codeunit.al
GOXOUTSensitivity.Enum.al
GOXOUTApplicationAreaSetup.TableExt.al
```

### 2.3 Variables and Procedures

- Use **PascalCase** for variable and procedure names.
- Use descriptive names — avoid single letters except for loop counters (`i`, `j`).
- Suffix object-type variables with the object name (CodeCop AA0072), e.g. `Record Customer` → `Customer`, `Codeunit "GOXOUT CreateEntry"` → `CreateEntry`.
- Prefix temporary records with `Temp` (e.g. `TempOutlookEntry`).
- Do not use abbreviations unless they are well-known BC terms (see [Suggested Abbreviations](https://alguidelines.dev/docs/bestpractices/suggested-abbreviations/)).

```al
// Good
var
    OutlookEntry: Record "GOXOUT Outlook Entry";
    OrganizerMailbox: Text;
    JsonBody: JsonObject;

// Bad
var
    OE: Record "GOXOUT Outlook Entry";    // Too abbreviated
    mb: Text;                               // Not PascalCase
```

### 2.4 Label Variable Naming

Use descriptive suffixes to indicate the purpose of label variables:

| Suffix   | Purpose                        | Example                          |
|----------|--------------------------------|----------------------------------|
| `Err`    | Error messages                 | `SetupNotEnabledErr`             |
| `Msg`    | User messages (informational)  | `ConnectionSuccessMsg`           |
| `Tok`    | Token constants (URLs, etc.)   | `EventsEndpointTok`              |
| `Lbl`    | General labels (UI text)       | `SecretSetLbl`                   |
| `Qst`    | Confirm questions              | `DeleteEntryQst`                 |

### 2.5 Interface and Implementation Naming

- Prefix interfaces with `I` (e.g., `IItemPriceCalculator`).
- In apps with a mandatory object prefix, the object prefix comes first and the
  `I` joins the name without a space (e.g., `GOXGAE IFormatImport`).
- Use `Impl` suffix for implementation codeunits (e.g., `Item Price Calc. Impl`).
- Keep interface and implementation names closely related.

---

## 3. Code Organization

### 3.1 Folder Structure

**A reader who does not know the app should find any object by reading folder
names alone.** That is the whole test. Everything below serves it.

Organize by **business feature**, not by object type. A feature folder holds the
table, its pages, its enums and its codeunits together, because that is the unit
a developer works on.

```
src/
├── .Extensions/              # Table and page extensions
├── .Installation/            # Install codeunits, permission sets, profiles
│   ├── App/
│   ├── Permissions/
│   └── RoleCenter/
├── .Subscriber/              # Event subscriber codeunits
└── OUT/                      # Feature area: Outlook Interface
    ├── 01 Setup/             # Setup table, page, install trigger
    ├── 02 Authentication/    # OAuth2 authentication
    ├── 03 OutlookEntry/      # Outlook entry table, pages, enums
    └── 04 GraphClient/       # Graph API client, helpers
```

Folders prefixed with a dot sort to the top and hold what cuts across every
feature: extensions, installation, subscribers.

#### The numbered spine

Number the **top-level feature folders** so they read in the order the data
actually flows (receive, store, process, present, export), not alphabetically.
The numbers are the app's story; a newcomer reads them top to bottom and learns
the pipeline.

- **Numbering stops at the spine.** Every folder below a numbered one is a plain
  unnumbered topic name. Do not number subfolders: they have no delivery order
  to express, and the numbers become a second thing to maintain.
- **Leave gaps** (`01`, `02`, `04`) rather than renumbering when a stage is
  removed. Renumbering rewrites paths across the repo and breaks every reference
  in a spec or a commit message for no gain.

#### When to add a subfolder

Split a folder when **both** hold:

1. It contains **more than about five objects of the same type**, and
2. a topic is **genuinely findable** from the file names.

The second condition is the one that gets skipped, and it is the one that
matters. **If no honest topic exists, leave the folder flat.** A long list is
merely tedious; a wrong grouping is actively harmful, because it sends a reader
confidently to the wrong place and they conclude the object does not exist.

When you leave a folder flat despite it being over the threshold, **say so and
say why** in the app's context notes, so the next person does not redo the
analysis or read it as an oversight.

#### Subfolder patterns that work

- **By topic**, the default. Group the objects that serve one job:
  `Queue/`, `Job Queue Runners/`, `Intake/`, `Notifications/`.
- **`Helpers/`** when a folder carries roughly four or more `… Helper`
  codeunits (§7.2). This is the most common split in a mature app, because
  helpers accumulate around a feature faster than anything else.
- **By object type** when a folder is genuinely mixed and one type dominates:
  a `Codeunits/` folder beside the tables and pages. Reach for this only when a
  topic split is not available; type is a weaker organizing idea than purpose.
- **By object shape** for large generated or schema-mirroring sets, where the
  shape is unambiguous: `Cards/` and `Lists/`.
- **Domain first, shape second** for a large mirrored object set: split by the
  business domain the objects belong to, then by shape inside it. This scales
  where a single axis does not.

#### Deriving a grouping, not guessing it

When the grouping is not obvious from the names, **derive it from the code**
rather than inferring it from the identifier. For example, to file a set of
enums by domain, find which table references each enum and take that table's
domain. A derived grouping is defensible and reproducible; a grouping guessed
from a name is the wrong-grouping failure above, arrived at with more
confidence.

If you cannot derive it cheaply, that is evidence the topic is not there. Leave
it flat.

#### Practical notes

- **AL binds nothing to folders.** The compiler scans the source tree
  recursively and namespaces are declared in the file (§3.3), so moving a file
  between folders cannot break the build. Folder structure is purely for human
  navigation, which means it is cheap to improve and there is no excuse for
  leaving it bad.
- **Move with `git mv`**, not delete-plus-add, so history follows the file.
- **Revisit the structure after a refactor that adds objects.** The threshold
  above is crossed silently: no build fails, no analyzer complains, and the
  folder is simply harder to read every week.

### 3.2 Region-Based Code Structure

Use `#region` / `#endregion` to organize code within AL objects. Maintain consistent region names across objects of the same type.

**Tables:**
```al
table 87701 "GOXOUT Outlook Entry"
{
    #region Object
    // Caption, DataClassification, DrillDownPageId, etc.
    #endregion Object

    #region Fields
    fields { ... }
    #endregion Fields

    #region Keys
    keys { ... }
    #endregion Keys

    #region FieldGroups
    fieldgroups { ... }
    #endregion FieldGroups

    #region Procedures
    // Table procedures
    #endregion Procedures

    #region Var
    var
    #endregion Var
}
```

**Pages:**
```al
page 87701 "GOXOUT Outlook Entry List"
{
    #region Object
    // ApplicationArea, Caption, SourceTable, PageType, etc.
    #endregion Object

    #region Layout
    layout { ... }
    #endregion Layout

    #region Actions
    actions { ... }
    #endregion Actions

    #region Trigger
    trigger OnAfterGetRecord() { ... }
    #endregion Trigger

    #region Work
    // Local helper procedures
    #endregion Work

    #region Var
    var
    #endregion Var
}
```

**Codeunits:**
```al
codeunit 87707 "GOXOUT CreateEntry"
{
    #region Object
    // Access, Permissions, SingleInstance
    #endregion Object

    #region Call
    // Main entry point procedure(s)
    #endregion Call

    #region Public
    // Public procedures (if any, for helper codeunits)
    #endregion Public

    #region Work
    // Local implementation procedures
    #endregion Work

    #region Var
    var
    // Label variables, tokens
    #endregion Var
}
```

**Subscriber codeunits** — use regions named after the source object/event:
```al
codeunit 87712 "GOXOUT Subscriber Codeunits"
{
    SingleInstance = true;

    #region codeunit 9178 "Application Area Mgmt."
    [EventSubscriber(ObjectType::Codeunit, Codeunit::"Application Area Mgmt.", OnGetEssentialExperienceAppAreas, '', false, false)]
    local procedure ApplicationAreaMgmt_OnGetEssentialExperienceAppAreas(...)
    #endregion codeunit 9178 "Application Area Mgmt."
}
```

### 3.3 Namespace and Using

- Always declare the namespace as the first line of every `.al` file.
- Place `using` statements immediately after the namespace.
- Use dot-separated namespaces matching the project structure.

```al
namespace ADIGO.ITS.Interfaces.Outlook;

using System.Security.Authentication;
using ADIGO.ITS.Basics.Foundation;
```

---

## 4. Variable Declaration Order

Declare variables in the following order (per [alguidelines.dev](https://alguidelines.dev/docs/bestpractices/variables-declarations-order/) and Microsoft CodeCop AA0021):

1. Record
2. Report
3. Codeunit
4. XmlPort
5. Page
6. Query
7. Notification
8. BigText
9. DateFormula
10. RecordId / RecordRef / FieldRef
11. FilterPageBuilder
12. Simple types (Text, Code, Decimal, Integer, Boolean, etc.)
13. .NET / DotNet types (if used)

```al
var
    OutlookEntry: Record "GOXOUT Outlook Entry";
    Setup: Record "GOXOUT Setup";
    EntryHelper: Codeunit "GOXOUT Entry Helper";
    GraphClient: Codeunit "GOXOUT GraphClient Helper";
    JsonBody: JsonObject;
    ResponseJson: JsonObject;
    OrganizerMailbox: Text;
    Endpoint: Text;
```

---

## 5. Tables

### 5.1 Table Properties

- Always set `Caption` and `DataClassification`.
- Set `DrillDownPageId` and `LookupPageId` to the appropriate pages.
- Set `Extensible = true` on tables intended for extension by other apps.
- Use `Permissions` on tables that need to read their own or related data.

```al
table 87700 "GOXOUT Setup"
{
    #region Object
    Caption = 'Outlook Interface Setup';
    DataClassification = CustomerContent;
    DrillDownPageId = "GOXOUT Setup";
    LookupPageId = "GOXOUT Setup";
    Extensible = true;
    Permissions = tabledata "GOXOUT Setup" = r;
    #endregion Object
```

### 5.2 Fields

- Use field IDs with **gaps** (1, 10, 20, 30...) to leave room for future fields.
- Start the primary key field at ID 1.
- Group related fields by ID range (e.g., 30-31 for start/end, 200-220 for sync metadata, 300-303 for source references).
- Every field **must** have `Caption` and `ToolTip` defined in the table.
- Set `DataClassification` when the table-level classification doesn't apply.
- Use `Editable = false` for system-managed fields.
- Use `AllowInCustomizations = Never` for fields that should never be exposed in customizations (e.g., primary key, auto-increment fields).

```al
field(1; "Entry No."; Integer)
{
    Caption = 'Entry No.';
    ToolTip = 'Specifies the entry number.';
    AutoIncrement = true;
    AllowInCustomizations = Never;
}

field(210; "Sync Status"; Enum "GOXOUT Sync Status")
{
    Caption = 'Sync Status';
    ToolTip = 'Specifies the synchronization status of the calendar event.';
    Editable = false;
}
```

### 5.3 ToolTip Best Practices

- **ToolTips for table fields belong in the table definition**, NOT on pages.
- Pages automatically inherit ToolTips from table fields.
- Only add ToolTips on pages for: actions, variable-bound fields, and calculated fields.
- ToolTips should be descriptive and start with a verb like "Specifies...", "Indicates...", "Shows...".

### 5.4 Keys

- Name keys descriptively: `key(PK; ...)`, `key(Source; ...)`.
- Use compact one-line syntax for simple keys.

```al
keys
{
    key(PK; "Entry No.") { Clustered = true; }
    key(Source; "Source Table ID", "Source System ID") { }
}
```

### 5.5 FieldGroups

- Define `DropDown` and `Brick` fieldgroups for better UX in lookups and tiles.

```al
fieldgroups
{
    fieldgroup(DropDown; "Entry No.", Subject, "Organizer Email") { }
    fieldgroup(Brick; "Entry No.", Subject, "Start DateTime", "Sync Status") { }
}
```

### 5.6 Table Procedures

- Tables can contain procedures for entity operations (e.g., `GetThis()`, `SetClientSecret()`).
- Use `this.` prefix when referencing the current record instance within table procedures.
- Provide XML documentation on all internal and global procedures, never on `local procedure` (§14.1).

> **Runtime requirement:** The `this` self-reference keyword requires **runtime 13.0 (BC 2024 wave 2)**
> or later and is supported on all object types. Ensure `app.json` targets a compatible `runtime`.

```al
/// <summary>
/// Retrieves the setup record. Throws an error if the setup record does not exist.
/// </summary>
/// <returns>The setup record.</returns>
procedure GetThis(): Record "GOXOUT Setup"
begin
    if not this.Get() then
        Error(this.RecordNotFoundErr);
    exit(this);
end;
```

### 5.7 Setup Table Pattern

- Use a single-row setup table with `"Primary Key"` field of `Code[10]`.
- Provide a `GetThis()` procedure that throws a meaningful error if the record doesn't exist.
- Store secrets in `IsolatedStorage` using `SecretText` — never in plain fields.

```al
procedure SetClientSecret(SecretValue: SecretText)
begin
    if IsNullGuid(this."Client Secret Key") then
        this."Client Secret Key" := CreateGuid();
    IsolatedStorage.Set(this."Client Secret Key", SecretValue, DataScope::Module);
end;

procedure GetClientSecret() SecretValue: SecretText
begin
    if IsNullGuid(this."Client Secret Key") then
        exit;
    if not IsolatedStorage.Get(this."Client Secret Key", DataScope::Module, SecretValue) then
        exit;
end;
```

---

## 6. Pages

### 6.1 Page Properties

- Define `ApplicationArea` **at the page level only**. Individual elements inherit from the page.
- Only set `ApplicationArea` on individual elements when it differs from the page-level value.
- Set `Caption`, `PageType`, `SourceTable`, and `UsageCategory` appropriately.
- Set `Extensible = true` on pages intended for extension.
- Use `DeleteAllowed = false` and `InsertAllowed = false` on setup pages.

```al
page 87700 "GOXOUT Setup"
{
    ApplicationArea = GOXOUTOutlookSetup;
    Caption = 'Outlook Interface Setup';
    SourceTable = "GOXOUT Setup";
    PageType = Card;
    UsageCategory = Administration;
    Extensible = true;
    DeleteAllowed = false;
    InsertAllowed = false;
```

### 6.2 Layout

- Group fields logically using `group()` with `Caption`.
- Use `Importance = Additional` for less important fields.
- Do NOT repeat `ToolTip` or `ApplicationArea` on fields that reference table fields — they are inherited.
- Use compact one-line syntax for simple field references: `field("No."; Rec."No.") { }`
- Use multi-line syntax when properties need to be set (StyleExpr, Visible, Editable, Importance).

```al
layout
{
    area(Content)
    {
        group(General)
        {
            Caption = 'General';
            field(Enabled; Rec.Enabled) { }
        }
        group(AzureAD)
        {
            Caption = 'Azure AD';
            field("Tenant ID"; Rec."Tenant ID") { }
            field("Client Secret Status"; this.ClientSecretStatusTxt)
            {
                Caption = 'Client Secret';
                ToolTip = 'Specifies whether a client secret has been configured.';
                Editable = false;
            }
        }
    }
}
```

### 6.3 Actions

- **Always** use `area(Promoted)` with `actionref` — never use deprecated `Promoted`, `PromotedCategory`, or `PromotedIsBig` properties.
- Name actionrefs with the pattern `<ActionName>_Promoted` or `<ActionName>Ref`.
- Every action must have `Caption`, `ToolTip`, and `Image`.
- Use `ShortCutKey` for common actions (e.g., `F9` for Post).

```al
actions
{
    area(Processing)
    {
        action(CreateInOutlook)
        {
            Caption = 'Create in Outlook';
            ToolTip = 'Creates the selected calendar event in Outlook via Microsoft Graph.';
            Image = SendTo;

            trigger OnAction()
            var
                CreateEntry: Codeunit "GOXOUT CreateEntry";
            begin
                CreateEntry.Call(Rec);
                CurrPage.Update(false);
            end;
        }
    }
    area(Promoted)
    {
        actionref(CreateInOutlookRef; CreateInOutlook) { }
    }
}
```

### 6.4 Triggers

- Place triggers in a dedicated `#region Trigger`.
- Keep trigger logic minimal — delegate to codeunits or local procedures.

```al
trigger OnOpenPage()
begin
    Rec.Reset();
    if not Rec.Get() then begin
        Rec.Init();
        Rec.Insert(true);
    end;
    this.UpdateClientSecretStatus();
end;
```

---

## 7. Codeunits

### 7.1 Business Operation Codeunits

Each codeunit has **ONE clear business purpose** with a single entry point:

- **Exactly ONE public procedure** as the entry point. Not "few", not "mostly
  one": one. Name it `Call` when the operation has no better name, otherwise
  name it for the job (`Enqueue`, `Resolve`, `BuildLines`).
- **Only `local` procedures below** for breaking down complex logic.
- Sort procedures in the order they are called, starting with the entry point.
- Move small helper functions to separate helper codeunits (§7.2).

The only codeunits allowed more than one public procedure are **helper
codeunits**, which must carry the `Helper` suffix (§7.2). If a codeunit has two
public procedures and is not a helper, one of three things is true, and the fix
differs:

1. **The extra procedure has no external caller.** Demote it to
   `local procedure`. Check every call site before demoting; this is the most
   common case and it costs nothing.
2. **The extra procedure is a second job.** Move it to its own codeunit. Two
   entry points mean two responsibilities, whatever the file name says.
3. **The extra procedure is a variant of the first.** Merge them into one
   procedure with a parameter, or make the caller's case the only case.

A stateful builder that genuinely needs a `Set…`/`Build`/`Get…` lifecycle, or a
`Codeunit.Run`-driven unit that needs a context setter beside `OnRun`, is a
recognised exception. State the reason in the entry point's `///` block so the
next reader does not have to rediscover it.

#### Size budget

A codeunit is a unit of comprehension, not a container. Treat these as review
thresholds, not as hard compiler limits:

| Lines | Verdict |
|---|---|
| under 200 | fine |
| 200 to 400 | acceptable; look for a seam before adding to it |
| 400 to 600 | a finding: name the clusters and say why they must stay together |
| over 600 | split it |

Length is the symptom, not the disease. Do not split a long codeunit at an
arbitrary line count into `…Part1` / `…Part2`: find the **responsibility
clusters** (groups of local procedures that only talk to each other and to one
slice of the state) and give each cluster its own codeunit with a name that says
what it does. If a cluster cannot be named without a banned suffix (§2.1), it is
not a cluster.

Two shapes are worth splitting on sight, because they hide in a line count:

- **A wide dispatch `case`** over dozens of branches. Group the branches by
  domain, give each group its own codeunit with the same entry-point signature,
  and leave the parent as a short chain over the groups.
- **A large block of pure lookups or predicates** with no access to the
  surrounding state. That is a helper (§7.2) that has not been extracted yet.

```al
codeunit 87707 "GOXOUT CreateEntry"
{
    #region Object
    Permissions = tabledata "GOXOUT Outlook Entry" = m;
    #endregion Object

    #region Call

    /// <summary>
    /// Creates an Outlook calendar event from the given Outlook Entry record via Microsoft Graph.
    /// </summary>
    /// <param name="OutlookEntry">The Outlook Entry record to create.</param>
    procedure Call(var OutlookEntry: Record "GOXOUT Outlook Entry")
    var
        Setup: Record "GOXOUT Setup";
        EntryHelper: Codeunit "GOXOUT Entry Helper";
        GraphClient: Codeunit "GOXOUT GraphClient Helper";
        JsonBody: JsonObject;
        ResponseJson: JsonObject;
    begin
        Setup := Setup.GetThis();
        this.ValidateSetupEnabled(Setup);
        this.ValidateCreateAllowed(OutlookEntry);

        // ... main business logic ...

        OutlookEntry.Modify(false);
    end;

    #endregion Call

    #region Work

    local procedure ValidateSetupEnabled(Setup: Record "GOXOUT Setup")
    begin
        if not Setup.Enabled then
            Error(this.SetupNotEnabledErr);
    end;

    #endregion Work

    #region Var
    var
        SetupNotEnabledErr: Label 'The Outlook interface is not enabled. Please enable it in the Outlook Setup.';
    #endregion Var
}
```

**Standard `Call` skeleton.** When the operation is extensible, keep `Call` as a
thin orchestrator: raise the `OnBefore` event with an `IsHandled` flag, exit when
a subscriber handled the work, delegate the real work to a `local procedure Do<Name>`,
then raise the `OnAfter` event. `Call` itself holds no business logic.

```al
codeunit 87707 "GOXOUT CreateEntry"
{
    #region Call

    /// <summary>
    /// Creates the Outlook calendar event for the given entry code.
    /// </summary>
    /// <param name="BOXCode">The entry code to create the calendar event for.</param>
    procedure Call(var BOXCode: Code[20])
    var
        IsHandled: Boolean;
    begin
        this.OnBeforeCall(BOXCode, IsHandled);
        if IsHandled then
            exit;

        this.DoCall(BOXCode);
        this.OnAfterCall(BOXCode);
    end;

    #endregion Call

    #region Work

    local procedure DoCall(var BOXCode: Code[20])
    begin
        // ... main business logic ...
    end;

    #endregion Work

    #region Events

    [IntegrationEvent(false, false)]
    local procedure OnBeforeCall(var BOXCode: Code[20]; var IsHandled: Boolean)
    begin
    end;

    [IntegrationEvent(false, false)]
    local procedure OnAfterCall(var BOXCode: Code[20])
    begin
    end;

    #endregion Events
}
```

Rules for this skeleton:

- The `OnBefore` event is always the first statement, and `IsHandled` is checked
  immediately after it. A handled call exits without raising `OnAfter`.
- Pass `IsHandled` by reference (`var`), and never reuse it for anything else.
- The work procedure is `local` and named `Do` plus the entry point name (`DoCall`).
- Only raise `OnAfter` when the work actually ran.
- See §13.2 for when to publish these events at all.

### 7.2 Helper Codeunits

A helper codeunit groups several **small, related** helping procedures that all
serve one process or one topic, where each on its own would be too small to
justify a codeunit. It is the single exception to the one-public-procedure rule
of §7.1.

**The `Helper` suffix is mandatory.** A codeunit with more than one public
procedure and no `Helper` suffix is a finding, and so is a codeunit named
`… Helper` that is not one. The suffix is the contract: it tells a reader that
the several public procedures are deliberate, and it tells a reviewer that the
one-public-procedure rule was considered rather than forgotten.

A codeunit qualifies as a helper when **all** of these hold:

- Its public procedures are small (roughly under 30 lines each) and each does
  one narrow thing: a lookup, an accessor, a predicate, a format, a small write.
- **None of them orchestrates the others.** There is no entry point, no sequence,
  no "call this first". If one public procedure calls another, or the caller must
  call them in a fixed order, that is an orchestrator with leaked internals
  (§7.1 case 1), not a helper.
- They belong to one named process or topic, and the name says which.
- Removing any one of them would not change what the codeunit is for.

Counter-examples, which look like helpers and are not:

- A **state machine** (a set of `Mark…` / `Set…` transitions guarding an
  invariant). It has one responsibility and a real contract; name it for that.
- A **lifecycle** (`Open` / `Step` / `Close`, `SetContext` / `Run`). The order is
  the point, so it is one job with several entry points; document the reason in
  the `///` block per §7.1.
- A **bag of leftovers** from several processes that happen to be read by the
  same page. Split it by process; a shared consumer is not a shared topic.

Other rules:

- Set `Access = Internal` on helper codeunits that should only be used within the app.
- Helper codeunits use `internal procedure` or `procedure` methods.
- Each procedure has a single, focused responsibility.
- A helper is still bound by the §7.1 size budget. A helper over 400 lines is
  usually two topics.

```al
codeunit 87706 "GOXOUT Graph Client Helper"
{
    Access = Internal;

    internal procedure Post(Endpoint: Text; JsonBody: JsonObject; var ResponseJson: JsonObject): Boolean
    begin
        exit(this.SendRequest('POST', Endpoint, JsonBody, ResponseJson));
    end;

    internal procedure GetLastErrorMessage(): Text
    begin
        exit(this.LastErrorMessage);
    end;
}
```

### 7.3 Subscriber Codeunits

- Use `SingleInstance = true` on subscriber codeunits.
- Group subscribers by source object using `#region` with the object name.
- Use descriptive parameter names — avoid generic `Rec` when a specific name is clearer.
- Keep subscriber logic minimal — delegate to a dedicated codeunit.

```al
codeunit 87712 "GOXOUT Subscriber Codeunits"
{
    SingleInstance = true;

    #region codeunit 9178 "Application Area Mgmt."
    [EventSubscriber(ObjectType::Codeunit, Codeunit::"Application Area Mgmt.", OnGetEssentialExperienceAppAreas, '', false, false)]
    local procedure ApplicationAreaMgmt_OnGetEssentialExperienceAppAreas(var TempApplicationAreaSetup: Record "Application Area Setup" temporary)
    var
        ExtensionOnSetAreas: Codeunit "GOXOUT App SetAreas";
    begin
        ExtensionOnSetAreas.Call(TempApplicationAreaSetup);
    end;
    #endregion codeunit 9178 "Application Area Mgmt."
}
```

### 7.4 Table Extension as Entity Function Library

- Table extensions can contain multiple `internal procedure` methods that serve as entity function gateways.
- Each procedure should **delegate** to a focused codeunit — no complex business logic in table extensions.
- Provide complete XML documentation on every internal and global procedure, never on `local procedure` (§14.1).

```al
tableextension 87700 "GOXOUT Project Extension" extends "Project"
{
    fields { ... }

    /// <summary>
    /// Gets the responsible resource for time capture for the specified project.
    /// </summary>
    internal procedure GetResponsibleResourceForTimeCapture(ProjectNo: Code[20]): Code[20]
    begin
        exit(GetRespTimeCaptureCodeunit.GetResponsibleResourceForTimeCapture(ProjectNo));
    end;

    var
        GetRespTimeCaptureCodeunit: Codeunit "GOX Get Resp. Time Capture";
}
```

---

## 8. Enums

- Set `Extensible = true` on enums intended for extension.
- **Always** declare `value(0; " ")` as the first value, with a locked blank caption, so
  the enum has an explicit "not set" state. A record whose enum field was never filled
  in reads as blank rather than silently landing on the first real value, and filters,
  validation, and required-field checks can test for it. New enum values start at 1 or
  above, never at 0. (This applies to the enum itself; an `enumextension` never adds a
  blank value, the base enum already owns 0.)
- Use value ID gaps (0, 1, 10, 20, 30...).
- Each value must have a `Caption`.
- **Never** put a comma inside an enum value caption — commas break UI display and value evaluation (AL0649 / AppSourceCop AS0087).

```al
enum 87702 "GOXOUT Sensitivity"
{
    Extensible = true;

    value(0; " ") { Caption = ' ', Locked = true; }
    value(1; Normal) { Caption = 'Normal'; }
    value(10; Personal) { Caption = 'Personal'; }
    value(20; Private) { Caption = 'Private'; }
    value(30; Confidential) { Caption = 'Confidential'; }
}
```

> Note: `Caption = ' ', Locked = true;` is a single property statement — `Locked` is a
> comma-separated *parameter* of the `Caption` property (same as for Labels), and the
> whole statement ends with a semicolon.

---

## 9. Labels and Text Constants

### 9.1 Label Syntax

- Use `Label` variables (not `TextConst`) for all user-facing text.
- Place all label variables in the `#region Var` section at the bottom of the object.
- Use the suffix conventions from Section 2.4.
- Add `Comment` property for labels with placeholders (`%1`, `%2`, etc.) to guide translators.
- Use `Locked = true` for non-translatable text (URLs, HTTP status codes, API field names).

```al
var
    EventsEndpointTok: Label 'https://graph.microsoft.com/v1.0/users/%1/events', Locked = true;
    SetupNotEnabledErr: Label 'The Outlook interface is not enabled. Please enable it in the Outlook Setup.';
    CreateFailedDetailedErr: Label 'Failed to create the calendar event in Outlook. %1', Comment = '%1 = error message from the Graph client.';
    ConnectionSuccessMsg: Label 'Connection successful. Access token acquired.';
```

### 9.2 Never Hardcode Strings

- **Never** use hardcoded strings in `Error()`, `Message()`, or `Confirm()` calls.
- Always use label variables to ensure proper localization via XLF translation files.
- Use the `GOXFOU Error` codeunit (see Section 11) for raising errors instead of calling `Error()` directly.

```al
// Good - via GOXFOU Error
FOUError.Call(this.SetupNotEnabledErr);

// Bad - hardcoded string
Error('The Outlook interface is not enabled.');
```

### 9.3 SecretText

- Use `SecretText` type for any sensitive data (tokens, passwords, secrets).
- Use `SecretStrSubstNo` instead of `StrSubstNo` when substituting secret values.
- Never log or display secret text values.

---

## 10. Permissions

### 10.1 Object-Level Permissions

- All codeunits that access tables **must** declare explicit `Permissions` property.
- Use the **minimum required permissions** (principle of least privilege).
- Permission letters: `r` (read), `i` (insert), `m` (modify), `d` (delete), `x` (execute).
- Combine as needed: `rim`, `rimd`, `r`.

| Operation | Code | Example methods |
|-----------|------|-----------------|
| Read | `r` | `Get()`, `FindFirst()`, `FindSet()`, `SetRange()` |
| Insert | `i` | `Insert()`, `Init()` + `Insert()` |
| Modify | `m` | `Modify()`, `Modify(true)` |
| Delete | `d` | `Delete()`, `DeleteAll()` |

```al
codeunit 87707 "GOXOUT CreateEntry"
{
    Permissions = tabledata "GOXOUT Outlook Entry" = m;
}

codeunit 52100 "GOX Service Reference Mgmt."
{
    Permissions = tabledata "GOX Service Reference" = r,
                  tabledata "G/L Account" = r,
                  tabledata "Sales Header" = r,
                  tabledata "Sales Line" = rm;
}
```

### 10.2 Analyzing Required Permissions

Review all procedures in the codeunit and identify:
1. Which tables are accessed.
2. What operations are performed (Read/Insert/Modify/Delete).
3. Add the appropriate `tabledata` permission for each table.

---

## 11. Error Handling

### 11.1 GOXFOU Error — Centralized Error Handler

All ADIGO apps depend on the **ADIGO.ITS.Basics.Foundation** app, which provides the `GOXFOU Error` codeunit (`codeunit 81015`). This is the **standard way to raise errors** across all ADIGO AL projects. Use it instead of calling `Error()` directly.

The `GOXFOU Error` codeunit creates collectible `ErrorInfo` objects with `ErrorType::Client` and `Verbosity::Error`, providing consistent error behavior and enabling error collection patterns.

**Two call signatures:**

| Signature | Purpose |
|-----------|---------|
| `Call(ErrorText: Text)` | Raise an error with a pre-formatted message |
| `Call(NotFoundTable: Text; NotFoundKey: Text)` | Raise a "record not found" error — auto-formats as `'<Table> <Key> was not found.'` |

### 11.2 Declaring the Error Handler Variable

Declare `GOXFOU Error` as a local variable where the error is raised, or as a global variable on tables that need error handling in multiple procedures:

```al
// As a local variable in a procedure
var
    FOUError: Codeunit "GOXFOU Error";

// As a global variable on a table
var
    FOUError: Codeunit "GOXFOU Error";
```

### 11.3 Usage Patterns

**Pre-formatted error message** — define the label locally, pass the formatted text:

```al
local procedure GetCurrencyCode(var Currency: Record Currency; CurrencyCode: Code[10])
var
    FOUError: Codeunit "GOXFOU Error";
    CurrencyNotFoundErr: Label 'Currency ''%1'' was not found.', Comment = '%1 = Currency';
begin
    if not Currency.Get(CurrencyCode) then
        FOUError.Call(StrSubstNo(CurrencyNotFoundErr, CurrencyCode));
    Currency.TestField("Amount Rounding Precision");
end;
```

**Direct label (no placeholders)** — pass the label variable directly:

```al
internal procedure SendAndValidateHttpRequest(var HttpRequest: HttpRequestMessage) HttpResponse: HttpResponseMessage
var
    GOXFOUError: Codeunit "GOXFOU Error";
    AzureConnectionErr: Label 'Failed connection to Azure. Please check your internet connection.';
    ErrorRetrievalOrganisationsMsg: Label 'Failed to retrieve Organisations from DevOps User.';
    HttpClient: HttpClient;
begin
    if not HttpClient.Send(HttpRequest, HttpResponse) then
        GOXFOUError.Call(AzureConnectionErr);
    if not HttpResponse.IsSuccessStatusCode() then
        GOXFOUError.Call(StrSubstNo(ErrorRetrievalOrganisationsMsg));
end;
```

**Record not found pattern** — pass table caption and key, auto-formatted by the codeunit:

```al
procedure GetThis(): Record "GOXOUT Setup"
begin
    if not this.Get() then
        this.FOUError.Call(Rec.TableCaption(), '');
    exit(this);
end;

// With a composite key
procedure GetThis(ID: Code[50]; RecID: RecordId; GetError: Boolean): Record "GOXFOU My Record"
var
    FOUError: Codeunit "GOXFOU Error";
begin
    if not this.Get(ID, RecID) then
        if GetError then
            FOUError.Call(this.TableCaption(), ID + '/' + Format(RecID));
end;
```

### 11.4 When to Use GOXFOU Error vs. Other Patterns

| Scenario | Approach |
|----------|----------|
| Validation errors, not-found errors, business rule violations | `FOUError.Call(...)` — standard approach |
| Non-fatal operations that should not roll back the caller | `Codeunit.Run()` with error handling, or `TryFunction` |
| External service errors that should be stored, not thrown | Capture error text, store on record, continue execution |

**External service error storage** — when calling external APIs, store the error on the record instead of throwing, so the user can see what went wrong and retry:

```al
if GraphClient.Post(Endpoint, JsonBody, ResponseJson) then begin
    OutlookEntry."Sync Status" := OutlookEntry."Sync Status"::Synced;
    OutlookEntry."Last Error Message" := '';
end else begin
    OutlookEntry."Sync Status" := OutlookEntry."Sync Status"::Error;
    OutlookEntry."Last Error Message" := CopyStr(
        StrSubstNo(this.CreateFailedDetailedErr, GraphClient.GetLastErrorMessage()),
        1, MaxStrLen(OutlookEntry."Last Error Message"));
end;
```

### 11.5 Error Message Quality

- Provide **meaningful context** — include relevant identifiers (record numbers, codes, names) in error messages.
- Use **label variables** with `Comment` property for placeholders (see Section 9).
- Do **not** pass raw hardcoded strings to `FOUError.Call()` — always use label variables.

---

## 12. Performance

### 12.1 Explicit RunTrigger Parameter

Always explicitly set the `RunTrigger` parameter on built-in record methods:

```al
OutlookEntry.Modify(false);   // RunTrigger = false
OutlookEntry.Modify(true);    // RunTrigger = true
OutlookEntry.Insert(true);    // RunTrigger = true
OutlookEntry.Delete(true);    // RunTrigger = true
```

### 12.2 Data Retrieval

- Use `SetLoadFields()` before `Get()` or `Find...()` to load only needed fields.
- Use `SetRange()` / `SetFilter()` **before** retrieving records to filter early.
- Use `FindFirst()` / `FindLast()` for single records, `FindSet()` for iteration.
- Use `CalcSums()` / `CalcFields()` for aggregation instead of manual loops.
- Use temporary tables, dictionaries, and lists for in-memory processing.
- Use `Count()` instead of looping and incrementing a counter.

```al
// Good - SetLoadFields before Find
Item.SetRange("Third Party Item Exists", false);
Item.SetLoadFields("Item Category Code");
Item.FindFirst();

// Good - CalcSums instead of loop
CustLedgerEntry.SetRange("Customer No.", CustomerNo);
CustLedgerEntry.CalcSums(Amount);
exit(CustLedgerEntry.Amount);
```

### 12.3 Loop Best Practices

- Extract business logic inside loops into local procedures for readability.
- Minimize database access inside loops.
- Use `repeat ... until Next() = 0` for record iteration.

---

## 13. SOLID Principles in AL

### 13.1 Single Responsibility (SRP)

- Each codeunit has **ONE clear business purpose**, expressed as **exactly one
  public procedure** (§7.1). The count of public procedures is the cheapest
  measurable proxy for SRP in AL: two entry points are two responsibilities.
- The one exception is a **helper codeunit**, which must carry the `Helper`
  suffix (§7.2).
- Each procedure has **ONE specific responsibility**.
- Move helper functions to separate helper codeunits.
- Table extensions serve as entity function gateways — delegate to focused codeunits.
- The codeunit **name** is part of the principle: a name that describes custody
  of a topic (`… Mgt`, `… Management`, `… Utils`) admits any responsibility and
  is banned (§2.1). Name the job.
- Respect the §7.1 size budget. A codeunit that has grown past 600 lines has
  almost always acquired a second responsibility on the way.

### 13.2 Open/Closed (OCP)

- Extend functionality through **events** without modifying existing code.
- Use **table extensions** and **page extensions** instead of modifying base objects.
- Publish integration events at key extensibility points.

```al
codeunit 87707 "GOXOUT CreateEntry"
{
    procedure Call(var OutlookEntry: Record "GOXOUT Outlook Entry")
    begin
        OnBeforeCreateEntry(OutlookEntry);
        // ... core logic ...
        OnAfterCreateEntry(OutlookEntry);
    end;

    [IntegrationEvent(false, false)]
    local procedure OnBeforeCreateEntry(var OutlookEntry: Record "GOXOUT Outlook Entry")
    begin
    end;

    [IntegrationEvent(false, false)]
    local procedure OnAfterCreateEntry(var OutlookEntry: Record "GOXOUT Outlook Entry")
    begin
    end;
}
```

### 13.3 Liskov Substitution (LSP)

- All implementations of an interface must honor the contract.
- Interface implementations must return expected types and behave consistently.

### 13.4 Interface Segregation (ISP)

- Create **small, focused interfaces** rather than large general ones.
- Each object should depend only on interfaces it actually uses.

```al
interface "Time Entry Validator"
{
    procedure ValidateEntry(TimeEntry: Record "Project Journal Line"): Boolean;
}

interface "Time Entry Calculator"
{
    procedure CalculateCost(TimeEntry: Record "Project Journal Line"): Decimal;
}
```

### 13.5 Dependency Inversion (DIP)

- Depend on **abstractions** (interfaces, setup tables) not hard-coded values.
- Use **setup tables** for configuration instead of hard-coded rules.
- Use **events** to decouple components.
- Avoid direct coupling between business logic codeunits — use interfaces or events.

---

## 14. Documentation and Comments

### 14.1 XML Documentation

- Add XML documentation (`/// <summary>`, `/// <param>`, `/// <returns>`) on **every
  `internal procedure` and every global procedure** (a `procedure` declared without
  `local`, including `protected`). These form the object's callable surface.
- **Never** put XML documentation on a `local procedure`. A local helper is an
  implementation detail: its name carries its meaning (§7.2, §14.2). Documenting it
  duplicates the name and rots. The same holds for triggers, `OnRun`, event
  publishers, and event subscriber procedures, which are always documented by their
  signature and attribute, not by a `///` block.
- Clearly explain the business purpose in the summary.
- Describe all parameters and return values.

#### Summary conciseness

A summary is precise, not exhaustive. **One or two sentences** is the target;
more is justified only when the procedure is genuinely complicated (a
multi-step state transition, a non-obvious caller contract). Rule of thumb:
under about 35 words; a hard case may reach three short sentences, never more.

**Cut on sight:**

- Restated parameter or return docs; the `<param>` and `<returns>` tags own
  them.
- Narration of what the next statement does.
- Inventories of call sites, dependants, or affected callers. Stale the day a
  caller is added. State the constraint instead.
- A guard described on the wrong object; a publisher does not document its
  caller's transition rules.
- A sentence repeated on every procedure of an object; it belongs in the
  object-level summary once, or nowhere.

**Keep, compressed to one sentence:**

- What the procedure does, in the caller's terms.
- A constraint a caller can violate (must be idempotent, cannot run inside a
  TryFunction, must commit first).
- A platform behavior not inferable from the signature.
- A named hazard with its consequence.

#### No workflow artifacts in documentation

Documentation comments must not reference the development process: feature
numbers (`feature 023`), spec or plan file names (`spec.md`, `plan.md`,
`tasks.md`, `validation.md`, `tech-design.md`, `specs/`, `roadmap.md`),
acceptance-criterion or task identifiers (`AC 4`, `Task T12`, `D2/D4`). The
specs are not part of the PR, so every one of these is a dangling pointer for a
reviewer. State the fact without the citation:

- `which feature 023 refused` becomes `which is not permitted`
- `the ID window declared in specs/tech-design.md` becomes `the typed-table ID
  window`
- `feature 023 plan.md D2 and D4 hold the reasoning` becomes: delete the
  clause, and move the reasoning into the feature's `plan.md` if it exists
  nowhere else.

`feature` is an ordinary domain word ("the specified feature of the project
line" is not a spec reference), and `AC0032`-style ids inside pragma
justifications are AppSourceCop rule ids, not acceptance criteria. Read each
hit before editing it.

```al
/// <summary>
/// Creates an Outlook calendar event from the given Outlook Entry record via Microsoft Graph.
/// </summary>
/// <param name="OutlookEntry">The Outlook Entry record to create.</param>
procedure Call(var OutlookEntry: Record "GOXOUT Outlook Entry")
```

```al
// Bad - a local helper does not get XML documentation; the name is the documentation
/// <summary>
/// Validates that the setup is enabled.
/// </summary>
local procedure ValidateSetupEnabled(Setup: Record "GOXOUT Setup")

// Good
local procedure ValidateSetupEnabled(Setup: Record "GOXOUT Setup")
```

### 14.2 Avoid Regular Comments

Regular comments (`//`, `/* */`) are to be avoided. The code carries its own
explanation through its structure and its object, procedure, and variable names.
A comment that restates what the code does is duplicated logic that rots as soon
as the code changes.

This rule does **not** apply to XML documentation comments (`///`) on internal and
global procedures (see §14.1). Those are required and must be left in place. On a
`local procedure` there is nothing to leave in place: `///` blocks do not belong
there either.

When you feel the urge to write a `//` comment, do this instead:

- **Name the thing.** Extract the commented block into a `local procedure` whose
  name says what the comment said. (§7.1, §7.2)
- **Name the value.** Replace a magic value or an opaque expression with a
  descriptively named local variable or a `Label`. (§2.3, §9)
- **Use a region.** Group related members with a `#region` block instead of a
  banner comment. (§3.2)

```al
// Bad - the comment carries the meaning the code should carry
procedure Call(var OutlookEntry: Record "GOXOUT Outlook Entry")
begin
    // check that the entry is not already synced
    if OutlookEntry."Sync Status" = OutlookEntry."Sync Status"::Synced then
        exit;

    // build the graph request and send it
    RequestBody := BuildBody(OutlookEntry);
    HttpClient.Post(GraphEventsUrlLbl, RequestBody, Response);
end;

// Good - names replace the comments
procedure Call(var OutlookEntry: Record "GOXOUT Outlook Entry")
begin
    if IsAlreadySynced(OutlookEntry) then
        exit;

    SendCreateEventRequest(OutlookEntry);
end;
```

One narrow exception, and only one:

- Compiler and tooling **pragmas** and directives (for example
  `#pragma warning disable`) are not prose comments, so the rule does not remove
  them. But a pragma suppresses a rule the analyzers were told to enforce, so it
  **must** carry a comment stating why the suppression is justified, and the
  scope must be reopened as soon as possible with `#pragma warning restore`.

A "genuine why" is **not** an exception in this repo. A rationale that cannot be
expressed through a name (a platform quirk, a rejected alternative, an accepted
trade-off) goes in the feature `plan.md` or in the `///` block of the nearest
internal procedure, where it is durable and reviewable. See the comment policy in
`AGENTS.md`, which governs.

```al
// Bad - a naked suppression, nobody can tell whether it is still needed
#pragma warning disable AA0210
Rec.SetRange("Sync Status", Rec."Sync Status"::Pending);
#pragma warning restore AA0210

// Good - the reason is on the record, and the scope is minimal
// AA0210 disabled: "Sync Status" has no key by design, the table stays under
// a few hundred rows and an extra key would cost more than the scan saves.
#pragma warning disable AA0210
Rec.SetRange("Sync Status", Rec."Sync Status"::Pending);
#pragma warning restore AA0210
```

Never leave commented-out code in the codebase. Delete it; version control is
the history.

---

## 15. Formatting and Readability

### 15.1 Indentation and Spacing

- Use **4 spaces** for indentation (project standard in `.vscode/settings.json`).
- One statement per line.
- Place binary operators at the **start of the next line** when wrapping.
- Place `begin` on the same line as the statement, or on the next line for procedure bodies.
- Use `begin ... end` only for compound statements (multi-line).

### 15.2 Compact Syntax

Use compact one-line syntax for simple, property-less elements:

```al
// Compact - no properties needed
field("Entry No."; Rec."Entry No.") { }
field(Subject; Rec.Subject) { }

// Multi-line - when properties are needed
field("Sync Status"; Rec."Sync Status")
{
    StyleExpr = SyncStatusStyleExpr;
}
```

### 15.3 Blank Lines

- Use blank lines to separate logical sections within procedures.
- Do NOT use blank lines at the start or end of `begin ... end` blocks.
- Do NOT use blank lines between consecutive single-line field declarations in a repeater.

### 15.4 Explicit Object References

AL does not support named arguments, so make intent clear by using fully qualified
object references (`Codeunit::"..."`, `Page::"..."`) and descriptive local variables
instead of passing bare values:

```al
// Clear intent - qualified reference
Codeunit.Run(Codeunit::"GOXOUT CreateEntry", OutlookEntry);

// Prefer a typed variable + Call() for readability
CreateEntry.Call(OutlookEntry);
```

---

## 16. Commit Messages

- Keep commit messages **short and precise**: a one-line subject that names the
  change in imperative mood (for example `Cancel running imports from the file
  card`). Add a short body only when a reviewer genuinely needs the why.
- **No workflow artifacts in commit messages**: no feature numbers
  (`feature 023`), no spec or plan file names (`spec.md`, `plan.md`,
  `tasks.md`, `validation.md`, `tech-design.md`, `specs/`, `roadmap.md`), no
  acceptance-criterion or task identifiers (`AC 4`, `Task T12`, `D2/D4`), and
  no references to agent sessions or reviews. A commit message ships in the
  repository history and a reviewer cannot open the artifacts it cites. State
  the change and, when needed, the reason in domain terms.
- The reasoning that motivated the change belongs in the feature `plan.md` or
  the `///` block of the nearest internal procedure (§14.1), not in the commit
  message.

---

## 17. Additional Resources

- [alguidelines.dev](https://alguidelines.dev/) — Community design patterns and best practices
- [alguidelines.dev Vibe Coding Rules](https://alguidelines.dev/docs/agentic-coding/vibe-coding-rules/) — AI-optimized AL coding rules
- [Microsoft AL Documentation](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-dev-overview)
- [AL Best Practices](https://alguidelines.dev/docs/bestpractices/) — Detailed best practice articles
- [Suggested Abbreviations](https://alguidelines.dev/docs/bestpractices/suggested-abbreviations/) — Standard BC abbreviations
