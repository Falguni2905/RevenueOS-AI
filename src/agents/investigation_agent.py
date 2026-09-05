"""
RevenueOS-AI
Merchant Investigation Agent

Purpose:
    Investigate merchant payment incidents using transaction evidence.

Current version:
    Local deterministic investigation engine.

Future version:
    LLM + tool-calling agent can be added without changing
    the underlying investigation tools.
"""

from src.services.investigation import (
    get_merchant_summary,
    get_failure_breakdown,
    get_payment_method_breakdown,
    get_hourly_failure_pattern,
    get_merchant_profile
)


# ============================================================
# 1. COLLECT INVESTIGATION EVIDENCE
# ============================================================

def collect_investigation_data(merchant_id):
    """
    Collect all available evidence for a merchant.
    """

    investigation_data = {}

    investigation_data["merchant_profile"] = (
        get_merchant_profile(merchant_id)
    )

    investigation_data["merchant_summary"] = (
        get_merchant_summary(merchant_id)
    )

    investigation_data["failure_breakdown"] = (
        get_failure_breakdown(merchant_id)
    )

    investigation_data["payment_method_breakdown"] = (
        get_payment_method_breakdown(merchant_id)
    )

    investigation_data["hourly_failure_pattern"] = (
        get_hourly_failure_pattern(merchant_id)
    )

    return investigation_data


# ============================================================
# 2. DETERMINE INCIDENT SEVERITY
# ============================================================

def determine_severity(failure_rate, failed_transactions):
    """
    Determine incident severity using deterministic rules.
    """

    if failure_rate >= 0.10 or failed_transactions >= 100:
        return "High"

    elif failure_rate >= 0.07 or failed_transactions >= 50:
        return "Medium"

    else:
        return "Low"


# ============================================================
# 3. FIND DOMINANT FAILURE REASON
# ============================================================

def find_dominant_failure(failure_breakdown):
    """
    Identify the most common payment failure reason.
    """

    if not failure_breakdown:
        return {
            "reason": "None",
            "count": 0
        }

    dominant_reason = max(
        failure_breakdown,
        key=failure_breakdown.get
    )

    dominant_count = failure_breakdown[
        dominant_reason
    ]

    return {
        "reason": dominant_reason,
        "count": dominant_count
    }


# ============================================================
# 4. DETERMINE LIKELY ROOT CAUSE
# ============================================================

def determine_root_cause(dominant_failure):
    """
    Translate the dominant failure reason into a
    business-oriented root-cause hypothesis.
    """

    root_causes = {

        "Network Error":
            "Potential payment connectivity or network "
            "reliability issue.",

        "Bank Decline":
            "Potential increase in issuer or bank-side "
            "payment declines.",

        "Payment Timeout":
            "Potential payment-processing latency or "
            "timeout issue.",

        "Authentication Failure":
            "Potential authentication or payment "
            "verification issue.",

        "Insufficient Funds":
            "Customer-side insufficient balance appears "
            "to be a major contributor.",

        "Technical Error":
            "Potential technical or platform-side "
            "payment-processing issue."
    }

    return root_causes.get(
        dominant_failure,
        "Insufficient evidence to determine a specific "
        "root cause."
    )


# ============================================================
# 5. DETERMINE PAYMENT METHOD ISSUE
# ============================================================

def analyze_payment_methods(payment_method_breakdown):
    """
    Identify the payment method with the highest
    failure rate.
    """

    if not payment_method_breakdown:
        return {
            "payment_method": "None",
            "failure_rate": 0
        }

    highest_failure_method = max(
        payment_method_breakdown,
        key=lambda x: x.get("failure_rate", 0)
    )

    return {
        "payment_method":
            highest_failure_method.get(
                "payment_method"
            ),

        "failure_rate":
            highest_failure_method.get(
                "failure_rate",
                0
            ),

        "transactions":
            highest_failure_method.get(
                "transactions",
                0
            ),

        "failures":
            highest_failure_method.get(
                "failures",
                0
            )
    }


# ============================================================
# 6. ANALYZE HOURLY PATTERN
# ============================================================

def analyze_hourly_pattern(hourly_pattern):
    """
    Identify the hour with the highest failure rate.
    """

    if not hourly_pattern:
        return {
            "hour": None,
            "failure_rate": 0
        }

    highest_failure_hour = max(
        hourly_pattern,
        key=lambda x: x.get("failure_rate", 0)
    )

    return {
        "hour":
            highest_failure_hour.get("hour"),

        "failure_rate":
            highest_failure_hour.get(
                "failure_rate",
                0
            ),

        "transactions":
            highest_failure_hour.get(
                "transactions",
                0
            ),

        "failures":
            highest_failure_hour.get(
                "failures",
                0
            )
    }


