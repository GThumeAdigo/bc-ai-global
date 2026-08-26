# GAEB Interface: User Guide

How to import a GAEB XML exchange file into Business Central, review what the typed
population reached, read the bill of quantities, and complete the fill-in texts.

This guide is written step by step so it can be walked by a person or driven by the
`bc-webclient-runner` agent. Every step names a documented outcome under **Expected**.
Where an outcome depends on which GAEB file you imported, the step says so, and the
assertion is on the shape of the value rather than on a fixed number.

App: `ADIGO.BAU.Interfaces.GAEB`. Object prefix `GOXGAE`, ID range 71000 to 71999.

## 1. Before you start

1. Sign in to the sandbox and confirm the company in the URL is the one you intend to
   work in.
2. Confirm your user has the `GOXGAE FULL` permission set. `GOXGAE INDI` is the
   read-only companion; several actions in this guide write data and will fail under it.
3. Have a GAEB file ready. The repository ships samples in
   `ADIGO.BAU.Interfaces.GAEB/gaeb-files/`. Use `gaeb.x83` (about 54 KB) for a quick
   pass. `Wasserwerk_81-86/Bonner Wasserwerk (MWM-Muster) 1700 Positionen.x86` is the
   large-volume case and is slow.

**Expected:** the role centre loads without an error notification.

> The upload dialog filters on `*.xml` and `*.x80` through `*.x89` only. The `.p84`
> files in `gaeb-files/` are therefore not selectable in step 3.2 and are out of scope
> for this guide.

## 2. Set the number series

1. Open **Tell Me** and search for `GAEB Setup`. Open the page.
2. Read the **GAEB Nos.** field.
3. If it is blank, click the lookup on **GAEB Nos.** and select a number series.
4. Read the **Project Nos.** field. If it is blank, click its lookup and select a
   number series. It may be the same series as **GAEB Nos.** or a different one.

**Expected:**

- The **GAEB Setup** page opens as a card. It creates its own record on first open, so
  it never shows "there is no record".
- The lookup on **GAEB Nos.** opens a number-series list, and the selected value writes
  back into the field.
- **GAEB Nos.** holds a value before you continue. Import assigns the document number
  from this series.
- **Project Nos.** holds a value before you reach section 14. Creating a GAEB project
  takes its code from this series, and a blank **Project Nos.** makes project creation
  fail with a "must have a value" error rather than silently doing nothing.

## 3. Import a GAEB file

1. Open **Tell Me** and search for `GAEB Files`. Open the list.
2. Click **Import**. A file dialog opens, titled *Please select the GAEB XML file*.
3. Select `gaeb.x83` and confirm.

**Expected:**

- A message appears reading *GAEB file successfully imported. GAEB No.: <no>. <n>
  source value(s) could not be converted and were skipped. <n> source element(s) were
  not reached by the typed schema.* The two counts are file-dependent; assert the
  message shape and capture the numbers, do not assert fixed values.
- After dismissing the message, a new row is at the top of the list. The list sorts by
  **No.** descending, so the newest import is always first.
- The new row's **Population Status** reads `Populated`.

### 3.1 Negative case: a non-GAEB XML file

1. Click **Import** and select any well-formed XML file that is not a GAEB file.

**Expected:** an error, *The selected XML file is not a GAEB file.* No new row is added
to the list.

### 3.2 Negative case: cancelling the dialog

1. Click **Import** and cancel the file dialog.

**Expected:** a message, *No file was selected.* No new row is added.

## 4. Review the imported file in the list

1. On **GAEB Files**, look at the row you just imported.

**Expected:** the row shows these columns, all populated except where noted:

- **No.**, from the number series set in section 2.
- **File Name**, matching the file you selected.
- **Created At**, a date-time at or just before now.
- **Source Size**, non-zero, matching the file size in bytes.
- **Entry Count**, non-zero.
- **Population Status**, reading `Populated`.
- **Unconverted Value Count**, file-dependent, often zero.

