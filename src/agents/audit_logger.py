import json
import os
from datetime import datetime

AUDIT_FILE = "data/processed/agent_audit_log.jsonl"


def _ensure_audit_directory():
    directory = os.path.dirname(AUDIT_FILE)

    if directory:
        os.makedirs(directory, exist_ok=True)


def _serialize_details(value):
    """
    Convert audit details into JSON-safe Python structures.

    Handles:
    - dictionaries
    - lists / tuples
    - primitive values
    - custom Python objects such as InvestigationState
    """

    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {
            str(key): _serialize_details(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _serialize_details(item)
            for item in value
        ]

    # Handle custom objects such as InvestigationState
    if hasattr(value, "__dict__"):
        return {
            str(key): _serialize_details(item)
            for key, item in vars(value).items()
            if not str(key).startswith("_")
        }

    # Final fallback
    return str(value)


def log_event(
    event_type,
    merchant_id,
    details,
    case_id=None,
    review_id=None
):
    """
    Create and persist one audit event.
    """

    _ensure_audit_directory()

    # Convert any custom objects into JSON-safe structures
    event_details = _serialize_details(details)

    # Ensure details are always stored as a dictionary
    if not isinstance(event_details, dict):
        event_details = {
            "value": event_details
        }

    # Try to extract identifiers from nested structures
    if case_id is None:
        case_id = event_details.get("case_id")

    if review_id is None:
        review_id = event_details.get("review_id")

    # Also check nested case/review structures
    if case_id is None:
        case_data = event_details.get("case")

        if isinstance(case_data, dict):
            case_id = case_data.get("case_id")

    if review_id is None:
        review_data = event_details.get("review")

        if isinstance(review_data, dict):
            review_id = review_data.get("review_id")

    # Attach identifiers when available
    if case_id is not None:
        event_details["case_id"] = str(case_id)

    if review_id is not None:
        event_details["review_id"] = str(review_id)

    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": str(event_type),
        "merchant_id": str(merchant_id),
        "details": event_details
    }

    with open(AUDIT_FILE, "a", encoding="utf-8") as file:
        file.write(
            json.dumps(event, default=str) + "\n"
        )

    return event


def log_risk_assessment(
    merchant_id,
    risk_score,
    risk_category,
    failure_rate,
    case_id=None,
    review_id=None
):
    details = {
        "risk_score": float(risk_score),
        "risk_category": str(risk_category),
        "failure_rate": float(failure_rate)
    }

    return log_event(
        "RISK_ASSESSMENT",
        merchant_id,
        details,
        case_id=case_id,
        review_id=review_id
    )


def log_decision(
    merchant_id,
    decision,
    reason,
    risk_score=None,
    risk_category=None,
    failure_rate=None,
    case_id=None,
    review_id=None
):
    details = {
        "decision": str(decision),
        "reason": str(reason)
    }

    if risk_score is not None:
        details["risk_score"] = float(risk_score)

    if risk_category is not None:
        details["risk_category"] = str(risk_category)

    if failure_rate is not None:
        details["failure_rate"] = float(failure_rate)

    return log_event(
        "DECISION",
        merchant_id,
        details,
        case_id=case_id,
        review_id=review_id
    )


def log_investigation(
    merchant_id,
    investigation,
    case_id=None,
    review_id=None
):
    return log_event(
        "INVESTIGATION",
        merchant_id,
        investigation,
        case_id=case_id,
        review_id=review_id
    )


def log_action(
    merchant_id,
    action,
    priority=None,
    status=None,
    human_approval_required=None,
    case_id=None,
    review_id=None
):
    details = {
        "action": str(action)
    }

    if priority is not None:
        details["priority"] = str(priority)

    if status is not None:
        details["status"] = str(status)

    if human_approval_required is not None:
        details["human_approval_required"] = bool(
            human_approval_required
        )

    return log_event(
        "ACTION",
        merchant_id,
        details,
        case_id=case_id,
        review_id=review_id
    )


def log_human_review(
    merchant_id,
    decision,
    reviewer=None,
    comments=None,
    case_id=None,
    review_id=None
):
    details = {
        "review_decision": str(decision)
    }

    if reviewer is not None:
        details["reviewer"] = str(reviewer)

    if comments is not None:
        details["comments"] = str(comments)

    return log_event(
        "HUMAN_REVIEW",
        merchant_id,
        details,
        case_id=case_id,
        review_id=review_id
    )


def log_complete_case(
    merchant_id,
    result,
    case_id=None,
    review_id=None
):
    return log_event(
        "CASE_COMPLETED",
        merchant_id,
        result,
        case_id=case_id,
        review_id=review_id
    )


def read_audit_log():
    """
    Read all audit events from the JSONL file.
    """

    if not os.path.exists(AUDIT_FILE):
        return []

    events = []

    with open(AUDIT_FILE, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return events


if __name__ == "__main__":
    print("=" * 70)
    print("REVENUEOS-AI AUDIT LOGGER")
    print("=" * 70)

    test_event = log_decision(
        merchant_id="M00008",
        decision="MONITOR",
        reason=(
            "Merchant has a 7.69% transaction failure rate. "
            "Risk is not critical, but elevated failure behaviour "
            "requires continuous monitoring."
        ),
        risk_score=30.12,
        risk_category="Medium",
        failure_rate=0.0769,
        case_id="CASE-M00008-TEST",
        review_id="REV-M00008-TEST"
    )

    print("\nAudit event created:")
    print(json.dumps(test_event, indent=4))

    print("\nCase ID:")
    print(test_event["details"].get("case_id"))

    print("\nReview ID:")
    print(test_event["details"].get("review_id"))

    print("\nAudit file:")
    print(AUDIT_FILE)

    print("\nTotal audit events:")
    print(len(read_audit_log()))

    print("\n")
    print("=" * 70)
    print("AUDIT LOGGER COMPLETE")
    print("=" * 70)