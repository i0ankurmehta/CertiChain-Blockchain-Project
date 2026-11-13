"""A deliberately narrow RFC 9901 SD-JWT research implementation for CertiChain.

Profile scope: compact JWS, ES256, top-level object-property disclosures,
SHA-256, and SD-JWT+KB holder binding. Nested/array disclosures, JWS JSON
serialization, SD-JWT VC profile semantics, and OpenID4VP transport are not
implemented. Do not use the ephemeral demo key handling in production.
"""
from __future__ import annotations

import base64
import hashlib
import ipaddress
import json
import re
import secrets
import socket
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence
from urllib.parse import urlsplit

import jwt
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

PROFILE_TYP = "academic+sd-jwt"
KB_TYP = "kb+jwt"
ALGORITHM = "ES256"
HASH_ALGORITHM = "sha-256"
RESERVED_CLAIMS = {
    "_sd", "_sd_alg", "...", "iss", "iat", "exp", "nbf", "aud",
    "jti", "cnf", "sub", "nonce", "sd_hash",
}
MAX_REMOTE_BYTES = 256 * 1024


class SDJWTError(ValueError):
    """Raised when an SD-JWT operation fails validation."""


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise SDJWTError("Malformed base64url value.")
    try:
        decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except Exception as exc:
        raise SDJWTError("Malformed base64url value.") from exc
    if _b64url(decoded) != value:
        raise SDJWTError("Non-canonical base64url value.")
    return decoded


def _public_jwk(public_key: ec.EllipticCurvePublicKey) -> Dict[str, str]:
    numbers = public_key.public_numbers()
    return {
        "kty": "EC",
        "crv": "P-256",
        "x": _b64url(numbers.x.to_bytes(32, "big")),
        "y": _b64url(numbers.y.to_bytes(32, "big")),
        "alg": ALGORITHM,
        "use": "sig",
    }


