from datetime import datetime


VALID_DECISIONS = {
    "APPROVE": "APPROVED",
    "REJECT": "REJECTED",
    "HOLD": "ON_HOLD"
}


def create_review_request(
    merchant_id,
    risk_score,
    risk_category,
    decision,
    reason,
    confidence
):
    """
    Create a new human review request.
    """

    review_request = {
        "review_id":
            f"REV-{merchant_id}-{int(datetime.now().timestamp())}",

        "merchant_id":
            merchant_id,

        "risk_score":
            risk_score,

        "risk_category":
            risk_category,

        "decision":
            decision,

        "reason":
            reason,

        "confidence":
            confidence,

        "status":
            "PENDING",

        "reviewer":
            None,

        "reviewer_decision":
            None,

        "reviewer_reason":
            None,

        "created_at":
            datetime.now().isoformat(),

        "reviewed_at":
            None
    }

    return review_request


def review_request(
    review_request,
    reviewer,
    decision,
    reason
):
    """
    Complete a human review request.

    Accepted decisions:
        APPROVE
        REJECT
        HOLD
    """

    decision = str(
        decision
    ).upper().strip()

    if decision not in VALID_DECISIONS:

        raise ValueError(
            "Decision must be "
            "APPROVE, REJECT, or HOLD."
        )

    review_request["status"] = (
        VALID_DECISIONS[decision]
    )

    review_request["reviewer"] = (
        reviewer
    )

    review_request["reviewer_decision"] = (
        decision
    )

    review_request["reviewer_reason"] = (
        reason
    )

    review_request["reviewed_at"] = (
        datetime.now().isoformat()
    )

    return review_request


if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("REVENUEOS-AI HUMAN REVIEW")
    print("=" * 70)

    request = create_review_request(
        merchant_id="M00005",
        risk_score=100.00,
        risk_category="Critical",
        decision="HUMAN_REVIEW",
        reason="High-risk merchant requires human approval.",
        confidence=0.90
    )

    print("\nREVIEW REQUEST")
    print("-" * 70)

    print(
        f"Review ID: {request['review_id']}"
    )

    print(
        f"Status:    {request['status']}"
    )

    completed = review_request(
        review_request=request,
        reviewer="Demo Reviewer",
        decision="APPROVE",
        reason=(
            "Investigation evidence "
            "supports the recommended action."
        )
    )

    print("\nREVIEW COMPLETED")
    print("-" * 70)

    print(
        f"Decision:  "
        f"{completed['reviewer_decision']}"
    )

    print(
        f"Status:    "
        f"{completed['status']}"
    )

    print(
        f"Reviewer:  "
        f"{completed['reviewer']}"
    )

    print("\n")
    print("=" * 70)
    print("HUMAN REVIEW COMPLETE")
    print("=" * 70)