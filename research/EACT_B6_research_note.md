# EACT-B6 Research Note
## Cryptographic Selective Disclosure and Authenticated Online Credential Intake

**Draft status:** Prototype specification and initial automated-test results; no institutional integration or external interoperability study has been completed.

### Abstract

EACT-B5 demonstrated purpose-bound claim minimisation using a synthetic policy engine, but the resulting disclosure proposal was not cryptographically protected. EACT-B6 advances the prototype by implementing a limited RFC 9901 SD-JWT profile using ES256 issuer signatures, SHA-256 disclosure digests, holder-selected disclosures and a Key Binding JWT containing a verifier audience, nonce and sd_hash. A verifier checks issuer authenticity against a configured public key, disclosure membership and the holder's proof of possession. An additional online-source intake retrieves issuer-hosted SD-JWTs only from explicitly allowlisted HTTPS hosts and verifies them against an independently configured issuer-key registry. The source connector records retrieval metadata and a response fingerprint but does not equate HTTPS transport with credential authenticity. The implementation is a research prototype: it does not implement full SD-JWT VC, OpenID4VP, status checking, a production wallet or institutional trust governance.

### 1. Research question

Can an academic-credential prototype issue and verify an RFC 9901 SD-JWT presentation that reveals only holder-selected claims, binds the presentation to a verifier transaction, and accepts externally hosted credentials only when their issuer signature validates against an independently configured trust key?

### 2. Method

A Python module performs ES256 issuance, salted top-level object-property disclosures, SHA-256 digest embedding, SD-JWT+KB presentation creation, and verifier-side validation. A Streamlit page presents the issuer-holder-verifier flow with a fictional sample academic record. A separate online-source interface retrieves an issuer-hosted SD-JWT from an exact HTTPS hostname allowlist and checks the JWS against an administrator-configured issuer public JWK.

### 3. Preliminary results

**Initial local result:** 15 focused B6 unit tests passed in the development container. The tests exercise issuance, selected disclosure, issuer signature validation, holder key binding, verifier audience and nonce checks, expiry/freshness handling, tamper rejection, and online-source URL policy. These results have not yet been run in the repository's GitHub Actions environment and should not be described as CI-passed until that workflow completes.

### 4. Contributions

- Moves B5's presentation proposal to actual signed and digest-linked disclosure data.
- Demonstrates that withholding a claim is enforced by not sending its disclosure object.
- Binds the holder's presentation to an audience and one-time challenge to reduce replay risk.
- Separates data retrieval provenance from issuer authenticity and configured issuer trust.
- Provides explicit configuration boundaries for authorized external issuer endpoints.

### 5. Standards relationship

The base selective-disclosure mechanism follows RFC 9901. SD-JWT VC is tracked as a separate active Internet-Draft, not claimed as implemented in full. OpenID4VP 1.0 is a finalized transport protocol but is not implemented in this milestone.

### 6. Limitations

The current profile is intentionally limited to compact serialization, ES256, SHA-256, flat object-property disclosures and SD-JWT+KB. It omits nested/array disclosures, decoy digests, issuer key discovery and rotation, credential revocation/status, OpenID4VP, real holder-wallet key management, and institution-approved integration. All local issuer examples are fictional. Online retrieval is disabled until an operator configures authorized source hosts and issuer public keys independently.

### 7. Conclusion

B6 changes the prototype's assurance model: the sample presentation is now checked cryptographically instead of relying solely on an application-level filtering rule. The result is a limited research implementation, not a production academic-credential system. The next validation step is standards interoperability testing and a security review before adding live issuer APIs.
