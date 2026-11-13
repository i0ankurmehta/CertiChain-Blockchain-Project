# EACT-B5 Research Note
## Purpose-Bound Minimum Disclosure for Academic Credential Verification

**Draft status:** Research design and prototype specification. Empirical and UI observations are pending.

### Abstract

Academic credentials can contain substantially more information than is necessary for a particular verification purpose. This experiment investigates a purpose-bound minimum-disclosure layer for academic credential presentations. A synthetic issuer-holder-verifier model is used to compare a complete academic-record baseline with a holder-approved presentation proposal. Four verifier purposes are modelled: employment degree verification, scholarship eligibility, internship enrollment and postgraduate admission. Ten synthetic scenarios explore overbroad requests, threshold predicates, incomplete consent, unsupported purposes, persistent identifiers, cross-verifier linkability, quasi-identifier combinations, secondary use and retention transparency.

The prototype intersects verifier-requested claims with holder-approved claims, compares them with purpose-specific minimum and allowed sets, and emits independent privacy findings. It also computes threshold outcomes from hidden synthetic values without adding the raw CGPA to the proposed presentation. These outcomes are policy simulations, not cryptographic zero-knowledge proofs. The experiment is designed to test deterministic fixture conformance and expose the trade-offs between evidence sufficiency and data minimisation. It does not establish production security, cryptographic assurance or compliance with any jurisdiction's law.

### 1. Introduction

Academic verification commonly occurs in situations where the verifier's decision may require fewer attributes than exist in the underlying student record. A degree check, for example, may need to establish the awarded qualification and issuer, while the complete transcript, date of birth, home address or persistent student identifier may not be necessary. Selective disclosure and purpose limitation provide a technical direction, but a verifier's request, a holder's consent, and a cryptographically valid presentation are distinct concerns.

This work extends CertiChain's EACT research from authenticity, evidence provenance and trust-anchor lifecycle toward information minimisation during presentation.

### 2. Research question

How can a purpose-bound disclosure policy minimize the academic attributes presented to a verifier while retaining enough evidence to answer a legitimate qualification or eligibility request?

### 3. Method

A deterministic Python rules engine evaluates ten fictional scenarios using four purpose policies. It compares the requested attribute set, holder-approved attribute set, policy minimum, issuer trust assertion, credential status, predicate request, declared secondary use and retention metadata. A Streamlit interface exposes the decision process. An automated test suite checks expected outcomes and privacy-specific edge cases.

### 4. Proposed contribution

The prototype separates:
- requested claims from holder-approved claims;
- minimum-required claims from optional or out-of-purpose claims;
- raw score disclosure from a simulated threshold predicate;
- issuer trust from data minimisation;
- stable identifier use from verifier-scoped presentation intent;
- primary verification purpose from secondary use and retention.

### 5. Standards relationship

The design is informed by W3C Verifiable Credentials Data Model 2.0, IETF RFC 9901, OpenID for Verifiable Presentations 1.0 and the SD-JWT VC Internet-Draft. The implementation does not claim conformance to these standards. It does not construct signed credentials, SD-JWTs or cryptographic proofs.

### 6. Planned evaluation

The initial evaluation comprises ten authored synthetic fixtures and unit tests. Measures include fixture conformance, minimum-claim completion, predicate completion, out-of-purpose request count, additional disclosure count, high-sensitivity disclosure, heuristic exposure reduction, linkability findings, re-identification warnings, secondary-use warnings and retention transparency.

### 7. Results

**Pending.** Do not insert a fixture pass rate or privacy improvement claim until the test suite and local UI scenarios have been executed and recorded.

### 8. Limitations

The purpose policies and sensitivity weights are design assumptions. The synthetic engine does not validate issuer signatures, identity binding, consent authenticity, credential status or a live trust registry. The predicate evaluation reads a hidden synthetic field and is not a zero-knowledge proof. The ten scenarios are not a representative user study.

### 9. Future research

Future work should compare concrete SD-JWT and W3C VC selective-disclosure implementations, test holder binding and privacy-aware status checking, measure re-identification under realistic attribute combinations, and conduct authorised usability research with students and verifiers.

### References

1. W3C, Verifiable Credentials Data Model v2.0, Recommendation, 15 May 2025. https://www.w3.org/TR/vc-data-model/
2. D. Fett, K. Yasuda and B. Campbell, RFC 9901, Selective Disclosure for JSON Web Tokens, November 2025. https://www.rfc-editor.org/rfc/rfc9901.html
3. OpenID Foundation, OpenID for Verifiable Presentations 1.0, Final Specification, July 2025. https://openid.net/specs/openid-4-verifiable-presentations-1_0.html
4. IETF OAuth Working Group, SD-JWT-based Verifiable Digital Credentials, Internet-Draft. https://datatracker.ietf.org/doc/draft-ietf-oauth-sd-jwt-vc/
