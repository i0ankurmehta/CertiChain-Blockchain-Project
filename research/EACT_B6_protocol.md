# EACT-B6 Research Protocol
## Cryptographic Selective Disclosure and Authenticated Online Credential Intake

**Experiment ID:** EACT-B6  
**Project:** CertiChain / Evidence-Aware Credential Triage (EACT)  
**Version:** 0.1 — implementation prototype  
**Standards baseline:** IETF RFC 9901 (November 2025)  
**Data:** Fictional local issuer fixtures; optional externally issued SD-JWTs from explicitly configured sources  
**Status:** Research prototype; not production-ready

---

## 1. Research problem

EACT-B5 models purpose-bound minimum disclosure, holder choice and privacy findings, but its presentation proposal is ordinary application data. It does not cryptographically prove that a disclosed claim was issued by a trusted party, that an undisclosed claim was withheld without altering the signed credential, or that the person presenting the credential controls the associated holder key.

B6 asks how to move from a policy-only proposal to a cryptographically checkable presentation, while allowing credentials to enter CertiChain from authorized online issuer endpoints without confusing network retrieval with authenticity.

## 2. Research question

**RQ-B6:** Can an academic-credential prototype issue and verify an RFC 9901 SD-JWT presentation that reveals only holder-selected claims, binds the presentation to a verifier transaction, and accepts externally hosted credentials only when their issuer signature validates against an independently configured trust key?

### Sub-questions

- RQ-B6.1: Can ES256 issuer signatures and SHA-256 disclosure digests protect a credential while allowing selected claim disclosure?
- RQ-B6.2: Can a holder Key Binding JWT bind the exact selected-disclosure set to an audience and one-time nonce?
- RQ-B6.3: Does the verifier reject altered signatures, disclosures, wrong holder keys, wrong audiences, stale proofs, and replayed/non-matching nonces?
- RQ-B6.4: How can remote credential retrieval preserve source URL, retrieval time, HTTP status, media type, byte count and content fingerprint without treating HTTPS retrieval as issuer authentication?
- RQ-B6.5: What additional trust, status, privacy and operational controls remain necessary before a real university source can be connected?

## 3. Standards and profile scope

The implementation uses **RFC 9901 — Selective Disclosure for JSON Web Tokens (SD-JWT)** as its normative cryptographic baseline. The prototype uses compact serialization, ES256, SHA-256, top-level object-property disclosures, and SD-JWT+KB holder binding. The application-specific JOSE type identifies this research profile.

This is not a claim of full SD-JWT VC conformance. As of 13 November 2026, SD-JWT VC remains an active IETF Internet-Draft (revision 26, 6 November 2026). OpenID4VP 1.0 is final, but the current prototype does not implement that transport protocol.

## 4. Actors and trust boundaries

1. **Demo issuer:** A local, fictional issuer signing sample academic claims with a per-session ES256 key.
2. **Holder:** Controls the session's holder key and selects which disclosure objects to present.
3. **Verifier:** Checks the issuer signature, disclosure membership, holder signature, audience, nonce and proof age.
4. **Online source connector:** Fetches an issuer-hosted SD-JWT from an exact HTTPS hostname in an administrator-configured allowlist.
5. **Trust registry:** A separately configured mapping from issuer identifier to public JWK. An issuer identifier extracted from a token is untrusted until the configured key validates its signature.

The prototype does not contact a university by default. A real connector requires an authorized endpoint, exact host allowlisting, and an issuer public key obtained through an independently authenticated channel.

## 5. Method

### 5.1 Issuance

The issuer creates a signed JWT containing iss, iat, exp, the holder's public key in cnf.jwk, _sd_alg set to sha-256, and one SHA-256 digest per selectively disclosable claim. Each top-level property disclosure contains a 128-bit random salt, claim name and claim value, base64url encoded. The issuer signs the JWT using ES256.

### 5.2 Holder selection and key binding