The list is read-only. There is no New, Edit, or Delete, and the rows cannot be typed
into.

## 5. Open the GAEB File Card

1. Click the **No.** of the imported row to open the card.

**Expected:** the **GAEB File** card opens showing:

- A **General** group repeating **No.**, **File Name**, **Created At**, **Source Size**
  and **Entry Count** from the list, plus **Data Exchange Phase**. **Correlation ID** is
  an additional field and is hidden until you expand **Show more**.
- A **Typed Population** group with **Population Status** reading `Populated`,
  **Populated At** carrying a date-time, **Unconverted Value Count** and **Unreached
  Element Count**. **Population Diagnostic Category** and **Population Diagnostic
  Message** are additional fields, hidden until you expand **Show more**, and are blank
  on a successful import.
- Six parts below: **Exchange Info**, **Project Info**, **Award Info**, **Parties and
  Sites**, **Additional Texts**, **Bill of Quantities**.
- A **Project and Award Texts** FactBox on the right.

### 5.1 Non-zero counts are styled and drillable

1. If **Unconverted Value Count** or **Unreached Element Count** is non-zero, note its
   styling, then click the number.

**Expected:**

- A non-zero count renders in the Attention style (red). A zero count renders
  unstyled. This is the only visual signal that the population dropped something.
- Clicking a non-zero count drills into **GAEB Coverage Gaps**, the same page section
  10 reaches via the action.
- The card is read-only throughout. No field accepts input.

## 6. Read the project and award texts

1. Click **Show Project and Award Texts**.

**Expected:** one of two outcomes, depending on the file.

- If the file carries a project description or an award text, a modal **GAEB Text**
  viewer opens at full width showing the formatted text. Close it to return to the card.
- If it carries neither, a message reads *This GAEB file carries neither a project
  description nor an award text.* and no viewer opens.

The same text is rendered in the **Project and Award Texts** FactBox without opening the
viewer.

## 7. Walk the bill of quantities

1. Scroll to the **Bill of Quantities** part on the card.

**Expected:**

- The part lists the BoQ as an indented tree. **Outline Text** is the indentation
  column, so categories nest above their items.
- Each row shows **Ordinal No.**, **Node Kind**, **Outline Text**, **Quantity**,
  **Unit**, **Unit Price**, **Item Total**, and the three flags **Has Outline Text**,
  **Has Detail Text**, **Has Complements**.
- **Node Kind** reads one of `Category`, `Item`, `Remark`, `Sub-Description`.
- **Quantity**, **Unit Price** and **Item Total** are blank rather than `0` on rows that
  carry no value, including every `Category` row.
- A **Total** field sits below the list, showing the sum of the item totals.

### 7.1 Action availability follows the selected row

Select rows of different kinds and watch the four text actions. Their enabled state is
computed per row, so this is the highest-value check in this section.

1. Select a row where **Node Kind** is `Item` and **Has Outline Text** is ticked.

   **Expected:** **Show Outline Text** is enabled. **Show Category Label** is disabled.

2. Click **Show Outline Text**.

   **Expected:** a modal **GAEB Text** viewer opens with the formatted outline text.

3. Select a row where **Node Kind** is `Category` and **Has Outline Text** is ticked.

   **Expected:** **Show Category Label** is enabled and **Show Outline Text** is
   disabled. The two are mutually exclusive: a category has a label, an item has an
   outline text, and no row offers both.

4. Select a row where **Has Detail Text** is ticked.

   **Expected:** **Show Detail Text** is enabled. Clicking it opens the viewer with the
   detail text, pictures included.

5. Select a row where **Has Detail Text** is not ticked.

   **Expected:** **Show Detail Text** is disabled.

6. Select a row where **Has Complements** is ticked.

   **Expected:** **Text Complements** is enabled.

## 8. Open the bill of quantities with texts beside it

1. With any row selected, click **Open with Texts**.

**Expected:**