# ============================================================
# 7. ESTIMATE BUSINESS IMPACT
# ============================================================

def calculate_business_impact(summary):
    """
    Estimate the value associated with failed transactions.

    This is an illustrative estimate, not actual Razorpay data.
    """

    failed_transactions = summary.get(
        "failed_transactions",
        0
    )

    total_value = summary.get(
        "total_value",
        0
    )

    transaction_count = summary.get(
        "transaction_count",
        0
    )

    if transaction_count == 0:
        return {
            "estimated_failed_value": 0,
            "average_transaction_value": 0
        }

    average_transaction_value = (
        total_value / transaction_count
    )

    estimated_failed_value = (
        failed_transactions *
        average_transaction_value
    )

    return {
        "estimated_failed_value":
            round(
                estimated_failed_value,
                2
            ),

        "average_transaction_value":
            round(
                average_transaction_value,
                2
            )
    }


# ============================================================
# 8. RECOMMEND ACTION
# ============================================================

def recommend_action(
    severity,
    dominant_failure,
    payment_method_analysis
):
    """
    Generate an operational recommendation.
    """

    if severity == "High":

        action = (
            "Immediately investigate the incident. "
            "Review the dominant failure reason and "
            "affected payment channels. Escalate to "
            "payment operations for human review."
        )

    elif severity == "Medium":

        action = (
            "Monitor the merchant closely. Investigate "
            "the dominant failure reason and review "
            "payment-method performance."
        )

    else:

        action = (
            "Continue monitoring merchant performance "
            "for changes in payment failure rate."
        )

    # Add payment-method information

    if (
        payment_method_analysis["payment_method"]
        != "None"
    ):

        action += (
            f" The payment method showing the highest "
            f"failure rate is "
            f"{payment_method_analysis['payment_method']}."
        )

    return action


# ============================================================
# 9. DETERMINE CONFIDENCE
# ============================================================

def determine_confidence(
    failed_transactions,
    dominant_failure_count
):
    """
    Determine confidence based on the amount of
    supporting evidence.
    """

    if (
        failed_transactions >= 50
        and dominant_failure_count >= 20
    ):

        return "High"

    elif (
        failed_transactions >= 20
        and dominant_failure_count >= 10
    ):

        return "Medium"

    else:

        return "Low"


# ============================================================
# 10. MAIN INVESTIGATION ENGINE
# ============================================================

def investigate_merchant(merchant_id):
    """
    Perform complete merchant investigation.
    """

    evidence = collect_investigation_data(
        merchant_id
    )

    merchant_profile = (
        evidence["merchant_profile"]
    )

    summary = (
        evidence["merchant_summary"]
    )

    # Merchant not found

    if summary is None:

        return {
            "merchant_id": merchant_id,
            "status": "Merchant Not Found",
            "error":
                f"Merchant {merchant_id} was not found."
        }

    # --------------------------------------------------------
    # Failure analysis
    # --------------------------------------------------------

    failure_analysis = find_dominant_failure(
        evidence["failure_breakdown"]
    )

    dominant_failure = failure_analysis["reason"]

    dominant_failure_count = (
        failure_analysis["count"]
    )

    # --------------------------------------------------------
    # Severity
    # --------------------------------------------------------

    failure_rate = summary.get(
        "failure_rate",
        0
    )

    failed_transactions = summary.get(
        "failed_transactions",
        0
    )

    severity = determine_severity(
        failure_rate,
        failed_transactions
    )

    # --------------------------------------------------------
    # Payment method analysis
    # --------------------------------------------------------

    payment_method_analysis = (
        analyze_payment_methods(
            evidence[
                "payment_method_breakdown"
            ]
        )
    )

    # --------------------------------------------------------
    # Hourly analysis
    # --------------------------------------------------------

    hourly_analysis = (
        analyze_hourly_pattern(
            evidence[
                "hourly_failure_pattern"
            ]
        )
    )

    # --------------------------------------------------------
    # Root cause
    # --------------------------------------------------------

    likely_cause = determine_root_cause(
        dominant_failure
    )

    # --------------------------------------------------------
    # Business impact
    # --------------------------------------------------------

    business_impact = calculate_business_impact(
        summary
    )

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    recommended_action = recommend_action(
        severity,
        dominant_failure,
        payment_method_analysis
    )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = determine_confidence(
        failed_transactions,
        dominant_failure_count
    )

    # --------------------------------------------------------
    # Human approval
    # --------------------------------------------------------

    human_approval_required = (
        severity == "High"
    )

    # --------------------------------------------------------
    # Final investigation result
    # --------------------------------------------------------

    result = {

        "merchant_id":
            merchant_id,

        "status":
            "Investigation Complete",

        "merchant_profile":
            merchant_profile,

        "incident": {

            "severity":
                severity,

            "failure_rate":
                round(
                    failure_rate,
                    4
                ),

            "failed_transactions":
                failed_transactions
        },

        "root_cause_analysis": {

            "dominant_failure_reason":
                dominant_failure,

            "dominant_failure_count":
                dominant_failure_count,

            "likely_cause":
                likely_cause
        },

        "payment_method_analysis":
            payment_method_analysis,

        "hourly_analysis":
            hourly_analysis,

        "business_impact":
            business_impact,

        "recommendation": {

            "action":
                recommended_action,

            "confidence":
                confidence,

            "human_approval_required":
                human_approval_required
        },

        "evidence":
            evidence
    }

    return result


