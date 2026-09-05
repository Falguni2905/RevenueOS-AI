def should_stop(state):

    tools_used = set(
        state.tools_used
    )

    # --------------------------------------------------------
    # Critical merchants
    # --------------------------------------------------------

    if state.risk_score >= 80:

        required_tools = {
            "merchant_profile",
            "failure_analysis",
            "payment_method_analysis",
            "hourly_analysis",
            "transaction_analysis"
        }

        if required_tools.issubset(
            tools_used
        ):

            return True

    # --------------------------------------------------------
    # High-risk merchants
    # --------------------------------------------------------

    elif state.risk_score >= 60:

        required_tools = {
            "merchant_profile",
            "failure_analysis",
            "payment_method_analysis",
            "hourly_analysis"
        }

        if required_tools.issubset(
            tools_used
        ):

            return True

    # --------------------------------------------------------
    # Moderate-risk merchants
    # --------------------------------------------------------

    elif state.risk_score >= 30:

        required_tools = {
            "merchant_profile",
            "failure_analysis"
        }

        if required_tools.issubset(
            tools_used
        ):

            return True

    return False