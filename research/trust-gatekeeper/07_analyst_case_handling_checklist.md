# 07 — Analyst Case-Handling Checklist

**Document ID:** TG-OPS-002  
**Version:** 0.1  
**Use:** One checklist per education-verification case  
**Related standard:** 06 — Trust Gatekeeper Operational Standards  
**Status:** Research prototype checklist; not a production BGV SOP

> Use this checklist to ensure that the case is authorised, evidence is assessed within its proper scope and dates, and unresolved questions are escalated. A completed checklist is not itself proof that a degree is authentic.

---

## A. Case registration

**Case ID:** ____________________  
**Customer / tenant:** ____________________  
**Customer reference:** ____________________  
**Verification purpose:** ____________________  
**Analyst:** ____________________  
**Quality reviewer (if required):** ____________________  
**Received date/time and timezone:** ____________________  
**Input mode:** ☐ Scan ☐ Structured ☐ Paired  
**Standard version:** TG-OPS-001 v0.1  
**Rule / model version:** ____________________

- [ ] A unique case ID has been assigned.
- [ ] The requesting customer and business purpose are recorded.
- [ ] The customer has confirmed its authority/instruction to submit this case for the stated purpose.
- [ ] Any required candidate notice, consent or other applicable authority is documented by the customer.
- [ ] The case is not being used for a purpose outside the recorded instruction.
- [ ] Only the minimum fields required for this check have been collected.

**Gate A result:** ☐ Pass to intake ☐ Hold for authority confirmation ☐ Reject / close  
**Reason / notes:** ______________________________________________________

Do not process personal data if the required processing authority is not documented. Escalate the authority question to the customer; do not infer it.

## B. Intake and file safety

For each submitted file, record:

| File ID | File type | Size | SHA-256 | Received at | Malware / safety result |
|---|---|---:|---|---|---|
| | | | | | |
| | | | | | |

- [ ] File type and size are within configured limits.
- [ ] Files passed the configured malware/safety checks.
- [ ] Original files are preserved separately from extracted or transformed copies.
- [ ] A content hash and receipt timestamp are recorded.
- [ ] Files are stored in the authorised case location with access controls.
- [ ] No unneeded identity or contact information is copied into the case record.
- [ ] Any unsafe, malformed or out-of-policy file is quarantined or rejected.

**Gate B result:** ☐ Pass ☐ Hold ☐ Intake blocked  
**Reason / notes:** ______________________________________________________

## C. Credential claim capture

Capture what the candidate/case record claims. Do not silently convert a claim into a verified fact.

| Field | Claimed value | Input source | Confidence / uncertainty |
|---|---|---|---|
| Candidate display name | | | |
| Awarding institution | | | |
| College / affiliated institution | | | |
| Campus / location | | | |
| Programme / qualification | | | |
| Qualification level | | | |
| Study mode | | | |
| Admission date / session | | | |
| Study period | | | |
| Completion date | | | |
| Award date | | | |
| Roll / enrolment reference (only if necessary) | | | |

- [ ] Each value is traced to the input that supplied it.
- [ ] Original strings are preserved alongside any normalised value.
- [ ] Unreadable, absent or low-confidence fields are marked unknown.
- [ ] OCR confidence is not treated as proof of factual correctness.
- [ ] Scan-only, structured-only and paired-input modes are correctly identified.
- [ ] In paired mode, differences between scan and structured data are preserved, not overwritten.

## D. Document-to-record reconciliation

- [ ] Candidate name comparison reviewed.
- [ ] Awarding institution comparison reviewed.
- [ ] College / campus comparison reviewed.
- [ ] Programme and qualification comparison reviewed.
- [ ] Study mode comparison reviewed.
- [ ] Admission, completion and award dates compared.
- [ ] Roll / enrolment reference compared, if required and available.
- [ ] Each mismatch is classified as extraction uncertainty, formatting/normalisation difference, missing data or substantive disagreement.
- [ ] A visual document anomaly, if present, is recorded separately from institutional-status findings.
- [ ] No visual anomaly is translated directly into a fraud conclusion.

**Document/record result:** ☐ No material mismatch ☐ Mismatch ☐ Cannot assess  
**Finding code (if applicable):** ☐ EV-06  
**Details:** ____________________________________________________________

## E. Evidence collection and source qualification

Create one row for every material assertion. Add rows as needed.

| Evidence ID | Claim supported | Publisher / source | Class A–E | Effective period | Published / observed date | Dependency |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |

For each material source:

- [ ] Its identity and publisher are recorded.
- [ ] The exact claim it supports is stated.
- [ ] Its scope and limitations are recorded.
- [ ] Publication date is distinguished from effective/valid date.
- [ ] The capture/observation date is recorded.
- [ ] A permitted source copy, excerpt or reference is retained.
- [ ] A content hash is recorded where appropriate.
- [ ] Its relationship to other sources is classified: independent, derived, suspected dependent or unknown.
- [ ] A third-party directory is not treated as the sole authority for an award or regulatory claim.
- [ ] Missing or undated evidence is not interpreted as proof that the claim is false.

