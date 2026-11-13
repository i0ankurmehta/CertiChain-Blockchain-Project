"""EACT-B5 purpose-bound, privacy-preserving academic disclosure research model.

This module evaluates a synthetic verifier request against a purpose policy and
holder-approved claims. It compares a complete academic-record baseline with a
minimum-claims presentation proposal.

It does NOT create or verify a Verifiable Credential, SD-JWT, digital signature,
selective-disclosure proof, zero-knowledge proof, or live issuer/status response.
Predicate checks are performed against hidden synthetic fixture values only.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Set


CLAIM_CATALOG: Dict[str, Dict[str, Any]] = {
    "award_status": {"label": "Award status", "sensitivity": "low", "weight": 1},
    "qualification_level": {"label": "Qualification level", "sensitivity": "low", "weight": 1},
    "program_name": {"label": "Programme name", "sensitivity": "medium", "weight": 2},
    "institution_name": {"label": "Awarding institution", "sensitivity": "medium", "weight": 2},
    "graduation_year": {"label": "Graduation year", "sensitivity": "medium", "weight": 2},
    "enrollment_status": {"label": "Enrollment status", "sensitivity": "low", "weight": 1},
    "cgpa": {"label": "CGPA (raw value)", "sensitivity": "high", "weight": 4},
    "transcript": {"label": "Detailed transcript / subject marks", "sensitivity": "high", "weight": 5},
    "roll_number": {"label": "University roll number", "sensitivity": "high", "weight": 4},
    "date_of_birth": {"label": "Date of birth", "sensitivity": "high", "weight": 4},
    "home_address": {"label": "Home address", "sensitivity": "high", "weight": 5},
    "email": {"label": "Personal email", "sensitivity": "high", "weight": 4},
    "global_student_id": {"label": "Persistent global student identifier", "sensitivity": "high", "weight": 5},
    "exact_award_date": {"label": "Exact award date", "sensitivity": "medium", "weight": 3},
    "campus": {"label": "Campus", "sensitivity": "medium", "weight": 3},
}

PREDICATES: Dict[str, Dict[str, Any]] = {
    "cgpa_at_least_7_0": {
        "label": "CGPA at least 7.0",
        "claim": "cgpa",
        "operator": "gte",
        "threshold": 7.0,
    },
    "cgpa_at_least_6_5": {
        "label": "CGPA at least 6.5",
        "claim": "cgpa",
        "operator": "gte",
        "threshold": 6.5,
    },
}

PURPOSE_POLICIES: Dict[str, Dict[str, Any]] = {
    "employment_degree_verification": {
        "label": "Employment — confirm awarded degree",
        "required_claims": ["award_status", "qualification_level", "program_name", "institution_name"],
        "allowed_claims": ["award_status", "qualification_level", "program_name", "institution_name", "graduation_year"],
        "required_predicates": [],
        "allowed_predicates": [],
        "description": "Confirm that the candidate holds the stated qualification from the named institution.",
    },
    "scholarship_eligibility": {
        "label": "Scholarship — minimum academic threshold",
        "required_claims": ["award_status", "program_name", "institution_name"],
        "allowed_claims": ["award_status", "program_name", "institution_name"],
        "required_predicates": ["cgpa_at_least_7_0"],
        "allowed_predicates": ["cgpa_at_least_7_0"],
        "description": "Confirm the qualification and whether the hidden CGPA meets the stated threshold.",
    },
    "internship_enrollment": {
        "label": "Internship — confirm current enrollment",
        "required_claims": ["enrollment_status", "program_name", "institution_name"],
        "allowed_claims": ["enrollment_status", "program_name", "institution_name", "graduation_year"],
        "required_predicates": [],
        "allowed_predicates": [],
        "description": "Confirm current enrollment and programme without requesting a full transcript.",
    },
    "postgraduate_admission": {
        "label": "Postgraduate admission — eligibility check",
        "required_claims": ["award_status", "qualification_level", "program_name", "institution_name"],
        "allowed_claims": ["award_status", "qualification_level", "program_name", "institution_name", "graduation_year"],
        "required_predicates": ["cgpa_at_least_6_5"],
        "allowed_predicates": ["cgpa_at_least_6_5"],
        "description": "Confirm the prior qualification and a minimum academic threshold without exposing raw marks.",
    },
}

QUASI_IDENTIFIER_GROUP = {
    "program_name",
    "institution_name",
    "graduation_year",
    "exact_award_date",
    "campus",
}


def _unique(items: Optional[Sequence[str]]) -> List[str]:
    if items is None:
        return []
    return list(dict.fromkeys(items))


def _validate_names(names: Sequence[str], allowed: Set[str], label: str) -> None:
    unknown = sorted(set(names) - allowed)
    if unknown:
        raise ValueError(f"Unknown {label}: {', '.join(unknown)}")


def _finding(
    code: str,
    label: str,
    severity: str,
    dimension: str,
    supplied_value: str,
    detail: str,
    next_action: str,
) -> Dict[str, str]:
    return {
        "code": code,
        "label": label,
        "severity": severity,
        "dimension": dimension,
        "supplied_value": supplied_value,
        "detail": detail,
        "next_action": next_action,
    }


def _base_result(scenario: Dict[str, Any], credential: Dict[str, Any]) -> Dict[str, Any]:
    claims = credential["claims"]
    full_units = sum(CLAIM_CATALOG[key]["weight"] for key in claims if key in CLAIM_CATALOG)
    return {
        "scenario_id": scenario.get("id", "CUSTOM"),
        "scenario_title": scenario.get("title", "Custom disclosure request"),
        "disposition": "not_assessed",
        "message": "",
        "can_verify_purpose": False,
        "presentation_ready": False,
        "privacy_review_required": False,
        "purpose": scenario.get("purpose", "unknown"),
        "issuer_trust": credential.get("issuer_trust", "unknown"),
        "credential_status": credential.get("credential_status", "unknown"),
        "minimum_required_claims": [],
        "required_predicates": [],
        "requested_claims": [],
        "approved_claims": [],
        "proposed_claims": {},
        "minimum_presentation": {},
        "requested_predicates": [],
        "approved_predicates": [],
        "predicate_results": [],
        "missing_required_claims": [],
        "missing_required_predicates": [],
        "overbroad_requested_claims": [],
        "additional_proposed_claims": [],
        "not_approved_claims": [],
        "findings": [],
        "full_credential_claim_count": len(claims),
        "full_credential_exposure_units": full_units,
        "proposed_claim_count": 0,
        "proposed_exposure_units": 0,
        "exposure_reduction_percent": 0.0,
        "high_sensitivity_claims_proposed": [],
    }


def evaluate_disclosure_request(
    scenario: Dict[str, Any],
    *,
    purpose: Optional[str] = None,
    requested_claims: Optional[Sequence[str]] = None,
    approved_claims: Optional[Sequence[str]] = None,
    requested_predicates: Optional[Sequence[str]] = None,
    approved_predicates: Optional[Sequence[str]] = None,
    issuer_trust: Optional[str] = None,
    credential_status: Optional[str] = None,
    secondary_use: Optional[str] = None,
    retention_days: Any = ...,
) -> Dict[str, Any]:
    """Evaluate a synthetic verifier request and holder-approved disclosure.

    The engine treats verifier purpose policies as research assumptions. It
    returns a presentation proposal, not a cryptographically verified result.
    A retention_days value of None means the verifier did not specify a period.
    """
    if not isinstance(scenario, dict) or not isinstance(scenario.get("credential"), dict):
        raise TypeError("scenario must contain a credential object")
    credential = scenario["credential"]
    claims = credential.get("claims")
    if not isinstance(claims, dict):
        raise TypeError("credential.claims must be a dictionary")

    purpose = purpose if purpose is not None else scenario.get("purpose", "unknown")
    requested = _unique(requested_claims if requested_claims is not None else scenario.get("requested_claims", []))
    approved = _unique(approved_claims if approved_claims is not None else scenario.get("approved_claims", []))
    req_predicates = _unique(
        requested_predicates if requested_predicates is not None else scenario.get("requested_predicates", [])
    )
    ok_predicates = _unique(
        approved_predicates if approved_predicates is not None else scenario.get("approved_predicates", [])
    )
    issuer_trust = issuer_trust if issuer_trust is not None else credential.get("issuer_trust", "unknown")
    credential_status = credential_status if credential_status is not None else credential.get("credential_status", "unknown")
    secondary_use = secondary_use if secondary_use is not None else scenario.get("secondary_use", "")
    retention_days = scenario.get("retention_days") if retention_days is ... else retention_days

    _validate_names(list(claims.keys()), set(CLAIM_CATALOG), "credential claim fields")
    _validate_names(requested, set(CLAIM_CATALOG), "requested claims")
    _validate_names(approved, set(CLAIM_CATALOG), "holder-approved claims")
    _validate_names(req_predicates, set(PREDICATES), "requested predicates")
    _validate_names(ok_predicates, set(PREDICATES), "holder-approved predicates")

    result = _base_result(scenario, credential)
    findings: List[Dict[str, str]] = []
    result["purpose"] = purpose
    result["issuer_trust"] = issuer_trust
    result["credential_status"] = credential_status
    result["requested_claims"] = requested
    result["approved_claims"] = approved
    result["requested_predicates"] = req_predicates
    result["approved_predicates"] = ok_predicates

    policy = PURPOSE_POLICIES.get(purpose)
    if policy is None:
        findings.append(_finding(
            "purpose_not_supported", "Purpose is not covered by a disclosure policy", "critical",
            "Purpose limitation", purpose,
            "The lab has no reviewed minimum-claim policy for this stated purpose.",
            "Define and approve a purpose-specific policy before requesting academic data.",
        ))
        result["disposition"] = "purpose_not_supported"
        result["message"] = "No claims are proposed because the purpose has no reviewed disclosure policy."
        result["findings"] = findings
        result["privacy_review_required"] = True
        return result

    required = list(policy["required_claims"])
    allowed = set(policy["allowed_claims"])
    required_pred = list(policy["required_predicates"])
    allowed_pred = set(policy["allowed_predicates"])
    result["minimum_required_claims"] = required
    result["required_predicates"] = required_pred

    if issuer_trust != "trusted":
        findings.append(_finding(
            "issuer_trust_not_established", "Issuer trust is not established", "critical",
            "Issuer provenance", issuer_trust,
            "Selective disclosure cannot compensate for an issuer that has not been independently trusted.",
            "Establish issuer trust through an approved trust framework before relying on the credential.",
        ))
        result["disposition"] = "issuer_trust_not_established"
        result["message"] = "No presentation is recommended until issuer trust is established."
        result["findings"] = findings
        result["privacy_review_required"] = True
        return result

    if credential_status != "active":
        findings.append(_finding(
            "credential_status_not_active", "Credential status is not confirmed active", "critical",
            "Credential status", credential_status,
            "The synthetic status assertion is revoked, expired, or unknown rather than active.",
            "Check status through an issuer-approved, privacy-aware status mechanism.",
        ))
        result["disposition"] = "credential_status_not_active"
        result["message"] = "No presentation is recommended until current credential status is established."
        result["findings"] = findings
        result["privacy_review_required"] = True
        return result

    secondary = (secondary_use or "").strip()
    if secondary and secondary.lower() not in {"none", purpose.lower(), policy["label"].lower()}:
        findings.append(_finding(
            "secondary_use_mismatch", "Secondary use is outside the declared purpose", "critical",
            "Purpose limitation", secondary,
            "The stated use goes beyond the purpose for which the minimum-disclosure policy was defined.",
            "Remove the secondary use or obtain a separate, transparent and justified request with fresh holder choice.",
        ))

    requested_set = set(requested)
    approved_set = set(approved)
    proposed_keys = requested_set & approved_set & set(claims)
    proposed = {key: claims[key] for key in requested if key in proposed_keys}
    not_approved = sorted(requested_set - approved_set)
    overbroad = sorted(requested_set - allowed)
    additional = sorted(set(proposed) - set(required))
    missing_requested = sorted(set(required) - requested_set)
    missing_approved = sorted(set(required) - set(proposed))

    result["proposed_claims"] = proposed
    result["not_approved_claims"] = not_approved
    result["overbroad_requested_claims"] = overbroad
    result["additional_proposed_claims"] = additional
    result["missing_required_claims"] = missing_approved
    result["minimum_presentation"] = {key: claims[key] for key in required if key in proposed}

    if overbroad:
        labels = [CLAIM_CATALOG[key]["label"] for key in overbroad]
        findings.append(_finding(
            "request_exceeds_purpose", "Verifier request exceeds the purpose policy", "warning",
            "Data minimisation", ", ".join(labels),
            "The verifier requested claims outside the lab's purpose-specific allowed-claim set.",
            "Ask the verifier to remove unnecessary fields or justify them under a separately reviewed purpose.",
        ))

    if missing_requested:
        findings.append(_finding(
            "required_claim_not_requested", "Verifier request omits required evidence", "warning",
            "Evidence sufficiency", ", ".join(missing_requested),
            "The request does not ask for every minimum claim defined by the selected purpose policy.",
            "Request only the missing minimum claim, explaining why it is needed.",
        ))

    if missing_approved:
        findings.append(_finding(
            "holder_consent_incomplete", "Holder has not approved every required claim", "warning",
            "Holder agency", ", ".join(missing_approved),
            "A required claim was not both requested and approved by the holder.",
            "Do not disclose withheld claims; explain the consequence and allow the holder to decline.",
        ))

    if not_approved:
        findings.append(_finding(
            "claims_not_approved", "Some requested claims were not approved", "info",
            "Holder agency", ", ".join(not_approved),
            "Requested attributes outside the holder-approved set are omitted from the proposed presentation.",
            "Respect the holder's selection and assess whether the remaining evidence is sufficient.",
        ))

    if additional:
        findings.append(_finding(
            "additional_claims_proposed", "Presentation includes claims beyond the minimum", "warning",
            "Data minimisation", ", ".join(CLAIM_CATALOG[key]["label"] for key in additional),
            "These claims are not required by the selected purpose policy, even if they are within its optional allowed set.",
            "Prefer the minimum presentation unless the holder has a clear reason to share additional claims.",
        ))

    if "global_student_id" in requested_set:
        disclosed_global = "global_student_id" in proposed
        findings.append(_finding(
            "persistent_identifier_shared" if disclosed_global else "persistent_identifier_requested",
            "Persistent student identifier is included" if disclosed_global else "Persistent student identifier was requested but withheld",
            "critical" if disclosed_global else "warning",
            "Cross-context linkability",
            "disclosed" if disclosed_global else "requested_not_approved",
            "A stable global identifier can let different verifiers correlate presentations of the same person.",
            "Use a verifier-scoped identifier or another holder-binding approach instead of a global student identifier.",
        ))

    history = scenario.get("presentation_history", [])
    if not isinstance(history, list):
        raise TypeError("presentation_history must be a list")
    if "global_student_id" in proposed:
        other_verifiers = sorted({
            item.get("verifier_id", "unknown")
            for item in history
            if isinstance(item, dict)
            and item.get("identifier_mode") == "global_student_id"
            and item.get("verifier_id") != scenario.get("verifier_id")
        })
        if other_verifiers:
            findings.append(_finding(
                "cross_verifier_linkability", "Global identifier links presentations across verifiers", "critical",
                "Cross-context linkability", ", ".join(other_verifiers),
                "The scenario history shows the same persistent identifier was previously used with another verifier.",
                "Avoid global identifiers in presentations and evaluate pairwise or unlinkable holder-binding designs.",
            ))

    quasi_disclosed = sorted(set(proposed) & QUASI_IDENTIFIER_GROUP)
    if len(quasi_disclosed) >= 4:
        findings.append(_finding(
            "quasi_identifier_combination", "Combination of academic attributes may aid re-identification", "warning",
            "Inference and re-identification risk", ", ".join(CLAIM_CATALOG[key]["label"] for key in quasi_disclosed),
            "Several attributes that look ordinary individually may become identifying in combination with external information.",
            "Remove exact dates or campus-level detail unless necessary; assess combinations rather than isolated fields.",
        ))

    high_sensitivity = sorted(
        key for key in proposed
        if CLAIM_CATALOG[key]["sensitivity"] == "high"
    )
    if high_sensitivity:
        findings.append(_finding(
            "high_sensitivity_claims_proposed", "High-sensitivity claims are in the presentation proposal", "warning",
            "Sensitive data exposure", ", ".join(CLAIM_CATALOG[key]["label"] for key in high_sensitivity),
            "The holder-approved proposal includes sensitive personal or detailed academic information.",
            "Replace raw values with narrower claims or an issuer-backed predicate where appropriate.",
        ))

    if retention_days is None:
        findings.append(_finding(
            "retention_not_specified", "Verifier retention period is not specified", "warning",
            "Retention limitation", "not_specified",
            "The request does not say how long the disclosed information will be retained.",
            "Require a clear retention period and deletion process before presentation.",
        ))
    elif not isinstance(retention_days, int) or retention_days < 0:
        raise ValueError("retention_days must be a non-negative integer or None")

    predicate_results: List[Dict[str, Any]] = []
    for predicate_id in req_predicates:
        if predicate_id not in allowed_pred:
            findings.append(_finding(
                "predicate_exceeds_purpose", "Requested predicate is outside the purpose policy", "warning",
                "Purpose limitation", PREDICATES[predicate_id]["label"],
                "The requested threshold is not allowed by the selected purpose policy.",
                "Use a policy-approved predicate or define a separately reviewed purpose.",
            ))
            continue
        if predicate_id not in ok_predicates:
            predicate_results.append({
                "id": predicate_id,
                "label": PREDICATES[predicate_id]["label"],
                "approved": False,
                "satisfied": None,
            })
            continue
        definition = PREDICATES[predicate_id]
        raw_value = claims.get(definition["claim"])
        try:
            satisfied = float(raw_value) >= float(definition["threshold"])
        except (TypeError, ValueError):
            satisfied = None
        predicate_results.append({
            "id": predicate_id,
            "label": definition["label"],
            "approved": True,
            "satisfied": satisfied,
        })

    missing_predicates = sorted(set(required_pred) - set(req_predicates))
    unapproved_predicates = sorted(set(required_pred) - set(ok_predicates))
    failed_predicates = sorted(
        item["id"] for item in predicate_results if item.get("satisfied") is False
    )
    unknown_predicates = sorted(
        item["id"] for item in predicate_results if item.get("satisfied") is None and item.get("approved")
    )
    result["predicate_results"] = predicate_results
    result["missing_required_predicates"] = sorted(set(missing_predicates + unapproved_predicates))

    if missing_predicates or unapproved_predicates:
        findings.append(_finding(
            "required_predicate_not_approved", "Required threshold proof is missing or not approved", "warning",
            "Holder agency and eligibility", ", ".join(sorted(set(missing_predicates + unapproved_predicates))),
            "The purpose policy requires a predicate result, but it was not both requested and approved.",
            "Explain the threshold request and ask for the holder's explicit choice; do not reveal the raw score.",
        ))

    if failed_predicates:
        findings.append(_finding(
            "eligibility_predicate_not_satisfied", "A requested eligibility threshold is not satisfied", "critical",
            "Eligibility predicate", ", ".join(PREDICATES[key]["label"] for key in failed_predicates),
            "The synthetic hidden value does not meet the requested threshold.",
            "Report only the predicate outcome; do not expose the underlying score unless separately justified.",
        ))

    if unknown_predicates:
        findings.append(_finding(
            "eligibility_predicate_unknown", "Eligibility predicate could not be evaluated", "warning",
            "Eligibility predicate", ", ".join(unknown_predicates),
            "The hidden fixture value is absent or malformed, so no predicate result can be derived.",
            "Obtain a suitable issuer-backed claim or return an inconclusive result.",
        ))

    missing_evidence = bool(missing_approved or missing_predicates or unapproved_predicates or failed_predicates or unknown_predicates)
    secondary_mismatch = any(item["code"] == "secondary_use_mismatch" for item in findings)

    can_verify = not missing_evidence and not secondary_mismatch
    privacy_review = any(item["severity"] in {"warning", "critical"} for item in findings)
    if secondary_mismatch:
        disposition = "secondary_use_requires_review"
        message = "The verification purpose may be supportable, but the stated secondary use requires separate review."
    elif missing_evidence:
        disposition = "insufficient_evidence_or_consent"
        message = "The minimum evidence is incomplete, a required predicate was withheld, or the synthetic threshold was not met."
    elif overbroad or additional or high_sensitivity or "global_student_id" in proposed or len(quasi_disclosed) >= 4:
        disposition = "sufficient_evidence_with_privacy_warnings"
        message = "The minimum evidence is present, but the requested or proposed presentation contains avoidable privacy risks."
    else:
        disposition = "minimum_disclosure_sufficient"
        message = "The holder-approved presentation meets the synthetic purpose policy with no avoidable extra claims."

    proposed_units = sum(CLAIM_CATALOG[key]["weight"] for key in proposed)
    full_units = result["full_credential_exposure_units"]
    reduction = (100.0 * (full_units - proposed_units) / full_units) if full_units else 0.0

    result.update({
        "disposition": disposition,
        "message": message,
        "can_verify_purpose": can_verify,
        "presentation_ready": can_verify and not privacy_review,
        "privacy_review_required": privacy_review,
        "proposed_claim_count": len(proposed),
        "proposed_exposure_units": proposed_units,
        "exposure_reduction_percent": round(reduction, 1),
        "high_sensitivity_claims_proposed": high_sensitivity,
        "findings": findings,
    })
    return result


def disclosure_matrix(result: Dict[str, Any]) -> List[Dict[str, str]]:
    """Return a UI-friendly status row for every catalog claim."""
    requested = set(result.get("requested_claims", []))
    approved = set(result.get("approved_claims", []))
    proposed = set(result.get("proposed_claims", {}))
    required = set(result.get("minimum_required_claims", []))
    rows = []
    for key, meta in CLAIM_CATALOG.items():
        rows.append({
            "Claim": meta["label"],
            "Sensitivity": meta["sensitivity"].title(),
            "Minimum": "Required" if key in required else "No",
            "Requested": "Yes" if key in requested else "No",
            "Holder approved": "Yes" if key in approved else "No",
            "Proposed": "Yes" if key in proposed else "No",
        })
    return rows
