# Ezra Staging — Bug Report & Test Cases

**Application:** Ezra Staging — `https://myezra-staging.ezra.com`
**Reported by:** Amarpreet Singh
**Report date:** 2026-03-30
**Environment:** Staging

---

## Severity & Priority Definitions

| Level | Severity meaning | Priority meaning |
|---|---|---|
| **Critical** | Application crash / data loss / security breach | Must fix before any release |
| **High** | Core feature broken or incorrect medical data accepted | Fix in current sprint |
| **Medium** | Degraded UX or edge-case data gap | Fix in next sprint |
| **Low** | Minor cosmetic / enhancement | Backlog |

---

## Bug Index

| # | Title                                                                         | Severity | Priority | Evidence |
|---|-------------------------------------------------------------------------------|---|---|---|
| BUG-01 | Heart scan does not surface Lung add-on                                       | High | High | [video](#bug-01-heart-scan--lung-add-on-not-displayed) |
| BUG-02 | Booking dates allowed up to and over year 2044                                | Medium | Medium | [screenshot](#bug-02-far-future-booking-dates-allowed-up-to-2044) |
| BUG-03 | ID upload accepts a different person's name                                   | High | High | _(no media — reproduced manually)_ |
| BUG-04 | Prior surgery date accepted before user's date of birth                       | High | Medium | [screenshot](#bug-04-prior-surgery-date-allowed-before-date-of-birth) |
| BUG-05 | "Confirm none apply" deselects individual items already selected              | Medium | Medium | [video](#bug-05-confirm-none-apply-deselects-all-individual-selections) |
| BUG-06 | Tattoo healing 6-week window calculated from questionnaire date, not MRI date | Medium | Medium | [screenshot](#bug-06-tattoo-healing-window-calculated-from-questionnaire-date) |
| BUG-07 | Questionnaire validity not enforced for far-future scan bookings              | High | Medium | [screenshot](#bug-07-questionnaire-validity-not-enforced-for-far-future-scans) |
| BUG-08 | User cannot review their previously submitted questionnaire answers           | Medium | Medium | _(no media — reproduced manually)_ |
| BUG-09 | Aggregated location filtering hides valid per-scan locations                  | Medium | Medium | [video](#bug-09-aggregated-location-filtering-hides-valid-per-scan-locations) |
| BUG-10 | Partial scan cancellation not supported — only full cancellation allowed      | Medium | Medium | _(no media — reproduced manually)_ |
| BUG-11 | Weight accepts 1 kg; changing weight clears height field                      | Medium | Medium | [screenshot · video](#bug-11-weight-accepts-1-kg--changing-weight-clears-height-field) |
| BUG-12 | Saved payment card intermittently not loaded for returning users              | Medium | Low | _(intermittent — no consistent reproduction)_ |

---

## Bug Details

---

### BUG-01: Heart Scan — Lung Add-on Not Displayed

| Field | Value |
|---|---|
| **Severity** | High |
| **Priority** | High |
| **Feature area** | Scan Selection — Add-ons |
| **Test data** | `bug_resources/ezra_bug_1_heart_and_lung_scan_Addon.mov` |

**Description**

When a user navigates to the scan selection page and selects **Heart Scan**, the
**Lung Scan add-on** is not displayed as an available option, preventing the user
from combining both scans in a single booking.

Conversely, when the user selects **Lung Scan** first, a Heart Scan add-on card
correctly appears and can be selected. This asymmetry suggests the add-on
relationship is only configured in one direction (Lung → Heart), not both
(Heart → Lung).

**Steps to Reproduce**

1. Log in and navigate to **Book a Scan**.
2. On the scan selection page, select the **Heart Scan** card.
3. Observe the add-on section.

**Expected Result**

A Lung Scan add-on option should appear after selecting Heart Scan, consistent
with the behaviour when Lung Scan is selected first.

**Actual Result**

No add-on option is displayed. The user can only proceed with Heart Scan alone.

**Impact**

Users who begin their selection with Heart Scan cannot discover or purchase the
Lung add-on. This results in lost revenue and an incomplete user journey for a
core use case.

**Evidence**

📹 [ezra_bug_1_heart_and_lung_scan_Addon.mov](bug_resources/ezra_bug_1_heart_and_lung_scan_Addon.mov)

---

### BUG-02: Far-Future Booking Dates Allowed (Up to 2044)

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Priority** | Medium |
| **Feature area** | Date & Time Selection |
| **Test data** | `bug_resources/far_off_date_selection.png` |

**Description**

The date picker on the appointment booking screen places no practical upper
limit on how far in the future a scan can be booked. Dates as far ahead as
**2044** are accepted without any warning or restriction.

This is directly compounded by BUG-07: the medical questionnaire, which asks
about the user's current health conditions, is completed at the time of booking
but will be completely medically irrelevant by the time the scan takes place
18 years later.

**Steps to Reproduce**

1. Log in and navigate to **Book a Scan**.
2. Select a scan type and location.
3. On the date picker, navigate forward month by month (or year by year).
4. Select a date in 2044 and proceed.

**Expected Result**

The date picker should enforce a maximum booking window (e.g., 6–12 months
from today), and dates beyond that limit should be disabled or display a
warning.

**Actual Result**

Dates up to (at least) 2044 are selectable and accepted. The booking proceeds
without any warning about questionnaire validity.

**Impact**

Bookings created for implausibly distant dates undermine the clinical value of
the questionnaire data and may generate operational noise for the Ezra
medical team.

**Evidence**

📸 [far_off_date_selection.png](bug_resources/far_off_date_selection.png)

---

### BUG-03: ID Upload Accepts a Different Person's Name

| Field | Value |
|---|---|
| **Severity** | High |
| **Priority** | High |
| **Feature area** | Medical Questionnaire — Identity Verification |
| **Test data** | _(reproduced manually — no media captured)_ |

**Description**

During the medical questionnaire, the user is asked whether they are completing
the questionnaire for themselves. When the user selects **"Yes, for myself"**,
the system then allows them to upload a photo ID belonging to a **different
person** (e.g., John Doe). The system reads the name from the uploaded ID and
substitutes it as the patient name for whom the scan will be booked — replacing
the name on the registered account (e.g., Amarpreet Singh).

**Steps to Reproduce**

1. Log in as a registered user (e.g., Amarpreet Singh).
2. Begin the medical questionnaire.
3. When prompted, select **"I am answering for myself"**.
4. When prompted to upload ID, upload a photo ID for a different person (John Doe).
5. Proceed through the questionnaire.

**Expected Result**

The system should validate that the name on the uploaded ID matches the name on
the registered account. A mismatch should surface an error and block progression.

**Actual Result**

The system accepts the mismatched ID and replaces the booking's patient name
with the name extracted from the uploaded document (John Doe). The scan is now
associated with the wrong identity.

**Impact**

This is a **medical data integrity and patient safety issue**. A scan could be
performed for, or attributed to, the wrong person. Clinical follow-up and results
would be delivered to the wrong patient identity.

**Evidence**

_(No media — reproduced manually. Recommend capturing a screen recording during
next regression cycle.)_

---

### BUG-04: Prior Surgery Date Allowed Before Date of Birth

| Field | Value |
|---|---|
| **Severity** | High |
| **Priority** | Medium |
| **Feature area** | Medical Questionnaire — Surgery History |
| **Test data** | `bug_resources/join_replacement_date_before_birth.png` |

**Description**

In the medical questionnaire, when the user is asked to provide the date of a
prior surgery or joint replacement, the date picker accepts dates that are
**earlier than the user's registered date of birth**. A person cannot have
undergone surgery before they were born, so this represents a basic input
validation failure.

**Steps to Reproduce**

1. Log in and begin the medical questionnaire.
2. Navigate to the section asking about prior surgeries or joint replacements.
3. Enter a surgery date that is earlier than the account holder's date of birth.
4. Proceed to the next step.

**Expected Result**

The system should validate that the surgery date is not earlier than the user's
date of birth and display an inline validation error if it is.

**Actual Result**

The date is accepted without any validation error and the questionnaire advances.

**Impact**

Invalid medical history data is accepted and stored, reducing the clinical
reliability of the questionnaire responses.

**Evidence**

📸 [join_replacement_date_before_birth.png](bug_resources/join_replacement_date_before_birth.png)

---

### BUG-05: "Confirm None Apply" Deselects All Individual Selections

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Priority** | Medium |
| **Feature area** | Medical Questionnaire — Implants / Devices Checklist |
| **Test data** | `bug_resources/ease_of_use_in_options.mov` |

**Description**

The implants and devices checklist contains a "select all that apply" list and
a master confirmation checkbox:

> _"I confirm that I have reviewed the list of items and devices below and
> declare that none apply to me at the time of my MRI."_

The intended workflow for a user who has **one** relevant item is:

1. Check the master "none apply" checkbox to quickly clear all items.
2. Then individually re-check the one item that does apply.

However, after checking the master checkbox and then re-selecting an individual
item, the master checkbox is cleared but **all other individual items that were
previously unchecked are also reset/deselected**, rather than remaining in their
prior state.

**Steps to Reproduce**

1. Navigate to the implants/devices checklist in the questionnaire.
2. Check the **"I confirm none apply"** master checkbox.
3. Individually select one item from the list (e.g., "Pacemaker").
4. Observe the state of the remaining items.

**Expected Result**

Selecting an individual item after using the master checkbox should only affect
that specific item. All other items should remain in their current state (cleared).

**Actual Result**

Selecting a single item after the master checkbox causes unexpected state changes
across other items in the list, making it impossible to achieve a "none except
one" selection without manually reviewing every item in the list.

**Impact**

Users with a single applicable condition face a significantly degraded and
error-prone experience when trying to accurately complete the checklist.

**Evidence**

📹 [ease_of_use_in_options.mov](bug_resources/ease_of_use_in_options.mov)

---

### BUG-06: Tattoo Healing Window Calculated from Questionnaire Date, Not MRI Date

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Priority** | Medium |
| **Feature area** | Medical Questionnaire — Tattoo / Permanent Makeup Section |
| **Test data** | `bug_resources/should_dates_for_tatto_healing_from_the_date_of_mri_or_questionaire.png` |

**Description**

The medical questionnaire informs users that a tattoo or permanent makeup must
be **at least 6 weeks healed** before an MRI can be performed. However, the
system calculates the 6-week window from the **date the questionnaire is
filled in**, rather than from the **date of the scheduled MRI scan**.

If a user fills in the questionnaire several weeks before their scheduled scan,
a tattoo that does not yet meet the 6-week threshold on the questionnaire date
may well be fully healed by the actual MRI date — but the system would
incorrectly flag it as a concern.

**Steps to Reproduce**

1. Book an MRI scan scheduled 4+ weeks in the future.
2. Begin the medical questionnaire.
3. In the tattoo/permanent makeup section, enter a tattoo date that is 5 weeks
   before today (but 9+ weeks before the MRI date).
4. Observe the validation message.

**Expected Result**

The 6-week healing window should be calculated relative to the **scheduled MRI
date**, not the questionnaire completion date.

**Actual Result**

The system calculates the 6-week window from today's date (questionnaire date),
potentially blocking a user whose tattoo will be fully healed by the MRI date.

**Impact**

Users may be incorrectly advised that they cannot proceed, or may be passed
through when they should be flagged — depending on the direction of the date
discrepancy.

**Evidence**

📸 [should_dates_for_tatto_healing_from_the_date_of_mri_or_questionaire.png](bug_resources/should_dates_for_tatto_healing_from_the_date_of_mri_or_questionaire.png)

---

### BUG-07: Questionnaire Validity Not Enforced for Far-Future Scans

| Field | Value |
|---|---|
| **Severity** | High |
| **Priority** | Medium |
| **Feature area** | Medical Questionnaire — Booking Validation |
| **Test data** | `bug_resources/question_should_be_completed_5_days_before_but_not_before_certain_num_of_days_or_year.png` |

**Description**

The application enforces that the medical questionnaire must be completed at
least **5 days before the scan date**. However, it does not enforce any
**maximum early completion window** — meaning a user can complete the
questionnaire in 2026 for a scan booked in 2044, even though the health
information they submitted will be clinically meaningless 18 years later.

The 5-day minimum rule only prevents last-minute completion. There is no
complementary rule that prevents completion so far in advance that the data
can no longer be considered valid.

**Steps to Reproduce**

1. Book a scan for a far-future date (e.g., 2044 — see BUG-02).
2. Complete the medical questionnaire immediately.
3. Observe that no warning is shown about data validity.

**Expected Result**

The system should enforce a maximum questionnaire completion window (e.g.,
no earlier than 6–12 months before the scan date), with a clear message
explaining why early completion is restricted.

**Actual Result**

The questionnaire is accepted in full regardless of how far in the future the
scan is scheduled. No validity warning is shown.

**Impact**

The Ezra medical team may be reviewing questionnaire data that is years out of
date, creating clinical risk and wasted operational effort.

**Evidence**

📸 [question_should_be_completed_5_days_before_but_not_before_certain_num_of_days_or_year.png](bug_resources/question_should_be_completed_5_days_before_but_not_before_certain_num_of_days_or_year.png)

---

### BUG-08: User Cannot Review Previously Submitted Questionnaire Answers

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Priority** | Medium |
| **Feature area** | Dashboard — Questionnaire Visibility |
| **Test data** | _(reproduced manually — no media captured)_ |

**Description**

Once a user has submitted their medical questionnaire, there is no way to
navigate back to view the answers they provided. If the user's circumstances
change in the weeks between completing the questionnaire and their scan date,
they have no way to cross-reference what they originally declared in order to
assess whether they need to notify Ezra.

This is particularly relevant when paired with BUG-02 (far-future bookings),
where months or years may elapse between questionnaire completion and the scan.

**Steps to Reproduce**

1. Complete the medical questionnaire for a booked scan.
2. Return to the dashboard.
3. Attempt to navigate to or view the submitted questionnaire responses.

**Expected Result**

A read-only view of previously submitted questionnaire answers should be
accessible from the dashboard or the booking detail page, allowing users to
review what they declared at time of submission.

**Actual Result**

No such view exists. The user has no way to access their previously submitted
questionnaire data from within the application.

**Impact**

Users cannot self-audit their submissions. If a relevant medical condition
changes between booking and scan, the user has no reference point to determine
whether a change disclosure is necessary. This creates a patient safety gap.

---

### BUG-09: Aggregated Location Filtering Hides Valid Per-Scan Locations

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Priority** | Medium |
| **Feature area** | Location Selection — Multi-Scan Bookings |
| **Test data** | `bug_resources/aggregated_locations_based_on_selection.mov` |

**Description**

When a user selects multiple scan types (e.g., Heart Scan + Lung Scan), the
location selection page only displays locations that offer **all** selected scan
types simultaneously (logical AND). Locations that offer only one of the selected
scans are hidden entirely.

This means a user who selected Heart Scan + Lung Scan and lives near a location
that only offers Lung Scan will see no nearby options and may abandon the booking
— even though that nearby location could serve their Lung Scan need, with the
Heart Scan handled separately at a different site.

**Scenarios affected:**

- A user wants a Heart Scan at a New Jersey location and an MRI/Lung Scan at a
  New York location (different schedules). The combined filter shows neither.
- A user near a Lung-only location selects Heart + Lung and sees zero results,
  even though a Lung-only booking would be perfectly valid.

**Steps to Reproduce**

1. Navigate to **Book a Scan**.
2. Select both **Heart Scan** and **Lung Scan** (or MRI + Heart).
3. Proceed to the location selection step.
4. Observe that locations offering only one of the two scans are hidden.

**Expected Result**

The location page should either:
- Allow the user to assign each scan type to a separate location independently, or
- Clearly surface single-scan locations with a note that the other scan would
  need to be booked separately.

**Actual Result**

Only locations that support all selected scan types are shown. All others are
filtered out without explanation.

**Impact**

Users in areas with limited Heart Scan coverage may be unable to complete a
multi-scan booking at all, leading to drop-off. Revenue for individual scan
types is also lost.

**Evidence**

📹 [aggregated_locations_based_on_selection.mov](bug_resources/aggregated_locations_based_on_selection.mov)

---

### BUG-10: Partial Scan Cancellation Not Supported

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Priority** | Medium |
| **Feature area** | Booking Management — Cancellation |
| **Test data** | _(reproduced manually — no media captured)_ |

**Description**

When a user has booked multiple scan types in a single appointment and wishes
to cancel only one of them (and receive a partial refund), the application
provides no mechanism to do so. The only available option is to cancel the
entire appointment.

**Steps to Reproduce**

1. Book an appointment with multiple scan types (e.g., MRI + Heart Scan).
2. Navigate to the booking management / cancellation screen.
3. Attempt to cancel only one of the scans.

**Expected Result**

The cancellation flow should allow the user to select individual scan types to
cancel and display the corresponding partial refund amount before confirming.

**Actual Result**

Only a full cancellation of all scans is available. Individual scan cancellation
is not possible.

**Impact**

Users who need to adjust their booking are forced into a full cancellation and
must re-book their remaining scans from scratch, creating unnecessary friction
and a risk of losing the appointment slot.

---

### BUG-11: Weight Accepts 1 kg; Changing Weight Clears Height Field

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Priority** | Medium |
| **Feature area** | Medical Questionnaire — Physical Measurements |
| **Test data** | `bug_resources/bug_height_value_not_shown_if_the_weight_is_changed_from_empty_0_1_regular.png` · `bug_resources/vid_bug_height_value_not_shown_if_the_weight_is_changed_from_empty_0_1_regular.mov` |

**Description**

This bug has two related symptoms:

**11a — No minimum weight validation:**
The weight input field accepts any value, including `1 kg`, with no minimum
validation. A weight of 1 kg is physiologically impossible for an adult patient
and should be rejected.

**11b — Height field cleared when weight is edited (intermittent, potential blocker):**
When an existing user edits their weight — specifically by changing it from
empty → `0` → a real value — the height field loses its previously saved value
and displays as empty. Since the questionnaire requires both fields, this renders
the questionnaire **uneditable** until the height is manually re-entered. This
was reproduced once and qualifies as a potential blocker for affected users.

**Steps to Reproduce (11b)**

1. Log in as an existing user with a previously saved height value.
2. Navigate to the physical measurements section of the questionnaire.
3. Clear the weight field, enter `0`, then change to a real weight value.
4. Observe the height field.

**Expected Result**

- Weight should enforce a clinically reasonable minimum (e.g., ≥ 20 kg).
- Editing the weight field should never affect the value in the height field.

**Actual Result**

- `1 kg` (and lower) is accepted without error.
- The height field is cleared after the weight editing sequence, making the form
  unsubmittable without re-entering height data.

**Evidence**

📸 [bug_height_value_not_shown_if_the_weight_is_changed_from_empty_0_1_regular.png](bug_resources/bug_height_value_not_shown_if_the_weight_is_changed_from_empty_0_1_regular.png)

📹 [vid_bug_height_value_not_shown_if_the_weight_is_changed_from_empty_0_1_regular.mov](bug_resources/vid_bug_height_value_not_shown_if_the_weight_is_changed_from_empty_0_1_regular.mov)

---

### BUG-12: Saved Payment Card Intermittently Not Loaded for Returning Users

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Priority** | Low |
| **Feature area** | Payment — Returning User Experience |
| **Test data** | _(intermittent — no consistent reproduction steps captured)_ |

**Description**

When a returning user (who previously saved a payment card) navigates to the
payment step of a new booking, their saved card is not always pre-populated in
the payment form. The behaviour is intermittent: the card appears on some
sessions and is absent on others, requiring the user to re-enter their card
details.

**Steps to Reproduce**

1. Log in as a returning user who has previously completed a booking and saved
   a payment card.
2. Navigate to **Book a Scan** and proceed through scan, location, and date
   selection to the payment step.
3. Observe whether the saved card is pre-filled.

**Expected Result**

The user's saved payment card should be consistently pre-filled on the payment
page for all returning sessions.

**Actual Result**

The saved card is present on some sessions and absent on others. No clear
trigger has been identified for the missing-card state.

**Impact**

Returning users face unexpected friction at checkout, reducing booking
completion rates. The intermittent nature makes it difficult for users to rely
on the saved-card feature.

**Evidence**

_(No media — intermittent reproduction. Recommend adding instrumentation to
capture the payment page state on each load during regression testing.)_

---

## Summary Table

| Bug | Title | Severity | Priority | Has Evidence |
|---|---|---|---|---|
| BUG-01 | Heart scan — Lung add-on not displayed | **High** | **High** | 📹 Video |
| BUG-02 | Far-future booking dates (2044) allowed | Medium | Medium | 📸 Screenshot |
| BUG-03 | ID upload accepts different person's name | **High** | **High** | — |
| BUG-04 | Surgery date accepted before date of birth | **High** | Medium | 📸 Screenshot |
| BUG-05 | "Confirm none apply" deselects all items | Medium | Medium | 📹 Video |
| BUG-06 | Tattoo healing window from questionnaire date, not MRI date | Medium | Medium | 📸 Screenshot |
| BUG-07 | Questionnaire validity not enforced for far-future scans | **High** | Medium | 📸 Screenshot |
| BUG-08 | No access to previously submitted questionnaire answers | Medium | Medium | — |
| BUG-09 | Aggregated locations hide valid per-scan locations | Medium | Medium | 📹 Video |
| BUG-10 | Partial scan cancellation not supported | Medium | Medium | — |
| BUG-11 | Weight accepts 1 kg; editing weight clears height field | Medium | Medium | 📸 + 📹 |
| BUG-12 | Saved payment card intermittently missing | Medium | Low | — |

---

*All bug evidence files are stored in `bug_resources/` relative to this document.*

