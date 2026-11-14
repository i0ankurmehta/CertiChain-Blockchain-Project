# 06 — Trust Gatekeeper Operational Standards

**Document ID:** TG-OPS-001  
**Version:** 0.1 — proposed internal research-prototype standard  
**Date:** 14 November 2026  
**Status:** Draft; not a statutory standard, legal compliance certification or production operating procedure.

## 1. Purpose and governing rule

This document defines how the Trust Gatekeeper research prototype should accept a case, classify and preserve evidence, assess findings, escalate uncertainty, and protect information.

> **CertiChain may organise and assess evidence. It must not claim to authenticate an individual's academic award unless that award has been verified through an appropriate issuing-authority or authoritative digital-record process. It must not make an adverse candidate decision.**

This is an internal design standard. A real BGV deployment requires customer-specific legal, privacy, security and operational review.

## 2. Non-negotiable operating principles

1. **Purpose limitation:** process only data necessary for the specific education-verification task.
2. **Claim-specific authority:** a source is authoritative only for the claim it is competent to establish.
3. **Temporal correctness:** assess status against the relevant admission, study, completion or award period—not merely today's status.
4. **Provenance:** record where each material claim came from, when it was observed and whether it derives from another source.
5. **No evidence inflation:** different URLs are not automatically independent corroboration.
6. **Uncertainty is explicit:** missing, undated, ambiguous or conflicting evidence remains visible.
7. **Human accountability:** an authorised reviewer owns escalation and final BGV disposition.
8. **Candidate fairness:** a system finding is not a finding of dishonesty; an automated output must not be the sole basis for rejection.
9. **Reproducibility:** the same evidence and standard version should yield an explainable assessment.
10. **Separation of checks:** document appearance, extraction, institutional status, affiliation, programme approval and individual award verification are distinct.

## 3. Roles and responsibilities

| Role | Responsibility |
|---|---|
| BGV customer / case owner | Defines the purpose, supplies a documented lawful instruction, confirms authority to submit the case and owns the final BGV decision |
| Trust Gatekeeper operator | Validates intake and runs the approved workflow without altering source facts to force an outcome |
| Education-verification analyst | Reviews findings, assesses source relevance and decides what requires issuer or regulator follow-up |
| Quality reviewer | Reviews conflicting, ambiguous and adverse-looking cases |
| System administrator | Manages access, configuration, logging, backup and incident handling |
| Research / benchmark maintainer | Controls synthetic fixtures, labels, experiment versions and test splits |

For a real deployment, contracts must allocate data-protection roles, including whether the customer and service provider act as Data Fiduciary, Data Processor or another role under the law applicable at that time. Do not assume those roles without a documented assessment.

## 4. Case lifecycle and mandatory gates

A blocked or escalated state is a valid result. The system must not force every case to completion.

| State | Required action | Exit condition |
|---|---|---|
| RECEIVED | Assign unique case ID; record customer, purpose, input type and receipt time | Case is traceable |
| AUTHORITY_CHECK | Confirm the customer has documented the applicable legal basis, notice/consent or other required authority and permitted purpose | Authorised or blocked |
| INTAKE_VALIDATED | Validate file type, size, malware status, required fields and integrity | Inputs safe and structurally acceptable |
| EXTRACTED | Extract fields while retaining original values and extraction confidence | Fields available for review |
| EVIDENCE_ASSEMBLED | Link each material assertion to source, date, scope and lineage state | Evidence assessable or explicitly insufficient |
| ANALYST_REVIEW | Evaluate entities, relevant time intervals, conflicts and document/record differences | Preliminary outcome recorded |
| ESCALATION_REQUIRED | Route unresolved claims to issuer, authority or senior reviewer | Response recorded or case remains unresolved |
| CLOSED | Record outcome, reviewer, rationale, unresolved items and closure time | Audit record complete |

A case must be held at AUTHORITY_CHECK if processing authority is not documented. Unsafe, malformed or out-of-policy files must be quarantined or rejected at INTAKE_VALIDATED.

## 5. Minimum case intake

### 5.1 Required case metadata

- Unique case ID—not Aadhaar or another national identifier.
- Customer/tenant ID and requesting business unit.
- Declared verification purpose.
- Receipt timestamp.
- Input mode: scan, structured or paired.
- Customer confirmation of applicable processing authority.
- Customer case reference, only where needed for reconciliation.

### 5.2 Minimum credential fields

Where available and relevant:
- candidate display name as stated in the submitted record;
- awarding institution;
- affiliated/constituent college, if applicable;
- campus/location, where relevant;
- programme or qualification title and level;
- study mode (regular, ODL, online, etc.);
- admission session/date;
- study period or completion date;
- award date;
- roll/enrolment number only where necessary for issuer verification.

