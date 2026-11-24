# Week Six UX/UI review: GCF APR Review Hub

**Author:** TR  
**Date:** 20 Nov 2026  
**Scope:** Four-screen student demonstrator (Dashboard, Submit Report, Report Review, Report History). Two sample roles; all data is invented.

## Course instructions and scoring

The available Week 06 Directed Learning brief says to score the interface against **Nielsen's ten heuristics**, with one line of evidence for each. It does not specify a score scale. This review uses 0-5 per heuristic (50 points maximum), matching the existing evidence and the assessment's 50-point maximum. The later five-heuristic fallback therefore does not apply.

The before state is the dated 19 Nov screenshot set and review notes: the interface after its reference-image redesign but before the documented Week Six accessibility refinements. It is **not** presented as the original ivory/terracotta concept. No earlier runnable code or Git baseline was available. Scores are one reviewer’s reasoned judgement, not a usability study or measured user outcome.

## Heuristic evaluation

| Nielsen heuristic | Before /5 | Before evidence | After /5 | After evidence |
|---|---:|---|---:|---|
| 1. Visibility of system status | 4 | Dashboard states and counts were visible, but a success notice was not focused or announced. | 5 | Status badges use icon and word; confirmation uses `role="status"` and receives focus. |
| 2. Match between system and real world | 5 | The roles and report statuses use familiar terms. | 5 | The same clear role and status terms remain; no domain terminology changed. |
| 3. User control and freedom | 4 | Cancel was available, but Escape did not close the mobile menu. | 5 | Cancel remains; Escape closes the menu and restores focus; modal dialog supports Escape. |
| 4. Consistency and standards | 4 | Some stand-alone action links were smaller than the other controls. | 5 | Actions use consistent styling and at least 44px height; page navigation marks the current item. |
| 5. Error prevention | 4 | Required fields and return comments were enforced, but errors needed clearer navigation. | 5 | Required text, confirmation prompts, linked error summary and inline errors guide correction. |
| 6. Recognition rather than recall | 5 | Visible field labels, statuses and navigation already identify the available choices. | 5 | Those cues remain; helper text and returned comments are visible where needed. |
| 7. Flexibility and efficiency of use | 3 | One path per task; no shortcuts, appropriate to the small demonstrator. | 3 | Scope intentionally remains one path per task; no unnecessary features were added. |
| 8. Aesthetic and minimalist design | 4 | Calm layout, but the dashboard table can feel dense at larger text sizes. | 4 | Same content and layout; stronger boundaries improve findability without changing the workflow. |
| 9. Help users recognize, diagnose and recover from errors | 4 | Required fields and messages existed, but error links were small and summary focus was absent. | 5 | Plain-language summary links, inline errors and focus on the summary support recovery. |
| 10. Help and documentation | 2 | Field hints were the only in-app help; broader guidance is outside the skeleton. | 2 | Help remains limited to relevant field hints; no new feature was added. |
| **Total** | **39/50** |  | **44/50** |  |

### Problems and improvements

- The success state was easy to miss for keyboard and assistive-technology users. The confirmation banner is announced and focused.
- Escape did not dismiss the mobile menu. The menu now closes on Escape and returns focus to its button; the confirmation uses a native modal dialog.
- Some action links were smaller than other controls. Interactive links and controls now have at least a 44px height, exceeding the 24px minimum.
- Error recovery and control boundaries needed strengthening. The form has associated visible labels, required text, summary and inline errors; the shared border is now `#8a8163`.
- The dashboard can still feel dense at larger text sizes, and the demonstrator has no additional help or task shortcuts. These were retained as documented limitations rather than expanding scope.

## Accessibility and visual checks

