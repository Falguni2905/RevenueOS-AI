import pandas as pd

df = pd.read_csv(
    "data/processed/anomaly_results.csv"
)

df["failed_transaction_value"] = (
    df["total_transaction_value"]
    * df["failure_rate"]
)

# Illustrative assumption only
RECOVERY_RATE = 0.30

df["estimated_recoverable_value"] = (
    df["failed_transaction_value"]
    * RECOVERY_RATE
)

df["priority_score"] = (
    df["estimated_recoverable_value"]
    * (1 + df["failure_rate"])
)

df = df.sort_values(
    "priority_score",
    ascending=False
)

df.to_csv(
    "data/processed/merchant_priorities.csv",
    index=False
)

print(
    df[
        [
            "merchant_id",
            "failure_rate",
            "failed_transaction_value",
            "estimated_recoverable_value",
            "priority_score"
        ]
    ].head(10)
)