# EACT-B5 Research Protocol
## Purpose-Bound Minimum Disclosure for Academic Credential Verification

**Experiment ID:** EACT-B5  
**Project:** CertiChain / Evidence-Aware Credential Triage (EACT)  
**Version:** 1.0  
**Scenario set:** B5-01 through B5-10  
**Data:** Fully synthetic  
**Status:** Prototype and deterministic experiment design

---

## 1. Research problem

Academic credentials often contain more information than a particular verifier needs. An employer checking whether a candidate has completed a BCA may ask for a complete transcript, raw CGPA, roll number, date of birth, address or a persistent student identifier. Some of these attributes may be unnecessary for the stated purpose. Even attributes that appear harmless in isolation can become identifying when combined or repeatedly presented.

The research problem is not simply whether a credential is authentic. It is how an issuer-holder-verifier system can provide enough evidence for a specific decision while reducing unnecessary disclosure, preserving holder agency, and limiting cross-context linkability.

A second tension is important: a verifier's request may be excessive, but a holder may still approve it. A privacy-aware system should make that excess visible rather than silently equating consent with necessity. Conversely, a holder's refusal to disclose a required attribute should result in an incomplete verification outcome, not an automatic fraud or misconduct label.

## 2. Research question

**RQ-B5:** How can a purpose-bound disclosure policy minimize the academic attributes presented to a verifier while retaining enough evidence to answer a legitimate qualification or eligibility request?

### Sub-questions

- RQ-B5.1: Can a purpose-specific policy distinguish minimum-required claims from optional and out-of-scope claims?
- RQ-B5.2: Can a threshold predicate (for example, CGPA at least 7.0) be represented without placing the raw CGPA in the proposed presentation?
- RQ-B5.3: How should the system respond when the holder withholds a required claim?
- RQ-B5.4: How can a request expose risks from persistent identifiers, attribute combinations, secondary use and unspecified retention?
- RQ-B5.5: What assurance is lost when a demonstration simulates selective disclosure without implementing cryptographic proofs?

## 3. Working hypotheses

- **H1 — Request/consent intersection:** A claim appears in the proposed presentation only when it is both requested by the verifier and approved by the holder.
- **H2 — Minimum evidence:** A policy can identify the smallest set of attributes and predicates needed for its defined purpose.
- **H3 — Predicate minimization:** A threshold outcome can be displayed without including the underlying raw CGPA in the proposed presentation.
- **H4 — Privacy warnings:** Out-of-purpose requests, excess disclosures, persistent identifiers, linkable presentation history, quasi-identifier combinations, secondary use and unspecified retention can be independently surfaced.
- **H5 — No false fraud inference:** Missing holder consent or an unsupported purpose must not be described as proof that a credential is fraudulent.

These are software-design hypotheses tested against authored fixtures. They are not empirical claims about real employers, students, universities or deployed credential ecosystems.

## 4. Proposed approach

EACT-B5 adds a policy-driven presentation layer on top of the evidence-oriented CertiChain work.

### 4.1 Actors

1. **Issuer:** A fictional university that asserts academic claims.
2. **Holder:** A fictional graduate or student who controls which attributes are approved for a presentation.
3. **Verifier:** A fictional employer, scholarship office, internship team or admissions office.
4. **Policy layer:** A prototype rule set mapping a declared purpose to minimum-required and allowed claims/predicates.

### 4.2 Credential claim inventory

The synthetic academic record contains:

- Award status
- Qualification level
- Programme name
- Awarding institution
- Graduation year
- Enrollment status
- Raw CGPA
- Detailed transcript / subject marks
- University roll number
- Date of birth
- Home address
- Personal email
- Persistent global student identifier
- Exact award date
- Campus

Each field receives an illustrative sensitivity category and an exposure weight. The weights are authored assumptions used only for comparing the same synthetic record under different disclosure selections. They are not a recognized privacy metric, legal classification, or calibrated re-identification probability.

### 4.3 Purpose policies

The initial policy fixtures cover:

