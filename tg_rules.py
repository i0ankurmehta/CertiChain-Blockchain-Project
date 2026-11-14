"""Deterministic, scope-specific evidence adjudication for Trust Gatekeeper.

This module is a synthetic research prototype. It is not a legal decision engine
and does not authenticate individual academic awards without issuer evidence.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

RULESET_ID = "TG-RULES-001"
RULESET_VERSION = "0.1"

EV01 = "EV-01"
EV02 = "EV-02"
EV03 = "EV-03"
EV04 = "EV-04"
EV05 = "EV-05"
EV06 = "EV-06"
EV07 = "EV-07"

OUTCOME_LABELS = {
    EV01: "Evidence consistent",
    EV02: "Temporal mismatch",
    EV03: "Entity ambiguity",
    EV04: "Source conflict",
    EV05: "Evidence insufficient",
    EV06: "Document/record mismatch",
    EV07: "Intake blocked",
}

# Summary convention from TG-RULES-001 §5; this is not a candidate severity score.
OUTCOME_PRECEDENCE = [EV07, EV04, EV02, EV03, EV05, EV06, EV01]
TRUSTED_SOURCE_CLASSES = {"A", "B", "C"}


def _normalise(value: Any) -> str:
    """Normalise formatting for comparison without deleting semantic content."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    return " ".join(text.split()).casefold()


