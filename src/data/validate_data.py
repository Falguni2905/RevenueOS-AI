import pandas as pd

# Load datasets
merchants = pd.read_csv(
    "data/raw/merchants.csv"
)

transactions = pd.read_csv(
    "data/raw/transactions.csv"
)

print("=" * 50)
print("DATASET VALIDATION")
print("=" * 50)

# --------------------------------------------------
# 1. Dataset dimensions
# --------------------------------------------------

print("\n1. DATASET SHAPES")

print("Merchants:", merchants.shape)
print("Transactions:", transactions.shape)


# --------------------------------------------------
# 2. Unique IDs
# --------------------------------------------------

print("\n2. UNIQUE IDs")

print(
    "Unique merchant IDs:",
    merchants["merchant_id"].nunique()
)

print(
    "Unique transaction IDs:",
    transactions["transaction_id"].nunique()
)

print(
    "Unique merchants in transactions:",
    transactions["merchant_id"].nunique()
)


# --------------------------------------------------
# 3. Duplicate transactions
# --------------------------------------------------

print("\n3. DUPLICATE TRANSACTIONS")

duplicate_transactions = (
    transactions["transaction_id"]
    .duplicated()
    .sum()
)

print(
    "Duplicate transaction IDs:",
    duplicate_transactions
)


# --------------------------------------------------
# 4. Invalid merchant IDs
# --------------------------------------------------

print("\n4. MERCHANT ID VALIDATION")

invalid_merchant_ids = set(
    transactions["merchant_id"]
) - set(
    merchants["merchant_id"]
)

print(
    "Invalid merchant IDs:",
    len(invalid_merchant_ids)
)


# --------------------------------------------------
# 5. Missing values
# --------------------------------------------------

print("\n5. MISSING VALUES")

print(
    transactions.isnull().sum()
)


# --------------------------------------------------
# 6. Negative / zero transaction amounts
# --------------------------------------------------

print("\n6. TRANSACTION AMOUNT VALIDATION")

invalid_amounts = (
    transactions["amount"] <= 0
).sum()

print(
    "Zero or negative amounts:",
    invalid_amounts
)


# --------------------------------------------------
# 7. Status validation
# --------------------------------------------------

print("\n7. STATUS VALIDATION")

print(
    transactions["status"]
    .value_counts()
)


# --------------------------------------------------
# 8. Failure reason validation
# --------------------------------------------------

print("\n8. FAILURE REASON VALIDATION")

failed_without_reason = (
    transactions[
        transactions["status"] == "Failed"
    ]["failure_reason"]
    .isna()
    .sum()
)

success_with_reason = (
    transactions[
        transactions["status"] == "Success"
    ]["failure_reason"]
    .notna()
    .sum()
)

print(
    "Failed transactions without reason:",
    failed_without_reason
)

print(
    "Successful transactions with failure reason:",
    success_with_reason
)




print("\n" + "=" * 50)
print("VALIDATION COMPLETE")
print("=" * 50)