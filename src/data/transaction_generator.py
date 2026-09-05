import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

# Load merchants
merchants_df = pd.read_csv(
    "data/raw/merchants.csv"
)

print("Merchant dataset loaded.")
print("Number of merchants:", len(merchants_df))

# Configuration
NUM_TRANSACTIONS = 10000

transaction_statuses = [
    "Success",
    "Failed"
]

failure_reasons = [
    "Insufficient Funds",
    "Bank Decline",
    "Network Error",
    "Authentication Failure",
    "Payment Timeout",
    "Technical Error"
]

# Date range
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)


def random_timestamp(start_date, end_date):

    time_difference = end_date - start_date

    random_seconds = random.randint(
        0,
        int(time_difference.total_seconds())
    )

    return start_date + timedelta(
        seconds=random_seconds
    )


# Generate transactions
transactions = []

for i in range(1, NUM_TRANSACTIONS + 1):

    merchant = merchants_df.sample(
        n=1
    ).iloc[0]

    transaction_id = f"T{i:08d}"

    timestamp = random_timestamp(
        start_date,
        end_date
    )

    avg_value = merchant[
        "avg_transaction_value"
    ]

    amount = random.gauss(
        avg_value,
        avg_value * 0.30
    )

    amount = max(
        1,
        round(amount, 2)
    )

    payment_method = merchant[
        "primary_payment_method"
    ]

    success_probability = merchant[
        "baseline_success_rate"
    ]

    is_successful = (
        random.random()
        < success_probability
    )

    if is_successful:
        status = "Success"
    else:
        status = "Failed"

    if status == "Failed":

        failure_reason = random.choice(
            failure_reasons
        )

    else:

        failure_reason = None

    transaction = {
        "transaction_id": transaction_id,
        "merchant_id": merchant["merchant_id"],
        "timestamp": timestamp,
        "amount": amount,
        "merchant_category": merchant["merchant_category"],
        "merchant_size": merchant["merchant_size"],
        "payment_method": payment_method,
        "status": status,
        "failure_reason": failure_reason
    }

    transactions.append(transaction)


# Create DataFrame
transactions_df = pd.DataFrame(
    transactions
)

print("\nTransaction dataset created.")
print("Shape:", transactions_df.shape)


# Validation
print("\nTransaction status distribution:")
print(
    transactions_df["status"]
    .value_counts()
)

print("\nTransaction status percentage:")
print(
    transactions_df["status"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print("\nFailure reason distribution:")
print(
    transactions_df[
        transactions_df["status"] == "Failed"
    ]["failure_reason"]
    .value_counts()
)


# Save
transactions_df.to_csv(
    "data/raw/transactions.csv",
    index=False
)

print(
    "\nTransaction dataset saved successfully."
)