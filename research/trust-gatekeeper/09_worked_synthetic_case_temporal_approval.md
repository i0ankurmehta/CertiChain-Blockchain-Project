# 09 — Worked Synthetic Case: Later Programme Approval and Source Dependency

**Case ID:** TG-DEMO-002  
**Scenario families:** S2 — Changed recognition; S3 — Programme/mode mismatch; S7 — Dependent sources  
**Input mode:** Paired scan + structured record  
**Status:** Synthetic training and benchmark case; no real candidate, institution, regulator, programme or source  
**Related standards:** TG-OPS-001 v0.1, TG-OPS-002 v0.1 and TG-BENCH-001 v0.1

> **Synthetic warning:** All names, dates, bodies, orders and documents are invented. The submitted document must carry the visible watermark “SYNTHETIC — NOT A VALID ACADEMIC DOCUMENT.” Nothing in this case describes or implies the status of a real institution or programme.

---

## 1. Purpose of the case

This case tests a specific failure of current-state lookup:

A fictional university's online programme is approved for admissions in a later academic session. A candidate claims admission in an earlier session. Several current directory pages display the programme as “approved,” but each page derives from the same later approval notice.

The system must:
- assess approval against the candidate's admission session;
- distinguish current status from historical applicability;
- detect the source lineage behind repeated directory entries;
- avoid counting copied pages as independent corroboration;
- separate the programme-status finding from the authenticity of the candidate's individual award.

The case is designed so that a current-state lookup or static graph can make a plausible but incorrect positive inference if it ignores time.

## 2. Fictional candidate claim

| Field | Submitted value |
|---|---|
| Candidate | Dev Malhotra (fictional) |
| Awarding institution claimed | Rivergate University (fictional) |
| Programme | Bachelor of Business Administration |
| Study mode | Online |
| Admission session | 2021–2022 |
| Completion date claimed | 30 June 2024 |
| Award date claimed | 20 August 2024 |
| Candidate reference | RG-BBA-ON-21-118 (fictional) |

The synthetic scanned certificate and structured JSON record agree on these values. The document is watermarked and must not resemble a real university certificate.

## 3. Synthetic authority and source records

For this case only, an invented authority called the **Aster Academic Programme Authority (AAPA)** publishes a fictional programme approval notice.

| Evidence ID | Synthetic source | Class | Statement represented | Limitation |
|---|---|---|---|---|
| SYN2-E01 | AAPA Order AAPA/ONL/22-23/014, dated 12 July 2022 | B — Statutory/regulatory fixture | Rivergate University's BBA Online programme is approved for new admissions in academic session 2022–2023 only; the order states that approval is not retrospective and does not cover earlier admission sessions | It does not verify any individual student's award |
| SYN2-E02 | AAPA session register, captured 10 November 2026 | B — Statutory/regulatory fixture | Current programme listing shows BBA Online as approved, with effective session 2022–2023 | A current listing must not be applied to 2021–2022 |
| SYN2-E03 | EduIndex directory page, captured 10 November 2026 | D — Third-party | Displays Rivergate BBA Online as “approved”; footer states it is based on AAPA session register SYN2-E02 | It is derived from SYN2-E02 and has no separate historical approval evidence |
| SYN2-E04 | CampusCourse directory page, captured 11 November 2026 | D — Third-party | Displays the same “approved” label; page cites EduIndex and the AAPA register | It derives from SYN2-E03 and ultimately SYN2-E02; not independent corroboration |
| SYN2-E05 | Candidate-submitted synthetic certificate scan | E — Submitted artefact | Shows the candidate's stated institution, programme, mode and award date | Does not authenticate the award or establish historical approval |
| SYN2-E06 | Candidate-supplied structured JSON record | E — Candidate-provided input | Supplies the same candidate and credential fields for reconciliation | Not independent verification |
| SYN2-E07 | Issuer award-register confirmation | — | Not supplied in this case | Individual award verification remains outstanding |

These are invented fixtures. Source classes indicate the role each fictional source is designed to play; they do not assign real authority to any actual organisation.

## 4. Timeline

