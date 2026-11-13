"""EACT-B4 trust-anchor governance and evidence-lifecycle assessment.

This deterministic research model distinguishes a key's current state from
whether a historical credential signature was valid at signing time.

No private keys are stored, no signatures are cryptographically verified here,
and no live issuer directory, timestamp authority, or revocation service is queried.
All identity, trust, timestamp, and lifecycle-event properties are supplied fixture
metadata and must not be represented as live verification.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


TRUSTED_EVENT_SOURCES = {
    "trusted_anchor_registry",
    "issuer_security_notice",
    "trusted_trust_list",
}
TRUSTED_TIMESTAMP_SOURCES = {
    "trusted_timestamp_authority",
    "qualified_timestamp_authority",
}
GENESIS_HASH = "0" * 64


def _parse_time(value: Optional[str], field_name: str) -> Optional[datetime]:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be an ISO-8601 string or None")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone (UTC 'Z' is recommended)")
    return parsed.astimezone(timezone.utc)


def _trusted_timestamp(verification: Dict[str, Any]) -> bool:
    return (
        verification.get("timestamp_source") in TRUSTED_TIMESTAMP_SOURCES
        and verification.get("timestamp_signature_status") == "verified"
        and _parse_time(verification.get("signed_at"), "signed_at") is not None
    )


def _trusted_event(event: Dict[str, Any]) -> bool:
    return (
        event.get("authority_status") == "authenticated"
        and event.get("source") in TRUSTED_EVENT_SOURCES
        and event.get("event_signature_status") == "verified"
    )


def _latest_event(events: Iterable[Dict[str, Any]], as_of: datetime) -> Optional[Dict[str, Any]]:
    eligible = []
    for event in events:
        effective_at = _parse_time(event.get("effective_at"), "event.effective_at")
        if effective_at is not None and effective_at <= as_of:
            eligible.append((effective_at, event))
    if not eligible:
        return None
    eligible.sort(key=lambda pair: pair[0])
    return eligible[-1][1]


def evaluate_trust_lifecycle(
    *,
    anchor: Dict[str, Any],
    lifecycle_events: List[Dict[str, Any]],
    verification: Dict[str, Any],
    assessment_time: str,
) -> Dict[str, Any]:
    """Assess anchor governance and a historical signature against event time.

    Routine rotation/revocation/expiry can stop future use without automatically
    invalidating an earlier signature when a trusted signing-time proof exists.
    A compromise effective at or before signing is treated as critical. A later
    compromise does not automatically invalidate a provably earlier signature,
    but the historical result is separately flagged for review.

    Event effective_at and recorded_at are intentionally separate. This models
    delayed reporting (similar to the distinction between invalidityDate and
    revocation processing time in X.509 CRLs).
    """
    if not isinstance(anchor, dict) or not isinstance(verification, dict):
        raise TypeError("anchor and verification must be dictionaries")
    if not isinstance(lifecycle_events, list):
        raise TypeError("lifecycle_events must be a list")

    allowed_registry_status = {"trusted", "untrusted", "unknown"}
    allowed_signature_status = {"valid", "invalid", "not_checked"}
    allowed_event_types = {"rotated", "revoked", "compromised", "distrusted", "reinstated"}

    registry_status = anchor.get("registry_status", "unknown")
    if registry_status not in allowed_registry_status:
        raise ValueError(f"Unsupported registry_status: {registry_status}")
    signature_status = verification.get("signature_status", "not_checked")
    if signature_status not in allowed_signature_status:
        raise ValueError(f"Unsupported signature_status: {signature_status}")

    assessment_dt = _parse_time(assessment_time, "assessment_time")
    signed_dt = _parse_time(verification.get("signed_at"), "signed_at")
    valid_from_dt = _parse_time(anchor.get("valid_from"), "anchor.valid_from")
    expires_at_dt = _parse_time(anchor.get("expires_at"), "anchor.expires_at")

    if assessment_dt is None:
        raise ValueError("assessment_time is required")
    if valid_from_dt and expires_at_dt and valid_from_dt >= expires_at_dt:
        raise ValueError("anchor.valid_from must be earlier than anchor.expires_at")

    trusted_events: List[Dict[str, Any]] = []
    untrusted_events: List[Dict[str, Any]] = []
    for event in lifecycle_events:
        if not isinstance(event, dict):
            raise TypeError("Each lifecycle event must be a dictionary")
        event_type = event.get("event_type")
        if event_type not in allowed_event_types:
            raise ValueError(f"Unsupported lifecycle event_type: {event_type}")
        effective_dt = _parse_time(event.get("effective_at"), "event.effective_at")
        recorded_dt = _parse_time(event.get("recorded_at"), "event.recorded_at")
        if effective_dt is None or recorded_dt is None:
            raise ValueError("Lifecycle events require effective_at and recorded_at")
        if effective_dt > assessment_dt:
            # Future events are allowed and shown as scheduled.
            pass
        (trusted_events if _trusted_event(event) else untrusted_events).append(event)

    timestamp_trusted = _trusted_timestamp(verification)
    findings: List[Dict[str, str]] = []

    def add(
        code: str,
        label: str,
        severity: str,
        dimension: str,
        supplied_value: str,
        detail: str,
        next_action: str,
    ) -> None:
        findings.append({
            "code": code,
            "label": label,
            "severity": severity,
            "dimension": dimension,
            "supplied_value": supplied_value,
            "detail": detail,
            "next_action": next_action,
            "provenance_note": (
                "Synthetic/manual metadata supplied to this lab; the application "
                "does not independently authenticate this source or event."
            ),
        })

    anchor_trusted = bool(anchor.get("registered")) and registry_status == "trusted"
    if not anchor.get("registered") or registry_status != "trusted":
        add(
            "trust_anchor_not_established",
            "Trust anchor not established",
            "critical",
            "Trust-anchor registration",
            f"registered={bool(anchor.get('registered'))}; registry_status={registry_status}",
            "The key is absent from, or not vouched for by, the configured trusted anchor registry.",
            "Obtain the issuer key and fingerprint through an independently governed trust-anchor onboarding process.",
        )

    if signature_status == "invalid":
        add(
            "credential_signature_invalid",
            "Credential signature invalid",
            "critical",
            "Credential signature",
            signature_status,
            "The supplied signature-check result indicates that the credential signature is invalid.",
            "Reject this signature and obtain a fresh credential from the issuer.",
        )
    elif signature_status == "not_checked":
        add(
            "credential_signature_not_checked",
            "Credential signature not checked",
            "warning",
            "Credential signature",
            signature_status,
            "No cryptographic signature-validation result is available in this scenario.",
            "Validate the signature with a supported cryptographic implementation and trusted public key.",
        )

    if not timestamp_trusted:
        timestamp_source = verification.get("timestamp_source", "unknown")
        timestamp_status = verification.get("timestamp_signature_status", "not_checked")
        add(
            "trusted_signing_time_not_established",
            "Trusted signing time not established",
            "warning",
            "Historical time evidence",
            f"{timestamp_source} / {timestamp_status}",
            "A local or unsigned timestamp cannot establish when the signature was made relative to rotation, expiry, revocation, or compromise.",
            "Obtain a verifiable timestamp token from an accepted timestamp authority or issuer-approved archival process.",
        )

    for event in untrusted_events:
        add(
            "lifecycle_event_unverified",
            "Lifecycle event not authenticated",
            "warning",
            "Trust-anchor event provenance",
            f"{event.get('event_type')} / {event.get('source')} / {event.get('authority_status')}",
            "A reported key lifecycle event is not supported by the configured trusted event source and authenticated event signature.",
            "Confirm the event through the trust-anchor registry or an authenticated issuer security notice.",
        )

    for event in trusted_events:
        if event["event_type"] == "compromised":
            effective_dt = _parse_time(event["effective_at"], "event.effective_at")
            recorded_dt = _parse_time(event["recorded_at"], "event.recorded_at")
            if effective_dt and recorded_dt and recorded_dt > effective_dt:
                add(
                    "compromise_reported_after_effective_time",
                    "Compromise was reported after its effective time",
                    "critical",
                    "Compromise reporting chronology",
                    f"effective_at={event['effective_at']}; recorded_at={event['recorded_at']}",
                    "The trusted event says the key became compromised before the registry recorded the report. Signatures in the interval require retrospective assessment.",
                    "Identify affected credentials using trusted signing timestamps and the issuer's compromise investigation.",
                )

    # Determine the current key state at assessment time.
    current_event = _latest_event(trusted_events, assessment_dt)
    if current_event:
        current_event_type = current_event["event_type"]
        current_state = {
            "rotated": "rotated",
            "revoked": "revoked",
            "compromised": "compromised",
            "distrusted": "distrusted",
            "reinstated": "active",
        }[current_event_type]
    elif expires_at_dt and assessment_dt > expires_at_dt:
        current_state = "expired"
    elif valid_from_dt and assessment_dt < valid_from_dt:
        current_state = "not_yet_valid"
    else:
        current_state = "active"

    # Find the latest trusted event effective at signing time, if signing time is trusted.
    signing_event = _latest_event(trusted_events, signed_dt) if timestamp_trusted and signed_dt else None
    post_signing_events = []
    if timestamp_trusted and signed_dt:
        post_signing_events = [
            event for event in trusted_events
            if _parse_time(event["effective_at"], "event.effective_at") > signed_dt
            and _parse_time(event["effective_at"], "event.effective_at") <= assessment_dt
        ]

    historical_state = "unknown"
    if timestamp_trusted and signed_dt:
        if valid_from_dt and signed_dt < valid_from_dt:
            historical_state = "not_yet_valid"
            add(
                "key_not_valid_at_signing",
                "Key was not yet valid at signing",
                "critical",
                "Key validity interval",
                verification["signed_at"],
                "The credential's trusted signing time predates the anchor's valid-from time.",
                "Reject the signature and obtain an issuer-issued credential signed by a valid key.",
            )
        elif expires_at_dt and signed_dt > expires_at_dt:
            historical_state = "expired"
            add(
                "key_expired_at_signing",
                "Key expired before signing",
                "critical",
                "Key validity interval",
                verification["signed_at"],
                "The credential was signed after the trust anchor's expiry time.",
                "Reject the signature and obtain a current credential from the issuer.",
            )
        elif signing_event:
            event_type = signing_event["event_type"]
            if event_type == "compromised":
                historical_state = "compromised"
                add(
                    "key_compromised_at_signing",
                    "Key compromised at signing time",
                    "critical",
                    "Key compromise",
                    signing_event["effective_at"],
                    "A trusted compromise event was effective at or before the credential's trusted signing time.",
                    "Quarantine the credential and refer it for issuer-led compromise investigation.",
                )
            elif event_type in {"revoked", "distrusted"}:
                historical_state = "revoked"
                add(
                    "key_revoked_at_signing",
                    "Key revoked or distrusted at signing time",
                    "critical",
                    "Key trust status",
                    signing_event["effective_at"],
                    "A trusted revocation/distrust event was effective at or before the credential's trusted signing time.",
                    "Do not accept the signature; request issuer confirmation and a reissued credential.",
                )
            elif event_type == "rotated":
                historical_state = "rotated"
                add(
                    "key_rotated_before_signing",
                    "Key had already been rotated",
                    "critical",
                    "Key lifecycle",
                    signing_event["effective_at"],
                    "The credential's trusted signing time is at or after the key's rotation effective time.",
                    "Verify the credential using the replacement key recorded by the issuer.",
                )
            elif event_type == "reinstated":
                historical_state = "active"
            else:
                historical_state = "active"
        else:
            historical_state = "active"

    # Evaluate lifecycle events that occurred after this signature was made.
    post_signing_types = {event["event_type"] for event in post_signing_events}
    if timestamp_trusted and signed_dt and historical_state == "active":
        compromise_after = next(
            (event for event in post_signing_events if event["event_type"] == "compromised"),
            None,
        )
        rotation_after = next(
            (event for event in post_signing_events if event["event_type"] == "rotated"),
            None,
        )
        revoke_after = next(
            (event for event in post_signing_events if event["event_type"] in {"revoked", "distrusted"}),
            None,
        )
        if compromise_after:
            historical_state = "pre_compromise"
            add(
                "signature_predates_key_compromise",
                "Signature predates the compromise effective time",
                "warning",
                "Historical key compromise",
                f"signed_at={verification['signed_at']}; compromise_effective_at={compromise_after['effective_at']}",
                "A trusted timestamp places signing before the stated compromise effective time. This supports historical ordering, but archival/signature policy must determine whether reliance is permitted.",
                "Preserve the timestamp and event evidence; request issuer policy or an authorised revalidation decision.",
            )
        elif rotation_after:
            historical_state = "pre_rotation"
            add(
                "signature_predates_key_rotation",
                "Historical signature predates routine key rotation",
                "info",
                "Historical key lifecycle",
                f"signed_at={verification['signed_at']}; rotation_effective_at={rotation_after['effective_at']}",
                "A trusted timestamp places signing before routine rotation. Rotation blocks future use of the old key but does not automatically invalidate a provably earlier signature in this prototype.",
                "Retain the historical verification record and confirm the issuer's archival-signature policy.",
            )
        elif revoke_after:
            historical_state = "pre_revocation"
            add(
                "signature_predates_key_revocation",
                "Historical signature predates key revocation",
                "warning",
                "Historical key lifecycle",
                f"signed_at={verification['signed_at']}; revocation_effective_at={revoke_after['effective_at']}",
                "A trusted timestamp places signing before revocation. The reason and issuer policy determine whether historical signatures remain acceptable.",
                "Preserve the historic evidence and seek issuer policy on signatures created before revocation.",
            )

    scheduled_events = [
        event for event in trusted_events
        if _parse_time(event["effective_at"], "event.effective_at") > assessment_dt
    ]
    for event in scheduled_events:
        add(
            "future_lifecycle_event_scheduled",
            "Future lifecycle event scheduled",
            "info",
            "Lifecycle planning",
            f"{event['event_type']} at {event['effective_at']}",
            "A trusted lifecycle event is scheduled after the assessment time and is not yet effective.",
            "Plan issuer and verifier transition before the event's effective time.",
        )

    # Choose a primary disposition. Secondary findings are never discarded.
    if not anchor_trusted:
        primary = (
            "trust_anchor_not_established",
            "Trust anchor not established",
            "The key is not currently established by the configured trusted registry.",
            "Obtain the issuer key and fingerprint through a governed trust-anchor onboarding process.",
        )
    elif signature_status == "invalid":
        primary = (
            "credential_signature_invalid",
            "Credential signature invalid",
            "The supplied signature check reports that the credential signature is invalid.",
            "Reject this signature and obtain a fresh issuer-issued credential.",
        )
    elif signature_status == "not_checked":
        primary = (
            "credential_signature_not_checked",
            "Credential signature not checked",
            "The credential's cryptographic signature has not been validated, so the system cannot report a valid signature.",
            "Validate the signature with a supported cryptographic implementation and trusted public key.",
        )
    elif not timestamp_trusted:
        primary = (
            "trusted_signing_time_not_established",
            "Historical signing time not established",
            "The application cannot reliably order this signature against key rotation, expiry, revocation, or compromise.",
            "Obtain a verifiable timestamp token from an accepted timestamp authority.",
        )
    elif historical_state == "not_yet_valid":
        primary = (
            "key_not_valid_at_signing",
            "Key was not yet valid at signing",
            "The credential signing time predates the key's validity interval.",
            "Reject the signature and obtain an issuer-issued credential signed by a valid key.",
        )
    elif historical_state == "expired":
        primary = (
            "key_expired_at_signing",
            "Key expired before signing",
            "The credential was signed after the trust anchor expired.",
            "Reject the signature and obtain a current issuer-issued credential.",
        )
    elif historical_state == "compromised":
        primary = (
            "key_compromised_at_signing",
            "Key compromised at signing time",
            "The trusted compromise effective time is at or before the credential's signing time.",
            "Quarantine the credential and refer it for issuer-led compromise investigation.",
        )
    elif historical_state == "revoked":
        primary = (
            "key_revoked_at_signing",
            "Key revoked or distrusted at signing time",
            "A trusted revocation/distrust event was effective at or before signing.",
            "Do not accept the signature; request issuer confirmation and a reissued credential.",
        )
    elif historical_state == "rotated":
        primary = (
            "key_rotated_before_signing",
            "Key was rotated before signing",
            "The credential was signed after the old key's rotation effective time.",
            "Verify the credential using the replacement key recorded by the issuer.",
        )
    elif "lifecycle_event_unverified" in {finding["code"] for finding in findings}:
        primary = (
            "lifecycle_event_unverified",
            "Lifecycle event requires manual review",
            "A reported key lifecycle event has not been authenticated by the configured trusted governance sources.",
            "Confirm the lifecycle event through an authenticated trust registry or issuer security notice.",
        )
    elif historical_state == "pre_compromise":
        primary = (
            "historical_signature_predates_compromise",
            "Historical signature predates later key compromise",
            "A trusted timestamp places signing before the compromise effective time; historical reliance still requires issuer policy.",
            "Preserve timestamp and event evidence and request issuer-led archival-signature review.",
        )
    elif historical_state == "pre_rotation":
        primary = (
            "historical_signature_predates_rotation",
            "Historical signature predates routine key rotation",
            "A trusted timestamp places signing before the rotation effective time.",
            "Retain the historical verification record and confirm the issuer's archival policy.",
        )
    elif historical_state == "pre_revocation":
        primary = (
            "historical_signature_predates_revocation",
            "Historical signature predates key revocation",
            "A trusted timestamp places signing before revocation; the revocation reason and issuer policy still matter.",
            "Preserve the evidence and seek issuer policy on pre-revocation signatures.",
        )
    elif current_state == "expired":
        primary = (
            "historically_valid_key_now_expired",
            "Historical signature predates key expiry",
            "The trusted signing time falls within the key validity interval, although the key has since expired.",
            "Preserve the historical verification record; do not use the expired key for new signatures.",
        )
    elif current_state == "compromised":
        primary = (
            "historical_key_compromise_review",
            "Key currently compromised — historical review required",
            "The key is now marked compromised. This record's trusted signing time predates the effective compromise time, but issuer archival policy must determine reliance.",
            "Preserve evidence and request issuer-led review of signatures made before the compromise effective time.",
        )
    elif current_state in {"revoked", "distrusted"}:
        primary = (
            "historical_key_revoked",
            "Key currently revoked or distrusted",
            "The trusted signing time predates the current key revocation/distrust state.",
            "Retain historical evidence and confirm the issuer's pre-revocation signature policy.",
        )
    elif current_state == "rotated":
        primary = (
            "historical_key_rotated",
            "Key rotated — historical signature retained",
            "The trusted signing time predates routine rotation; the old key is not for new signatures.",
            "Retain the historic record and use the replacement key for new signatures.",
        )
    else:
        primary = (
            "active_key_historical_signature_valid",
            "Active trust anchor — historical signature valid in prototype",
            "The supplied registration, signature and trusted-time metadata satisfy the prototype's current checks.",
            "Retain the minimum audit evidence required by the issuer's policy.",
        )

    return {
        "disposition": primary[0],
        "label": primary[1],
        "explanation": primary[2],
        "next_action": primary[3],
        "findings": findings,
        "finding_count": len(findings),
        "anchor_trusted": anchor_trusted,
        "current_key_state": current_state,
        "historical_key_state_at_signing": historical_state,
        "timestamp_trusted": timestamp_trusted,
        "trusted_event_count": len(trusted_events),
        "untrusted_event_count": len(untrusted_events),
        "scheduled_event_count": len(scheduled_events),
        "provenance_note": (
            "All key, event, timestamp and signature properties are synthetic/manual "
            "scenario assertions. The application does not perform cryptographic "
            "signature verification or contact a live trust registry."
        ),
    }


def _audit_payload(sequence: int, previous_hash: str, record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "sequence": sequence,
        "previous_hash": previous_hash,
        "record": record,
    }


def build_audit_trail(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build a deterministic hash-linked audit demonstration.

    A hash chain makes alteration detectable when hashes are recomputed from a
    trusted checkpoint. It does not, by itself, make storage immutable or prevent
    an attacker from rewriting the entire chain.
    """
    trail: List[Dict[str, Any]] = []
    previous_hash = GENESIS_HASH
    for index, record in enumerate(records, start=1):
        payload = _audit_payload(index, previous_hash, record)
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        record_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        trail.append({**payload, "record_hash": record_hash})
        previous_hash = record_hash
    return trail


def verify_audit_trail(trail: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Check sequence, previous-hash linkage and record hashes."""
    previous_hash = GENESIS_HASH
    for index, entry in enumerate(trail, start=1):
        if entry.get("sequence") != index:
            return {"valid": False, "first_invalid_index": index, "reason": "sequence_mismatch"}
        if entry.get("previous_hash") != previous_hash:
            return {"valid": False, "first_invalid_index": index, "reason": "previous_hash_mismatch"}
        payload = _audit_payload(index, previous_hash, entry.get("record", {}))
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        expected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if entry.get("record_hash") != expected_hash:
            return {"valid": False, "first_invalid_index": index, "reason": "record_hash_mismatch"}
        previous_hash = entry["record_hash"]
    return {"valid": True, "first_invalid_index": None, "reason": "all_links_valid"}