Do not collect Aadhaar, PAN, date of birth, home address, personal contact details or unrelated academic/financial data merely because they appear on a document. A customer must justify additional identifiers as necessary for the particular purpose.

### 5.3 Input handling

- Accept only configured file types and size limits.
- Preserve the received file hash and receipt time.
- Keep the original input separate from OCR output and normalised fields.
- Never silently overwrite source values during normalisation.
- Treat OCR as an extraction aid, not evidence that the extracted statement is true.
- Mark unreadable or low-confidence fields as unknown; do not guess.

## 6. Evidence-source standard

### 6.1 Classify each source by the claim it can support

| Evidence class | Typical source | Permitted use |
|---|---|---|
| A — Award-specific authoritative evidence | Issuing university/registrar confirmation; verified award record through an authorised official repository such as NAD/DigiLocker | Supports an individual-award verification claim, subject to identity matching and source scope |
| B — Statutory/regulatory evidence | UGC/UGC-DEB or relevant statutory council notification, order or recognition/approval list | Supports only regulatory or recognition claims within that authority's remit and relevant period |
| C — Institution-issued evidence | Official university circular, archived prospectus, affiliation order, programme notice or institutional record | Supports the specific institutional/programme/affiliation assertion described by that record |
| D — Third-party/commercial source | BGV provider, directory, aggregator, news report or secondary website | Discovery and corroboration lead; not sole basis for a conclusive regulatory or award claim |
| E — Unattributed/unverified source | Social-media post, forum, anonymous upload, unverifiable screenshot or unknown-origin document | Lead only; cannot independently support a conclusive outcome |

This is not a universal ranking. Source relevance depends on the claim. UGC distinguishes its recognition-status function from an issuing institution's responsibility for verifying an individual's degree. [1]

### 6.2 Required source record

For each material source, record where available:
- source ID and URI or documented non-web location;
- publisher, source type and evidence class;
- claim scope (what the source can and cannot establish);
- publication date as stated by the source;
- valid-from and valid-to dates, if stated;
- observed/captured timestamp;
- content hash of captured bytes or retained evidence artefact;
- relevant page, section, field or excerpt;
- parent/derived-from relationship, if known;
- review state and reviewer;
- limitations, missing dates and uncertainty notes.

If the source does not state a date, record it as undated. Do not invent publication or effective dates. Retain only source copies/excerpts the customer is permitted to retain. If full content cannot be retained, preserve a permitted reference, metadata and hash where lawful and technically appropriate.

### 6.3 Source independence and lineage

Classify the relationship between sources as:
- INDEPENDENT;
- DERIVED_FROM_KNOWN_SOURCE;
- DEPENDENCY_SUSPECTED;
- DEPENDENCY_UNKNOWN.

Two URLs are not two independent confirmations merely because their domains differ. Where a page reproduces an official circular, link it to that circular as a parent where known. If lineage cannot be established, use DEPENDENCY_UNKNOWN rather than assuming independence.

### 6.4 Source freshness

Do not apply one universal freshness period:
- A current portal page may be appropriate for current operational contact details.
- A historical recognition order may remain relevant to the period it expressly covers.
- A source captured years ago may be evidence of what it stated then, but must not be described as current.
- Re-check current-status assertions when the case depends on current status.
- Preserve historical snapshots and capture times; never silently replace them with newer pages.

## 7. Temporal assessment standard

1. Identify the date or academic session to which the relevant rule applies: admission, study, examination, completion or award.
2. Preserve source date precision: day, month, year, academic session or unknown.
3. Store valid time separately from observation time.
4. Apply a status only to the interval it supports.
5. Never infer that current recognition existed in earlier years.
6. Never infer that recognition in one academic session extends to the next.
7. Model programme, study mode, campus and affiliation separately where the source distinguishes them.
8. If the relevant date cannot be matched to the source period, return EVIDENCE_INSUFFICIENT or ENTITY_AMBIGUITY; do not guess.
9. A missing end date means the end date is unknown, not that status continued forever.
10. If a source uses an academic session, retain that session as stated rather than converting it to invented exact dates.

UGC-DEB states that recognition for a previous year does not imply recognition for the next session and provides session-specific guidance for ODL and online education. [2]

## 8. Entity and field matching

- Preserve original institution, college and programme strings.
- Maintain canonical IDs and aliases separately.
- Do not merge institutions on approximate name similarity alone.
- A rename, merger or successor relationship requires explicit supporting evidence or a human-reviewed identity link.
- Record the matching method: exact identifier, exact name plus corroborating fields, reviewed alias, fuzzy suggestion or unresolved.
- Fuzzy matching may suggest a candidate match but may never alone establish institutional identity.
- Candidate-name similarity is not sufficient to establish that two records belong to the same person.
- Preserve both values when OCR output and structured data disagree, including which input supplied each value.