| Date / period | Event | Evidence |
|---|---|---|
| 2021–2022 | Candidate's claimed admission session | SYN2-E05 / SYN2-E06 |
| 12 July 2022 | AAPA publishes Order AAPA/ONL/22-23/014 | SYN2-E01 |
| 2022–2023 | The order's explicitly stated approval period for new admissions | SYN2-E01 |
| 30 June 2024 | Candidate's claimed completion | SYN2-E05 / SYN2-E06 |
| 20 August 2024 | Candidate's claimed award date | SYN2-E05 / SYN2-E06 |
| 10 November 2026 | Current session register is captured | SYN2-E02 |
| 10 November 2026 | EduIndex page is captured | SYN2-E03 |
| 11 November 2026 | CampusCourse page is captured | SYN2-E04 |
| 14 November 2026 | Case is assessed in this synthetic walkthrough | Demonstration timestamp |

## 5. Intake and field reconciliation

### Case authority and intake

For this example, processing authority is represented as a completed synthetic fixture. No real personal data is used.

- [x] Unique case ID assigned.
- [x] Purpose recorded as synthetic education-verification research.
- [x] Synthetic scan and JSON received.
- [x] Files labelled as synthetic.
- [x] Original inputs separated from extracted fields.
- [x] Receipt times and content hashes recorded in the fixture.

**Intake result:** Pass for synthetic demonstration only.

### Scan-to-JSON comparison

| Field | Scan extraction | Structured JSON | Result |
|---|---|---|---|
| Candidate | Dev Malhotra | Dev Malhotra | Match |
| Awarding institution | Rivergate University | Rivergate University | Match |
| Programme | BBA | BBA | Match |
| Study mode | Online | Online | Match |
| Admission session | 2021–2022 | 2021–2022 | Match |
| Completion date | 30 June 2024 | 30 June 2024 | Match |
| Award date | 20 August 2024 | 20 August 2024 | Match |

**Document/record result:** No material mismatch in the synthetic fixture.

This is only agreement between two submitted representations. It is not evidence that either representation is true.

## 6. Provenance and dependency analysis

The source lineage is:

```text
AAPA Order SYN2-E01
        |
        v
AAPA session register SYN2-E02
        |
        v
EduIndex page SYN2-E03
        |
        v
CampusCourse page SYN2-E04
```

For the benchmark, the dependency is explicitly known:
- SYN2-E02 records the AAPA order.
- SYN2-E03 states that it uses SYN2-E02.
- SYN2-E04 cites SYN2-E03 and SYN2-E02.

Therefore, the three current pages do **not** represent three independent confirmations of historical approval. They are one underlying approval assertion repeated through a source chain.

The system should retain all source records, because they may help locate the original. It should not multiply confidence merely because several pages repeat the same result.

## 7. Temporal assessment

The credential claim states admission in session 2021–2022.

The AAPA order states:
- approval is for new admissions in session 2022–2023;
- approval is not retrospective;
- earlier admission sessions are outside the order's scope.

The current register's “approved” label is consistent with the later approval. It does not establish approval for the candidate's earlier 2021–2022 admission session.

### Claim-by-claim assessment

| Question | Finding | Reason |
|---|---|---|
| Is Rivergate University's BBA Online programme listed as approved in the later session? | Supported by the synthetic evidence | SYN2-E01 and SYN2-E02 |
| Does that approval cover the candidate's 2021–2022 admission session? | No, the order expressly excludes earlier admissions | SYN2-E01 |
| Do the third-party pages independently establish earlier approval? | No | SYN2-E03 and SYN2-E04 derive from the same later approval assertion |
| Does this establish that the candidate's degree is fraudulent or never issued? | No | Programme approval evidence is not the individual award register |
| Is the candidate's award independently verified? | No | SYN2-E07 is absent |

### Primary preliminary outcome

<badge color="warning">EV-02 — Temporal mismatch</badge>

The programme approval evidence supplied for this case does not cover the claimed 2021–2022 admission session. The 2022–2023 approval is expressly non-retrospective in the fictional order.

### Secondary outcome

**EV-05 — Evidence insufficient for individual award verification.**

The available evidence does not establish whether Rivergate University's official award register contains the candidate's claimed award.

### Source dependency finding

SYN2-E03 and SYN2-E04 are dependent on SYN2-E02/SYN2-E01. They must not be counted as independent corroboration.

