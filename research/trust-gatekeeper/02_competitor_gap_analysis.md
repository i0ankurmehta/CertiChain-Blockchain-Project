# 02 — Competitor and Gap Analysis

**Version:** 0.1  
**Evidence cut-off:** 14 November 2026  
**Scope:** Publicly documented education-verification capabilities relevant to India.

## 1. How to read this analysis

This is a desk-research comparison, not a hands-on product test or market-share study.

- **Documented capability** means a provider or official body publicly describes the capability.
- **Vendor claim** means the statement comes from the provider's own product or support material and has not been independently performance-tested here.
- **Not disclosed** means the public materials reviewed did not describe the capability. It does **not** mean the provider lacks it.
- The proposed CertiChain gap is a research hypothesis to validate with BGV practitioners and product demonstrations.

## 2. Capability matrix

| Provider / ecosystem | Publicly documented education-verification capability | What that means for CertiChain | What remains unknown from public material |
|---|---|---|---|
| **DigiLocker–NAD** | Stores academic awards lodged by participating institutions; institutions are responsible for award-data authenticity. Legacy award data can be uploaded in machine-readable formats; scanned PDFs are not accepted as repository award data. [1][2] | A national digital repository and verification route already exist. CertiChain should complement it, not create another repository. | BGV-side integrations, coverage for a particular candidate/institution, and how unresolved legacy cases are handled by each verifier. |
| **SpringVerify** | Its preliminary education check publicly describes OCR and image analysis for altered seals, inconsistent fonts and pixelation, plus checks whether the stated degree/specialisation is offered by the institution. It says the system generates a preliminary report and supports human escalation. [3] Its education-verification page describes historical closed/merged/renamed institution routing and official registrar checks. [4] | OCR, image-forensics signals, automatic preliminary screening and basic institution/degree cross-checking are already commercial feature claims. These cannot be CertiChain's novelty claim. | Whether the internal evidence model exposes dated source assertions, source-dependency lineage, temporal graph explanations, or equivalent controls. Public product pages do not settle this. |
| **AuthBridge** | Public material describes instant checks through DigiLocker and a proprietary database, plus human-led checks through calls, email and vendor assistance. Its output fields include course details, duration, GPA, graduation status and attendance dates. [5] | Multi-channel verification and a mix of automation and human outreach are established approaches. | Whether its internal platform models historical programme/affiliation relationships and source lineage in a graph. Not disclosed in the reviewed public material. |
| **First Advantage India** | Its India site describes education verification against school registers or third-party providers, combined with automation and specialist outreach. [6] | Broad source coverage and human operations are established. A new product must demonstrate a distinct analyst benefit rather than merely add another dashboard. | Public page does not disclose detailed source provenance or temporal graph implementation. |
| **UGC / UGC-DEB / statutory authorities** | UGC-DEB publishes year/session-specific recognition and programme information. UGC states that the issuing authority verifies an individual degree. [7][8] | Authoritative sources exist, but they answer different questions: recognition/approval status is not the same as verifying the candidate's individual award. | Data completeness, historical availability, machine readability and interpretation can vary across source families and periods. |

## 3. What is already commoditised or clearly overlapped?

The following cannot be claimed as novel by CertiChain:
- OCR of academic documents.
- Detecting visual artefacts such as inconsistent fonts, pixelation or altered seals.
- Extracting university, degree, subject, marks or date fields.
- Checking whether a university is recognised at a high level.
- Basic checks that a stated degree/programme exists at a named institution.
- Preliminary automated grading with manual escalation.
- Direct institutional verification and partner-assisted verification.
- A digital repository for institution-lodged academic awards.

SpringVerify is the closest directly documented overlap for an instant preliminary-screening product. AuthBridge and First Advantage are important comparators for broader education-verification operations and multi-source/human verification workflows.

## 4. Proposed research gap — stated cautiously

**Candidate gap:** an auditable representation of historical institutional/programme relationships and the provenance/dependency of evidence used to assess a credential case.

The specific capabilities to investigate are:

1. **Temporal applicability:** can an analyst see which recognition, approval, affiliation, campus or programme relationship applied during the candidate's admission/study/award period?
2. **Entity continuity:** can renamed, merged, closed or successor institutions be connected without treating their names as interchangeable?
3. **Source lineage:** can the system show the original notice or record behind a claim and identify sources that merely reproduce it?
4. **Conflict explanation:** can it show which sources conflict, what dates or entities differ, and what would resolve the conflict?
5. **Selective abstention:** can the system say that the supplied evidence is insufficient instead of auto-clearing or accusing a candidate?

This is not yet an established white space. Competitors may already implement some or all of these techniques internally. The public pages reviewed do not reveal enough to answer that.

## 5. Why the Indian context makes temporal modelling important

UGC's FAQ says the recognition status of a higher-education institution for a previous year does not establish its recognition for the next session. The UGC-DEB FAQ provides further session-specific guidance for ODL and online programmes and discusses conditions such as programme availability and territorial jurisdiction. [7][8]

The same UGC FAQ says that the issuing university or institution verifies the individual degree, while UGC-DEB provides the relevant institution/programme recognition status. [7]

DigiLocker-NAD says institutions are responsible for the authenticity of the award data they lodge. It permits machine-readable legacy data uploads but does not accept scanned images/PDFs as award records in the repository. [1][2]

**Implication:** an institution-status check, programme/session check, document appearance check and individual award verification must remain separate evidence dimensions.

## 6. Customer discovery questions

Ask BGV analysts and operations leads:

1. Which education cases currently require the most manual research after the first automated check?
2. How do you assess a degree from an institution that changed name, merged or closed?
3. How do you check programme and study-mode recognition for historical admission sessions?
4. How are disagreements between regulator pages, university pages and third-party directories resolved?
5. Do analysts retain the source URL, original notice, capture date and a copy/hash of the evidence?
6. Can your team tell when multiple web sources repeat the same original notice?
7. What triggers a manual escalation, and who has authority to close the case?
8. Which existing vendor system already solves some of these tasks?
9. Would a source-linked historical evidence dossier fit into your existing workflow, and what format/API would it need?
10. What candidate-consent, retention and audit requirements constrain such a tool?

Do not pitch the graph as a solution before hearing their existing process.

## 7. Competitive position to test

**Avoid:** “AI certificate fraud detection,” “instant degree verification,” “blockchain proves academic authenticity,” or “we reduce BGV costs by 60–80%.”

**Test instead:** “An explainable evidence-resolution layer for difficult education checks, showing which institutional/programme relationships applied at the relevant time, how each finding is sourced, which sources are dependent or conflicting, and when the evidence is insufficient.”

This phrasing describes the intended research behaviour, not a proven market advantage.

## 8. References

[1] National Academic Depository, FAQ: https://www.nad.gov.in/faq.html  
[2] DigiLocker-NAD, FAQ (legacy awards, data formats and scanned PDF limitations): https://nad.digilocker.gov.in/faq  
[3] SpringVerify, Education Check (Preliminary) setup guide: https://support.springworks.in/portal/en/kb/articles/how-to-use-education-check-preliminary  
[4] SpringVerify, Education Verification: https://in.springverify.com/screenings/education-verification/  
[5] AuthBridge, Education Verification: https://authbridge.com/checks/education-verification/  
[6] First Advantage India, Background Verification: https://fadv.com/en-in/solutions/background-verification/  
[7] UGC, Frequently Asked Questions: https://www.ugc.gov.in/Home/faq  
[8] UGC Distance Education Bureau, FAQ: https://deb.ugc.ac.in/FAQ

**Accessed:** 14 November 2026.