| Purpose | Minimum claims | Predicate |
|---|---|---|
| Employment degree verification | Award status, qualification level, programme, institution | None |
| Scholarship eligibility | Award status, programme, institution | CGPA at least 7.0 |
| Internship enrollment | Enrollment status, programme, institution | None |
| Postgraduate admission | Award status, qualification level, programme, institution | CGPA at least 6.5 |

These are prototype policies, not universal statements about what any real employer, scholarship or university is entitled to request. Actual requirements require purpose-specific governance and legal/institutional review.

### 4.4 Evaluation sequence

1. Load a fictional credential and verifier request.
2. Select a declared purpose and look up its policy.
3. Check the fixture's issuer-trust and credential-status assertions.
4. Identify the policy's required and allowed claims/predicates.
5. Intersect requested claims with holder-approved claims.
6. Compute missing required evidence and claims outside the purpose policy.
7. Evaluate approved threshold predicates against hidden synthetic values.
8. Detect privacy findings, including persistent identifier use and selected quasi-identifier combinations.
9. Compare the proposed presentation with the full-record baseline.
10. Produce a disposition, evidence summary, privacy findings and recommended next steps.

The engine creates a presentation proposal for inspection. It does not send data to a verifier.

## 5. Scenarios

| ID | Scenario | Main question |
|---|---|---|
| B5-01 | Minimum degree proof for employment | Can the minimum policy be satisfied without extra claims? |
| B5-02 | Employer asks for the entire academic record | Does the system expose overcollection and sensitive disclosure? |
| B5-03 | Scholarship threshold without raw CGPA | Can a threshold result be presented without the raw score? |
| B5-04 | Internship checks current enrollment | Can enrollment be confirmed without transcript details? |
| B5-05 | Holder withholds a required claim | Is the result incomplete without accusing the holder of fraud? |
| B5-06 | Unscoped candidate profiling request | Does an unsupported purpose fail closed? |
| B5-07 | Global student ID requested | Is persistent identifier disclosure flagged? |
| B5-08 | Same global identifier links two verifiers | Does the history expose cross-verifier linkability? |
| B5-09 | Academic attributes combine into a fingerprint | Are combinations of quasi-identifiers surfaced? |
| B5-10 | Secondary use and unspecified retention | Does a new purpose require review, and is missing retention visible? |

## 6. Outcome measures

- **Fixture conformance:** number of authored cases whose actual disposition matches their expected disposition.
- **Minimum-claim completion:** whether every required claim is both requested and holder-approved.
- **Predicate completion:** whether each required predicate is requested, approved and satisfied.
- **Out-of-purpose request count:** requested claims outside the policy's allowed set.
- **Additional disclosure count:** proposed claims beyond the minimum-required set.
- **Sensitivity exposure:** count and illustrative weight of high-sensitivity claims proposed.
- **Record minimization:** proposed claim count and illustrative exposure units versus the full synthetic record.
- **Linkability findings:** persistent identifier requested/shared and cross-verifier history flags.
- **Inference findings:** combinations of quasi-identifiers in a proposed presentation.
- **Governance findings:** secondary purpose and retention period not specified.

The percentage reduction and exposure units are descriptive comparisons within this experiment only. They must not be presented as differential privacy, anonymity, or a formal privacy-risk score.

## 7. Threat model

### In scope

- Verifiers requesting more claims than the declared purpose policy allows.
- Holders approving more fields than are needed.
- Holders withholding minimum evidence.
- Stable identifiers enabling correlation across verifiers.
- Attribute combinations enabling inference or re-identification.
- Use beyond the declared purpose.
- Missing retention information.
- Unsupported purpose requests.

### Out of scope

- Malicious or compromised issuer signing keys.
- Forged cryptographic signatures or timestamp tokens.
- Wallet/device compromise and malware.
- Collusion between issuers and verifiers.
- Actual browser/device fingerprinting.
- Timing, network, transport and metadata side channels beyond the fixture flags.
- Formal anonymity, unlinkability or zero-knowledge security proofs.
- Legal entitlement to request or process any specific academic attribute.

## 8. Standards context and implementation boundary

The design is informed by the following standards as checked on **13 November 2026**:

1. **W3C Verifiable Credentials Data Model 2.0** — W3C Recommendation published 15 May 2025. It defines the VC data model and issuer-holder-verifier ecosystem, including security and privacy considerations. It does not mean that any arbitrary JSON filtering operation becomes a verifiable selective-disclosure presentation.
   - https://www.w3.org/TR/vc-data-model/
