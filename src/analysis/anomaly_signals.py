import pandas as pd


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(
    "data/processed/merchant_analysis.csv"
)


# ============================================================
# CALCULATE FAILURE RATE Z-SCORE
# ============================================================

failure_mean = df["failure_rate"].mean()

failure_std = df["failure_rate"].std()

df["failure_rate_zscore"] = (
    df["failure_rate"]
    -
    failure_mean
) / failure_std


# ============================================================
# CALCULATE VOLUME Z-SCORE
# ============================================================

volume_mean = (
    df["transaction_count"].mean()
)

volume_std = (
    df["transaction_count"].std()
)

df["transaction_volume_zscore"] = (
    df["transaction_count"]
    -
    volume_mean
) / volume_std


# ============================================================
# CALCULATE VALUE Z-SCORE
# ============================================================

value_mean = (
    df["total_transaction_value"].mean()
)

value_std = (
    df["total_transaction_value"].std()
)

df["transaction_value_zscore"] = (
    df["total_transaction_value"]
    -
    value_mean
) / value_std


# ============================================================
# ANOMALY SCORE
# ============================================================

df["anomaly_score"] = (

    abs(
        df["failure_rate_zscore"]
    )
    * 0.60

    +

    abs(
        df["transaction_volume_zscore"]
    )
    * 0.20

    +

    abs(
        df["transaction_value_zscore"]
    )
    * 0.20
)


# ============================================================
# RANK MERCHANTS
# ============================================================

df = df.sort_values(
    "anomaly_score",
    ascending=False
)


# ============================================================
# DISPLAY
# ============================================================

print("\n")
print("=" * 70)
print("TOP MERCHANT ANOMALIES")
print("=" * 70)

print(
    df[
        [
            "merchant_id",
            "merchant_type",
            "failure_rate",
            "failed_transactions",
            "transaction_count",
            "anomaly_score"
        ]
    ]
    .head(15)
    .to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    "data/processed/merchant_anomaly_scores.csv",
    index=False
)

print(
    "\nAnomaly scores saved successfully."
)