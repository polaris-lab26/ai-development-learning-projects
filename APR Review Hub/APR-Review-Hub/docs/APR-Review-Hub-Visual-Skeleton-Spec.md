# GCF APR Review Hub: Visual Skeleton Specification

**Author:** TR  
**Status:** Revision 2.4 (20 Nov 2026). As-built visual specification for the Week Six demonstrator.
**Scope:** Student demonstrator for CA2. Not an official GCF system or a commercial product. All data shown is invented.
**Purpose:** describe the four-screen visual skeleton and its Week Six accessibility expectations. The Flask app is a demonstrator: it has no database, sign-in or persistence. A valid submission or decision displays a message but does not change the sample data. Authentication, storage and real workflow are later work.

---

## 1. Application overview

The APR Review Hub supports one simple workflow for Annual Performance Reports (APRs):

1. A **Project Officer** prepares and submits an APR.
2. A **Programme Manager** reviews the submission.
3. The Programme Manager either **approves** it or **returns it with a comment**.
4. The Project Officer can **amend and resubmit** a returned report.
5. In the intended system, each action is recorded. In this visual demonstrator, the activity shown is invented and no new action is saved.

Two roles only. No attachments, messaging, reminders, analytics or other roles.

### Report statuses

Three statuses, each shown as **text plus an icon shape**, never colour alone. There is no Draft status in the initial MVP (see D1):

| Status | Meaning | Icon (with text label) | Accent colour |
|---|---|---|---|
| Submitted | Waiting for Programme Manager review | ● circle | Espresso outline |
| Returned | Sent back with a comment; Officer must amend | ↩ return arrow | Terracotta |
| Approved | Accepted by Programme Manager | ✓ tick | Green (icon and outline); label text in green |

---

## 2. Proposed navigation structure

A single role-aware top navigation bar (collapses to a menu button on small screens). The current page is marked with `aria-current="page"`. A separate “Demonstration only” bar switches the displayed sample role with `?role=manager`; it is not authentication.

| Nav item | Project Officer | Programme Manager |
|---|---|---|
| Dashboard | Yes | Yes |
| Submit Report | Yes | Hidden |
| Report History | Yes (own reports) | Yes (all reports) |
| Report Review | Not in nav | Not in nav (opened from a queue item) |

- **Report Review** is not a menu item because it always applies to one specific report. The Programme Manager reaches it from the Dashboard queue or from Report History.
- The bar shows the selected sample person's name and role as text. There is no sign-out link or sign-in.

**Key navigation paths**

- Officer: Dashboard → *Submit new report* → Submit Report → back to Dashboard with a confirmation message.
- Officer: Dashboard → *Amend and resubmit* on a Returned report → Submit Report (pre-filled, showing the return comment).
- Manager: Dashboard → *Review* on a Submitted report → Report Review → Approve or Return → back to Dashboard.
- Either role: Dashboard or History → *View history* on a report → Report History (that report expanded).

---

## 3. Screen-by-screen specification

### 3.1 Dashboard

| | |
|---|---|
| **Purpose** | A calm starting point showing what needs the person's attention now. |
| **Access** | Both roles. Content differs by role. |
| **Main information** | **Officer:** a short list of their own reports with title, reporting year, status, last updated. Returned reports are listed first with the Manager's comment preview. **Manager:** a "Waiting for review" list of Submitted reports with title, officer name, submitted date. Below it, a short "Recently decided" list. Both roles see simple count tiles (e.g. "2 Submitted, 1 Returned, 3 Approved"). Counts only, no charts. |
| **Main actions** | Officer: *Submit new report*; *Amend and resubmit* (Returned reports). Manager: *Review* (Submitted reports). Both: *View history*. |
| **Navigation links** | Submit Report, Report Review, Report History, and the top nav. |
| **Accessibility and usability** | Single `<h1>`; lists as real tables or lists; status shown as icon plus word; empty states in plain words ("No reports are waiting for review."); the primary action is the most visually prominent element. |

### 3.2 Submit Report

