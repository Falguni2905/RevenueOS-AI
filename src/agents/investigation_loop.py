from src.agents.agent_state import (
    InvestigationState
)

from src.agents.tool_selector import (
    select_tools
)

from src.tools.tool_registry import (
    execute_tool
)

from src.agents.evidence_analyzer import (
    analyze_evidence
)

from src.agents.confidence_scorer import (
    calculate_confidence
)

def run_investigation(
    merchant_id,
    risk_score,
    risk_category,
    failure_rate
):

    # ========================================================
    # CREATE AGENT STATE
    # ========================================================

    state = InvestigationState(
        merchant_id=merchant_id,
        risk_score=risk_score,
        risk_category=risk_category,
        failure_rate=failure_rate
    )

    # ========================================================
    # SELECT TOOLS
    # ========================================================

    selected_tools = select_tools(
        risk_score,
        failure_rate
    )

    print("\n")
    print("=" * 70)
    print("INVESTIGATION AGENT")
    print("=" * 70)

    print(
        f"\nMerchant: {merchant_id}"
    )

    print(
        f"Risk Score: {risk_score}"
    )

    print(
        f"Risk Category: {risk_category}"
    )

    print(
        f"Failure Rate: {failure_rate:.2%}"
    )

    print("\nSelected Tools:")

    for tool in selected_tools:

        print(
            f"  → {tool}"
        )

    # ========================================================
    # EXECUTE TOOLS
    # ========================================================

    for tool_name in selected_tools:

        print("\n")
        print(
            "-" * 70
        )

        print(
            f"EXECUTING TOOL: {tool_name}"
        )

        print(
            "-" * 70
        )

        result = execute_tool(
            tool_name,
            merchant_id
        )

        # Store result in agent state
        state.add_evidence(
            tool_name,
            result
        )

        print(
            "Tool completed successfully."
        )

    # ========================================================
    # UPDATE STATE
    # ========================================================

    # ========================================================
# ANALYZE EVIDENCE
# ========================================================

    findings = analyze_evidence(
    state
)

# ========================================================
# CALCULATE CONFIDENCE
# ========================================================

    confidence = calculate_confidence(
    state,
    findings
)

    state.confidence = confidence

    state.status = "EVIDENCE_ANALYZED"

    return state