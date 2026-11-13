"""EACT-B6: RFC 9901 SD-JWT issuance, selective presentation and verification."""
from __future__ import annotations

import os
import secrets

import streamlit as st

from eact_sdjwt import (
    SDJWTError,
    create_sd_jwt_presentation,
    fetch_remote_sd_jwt,
    generate_es256_keypair,
    issue_sd_jwt,
    load_trusted_issuer_registry,
    untrusted_issuer_from_sd_jwt,
    verify_issued_sd_jwt,
    verify_sd_jwt_presentation,
)


st.set_page_config(page_title="EACT-B6 Cryptographic Selective Disclosure", layout="wide")
st.title("EACT-B6 — Cryptographic Selective Disclosure Lab")
st.caption("RFC 9901 SD-JWT • Issuer signatures • Holder key binding • Online issuer intake")
st.warning(
    "Research prototype. The local issuer and holder keys are generated for this Streamlit "
    "session and are not production-managed keys. The sample credential is fictional. "
    "This page implements a limited RFC 9901 profile, not full SD-JWT VC or OpenID4VP."
)


# The demo keys remain in this user's Streamlit session only. They are never written to disk.
if "b6_issuer_keys" not in st.session_state:
    st.session_state.b6_issuer_keys = generate_es256_keypair()
if "b6_holder_keys" not in st.session_state:
    st.session_state.b6_holder_keys = generate_es256_keypair()
if "b6_nonce" not in st.session_state:
    st.session_state.b6_nonce = secrets.token_urlsafe(24)
if "b6_issued_credential" not in st.session_state:
    st.session_state.b6_issued_credential = None
if "b6_presentation" not in st.session_state:
    st.session_state.b6_presentation = None


DEMO_ISSUER = "https://certichain.example/issuer/demo"
DEMO_AUDIENCE = "https://verifier.certichain.example/demo"
DEMO_CLAIMS = {
    "award_status": "awarded",
    "qualification_level": "Bachelor's degree",
    "program_name": "Bachelor of Computer Applications",
    "institution_name": "Northstar Fictional University",
    "graduation_year": 2025,
    "cgpa": 8.2,
    "roll_number": "SYN-BCA-001",
    "date_of_birth": "2005-01-15",
    "home_address": "12 Example Lane, Fictional City",
}

with st.expander("What is actually cryptographic in this experiment?", expanded=True):
    st.markdown(
        """
        1. The demo issuer signs a JWT using an ephemeral ES256 key.
        2. Each selectively disclosable claim is placed in a salted disclosure. The issuer-signed JWT contains SHA-256 digests, not the hidden claim values.
        3. The holder chooses which disclosures to release.
        4. A holder Key Binding JWT signs the exact selected-disclosure set and includes the verifier audience and one-time nonce.
        5. The verifier checks the issuer signature, disclosure digests, holder signature, audience, nonce and proof freshness.

        This is real signature and digest validation using cryptographic libraries. It is not a blockchain consensus mechanism, a zero-knowledge proof, a full credential wallet, or an institutional trust framework.
        """
    )

st.header("1. Local issuer — create a signed research credential")
st.info(
    "The example below is deliberately fictional. Do not paste live student records into this local demo issuer: "
    "it would sign the data with a CertiChain demonstration key, not with your university's key."
)
with st.expander("Inspect the fictional sample claims"):
    st.json(DEMO_CLAIMS)

issuer_keys = st.session_state.b6_issuer_keys
holder_keys = st.session_state.b6_holder_keys
key_columns = st.columns(2)
with key_columns[0]:
    st.metric("Issuer signing algorithm", "ES256 / P-256")
    st.caption("Ephemeral issuer public-key fingerprint")
    st.code(issuer_keys["public_jwk"]["x"][:16] + "…" + issuer_keys["public_jwk"]["y"][-12:])
with key_columns[1]:
    st.metric("Holder binding algorithm", "ES256 / P-256")
    st.caption("The credential is bound to this session's holder public key.")
    st.code(holder_keys["public_jwk"]["x"][:16] + "…" + holder_keys["public_jwk"]["y"][-12:])

if st.button("Issue fictional SD-JWT credential", type="primary"):
    try:
        st.session_state.b6_issued_credential = issue_sd_jwt(
            DEMO_CLAIMS,
            issuer=DEMO_ISSUER,
            issuer_private_key_pem=issuer_keys["private_key_pem"],
            holder_public_jwk=holder_keys["public_jwk"],
        )
        st.session_state.b6_presentation = None
        st.success("Issuer-signed SD-JWT created. The full credential remains in session memory.")
    except SDJWTError as error:
        st.error(str(error))