## 9. Preliminary outcomes

| Code | Display label | Meaning | Required next action |
|---|---|---|---|
| EV-01 | Evidence consistent | Available evidence supports the contextual claims checked; it does not authenticate the individual's award | Complete issuer/award verification where required |
| EV-02 | Temporal mismatch | Dated evidence is inconsistent with the relevant credential period | Human review; obtain governing historical order/confirmation |
| EV-03 | Entity ambiguity | Institution, college, campus, programme or successor identity is unresolved | Obtain authoritative identity/affiliation evidence |
| EV-04 | Source conflict | Material sources make incompatible assertions | Preserve both sources and escalate |
| EV-05 | Evidence insufficient | Evidence is unavailable, undated, out of scope or insufficiently authoritative | Request issuer/regulator confirmation or additional records |
| EV-06 | Document/record mismatch | Extracted document fields differ materially from structured case data | Review original document and source record |
| EV-07 | Intake blocked | Input is unsafe, malformed or processing authority is undocumented | Do not process; return to case owner |

### 9.1 Conditions for EV-01

EV-01 may be used only when:
- relevant entities are resolved;
- material time-dependent relationships are supported for the period in question;
- each source is appropriate for the claim it supports;
- no unresolved material conflict exists;
- no unresolved document/record mismatch affects the conclusion;
- the analyst records evidence and limitations.

Required qualification:

**“Evidence consistent for the contextual checks performed; individual award verification is separate.”**

### 9.2 Prohibited outputs

Do not use:
- “Fake degree”;
- “Fraudulent candidate”;
- “Invalid candidate”;
- “University is fake” based only on a missing registry result;
- “Verified degree” when only institution/programme recognition was checked;
- an opaque trust score or probability unless a later calibrated and independently evaluated method supports it.

“Not found” means not found in the sources checked. It does not mean false.

## 10. Human review and escalation

Mandatory escalation applies when:
- material sources disagree;
- the source lacks dates needed to assess historical applicability;
- identity, rename, merger or successor status is unresolved;
- programme, campus, study mode or affiliation is material but undocumented;
- OCR uncertainty affects a critical field;
- candidate and structured-record details conflict;
- the case could lead to an adverse BGV finding;
- a source appears altered, unauthenticated or outside its stated scope.

Escalation destination:
- **Individual award/student record:** issuing university or authorised awarding institution.
- **Recognition/programme approval:** relevant regulator or statutory authority.
- **Affiliation/campus/institution identity:** issuing university, statutory authority or body that issued the relevant order.
- **Unresolved conflict:** senior BGV reviewer; seek the original order or direct confirmation.

Record the question asked, authority contacted, request/response dates, responder/source, response evidence and result. If no response is received, the case remains unresolved; silence is not confirmation.

## 11. Candidate fairness and correction

For a real deployment:
- The BGV customer must define how the candidate is informed about the check and how the candidate can provide missing or corrected information.
- A preliminary machine finding must not be the sole basis for rejecting employment, admission or another opportunity.
- Material adverse-looking findings require human review and a documented rationale.
- Provide a correction route for OCR mistakes, name variants, date mapping errors and incomplete source coverage.
- Distinguish a candidate-provided discrepancy from an independently established contradiction.
- Do not infer intent or dishonesty from inconsistency.

These are product safeguards. Their exact legal implementation must be reviewed against the law and contracts applicable to the deployment.

## 12. Privacy and data minimisation

### Research prototype
- Use fabricated identities, institutions and source records only.
- Do not upload genuine candidate documents or university records.
- Do not connect real BGV systems or scrape personal records.
- Do not reuse candidate data to train models.

### Future controlled deployment

Before processing real personal data:
1. document customer and service-provider roles;
2. document the specific purpose and applicable legal basis;
3. obtain customer-approved candidate notice/consent or other required authority;
4. define necessary fields and reject unrelated data;
5. define access roles, approved subprocessors and hosting locations;
6. define retention/deletion for source documents, extracted fields, evidence copies, logs and backups;
7. provide escalation and grievance paths;
8. review cross-border transfers and vendor terms;
9. complete security/privacy assessment and obtain legal approval.

**Legal timing caution (India, 14 November 2026):** the DPDP Act and Rules have staged commencement notifications. The Act's commencement schedule places sections 7–17 among provisions scheduled to commence eighteen months after the 13 November 2025 notification (13 May 2027). The Rules also have phased commencement. Do not assume every DPDP obligation—or the employment-related legitimate-use provision in section 7(i)—is already operative on this document's date. Equally, do not assume no privacy obligations apply: counsel must map the provisions and other applicable law actually in force for the specific processing date and data flow. [3][4][5]

