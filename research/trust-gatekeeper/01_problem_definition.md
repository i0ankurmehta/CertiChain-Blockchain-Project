# 01 — Problem Definition

**Version:** 0.1  
**Status:** Initial scope freeze for research design  
**Date:** 14 November 2026

## 1. Working title

**Temporal and Provenance-Aware Evidence Graphs for Explainable Academic Credential Risk Triage in Indian Background Verification**

## 2. Problem statement

Indian background-verification providers assess education claims using a mixture of candidate documents, structured candidate data, digital repositories, institutional databases, public regulatory information, third-party partners and direct issuer contact.

A difficult case may involve:
- an institution whose name, legal status, affiliation or successor relationship changed over time;
- a programme or study mode whose approval/recognition is session-specific;
- a mismatch between an awarding body, affiliated college, campus or programme;
- conflicting or stale evidence from multiple sources;
- multiple web pages that repeat one underlying notice rather than independently corroborating it;
- a scanned credential whose extracted fields disagree with the BGV case record.

The research problem is whether a **temporal and provenance-aware graph** can represent these facts and their sources in a way that improves preliminary analyst triage over simpler current-state lookups and static graph approaches.

This is an evidence-assessment problem, not a binary degree-fraud classification problem.

## 3. Initial customer and user

- **Initial customer segment:** Indian background-verification (BGV) companies.
- **Primary user:** education-verification analyst or reviewer.
- **Secondary user:** quality-control lead or BGV operations manager.
- **Buyer hypothesis:** BGV operations/product leadership may value reduced repetitive investigation and better auditability. This needs customer discovery; it is not yet validated.

## 4. Intended system role

CertiChain Trust Gatekeeper is a proposed analyst-assist layer that:
1. accepts scanned academic documents and/or structured education records;
2. extracts or ingests relevant credential fields;
3. links claims to institution, campus, college, programme, mode, awarding authority and time intervals;
4. records the source and lineage behind each assertion;
5. identifies temporal mismatches, entity ambiguity, source conflicts, dependent sources and missing evidence;
6. produces an explanation and a suggested next verification step for a human reviewer.

The system must keep separate:
- document appearance and field extraction;
- institutional/programme status evidence;
- relationships between institutions and awarding authorities;
- authenticity of the individual's specific award.

Only the issuing authority can verify an individual degree where that authority retains the student award record. UGC's FAQ states that the issuing university/institution verifies the degree itself, while UGC-DEB publishes the recognition status of HEIs and programmes for relevant periods. [1]

## 5. Initial geography and evidence context

**India only for the first research phase.**

The initial model must be able to represent session-specific recognition. UGC-DEB states that recognition status in a previous year does not establish recognition in the next session. It also explains that degree verification remains the responsibility of the issuing authority. [1][2]

DigiLocker-NAD is an existing national route for academic awards lodged by participating institutions. Its FAQ says the institution is responsible for the authenticity of award data. It permits digitised legacy data uploads, but scanned images/PDFs are not accepted as repository award data; the institution is responsible for digitisation. [3][4]

Therefore the initial product hypothesis is to complement authoritative digital verification routes and support evidence triage for cases that are not immediately resolved by them—not to replace DigiLocker-NAD or institutional verification.

## 6. Research questions

- **RQ1 — Temporal reasoning:** Does representing recognition, approval, affiliation and institutional identity as time-bounded relationships improve assessment of historical credential cases compared with current-state lookups?
- **RQ2 — Provenance:** Does explicit source lineage help distinguish independent corroboration from repeated or dependent claims?
- **RQ3 — Multi-format evidence:** Does combining scanned-document extraction with structured candidate records improve the detection and explanation of data inconsistencies?
- **RQ4 — Uncertainty:** Can explicit abstention reduce unsupported positive conclusions when evidence is incomplete, contradictory or ambiguous?

## 7. Hypotheses

- **H1:** On controlled synthetic cases with time-dependent status changes, temporal graph reasoning will make fewer temporal-validity errors than a current-state lookup and a static graph baseline.
- **H2:** Source-lineage modelling will identify more deliberately constructed dependent-source cases than a baseline that counts distinct URLs as separate corroboration.
- **H3:** Field-level reconciliation between scanned and structured inputs will identify injected inconsistencies, while preserving an explicit distinction between extraction error and underlying credential contradiction.
- **H4:** An abstention policy will reduce the error rate among cases on which the system makes a conclusive recommendation, at the cost of lowering coverage.

These are hypotheses for controlled evaluation, not claims of expected commercial performance.

## 8. Initial scope

### Included
- Indian higher-education credential cases in a synthetic benchmark.
- Scanned document inputs: generated PDF/image artefacts.
- Structured inputs: CSV and JSON records.
- Institution, awarding authority, affiliated college, campus, programme, qualification, study mode and relevant date intervals.
- Public-source evidence represented as synthetic source records during the first benchmark.
- Historical status, identity changes, source conflict, source dependency and document/record mismatch.
- Explainable findings and an evidence trail.
- Human review and escalation.

### Excluded from v0.1
- Real candidate personal data or genuine certificate scans.
- Live scraping or automated interpretation of regulator portals.
- Automated legal conclusions about recognition or equivalence.
- Automated candidate rejection, hiring recommendations or fraud verdicts.
- Issuing credentials, storing authoritative student records or replacing issuer checks.
- Blockchain, wallet, MPC, selective-disclosure or token features as part of the research contribution.
- Claims about savings, accuracy, or turnaround without a suitable real-world evaluation.

## 9. Output vocabulary

The first prototype should produce evidence states rather than a single opaque trust score:

- **Evidence consistent:** the available benchmark evidence supports the relevant claimed relationships and dates.
- **Temporal mismatch:** a time-bounded claim does not match the credential's relevant period.
- **Entity ambiguity:** the relevant institution, campus, programme or awarding relationship cannot be resolved confidently.
- **Source conflict:** sources make materially incompatible claims.
- **Evidence insufficient:** the supplied evidence does not establish the relevant claim.
- **Document/record mismatch:** extracted document fields differ from the associated structured record.

A visual anomaly is a separate document finding. It must not automatically become an institutional-status finding or a finding of candidate fraud.

## 10. Success criteria for this research phase

The foundation phase is successful only if it produces:
1. a documented competitor capability matrix grounded in public sources;
2. a defined ontology with explicit temporal and provenance semantics;
3. a reproducible synthetic benchmark specification with ground-truth labels;
4. baseline methods against which the proposed graph can be compared;
5. an evaluation plan that measures false-clear and false-flag errors separately and permits abstention;
6. a clear list of limits and claims that the synthetic study cannot support.

## 11. Risks and assumptions

- Publicly available product information may omit internal competitor capabilities. No absence-of-feature claim should be made without demonstrations, technical material or customer evidence.
- Public regulatory data may be incomplete, archived, ambiguous or difficult to interpret. Missing data must not be treated as proof of invalidity.
- Institutional recognition, programme approval, accreditation, affiliation and individual award verification are distinct concepts.
- Synthetic cases can demonstrate rule behaviour and controlled failure modes, but cannot validate performance on genuine documents or actual BGV operations.

## References

[1] UGC, Frequently Asked Questions — Distance Education: https://www.ugc.gov.in/Home/faq  
[2] UGC Distance Education Bureau, FAQ: https://deb.ugc.ac.in/FAQ  
[3] National Academic Depository, FAQ: https://www.nad.gov.in/faq.html  
[4] DigiLocker-NAD, FAQ: https://nad.digilocker.gov.in/faq

**Accessed:** 14 November 2026.