2. **IETF RFC 9901 — Selective Disclosure for JSON Web Tokens** — Proposed Standard published November 2025. It defines selective disclosure of individual elements of a JSON structure used in a JWS/JWT payload.
   - https://www.rfc-editor.org/rfc/rfc9901.html
3. **OpenID for Verifiable Presentations 1.0** — OpenID Final Specification published July 2025. It defines a protocol for requesting and presenting credentials; it is a presentation protocol, not itself a universal credential signature or privacy proof.
   - https://openid.net/specs/openid-4-verifiable-presentations-1_0.html
4. **SD-JWT-based Verifiable Digital Credentials (SD-JWT VC)** — IETF Internet-Draft. The datatracker listed revision 26, dated 6 November 2026, in IESG AD Followup at the time of this protocol. It is not labelled here as a finalized RFC.
   - https://datatracker.ietf.org/doc/draft-ietf-oauth-sd-jwt-vc/

### Explicit prototype boundary

The B5 engine:
- Reads fictional JSON fields.
- Uses purpose policy and holder selection to generate a filtered presentation proposal.
- Computes threshold results from hidden fixture values.
- Displays heuristic exposure comparisons and rule findings.

It does **not**:
- Create a signed W3C Verifiable Credential.
- Generate or verify an SD-JWT / SD-JWT VC.
- Generate or verify a zero-knowledge proof.
- Implement cryptographic holder binding or pairwise identifiers.
- Query revocation/status services or verify issuer trust.
- Connect to university student systems or real applicant data.

The phrase "predicate proof" in the interface refers to a simulated outcome only. A production implementation requires a suitable cryptographic credential format and verification library, key/issuer trust governance, holder binding, status checking, wallet/presentation protocol, replay and nonce protection, and privacy review.

## 9. Experiment procedure

1. Start the Streamlit app and open Privacy-Preserving Credential Lab.
2. Select B5-01 and confirm the minimum presentation contains only the four employment claims.
3. Select B5-02 and compare the full-record request with the out-of-purpose and high-sensitivity findings.
4. Select B5-03 and confirm the output shows the threshold result without raw CGPA.
5. Select B5-05 and verify that withholding a required claim yields an incomplete result without a fraud label.
6. Select B5-07 and B5-08 to inspect stable identifier and cross-verifier findings.
7. Select B5-09 to inspect quasi-identifier combination warnings.
8. Select B5-10 to inspect secondary-use and retention findings.
9. Edit the request/consent controls and observe how the proposed presentation changes.
10. Record results in EACT_B5_results_template.csv and save screenshots of representative cases.

## 10. Ethics and data handling

- Use only the committed fictional records.
- Do not upload real transcripts, roll numbers, student IDs, dates of birth or university database exports.
- Do not infer that a candidate is dishonest because they refuse optional or excessive requests.
- Do not use prototype dispositions in actual hiring, admissions, scholarship or disciplinary decisions.
- Any later participant study, university data access or institutional deployment requires appropriate authorisation and review.

## 11. Limitations and future work

Ten crafted fixtures do not establish accuracy in real hiring or university workflows. The purpose policies and sensitivity weights need review with students, employers, registrars, privacy professionals and institutional stakeholders. The model does not evaluate privacy leakage from credential metadata, repeated timing, issuer contact, wallet telemetry, verifier collusion or browser fingerprinting.

Future work should compare concrete credential formats and libraries, implement signed credentials and real selective-disclosure cryptography, test holder binding and revocation/status privacy, explore verifier-scoped identifiers, and study how holders understand requests and consent prompts. A later experiment should compare several policy strategies rather than assume one universal minimum for every institution or employer.

## 12. Expected contribution

EACT-B5 provides a reproducible synthetic framework for exploring the tension between verification sufficiency and unnecessary academic-data disclosure. It makes request scope, holder choice, predicate outcomes, persistent identifiers, attribute combinations, secondary use and retention visible as separate dimensions. It also deliberately marks the boundary between a policy-driven prototype and cryptographic selective disclosure.