- A modal **GAEB Bill of Quantities** page opens with the same columns as the embedded
  part, plus a **Text of the Selected Line** FactBox on the right.
- Moving between rows updates the FactBox to the text of the newly selected line.
- This page deliberately does not repeat the **Total** field or the modal text-viewer
  actions. Their absence is correct, not a defect.
- **Text Complements** is present and is enabled only on rows where **Has Complements**
  is ticked.
- Closing the page returns you to the card.

## 9. Complete a text complement

Complements are the fill-in blanks a GAEB text carries. This is the only flow in the
guide that writes data.

1. Select a row where **Has Complements** is ticked and click **Text Complements**.

   **Expected:** a modal **GAEB Text Complements** list opens, one row per fill-in blank,
   showing **Text Kind**, **Complement Index**, **Caption Text**, **Body Text**, **Tail
   Text** and **Is Edited**. On a freshly imported file every **Is Edited** is
   unticked.

2. Select a complement and click **Edit**.

   **Expected:** a modal editor opens carrying the caption and the tail of the blank,
   with the body editable.

3. Change the body and confirm with **OK**.

   **Expected:** the list refreshes. The edited row now shows **Is Edited** ticked and
   its **Body Text** rendered in the Favorable style (green).

4. Click **Discard Edit** on that row.

   **Expected:** the row returns to **Is Edited** unticked, the body reverts to the
   imported text, and the Favorable styling is gone.

### 9.1 Cancelling leaves no trace

1. Click **Edit** on an unedited complement, change the body, then cancel the editor
   rather than confirming.

   **Expected:** **Is Edited** stays unticked. Cancelling stores nothing.

2. Click **Edit** on an unedited complement and confirm with **OK** without changing
   anything.

   **Expected:** **Is Edited** stays unticked. Opening and saving an unchanged
   complement is not an edit.

### 9.2 A line with no editable text

1. If you can reach **Text Complements** on a line carrying neither a detail text nor an
   outline text, click it.

   **Expected:** a message, *The selected line carries neither a detail text nor an
   outline text, so it has no fill-in texts to complete.* No list opens.

## 10. Inspect the coverage gaps

Coverage gaps are what the typed population did not reach. Reviewing them is how you
judge whether an import is trustworthy.

1. From the card, click **Show Coverage Gaps**. The same page is reachable from the
   **GAEB Files** list, and by clicking a non-zero count as in step 5.1.

**Expected:**

- A **GAEB Coverage Gaps** list opens showing **Kind**, **Element Name**, **Parent
  Table**, **Occurrence Count**, **Lost Element Count** and **In Document Namespace**.
  **Namespace URI** and **First Occurrence Path** are additional fields, hidden until
  you expand **Show more**.
- **Kind** reads one of `Unreached`, `Captured Markup`, `Leaf Children`.
- No row shows an element's value. The page reports structure, never customer data.
- The list is read-only.

2. Compare the counts to the card.

**Expected:** only `Unreached` rows feed **Unreached Element Count** on the card. The
three kinds are deliberately not summed, so the card count will be lower than the total
row count whenever `Captured Markup` or `Leaf Children` rows are present. A card count
that equals the sum of all three kinds is a defect.

## 11. Open the preserved XML source

1. Return to the card and click **Open XML Source**.

**Expected:** an XML document card opens showing the preserved source the typed data was
populated from, for the same document number you started on.

## 12. Re-populate the typed data

1. Return to the card and note the current **Populated At**.
2. Click **Populate Typed Data**.

**Expected:**

- The population runs again from the preserved source. No file dialog opens: this reads
  the stored source, it does not re-upload.
- **Populated At** advances to a later timestamp.
- **Population Status** still reads `Populated`.
- The **Bill of Quantities** part rebuilds and shows the same rows and the same
  **Total** as before. A re-population of an unchanged source that changes the totals is
  a defect.
- Any text complement edits you made in section 9 survive. They live in an overlay
  keyed on the source document, not in the populated rows.