issued = st.session_state.b6_issued_credential
if issued:
    st.success(f"Credential created for issuer {issued['issuer']}.")
    st.caption(
        f"Issued at Unix time {issued['issued_at']} · Expires at Unix time {issued['expires_at']} · "
        f"{len(issued['disclosable_claim_names'])} selectively disclosable claims"
    )
    with st.expander("Inspect the issuer-signed SD-JWT and disclosure inventory"):
        st.code(issued["sd_jwt"], language="text")
        st.dataframe(
            [{"Claim": name, "Disclosure digest": "SHA-256 digest embedded in issuer JWT"}
             for name in issued["disclosable_claim_names"]],
            use_container_width=True,
            hide_index=True,
        )

    st.header("2. Holder — choose what to disclose")
    selected_claims = st.multiselect(
        "Claims to disclose to this verifier",
        options=issued["disclosable_claim_names"],
        default=["award_status", "qualification_level", "program_name", "institution_name"],
    )
    audience = st.text_input("Verifier audience (exact identifier)", value=DEMO_AUDIENCE)
    nonce = st.text_input("Verifier's one-time challenge nonce", value=st.session_state.b6_nonce)
    if st.button("Create holder-bound presentation"):
        try:
            st.session_state.b6_presentation = create_sd_jwt_presentation(
                issued,
                selected_claims=selected_claims,
                holder_private_key_pem=holder_keys["private_key_pem"],
                audience=audience.strip(),
                nonce=nonce.strip(),
            )
            st.success("Holder presentation created with a Key Binding JWT.")
        except SDJWTError as error:
            st.error(str(error))

    presentation = st.session_state.b6_presentation
    if presentation:
        st.markdown("**Presentation sent to the verifier (selected disclosures only):**")
        st.code(presentation["presentation"], language="text")
        st.caption("The issuer's complete credential is not sent in this presentation.")

        st.header("3. Verifier — validate the presentation")
        if st.button("Verify issuer, disclosures and holder binding", type="primary"):
            try:
                verification = verify_sd_jwt_presentation(
                    presentation["presentation"],
                    issuer_public_key=issuer_keys["public_jwk"],
                    expected_issuer=DEMO_ISSUER,
                    expected_audience=audience.strip(),
                    expected_nonce=nonce.strip(),
                )
                st.success("VALID: issuer signature, selected disclosures and holder key binding verified.")
                st.write("**Verified claims available to this verifier:**")
                st.json(verification["claims"])
                st.caption(
                    "The verifier sees only permanent claims and the disclosures selected by the holder. "
                    "The raw CGPA, roll number, date of birth and address remain undisclosed in this example."
                )
            except SDJWTError as error:
                st.error(f"REJECTED: {error}")

        with st.expander("Negative test — deliberately use a different nonce"):
            wrong_nonce = st.text_input("Incorrect nonce", value="replay-attempt-0001", key="b6_wrong_nonce")
            if st.button("Run replay/challenge test"):
                try:
                    verify_sd_jwt_presentation(
                        presentation["presentation"],
                        issuer_public_key=issuer_keys["public_jwk"],
                        expected_issuer=DEMO_ISSUER,
                        expected_audience=audience.strip(),
                        expected_nonce=wrong_nonce,
                    )
                    st.error("Unexpected result: the mismatched challenge was accepted.")
                except SDJWTError as error:
                    st.success(f"Correctly rejected: {error}")
else:
    st.caption("Issue the fictional SD-JWT first to unlock holder presentation and verifier checks.")

st.divider()
st.header("4. Online issuer intake — fetch a real issuer-hosted SD-JWT")
st.write(
    "This connector retrieves an issuer-signed SD-JWT from an approved HTTPS endpoint. "
    "A normal JSON page, a university website homepage, or a hash match is not accepted as a credential."
)


def read_setting(name: str) -> str:
    try:
        value = st.secrets.get(name, None)
        if value is not None:
            return str(value)
    except Exception:
        pass
    return os.environ.get(name, "")


allowed_hosts = [
    item.strip().lower()
    for item in read_setting("EACT_ALLOWED_SOURCE_HOSTS").split(",")
    if item.strip()
]
try:
    trusted_issuers = load_trusted_issuer_registry(read_setting("EACT_TRUSTED_ISSUERS_JSON"))
