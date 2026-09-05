import pandas as pd

df = pd.read_csv(
    "data/processed/merchant_features.csv"
)


# Failure component
failure_score = (
    df["failure_rate"] * 100
)


# Volume component
volume_score = (
    df["transaction_count"]
    /
    df["transaction_count"].max()
    * 100
)


# Revenue exposure
revenue_score = (
    df["total_transaction_value"]
    /
    df["total_transaction_value"].max()
    * 100
)


# Overall risk score
df["merchant_risk_score"] = (
    0.50 * failure_score
    +
    0.20 * volume_score
    +
    0.30 * revenue_score
)


# Risk category
def classify_risk(score):

    if score >= 60:
        return "High"

    elif score >= 30:
        return "Medium"

    else:
        return "Low"


df["risk_category"] = (
    df["merchant_risk_score"]
    .apply(classify_risk)
)


df.to_csv(
    "data/processed/merchant_health.csv",
    index=False
)


print(
    df[
        [
            "merchant_id",
            "failure_rate",
            "transaction_count",
            "total_transaction_value",
            "merchant_risk_score",
            "risk_category"
        ]
    ]
    .sort_values(
        "merchant_risk_score",
        ascending=False
    )
    .head(10)
)