## 13. Assign a file to a new GAEB project

A GAEB project groups the files of one exchange across their phases. Membership is
optional: a file that belongs to no project behaves exactly as it did before.

1. Open **GAEB Files** and import `Wasserwerk_81-86/X81_Bonner_Wasserwerk_MWM-Muster.xml`
   as in section 3.
2. Select that row. The import leaves the selection on the row you had before, so
   click the new file explicitly rather than assuming it is selected.
3. Click **Assign to Project**.
4. In the dialog, expand the **Assignment** group if it is collapsed. Leave **Existing
   Project** blank and confirm with **OK**.

**Expected:**

- A dialog opens titled *Assign GAEB File to Project*, showing the file's **No.** and
  **File Name** read-only.
- The **Proposal** group is expanded on first open and the **Assignment** group is
  collapsed. Business Central remembers the expanded state afterwards, so this is a
  first-open detail rather than a permanent one.
- The **Proposal** text reads *No existing GAEB project matches this file. Confirm to
  create a new one from the file's own header, or pick an existing project.* This is the
  expected text on a clean company, because no project exists yet.
- **Existing Project** is blank, and **New Project Description** is prefilled with
  `Bonner Wasserwerk`, taken from the file's GAEB project name.
- After **OK**, the file's **GAEB Project** column on the list holds a project code from
  the **Project Nos.** series.

## 14. Assign a second file to the same project

1. Import `Wasserwerk_81-86/X83_Bonner_Wasserwerk_MWM-Muster.xml`.
2. Select it and click **Assign to Project**.

**Expected:**

- The **Proposal** text now reads *GAEB project <code> (Bonner Wasserwerk) matches this
  file. Confirm to assign it, or pick a different project.*
- **Existing Project** is prefilled with that project's code. The match is on the GAEB
  project name, which both files carry; neither file carries an award number or a DP
  number, so the weaker hints are not what matched.
- Confirming with **OK** assigns the second file to the **same** project, not a new one.
- Importing `x83bsp.X83` and repeating this step proposes a **new** project instead,
  because its project name is `BVBS GAEB Muster` and matches nothing existing.

## 15. Read the project card and set a file's lineage

1. With a file of the project selected in **GAEB Files**, click **Open Project**.
2. Expand the **Matching Hints** group and the **GAEB Files** part if they are
   collapsed. Both render collapsed on first open.

**Expected:**

- A **GAEB Project** card opens with three groups: **General** (**Code**,
  **Description**), **GAEB Identity** (**GAEB Project ID**, **Project ID Origin**) and
  **Matching Hints** (**Project Name**, **Award No.**, **DP No.**).
- **GAEB Project ID** is a non-blank 32-character value and **Project ID Origin** reads
  `Generated`, because the uploaded files carried no project id of their own.
- The **GAEB Files** part lists both files with their **Exchange Phase** (`81` and
  `83`), **Created At**, **Population Status** and **Superseded By**. The same value is
  captioned **Data Exchange Phase** on the GAEB File card, and **Datenaustauschphase**
  in a German session.
- Selecting the phase-83 row and clicking **Set Derived From** opens a list of the
  project's other files. Picking the phase-81 file writes it into **Derived From**.
- **Clear Derived From** empties it again.
- The card also carries **Add GAEB Files**, which picks up files belonging to no
  project, and the files part carries **Remove from Project**.

> **Lineage across projects cannot be attempted from this screen, by design.** The
> **Set Derived From** lookup is pre-filtered to the selected file's own project, so a
> file of a different project is never offered. The rule that refuses it
> (*GAEB file <a> cannot be recorded as the origin of GAEB file <b>, because lineage is
> only valid between two files of the same GAEB project.*) is enforced in the seam as
> defence in depth for a future caller, and is not reachable from the client.

## 16. A re-imported file archives the one it duplicates