# ============================================================
# 11. PRINT INVESTIGATION REPORT
# ============================================================

def print_investigation_report(result):
    """
    Display investigation results in a readable format.
    """

    print("\n")
    print("=" * 70)
    print("REVENUEOS-AI MERCHANT INVESTIGATION")
    print("=" * 70)

    if "error" in result:

        print(
            f"\nERROR: {result['error']}"
        )

        return

    merchant_id = result[
        "merchant_id"
    ]

    incident = result[
        "incident"
    ]

    root_cause = result[
        "root_cause_analysis"
    ]

    payment_analysis = result[
        "payment_method_analysis"
    ]

    hourly_analysis = result[
        "hourly_analysis"
    ]

    impact = result[
        "business_impact"
    ]

    recommendation = result[
        "recommendation"
    ]

    # --------------------------------------------------------
    # Merchant
    # --------------------------------------------------------

    print(
        f"\nMerchant: {merchant_id}"
    )

    print(
        f"Status: {result['status']}"
    )

    # --------------------------------------------------------
    # Incident
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("INCIDENT")
    print("-" * 70)

    print(
        f"Severity: "
        f"{incident['severity']}"
    )

    print(
        f"Failure Rate: "
        f"{incident['failure_rate']:.2%}"
    )

    print(
        f"Failed Transactions: "
        f"{incident['failed_transactions']}"
    )

    # --------------------------------------------------------
    # Root Cause
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("ROOT CAUSE ANALYSIS")
    print("-" * 70)

    print(
        f"Dominant Failure: "
        f"{root_cause['dominant_failure_reason']}"
    )

    print(
        f"Failure Count: "
        f"{root_cause['dominant_failure_count']}"
    )

    print(
        f"Likely Cause: "
        f"{root_cause['likely_cause']}"
    )

    # --------------------------------------------------------
    # Payment Method
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("PAYMENT METHOD ANALYSIS")
    print("-" * 70)

    print(
        f"Highest Failure Method: "
        f"{payment_analysis['payment_method']}"
    )

    print(
        f"Failure Rate: "
        f"{payment_analysis['failure_rate']:.2%}"
    )

    print(
        f"Transactions: "
        f"{payment_analysis['transactions']}"
    )

    print(
        f"Failures: "
        f"{payment_analysis['failures']}"
    )

    # --------------------------------------------------------
    # Hourly Pattern
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("HOURLY PATTERN")
    print("-" * 70)

    if hourly_analysis["hour"] is not None:

        print(
            f"Highest Failure Hour: "
            f"{hourly_analysis['hour']}:00"
        )

        print(
            f"Failure Rate: "
            f"{hourly_analysis['failure_rate']:.2%}"
        )

        print(
            f"Transactions: "
            f"{hourly_analysis['transactions']}"
        )

        print(
            f"Failures: "
            f"{hourly_analysis['failures']}"
        )

    else:

        print(
            "No hourly pattern available."
        )

    # --------------------------------------------------------
    # Business Impact
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("BUSINESS IMPACT")
    print("-" * 70)

    print(
        f"Average Transaction Value: "
        f"₹{impact['average_transaction_value']:,.2f}"
    )

    print(
        f"Estimated Failed Transaction Value: "
        f"₹{impact['estimated_failed_value']:,.2f}"
    )

    print(
        "Note: Failed transaction value is an "
        "illustrative estimate based on historical "
        "average transaction value."
    )

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("RECOMMENDED ACTION")
    print("-" * 70)

    print(
        recommendation["action"]
    )

    print(
        f"\nConfidence: "
        f"{recommendation['confidence']}"
    )

    print(
        f"Human Approval Required: "
        f"{recommendation['human_approval_required']}"
    )

    print("\n" + "=" * 70)


# ============================================================
# 12. TEST THE AGENT
# ============================================================

if __name__ == "__main__":

    # Known incident merchant
    merchant_id = "M00008"

    result = investigate_merchant(
        merchant_id
    )

    print_investigation_report(
        result
    )