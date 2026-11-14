# 08 — Worked Synthetic Case: Affiliation Transition and Awarding-Authority Ambiguity

**Case ID:** TG-DEMO-001  
**Scenario family:** S4 — Affiliation / institutional relationship changes  
**Input mode:** Paired scan + structured record  
**Status:** Synthetic training example; no real candidate, institution, programme, regulator or source  
**Related standards:** TG-OPS-001 v0.1 and TG-OPS-002 v0.1

> **Synthetic warning:** All names, dates, institutions, orders and document contents below are invented for testing. The example certificate is not a valid academic document. No real university status or affiliation is asserted.

## 1. What this case is designed to test

A candidate claims a degree awarded in 2023 by a fictional university after studying at a fictional college whose affiliation changed during the candidate's study period.

The documents establish:
- an earlier affiliation relationship;
- a later affiliation relationship;
- a candidate-submitted certificate naming the earlier university as the awarding body.

But the supplied evidence does **not** establish what happened to students already enrolled when the affiliation changed. In particular, it does not establish whether the earlier university retained a teach-out arrangement, whether students were transferred, or which institution held the final award register for this candidate.

The correct system behaviour is to preserve the facts that are supported, show the unresolved question, and escalate. It must not infer fraud from the transition.

## 2. Fictional case facts

### Candidate's submitted claim

| Field | Submitted value |
|---|---|
| Candidate | Kavya Sharma (fictional) |
| Awarding institution claimed | Aster State University (fictional) |
| College | Northbridge College (fictional) |
| Qualification | Bachelor of Commerce |
| Study mode | Regular |
| Admission session | 2020–2021 |
| Study period claimed | 2020–2023 |
| Completion date | 30 June 2023 |
| Award date on submitted certificate | 15 August 2023 |
| Candidate roll reference | ASU-BCom-20-041 (fictional) |

The same values are supplied in a fictional scanned certificate and a structured JSON case record. The scan is visibly watermarked “SYNTHETIC — NOT A VALID ACADEMIC DOCUMENT.”

## 3. Evidence register

| Evidence ID | Synthetic source | Class | What it supports | What it does not establish |
|---|---|---|---|---|
| SYN-E01 | Aster State University archived affiliation register, fictional notice dated 10 July 2020 | C — Institution-issued | Northbridge College was listed as affiliated to Aster for sessions 2020–2021 and 2021–2022 | Whether existing students remained under Aster after the transition; whether this candidate's award was issued |
| SYN-E02 | Meridian University affiliation notification, fictional notice dated 20 June 2022, effective for session 2022–2023 | C — Institution-issued | Northbridge College's new affiliation to Meridian from the stated effective session | Student migration, teach-out arrangements, treatment of continuing cohorts or individual award authority |
| SYN-E03 | Fictional third-party college directory, captured 4 May 2024 | D — Third-party | A discovery lead that Northbridge is listed with Meridian | Independent corroboration: its page states it is based on SYN-E02 and is therefore derived |
| SYN-E04 | Candidate-submitted synthetic certificate image | E — Unverified submitted artefact until independently verified | What the submitted document represents: Aster as awarding body, BCom and award date | Whether Aster's register contains the award; whether certificate is authentic |
| SYN-E05 | Candidate-supplied synthetic structured record | E — Candidate-provided case input | The structured values supplied for comparison | Independent confirmation of the values |
| SYN-E06 | Synthetic issuer-response placeholder | — | No response received in this worked case | Silence does not confirm or disprove the award |

The evidence classes describe the source's role in this synthetic example. They do not certify the authority of any real organisation.

## 4. Source timeline

| Date / period | Event | Evidence |
|---|---|---|
| 10 July 2020 | Aster's fictional register lists Northbridge for sessions 2020–21 and 2021–22 | SYN-E01 |
| 2020–21 | Candidate's claimed admission session | Submitted claim |
| 2021–22 | Last session covered by SYN-E01 | SYN-E01 |
| 20 June 2022 | Meridian's fictional affiliation notification is issued | SYN-E02 |
| 2022–23 | New Northbridge–Meridian affiliation becomes effective | SYN-E02 |
| 30 June 2023 | Candidate's claimed completion date | Submitted claim |
| 15 August 2023 | Candidate's claimed award date | SYN-E04 / SYN-E05 |
| 4 May 2024 | Third-party directory is captured; it identifies Meridian and declares SYN-E02 as its basis | SYN-E03 |
| 14 November 2026 | Synthetic case is assessed for this walkthrough | Demonstration timestamp |

