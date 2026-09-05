import pandas as pd

from src.agents.decision_agent import (
    decide_action
)

from src.agents.investigation_loop import (
    run_investigation
)

from src.agents.evidence_analyzer import (
    analyze_evidence
)

from src.agents.confidence_scorer import (
    calculate_confidence
)

from src.agents.review_controller import (
    evaluate_for_review
)

from src.agents.case_manager import (
    create_case,
    update_case,
    link_review_to_case
)

from src.agents.audit_logger import (
    log_event,
    log_risk_assessment,
    log_decision,
    log_investigation,
    log_action,
    log_human_review,
    log_complete_case
)


# ==========================================================
# CONFIGURATION
# ==========================================================

RISK_FILE = (
    "data/processed/merchant_risk_scores.csv"
)


# ==========================================================
# MAIN REVENUEOS PIPELINE
# ==========================================================

def run_revenueos(
    merchant_id
):

    print("\n")
    print("=" * 70)
    print("REVENUEOS-AI")
    print("AUTONOMOUS MERCHANT RISK INVESTIGATION")
    print("=" * 70)

    # ======================================================
    # 1. LOAD MERCHANT RISK
    # ======================================================

    df = pd.read_csv(
        RISK_FILE
    )

    merchant = df[
        df["merchant_id"] == merchant_id
    ]

    if merchant.empty:

        print(
            f"\nMerchant {merchant_id} not found."
        )

        return None

    merchant = merchant.iloc[0]

    risk_score = float(
        merchant["risk_score"]
    )

    risk_category = (
        merchant["risk_category"]
    )

    failure_rate = float(
        merchant["failure_rate"]
    )

    # Create the case before any audit events so every stage
    # of this pipeline can be linked to the same case.
    case = create_case(
        merchant_id=merchant_id,
        risk_score=risk_score,
        risk_category=risk_category,
        findings=[],
        recommended_action="PENDING",
        confidence=0
    )

    case_id = case["case_id"]

    # ======================================================
    # 2. RISK ASSESSMENT
    # ======================================================

    print("\n")
    print("RISK ASSESSMENT")
    print("-" * 70)

    print(
        f"Risk Score:       "
        f"{risk_score:.2f}"
    )

    print(
        f"Risk Category:    "
        f"{risk_category}"
    )

    print(
        f"Failure Rate:     "
        f"{failure_rate:.2%}"
    )

    log_risk_assessment(
        merchant_id=merchant_id,
        risk_score=risk_score,
        risk_category=risk_category,
        failure_rate=failure_rate,
        case_id=case_id
    )

    # ======================================================
    # 3. INITIAL DECISION
    # ======================================================

    decision_result = decide_action(
        merchant_id
    )

    if decision_result is None:

        log_event(
            "PIPELINE_ERROR",
            merchant_id,
            {
                "stage":
                    "DECISION",

                "error":
                    "Decision agent returned None."
            }
        )

        return None

    decision = decision_result[
        "decision"
    ]

    reason = decision_result[
        "reason"
    ]

    print("\n")
    print("DECISION")
    print("-" * 70)

    print(
        f"Decision:         "
        f"{decision}"
    )

    print(
        f"Reason:           "
        f"{reason}"
    )

    log_decision(
        merchant_id=merchant_id,
        decision=decision,
        reason=reason,
        risk_score=risk_score,
        risk_category=risk_category,
        failure_rate=failure_rate,
        case_id=case_id
    )

    # ======================================================
    # 4. LOW-RISK PATH
    # ======================================================

    if decision not in [
        "INVESTIGATE",
        "ESCALATE"
    ]:

        print("\n")
        print(
            "No automated investigation required."
        )

        case = update_case(
            case_id=case_id,
            updates={
                "recommended_action": decision,
                "confidence": 100,
                "status": "COMPLETED"
            }
        )

        log_complete_case(
            merchant_id,
            {
                "decision": decision,
                "risk_score": risk_score,
                "risk_category": risk_category,
                "failure_rate": failure_rate,
                "reason": reason,
                "status": "COMPLETED"
            },
            case_id=case_id
        )

        print("\n")
        print("AUDIT")
        print("-" * 70)

        print(
            "Risk assessment logged"
        )

        print(
            "Decision logged"
        )

        print(
            "Case completion logged"
        )

        return {

            "merchant_id":
                merchant_id,

            "decision":
                decision,

            "risk_score":
                risk_score,

            "risk_category":
                risk_category,

            "failure_rate":
                failure_rate,

            "reason":
                reason
        }

    # ======================================================
    # 6. INVESTIGATION
    # ======================================================

    print("\n")
    print("INVESTIGATION")
    print("-" * 70)

    state = run_investigation(
        merchant_id,
        risk_score,
        risk_category,
        failure_rate
    )

    log_investigation(
        merchant_id=merchant_id,
        investigation=state,
        case_id=case_id
    )

    # ======================================================
    # 6. EVIDENCE ANALYSIS
    # ======================================================

    findings = analyze_evidence(
        state
    )

    print(
        f"Evidence Findings: "
        f"{len(findings)}"
    )

    for finding in findings:

        print(
            f"  - {finding}"
        )

    # ======================================================
    # 7. CONFIDENCE
    # ======================================================

    confidence = calculate_confidence(
        state,
        findings
    )

    confidence_score = confidence[
        "score"
    ]

    confidence_category = confidence[
        "category"
    ]

    print("\n")
    print("CONFIDENCE")
    print("-" * 70)

    print(
        f"Score:            "
        f"{confidence_score}"
    )

    print(
        f"Category:         "
        f"{confidence_category}"
    )

    # ======================================================
    # 8. REVIEW CONTROLLER
    # ======================================================

    review_evaluation = evaluate_for_review(

        merchant_id=
            merchant_id,

        risk_score=
            risk_score,

        confidence_score=
            confidence_score,

        risk_category=
            risk_category,

        reason=
            reason
    )

    recommended_action = (
        review_evaluation[
            "recommended_action"
        ]
    )

    human_approval = (
        review_evaluation[
            "human_approval_required"
        ]
    )

    review = (
        review_evaluation[
            "review_request"
        ]
    )

    print("\n")
    print("RECOMMENDED ACTION")
    print("-" * 70)

    print(
        f"Action:           "
        f"{recommended_action}"
    )

    print(
        f"Human Approval:   "
        f"{'REQUIRED' if human_approval else 'NOT REQUIRED'}"
    )

    log_action(
        merchant_id=
            merchant_id,

        action=
            recommended_action,

        priority=None,

        status=(
            "PENDING_REVIEW"
            if human_approval
            else "READY"
        ),

        human_approval_required=
            human_approval,

        case_id=
            case_id
    )

    # ======================================================
    # 9. UPDATE CASE WITH INVESTIGATION RESULTS
    # ======================================================

    case = update_case(
        case_id=case_id,
        updates={
            "findings": findings,
            "recommended_action": recommended_action,
            "confidence": confidence_score
        }
    )

    if case is None:

        log_event(
            "PIPELINE_ERROR",
            merchant_id,
            {
                "stage":
                    "CASE_UPDATE",

                "error":
                    "Unable to update investigation case.",

                "case_id":
                    case_id
            },
            case_id=case_id
        )

        return None

    # ======================================================
    # 10. LINK REVIEW TO CASE
    # ======================================================

    if human_approval:

        review_id = (
            review["review_id"]
        )

        linked_case = link_review_to_case(

            case_id=
                case["case_id"],

            review_id=
                review_id
        )

        if linked_case is None:

            log_event(
                "PIPELINE_ERROR",
                merchant_id,
                {
                    "stage":
                        "REVIEW_LINK",

                    "error":
                        "Unable to link review to case.",

                    "case_id":
                        case["case_id"],

                    "review_id":
                        review_id
                },
                case_id=case["case_id"],
                review_id=review_id
            )

            return None

        case = linked_case

    # ======================================================
    # DISPLAY CASE
    # ======================================================

    print("\n")
    print("CASE")
    print("-" * 70)

    print(
        f"Case ID:          "
        f"{case['case_id']}"
    )

    print(
        f"Status:           "
        f"{case['status']}"
    )

    # ======================================================
    # 11. HUMAN REVIEW
    # ======================================================

    if human_approval:

        print("\n")
        print("HUMAN REVIEW")
        print("-" * 70)

        print(
            f"Review ID:        "
            f"{review['review_id']}"
        )

        print(
            "Status:           PENDING"
        )

        log_human_review(
            merchant_id=
                merchant_id,

            decision=
                "PENDING",

            reviewer=
                None,

            comments=
                "Human approval requested.",

            case_id=
                case["case_id"],

            review_id=
                review["review_id"]
        )

    # ======================================================
    # 12. FINAL AUDIT
    # ======================================================

    final_audit_data = {

        "risk_score":
            risk_score,

        "risk_category":
            risk_category,

        "failure_rate":
            failure_rate,

        "decision":
            decision,

        "reason":
            reason,

        "findings":
            findings,

        "confidence":
            confidence,

        "recommended_action":
            recommended_action,

        "human_approval_required":
            human_approval,

        "case_id":
            case["case_id"],

        "case_status":
            case["status"],

        "review_id":
            review["review_id"]
            if review
            else None,

        "review_status":
            "PENDING"
            if human_approval
            else "NOT_REQUIRED"
    }

    log_complete_case(
        merchant_id,
        final_audit_data,
        case_id=case["case_id"],
        review_id=(
            review["review_id"]
            if review
            else None
        )
    )

    # ======================================================
    # 13. AUDIT DISPLAY
    # ======================================================

    print("\n")
    print("AUDIT")
    print("-" * 70)

    print(
        "Risk assessment logged"
    )

    print(
        "Decision logged"
    )

    print(
        "Investigation logged"
    )

    print(
        "Action logged"
    )

    print(
        "Case logged"
    )

    if human_approval:

        print(
            "Human review logged"
        )

    print(
        "Final audit event logged"
    )

    # ======================================================
    # PIPELINE COMPLETE
    # ======================================================

    print("\n")
    print("=" * 70)
    print("REVENUEOS-AI PIPELINE COMPLETE")
    print("=" * 70)

    # ======================================================
    # RETURN RESULT
    # ======================================================

    return {

        "merchant_id":
            merchant_id,

        "risk_score":
            risk_score,

        "risk_category":
            risk_category,

        "failure_rate":
            failure_rate,

        "decision":
            decision,

        "reason":
            reason,

        "findings":
            findings,

        "confidence":
            confidence,

        "recommended_action":
            recommended_action,

        "human_approval_required":
            human_approval,

        "case":
            case,

        "review":
            review
    }


# ==========================================================
# DIRECT EXECUTION
# ==========================================================

if __name__ == "__main__":

    merchant_id = "M00005"

    run_revenueos(
        merchant_id
    )