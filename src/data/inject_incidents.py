import pandas as pd
import random

random.seed(42)


# --------------------------------------------------
# Load transactions
# --------------------------------------------------

transactions = pd.read_csv(
    "data/raw/transactions.csv",
    parse_dates=["timestamp"]
)


# --------------------------------------------------
# Create ground-truth column
# --------------------------------------------------

transactions["is_injected_anomaly"] = 0

transactions["incident_type"] = None


# --------------------------------------------------
# Select merchants
# --------------------------------------------------

merchant_ids = (
    transactions["merchant_id"]
    .unique()
    .tolist()
)

random.shuffle(merchant_ids)


# --------------------------------------------------
# Incident 1
# Sudden failure spike
# --------------------------------------------------

incident_1_merchant = merchant_ids[0]

mask_1 = (
    transactions["merchant_id"]
    == incident_1_merchant
)

indices_1 = transactions[
    mask_1
].sample(
    frac=0.20,
    random_state=42
).index

transactions.loc[
    indices_1,
    "status"
] = "Failed"

transactions.loc[
    indices_1,
    "failure_reason"
] = "Network Error"

transactions.loc[
    indices_1,
    "is_injected_anomaly"
] = 1

transactions.loc[
    indices_1,
    "incident_type"
] = "Sudden Failure Spike"


# --------------------------------------------------
# Incident 2
# Payment method degradation
# --------------------------------------------------

incident_2_merchant = merchant_ids[1]

mask_2 = (
    transactions["merchant_id"]
    == incident_2_merchant
)

candidate_indices = transactions[
    mask_2
].index

if len(candidate_indices) > 0:

    indices_2 = transactions.loc[
        candidate_indices
    ].sample(
        frac=0.25,
        random_state=43
    ).index

    transactions.loc[
        indices_2,
        "status"
    ] = "Failed"

    transactions.loc[
        indices_2,
        "failure_reason"
    ] = "Bank Decline"

    transactions.loc[
        indices_2,
        "is_injected_anomaly"
    ] = 1

    transactions.loc[
        indices_2,
        "incident_type"
    ] = "Payment Method Degradation"


# --------------------------------------------------
# Incident 3
# Time-based incident
# --------------------------------------------------

incident_3_merchant = merchant_ids[2]

mask_3 = (
    (transactions["merchant_id"] == incident_3_merchant)
    &
    (transactions["timestamp"].dt.hour >= 18)
    &
    (transactions["timestamp"].dt.hour <= 21)
)

indices_3 = transactions[
    mask_3
].sample(
    frac=0.40,
    random_state=44
).index

transactions.loc[
    indices_3,
    "status"
] = "Failed"

transactions.loc[
    indices_3,
    "failure_reason"
] = "Payment Timeout"

transactions.loc[
    indices_3,
    "is_injected_anomaly"
] = 1

transactions.loc[
    indices_3,
    "incident_type"
] = "Time-Based Degradation"


# --------------------------------------------------
# Incident 4
# High-value merchant incident
# --------------------------------------------------

merchant_transaction_values = (
    transactions
    .groupby("merchant_id")["amount"]
    .sum()
    .sort_values(
        ascending=False
    )
)

incident_4_merchant = (
    merchant_transaction_values
    .index[0]
)

mask_4 = (
    transactions["merchant_id"]
    == incident_4_merchant
)

indices_4 = transactions[
    mask_4
].sample(
    frac=0.15,
    random_state=45
).index

transactions.loc[
    indices_4,
    "status"
] = "Failed"

transactions.loc[
    indices_4,
    "failure_reason"
] = "Technical Error"

transactions.loc[
    indices_4,
    "is_injected_anomaly"
] = 1

transactions.loc[
    indices_4,
    "incident_type"
] = "High Value Merchant Incident"


# --------------------------------------------------
# Save
# --------------------------------------------------

transactions.to_csv(
    "data/processed/transactions_with_incidents.csv",
    index=False
)


# --------------------------------------------------
# Output
# --------------------------------------------------

print("=" * 60)
print("INCIDENT INJECTION COMPLETE")
print("=" * 60)

print(
    "\nOriginal transactions:",
    len(transactions)
)

print(
    "\nInjected anomaly transactions:",
    transactions[
        "is_injected_anomaly"
    ].sum()
)

print(
    "\nIncident distribution:"
)

print(
    transactions[
        transactions["is_injected_anomaly"] == 1
    ]["incident_type"]
    .value_counts()
)

print(
    "\nIncident merchants:"
)

print(
    [
        incident_1_merchant,
        incident_2_merchant,
        incident_3_merchant,
        incident_4_merchant
    ]
)