def generate_es256_keypair() -> Dict[str, Any]:
    """Create an ephemeral P-256 key pair; private material is returned to caller."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")
    return {
        "private_key_pem": private_pem,
        "public_key_pem": public_pem,
        "public_jwk": _public_jwk(private_key.public_key()),
    }


def _load_public_key(key: Any):
    if isinstance(key, Mapping):
        jwk = dict(key)
        if jwk.get("kty") != "EC" or jwk.get("crv") != "P-256" or "d" in jwk:
            raise SDJWTError("Only public P-256 EC JWKs are accepted for verification.")
        if jwk.get("alg", ALGORITHM) != ALGORITHM:
            raise SDJWTError("Issuer/holder JWK algorithm must be ES256.")
        try:
            return jwt.PyJWK.from_dict(jwk, algorithm=ALGORITHM).key
        except Exception as exc:
            raise SDJWTError("Invalid public JWK.") from exc
    if isinstance(key, (str, bytes)):
        try:
            return serialization.load_pem_public_key(
                key.encode("ascii") if isinstance(key, str) else key
            )
        except Exception as exc:
            raise SDJWTError("Invalid PEM public key.") from exc
    raise SDJWTError("A PEM public key or public JWK is required.")


def _validate_claims(claims: Mapping[str, Any]) -> None:
    if not isinstance(claims, Mapping) or not claims:
        raise SDJWTError("Credential claims must be a non-empty JSON object.")
    for name, value in claims.items():
        if not isinstance(name, str) or not name or name in RESERVED_CLAIMS:
            raise SDJWTError(f"Unsupported or reserved claim name: {name!r}")
        try:
            json.dumps(value, ensure_ascii=False, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise SDJWTError(f"Claim {name!r} is not valid JSON data.") from exc


def issue_sd_jwt(
    claims: Mapping[str, Any],
    *,
    issuer: str,
    issuer_private_key_pem: str,
    holder_public_jwk: Mapping[str, Any],
    lifetime_seconds: int = 3600,
    now: Optional[int] = None,
    key_id: str = "certichain-demo-issuer-es256",
) -> Dict[str, Any]:
    """Issue an SD-JWT with independently salted top-level object disclosures."""
    _validate_claims(claims)
    if not issuer or not isinstance(issuer, str):
        raise SDJWTError("An issuer identifier is required.")
    if not isinstance(lifetime_seconds, int) or not 1 <= lifetime_seconds <= 31_536_000:
        raise SDJWTError("Credential lifetime must be between 1 second and 365 days.")
    if not isinstance(holder_public_jwk, Mapping):
        raise SDJWTError("Holder public JWK is required for key binding.")
    holder_jwk = dict(holder_public_jwk)
    if holder_jwk.get("kty") != "EC" or holder_jwk.get("crv") != "P-256" or "d" in holder_jwk:
        raise SDJWTError("Holder key must be a public P-256 EC JWK.")
    _load_public_key(holder_jwk)

    issued_at = int(time.time() if now is None else now)
    disclosure_map: Dict[str, str] = {}
    digests = []
    for name, value in claims.items():
        salt = _b64url(secrets.token_bytes(16))
        disclosure_json = json.dumps(
            [salt, name, value], ensure_ascii=False, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
        disclosure = _b64url(disclosure_json)
        digest = _b64url(hashlib.sha256(disclosure.encode("ascii")).digest())
        if digest in digests:
            raise SDJWTError("Digest collision detected; refusing to issue credential.")
        digests.append(digest)
        disclosure_map[name] = disclosure

    payload = {
        "iss": issuer,
        "iat": issued_at,
        "exp": issued_at + lifetime_seconds,
        "cnf": {"jwk": holder_jwk},
        "_sd_alg": HASH_ALGORITHM,
        "_sd": digests,
    }
    try:
        issuer_jwt = jwt.encode(
            payload,
            issuer_private_key_pem,
            algorithm=ALGORITHM,
            headers={"typ": PROFILE_TYP, "kid": key_id},
        )
    except Exception as exc:
        raise SDJWTError("Could not create the issuer-signed JWT.") from exc

    issued_sd_jwt = issuer_jwt + "~" + "".join(value + "~" for value in disclosure_map.values())
    return {
        "issuer_signed_jwt": issuer_jwt,
        "sd_jwt": issued_sd_jwt,
        "disclosures": disclosure_map,
        "issuer": issuer,
        "issued_at": issued_at,
        "expires_at": issued_at + lifetime_seconds,
        "disclosable_claim_names": list(disclosure_map),
        "key_id": key_id,
    }


def create_sd_jwt_presentation(
    issued: Mapping[str, Any],
    *,
    selected_claims: Sequence[str],
    holder_private_key_pem: str,
    audience: str,
    nonce: str,
    now: Optional[int] = None,
) -> Dict[str, Any]:
    """Create an SD-JWT+KB containing only selected disclosures and a holder proof."""
    if not audience or not nonce:
        raise SDJWTError("A verifier audience and fresh nonce are required.")
    disclosures = issued.get("disclosures")
    issuer_jwt = issued.get("issuer_signed_jwt")
    if not isinstance(disclosures, Mapping) or not isinstance(issuer_jwt, str):
        raise SDJWTError("Issued SD-JWT object is incomplete.")
    if len(set(selected_claims)) != len(list(selected_claims)):
        raise SDJWTError("A disclosure cannot be selected more than once.")
    unknown = sorted(set(selected_claims) - set(disclosures))
    if unknown:
        raise SDJWTError("Unknown disclosure selection: " + ", ".join(unknown))

    selected_names = set(selected_claims)
    selected = [disclosures[name] for name in disclosures if name in selected_names]
    sd_jwt_part = issuer_jwt + "~" + "".join(item + "~" for item in selected)
    sd_hash = _b64url(hashlib.sha256(sd_jwt_part.encode("ascii")).digest())
    issued_at = int(time.time() if now is None else now)
    kb_payload = {
        "iat": issued_at,
        "aud": audience,
        "nonce": nonce,
        "sd_hash": sd_hash,
    }
    try:
        kb_jwt = jwt.encode(
            kb_payload,
            holder_private_key_pem,
            algorithm=ALGORITHM,
            headers={"typ": KB_TYP},
        )
    except Exception as exc:
        raise SDJWTError("Could not create the holder Key Binding JWT.") from exc
    return {
        "presentation": sd_jwt_part + kb_jwt,
        "sd_jwt": sd_jwt_part,
        "key_binding_jwt": kb_jwt,
        "sd_hash": sd_hash,
        "selected_claims": [name for name in disclosures if name in selected_names],
        "audience": audience,
        "nonce": nonce,
    }


def _decode_issuer_jwt(issuer_jwt: str, issuer_public_key: Any, expected_issuer: Optional[str]):
    try:
        header = jwt.get_unverified_header(issuer_jwt)
    except Exception as exc:
        raise SDJWTError("Issuer JWT header is malformed.") from exc
    if header.get("typ") != PROFILE_TYP:
        raise SDJWTError(f"Unexpected credential typ; expected {PROFILE_TYP!r}.")
    if header.get("alg") != ALGORITHM:
        raise SDJWTError("Only ES256 issuer signatures are accepted by this profile.")
    if isinstance(issuer_public_key, Mapping):
        configured_kid = issuer_public_key.get("kid")
        if configured_kid and header.get("kid") != configured_kid:
            raise SDJWTError("Issuer key ID does not match the configured trust entry.")
    public_key = _load_public_key(issuer_public_key)
    try:
        payload = jwt.decode(
            issuer_jwt,
            public_key,
            algorithms=[ALGORITHM],
            issuer=expected_issuer,
            options={"require": ["iss", "iat", "exp"]},
        )
    except Exception as exc:
        raise SDJWTError(f"Issuer signature or JWT validation failed: {exc}") from exc
    if expected_issuer is not None and payload.get("iss") != expected_issuer:
        raise SDJWTError("Credential issuer does not match the configured trust anchor.")
    if payload.get("_sd_alg", HASH_ALGORITHM) != HASH_ALGORITHM:
        raise SDJWTError("This profile supports only SHA-256 disclosure digests.")
    digest_list = payload.get("_sd", [])
    if not isinstance(digest_list, list) or any(not isinstance(x, str) for x in digest_list):
        raise SDJWTError("Issuer disclosure digest list is malformed.")
    if len(digest_list) != len(set(digest_list)):
        raise SDJWTError("Issuer JWT contains duplicate disclosure digests.")
    cnf = payload.get("cnf")
    if not isinstance(cnf, dict) or not isinstance(cnf.get("jwk"), dict):
        raise SDJWTError("Credential has no holder public key for required key binding.")
    _load_public_key(cnf["jwk"])
    return header, payload, digest_list


def _process_disclosures(
    issuer_payload: Mapping[str, Any], digest_list: Sequence[str], disclosure_parts: Sequence[str]
) -> Dict[str, Any]:
    processed = {k: v for k, v in issuer_payload.items() if k not in {"_sd", "_sd_alg"}}
    seen_digests = set()
    for encoded in disclosure_parts:
        if not encoded:
            raise SDJWTError("Empty disclosure component is not permitted.")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", encoded):
            raise SDJWTError("Disclosure is not valid base64url text.")
        digest = _b64url(hashlib.sha256(encoded.encode("ascii")).digest())
        if digest in seen_digests:
            raise SDJWTError("A disclosure was presented more than once.")
        seen_digests.add(digest)
        if digest not in digest_list:
            raise SDJWTError("A disclosure digest is not present in the issuer-signed JWT.")
        try:
            raw = json.loads(_b64url_decode(encoded).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SDJWTError("Disclosure JSON is malformed.") from exc
        if not isinstance(raw, list) or len(raw) != 3:
            raise SDJWTError("This profile accepts only three-item object-property disclosures.")
        salt, name, value = raw
        if not isinstance(salt, str) or len(_b64url_decode(salt)) < 16:
            raise SDJWTError("Disclosure salt is invalid or has insufficient entropy.")
        if not isinstance(name, str) or not name or name in RESERVED_CLAIMS:
            raise SDJWTError("Disclosure claim name is invalid or reserved.")
        if name in processed:
            raise SDJWTError("Disclosure collides with an already-present claim.")
        processed[name] = value
    return processed


def verify_issued_sd_jwt(
    sd_jwt: str,
    *,
    issuer_public_key: Any,
    expected_issuer: str,
) -> Dict[str, Any]:
    """Verify an issuer-to-holder SD-JWT (without a verifier Key Binding JWT)."""
    if not isinstance(sd_jwt, str) or not sd_jwt:
        raise SDJWTError("An SD-JWT string is required.")
    parts = sd_jwt.split("~")
    if len(parts) < 2 or parts[-1] != "":
        raise SDJWTError("Issued SD-JWT must end with a tilde and must not include a KB-JWT.")
    issuer_jwt, disclosure_parts = parts[0], parts[1:-1]
    header, payload, digest_list = _decode_issuer_jwt(issuer_jwt, issuer_public_key, expected_issuer)
    claims = _process_disclosures(payload, digest_list, disclosure_parts)
    permanent_claims = {k for k in payload if k not in {"_sd", "_sd_alg"}}
    return {
        "valid": True,
        "issuer": payload["iss"],
        "claims": claims,
        "disclosed_claim_names": [name for name in claims if name not in permanent_claims],
        "issued_at": payload["iat"],
        "expires_at": payload["exp"],
        "key_id": header.get("kid"),
        "holder_public_jwk": payload["cnf"]["jwk"],
    }


def verify_sd_jwt_presentation(
    presentation: str,
    *,
    issuer_public_key: Any,
    expected_issuer: str,
    expected_audience: str,
    expected_nonce: str,
    max_key_binding_age_seconds: int = 300,
    now: Optional[int] = None,
) -> Dict[str, Any]:
    """Verify issuer signature, disclosure membership, holder key binding and freshness."""
    if not isinstance(presentation, str) or not presentation:
        raise SDJWTError("An SD-JWT+KB presentation is required.")
    parts = presentation.split("~")
    if len(parts) < 2 or not parts[-1] or any(not x for x in parts[1:-1]):
        raise SDJWTError("Malformed SD-JWT+KB compact serialization.")
    issuer_jwt, disclosure_parts, kb_jwt = parts[0], parts[1:-1], parts[-1]
    header, issuer_payload, digest_list = _decode_issuer_jwt(
        issuer_jwt, issuer_public_key, expected_issuer
    )
    claims = _process_disclosures(issuer_payload, digest_list, disclosure_parts)

    try:
        kb_header = jwt.get_unverified_header(kb_jwt)
    except Exception as exc:
        raise SDJWTError("Key Binding JWT header is malformed.") from exc
    if kb_header.get("typ") != KB_TYP:
        raise SDJWTError("Key Binding JWT typ must be 'kb+jwt'.")
    if kb_header.get("alg") != ALGORITHM:
        raise SDJWTError("Only ES256 holder key-binding signatures are accepted.")
    holder_key = _load_public_key(issuer_payload["cnf"]["jwk"])
    try:
        kb_payload = jwt.decode(
            kb_jwt,
            holder_key,
            algorithms=[ALGORITHM],
            audience=expected_audience,
            options={"require": ["iat", "aud", "nonce", "sd_hash"]},
        )
    except Exception as exc:
        raise SDJWTError(f"Holder key-binding validation failed: {exc}") from exc

    if kb_payload.get("nonce") != expected_nonce:
        raise SDJWTError("Holder proof nonce does not match this verifier transaction.")
    current_time = int(time.time() if now is None else now)
    issued_at = kb_payload.get("iat")
    if not isinstance(issued_at, int) or issued_at > current_time + 30:
        raise SDJWTError("Holder proof timestamp is invalid or in the future.")
    if current_time - issued_at > max_key_binding_age_seconds:
        raise SDJWTError("Holder proof is stale; create a fresh presentation.")

    sd_jwt_part = "~".join(parts[:-1]) + "~"
    expected_sd_hash = _b64url(hashlib.sha256(sd_jwt_part.encode("ascii")).digest())
    if not secrets.compare_digest(kb_payload.get("sd_hash", ""), expected_sd_hash):
        raise SDJWTError("Key Binding JWT is not bound to this exact SD-JWT disclosure set.")

    permanent_claims = {k for k in issuer_payload if k not in {"_sd", "_sd_alg"}}
    disclosed_names = [name for name in claims if name not in permanent_claims]
    return {
        "valid": True,
        "issuer": issuer_payload["iss"],
        "claims": claims,
        "disclosed_claim_names": disclosed_names,
        "issuer_key_id": header.get("kid"),
        "key_binding_valid": True,
        "audience": kb_payload["aud"],
        "nonce_valid": True,
        "key_binding_iat": issued_at,
        "credential_expires_at": issuer_payload["exp"],
    }


def untrusted_issuer_from_sd_jwt(sd_jwt: str) -> str:
    """Read an issuer identifier for key selection only; this value is NOT trusted yet."""
    try:
        issuer_jwt = sd_jwt.split("~", 1)[0]
        payload_segment = issuer_jwt.split(".")[1]
        payload = json.loads(_b64url_decode(payload_segment).decode("utf-8"))
        issuer = payload.get("iss")
        if not isinstance(issuer, str) or not issuer:
            raise ValueError("iss missing")
        return issuer
    except Exception as exc:
        raise SDJWTError("Could not read an issuer identifier from the source token.") from exc


def fetch_remote_sd_jwt(
    url: str,
    *,
    allowed_hosts: Iterable[str],
    max_bytes: int = MAX_REMOTE_BYTES,
) -> Dict[str, Any]:
    """Fetch an issuer-hosted SD-JWT from an exact allowlisted HTTPS host.

    Redirects, non-HTTPS URLs, credentials in URLs, non-public DNS results,
    unexpected content types and oversized responses are rejected. Production
    deployments should additionally enforce outbound network policies and
    pinned DNS/TLS egress at the infrastructure layer.
    """
    parsed = urlsplit((url or "").strip())
    host = (parsed.hostname or "").rstrip(".").lower()
    allowlist = {item.strip().rstrip(".").lower() for item in allowed_hosts if item.strip()}
    if parsed.scheme.lower() != "https" or not host:
        raise SDJWTError("Online credential sources must use HTTPS.")
    if parsed.username or parsed.password or parsed.fragment:
        raise SDJWTError("URL credentials and fragments are not accepted.")
    try:
        port = parsed.port or 443
    except ValueError as exc:
        raise SDJWTError("Invalid URL port.") from exc
    if port != 443:
        raise SDJWTError("Only HTTPS on port 443 is accepted.")
    if host not in allowlist:
        raise SDJWTError("Source host is not in EACT_ALLOWED_SOURCE_HOSTS.")
    try:
        addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        resolved = {item[4][0] for item in addresses}
    except OSError as exc:
        raise SDJWTError("Could not resolve the allowlisted source host.") from exc
    if not resolved:
        raise SDJWTError("Source host did not resolve to an address.")
    for address in resolved:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError as exc:
            raise SDJWTError("Source host resolved to an invalid IP address.") from exc
        if not ip.is_global:
            raise SDJWTError("Source host resolves to a non-public IP address; request blocked.")

    session = requests.Session()
    session.trust_env = False
    try:
        response = session.get(
            url,
            headers={"Accept": "application/sd-jwt, text/plain;q=0.9"},
            timeout=(3.05, 10),
            allow_redirects=False,
            stream=True,
        )
        if 300 <= response.status_code < 400:
            raise SDJWTError("Redirects are disabled for credential source retrieval.")
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type not in {"application/sd-jwt", "text/plain"}:
            raise SDJWTError("Source must return application/sd-jwt or text/plain.")
        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            total += len(chunk)
            if total > max_bytes:
                raise SDJWTError("Remote credential exceeds the configured size limit.")
            chunks.append(chunk)
        body = b"".join(chunks)
        token = body.decode("ascii").strip()
        if not token:
            raise SDJWTError("The remote source returned an empty credential.")
        if len(token) > max_bytes or "." not in token or "~" not in token:
            raise SDJWTError("Remote response is not an SD-JWT compact serialization.")
    except requests.RequestException as exc:
        raise SDJWTError(f"Online source request failed: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise SDJWTError("Remote credential is not valid ASCII serialization.") from exc
    finally:
        session.close()

    retrieved = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return {
        "credential": token,
        "source_url": url,
        "source_host": host,
        "retrieved_at": retrieved,
        "content_type": content_type,
        "http_status": response.status_code,
        "byte_length": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
    }


def load_trusted_issuer_registry(raw_json: str) -> Dict[str, Dict[str, Any]]:
    """Parse EACT_TRUSTED_ISSUERS_JSON as issuer URL -> public JWK mapping."""
    if not raw_json.strip():
        return {}
    try:
        registry = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise SDJWTError("EACT_TRUSTED_ISSUERS_JSON is not valid JSON.") from exc
    if not isinstance(registry, dict):
        raise SDJWTError("Trusted issuer registry must be a JSON object.")
    checked: Dict[str, Dict[str, Any]] = {}
    for issuer, jwk in registry.items():
        if not isinstance(issuer, str) or not isinstance(jwk, dict):
            raise SDJWTError("Trusted issuer entries must map issuer URLs to public JWK objects.")
        _load_public_key(jwk)
        checked[issuer] = jwk
    return checked