| | |
|---|---|
| **Purpose** | Let the Officer prepare and submit a new APR, or amend and resubmit a returned one. |
| **Access** | Project Officer only. A Manager who opens the address directly sees a plain "This page is for Project Officers" message with a link back to the Dashboard. |
| **Main information** | A single-column form with labelled fields: Project name, Reporting year, Progress summary, Key results achieved, Challenges encountered, Priorities for next year (these fields are **provisional**, not confirmed requirements: Decision D2). Each long-text field carries the same short helper line: "Describe the project only. Do not include personal details about individuals." (data minimisation, see Section 9). In **resubmit mode**, a highlighted panel at the top shows the Manager's return comment, who returned it and when, with the form pre-filled with the previous content. |
| **Main actions** | *Submit report* (primary); *Cancel* (text link). There is no Save draft action in the initial MVP (D1). Submit asks for a clear confirmation before sending ("Submit this report for review?"). |
| **Navigation links** | Back to Dashboard; View history for this report (resubmit mode). |
| **Accessibility and usability** | Visible label above every field (no placeholder-only labels); required fields marked in text ("required"), not just an asterisk; error summary at the top of the form with links to each problem field, plus an inline message beside each field; helper text linked with `aria-describedby`; logical tab order; character guidance for long text fields; the submit button never relies on colour alone to look active or disabled. |

### 3.3 Report Review

| | |
|---|---|
| **Purpose** | Let the Programme Manager read one submitted report and make a decision. |
| **Access** | Programme Manager only. An Officer who opens the address directly sees a plain "This page is for Programme Managers" message with a link back to the Dashboard (same pattern as Submit Report). |
| **Main information** | Report details laid out as read-only labelled sections (project name, year, all report fields); a status badge; submitted by and submitted on; a compact "Previous decisions" note if the report was returned before; a decision panel with a comment box. |
| **Main actions** | *Approve* (primary); *Return with comment* (secondary). The comment is **required** to return, optional on approval (D3). Both actions ask for confirmation. Only available while status is Submitted. |
| **Navigation links** | Back to Dashboard; View history for this report. |
| **Accessibility and usability** | The decision panel follows the report content in reading order; Approve and Return look clearly different through label and shape, not only colour; the required comment error is announced to screen readers; after deciding, the person returns to the Dashboard with a confirmation message (`role="status"`); already-decided reports show the decision read-only with no buttons. |

### 3.4 Report History

| | |
|---|---|
| **Purpose** | A clear record of who did what and when. |
| **Access** | Both roles. Officers see only their own reports; Managers see all reports (D4). |
| **Main information** | A list of reports (title, year, current status, last action date) with a status filter. Selecting a report expands an **activity timeline**: each entry has the action (Submitted, Returned, Resubmitted, Approved), the person's name and role, the date and time, and the comment if there was one. Newest first. No interface change is made for automation. If an automation is implemented later and records an entry, the actor shown reads "System (automation)" in the same place as a person's name, with no extra role (D13). |
| **Main actions** | Filter by status; expand or collapse a report's timeline; *Open* (takes an Officer to Submit Report for a Returned report, or a Manager to Report Review for a Submitted one). |
| **Navigation links** | Dashboard; Submit Report (Officer); Report Review (Manager). |
| **Accessibility and usability** | Timeline marked up as an ordered list; dates written in full ("14 Nov 2026, 10:42") rather than relative terms; the expand control is a real button with `aria-expanded`; filter is a labelled select, not colour chips. |

---

## 4. Suggested layout and component structure

### Page frame (all screens)

```
+--------------------------------------------------------------+
| Demonstration only · view as Project Officer / Programme Manager |
| Skip link; original globe; APR Review Hub wordmark            |
| Dashboard | Submit Report | Report History · sample name/role |
+--------------------------------------------------------------+
|  <h1> Page title                                             |
|  Optional short intro line                                   |
|                                                              |
|  Main content (max width 1040px, centred, generous margins) |
|                                                              |
+--------------------------------------------------------------+
| Footer: "Student demonstrator. Not an official GCF system."  |
+--------------------------------------------------------------+
```

