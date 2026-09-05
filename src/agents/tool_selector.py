def select_tools(
    risk_score,
    failure_rate
):

    selected_tools = []

    # Always understand the merchant
    selected_tools.append(
        "merchant_profile"
    )

    # Failure analysis is important
    # for elevated failure rates
    if failure_rate >= 0.05:

        selected_tools.append(
            "failure_analysis"
        )

    # Higher-risk merchants require
    # payment method investigation
    if risk_score >= 40:

        selected_tools.append(
            "payment_method_analysis"
        )

    # Very high-risk merchants require
    # temporal investigation
    if risk_score >= 60:

        selected_tools.append(
            "hourly_analysis"
        )

    # Critical/high-value cases get
    # transaction-level inspection
    if risk_score >= 80:

        selected_tools.append(
            "transaction_analysis"
        )

    return selected_tools