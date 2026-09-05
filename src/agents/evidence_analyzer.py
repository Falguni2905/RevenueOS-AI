def analyze_evidence(state):

    evidence = state.evidence

    findings = []

    # ========================================================
    # FAILURE ANALYSIS
    # ========================================================

    failure_data = evidence.get(
        "failure_analysis"
    )

    if failure_data:

        dominant_failure = (
            failure_data
            .get(
                "dominant_failure_reason"
            )
        )

        if dominant_failure:

            findings.append({
                "type": "failure_pattern",
                "finding":
                    f"Dominant failure reason: "
                    f"{dominant_failure}",
                "source":
                    "failure_analysis"
            })

    # ========================================================
    # PAYMENT METHOD
    # ========================================================

    payment_data = evidence.get(
        "payment_method_analysis"
    )

    if payment_data:

        methods = payment_data.get(
            "payment_method_analysis",
            []
        )

        if methods:

            worst_method = max(
                methods,
                key=lambda x:
                    x["failure_rate"]
            )

            findings.append({
                "type":
                    "payment_method_pattern",

                "finding":
                    f"Highest payment-method "
                    f"failure rate: "
                    f"{worst_method['payment_method']}",

                "source":
                    "payment_method_analysis"
            })

    # ========================================================
    # HOURLY ANALYSIS
    # ========================================================

    hourly_data = evidence.get(
        "hourly_analysis"
    )

    if hourly_data:

        hours = hourly_data.get(
            "hourly_analysis",
            []
        )

        if hours:

            worst_hour = max(
                hours,
                key=lambda x:
                    x["failure_rate"]
            )

            findings.append({
                "type":
                    "time_pattern",

                "finding":
                    f"Highest failure rate "
                    f"occurs around "
                    f"{worst_hour['hour']}:00",

                "source":
                    "hourly_analysis"
            })

    return findings