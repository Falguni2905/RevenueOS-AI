def calculate_confidence(state, findings):
    """
    Calculate investigation confidence using
    deterministic evidence-based rules.

    Returns a score from 0 to 100.
    """

    score = 0

    # ========================================================
    # 1. BASE SCORE
    # ========================================================

    if state.risk_score >= 80:
        score += 20

    elif state.risk_score >= 60:
        score += 15

    elif state.risk_score >= 30:
        score += 10

    # ========================================================
    # 2. FAILURE ANALYSIS
    # ========================================================

    if "failure_analysis" in state.evidence:

        score += 20

    # ========================================================
    # 3. MERCHANT PROFILE
    # ========================================================

    if "merchant_profile" in state.evidence:

        score += 10

    # ========================================================
    # 4. PAYMENT METHOD EVIDENCE
    # ========================================================

    if "payment_method_analysis" in state.evidence:

        score += 15

    # ========================================================
    # 5. TIME-BASED EVIDENCE
    # ========================================================

    if "hourly_analysis" in state.evidence:

        score += 15

    # ========================================================
    # 6. TRANSACTION-LEVEL EVIDENCE
    # ========================================================

    if "transaction_analysis" in state.evidence:

        score += 10

    # ========================================================
    # 7. FINDINGS
    # ========================================================

    finding_count = len(findings)

    if finding_count >= 3:

        score += 10

    elif finding_count == 2:

        score += 7

    elif finding_count == 1:

        score += 4

    # ========================================================
    # CAP SCORE
    # ========================================================

    score = min(
        score,
        100
    )

    # ========================================================
    # CONFIDENCE CATEGORY
    # ========================================================

    if score >= 80:

        category = "HIGH"

    elif score >= 60:

        category = "MEDIUM"

    else:

        category = "LOW"

    return {
        "score": score,
        "category": category,
        "finding_count": finding_count
    }