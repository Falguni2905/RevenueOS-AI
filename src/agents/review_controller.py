from src.agents.human_review import (
    create_review_request
)

from src.agents.action_policy import (
    determine_action
)

from src.agents.case_manager import (
    get_all_cases,
    complete_case_review
)

from src.agents.audit_logger import (
    log_human_review
)


VALID_REVIEW_DECISIONS = {
    "APPROVE",
    "REJECT",
    "HOLD"
}


# ==========================================================
# EVALUATE WHETHER HUMAN REVIEW IS REQUIRED
# ==========================================================

def evaluate_for_review(
    merchant_id,
    risk_score,
    confidence_score,
    risk_category,
    reason
):
    """
    Determine whether human review is required.

    This function creates the review request.
    Persistence and case linking are handled by
    the orchestrator after the case is created.
    """

    action = determine_action(
        risk_score,
        confidence_score
    )

    result = {

        "merchant_id":
            merchant_id,

        "risk_score":
            risk_score,

        "risk_category":
            risk_category,

        "recommended_action":
            action["action"],

        "human_approval_required":
            action["human_approval_required"],

        "reason":
            reason,

        "confidence":
            confidence_score,

        "review_status":
            "NOT_REQUIRED",

        "review_request":
            None
    }

    if action[
        "human_approval_required"
    ]:

        review = create_review_request(

            merchant_id=
                merchant_id,

            risk_score=
                risk_score,

            risk_category=
                risk_category,

            decision=
                action["action"],

            reason=
                reason,

            confidence=
                confidence_score
        )

        result[
            "review_request"
        ] = review

        result[
            "review_status"
        ] = "PENDING"

    return result


# ==========================================================
# FIND CASE BY REVIEW ID
# ==========================================================

def find_case_by_review_id(
    review_id
):
    """
    Find the persistent case associated
    with a review request.
    """

    cases = get_all_cases()

    for case in cases:

        if case.get(
            "review_id"
        ) == review_id:

            return case

    return None


# ==========================================================
# PROCESS HUMAN REVIEW DECISION
# ==========================================================

def process_review_decision(
    merchant_id,
    review_id,
    review_decision,
    reviewer=None,
    comments=None
):
    """
    Process a human review decision.

    The review must exist in the persistent
    case store before it can be processed.
    """

    review_decision = str(
        review_decision
    ).upper().strip()

    if review_decision not in (
        VALID_REVIEW_DECISIONS
    ):

        raise ValueError(
            "Invalid review decision. "
            "Use APPROVE, REJECT, or HOLD."
        )

    # ------------------------------------------------------
    # FIND PERSISTENT CASE
    # ------------------------------------------------------

    case = find_case_by_review_id(
        review_id
    )

    if case is None:

        raise ValueError(
            f"Review ID {review_id} "
            "does not exist."
        )

    # ------------------------------------------------------
    # VERIFY MERCHANT
    # ------------------------------------------------------

    if case.get(
        "merchant_id"
    ) != merchant_id:

        raise ValueError(
            "Review ID does not belong "
            "to the specified merchant."
        )

    # ------------------------------------------------------
    # CHECK REVIEW STATUS
    # ------------------------------------------------------

    current_status = case.get(
        "review_status"
    )

    if current_status not in [
        "PENDING",
        "NOT_REQUIRED"
    ]:

        raise ValueError(
            f"Review has already been processed. "
            f"Current status: {current_status}"
        )

    # ------------------------------------------------------
    # UPDATE PERSISTENT CASE
    # ------------------------------------------------------

    updated_case = complete_case_review(

        case_id=
            case["case_id"],

        review_decision=
            review_decision,

        reviewer=
            reviewer,

        comments=
            comments
    )

    if updated_case is None:

        raise ValueError(
            "Unable to update the persistent case."
        )

    # ------------------------------------------------------
    # AUDIT
    # ------------------------------------------------------
    #
    # Store the case ID and review ID so the final
    # human-review event can be traced back to the
    # exact investigation case.
    # ------------------------------------------------------

    log_human_review(

        merchant_id=
            merchant_id,

        decision=
            review_decision,

        reviewer=
            reviewer,

        comments=
            comments,

        case_id=
            updated_case["case_id"],

        review_id=
            review_id
    )

    # ------------------------------------------------------
    # RESPONSE
    # ------------------------------------------------------

    return {

        "review_id":
            review_id,

        "merchant_id":
            merchant_id,

        "case_id":
            updated_case["case_id"],

        "review_decision":
            review_decision,

        "reviewer":
            reviewer,

        "comments":
            comments,

        "status":
            updated_case["status"],

        "case_status":
            updated_case["status"],

        "review_status":
            updated_case["review_status"],

        "timestamp":
            updated_case["updated_at"]
    }


# ==========================================================
# APPROVE REVIEW
# ==========================================================

def approve_review(
    merchant_id,
    review_id,
    reviewer=None,
    comments=None
):

    return process_review_decision(

        merchant_id=
            merchant_id,

        review_id=
            review_id,

        review_decision=
            "APPROVE",

        reviewer=
            reviewer,

        comments=
            comments
    )


# ==========================================================
# REJECT REVIEW
# ==========================================================

def reject_review(
    merchant_id,
    review_id,
    reviewer=None,
    comments=None
):

    return process_review_decision(

        merchant_id=
            merchant_id,

        review_id=
            review_id,

        review_decision=
            "REJECT",

        reviewer=
            reviewer,

        comments=
            comments
    )


# ==========================================================
# HOLD REVIEW
# ==========================================================

def hold_review(
    merchant_id,
    review_id,
    reviewer=None,
    comments=None
):

    return process_review_decision(

        merchant_id=
            merchant_id,

        review_id=
            review_id,

        review_decision=
            "HOLD",

        reviewer=
            reviewer,

        comments=
            comments
    )


# ==========================================================
# STANDALONE TEST
# ==========================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("REVENUEOS-AI REVIEW CONTROLLER")
    print("=" * 70)

    print("\nController loaded successfully.")

    print(
        "\nReview decisions supported:"
    )

    print("  APPROVE")
    print("  REJECT")
    print("  HOLD")

    print(
        "\nPersistent case verification enabled."
    )

    print(
        "\nFinal human-review audit linkage enabled."
    )

    print("\n")
    print("=" * 70)
    print("REVIEW CONTROLLER READY")
    print("=" * 70)