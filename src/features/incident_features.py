import pandas as pd

# Load transactions with incidents
transactions = pd.read_csv(
    "data/processed/transactions_with_incidents.csv",
    parse_dates=["timestamp"]
)

# Create failure indicator
transactions["is_failed"] = (
    transactions["status"] == "Failed"
).astype(int)

# Merchant-level aggregation
merchant_features = (
    transactions
    .groupby("merchant_id")
    .agg(
        transaction_count=(
            "transaction_id",
            "count"
        ),

        total_transaction_value=(
            "amount",
            "sum"
        ),

        average_transaction_value=(
            "amount",
            "mean"
        ),

        failed_transactions=(
            "is_failed",
            "sum"
        ),

        injected_anomaly_count=(
            "is_injected_anomaly",
            "sum"
        )
    )
    .reset_index()
)

# Failure rate
merchant_features["failure_rate"] = (
    merchant_features["failed_transactions"]
    /
    merchant_features["transaction_count"]
)

# Success rate
merchant_features["success_rate"] = (
    1 -
    merchant_features["failure_rate"]
)

# Ground-truth incident flag
merchant_features["has_injected_incident"] = (
    merchant_features["injected_anomaly_count"] > 0
).astype(int)

# Save
merchant_features.to_csv(
    "data/processed/merchant_incident_features.csv",
    index=False
)

# Display results
print("=" * 60)
print("INCIDENT FEATURE ENGINEERING")
print("=" * 60)

print("\nShape:")
print(merchant_features.shape)

print("\nMerchants with injected incidents:")

print(
    merchant_features[
        merchant_features["has_injected_incident"] == 1
    ][
        [
            "merchant_id",
            "transaction_count",
            "failed_transactions",
            "failure_rate",
            "injected_anomaly_count"
        ]
    ]
)