### Shared components

| Component | Notes |
|---|---|
| Top navigation bar | Evergreen text on cream; active page uses an evergreen pill and `aria-current="page"`; collapses to a menu button on narrow screens. |
| Page header | `<h1>`, optional one-line description, primary action aligned right (stacks below on mobile). |
| Card | Cream-tinted panel, 1px `#8a8163` border, 12px radius, very light shadow. |
| Status badge | Icon + word, outlined; never colour alone. Submitted is blue, Approved green and Returned burnt orange as shown below. |
| Count tile | Large number plus label ("Submitted"). No charts. |
| Report list/table | Table on desktop; stacked cards on mobile. |
| Form field | Visible label, optional helper text, input with a 1px `#8a8163` border, inline error. |
| Buttons | Primary (evergreen fill, white text), secondary (outlined), text link. Minimum 44px height; keyboard focus has a 3px evergreen outline and 3px offset. |
| Confirmation dialog | Short question, two clear buttons, focus moves into it and returns afterwards. |
| Message banner | Success or error includes an icon and explanatory text. |
| Timeline | Vertical list with action, person, role, date/time, comment. |

### Implemented colour roles

The values below match `static/css/styles.css`. Ratios were calculated from the hex values against the rendered cream or panel surface.

| Role | Colour | Contrast (calculated) | Use |
|---|---|---|---|
| Page background | Cream `#efe6d0` | n/a | Page background |
| Panel surface | `#f7f0df` | n/a | Cards, banners and forms |
| Body text | `#1c2b21` | 11.93:1 on cream; 13.05:1 on panel | Body text and labels |
| Secondary text | `#4a5a4d` | 5.91:1 on cream; 6.46:1 on panel | Hints, captions and dates |
| Headings | Evergreen `#0b391a` | 10.47:1 on cream; 11.45:1 on panel | Headings and report labels |
| Links | `#14572c` | 6.96:1 on cream; 7.61:1 on panel | Links |
| Primary button | `#0f4a26` | White text: 10.36:1 | Primary actions |
| Submitted status | Blue `#134a63` | White: 9.60:1 | Status tile; badge also has a circle and “Submitted” |
| Approved status | Green `#0d611d` | White: 7.65:1 | Status tile; badge also has a tick and “Approved” |
| Returned status | Burnt orange `#b9570b`; text `#a64d09` | White on fill: 4.74:1; text: 4.58:1 on cream, 5.01:1 on panel | Status tile and badge; badge also has a return arrow and “Returned” |
| Component/control boundary | `#8a8163` | 3.13:1 on cream; 3.42:1 on panel | Cards, fields, outlined buttons and rules |
| Focus outline | Evergreen `#0b391a`, 3px with 3px offset | 10.47:1 on cream | Keyboard focus indicator |

**Rules**

- Normal text meets 4.5:1 and large text and meaningful component boundaries meet 3:1 on the two surfaces.
- The status word and icon are always present; colour is supplementary.
- The calculated contrast values should be rechecked if any palette value changes.

**Colour-blindness note.** The status accent colours are distinct, but meaning never relies on colour: each status has its own icon shape and text label.

### Typography and spacing

- One readable system or web-safe sans-serif family; 16px minimum body size; line height around 1.5.
- Clear heading scale (H1 largest, then H2 for sections).
- Spacing in multiples of 8px; generous padding in cards and forms.

### Responsive behaviour

- Desktop: centred content column, tables for lists.
- Tablet: same layout with tighter margins.
- Mobile: nav collapses to a menu button; tables become stacked cards; buttons go full width; the form stays single column.

---

## 5. Accessibility and usability checklist

