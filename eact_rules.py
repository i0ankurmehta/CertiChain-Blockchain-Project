"""Evidence-Aware Credential Triage (EACT) rules for synthetic experiments.

This module deliberately keeps evidence dimensions separate. A hash match alone
never establishes issuer identity, subject match, or current credential status.
It is a deterministic research prototype, not a production verifier.
"""

from typing import Dict, Any


def evaluate_evidence(
    integrity: str,
    issuer_identity: str,
    credential_status: str,
    subject_match: str,
    source_state: str,
) -> Dict[str, str]:
    """Return an explainable disposition and next action from evidence states."""
    # A confirmed integrity mismatch is the strongest negative evidence.
    if integrity == "mismatch":
        return {
            "disposition": "altered",
            "label": "Altered — integrity mismatch",
            "explanation": (
                "The credential content does not match the trusted reference "
                "digest or signature comparison. Do not treat this copy as intact."
            ),
            "next_action": "Obtain the credential again from its issuer and investigate the mismatch.",
        }

    # Workflow state is not a fraud signal.
    if source_state == "consent_pending":
        return {
            "disposition": "pending_consent",
            "label": "Pending — consent required",
            "explanation": (
                "The required holder consent has not yet been completed. "
                "The available evidence is insufficient for a final verification decision."
            ),
            "next_action": "Request or await the holder's consent, then retry the authorised verification.",
        }

    if source_state == "no_record_found":
        return {
            "disposition": "inconclusive_manual_review",
            "label": "Inconclusive — no record returned",
            "explanation": (
                "The queried source returned no matching record. This alone does not "
                "prove that the credential is forged; the issuer may use another channel "
                "or the record may not be present in that repository."
            ),
            "next_action": "Check the issuer's official verification route or contact the issuer.",
        }

    if source_state in {"service_unavailable", "status_service_unavailable"}:
        if (
            source_state == "status_service_unavailable"
            and integrity == "match"
            and issuer_identity == "authenticated"
            and subject_match == "match"
            and credential_status == "unknown"
        ):
            return {
                "disposition": "issuer_and_integrity_verified_status_unknown",
                "label": "Partially verified — status unknown",
                "explanation": (
                    "The issuer identity, document integrity, and subject match are "
                    "supported, but the status endpoint is unavailable. Current status "
                    "cannot be confirmed."
                ),
                "next_action": "Retry the status check or request an issuer-issued status confirmation.",
            }
        return {
            "disposition": "inconclusive_source_unavailable",
            "label": "Inconclusive — source unavailable",
            "explanation": (
                "The verification source could not be reached. Availability failure "
                "is not evidence that the credential is fraudulent."
            ),
            "next_action": "Retry later or use another issuer-approved verification channel.",
        }

    if issuer_identity != "authenticated":
        return {
            "disposition": "issuer_unverified",
            "label": "Issuer unverified",
            "explanation": (
                "The content may match a stored digest, but the issuer's identity "
                "has not been authenticated. Integrity is not the same as authenticity."
            ),
            "next_action": "Verify the issuer using an independently trusted issuer directory or channel.",
        }

    if credential_status in {"revoked", "suspended", "expired"}:
        return {
            "disposition": credential_status,
            "label": credential_status.capitalize(),
            "explanation": (
                "An authenticated issuer or trusted status source reports that the "
                "credential is not currently active."
            ),
            "next_action": "Follow the issuer's status details and request clarification if necessary.",
        }

    if subject_match == "mismatch":
        return {
            "disposition": "subject_mismatch",
            "label": "Subject mismatch",
            "explanation": (
                "The credential is associated with a subject that does not match "
                "the person presenting it."
            ),
            "next_action": "Check identity binding through an authorised, privacy-preserving process.",
        }

    if integrity == "not_checked":
        return {
            "disposition": "integrity_not_checked",
            "label": "Incomplete — integrity not checked",
            "explanation": "No trusted comparison was performed for the document contents.",
            "next_action": "Obtain a trusted digest, signature validation, or issuer-side comparison.",
        }

    if subject_match != "match":
        return {
            "disposition": "subject_not_checked",
            "label": "Incomplete — subject not checked",
            "explanation": "The credential has not been reliably bound to the applicant.",
            "next_action": "Complete an authorised subject-matching step.",
        }

    if credential_status != "active":
        return {
            "disposition": "credential_status_unknown",
            "label": "Incomplete — credential status unknown",
            "explanation": "The issuer is authenticated, but current credential status is not confirmed.",
            "next_action": "Query a trusted status source or obtain issuer confirmation.",
        }

    if integrity == "match" and source_state in {
        "available",
        "available_consent_granted",
        "status_source_available",
    }:
        return {
            "disposition": "verified_against_trusted_source",
            "label": "Verified against trusted source",
            "explanation": (
                "The evidence indicates matching document integrity, an authenticated "
                "issuer, active status, and a subject match from an available source."
            ),
            "next_action": "Retain the minimum verification evidence required by the organisation's policy.",
        }

    return {
        "disposition": "inconclusive_manual_review",
        "label": "Inconclusive — manual review",
        "explanation": "The evidence combination does not satisfy a defined verification rule.",
        "next_action": "Review the missing evidence and contact the issuer through an approved channel.",
    }


def hash_only_baseline(integrity: str) -> Dict[str, str]:
    """Model the intentionally simplistic hash-only baseline."""
    if integrity == "match":
        return {
            "disposition": "valid",
            "label": "VALID (hash matches)",
            "warning": "This shortcut does not establish issuer identity, subject match, or status.",
        }
    if integrity == "mismatch":
        return {
            "disposition": "invalid",
            "label": "INVALID (hash mismatch)",
            "warning": "A mismatch is an integrity failure; it does not by itself explain the cause.",
        }
    return {
        "disposition": "not_applicable",
        "label": "NO HASH RESULT",
        "warning": "No hash comparison result is available.",
    }


def evidence_completeness(
    integrity: str,
    issuer_identity: str,
    credential_status: str,
    subject_match: str,
    source_state: str,
) -> int:
    """Count explicitly assessed dimensions; this is not a confidence score."""
    unknown_values = {"unknown", "not_checked", "not_applicable", ""}
    values = [integrity, issuer_identity, credential_status, subject_match, source_state]
    return sum(value not in unknown_values for value in values)