This document does not decide whether consent or a particular lawful basis is required in an individual BGV use case.

## 13. Security and audit controls

Minimum design controls before any real-data pilot:
- encryption in transit and at rest;
- tenant separation;
- role-based least-privilege access;
- multifactor authentication for privileged users;
- secrets stored outside source control;
- secure upload validation and malware scanning;
- access logs for viewing, exporting, changing and deleting case information;
- append-only or tamper-evident audit records for assessment changes;
- backups with tested restoration and defined deletion handling;
- incident-response ownership and notification workflow;
- dependency and vulnerability management;
- no external AI/OCR provider receives case documents unless the customer has approved the provider, data flow, contract and retention terms.

CERT-In's 28 April 2022 directions require specified covered entities, including service providers and body corporates, to enable ICT logs and maintain them securely for a rolling 180 days within Indian jurisdiction. Applicability and scope must be assessed for the actual entity/system. This is not a direction to retain every candidate document for 180 days; security-log retention and case-record retention are separate decisions. [6]

## 14. Quality assurance

- Every output records standard version, rule/model version, source set and assessment timestamp.
- Every material finding links to supporting evidence or explicitly states that supporting evidence is absent.
- A reviewer can reproduce the assessment from retained, permitted evidence.
- All EV-02, EV-03, EV-04 and candidate-adverse cases require second-person review in a real workflow.
- Benchmark labels are reviewed independently from the code that produces system results.
- Track false-clear, false-flag, abstention, unresolved-case and correction rates separately.
- Do not publish overall accuracy without scenario-level results.
- Changes to ontology, source classes, outcome definitions or rules require versioning and regression tests.

## 15. Retention and deletion

This standard does not prescribe a universal retention period.

For each deployment, the customer must approve a schedule for:
- original candidate documents;
- extracted and normalised fields;
- source evidence and permitted snapshots;
- analyst notes and outcomes;
- access/security logs;
- backups and derived artefacts.

At the end of the approved period, delete or irreversibly de-identify relevant records according to applicable law, contract and legal-hold requirements. Do not retain candidate data “just in case.” Hashes and pseudonymous IDs are not automatically anonymous if they remain linkable to a person.

## 16. Operational metrics

Track separately:
- cases blocked at intake;
- cases requiring manual review;
- cases escalated to issuer/regulator;
- time from receipt to first evidence report;
- time waiting on external authority;
- findings with a source link and capture date;
- unresolved source-conflict rate;
- OCR critical-field correction rate;
- candidate/case correction rate;
- false-clear and false-flag rate on labelled benchmark cases;
- abstention rate and coverage.

Do not promise savings or turnaround SLAs until a real workflow baseline and controlled pilot measure them.

## 17. Operational release gates

| Gate | Required evidence |
|---|---|
| O1 — Synthetic-only research | Fixtures clearly synthetic; no personal data; lifecycle and labels reproducible |
| O2 — Internal demo | Source traceability, date handling, abstention and audit records work on benchmark cases |
| O3 — Controlled BGV pilot | Customer authority, legal/privacy review, security controls, human-review workflow, retention schedule and incident plan approved |
| O4 — Production | Independent security review, operational support, monitoring, access review, change control, resilience and measured pilot performance |

The current track is at **O1 design stage only**. No production-readiness or compliance claim is permitted.

## 18. References

[1] UGC, FAQ — recognition status versus individual degree verification: https://www.ugc.gov.in/Home/faq  
[2] UGC Distance Education Bureau, FAQ — session-specific recognition and ODL/online requirements: https://deb.ugc.ac.in/FAQ  
[3] Digital Personal Data Protection Act, 2023, official MeitY text: https://www.meity.gov.in/static/uploads/2024/02/Digital-Personal-Data-Protection-Act-2023.pdf  
[4] DPDP Act commencement notification, G.S.R. 843(E), 13 November 2025: https://indiacode.ecourtsindia.com/rules/enforcement-timeline-for-the-dpdp-act-e1be0965/  
[5] Digital Personal Data Protection Rules, 2025, G.S.R. 846(E), 13 November 2025: https://upload.indiacode.nic.in/showfile?actid=AC_CEN_45_0_00003_2023-22_1763464807080&filename=dpdprules2025.pdf&type=rule  
[6] CERT-In Directions under section 70B, 28 April 2022: https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf  
[7] National Academic Depository, FAQ — institution responsibility for award data: https://www.nad.gov.in/faq.html

**Accessed:** 14 November 2026.