- [ ] "Skip to main content" link on every page.
- [ ] One `<h1>` per page, headings in logical order.
- [ ] Every form field has a visible, associated label.
- [ ] Required fields identified in words.
- [ ] Errors are listed in a summary and shown beside each field, in plain language.
- [ ] Status always shown as text plus icon, never colour alone.
- [ ] All text meets WCAG AA contrast (4.5:1); large text and meaningful UI boundaries meet 3:1 using the colour roles in Section 4.
- [ ] Rendered pages re-checked against the calculated contrast ratios.
- [ ] Screenshots reviewed through colour-blindness simulations; statuses remain distinguishable by icon and word.
- [ ] Icons and borders remain visible in forced-colours (Windows high-contrast) mode.
- [ ] Everything works with keyboard only; focus indicator is clearly visible (e.g. 3px terracotta outline).
- [ ] Logical tab order; dialogs trap focus and restore it on close.
- [ ] Confirmation and error messages announced to assistive technology (`role="status"` / `role="alert"`).
- [ ] Current nav page marked with `aria-current="page"`.
- [ ] Touch targets at least 44×44px.
- [ ] Layout works at 375px and at actual 200% and 400% browser zoom without horizontal scrolling; completion is recorded in `week06-ui-review.md`.
- [ ] Dates and times written in full and unambiguous.
- [ ] Destructive or irreversible actions (Submit, Approve, Return) ask for confirmation.
- [ ] Empty states explain what to do next.
- [ ] Respect reduced-motion settings; keep animation minimal.

---

## 6. Sample data (invented)

**People:** Aoife Murphy (Project Officer), Daniel Okafor (Programme Manager).

| Report | Year | Status | Last action |
|---|---|---|---|
| Coastal Resilience Pilot, APR 2025 | 2025 | Submitted | Submitted by Aoife Murphy, 14 Nov 2026, 10:42 |
| Solar Irrigation Scheme, APR 2025 | 2025 | Returned | Returned by Daniel Okafor, 12 Nov 2026, 15:05. Comment: "Please add results against the original targets." |
| Mangrove Restoration, APR 2025 | 2025 | Approved | Approved by Daniel Okafor, 5 Nov 2026, 09:30 |

These are fictional examples, not real projects.

---

## 7. Assumptions

- The eventual application requires **actual authentication** (D9). The displayed name and role are sample data; the visible role switch exists only to evaluate both views and is not sign-in. A sample-user or role selector is not an acceptable final sign-in. Authentication is not designed or implemented in this skeleton.
- Each report belongs to one Officer; the Manager can see all reports.
- A report can be returned and resubmitted more than once; every cycle is kept in history.
- Approved reports are final and read-only.
- Times are shown in Dublin local time.
- Report content is text only (no files).

---

## 8. Unresolved decisions (need confirmation)

| # | Decision | Suggested default |
|---|---|---|
| D1 | ~~Draft status and Save draft~~ | **Decided:** removed from the initial MVP. Statuses are Submitted, Returned and Approved. |
| D2 | **Which fields** does an APR contain? The brief does not list them. | **Provisional:** the fields in 3.2 (all free text plus a year selector) are placeholders, not confirmed requirements. |
| D3 | Is a comment **required or optional** when approving? | Required to return; optional to approve. |
| D4 | Should an Officer see only their **own** reports, or all? | Own only. |
| D5 | Can a Manager **edit** a report or only decide? | Decide only. |
| D6 | Can an Officer **withdraw** a submitted report before review? | No (not in the approved workflow). |
| D7 | Is **Report Review** a nav item or only reachable from lists? | Only from lists. |
| D8 | Does Report History include a **global activity log** or only per-report timelines? | Per-report timelines inside a report list. |
| D9 | How are people identified in the eventual application (**sign-in method**)? | **Decided in principle:** actual authentication is required, not a sample-user or role selector. The mechanism is chosen at the later authentication stage. |
| D10 | Is the **logo/wordmark** needed, or just text? | Text wordmark only. |
| D11 | Is a **single report per Officer per year** enforced? | No restriction. |
| D12 | Should **comment history** show all previous returns or just the latest? | Show all in History; latest on Submit Report. |
| D13 | How can automated activity be recorded without a third role? | Each Report Activity entry records either a person (a User) or "System (automation)". The role list stays exactly two: Project Officer and Programme Manager. How this is stored is a later database decision. |
| D14 | **Future implementation item:** what does the **scheduled** automation do, given the brief rules out in-app reminders and messaging? | No screen or interface change. Candidate: housekeeping such as a retention check (D16). |
| D15 | **Future implementation item:** what does the **event-triggered** automation do? | No screen or interface change. Candidate: on Submit/Return/Approve, a notification outside the app. |
| D16 | What is the **retention period** for reports and activity, and what happens at the end (delete or anonymise)? | Short period stated in the CA2 write-up, applied by the scheduled automation. |
| D17 | Is a short **privacy statement** needed, and where? | One static footer paragraph, not a new screen. |