**Evidence sufficiency:** ☐ Sufficient for scoped question ☐ Insufficient ☐ Conflicting ☐ Not yet assessed

## F. Temporal and entity assessment

### Date questions
- [ ] Relevant admission session/date identified.
- [ ] Relevant study period identified.
- [ ] Completion and award dates identified, where available.
- [ ] Source effective period identified.
- [ ] Source publication date kept separate from effective period.
- [ ] Source observation/capture date kept separate from both.
- [ ] Academic-session precision preserved where exact dates are not stated.
- [ ] Current status has not been applied retrospectively.
- [ ] An unknown end date has not been interpreted as “valid forever.”

### Entity questions
- [ ] Awarding institution resolved or explicitly marked ambiguous.
- [ ] College / affiliation relationship resolved for the relevant period.
- [ ] Campus/location relationship checked if material.
- [ ] Programme and study mode checked separately if material.
- [ ] Rename, merger or successor relationship is supported by evidence, not name similarity alone.
- [ ] Recognition, accreditation, approval, affiliation and award verification have not been conflated.

**Temporal/entity result:**  
☐ Consistent for scoped check  
☐ EV-02 Temporal mismatch  
☐ EV-03 Entity ambiguity  
☐ EV-05 Evidence insufficient  
☐ EV-04 Source conflict

**Explanation and evidence IDs:** ________________________________________

## G. Preliminary outcome

Select the most appropriate primary outcome. Record secondary findings separately where needed.

- [ ] EV-01 — Evidence consistent
- [ ] EV-02 — Temporal mismatch
- [ ] EV-03 — Entity ambiguity
- [ ] EV-04 — Source conflict
- [ ] EV-05 — Evidence insufficient
- [ ] EV-06 — Document/record mismatch
- [ ] EV-07 — Intake blocked

**Primary outcome:** ____________________  
**Secondary finding(s):** ____________________  
**Reasoning:** _________________________________________________________  
**Evidence IDs relied upon:** ___________________________________________  
**Unresolved questions:** ______________________________________________

Before selecting EV-01:
- [ ] Required entities are resolved.
- [ ] Required time-bounded relationships are supported for the relevant period.
- [ ] Each source is appropriate for the claim it supports.
- [ ] No unresolved material source conflict exists.
- [ ] No unresolved document/record mismatch affects the scoped conclusion.
- [ ] The analyst records the limitations.
- [ ] The outcome is qualified: “Evidence consistent for the contextual checks performed; individual award verification is separate.”

## H. Escalation

Escalate when material evidence is missing, ambiguous, contradictory, undated, outside source scope, or could lead to an adverse BGV finding.

**Escalation required:** ☐ Yes ☐ No  
**Destination:** ☐ Issuing institution ☐ Regulator / statutory authority ☐ Affiliation authority ☐ Senior reviewer ☐ Customer  
**Specific question to resolve:** ________________________________________

- [ ] Question is specific and limited to the unresolved claim.
- [ ] Minimum necessary candidate information is included.
- [ ] Customer authority and permitted disclosure have been checked.
- [ ] Request date, channel and receiving authority are recorded.
- [ ] Response date, responder and response evidence are recorded.
- [ ] No response has not been treated as confirmation.
- [ ] Conflicting source records are preserved.
- [ ] Candidate correction / supplementary information route is available where relevant.

**Escalation status:** ☐ Not required ☐ Pending ☐ Responded ☐ Unresolved

## I. Human review and closure

- [ ] Analyst has written a plain-language explanation.
- [ ] A second reviewer has checked EV-02, EV-03, EV-04 and any candidate-adverse case.
- [ ] No automated outcome is being used as the sole basis for candidate rejection.
- [ ] Limitations and unverified claims are explicit.
- [ ] The customer receives only the permitted output for the recorded purpose.
- [ ] Case outcome, reviewer, rationale, unresolved items and closure time are recorded.
- [ ] Retention/deletion schedule is applied.
- [ ] Access and change events are logged.
- [ ] The current standard and rule/model versions are recorded.

**Final case status:** ☐ Closed — evidence report ☐ Closed — issuer verified separately ☐ Pending external response ☐ Returned for more information ☐ Blocked  
**Analyst sign-off:** ____________________ **Date:** __________  
**Quality reviewer:** ____________________ **Date:** __________

---

## J. Mandatory language check before report release

Confirm the report does **not** say:
- [ ] “Fake degree” unless a competent authority has made that determination and the customer has authorised its communication.
- [ ] “Fraudulent candidate.”
- [ ] “Invalid candidate.”
- [ ] “Verified degree” when only recognition or affiliation was assessed.
- [ ] “No record exists” when only limited sources were checked.

Preferred language:
- “The supplied evidence is consistent with the contextual checks described.”
- “The available sources do not establish the claimed relationship for the relevant period.”
- “The sources reviewed make conflicting statements.”
- “The available evidence is insufficient; issuer confirmation is required.”
- “A document/record field mismatch requires analyst review.”

**Operational note:** this checklist is a proposed research-prototype control. A real customer SOP must be adapted, legally reviewed and approved by the BGV organisation.