### What the timeline establishes

It establishes two sequential affiliation claims in the synthetic evidence set: Aster for 2020–21 and 2021–22, then Meridian from 2022–23.

### What it does not establish

It does not establish how the 2020–21 entrant's cohort was handled after the affiliation transition. It also does not establish which university's authorised register contains the candidate's award.

A temporal graph must not infer a cohort-level migration or teach-out rule merely from the date on which a new affiliation became effective.

## 5. Walkthrough against the case lifecycle

### State 1 — RECEIVED

- Case ID assigned: TG-DEMO-001.
- Purpose recorded: synthetic education-verification demonstration.
- Inputs: one synthetic PDF/image plus one synthetic JSON record.
- Receipt timestamp recorded in the case metadata.

**Result:** Pass.

### State 2 — AUTHORITY_CHECK

For this training case, the authority check is represented as a completed synthetic fixture. No real personal data is being processed.

A real case would require the BGV customer to document its purpose, applicable authority/instruction and candidate-facing process before processing.

**Result:** Pass for synthetic demonstration only.

### State 3 — INTAKE_VALIDATED

- Input formats are permitted by the synthetic test configuration.
- The artefact carries the synthetic warning.
- File hashes and receipt times are stored in the fixture.
- Original scan and JSON are retained separately from extracted values.
- No real certificate or personal identifier is present.

**Result:** Pass.

### State 4 — EXTRACTED

The fictional scan extraction yields the same core values as the JSON record:

| Field | Scan extraction | JSON value | Result |
|---|---|---|---|
| Candidate name | Kavya Sharma | Kavya Sharma | Match |
| Awarding institution | Aster State University | Aster State University | Match |
| College | Northbridge College | Northbridge College | Match |
| Programme | Bachelor of Commerce | Bachelor of Commerce | Match |
| Study mode | Regular | Regular | Match |
| Admission session | 2020–2021 | 2020–2021 | Match |
| Completion date | 30 June 2023 | 30 June 2023 | Match |
| Award date | 15 August 2023 | 15 August 2023 | Match |
| Roll reference | ASU-BCom-20-041 | ASU-BCom-20-041 | Match |

**Result:** No document/record mismatch in the synthetic fixture.

This does not make the document authentic. It only shows that two submitted inputs agree.

### State 5 — EVIDENCE_ASSEMBLED

The analyst links:
- the claimed awarding institution to Aster State University;
- the claimed college to Northbridge College;
- the earlier affiliation assertion to SYN-E01;
- the new affiliation assertion to SYN-E02;
- the third-party directory to SYN-E03 and marks its dependency on SYN-E02;
- the certificate and JSON to the submitted claim, not to an independently verified award record.

**Provenance check:** SYN-E03 is not an independent confirmation of SYN-E02. It reproduces the later affiliation claim and is marked DERIVED_FROM_KNOWN_SOURCE.

**Result:** The affiliation facts are assembled, but the responsible awarding entity for the continuing cohort is unresolved; individual award evidence is also absent.

### State 6 — ANALYST_REVIEW

| Question | Assessment | Why |
|---|---|---|
| Was Northbridge affiliated with Aster in the early claimed study period? | Supported by synthetic evidence | SYN-E01 covers 2020–21 and 2021–22 |
| Was Northbridge affiliated with Meridian from 2022–23? | Supported by synthetic evidence | SYN-E02 states the later effective session |
| Does the new affiliation automatically prove that the 2020 entrant transferred to Meridian? | Not established | No cohort-transfer or teach-out evidence is supplied |
| Does the earlier affiliation automatically prove Aster awarded this candidate's 2023 degree? | Not established | Affiliation evidence is not an individual award register |
| Does SYN-E03 independently corroborate the new affiliation? | No | It declares SYN-E02 as its source |
| Is the candidate's certificate independently authenticated? | No | It is only a candidate-submitted synthetic artefact |
| Is there evidence that the candidate committed fraud? | No | No such conclusion is supported by these facts |

### Primary outcome

<badge color="warning">EV-05 — Evidence insufficient</badge>

**Secondary observation:** EV-03 — Entity / awarding-authority ambiguity for the continuing cohort.

**Do not assign EV-02 temporal mismatch:** the two affiliation periods are sequential and can both be true. The missing fact is the treatment of continuing students and the awarding authority for this cohort, not necessarily a contradiction between the two dated orders.

**Do not assign EV-04 source conflict:** the third-party directory repeats the later order; it does not supply a contradictory independent assertion.

**Do not assign EV-06:** the scan and structured record agree in this synthetic case.