## 8. Why this is not a fraud finding

The evidence supports a specific temporal discrepancy between:
- the candidate's claimed admission session; and
- the effective scope of the supplied programme approval order.

It does not establish:
- whether another approval or transitional arrangement existed;
- whether an authority issued a separate cohort-specific direction;
- whether the candidate was admitted under a different lawful arrangement;
- whether the candidate's award exists in the issuer's records;
- whether the candidate knew of any programme-status issue or intended to misrepresent anything.

The appropriate next step is to obtain authoritative clarification, not to label the candidate fraudulent.

## 9. Escalation questions

### To the fictional programme authority

> Does any separate order, approval, transitional direction or cohort-specific arrangement authorise Rivergate University's BBA Online admissions for academic session 2021–2022? The supplied fictional Order AAPA/ONL/22-23/014 states that its approval begins in 2022–2023 and is not retrospective. Please identify any applicable earlier order or confirm the scope of the supplied order.

### To Rivergate University's registrar

> For candidate reference RG-BBA-ON-21-118, please confirm the admission session and study mode recorded by the institution, the authority under which the candidate was admitted, and whether the institution's official award register records the claimed 2024 BBA award. Please identify any cohort-specific approval or transition arrangement relied upon.

These questions are fictional examples, not real communications.

## 10. Expected analyst report

**Case:** TG-DEMO-002  
**Primary outcome:** EV-02 — Temporal mismatch  
**Secondary outcome:** EV-05 — Evidence insufficient for individual award verification  
**Source-lineage note:** Three displayed web records trace back to one underlying fictional approval order and are not independent confirmations.

**Finding:** The submitted scan and structured case record agree that the candidate claims admission to Rivergate University's BBA Online programme in academic session 2021–2022. The supplied fictional AAPA Order AAPA/ONL/22-23/014 states that programme approval applies to new admissions in academic session 2022–2023 only and is not retrospective. The current AAPA register and two third-party directory pages show a later approval status, but the directory pages derive from the same underlying order and do not establish approval for the earlier admission session.

**Action required:** Obtain any separate order or cohort-specific transitional authority applicable to the 2021–2022 admission session. Separately verify the candidate's individual award with the issuing institution.

**Limitation:** This is a synthetic evidence assessment only. No real institution, regulator, candidate or academic award has been checked.

## 11. Baseline comparison — expected behaviour

This table describes expected behaviour under the simplified methods in the benchmark protocol. It is a design expectation to be tested, not an observed result.

| Method | Expected behaviour on this case | Failure or value being tested |
|---|---|---|
| B0 — Field/schema matching | Finds no scan-to-JSON mismatch | Cannot assess historical approval from matching fields |
| B1 — Current-state lookup | May incorrectly report programme approved if it checks only current status | Current status is not historical applicability |
| B2 — Static graph | May see an approval relationship without its effective interval | Relationship existence is not enough |
| B3 — Temporal graph | Identifies that the supplied approval interval does not cover 2021–2022 | Tests time-bounded relation reasoning |
| B4 — Temporal + provenance | Identifies the same temporal mismatch and marks E03/E04 as dependent sources | Tests source lineage and avoids evidence inflation |
| B5 — B4 + abstention | Gives EV-02 for the supplied programme-status claim, but abstains from an individual-award authenticity conclusion | Tests scoped conclusion and uncertainty handling |

A positive result would require B3 to outperform B1/B2 on the intended temporal question and B4 to correctly report source dependency. No measured result is claimed by this specification.

## 12. Acceptance criteria

The case passes only if the system:
- [ ] identifies the claimed admission session as 2021–2022;
- [ ] retains the approval's 2022–2023 effective session and non-retroactive scope;
- [ ] does not apply the current approved status to the earlier session;
- [ ] identifies E03 and E04 as dependent on the same underlying evidence;
- [ ] does not count three URLs as three independent approvals;
- [ ] preserves the scan/JSON agreement without treating it as authenticity proof;
- [ ] returns EV-02 for the programme-session mismatch;
- [ ] separately states that individual award verification remains outstanding (EV-05);
- [ ] does not infer fraud or automatically reject the candidate;
- [ ] produces a targeted issuer/authority escalation question.

**Expected result:** pass only when all applicable checks are satisfied.
