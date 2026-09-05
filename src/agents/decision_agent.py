import pandas as pd

from src.agents.investigation_agent import investigate_merchant


# ==========================================================
# CONFIGURATION
# ==========================================================

RISK_FILE = "data/processed/merchant_risk_scores.csv"

INVESTIGATION_DECISIONS = [
    "INVESTIGATE",
    "ESCALATE"
]


# ==========================================================
# DECISION AGENT
# ==========================================================

def decide_action(merchant_id):

    # ------------------------------------------------------
    # LOAD RISK DATA
    # ------------------------------------------------------

    try:

        df = pd.read_csv(RISK_FILE)

    except FileNotFoundError:

        return {
            "merchant_id": merchant_id,
            "decision": "ERROR",
            "reason": f"Risk file not found: {RISK_FILE}"
        }

    # ------------------------------------------------------
    # VALIDATE COLUMNS
    # ------------------------------------------------------

    required_columns = [
        "merchant_id",
        "risk_score",
        "risk_category",
        "failure_rate"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        return {
            "merchant_id": merchant_id,
            "decision": "ERROR",
            "reason": (
                "Missing columns: "
                + ", ".join(missing_columns)
            )
        }

    # ------------------------------------------------------
    # FIND MERCHANT
    # ------------------------------------------------------

    merchant = df[
        df["merchant_id"].astype(str) == str(merchant_id)
    ]

    if merchant.empty:

        return {
            "merchant_id": merchant_id,
            "decision": "UNKNOWN",
            "reason": "Merchant not found in risk dataset."
        }

    merchant = merchant.iloc[0]

    # ------------------------------------------------------
    # EXTRACT RISK INFORMATION
    # ------------------------------------------------------

    try:

        risk_score = float(
            merchant["risk_score"]
        )

        failure_rate = float(
            merchant["failure_rate"]
        )

    except (ValueError, TypeError):

        return {
            "merchant_id": merchant_id,
            "decision": "ERROR",
            "reason": "Invalid risk score or failure rate."
        }

    risk_category = str(
        merchant["risk_category"]
    ).strip().title()

    failure_rate_pct = (
        failure_rate * 100
    )

    # ======================================================
    # DECISION LOGIC
    # ======================================================
    #
    # Priority:
    #
    # 1. Critical risk       -> ESCALATE
    # 2. High risk           -> INVESTIGATE
    # 3. High failure rate   -> INVESTIGATE
    # 4. Medium risk         -> MONITOR
    # 5. Moderate failure    -> MONITOR
    # 6. Otherwise           -> NO_ACTION
    #
    # ======================================================

    # ------------------------------------------------------
    # CRITICAL
    # ------------------------------------------------------

    if (
        risk_score >= 90
        or risk_category == "Critical"
    ):

        decision = "ESCALATE"

        reason = (
            "Critical merchant risk detected. "
            "Immediate investigation and human review "
            "are required."
        )

    # ------------------------------------------------------
    # HIGH RISK
    # ------------------------------------------------------

    elif (
        risk_score >= 60
        or risk_category == "High"
    ):

        decision = "INVESTIGATE"

        reason = (
            "High merchant risk detected based on "
            "risk score or risk category. "
            "Automated investigation is required."
        )

    # ------------------------------------------------------
    # HIGH FAILURE RATE
    # ------------------------------------------------------

    elif failure_rate_pct >= 10:

        decision = "INVESTIGATE"

        reason = (
            "Transaction failure rate is critically elevated. "
            "Automated investigation is required."
        )

    # ------------------------------------------------------
    # MEDIUM RISK
    # ------------------------------------------------------

    elif (
        risk_score >= 30
        or risk_category == "Medium"
    ):

        decision = "MONITOR"

        reason = (
            "Moderate merchant risk detected. "
            "Merchant should be continuously monitored."
        )

    # ------------------------------------------------------
    # MODERATE FAILURE RATE
    # ------------------------------------------------------

    elif failure_rate_pct >= 5:

        decision = "MONITOR"

        reason = (
            "Transaction failure behaviour is elevated "
            "but does not require immediate investigation. "
            "Continuous monitoring is recommended."
        )

    # ------------------------------------------------------
    # NORMAL
    # ------------------------------------------------------

    else:

        decision = "NO_ACTION"

        reason = (
            "Merchant risk and transaction behaviour "
            "are within the normal operating range."
        )

    # ======================================================
    # CREATE RESULT
    # ======================================================

    result = {

        "merchant_id": merchant_id,

        "risk_score": round(
            risk_score,
            2
        ),

        "risk_category": risk_category,

        "failure_rate": round(
            failure_rate,
            4
        ),

        "failure_rate_pct": round(
            failure_rate_pct,
            2
        ),

        "decision": decision,

        "reason": reason
    }

    # ======================================================
    # AUTOMATED INVESTIGATION
    # ======================================================

    if decision in INVESTIGATION_DECISIONS:

        try:

            investigation = investigate_merchant(
                merchant_id
            )

            if investigation:

                result[
                    "investigation"
                ] = investigation

            else:

                result[
                    "investigation_error"
                ] = (
                    "Investigation returned no result."
                )

        except Exception as e:

            result[
                "investigation_error"
            ] = (
                f"{type(e).__name__}: {e}"
            )

    # ======================================================
    # RETURN RESULT
    # ======================================================

    return result


# ==========================================================
# DISPLAY FUNCTION
# ==========================================================

def display_result(result):

    print("\n")
    print("=" * 70)
    print("REVENUEOS-AI DECISION AGENT")
    print("=" * 70)

    # ------------------------------------------------------
    # BASIC INFORMATION
    # ------------------------------------------------------

    print("\nRISK ASSESSMENT")
    print("-" * 70)

    print(
        f"Merchant:       "
        f"{result.get('merchant_id', 'N/A')}"
    )

    print(
        f"Risk Score:     "
        f"{result.get('risk_score', 'N/A')}"
    )

    print(
        f"Risk Category:  "
        f"{result.get('risk_category', 'N/A')}"
    )

    failure_rate = result.get(
        "failure_rate",
        None
    )

    if failure_rate is not None:

        print(
            f"Failure Rate:   "
            f"{failure_rate:.2%}"
        )

    # ------------------------------------------------------
    # DECISION
    # ------------------------------------------------------

    print("\nDECISION")
    print("-" * 70)

    print(
        f"Decision:       "
        f"{result.get('decision', 'N/A')}"
    )

    print(
        f"Reason:         "
        f"{result.get('reason', 'N/A')}"
    )

    # ======================================================
    # AUTOMATED INVESTIGATION
    # ======================================================

    if "investigation" in result:

        investigation = result[
            "investigation"
        ]

        print("\n")
        print("-" * 70)
        print("AUTOMATED INVESTIGATION")
        print("-" * 70)

        # --------------------------------------------------
        # ROOT CAUSE ANALYSIS
        # --------------------------------------------------

        analysis = investigation.get(
            "root_cause_analysis",
            {}
        )

        if not isinstance(
            analysis,
            dict
        ):

            analysis = {}

        # --------------------------------------------------
        # RECOMMENDATION
        # --------------------------------------------------

        recommendation = investigation.get(
            "recommendation",
            {}
        )

        if not isinstance(
            recommendation,
            dict
        ):

            recommendation = {}

        # --------------------------------------------------
        # DOMINANT FAILURE
        # --------------------------------------------------

        print(
            "\nDominant Failure: "
            f"{analysis.get(
                'dominant_failure_reason',
                'N/A'
            )}"
        )

        # --------------------------------------------------
        # LIKELY CAUSE
        # --------------------------------------------------

        print(
            "Likely Cause:     "
            f"{analysis.get(
                'likely_cause',
                'N/A'
            )}"
        )

        # --------------------------------------------------
        # RECOMMENDED ACTION
        # --------------------------------------------------

        print(
            "\nRecommended Action:"
        )

        print(
            recommendation.get(
                "action",
                "N/A"
            )
        )

        # --------------------------------------------------
        # CONFIDENCE
        # --------------------------------------------------

        print(
            "\nConfidence: "
            f"{recommendation.get(
                'confidence',
                'N/A'
            )}"
        )

        # --------------------------------------------------
        # HUMAN APPROVAL
        # --------------------------------------------------

        print(
            "Human Approval Required: "
            f"{recommendation.get(
                'human_approval_required',
                'N/A'
            )}"
        )

    # ======================================================
    # INVESTIGATION ERROR
    # ======================================================

    if "investigation_error" in result:

        print("\n")
        print("-" * 70)
        print("INVESTIGATION ERROR")
        print("-" * 70)

        print(
            result[
                "investigation_error"
            ]
        )

    # ======================================================
    # COMPLETE
    # ======================================================

    print("\n")
    print("=" * 70)
    print("DECISION AGENT COMPLETE")
    print("=" * 70)


# ==========================================================
# TEST / SCRIPT ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    # Change this ID when testing another merchant
    merchant_id = "M00005"

    result = decide_action(
        merchant_id
    )

    display_result(
        result
    )