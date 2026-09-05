import pandas as pd

from src.agents.revenueos_orchestrator import run_revenueos
from src.agents.investigation_agent import investigate_merchant


# ==========================================================
# CONFIGURATION
# ==========================================================

EVALUATION_FILE = "evaluation/evaluation_cases.csv"

RESULTS_FILE = (
    "evaluation/decision_evaluation_results.csv"
)

SCORECARD_FILE = (
    "evaluation/agent_scorecard.csv"
)

INVESTIGATION_DECISIONS = [
    "INVESTIGATE",
    "ESCALATE"
]

DECISION_SEVERITY = {
    "NO_ACTION": 0,
    "MONITOR": 1,
    "INVESTIGATE": 2,
    "ESCALATE": 3
}


# ==========================================================
# MAIN EVALUATION FUNCTION
# ==========================================================

def evaluate_system():

    # ======================================================
    # LOAD EVALUATION CASES
    # ======================================================

    try:

        cases = pd.read_csv(
            EVALUATION_FILE
        )

    except FileNotFoundError:

        print("\nERROR:")
        print(
            f"Evaluation file not found: "
            f"{EVALUATION_FILE}"
        )

        return None

    if cases.empty:

        print("\nERROR:")
        print(
            "Evaluation file contains no cases."
        )

        return None

    # ======================================================
    # VALIDATE REQUIRED COLUMNS
    # ======================================================

    required_columns = [
        "merchant_id",
        "expected_decision"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in cases.columns
    ]

    if missing_columns:

        print("\nERROR:")
        print(
            "Missing required columns:"
        )

        print(
            ", ".join(missing_columns)
        )

        return None

    # ======================================================
    # INITIALIZE RESULTS
    # ======================================================

    results = []

    print("\n")
    print("=" * 70)
    print(
        "REVENUEOS-AI DECISION EVALUATION"
    )
    print("=" * 70)

    print(
        f"\nEvaluation File: "
        f"{EVALUATION_FILE}"
    )

    print(
        f"Total Cases:     "
        f"{len(cases)}"
    )

    # ======================================================
    # RUN AGENT AGAINST ALL CASES
    # ======================================================

    for index, row in cases.iterrows():

        merchant_id = str(
            row["merchant_id"]
        ).strip()

        expected_decision = str(
            row["expected_decision"]
        ).strip().upper()

        print(
            "\n" + "-" * 70
        )

        print(
            f"Case {index + 1}/{len(cases)}"
        )

        print(
            f"Merchant: {merchant_id}"
        )

        print(
            f"Expected: {expected_decision}"
        )

        # --------------------------------------------------
        # RUN REVENUEOS AGENT
        # --------------------------------------------------

        try:

            output = run_revenueos(
                merchant_id
            )

            if output is None:

                actual_decision = "ERROR"

            elif not isinstance(
                output,
                dict
            ):

                actual_decision = "ERROR"

            else:

                actual_decision = str(
                    output.get(
                        "decision",
                        "UNKNOWN"
                    )
                ).strip().upper()

                if not actual_decision:

                    actual_decision = "UNKNOWN"

        except Exception as e:

            actual_decision = "ERROR"

            print(
                f"Agent Error: "
                f"{type(e).__name__}: {e}"
            )

        # --------------------------------------------------
        # CHECK DECISION
        # --------------------------------------------------

        correct = (
            actual_decision
            == expected_decision
        )

        print(
            f"Actual:   {actual_decision}"
        )

        print(
            f"Result:   "
            f"{'CORRECT' if correct else 'INCORRECT'}"
        )

        # --------------------------------------------------
        # STORE RESULT
        # --------------------------------------------------

        results.append({

            "merchant_id":
                merchant_id,

            "expected_decision":
                expected_decision,

            "actual_decision":
                actual_decision,

            "correct":
                correct
        })

    # ======================================================
    # CREATE RESULTS DATAFRAME
    # ======================================================

    results_df = pd.DataFrame(
        results
    )

    # ======================================================
    # BASIC VALIDATION
    # ======================================================

    if results_df.empty:

        print("\nERROR:")
        print(
            "No evaluation results were generated."
        )

        return None

    # ======================================================
    # OVERALL ACCURACY
    # ======================================================

    total_cases = len(
        results_df
    )

    correct_cases = int(
        results_df["correct"].sum()
    )

    incorrect_cases = (
        total_cases
        - correct_cases
    )

    accuracy = (
        correct_cases
        / total_cases
        * 100
        if total_cases > 0
        else 0.0
    )

    print("\n")
    print("=" * 70)
    print(
        "OVERALL PERFORMANCE"
    )
    print("=" * 70)

    print(
        f"Total Cases:          "
        f"{total_cases}"
    )

    print(
        f"Correct Decisions:    "
        f"{correct_cases}"
    )

    print(
        f"Incorrect Decisions:  "
        f"{incorrect_cases}"
    )

    print(
        f"Decision Accuracy:    "
        f"{accuracy:.2f}%"
    )

    # ======================================================
    # ACCURACY BY DECISION TYPE
    # ======================================================

    print("\n")
    print("-" * 70)
    print(
        "ACCURACY BY DECISION TYPE"
    )
    print("-" * 70)

    decision_summary = (
        results_df
        .groupby(
            "expected_decision"
        )
        .agg(
            total_cases=(
                "merchant_id",
                "count"
            ),
            correct_cases=(
                "correct",
                "sum"
            )
        )
    )

    decision_summary["accuracy"] = (
        decision_summary["correct_cases"]
        /
        decision_summary["total_cases"]
        * 100
    )

    print(
        decision_summary
        .round(2)
        .to_string()
    )

    # ======================================================
    # ERROR ANALYSIS
    # ======================================================

    print("\n")
    print("-" * 70)
    print(
        "AGENT ERROR ANALYSIS"
    )
    print("-" * 70)

    errors = results_df[
        results_df["correct"] == False
    ]

    print(
        f"\nIncorrect Decisions: "
        f"{len(errors)}"
    )

    print(
        f"Total Cases: "
        f"{total_cases}"
    )

    error_rate = (
        len(errors)
        / total_cases
        * 100
        if total_cases > 0
        else 0.0
    )

    print(
        f"Error Rate: "
        f"{error_rate:.2f}%"
    )

    print("\nDecision Errors:")
    print("-" * 70)

    if errors.empty:

        print(
            "No incorrect decisions found."
        )

    else:

        print(
            errors[
                [
                    "merchant_id",
                    "expected_decision",
                    "actual_decision"
                ]
            ].to_string(
                index=False
            )
        )

    # ======================================================
    # CONFUSION MATRIX
    # ======================================================

    print("\n")
    print("-" * 70)
    print(
        "DECISION CONFUSION MATRIX"
    )
    print("-" * 70)

    decision_order = [
        "NO_ACTION",
        "MONITOR",
        "INVESTIGATE",
        "ESCALATE"
    ]

    confusion_matrix = pd.crosstab(
        results_df[
            "expected_decision"
        ],
        results_df[
            "actual_decision"
        ],
        rownames=["Expected"],
        colnames=["Actual"],
        dropna=False
    )

    confusion_matrix = (
        confusion_matrix
        .reindex(
            index=decision_order,
            fill_value=0
        )
    )

    # Add missing normal decision columns
    for decision in decision_order:

        if decision not in confusion_matrix.columns:

            confusion_matrix[
                decision
            ] = 0

    # Add ERROR / UNKNOWN if present
    special_decisions = [
        "ERROR",
        "UNKNOWN"
    ]

    for decision in special_decisions:

        if decision in results_df[
            "actual_decision"
        ].values:

            if decision not in confusion_matrix.columns:

                confusion_matrix[
                    decision
                ] = 0

            for expected in decision_order:

                confusion_matrix.loc[
                    expected,
                    decision
                ] = len(
                    results_df[
                        (
                            results_df[
                                "expected_decision"
                            ]
                            == expected
                        )
                        &
                        (
                            results_df[
                                "actual_decision"
                            ]
                            == decision
                        )
                    ]
                )

    confusion_matrix = confusion_matrix[
        [
            column
            for column in [
                "NO_ACTION",
                "MONITOR",
                "INVESTIGATE",
                "ESCALATE",
                "ERROR",
                "UNKNOWN"
            ]
            if column in confusion_matrix.columns
        ]
    ]

    print(
        confusion_matrix.to_string()
    )

    # ======================================================
    # INVESTIGATION COVERAGE
    # ======================================================

    print("\n")
    print("-" * 70)
    print(
        "INVESTIGATION COVERAGE"
    )
    print("-" * 70)

    expected_investigations = (
        results_df[
            results_df[
                "expected_decision"
            ].isin(
                INVESTIGATION_DECISIONS
            )
        ]
    )

    actual_investigations = (
        results_df[
            results_df[
                "actual_decision"
            ].isin(
                INVESTIGATION_DECISIONS
            )
        ]
    )

    expected_count = len(
        expected_investigations
    )

    actual_count = len(
        actual_investigations
    )

    successful_investigations = len(
        results_df[
            results_df[
                "expected_decision"
            ].isin(
                INVESTIGATION_DECISIONS
            )
            &
            results_df[
                "actual_decision"
            ].isin(
                INVESTIGATION_DECISIONS
            )
        ]
    )

    if expected_count > 0:

        investigation_coverage = (
            successful_investigations
            / expected_count
            * 100
        )

    else:

        investigation_coverage = 100.0

    print(
        f"Expected Investigations:  "
        f"{expected_count}"
    )

    print(
        f"Actual Investigations:    "
        f"{actual_count}"
    )

    print(
        f"Successful Investigations:"
        f" {successful_investigations}"
    )

    print(
        f"Investigation Coverage:    "
        f"{investigation_coverage:.2f}%"
    )

    # ======================================================
    # INVESTIGATION MISSES
    # ======================================================

    print("\n")
    print("-" * 70)
    print(
        "INVESTIGATION MISSES"
    )
    print("-" * 70)

    investigation_misses = (
        results_df[
            results_df[
                "expected_decision"
            ].isin(
                INVESTIGATION_DECISIONS
            )
            &
            ~results_df[
                "actual_decision"
            ].isin(
                INVESTIGATION_DECISIONS
            )
        ]
    )

    if investigation_misses.empty:

        print("None")

    else:

        print(
            investigation_misses[
                [
                    "merchant_id",
                    "expected_decision",
                    "actual_decision"
                ]
            ].to_string(
                index=False
            )
        )

    # ======================================================
    # INVESTIGATION QUALITY
    # ======================================================

    print("\n")
    print("-" * 70)
    print(
        "INVESTIGATION QUALITY"
    )
    print("-" * 70)

    quality_checks = {

        "root_cause_present": 0,

        "recommendation_present": 0,

        "confidence_present": 0,

        "failure_reason_present": 0
    }

    investigated_cases = 0

    for _, row in results_df.iterrows():

        actual_decision = row[
            "actual_decision"
        ]

        if actual_decision not in (
            INVESTIGATION_DECISIONS
        ):

            continue

        investigated_cases += 1

        merchant_id = row[
            "merchant_id"
        ]

        try:

            investigation = (
                investigate_merchant(
                    merchant_id
                )
            )

            if not investigation:

                continue

            if not isinstance(
                investigation,
                dict
            ):

                continue

            analysis = investigation.get(
                "root_cause_analysis",
                {}
            )

            recommendation = investigation.get(
                "recommendation",
                {}
            )

            if not isinstance(
                analysis,
                dict
            ):

                analysis = {}

            if not isinstance(
                recommendation,
                dict
            ):

                recommendation = {}

            # ----------------------------------------------
            # FAILURE REASON
            # ----------------------------------------------

            if analysis.get(
                "dominant_failure_reason"
            ):

                quality_checks[
                    "failure_reason_present"
                ] += 1

            # ----------------------------------------------
            # ROOT CAUSE
            # ----------------------------------------------

            if analysis.get(
                "likely_cause"
            ):

                quality_checks[
                    "root_cause_present"
                ] += 1

            # ----------------------------------------------
            # RECOMMENDATION
            # ----------------------------------------------

            if recommendation.get(
                "action"
            ):

                quality_checks[
                    "recommendation_present"
                ] += 1

            # ----------------------------------------------
            # CONFIDENCE
            # ----------------------------------------------

            if recommendation.get(
                "confidence"
            ) is not None:

                quality_checks[
                    "confidence_present"
                ] += 1

        except Exception as e:

            print(
                f"Investigation error for "
                f"{merchant_id}: "
                f"{type(e).__name__}: {e}"
            )

    print(
        f"Investigated Cases: "
        f"{investigated_cases}"
    )

    if investigated_cases > 0:

        for check, count in (
            quality_checks.items()
        ):

            percentage = (
                count
                / investigated_cases
                * 100
            )

            print(
                f"{check}: "
                f"{percentage:.2f}%"
            )

        investigation_quality_score = (
            sum(
                quality_checks.values()
            )
            /
            (
                investigated_cases
                * len(quality_checks)
            )
            * 100
        )

    else:

        investigation_quality_score = 0.0

    print(
        f"\nInvestigation Quality Score: "
        f"{investigation_quality_score:.2f}%"
    )

    # ======================================================
    # RISK-WEIGHTED EVALUATION
    # ======================================================

    print("\n")
    print("-" * 70)
    print(
        "RISK-WEIGHTED EVALUATION"
    )
    print("-" * 70)

    false_negative_count = 0

    false_positive_count = 0

    severe_error_count = 0

    # ------------------------------------------------------
    # COMPARE EXPECTED VS ACTUAL
    # ------------------------------------------------------

    for _, row in results_df.iterrows():

        expected = row[
            "expected_decision"
        ]

        actual = row[
            "actual_decision"
        ]

        expected_level = (
            DECISION_SEVERITY.get(
                expected
            )
        )

        actual_level = (
            DECISION_SEVERITY.get(
                actual
            )
        )

        # --------------------------------------------------
        # AGENT ERROR
        # --------------------------------------------------

        if actual in (
            "ERROR",
            "UNKNOWN"
        ):

            false_negative_count += 1

            if expected in (
                "INVESTIGATE",
                "ESCALATE"
            ):

                severe_error_count += 1

            continue

        # --------------------------------------------------
        # UNKNOWN EXPECTED DECISION
        # --------------------------------------------------

        if expected_level is None:

            continue

        # --------------------------------------------------
        # FALSE NEGATIVE
        # --------------------------------------------------

        if actual_level < expected_level:

            false_negative_count += 1

            if (
                expected_level >= 2
                and actual_level <= 1
            ):

                severe_error_count += 1

        # --------------------------------------------------
        # FALSE POSITIVE
        # --------------------------------------------------

        elif actual_level > expected_level:

            false_positive_count += 1

    # ======================================================
    # ERROR RATES
    # ======================================================

    false_negative_rate = (
        false_negative_count
        / total_cases
        * 100
        if total_cases > 0
        else 0.0
    )

    false_positive_rate = (
        false_positive_count
        / total_cases
        * 100
        if total_cases > 0
        else 0.0
    )

    severe_error_rate = (
        severe_error_count
        / total_cases
        * 100
        if total_cases > 0
        else 0.0
    )

    # ======================================================
    # RISK-WEIGHTED SCORE
    # ======================================================

    penalty = (
        false_negative_count * 3
        + false_positive_count
        + severe_error_count * 5
    )

    maximum_penalty = (
        total_cases * 8
    )

    if maximum_penalty > 0:

        risk_weighted_score = max(
            0.0,
            100.0
            -
            (
                penalty
                / maximum_penalty
                * 100.0
            )
        )

    else:

        risk_weighted_score = 100.0

    print(
        f"False Negatives:       "
        f"{false_negative_count}"
    )

    print(
        f"False Negative Rate:   "
        f"{false_negative_rate:.2f}%"
    )

    print(
        f"False Positives:       "
        f"{false_positive_count}"
    )

    print(
        f"False Positive Rate:   "
        f"{false_positive_rate:.2f}%"
    )

    print(
        f"Severe Risk Errors:    "
        f"{severe_error_count}"
    )

    print(
        f"Severe Error Rate:     "
        f"{severe_error_rate:.2f}%"
    )

    print(
        f"Risk-Weighted Score:   "
        f"{risk_weighted_score:.2f}%"
    )

    # ======================================================
    # ACTUAL DECISION DISTRIBUTION
    # ======================================================

    print("\n")
    print("-" * 70)
    print(
        "ACTUAL DECISION DISTRIBUTION"
    )
    print("-" * 70)

    print(
        results_df[
            "actual_decision"
        ].value_counts()
    )

    # ======================================================
    # EXPECTED DECISION DISTRIBUTION
    # ======================================================

    print("\n")
    print("-" * 70)
    print(
        "EXPECTED DECISION DISTRIBUTION"
    )
    print("-" * 70)

    print(
        results_df[
            "expected_decision"
        ].value_counts()
    )

    # ======================================================
    # AGENT PERFORMANCE SCORECARD
    # ======================================================

    print("\n")
    print("=" * 70)
    print(
        "REVENUEOS-AI AGENT PERFORMANCE SCORECARD"
    )
    print("=" * 70)

    decision_accuracy_score = (
        accuracy
    )

    false_negative_score = max(
        0.0,
        100.0 - false_negative_rate
    )

    investigation_coverage_score = (
        investigation_coverage
    )

    investigation_quality = (
        investigation_quality_score
    )

    risk_score_component = (
        risk_weighted_score
    )

    # ------------------------------------------------------
    # WEIGHTED OVERALL SCORE
    # ------------------------------------------------------

    overall_agent_score = (

        decision_accuracy_score
        * 0.20

        +

        false_negative_score
        * 0.20

        +

        investigation_coverage_score
        * 0.20

        +

        investigation_quality
        * 0.20

        +

        risk_score_component
        * 0.20
    )

    print("\nComponent Scores:")
    print("-" * 70)

    print(
        f"Decision Accuracy:         "
        f"{decision_accuracy_score:.2f}%"
    )

    print(
        f"False Negative Safety:     "
        f"{false_negative_score:.2f}%"
    )

    print(
        f"Investigation Coverage:    "
        f"{investigation_coverage_score:.2f}%"
    )

    print(
        f"Investigation Quality:     "
        f"{investigation_quality:.2f}%"
    )

    print(
        f"Risk-Weighted Performance: "
        f"{risk_score_component:.2f}%"
    )

    print("\n")
    print("-" * 70)

    print(
        f"OVERALL AGENT SCORE: "
        f"{overall_agent_score:.2f}%"
    )

    # ======================================================
    # PERFORMANCE LEVEL
    # ======================================================

    if overall_agent_score >= 90:

        performance_level = (
            "EXCELLENT"
        )

    elif overall_agent_score >= 75:

        performance_level = (
            "GOOD"
        )

    elif overall_agent_score >= 60:

        performance_level = (
            "NEEDS IMPROVEMENT"
        )

    else:

        performance_level = (
            "POOR"
        )

    print(
        f"Performance Level: "
        f"{performance_level}"
    )

    print("=" * 70)

    # ======================================================
    # SAVE SCORECARD
    # ======================================================

    scorecard = pd.DataFrame([

        {
            "metric":
                "Decision Accuracy",

            "score":
                round(
                    decision_accuracy_score,
                    2
                )
        },

        {
            "metric":
                "False Negative Safety",

            "score":
                round(
                    false_negative_score,
                    2
                )
        },

        {
            "metric":
                "Investigation Coverage",

            "score":
                round(
                    investigation_coverage_score,
                    2
                )
        },

        {
            "metric":
                "Investigation Quality",

            "score":
                round(
                    investigation_quality,
                    2
                )
        },

        {
            "metric":
                "Risk Weighted Performance",

            "score":
                round(
                    risk_score_component,
                    2
                )
        },

        {
            "metric":
                "Overall Agent Score",

            "score":
                round(
                    overall_agent_score,
                    2
                )
        }
    ])

    try:

        scorecard.to_csv(
            SCORECARD_FILE,
            index=False
        )

        print(
            "\nAgent scorecard saved to:"
        )

        print(
            SCORECARD_FILE
        )

    except Exception as e:

        print(
            "\nERROR saving scorecard:"
        )

        print(
            f"{type(e).__name__}: {e}"
        )

    # ======================================================
    # SAVE DETAILED RESULTS
    # ======================================================

    try:

        results_df.to_csv(
            RESULTS_FILE,
            index=False
        )

        print("\nEvaluation results saved to:")

        print(
            RESULTS_FILE
        )

    except Exception as e:

        print(
            "\nERROR saving evaluation results:"
        )

        print(
            f"{type(e).__name__}: {e}"
        )

    # ======================================================
    # FINAL SUMMARY
    # ======================================================

    print("\n")
    print("=" * 70)
    print(
        "FINAL EVALUATION SUMMARY"
    )
    print("=" * 70)

    print(
        f"Decision Accuracy:         "
        f"{accuracy:.2f}%"
    )

    print(
        f"False Negative Rate:       "
        f"{false_negative_rate:.2f}%"
    )

    print(
        f"False Positive Rate:       "
        f"{false_positive_rate:.2f}%"
    )

    print(
        f"Investigation Coverage:    "
        f"{investigation_coverage:.2f}%"
    )

    print(
        f"Investigation Quality:     "
        f"{investigation_quality_score:.2f}%"
    )

    print(
        f"Risk-Weighted Score:       "
        f"{risk_weighted_score:.2f}%"
    )

    print(
        f"Overall Agent Score:       "
        f"{overall_agent_score:.2f}%"
    )

    print(
        f"Performance Level:         "
        f"{performance_level}"
    )

    print("=" * 70)

    print("\n")
    print("=" * 70)
    print(
        "EVALUATION COMPLETE"
    )
    print("=" * 70)

    return results_df


# ==========================================================
# SCRIPT ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    evaluate_system()