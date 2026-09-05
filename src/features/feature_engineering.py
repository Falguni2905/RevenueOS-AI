import pandas as pd


# --------------------------------------------------
# Load transactions
# --------------------------------------------------

transactions = pd.read_csv(
    "data/raw/transactions.csv",
    parse_dates=["timestamp"]
)


# --------------------------------------------------
# Create basic transaction features
# --------------------------------------------------

transactions["is_failed"] = (
    transactions["status"] == "Failed"
).astype(int)

transactions["date"] = (
    transactions["timestamp"].dt.date
)

transactions["hour"] = (
    transactions["timestamp"].dt.hour
)

transactions["day_of_week"] = (
    transactions["timestamp"].dt.dayofweek
)

transactions["month"] = (
    transactions["timestamp"].dt.month
)


# --------------------------------------------------
# Merchant-level aggregation
# --------------------------------------------------

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
        )
    )
    .reset_index()
)


# --------------------------------------------------
# Calculate failure rate
# --------------------------------------------------

merchant_features["failure_rate"] = (
    merchant_features["failed_transactions"]
    /
    merchant_features["transaction_count"]
)


# --------------------------------------------------
# Calculate success rate
# --------------------------------------------------

merchant_features["success_rate"] = (
    1 -
    merchant_features["failure_rate"]
)


# --------------------------------------------------
# Add merchant information
# --------------------------------------------------

merchant_info = pd.read_csv(
    "data/raw/merchants.csv"
)

merchant_features = merchant_features.merge(
    merchant_info,
    on="merchant_id",
    how="left"
)


# --------------------------------------------------
# Save
# --------------------------------------------------

merchant_features.to_csv(
    "data/processed/merchant_features.csv",
    index=False
)


# --------------------------------------------------
# Output
# --------------------------------------------------

print("=" * 50)
print("MERCHANT FEATURE ENGINEERING")
print("=" * 50)

print(
    "\nShape:",
    merchant_features.shape
)

print(
    "\nColumns:"
)

print(
    merchant_features.columns.tolist()
)

print(
    "\nFirst 5 merchants:"
)

print(
    merchant_features.head()
)

print("\nTop 10 merchants by failure rate:")

print(
    merchant_features[
        [
            "merchant_id",
            "transaction_count",
            "failure_rate",
            "failed_transactions",
            "total_transaction_value"
        ]
    ]
    .sort_values(
        "failure_rate",
        ascending=False
    )
    .head(10)
)