The holder chooses a subset of issued disclosures. The holder constructs the SD-JWT from the issuer-signed JWT and only those disclosures. The holder then signs a Key Binding JWT (typ kb+jwt) containing iat, aud, nonce, and sd_hash. The sd_hash binds the proof to the exact serialized issuer JWT and selected disclosure sequence.

### 5.3 Verification

The verifier validates the issuer signature against a configured issuer public key, checks issuer identity and credential expiry, recomputes each selected disclosure digest, rejects duplicates and unknown disclosures, verifies the holder signature using the public key bound in cnf.jwk, checks the audience and nonce, validates proof freshness, and recomputes sd_hash.

### 5.4 Online source intake

The remote connector accepts only HTTPS on port 443, exact allowlisted hostnames, public DNS address resolutions, no URL credentials, no fragments, no redirects, a bounded response size, and application/sd-jwt or text/plain responses. It records retrieval metadata and a SHA-256 fingerprint. It then verifies the fetched SD-JWT only if the extracted issuer identifier matches a configured trust-registry entry and the signature validates under that entry's public JWK.

Plain JSON, arbitrary webpages, HTML, and unsigned data are not treated as credentials. A successful HTTP response proves retrieval from a web endpoint, not that its contents are authentic. A verified SD-JWT signature proves signing by the configured key, not that the key owner is a legitimate university; trust configuration is a separate decision.

## 6. Security and privacy constraints

- The local demonstration uses ephemeral in-memory private keys and fictional records. Keys are not persisted and must not be reused for production.
- No private issuer or holder key is stored in Git, app configuration, or the online-source registry.
- The online source registry stores public keys only.
- The remote fetch path does not follow redirects, blocks non-public DNS resolutions, and requires an exact hostname allowlist. Production deployment additionally requires network egress controls and pinned DNS/TLS handling to mitigate DNS rebinding and infrastructure-level SSRF risks.
- Retrieved credentials and claims are not written to the repository or a database by this page. Operators must still assess application hosting, session memory, logs, backups and data-retention controls.
- The prototype does not query credential revocation/status lists, prove real-world holder identity, validate consent authenticity, or implement a full wallet lifecycle.
- The cryptographic checks do not establish legal authority to process personal data. Obtain authorization before connecting real institutional sources.

## 7. Evaluation design

The test suite covers valid issuance/presentation, selective claim release, issuer signature tampering, wrong issuer trust anchor, wrong audience, wrong nonce, wrong holder key, expired credentials, stale key-binding proof, disclosure tampering, reserved claims, duplicate/unknown claim selections, URL scheme and allowlist checks, private-address blocking, and retrieval metadata generation.

The automated tests are deterministic software tests, not interoperability certification, penetration testing, empirical accuracy measurements, or institutional validation.

## 8. Known limitations and next steps

The current implementation intentionally supports only top-level object-property disclosures and compact serialization. It does not yet implement nested and array disclosures, decoy digests, JWS JSON serialization, the SD-JWT VC profile, OpenID4VP/DCQL transport, a wallet, issuer key discovery/rotation, a status-list service, or a production trust framework. The online connector accepts a configured issuer-signed SD-JWT endpoint, not arbitrary university web pages or student portals.

Future work should add interoperability vectors from multiple implementations, nested disclosure support, formal issuer-key rotation, a status-list integration, holder-side encrypted key storage, OpenID4VP transaction handling, independent security review, and an institution-approved connector.

## 9. References

- IETF RFC 9901, Selective Disclosure for JSON Web Tokens (SD-JWT), November 2025: https://www.rfc-editor.org/rfc/rfc9901.html
- IETF draft-ietf-oauth-sd-jwt-vc-26, SD-JWT-based Verifiable Digital Credentials, 6 November 2026: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-sd-jwt-vc
- OpenID for Verifiable Presentations 1.0, Final: https://openid.net/specs/openid-4-verifiable-presentations-1_0.html
- W3C Verifiable Credentials Data Model v2.0, Recommendation: https://www.w3.org/TR/vc-data-model/
