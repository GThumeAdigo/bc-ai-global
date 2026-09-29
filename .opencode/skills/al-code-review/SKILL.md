---
name: al-code-review
description: Authoring essentials and scoped house-rule review for AL. Load before writing AL, then only the applicable style guide and domain sections.
---

# AL authoring and review essentials

## Authorities

`styleguide.md` owns the numbered local coding conventions. App-specific
identifiers and architecture come from `APP_CONTEXT.md` and product decisions;
GOX names are examples, not a requirement on every app. BCQuality owns reusable
domain knowledge. Microsoft Learn and the installed symbols establish platform
API behavior and version support. The SDD router owns review/approval/stopping.

Read applicable sections, not the entire guide for every change:

| Changed concern | Style sections / additional source |
|---|---|
| Naming, organization, variables | 2–4 |
| Tables, pages, enums | 5, 6, 8 |
| Business operations and subscribers | 7; selected subscriber contract |
| Labels, secrets, permissions, errors | 9–11 |
| Data access and performance | 12–13; worklisted BCQuality performance rules |
| Documentation and readability | 14–15 |
| Integration, upgrades, Copilot | Applicable corpus action/knowledge, not generic checklists |

## While authoring

- Reuse existing standard BC behavior and app patterns after inspecting callers.
- Resolve object ranges and namespaces from the actual app. Avoid guessed IDs,
  public contracts and API guarantees. Use semantic navigation for AL.
- Preserve transaction/trigger behavior deliberately; make RunTrigger intent
  explicit. Check failure and retry paths where behavior changes.
- Keep responsibilities and names understandable. Size/complexity thresholds are
  investigation cues, not permission for unrequested splits or abstractions.
- Follow the app's error/telemetry boundaries. Protected-operation telemetry must
  have an observable assertion seam when that policy applies to the app.
- Keep user strings translatable and explain label placeholders. Resolve locale
  coverage only for affected strings/locales, not as a full release audit.
- Use least-privilege permission intent and verify real company/tenant boundaries.
- API **queries** cannot use `ODataKeyFields`; this is not a ban on API pages.
  Use compiler diagnostics for property applicability and Learn for API design.
- Verify uncertain platform behavior before relying on it, particularly boundary
  semantics. Evidence can be reused while API version and relevant inputs remain
  unchanged; no repeated lookup solely to satisfy a ritual.

## While reviewing

Review changed scope and affected callers. Do not repeat compiler/analyzer
findings already represented in evidence. Classify new versus baseline findings.
Model-estimated complexity is judgment, not deterministic measurement.

Report a blocking defect only with concrete impact and an acceptance, platform
or explicit app-rule basis. Naming preferences, line-count heuristics and proposed
IDataAccess abstractions are advisory unless the app actually mandates them.
Recognize the style guide's stateful lifecycle exceptions; avoid flattening them
into a generic one-public-procedure rule. Do not demand an abstraction absent from
the app's architecture merely because a corpus example uses it.

For corpus findings cite corpus-relative knowledge paths. House findings name
the authoritative style section and remain separate from BCQuality DO references.
Use SDD's evidence and confirmation contract rather than maintaining another
reviewer-set or waiver policy in this file.