def _parse_date(value: Any) -> Optional[date]:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def _session_years(value: Any) -> Optional[Tuple[int, int]]:
    """Parse labels such as 2021-2022 or 2021–22 for interval comparison."""
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"\s*(\d{4})\s*[-–/]\s*(\d{2}|\d{4})\s*", value)
    if not match:
        return None
    start = int(match.group(1))
    end_text = match.group(2)
    end = int(end_text) if len(end_text) == 4 else (start // 100) * 100 + int(end_text)
    if end < start:
        end += 100
    if end - start > 2:
        return None
    return start, end


def _session_contains(evidence: Dict[str, Any], target: str) -> Optional[bool]:
    """Return True/False when session coverage is explicit; otherwise None."""
    if target in (evidence.get("excluded_sessions") or []):
        return False
    valid_sessions = evidence.get("valid_sessions")
    if isinstance(valid_sessions, list):
        return target in valid_sessions
    start = _session_years(evidence.get("valid_from_session"))
    end = _session_years(evidence.get("valid_to_session"))
    target_years = _session_years(target)
    if start and target_years:
        end_year = end[1] if end else start[1]
        return start[0] <= target_years[0] and target_years[1] <= end_year
    if evidence.get("period_scope_complete") is True and start and target_years:
        return False
    return None


def _date_contains(evidence: Dict[str, Any], target: str) -> Optional[bool]:
    target_date = _parse_date(target)
    valid_from = _parse_date(evidence.get("valid_from"))
    valid_to = _parse_date(evidence.get("valid_to"))
    if not target_date or not valid_from:
        return None
    if valid_to is None and evidence.get("open_ended") is not True:
        return None
    return valid_from <= target_date and (valid_to is None or target_date <= valid_to)


def _period_contains(evidence: Dict[str, Any], claim: Dict[str, Any]) -> Optional[bool]:
    session = claim.get("relevant_session")
    if session:
        return _session_contains(evidence, str(session))
    relevant_date = claim.get("relevant_date")
    if relevant_date:
        return _date_contains(evidence, str(relevant_date))
    return None


def _periods_overlap(left: Dict[str, Any], right: Dict[str, Any]) -> Optional[bool]:
    left_sessions = left.get("valid_sessions")
    right_sessions = right.get("valid_sessions")
    if isinstance(left_sessions, list) and isinstance(right_sessions, list):
        return bool(set(left_sessions).intersection(right_sessions))
    left_start = _parse_date(left.get("valid_from"))
    left_end = _parse_date(left.get("valid_to"))
    right_start = _parse_date(right.get("valid_from"))
    right_end = _parse_date(right.get("valid_to"))
    if left_start and right_start and left_end and right_end:
        return max(left_start, right_start) <= min(left_end, right_end)
    return None


def _matches_claim(evidence: Dict[str, Any], claim: Dict[str, Any]) -> bool:
    return (
        evidence.get("subject_id") == claim.get("subject_id")
        and evidence.get("predicate") == claim.get("predicate")
        and evidence.get("claim_scope", evidence.get("scope")) == claim.get("scope")
    )


def _is_qualified(evidence: Dict[str, Any], claim: Dict[str, Any]) -> bool:
    allowed = set(claim.get("required_source_classes") or TRUSTED_SOURCE_CLASSES)
    return (
        evidence.get("source_class") in allowed
        and evidence.get("review_state", "unreviewed") == "reviewed"
        and evidence.get("source_scope_match", True) is True
    )


def _root_source(source_id: str, parent_by_source: Dict[str, Optional[str]]) -> str:
    seen = set()
    current = source_id
    while parent_by_source.get(current):
        if current in seen:
            return "DEPENDENCY_CYCLE:" + min(seen)
        seen.add(current)
        current = str(parent_by_source[current])
    return current


def _dependency_groups(evidence: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    parent_by_source: Dict[str, Optional[str]] = {}
    for item in evidence:
        source_id = item.get("source_id")
        if source_id:
            parent_by_source[str(source_id)] = item.get("parent_source_id")

    grouped: Dict[str, Dict[str, Any]] = {}
    for item in evidence:
        source_id = item.get("source_id")
        if not source_id:
            continue
        root = _root_source(str(source_id), parent_by_source)
        group = grouped.setdefault(
            root, {"root_source_id": root, "source_ids": set(), "evidence_ids": set()}
        )
        group["source_ids"].add(str(source_id))
        if item.get("evidence_id"):
            group["evidence_ids"].add(str(item["evidence_id"]))

    result = []
    for root, group in grouped.items():
        if len(group["source_ids"]) > 1 or str(root).startswith("DEPENDENCY_CYCLE:"):
            result.append({
                "root_source_id": root,
                "source_ids": sorted(group["source_ids"]),
                "evidence_ids": sorted(group["evidence_ids"]),
                "relationship": "shared_source_lineage",
            })
    return sorted(result, key=lambda item: item["root_source_id"])


def _conflict_pairs(
    evidence: Sequence[Dict[str, Any]], claim: Dict[str, Any]
) -> List[Tuple[str, str]]:
    relevant = [
        item for item in evidence
        if _matches_claim(item, claim) and _is_qualified(item, claim)
    ]
    pairs: List[Tuple[str, str]] = []
    for index, left in enumerate(relevant):
        for right in relevant[index + 1:]:
            if _normalise(left.get("value")) == _normalise(right.get("value")):
                continue
            if _periods_overlap(left, right) is True:
                pairs.append((
                    str(left.get("evidence_id", "")),
                    str(right.get("evidence_id", "")),
                ))
    return pairs


def _assess_claim(
    claim: Dict[str, Any], evidence: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    matching = [item for item in evidence if _matches_claim(item, claim)]
    qualified = [item for item in matching if _is_qualified(item, claim)]
    conflict_pairs = _conflict_pairs(evidence, claim)
    if conflict_pairs:
        return {
            "claim_id": claim.get("claim_id"),
            "scope": claim.get("scope"),
            "outcome": EV04,
            "label": OUTCOME_LABELS[EV04],
            "evidence_ids": sorted({
                item for pair in conflict_pairs for item in pair if item
            }),
            "explanation": (
                "Comparable, reviewed sources make incompatible claims "
                "for overlapping periods."
            ),
            "conflict_pairs": [list(pair) for pair in conflict_pairs],
        }

    relevant_session = claim.get("relevant_session")
    relevant_date = claim.get("relevant_date")
    supporting = []
    temporal_exclusions = []
    for item in qualified:
        coverage = _period_contains(item, claim)
        explicit_excluded = bool(
            relevant_session
            and relevant_session in (item.get("excluded_sessions") or [])
        )
        scope_complete_exclusion = (
            coverage is False and item.get("period_scope_complete") is True
        )
        if explicit_excluded or scope_complete_exclusion:
            temporal_exclusions.append(item)
            continue
        if _normalise(item.get("value")) != _normalise(claim.get("expected_value")):
            continue
        if coverage is True:
            supporting.append(item)
        elif coverage is False and item.get("period_scope_complete") is True:
            temporal_exclusions.append(item)

    if temporal_exclusions:
        ids = sorted({
            str(item.get("evidence_id", ""))
            for item in temporal_exclusions if item.get("evidence_id")
        })
        return {
            "claim_id": claim.get("claim_id"),
            "scope": claim.get("scope"),
            "outcome": EV02,
            "label": OUTCOME_LABELS[EV02],
            "evidence_ids": ids,
            "explanation": (
                "Reviewed, claim-appropriate evidence explicitly excludes the "
                "relevant date/session or defines a complete period that does not cover it."
            ),
            "conflict_pairs": [],
        }

    explicit_contradictions = [
        item for item in qualified
        if _period_contains(item, claim) is True
        and _normalise(item.get("value")) != _normalise(claim.get("expected_value"))
        and item.get("explicitly_excludes_claim") is True
    ]
    if explicit_contradictions:
        ids = sorted({
            str(item.get("evidence_id", ""))
            for item in explicit_contradictions if item.get("evidence_id")
        })
        return {
            "claim_id": claim.get("claim_id"),
            "scope": claim.get("scope"),
            "outcome": EV02,
            "label": OUTCOME_LABELS[EV02],
            "evidence_ids": ids,
            "explanation": (
                "Reviewed, claim-appropriate evidence explicitly states a different status "
                "for the relevant date/session."
            ),
            "conflict_pairs": [],
        }

    if supporting:
        return {
            "claim_id": claim.get("claim_id"),
            "scope": claim.get("scope"),
            "outcome": EV01,
            "label": OUTCOME_LABELS[EV01],
            "evidence_ids": sorted({
                str(item.get("evidence_id", ""))
                for item in supporting if item.get("evidence_id")
            }),
            "explanation": (
                "Reviewed, claim-appropriate evidence supports the expected claim "
                "for the relevant period."
            ),
            "conflict_pairs": [],
        }

    reason = (
        "No reviewed source with the required claim scope and source class "
        "establishes the expected claim for the relevant period."
    )
    if matching and not qualified:
        reason = (
            "Matching source records exist, but none meets the required source-class, "
            "review-state and claim-scope conditions."
        )
    elif qualified and not (relevant_session or relevant_date):
        reason = (
            "The required claim has no relevant date or academic session, "
            "so temporal coverage cannot be assessed."
        )
    elif qualified:
        reason = (
            "Sources exist, but their effective periods do not establish coverage "
            "of the relevant date/session; absence of coverage is not treated as contradiction."
        )
    return {
        "claim_id": claim.get("claim_id"),
        "scope": claim.get("scope"),
        "outcome": EV05,
        "label": OUTCOME_LABELS[EV05],
        "evidence_ids": sorted({
            str(item.get("evidence_id", ""))
            for item in matching if item.get("evidence_id")
        }),
        "explanation": reason,
        "conflict_pairs": [],
    }


def _field_findings(
    comparisons: Iterable[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    findings = []
    for item in comparisons or []:
        if item.get("material", True) is False:
            continue
        confidence = item.get("ocr_confidence")
        threshold = item.get("confidence_threshold", 0.8)
        if confidence is not None:
            try:
                low_confidence = float(confidence) < float(threshold)
            except (TypeError, ValueError):
                low_confidence = True
            if low_confidence:
                findings.append({
                    "code": "OCR_LOW_CONFIDENCE",
                    "field": item.get("field"),
                    "submitted_value": item.get("submitted_value"),
                    "extracted_value": item.get("extracted_value"),
                    "explanation": (
                        "OCR confidence is below the configured field threshold; "
                        "human review is required before comparison."
                    ),
                })
                continue
        if _normalise(item.get("submitted_value")) != _normalise(item.get("extracted_value")):
            findings.append({
                "code": EV06,
                "field": item.get("field"),
                "submitted_value": item.get("submitted_value"),
                "extracted_value": item.get("extracted_value"),
                "explanation": "Material values differ after safe formatting normalisation.",
            })
    return findings


def assess_case(case: Dict[str, Any]) -> Dict[str, Any]:
    """Assess a case and return deterministic, auditable scope-specific findings."""
    if not isinstance(case, dict):
        raise TypeError("case must be a dictionary")

    case_id = str(case.get("case_id") or "UNASSIGNED")
    if (
        case.get("processing_authority_documented") is not True
        or case.get("input_safe") is not True
    ):
        return {
            "case_id": case_id,
            "ruleset_id": RULESET_ID,
            "ruleset_version": RULESET_VERSION,
            "case_state": "BLOCKED",
            "primary_outcome": EV07,
            "primary_label": OUTCOME_LABELS[EV07],
            "secondary_findings": [],
            "scope_results": [],
            "field_findings": [],
            "dependency_groups": [],
            "evidence_ids": [],
            "unresolved_questions": [
                "Confirm documented processing authority and/or resolve the input safety failure before processing."
            ],
            "recommended_actions": [
                "Return the case to the customer; do not process the submitted data."
            ],
            "explanation": "The intake gate failed. No substantive evidence assessment was performed.",
            "review_required": True,
        }

    evidence = case.get("evidence") or []
    claims = case.get("required_claims") or []
    if not isinstance(evidence, list) or not isinstance(claims, list):
        raise ValueError("evidence and required_claims must be lists")

    field_findings = _field_findings(case.get("field_comparisons") or [])
    scope_results = [_assess_claim(item, evidence) for item in claims]
    outcomes = {result["outcome"] for result in scope_results}

    entity_status = case.get("entity_resolution_status", "unknown")
    if entity_status in {"ambiguous", "unresolved"}:
        outcomes.add(EV03)
    elif entity_status not in {"resolved", "not_required"}:
        outcomes.add(EV05)

    if any(item["code"] == EV06 for item in field_findings):
        outcomes.add(EV06)
    if any(item["code"] == "OCR_LOW_CONFIDENCE" for item in field_findings):
        outcomes.add(EV05)
    if not outcomes:
        outcomes.add(EV05)

    primary = next(code for code in OUTCOME_PRECEDENCE if code in outcomes)
    secondary = [
        code for code in OUTCOME_PRECEDENCE
        if code in outcomes and code != primary
    ]
    dependency_groups = _dependency_groups(evidence)

    unresolved = []
    actions = []
    for result in scope_results:
        if result["outcome"] != EV01:
            unresolved.append(f"{result['scope']}: {result['explanation']}")
            if result["outcome"] == EV02:
                actions.append(
                    "Obtain the governing historical approval/recognition order for the claimed session."
                )
            elif result["outcome"] == EV03:
                actions.append(
                    "Obtain authoritative identity, affiliation or cohort-transition evidence."
                )
            elif result["outcome"] == EV04:
                actions.append(
                    "Escalate the incompatible source assertions to a senior reviewer or issuing authority."
                )
            else:
                actions.append(
                    "Request the missing claim-appropriate evidence from the issuing institution or relevant authority."
                )

    if entity_status in {"ambiguous", "unresolved"}:
        unresolved.append("A material institution/programme/awarding relationship is not resolved.")
        actions.append("Obtain authoritative entity-identity or relationship evidence.")

    for item in field_findings:
        if item["code"] == EV06:
            unresolved.append(f"Document/record mismatch for {item['field']}.")
            actions.append(
                "Review the original document and structured case record; retain both values."
            )
        elif item["code"] == "OCR_LOW_CONFIDENCE":
            unresolved.append(
                f"OCR result for {item['field']} is below the configured confidence threshold."
            )
            actions.append(
                "Have an analyst inspect the original scan before relying on this field."
            )

    if EV05 in outcomes and not claims:
        unresolved.append("No required claims were supplied for assessment.")
        actions.append("Define the claim scopes and relevant dates/sessions before assessment.")
    if EV01 in outcomes and not unresolved:
        actions.append(
            "Record the scoped evidence assessment; individual award verification remains separate unless an award-specific claim was assessed."
        )

    actions = list(dict.fromkeys(actions))
    unresolved = list(dict.fromkeys(unresolved))
    review_required = any(code != EV01 for code in outcomes)
    return {
        "case_id": case_id,
        "ruleset_id": RULESET_ID,
        "ruleset_version": RULESET_VERSION,
        "case_state": "REVIEW_REQUIRED" if review_required else "ASSESSED",
        "primary_outcome": primary,
        "primary_label": OUTCOME_LABELS[primary],
        "secondary_findings": secondary,
        "scope_results": scope_results,
        "field_findings": field_findings,
        "dependency_groups": dependency_groups,
        "evidence_ids": sorted({
            str(item.get("evidence_id"))
            for item in evidence if item.get("evidence_id")
        }),
        "unresolved_questions": unresolved,
        "recommended_actions": actions,
        "explanation": (
            f"{OUTCOME_LABELS[primary]} is the primary summary for the contextual "
            "and claim-specific checks performed. See scope results and limitations "
            "for the exact claims assessed."
        ),
        "review_required": review_required,
    }