---

## 9. CA2 readiness review (added 18 Nov)

**Approach:** the four screens and visual skeleton above are implemented. The Week Six review and checks are in `week06-ui-review.md`. This section maps the skeleton to possible later CA2 requirements; it does not claim that backend permissions or security are implemented. The CA2 brief wording was not supplied, so check these points against it.

### 9.1 Three related tables

| Table | Likely contents (proposed) | Where it appears in the skeleton |
|---|---|---|
| **User** | Name, role (Project Officer or Programme Manager), email | Top bar (name and role); "submitted by", "returned by" labels |
| **APR Report** | Owner (a User), project name, reporting year, the long-text fields, current status, created and last-updated times | Dashboard lists and count tiles; Submit Report form; Report Review content |
| **Report Activity** | Report, who acted (a User, or "System (automation)"; see D13), action, comment, date and time | Report History timeline; return comment on Submit Report; "Previous decisions" on Report Review |

Relationships: one User has many Reports; one Report has many Activity entries; each Activity entry is linked to one User, or is marked as automated (D13).

What the skeleton already supports: every screen field maps to exactly one table, the status list is fixed (Submitted, Returned, Approved), and the action list is fixed (Submitted, Returned, Resubmitted, Approved). Dashboard counts are derived from Report status, not stored separately.

Dependency to settle first: D2 (the report fields are provisional and decide the APR Report columns).

### 9.2 Roles and data-level permissions

The screens already separate the two roles, but hiding a link is not security. The intended data rules, to be enforced later at data level:

| Role | APR Report | Report Activity | User |
|---|---|---|---|
| Project Officer | Read own; create (by submitting); edit own only while Returned | Read for own reports; create Submitted and Resubmitted | Read own record |
| Programme Manager | Read all; change status of Submitted reports only | Read all; create Approved and Returned | Read names and roles needed for display |

The skeleton change made: Report Review now has the same "wrong role" message as Submit Report.

### 9.3 Three automations

| Automation | Natural fit in the skeleton | Open point |
|---|---|---|
| **Human approval** | Already the core workflow: Report Review, Approve or Return | None; this is the approved workflow |
| **Event-triggered** | **Future implementation item.** A new Report Activity entry (submit, return, approve) is the event | D15 |
| **Scheduled** | **Future implementation item.** No screen needed | D14, D16. The brief rules out in-app reminders, so avoid a reminder feature |

No screens or interface functionality are added for the two future automations. The History timeline already has a place for the actor's name, so an automated entry can later show "System (automation)" there (D13). No new role or screen is added.

### 9.4 Level-1 Data Flow Diagram

Suggested mapping from existing screens to DFD elements:

| DFD element | Skeleton source |
|---|---|
| External entities | Project Officer, Programme Manager (and the email service, if D15 is adopted) |
| Process 1: Identify user and role | Top bar, role messages |
| Process 2: Submit or resubmit report | Submit Report |
| Process 3: Review and decide | Report Review |
| Process 4: View dashboard and history | Dashboard, Report History |
| Process 5: Run automations | Outside the four screens |
| Data stores | User, APR Report, Report Activity |
| Trust boundaries | (a) person's browser and the application; (b) application and the data stores; (c) application and any external automation or email service |