- **Contrast calculation from the implemented CSS values:** body text `#1c2b21` is 11.93:1 on cream and 13.05:1 on panel; secondary text `#4a5a4d` is 5.91:1 and 6.46:1; returned small text `#a64d09` is 4.58:1 and 5.01:1. These meet the 4.5:1 normal-text minimum. White on the returned tile fill `#b9570b` is 4.74:1.
- Meaningful panel/control borders `#8a8163` are 3.13:1 on cream and 3.42:1 on panel. The evergreen focus outline has at least 10.47:1 against cream.
- Template review and route tests confirm visible labels associate with form controls; status badges show both an icon and a word.
- CSS provides `:focus-visible`; the mobile menu has an Escape handler and focus restoration; the native modal dialog closes on Escape. Keyboard focus screenshots are included below. A screen-reader usability study was not performed.
- At 375px, and at 640px and 320px CSS viewport widths, all five rendered screen/role routes had no document-level horizontal overflow and no visible control below 24px. These are **viewport-width checks, not browser-zoom tests**.
- The Project Officer dashboard was checked at actual Microsoft Edge browser zoom of 200% (the browser Zoom menu showed 200%). It reflowed to a single column with no visible horizontal overflow in the full-page capture. This is after-only evidence, not a before/after comparison. Other routes at 200% and all routes at 400% remain unverified. A true 400% browser-zoom check and screenshot are outstanding; the 320px viewport result must not be substituted for 400% zoom. Edge rendered a blank page on subsequent reloads, so no 400% result is claimed.

## Evidence

The dated before/after pairs below differ and are used for comparison:

- Dashboard desktop: [before](portfolio/img/before-dashboard-officer-desktop.png), [after](portfolio/img/after-dashboard-officer-desktop.png)
- Dashboard mobile at 375px: [before](portfolio/img/before-dashboard-officer-mobile-375.png), [after](portfolio/img/after-dashboard-officer-mobile-375.png)
- Submit errors: [before](portfolio/img/before-submit-report-errors-desktop.png), [after](portfolio/img/after-submit-report-errors-desktop.png)
- Report Review desktop: [before](portfolio/img/before-report-review-desktop.png), [after](portfolio/img/after-report-review-desktop.png)
- Report History desktop: [before](portfolio/img/before-report-history-desktop.png), [after](portfolio/img/after-report-history-desktop.png)
- Submit Report mobile at 375px: [before](portfolio/img/before-submit-report-mobile-375.png), [after](portfolio/img/after-submit-report-mobile-375.png)
- Keyboard focus: [before](portfolio/img/before-evidence-keyboard-focus.png), [after](portfolio/img/after-evidence-keyboard-focus.png)
- Existing 200%-named pair: [before](portfolio/img/before-dashboard-officer-zoom-200.png), [after](portfolio/img/after-dashboard-officer-zoom-200.png) (retained, zoom state not independently verified).
- Actual 200% browser-zoom capture, Project Officer dashboard (supplemental current-state evidence only): [after](portfolio/img/after-dashboard-officer-browser-zoom-200.jpeg).
- Current Programme Manager dashboard capture: [after](portfolio/img/after-audit-dashboard-manager-desktop.png) (the older before/after pair was identical and is not used as change evidence).

The manager-dashboard pair and the before/after colour-simulation and forced-colour pairs were byte-identical in the supplied evidence; they are not presented as evidence of a change. The new manager-dashboard capture above was taken from the running app after the boundary update. Colour simulation and Windows forced-colours have not been independently recaptured for the current version.

## Functional verification and limitations

The Flask prototype retains the two sample roles and intended submit, review, approve, return-with-comment, amend/resubmit and history routes. A valid new submission appears on the submitting browser session's dashboard and is not stored permanently; review decisions remain demonstration messages. Focused Flask tests cover route access, validation, session-scoped submission display, role-specific lists, return comments, resubmission and history filtering.

The available Week Six brief also asks for three short answers to be posted to the course forum and for pre-session reading/video work. These are external course tasks and are not represented as completed here. No explicit CCT AI-use disclosure rule appears in the available Week Six brief or project files; the separate CA2/CCT brief was not supplied, so any requirement in it remains unverified. No AI attribution has been added.