**Do not assign a fraud label:** the available facts do not establish candidate dishonesty or an inauthentic award.

## 6. Required escalation

### Primary question to Aster State University registrar

> For the fictional Bachelor of Commerce cohort admitted to Northbridge College in academic session 2020–2021 and completing in 2023, did Aster State University retain academic responsibility under a teach-out, transitional or other approved arrangement after Northbridge's affiliation with Meridian University became effective for session 2022–2023? If so, was Aster the awarding authority for this cohort, and does its official award register contain the submitted roll reference and award?

### Parallel question to Meridian University

> Did the 2022–2023 affiliation apply only to new admissions, or did it include continuing students admitted under the earlier affiliation? Was there an approved migration/transfer or cohort-specific arrangement, and which authority was responsible for final assessment and award for this cohort?

These are synthetic questions to demonstrate escalation. No real authority is being contacted.

### Evidence required to resolve

At least one appropriate authoritative response or record that directly addresses:
- the continuing cohort's academic status;
- any teach-out, migration or transition order;
- the awarding authority for this cohort;
- the individual candidate's award entry, where the issuer is authorised to confirm it.

A general institution-recognition page or a third-party directory is not enough to settle the individual award claim.

## 7. Example analyst report

**Case:** TG-DEMO-001  
**Preliminary outcome:** Evidence insufficient (EV-05)  
**Secondary outcome:** Evidence insufficient (EV-05) for individual award verification.

**Finding:** The submitted scan and structured case record agree on the candidate's stated institution, college, programme and dates. The synthetic evidence set records Northbridge College as affiliated with Aster State University for sessions 2020–21 and 2021–22, and with Meridian University from session 2022–23. The provided later directory entry derives from the Meridian affiliation notification and is not independent corroboration.

The available evidence does not describe how students admitted under the earlier affiliation were treated after the transition. It therefore does not establish which institution retained responsibility for this candidate's continuing cohort or which institution's official register should contain the 2023 award.

**Action required:** Obtain a cohort-specific transition/teach-out or migration record and direct confirmation from the appropriate awarding authority. Individual award verification remains outstanding.

**Limitation:** This is a synthetic evidence assessment. No real institution, recognition status, candidate identity or academic award has been checked.

## 8. Audit trail example

| Event | Actor | Record |
|---|---|---|
| Case created | System | Case ID TG-DEMO-001, synthetic purpose and receipt time |
| Inputs accepted | Operator | Synthetic scan and JSON file IDs, hashes and safety result |
| Fields extracted | Extraction service | Extracted values, confidence and source-field mapping |
| Sources linked | Analyst | SYN-E01 to SYN-E05 with scope, dates and source lineage |
| Dependency recorded | Analyst | SYN-E03 derives from SYN-E02 |
| Preliminary finding | Analyst | EV-05 primary, EV-03 secondary, with explanation |
| Escalation prepared | Analyst | Cohort transition and awarding-authority questions |
| Case state | System | Pending issuer/authority response; not closed as verified |

A real implementation must record actual timestamps, authenticated user IDs, access events and immutable/tamper-evident change history. The table above is only a training illustration.

## 9. What a good system must learn from this case

1. Two affiliations with different effective periods do not necessarily contradict one another.
2. A new affiliation does not, by itself, explain the treatment of already-enrolled students.
3. A college-affiliation record does not authenticate an individual degree.
4. A candidate-submitted document is a claim artefact until independently verified.
5. A third-party page derived from an official notice is not an independent second confirmation.
6. The correct outcome can be “evidence insufficient” even when several facts are established.
7. Escalation questions should target the exact missing fact, not request a broad “is this university valid?” response.
8. The system must not turn uncertainty into a fraud allegation.

## 10. Acceptance checklist for this worked case

The prototype passes this case only if it:
- [ ] preserves both affiliation intervals;
- [ ] relates the candidate's study dates to both intervals;
- [ ] does not infer that the cohort automatically transferred;
- [ ] distinguishes affiliation evidence from individual award verification;
- [ ] records SYN-E03 as dependent on SYN-E02;
- [ ] avoids treating matching scan/JSON fields as proof of authenticity;
- [ ] returns EV-03 as the primary outcome, with EV-05 for the separate individual-award scope;
- [ ] explains EV-03 as a secondary ambiguity;
- [ ] does not incorrectly return EV-02 or EV-04;
- [ ] generates a specific escalation question;
- [ ] avoids a fraud verdict.

**Expected result:** pass only when all applicable checks above are satisfied.
