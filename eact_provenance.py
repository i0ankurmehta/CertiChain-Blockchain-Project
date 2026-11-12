"""EACT-B3 provenance and freshness assessment.

This module evaluates synthetic evidence metadata. It does not contact issuers,
validate real signatures, or establish the trustworthiness of live sources.

Experimental thresholds (90 days for issuer-authentication evidence and 24 hours
for credential-status evidence) are research parameters, not universal standards.
"""

from typing import Any, Dict, List, Optional


TRUSTED_REFERENCE_ORIGINS = {"issuer_signed_manifest", "trusted_registry_export"}
TRUSTED_ISSUER_AUTH_SOURCES = {"trusted_issuer_directory"}
TRUSTED_STATUS_SOURCES = {"issuer_status_api", "signed_registry_snapshot"}
INACTIVE_STATUSES = {"revoked", "suspended", "expired"}

DEFAULT_MAX_ISSUER_AUTH_AGE_DAYS = 90.0
DEFAULT_MAX_STATUS_AGE_HOURS = 24.0


def _validate_age(name: str, value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number or None")
    value = float(value)
    if value < 0:
        raise ValueError(f"{name} cannot be negative")
    return value


def evaluate_provenance(
    *,
    integrity_result: str,
    reference_origin: str,
    reference_signature_status: str,
    issuer_authentication_status: str,
    issuer_auth_source: str,
    issuer_auth_age_days: Optional[float],
    credential_status: str,
    status_source_type: str,
    status_source_authentication: str,
    status_checked_age_hours: Optional[float],
    max_issuer_auth_age_days: float = DEFAULT_MAX_ISSUER_AUTH_AGE_DAYS,
    max_status_age_hours: float = DEFAULT_MAX_STATUS_AGE_HOURS,
) -> Dict[str, Any]:
    """Return a primary assessment plus all provenance/freshness findings.

    Freshness is calculated from the supplied age values. The source identity,
    signature status, and timestamps are scenario assertions, not independently
    fetched or verified facts.
    """
    allowed_integrity = {"match", "mismatch", "not_checked"}
    allowed_signature = {"verified", "invalid", "not_checked"}
    allowed_authentication = {"authenticated", "unverified"}
    allowed_reference_origins = TRUSTED_REFERENCE_ORIGINS | {
        "local_database", "student_uploaded_hash", "unknown"
    }
    allowed_issuer_sources = TRUSTED_ISSUER_AUTH_SOURCES | {"manual_claim", "unknown"}
    allowed_status_sources = TRUSTED_STATUS_SOURCES | {"manual_claim", "unknown"}
    allowed_status_auth = {"authenticated", "unverified"}
    allowed_status_values = {"active", "revoked", "suspended", "expired", "unknown"}

    checks = [
        (integrity_result, allowed_integrity, "integrity_result"),
        (reference_signature_status, allowed_signature, "reference_signature_status"),
        (issuer_authentication_status, allowed_authentication, "issuer_authentication_status"),
        (reference_origin, allowed_reference_origins, "reference_origin"),
        (issuer_auth_source, allowed_issuer_sources, "issuer_auth_source"),
        (status_source_type, allowed_status_sources, "status_source_type"),
        (status_source_authentication, allowed_status_auth, "status_source_authentication"),
        (credential_status, allowed_status_values, "credential_status"),
    ]
    for value, allowed, name in checks:
        if value not in allowed:
            raise ValueError(f"Unsupported {name}: {value}")

    issuer_age = _validate_age("issuer_auth_age_days", issuer_auth_age_days)
    status_age = _validate_age("status_checked_age_hours", status_checked_age_hours)
    max_issuer_auth_age_days = _validate_age(
        "max_issuer_auth_age_days", max_issuer_auth_age_days
    )
    max_status_age_hours = _validate_age("max_status_age_hours", max_status_age_hours)

    if max_issuer_auth_age_days is None or max_status_age_hours is None:
        raise ValueError("Freshness thresholds must be numeric")

    reference_trusted = (
        reference_origin in TRUSTED_REFERENCE_ORIGINS
        and reference_signature_status == "verified"
    )
    issuer_source_trusted = (
        issuer_authentication_status == "authenticated"
        and issuer_auth_source in TRUSTED_ISSUER_AUTH_SOURCES
    )
    status_source_trusted = (
        status_source_authentication == "authenticated"
        and status_source_type in TRUSTED_STATUS_SOURCES
    )

    issuer_freshness = (
        "not_assessed" if not issuer_source_trusted
        else "timestamp_missing" if issuer_age is None
        else "stale" if issuer_age > max_issuer_auth_age_days
        else "current"
    )
    status_freshness = (
        "not_assessed" if not status_source_trusted
        else "timestamp_missing" if status_age is None
        else "stale" if status_age > max_status_age_hours
        else "current"
    )

    findings: List[Dict[str, str]] = []

    def add(code: str, label: str, severity: str, dimension: str,
            supplied_value: str, source: str, freshness: str,
            detail: str, next_action: str) -> None:
        findings.append({
            "code": code,
            "label": label,
            "severity": severity,
            "dimension": dimension,
            "supplied_value": supplied_value,
            "source": source,
            "freshness": freshness,
            "detail": detail,
            "provenance_note": (
                "Synthetic/manual metadata supplied to this lab; it has not been "
                "independently authenticated by the application."
            ),
            "next_action": next_action,
        })

    # Reference-digest provenance and integrity.
    if reference_signature_status == "invalid":
        add(
            "reference_signature_invalid",
            "Reference signature invalid",
            "critical",
            "Reference provenance",
            reference_signature_status,
            reference_origin,
            "not_applicable",
            "The supplied reference-signature check reports an invalid signature.",
            "Do not rely on this reference. Obtain a fresh signed reference through an approved issuer channel.",
        )
    elif not reference_trusted:
        add(
            "reference_provenance_unverified",
            "Reference provenance unverified",
            "warning",
            "Reference provenance",
            reference_origin + " / " + reference_signature_status,
            reference_origin,
            "not_established",
            "The reference origin is not on the configured trusted-source list or its signature is not verified. A hash match against this reference cannot establish credential integrity.",
            "Obtain a verifiable issuer-signed manifest or trusted registry reference.",
        )

    if integrity_result == "mismatch":
        if reference_trusted:
            add(
                "integrity_mismatch_confirmed",
                "Integrity mismatch against trusted reference",
                "critical",
                "Document integrity",
                integrity_result,
                reference_origin,
                "reference_signature_verified",
                "The supplied comparison reports a mismatch against a reference whose origin and signature satisfy this prototype's trust rules.",
                "Obtain a fresh credential from the issuer and investigate the mismatch.",
            )
        else:
            add(
                "integrity_comparison_untrusted",
                "Mismatch cannot be confirmed against an untrusted reference",
                "warning",
                "Document integrity",
                integrity_result,
                reference_origin,
                "reference_provenance_unverified",
                "A mismatch is reported, but the reference source is not trusted. The prototype cannot conclude that the credential itself was altered.",
                "First obtain and validate a trusted reference, then repeat the integrity comparison.",
            )
    elif integrity_result == "not_checked":
        add(
            "integrity_not_checked",
            "Integrity not checked",
            "warning",
            "Document integrity",
            integrity_result,
            reference_origin,
            "not_assessed",
            "No integrity comparison was performed.",
            "Obtain a trusted reference and run the integrity comparison.",
        )

    # Issuer authentication provenance and freshness.
    if not issuer_source_trusted:
        add(
            "issuer_authentication_unverified",
            "Issuer authentication not established",
            "warning",
            "Issuer authentication",
            issuer_authentication_status + " / " + issuer_auth_source,
            issuer_auth_source,
            "not_established",
            "The supplied issuer-authentication state is not backed by the configured trusted issuer directory.",
            "Authenticate the issuer through an independently trusted directory or approved channel.",
        )
    elif issuer_age is None:
        add(
            "issuer_authentication_timestamp_missing",
            "Issuer-authentication timestamp missing",
            "warning",
            "Issuer authentication freshness",
            "timestamp missing",
            issuer_auth_source,
            "unknown",
            "Issuer authentication is reported, but its age cannot be calculated.",
            "Obtain the issuer-authentication event timestamp and reassess freshness.",
        )
    elif issuer_age > max_issuer_auth_age_days:
        add(
            "issuer_authentication_stale",
            "Issuer-authentication evidence stale",
            "warning",
            "Issuer authentication freshness",
            f"{issuer_age:g} days old",
            issuer_auth_source,
            "stale",
            f"Issuer authentication is older than the configured {max_issuer_auth_age_days:g}-day research threshold.",
            "Re-authenticate the issuer and record a fresh verification timestamp.",
        )

    # Credential-status source and freshness.
    if not status_source_trusted:
        add(
            "status_source_untrusted",
            "Credential-status source not authenticated",
            "warning",
            "Credential status provenance",
            status_source_authentication + " / " + status_source_type,
            status_source_type,
            "not_established",
            "The status value is not backed by a configured trusted status source.",
            "Confirm status through an authenticated issuer status API or signed registry snapshot.",
        )
    elif status_age is None:
        add(
            "status_timestamp_missing",
            "Credential-status timestamp missing",
            "warning",
            "Credential status freshness",
            "timestamp missing",
            status_source_type,
            "unknown",
            "The status source is trusted in the supplied scenario, but the age of its status record cannot be calculated.",
            "Obtain the status-check timestamp and reassess freshness.",
        )
    elif status_age > max_status_age_hours:
        add(
            "status_evidence_stale",
            "Credential-status evidence stale",
            "warning",
            "Credential status freshness",
            f"{status_age:g} hours old",
            status_source_type,
            "stale",
            f"The status record is older than the configured {max_status_age_hours:g}-hour research threshold.",
            "Refresh the credential-status check through the trusted source.",
        )

    status_is_current_and_trusted = status_source_trusted and status_freshness == "current"
    if credential_status in INACTIVE_STATUSES:
        if status_is_current_and_trusted:
            add(
                "credential_status_" + credential_status,
                "Credential status: " + credential_status,
                "critical",
                "Credential status",
                credential_status,
                status_source_type,
                "current",
                "The supplied current status is reported by a configured trusted status source.",
                "Follow the issuer's status details and retain the minimum required evidence.",
            )
        else:
            add(
                "inactive_status_claim_unconfirmed",
                "Inactive-status claim not confirmed",
                "warning",
                "Credential status",
                credential_status,
                status_source_type,
                status_freshness,
                "The status field says " + credential_status + ", but the source is untrusted, stale, or lacks a timestamp. It must not be treated as a confirmed current status.",
                "Recheck the status through a trusted source and record its timestamp.",
            )
    elif credential_status == "unknown":
        add(
            "credential_status_unknown",
            "Credential status unknown",
            "warning",
            "Credential status",
            credential_status,
            status_source_type,
            status_freshness,
            "The current credential status has not been established.",
            "Obtain a current status response from an authenticated source.",
        )

    # Primary disposition. Findings are retained regardless of this ordering.
    if reference_signature_status == "invalid":
        primary = (
            "reference_signature_invalid",
            "Reference provenance failed",
            "The reference-signature check is invalid; the reference must not be used.",
            "Obtain a fresh signed reference through an approved issuer channel.",
        )
    elif not reference_trusted:
        primary = (
            "reference_provenance_unverified",
            "Reference provenance unverified",
            "The hash comparison cannot establish integrity because the reference source is not trusted.",
            "Obtain a verifiable issuer-signed manifest or trusted registry reference.",
        )
    elif integrity_result == "mismatch":
        primary = (
            "integrity_mismatch_confirmed",
            "Integrity mismatch against trusted reference",
            "The supplied comparison indicates a mismatch against a trusted reference.",
            "Obtain a fresh credential from the issuer and investigate the mismatch.",
        )
    elif integrity_result == "not_checked":
        primary = (
            "integrity_not_checked",
            "Incomplete — integrity not checked",
            "A trusted reference is available, but document integrity has not been compared.",
            "Run the integrity comparison against the trusted reference.",
        )
    elif not issuer_source_trusted:
        primary = (
            "issuer_authentication_unverified",
            "Issuer authentication unverified",
            "The issuer is not authenticated through the configured trusted source.",
            "Authenticate the issuer through an independently trusted directory or approved channel.",
        )
    elif issuer_freshness == "timestamp_missing":
        primary = (
            "issuer_authentication_timestamp_missing",
            "Issuer-authentication freshness unknown",
            "The issuer-authentication timestamp is missing, so freshness cannot be established.",
            "Obtain the issuer-authentication event timestamp and reassess.",
        )
    elif issuer_freshness == "stale":
        primary = (
            "issuer_authentication_stale",
            "Issuer-authentication evidence stale",
            f"The last issuer-authentication event is older than the {max_issuer_auth_age_days:g}-day research threshold.",
            "Re-authenticate the issuer and record a fresh verification timestamp.",
        )
    elif not status_source_trusted:
        primary = (
            "status_source_untrusted",
            "Credential-status source untrusted",
            "The current status claim is not backed by an authenticated status source.",
            "Confirm status through an authenticated issuer status API or signed registry snapshot.",
        )
    elif status_freshness == "timestamp_missing":
        primary = (
            "status_timestamp_missing",
            "Credential-status freshness unknown",
            "The status source is trusted in the scenario, but its timestamp is missing.",
            "Obtain the status-check timestamp and reassess freshness.",
        )
    elif status_freshness == "stale":
        primary = (
            "status_evidence_stale",
            "Credential-status evidence stale",
            f"The last status check is older than the {max_status_age_hours:g}-hour research threshold.",
            "Refresh the credential-status check through the trusted source.",
        )
    elif credential_status in INACTIVE_STATUSES:
        primary = (
            "credential_status_" + credential_status + "_confirmed",
            "Credential status confirmed: " + credential_status,
            "A current status record from a configured trusted source reports the credential as " + credential_status + ".",
            "Follow the issuer's status details and retain the minimum required evidence.",
        )
    elif credential_status == "unknown":
        primary = (
            "credential_status_unknown",
            "Credential status unknown",
            "No current active/inactive status is established.",
            "Obtain a current status response from an authenticated source.",
        )
    else:
        primary = (
            "provenance_and_freshness_current",
            "Evidence provenance and freshness checks passed",
            "The supplied reference, issuer-authentication evidence, and credential-status evidence satisfy this prototype's configured trust and freshness rules.",
            "Retain only the minimum verification metadata required by organisational policy.",
        )

    return {
        "disposition": primary[0],
        "label": primary[1],
        "explanation": primary[2],
        "next_action": primary[3],
        "findings": findings,
        "finding_count": len(findings),
        "reference_trusted": reference_trusted,
        "issuer_source_trusted": issuer_source_trusted,
        "issuer_freshness": issuer_freshness,
        "status_source_trusted": status_source_trusted,
        "status_freshness": status_freshness,
        "thresholds": {
            "max_issuer_auth_age_days": max_issuer_auth_age_days,
            "max_status_age_hours": max_status_age_hours,
        },
        "provenance_note": (
            "All evidence metadata is synthetic/manual input. The application does "
            "not independently validate signatures, issuer identities, or registry timestamps."
        ),
    }