1. Import `WG_ Testprojekt Sachsenmilch/LV_Los03_Technische Anlagen_ELT.X83`.
2. Import `WG_ Testprojekt Sachsenmilch/LV_Los03_Technische Anlagen_ELT[1].X83`, which
   is byte-for-byte identical to the first.

**Expected:**

- Both imports succeed with the usual message. The second import does **not** refuse.
- Only **one** of the two rows remains in **GAEB Files**: the first file is archived and
  leaves the list. Neither file needs to belong to a project for this to happen, because
  the rule that fires here is the byte-identity rule, not the project rule.
- The four Wasserwerk files, by contrast, archive **none** of each other even in one
  project, because their exchange phases differ.

## 17. Show, unarchive and delete an archived file

1. In **GAEB Files**, click **Show Archived**.

**Expected:**

- A modal **Archived GAEB Files** page opens listing only archived files.
- The archived `LV_Los03` row shows **Superseded By** holding the newer file's number,
  and **Archive Reason** reading *Superseded by the newer GAEB file <no>.* A file you
  archived by hand instead reads *Archived by a user.*
- **Unarchive** returns the file to **GAEB Files** and changes nothing else about it:
  its typed data, its viewer and its population outcome are as they were.
- **Delete** asks first, naming the file: *Delete GAEB file <no> (<file name>)
  permanently? Its preserved XML source, typed GAEB data, coverage gaps, text overlays
  and text complements are all removed and cannot be recovered.* Answering **No**
  changes nothing.
- Answering **Yes** removes the row. Every other file still opens and still shows its
  bill of quantities.
- A file that is **not** archived cannot be deleted. There is no delete action on
  **GAEB Files** at all, and the table refuses the deletion even if it is reached
  another way.

## 18. A file that states its own project id joins without asking

The corpus contains no file carrying a `PrjID`, so this section uses two prepared
fixtures. Both carry the same id,
`4F2C1A9B7D3E48F0A1B2C3D4E5F60717`.

1. Import `gaeb-files/017-prjid-X81_Bonner_Wasserwerk.X81`.
2. Import `gaeb-files/017-prjid-X83_Bonner_Wasserwerk.X83`.

**Expected:**

- Neither import shows an assignment dialog. The import flow is unchanged: the same
  success message and nothing else.
- After the first import, a **new** GAEB project exists whose **GAEB Project ID** is
  `4F2C1A9B7D3E48F0A1B2C3D4E5F60717` and whose **Project ID Origin** reads `From File`,
  not `Generated`.
- After the second import, both files are in **that same project**, visible as the
  **GAEB Project** column on **GAEB Files** and as two rows on the project card.
- Neither file archives the other: their phases are `81` and `83`.

## 19. The project id survives a re-population

1. Open the card of a file that belongs to a project and note its **GAEB Project ID**.
2. Click **Populate Typed Data**.

**Expected:**

- **Populated At** advances, as in section 12.
- **GAEB Project ID** on the card still shows the same value afterwards. Re-population
  rebuilds the typed rows from the preserved source, which carries no id, so the value
  being present afterwards is the point of the check. A blank here is a defect.
- **Project ID Backfilled** still reads the same as before.

## 20. Deleting a project keeps its files

1. Open a GAEB project card and click **Delete Project**.

**Expected:**

- A confirmation names the project and says what happens: *GAEB project <code> has <n>
  file(s). Deleting the project leaves every one of them imported, populated and usable,
  merely unassigned. No GAEB file is deleted. Delete the project?*
- Answering **Yes** closes the card. The project is gone from **GAEB Projects**.
- Every file that belonged to it is still in **GAEB Files**, still opens, still shows its
  bill of quantities, and now has a blank **GAEB Project**.
- Renaming a project's **Description** instead changes no assignment and no suggestion.

---

## Notes for automated runners

Read this before driving the guide with `bc-webclient-runner`.

