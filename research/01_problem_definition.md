# Research Study: Evidence-Aware Academic Credential Verification for SME Hiring in India

**Working title:** *Evidence-Aware Academic Credential Verification for Resource-Constrained Employers: A Design-Science Study in India's Mixed Digital Credential Ecosystem*

**Project:** CertiChain / EREBUS_v027  
**Author:** Ankur Mehta  
**Programme:** BCA Computer Science, 5th Semester  
**Course:** Blockchain Technology  
**Supervisor:** Assistant Professor Ms. Meetali

## 1. Research situation

Consider a small or medium-sized IT employer in Punjab screening an entry-level developer. An applicant presents a portfolio containing:

1. A university degree or marksheet that may be available through DigiLocker / the National Academic Depository (NAD).
2. A professional or micro-credential issued by an external training provider.
3. A certificate PDF from a small training provider without an independently accessible verification service.

The recruiter has limited time and cannot assume that every issuer uses the same repository, signature format, status endpoint, or consent process. The recruiter also should not collect more personal information than the hiring decision requires.

This is a realistic mixed-evidence scenario, not a claim that all employers or credentials experience the same failure.

## 2. Why this is not simply a 'fake certificate' problem

India already has an official academic-award infrastructure. DigiLocker-NAD allows institutions to lodge academic awards and provides a consent-based path for authorised verifiers. Its published process depends on the issuing institution having published the award and on the student granting consent. The NAD FAQ says that verification is made available within 24 hours after consent; if consent is not given in a reasonable time, the request can lapse.

Therefore:
- A record not found in a repository is not, by itself, proof of forgery.
- A verification service being unavailable is not proof that the credential is invalid.
- A matching document hash proves only that the compared content matches the referenced digest; it does not establish who issued the credential.
- A valid issuer signature does not necessarily establish that a credential has not since been revoked or suspended.
- A valid credential may still refer to a different person from the applicant presenting it.

## 3. Problem statement

**How can a resource-constrained Indian SME recruiter make a defensible and privacy-conscious decision when an applicant presents heterogeneous academic and professional credentials, but evidence about document integrity, issuer identity, credential status, subject match, and source availability is incomplete or comes from different systems?**

There is no single verification mechanism that resolves all of these dimensions. The study investigates a layered evidence-triage workflow rather than assuming that blockchain alone is the answer.

## 4. Research questions

- **RQ1:** How reliably can a hash-linked ledger detect post-issuance changes to certificate data in controlled synthetic scenarios?
- **RQ2:** What incorrect conclusions arise when hash integrity is treated as equivalent to issuer authenticity?
- **RQ3:** How should a verifier classify 'not found', 'consent pending', and 'source unavailable' without automatically treating them as fraudulent?
- **RQ4:** Can a multi-evidence decision model produce more informative and defensible outcomes than a binary valid/invalid result while collecting less data?

## 5. Proposed contribution

The proposed contribution is a small, explainable **Evidence-Aware Credential Triage (EACT)** layer for CertiChain. It does not replace NAD, DigiLocker, an issuer's own verifier, or a future standards-based credential wallet. It helps a reviewer state precisely what has and has not been established.

The model records five independent evidence dimensions:

| Dimension | Example states |
|---|---|
| Document integrity | Match / mismatch / not checked |
| Issuer identity | Authenticated / not trusted / unknown |
| Credential status | Active / suspended / revoked / expired / unknown |
| Subject match | Match / mismatch / not checked |
| Source/consent state | Available / no record / unavailable / consent pending / not applicable |

The output is not a single opaque confidence score. It is an evidence summary plus a disposition:

- **Verified against trusted source** — issuer is authenticated, subject matches, integrity checks pass, and status is active.
- **Altered** — a trusted comparison detects a content or signature mismatch.
- **Revoked / suspended / expired** — the trusted status source reports that state.
- **Issuer unverified** — the document may be internally intact, but issuer identity is not established.
- **Subject mismatch** — evidence does not bind the credential to the applicant.
- **Pending consent** — the required consent step has not completed.
- **Inconclusive / manual review** — source not found, unavailable, or evidence is incomplete.

A 'not found' or 'unavailable' result must not be presented as 'fake'.

## 6. Relationship to CertiChain

The current CertiChain prototype already demonstrates:
- a genesis block and SHA-256 block hashes;
- previous-hash links and proof-of-work with a small demonstration difficulty;
- manual certificate issuance;
- a separately loaded synthetic ledger;
- tampering simulation and an audit result.

This demonstrates **record-integrity checking** in a controlled local application. It does not yet authenticate the original university issuer, establish the student's identity, check revocation, connect to NAD, or implement W3C Verifiable Credentials.

The next research increment should extend the prototype from a hash-only result toward an evidence summary, while keeping external registry integrations simulated until authorised access exists.

## 7. Scope and boundaries

- Initial evaluation uses only fictional, repository-committed test cases.
- No real student records, Aadhaar information, contact details, or university database are used.
- No NAD / DigiLocker API integration is claimed or attempted.
- No production security, legal compliance, or institutional approval is claimed.
- Any future live integration requires institutional authorisation, suitable credentials, consent handling, privacy review, and security testing.

## 8. Expected value

The intended value is not to create another national academic repository. It is to explore how a small employer-facing tool can combine or route evidence from existing systems, explain uncertainty, preserve a review trail, and avoid false assurance when one source is missing.
