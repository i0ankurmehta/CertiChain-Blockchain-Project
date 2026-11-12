"""EACT decision rules.

EACT-v1 preserves the original single-disposition baseline.
EACT-v2 adds a multi-finding assessment for synthetic research scenarios.

This is a deterministic research prototype, not a production credential verifier.
Every evidence value is supplied by the lab fixture or operator; the prototype
does not independently authenticate issuers, query registries, or bind identities.
"""

from typing import Any, Dict, List


def evaluate_evidence(
    integrity: str,
    issuer_identity: str,
    credential_status: str,
    subject_match: str,
    source_state: str,
) -> Dict[str, str]:
    """EACT-v1: original first-match decision for baseline comparison."""
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


def evaluate_evidence_v2(
    integrity: str,
    issuer_identity: str,
    credential_status: str,
    subject_match: str,
    source_state: str,
) -> Dict[str, Any]:
    """Return one primary disposition plus every detected independent finding.

    Findings state what the supplied scenario inputs indicate. Because this
    prototype has no per-field provenance or live issuer connector, each finding
    explicitly identifies that its evidence is synthetic/manual and not
    independently validated by this application.
    """
    findings: List[Dict[str, str]] = []

    def add_finding(code: str, label: str, severity: str, detail: str,
                    dimension: str, supplied_value: str, authority: str,
                    next_action: str) -> None:
        findings.append({
            "code": code,
            "label": label,
            "severity": severity,
            "detail": detail,
            "dimension": dimension,
            "supplied_value": supplied_value,
            "authority": authority,
            "provenance": (
                "Synthetic/manual scenario input; the lab does not independently "
                "query or authenticate this evidence."
            ),
            "next_action": next_action,
        })

    # Record all dimensions, not only the first matching branch.
    if integrity == "mismatch":
        add_finding(
            "integrity_mismatch",
            "Integrity mismatch",
            "critical",
            "The supplied integrity result indicates that the document differs from its reference.",
            "Document integrity",
            integrity,
            "Reference provenance is not independently represented in this prototype.",
            "Obtain a fresh copy from the issuer and investigate the reference mismatch.",
        )
    elif integrity == "not_checked":
        add_finding(
            "integrity_not_checked",
            "Integrity not checked",
            "warning",
            "No document-integrity comparison is available.",
            "Document integrity",
            integrity,
            "No trusted comparison was performed by this lab.",
            "Obtain a trusted digest, signature validation, or issuer-side comparison.",
        )

    if issuer_identity != "authenticated":
        add_finding(
            "issuer_not_authenticated",
            "Issuer not authenticated",
            "warning",
            "The supplied evidence does not establish the issuer's identity.",
            "Issuer identity",
            issuer_identity,
            "Issuer authentication is unknown or not trusted in the supplied scenario.",
            "Verify the issuer through an independently trusted directory or channel.",
        )

    inactive_statuses = {"revoked", "suspended", "expired"}
    if credential_status in inactive_statuses:
        if issuer_identity == "authenticated" and source_state in {
            "available", "available_consent_granted", "status_source_available"
        }:
            add_finding(
                "credential_" + credential_status,
                "Credential " + credential_status,
                "critical",
                "The supplied authenticated-issuer/status-source scenario reports that the credential is not active.",
                "Credential status",
                credential_status,
                "Treated as authenticated within the synthetic scenario; no live status query occurred.",
                "Follow the issuer's status details and request clarification if required.",
            )
        else:
            add_finding(
                "status_claim_not_authenticated",
                "Inactive status claim is not authenticated",
                "warning",
                "The scenario reports " + credential_status + ", but the issuer/status evidence is not sufficiently authenticated to treat this as a confirmed status.",
                "Credential status",
                credential_status,
                "Status claim is not independently authenticated in this scenario.",
                "Authenticate the issuer and confirm status through its trusted status channel.",
            )
    elif credential_status == "unknown":
        add_finding(
            "credential_status_unknown",
            "Credential status unknown",
            "warning",
            "The current status of the credential has not been confirmed.",
            "Credential status",
            credential_status,
            "No authenticated current-status result is available in the supplied scenario.",
            "Query a trusted status source or obtain issuer confirmation.",
        )

    if subject_match == "mismatch":
        add_finding(
            "subject_mismatch",
            "Subject mismatch",
            "critical",
            "The supplied subject-check result indicates that the credential subject differs from the presenter.",
            "Subject match",
            subject_match,
            "The scenario supplies this result; the lab does not perform identity proofing.",
            "Review identity binding through an authorised, privacy-preserving process.",
        )
    elif subject_match == "not_checked":
        add_finding(
            "subject_not_checked",
            "Subject not checked",
            "warning",
            "The credential has not been reliably bound to the applicant.",
            "Subject match",
            subject_match,
            "No identity-binding check is performed by this lab.",
            "Complete an authorised subject-matching step.",
        )

    if source_state == "consent_pending":
        add_finding(
            "consent_pending",
            "Holder consent pending",
            "info",
            "The required holder-consent step has not completed.",
            "Source / consent",
            source_state,
            "Workflow state supplied by the synthetic scenario.",
            "Request or await the holder's consent, then retry authorised verification.",
        )
    elif source_state == "no_record_found":
        add_finding(
            "no_record_returned",
            "No record returned by queried source",
            "warning",
            "The queried source returned no matching record; this alone does not prove forgery.",
            "Source availability",
            source_state,
            "Repository query outcome supplied by the synthetic scenario.",
            "Check the issuer's official verification route or contact the issuer.",
        )
    elif source_state in {"service_unavailable", "status_service_unavailable"}:
        add_finding(
            "verification_source_unavailable",
            "Verification source unavailable",
            "warning",
            "The source could not be reached, so the evidence it would provide remains unconfirmed.",
            "Source availability",
            source_state,
            "Availability state supplied by the synthetic scenario.",
            "Retry later or use another issuer-approved verification channel.",
        )
    elif source_state == "offline_document_only":
        add_finding(
            "offline_document_only",
            "Offline document only",
            "warning",
            "Only a local document is available; no issuer verification source was queried.",
            "Source availability",
            source_state,
            "No external source connection exists in this prototype.",
            "Use an issuer-approved verification channel.",
        )

    # Select a primary disposition, without discarding the findings list.
    if integrity == "mismatch":
        primary = (
            "altered",
            "Integrity check failed — document not intact",
            "The supplied integrity comparison indicates a mismatch. Other findings are listed separately.",
            "Obtain a fresh issuer copy and investigate the mismatch before relying on this document.",
        )
    elif source_state == "consent_pending":
        primary = (
            "pending_consent",
            "Pending — consent required",
            "A required consent step is incomplete. This is a workflow state, not a fraud finding.",
            "Request or await holder consent, then retry the authorised verification.",
        )
    elif source_state == "no_record_found":
        primary = (
            "inconclusive_manual_review",
            "Inconclusive — no record returned",
            "The queried repository returned no record. Absence from one source does not establish forgery.",
            "Check another issuer-approved route or contact the issuer.",
        )
    elif source_state in {"service_unavailable", "status_service_unavailable"}:
        if (
            source_state == "status_service_unavailable"
            and integrity == "match"
            and issuer_identity == "authenticated"
            and subject_match == "match"
            and credential_status == "unknown"
        ):
            primary = (
                "issuer_and_integrity_verified_status_unknown",
                "Partially verified — status unknown",
                "Issuer identity, integrity and subject match are supported in the scenario; current status remains unconfirmed.",
                "Retry the status check or request issuer-issued status confirmation.",
            )
        else:
            primary = (
                "inconclusive_source_unavailable",
                "Inconclusive — source unavailable",
                "The required verification source could not be reached. Availability failure is not evidence of fraud.",
                "Retry later or use another issuer-approved verification channel.",
            )
    elif issuer_identity != "authenticated":
        primary = (
            "issuer_unverified",
            "Issuer unverified",
            "The issuer has not been authenticated. Any status claim must be treated as unverified.",
            "Verify the issuer through an independently trusted directory or channel.",
        )
    elif credential_status in inactive_statuses and subject_match == "mismatch":
        primary = (
            "manual_review_multiple_findings",
            "Manual review — multiple adverse findings",
            "The supplied evidence indicates both a non-active credential status and a subject mismatch.",
            "Refer for authorised manual review; preserve both findings in the review record.",
        )
    elif credential_status in inactive_statuses:
        primary = (
            credential_status,
            credential_status.capitalize(),
            "The authenticated scenario reports that the credential is not currently active.",
            "Follow the issuer's status details and request clarification if required.",
        )
    elif subject_match == "mismatch":
        primary = (
            "subject_mismatch",
            "Subject mismatch",
            "The supplied subject-check result does not match the presenter.",
            "Review identity binding through an authorised, privacy-preserving process.",
        )
    elif integrity == "not_checked":
        primary = (
            "integrity_not_checked",
            "Incomplete — integrity not checked",
            "No trusted comparison was performed for document contents.",
            "Obtain a trusted digest, signature validation, or issuer-side comparison.",
        )
    elif subject_match != "match":
        primary = (
            "subject_not_checked",
            "Incomplete — subject not checked",
            "The credential has not been reliably bound to the applicant.",
            "Complete an authorised subject-matching step.",
        )
    elif credential_status != "active":
        primary = (
            "credential_status_unknown",
            "Incomplete — credential status unknown",
            "Current credential status is not confirmed.",
            "Query a trusted status source or obtain issuer confirmation.",
        )
    elif integrity == "match" and source_state in {
        "available", "available_consent_granted", "status_source_available"
    }:
        primary = (
            "verified_against_trusted_source",
            "Verified against trusted source",
            "All five supplied scenario dimensions support verification.",
            "Retain only the minimum evidence required by organisational policy.",
        )
    else:
        primary = (
            "inconclusive_manual_review",
            "Inconclusive — manual review",
            "The evidence combination does not satisfy a defined verification rule.",
            "Review missing evidence and use an approved issuer channel.",
        )

    return {
        "disposition": primary[0],
        "label": primary[1],
        "explanation": primary[2],
        "next_action": primary[3],
        "findings": findings,
        "finding_count": len(findings),
        "evidence_dimensions_assessed": evidence_completeness(
            integrity, issuer_identity, credential_status, subject_match, source_state
        ),
        "provenance_note": (
            "Every input is a synthetic/manual scenario assertion. This prototype "
            "does not independently authenticate or fetch any evidence."
        ),
    }