**The delayed-insert check does not apply to the file pages.** Every GAEB **file** page
in this guide is `Editable = false` with insert, modify and delete disabled, so the
"type into the first non-PK field and tab off" probe in the agent's check 8 has nothing
to run against there. The **GAEB Project** card (section 15) *is* editable, and its
**Description** is the one field that probe applies to.

**Lookup probing targets.** The writable fields in this guide are **GAEB Nos.** and
**Project Nos.** on **GAEB Setup** (steps 2.3 and 2.4), **Existing Project** on the
assignment dialog (section 13), and **Description** on the project card. Everything
else is read-only, so the agent's check 7 should be scoped to those.

**Sections 13 to 20 need sections 2 and 3 to have run first**, and section 2 must have
set **Project Nos.**, or project creation fails with a "must have a value" error that
is correct behaviour rather than a defect.

**Project codes and GAEB project ids are generated. Do not assert fixed values** for
**Code** on a GAEB project, or for **GAEB Project ID** where **Project ID Origin** reads
`Generated`. Capture them and assert their relationships: that the second file of
section 14 receives the *same* project code as the first, and that the id in section 19
is *unchanged* across the re-population. The one id you may assert literally is
`4F2C1A9B7D3E48F0A1B2C3D4E5F60717` in section 18, because the fixtures state it.

**Section 16 depends on two files being byte-identical.** If the run reports that the
second `LV_Los03` import did not archive the first, compare their md5 and check the two
files are still identical before reporting an app defect.

**Import needs file upload, not typing.** Step 3.2 opens a real browser file dialog via
`UploadIntoStream`. Drive it with `browser_file_upload`, pointing at an absolute path
under `ADIGO.BAU.Interfaces.GAEB/gaeb-files/`. The dialog cannot be satisfied by typing
a path into the page.

**These values are file-dependent. Do not assert fixed numbers:** the two counts in the
import success message, **Source Size**, **Entry Count**, **Unconverted Value Count**,
**Unreached Element Count**, the BoQ row count, and **Total**. Capture them and assert
their shape and their relationships, for example that **Total** is unchanged across the
re-population in section 12.

**State labels to check for drift.** **Population Status** renders `Populated` or
`Failed`. **Node Kind** renders `Category`, `Item`, `Remark` or `Sub-Description`.
**Kind** on the coverage gaps page renders `Unreached`, `Captured Markup` or `Leaf
Children`. **Project ID Origin** renders `From File` or `Generated`. **Exchange Phase**
renders a GAEB phase such as `81`, `83`, `84` or `86`. Each enum also carries a blank
value that should not appear on a populated document. A displayed value outside these
sets is label drift.

**This guide is written for an English session.** The app ships a complete de-DE
translation, so a German session renders the same controls as **GAEB-Projekt**,
**Projekt zuordnen**, **Projekt öffnen**, **Archivieren**, **Archivierte anzeigen**,
**Archivierung aufheben**, **Löschen**, **Herkunft der Projekt-ID** (*Aus Datei* /
*Generiert*), **Projekt-ID nachgetragen**, **Ersetzt durch** and
**Archivierungsgrund**. Those are translations, not drift.

**Known caption defect, pre-existing and not this feature's.** On **GAEB Files**, on the
project card's files part and on the **GAEB File** card, the population columns render
their raw control names (`PopulationStatus`, `UnconvertedValueCount`, `PopulatedAt`,
`UnreachedElementCount`, `PopulationDiagnosticCategory`, `PopulationDiagnosticMessage`)
instead of captions, because a page field bound to a variable inherits no caption from
the table. The values are correct. Report it once, not per screen.

**Sections 3.1, 3.2, 9.1, 9.2 and the refusals in 15 and 17 are negative cases.** The
documented outcome is an error, a confirmation or a message. Reaching it is a pass, not
a failure.

**Deleting is destructive and ordered last for that reason.** Section 17's delete
removes a file permanently. Run it on the archived `LV_Los03` duplicate, which is a
redundant copy by construction, and not on a file another section still needs.