except SDJWTError as error:
    trusted_issuers = {}
    st.error(f"Issuer trust configuration error: {error}")

if not allowed_hosts:
    st.warning(
        "No online source hosts are configured. Add EACT_ALLOWED_SOURCE_HOSTS to the local "
        ".streamlit/secrets.toml or deployment secrets before fetching any online credential."
    )
else:
    st.caption("Configured source hosts: " + ", ".join(allowed_hosts))
if not trusted_issuers:
    st.warning(
        "No issuer public keys are trusted yet. Add EACT_TRUSTED_ISSUERS_JSON with public JWKs "
        "obtained through an independently authenticated issuer channel. Do not trust a key merely "
        "because the credential endpoint supplies it."
    )
else:
    st.caption("Configured trusted issuer identifiers: " + ", ".join(trusted_issuers.keys()))

remote_url = st.text_input(
    "Authorized issuer credential endpoint (HTTPS)",
    placeholder="https://credentials.your-institution.edu/credential/…",
)
if st.button("Fetch and verify online credential"):
    if not allowed_hosts or not trusted_issuers:
        st.error("Configure both an exact source-host allowlist and a trusted issuer public key first.")
    else:
        try:
            fetched = fetch_remote_sd_jwt(remote_url, allowed_hosts=allowed_hosts)
            # The issuer claim is untrusted until the matching configured key verifies the JWS.
            candidate_issuer = untrusted_issuer_from_sd_jwt(fetched["credential"])
            if candidate_issuer not in trusted_issuers:
                raise SDJWTError("Credential issuer is not present in the independently configured trust registry.")
            remote_result = verify_issued_sd_jwt(
                fetched["credential"],
                issuer_public_key=trusted_issuers[candidate_issuer],
                expected_issuer=candidate_issuer,
            )
            st.success("Issuer signature and SD-JWT disclosures verified against the configured trust key.")
            st.json({
                "issuer": remote_result["issuer"],
                "verified_claims": remote_result["claims"],
                "key_id": remote_result["key_id"],
            })
            st.markdown("**Retrieval evidence**")
            st.json({key: value for key, value in fetched.items() if key != "credential"})
            st.warning(
                "This verifies the issuer-signed credential and disclosure digests only. It does not "
                "check a live revocation/status service, independently prove the real-world identity "
                "of the holder, or create a verifier presentation. Key binding requires the matching "
                "holder private key and a fresh verifier nonce. Retrieved data was kept in this run's "
                "memory and was not written into the repository or a database."
            )
        except SDJWTError as error:
            st.error(f"Online credential rejected: {error}")

with st.expander("Online-source configuration example"):
    st.code(
        """# .streamlit/secrets.toml — use only issuer endpoints you are authorised to access
EACT_ALLOWED_SOURCE_HOSTS = "credentials.example.edu"
EACT_TRUSTED_ISSUERS_JSON = '{"https://issuer.example.edu":{"kty":"EC","crv":"P-256","x":"BASE64URL_X","y":"BASE64URL_Y","alg":"ES256","use":"sig"}}'""",
        language="toml",
    )
    st.caption(
        "Replace the example hostname and public JWK with values published or provided through an "
        "authenticated issuer channel. Never put issuer or holder private keys in this configuration. "
        "The example placeholders are not a usable trust anchor."
    )

st.divider()
st.header("Research scope and limitations")
st.markdown(
    """
    - Implemented profile: RFC 9901 compact serialization, ES256, SHA-256, flat top-level object-property disclosures, and SD-JWT+KB audience/nonce binding.
    - Not implemented: nested and array disclosures, decoy digests, JWS JSON serialization, OpenID4VP request/response transport, a wallet, issuer lifecycle/status checks, or an institution trust-list integration.
    - SD-JWT VC is a separate IETF Internet-Draft and is not claimed as fully implemented here.
    - A signed credential proves that the configured issuer key signed the token; it does not, by itself, prove that the issuer is legitimate. Issuer keys must be pinned through an independent trust process.
    - Online import is restricted to exact HTTPS hosts in EACT_ALLOWED_SOURCE_HOSTS and issuers in EACT_TRUSTED_ISSUERS_JSON. Redirects and private/reserved IP resolutions are rejected. Production deployments still need network-level egress restrictions and pinned DNS/TLS handling.
    - No institution API is preconfigured. Obtain explicit permission and technical documentation before connecting a real university source. Never scrape student portals or bypass access controls.
    """
)
