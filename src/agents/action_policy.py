def determine_action(
    risk_score,
    confidence_score
):

    # ========================================================
    # CRITICAL RISK
    # ========================================================

    if risk_score >= 80:

        if confidence_score >= 80:

            return {
                "action": "ESCALATE",
                "human_approval_required": True,
                "reason":
                    "Critical risk with strong evidence."
            }

        return {
            "action": "HUMAN_REVIEW",
            "human_approval_required": True,
            "reason":
                "Critical risk but insufficient confidence."
        }

    # ========================================================
    # HIGH RISK
    # ========================================================

    if risk_score >= 60:

        if confidence_score >= 80:

            return {
                "action": "INVESTIGATE",
                "human_approval_required": False,
                "reason":
                    "High risk with sufficient evidence."
            }

        return {
            "action": "HUMAN_REVIEW",
            "human_approval_required": True,
            "reason":
                "High risk requires human validation."
        }

    # ========================================================
    # MODERATE RISK
    # ========================================================

    if risk_score >= 30:

        return {
            "action": "MONITOR",
            "human_approval_required": False,
            "reason":
                "Moderate risk. Continue monitoring."
        }

    # ========================================================
    # LOW RISK
    # ========================================================

    return {
        "action": "NO_ACTION",
        "human_approval_required": False,
        "reason":
            "Risk is within normal range."
    }