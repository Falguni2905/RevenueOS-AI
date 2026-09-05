import pandas as pd


# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(
    "data/processed/merchant_anomaly_scores.csv"
)


# ============================================================
# NORMALIZE ANOMALY SCORE TO 0-100
# ============================================================

min_score = df["anomaly_score"].min()

max_score = df["anomaly_score"].max()

if max_score == min_score:

    df["risk_score"] = 0

else:

    df["risk_score"] = (
        (
            df["anomaly_score"]
            -
            min_score
        )
        /
        (
            max_score
            -
            min_score
        )
        * 100
    )


df["risk_score"] = (
    df["risk_score"]
    .round(2)
)


# ============================================================
# RISK CATEGORY
# ============================================================

def classify_risk(score):

    if score >= 80:
        return "Critical"

    elif score >= 60:
        return "High"

    elif score >= 30:
        return "Medium"

    else:
        return "Low"


df["risk_category"] = (
    df["risk_score"]
    .apply(classify_risk)
)


# ============================================================
# DISPLAY
# ============================================================

print("\n")
print("=" * 70)
print("MERCHANT RISK SCORING")
print("=" * 70)

print(
    df[
        [
            "merchant_id",
            "merchant_type",
            "failure_rate",
            "risk_score",
            "risk_category"
        ]
    ]
    .sort_values(
        "risk_score",
        ascending=False
    )
    .head(20)
    .to_string(index=False)
)


# ============================================================
# RISK DISTRIBUTION
# ============================================================

print("\nRisk Category Distribution:")

print(
    df["risk_category"]
    .value_counts()
)


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    "data/processed/merchant_risk_scores.csv",
    index=False
)

print(
    "\nRisk scoring completed successfully."
)