The screens already line up with these processes; no layout change was needed.

### 9.5 STRIDE

No visual changes needed. The threat analysis will use the DFD in 9.4. Skeleton features that already support later mitigations:

| STRIDE | Skeleton feature to build on |
|---|---|
| Spoofing | Role and name always visible in the top bar; real authentication to be added later (D9) |
| Tampering | Approved reports read-only; decision only while Submitted |
| Repudiation | Report Activity records who, what, when |
| Information disclosure | Officers limited to own reports (D4) |
| Denial of service | Out of scope for a demonstrator; note as accepted |
| Elevation of privilege | Wrong-role messages on Submit Report and Report Review, backed by data-level rules (9.2) |

### 9.6 GDPR

| Requirement | Skeleton position | Change made or open |
|---|---|---|
| Data minimisation | Only name, role and email in User; invented data only | Added a helper line on the long-text fields warning against personal details |
| Access | Officers see their own data; History shows who did what | None |
| Retention | Not yet visible anywhere | D16; no screen change |
| Transparency | Footer already says "Student demonstrator" | D17: optional static privacy paragraph in the footer |

### 9.7 Summary of changes made to this specification

1. Helper line on long-text fields in Submit Report (data minimisation).
2. "Wrong role" message added to Report Review.
3. History timeline may show "System (automation)" as an actor.
4. Decisions D13 to D17 added.

### 9.8 Left for later

Tables and data-level permissions, actual authentication, the scheduled and event-triggered automations (the human approval step already exists as the Report Review workflow), the written DFD, the full STRIDE analysis, and the GDPR retention and privacy wording. These all depend on the open decisions above.

---

## 10. Revision log

**Revision 2 (18 Nov 2026).** Limited refinements; the four-screen structure, navigation, visual design and core workflow are unchanged.

| # | Change | Where |
|---|---|---|
| 1 | Draft status and Save draft removed from the initial MVP; statuses are Submitted, Returned, Approved | Section 1, 3.2, 8 (D1), 9.1, 9.2 |
| 2 | Report fields marked provisional, not confirmed requirements | 3.2, 8 (D2), 9.1 |
| 3 | Actual authentication stated as an eventual requirement; sample users and role selector are for skeleton screens only | Section 7, 8 (D9), 9.5 |
| 4 | Scheduled and event-triggered automations marked as future implementation items; no screens or interface functionality added | 3.4, 8 (D14, D15), 9.3 |
| 5 | Automated activity can be recorded as "System (automation)" with no additional role | 3.4, 8 (D13), 9.1, 9.3 |
| 6 | Purpose and scope clarified: visual skeleton for Week Six accessibility and usability work | Document header |

**Revision 2.1 (18 Nov 2026).** Earlier colour and contrast proposal. Superseded by the implemented palette in Revision 2.4.

| # | Change | Where |
|---|---|---|
| 7 | Supporting colour roles added with calculated contrast ratios (card tint, secondary text, deep sage for small sage text, control border, focus ring) | Section 4 (Colour roles) |
| 8 | Sage text moved to deep sage `#496339`; sage `#587446` kept for icons, fills and edges | Section 1 (statuses), Section 4 |
| 9 | Control borders kept as the gentle `#d9d0c4` at the owner's request (a darker `#8a7a6a` was tried and rejected as too heavy). Recorded as a known exception below 3:1, with fallback `#948574` | Section 4 (Colour roles, Rules, Shared components) |
| 10 | Colour-blindness note added; status already relies on icon and word, not colour | Section 4 |
| 11 | Contrast, colour-blindness and forced-colours checks added to the checklist | Section 5 |

**Revision 2.4 (20 Nov 2026).** As-built visual specification aligned to the Flask templates and CSS. Added the actual demo-role navigation, implemented status palette and measured contrast values; raised meaningful component and control borders to at least 3:1; corrected the accessibility checklist and linked the Week Six review.

**Still open:** D2 (final report fields), D3 to D8, D10 to D12, D14 to D17.
