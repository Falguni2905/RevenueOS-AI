import pandas as pd


TRANSACTION_FILE = "data/raw/transactions.csv"
MERCHANT_FILE = "data/raw/merchants.csv"


def load_transactions():

    return pd.read_csv(
        TRANSACTION_FILE,
        parse_dates=["timestamp"]
    )


def load_merchants():

    return pd.read_csv(
        MERCHANT_FILE
    )


# ============================================================
# TOOL 1 — MERCHANT PROFILE
# ============================================================

def merchant_profile(merchant_id):

    merchants = load_merchants()

    merchant = merchants[
        merchants["merchant_id"] == merchant_id
    ]

    if merchant.empty:

        return {
            "success": False,
            "error": "Merchant not found."
        }

    merchant = merchant.iloc[0]

    return {
        "success": True,
        "merchant_id": merchant_id,
        "merchant_category": merchant["merchant_category"],
        "merchant_size": merchant["merchant_size"],
        "average_transaction_value": merchant[
            "avg_transaction_value"
        ],
        "monthly_transaction_volume": merchant[
            "monthly_transaction_volume"
        ],
        "baseline_success_rate": merchant[
            "baseline_success_rate"
        ],
        "primary_payment_method": merchant[
            "primary_payment_method"
        ],
        "geography": merchant["geography"],
        "subscription_enabled": merchant[
            "subscription_enabled"
        ]
    }


# ============================================================
# TOOL 2 — FAILURE ANALYSIS
# ============================================================

def failure_analysis(merchant_id):

    transactions = load_transactions()

    merchant_transactions = transactions[
        transactions["merchant_id"] == merchant_id
    ]

    if merchant_transactions.empty:

        return {
            "success": False,
            "error": "No transactions found."
        }

    failed = merchant_transactions[
        merchant_transactions["status"] == "Failed"
    ]

    total_transactions = len(
        merchant_transactions
    )

    failed_transactions = len(
        failed
    )

    failure_rate = (
        failed_transactions /
        total_transactions
    )

    if failed.empty:

        return {
            "success": True,
            "merchant_id": merchant_id,
            "total_transactions": total_transactions,
            "failed_transactions": 0,
            "failure_rate": 0,
            "dominant_failure_reason": None,
            "failure_breakdown": {}
        }

    failure_breakdown = (
        failed["failure_reason"]
        .value_counts()
        .to_dict()
    )

    dominant_failure = (
        failed["failure_reason"]
        .value_counts()
        .idxmax()
    )

    return {
        "success": True,
        "merchant_id": merchant_id,
        "total_transactions": total_transactions,
        "failed_transactions": failed_transactions,
        "failure_rate": round(
            failure_rate,
            4
        ),
        "dominant_failure_reason": dominant_failure,
        "failure_breakdown": failure_breakdown
    }


# ============================================================
# TOOL 3 — PAYMENT METHOD ANALYSIS
# ============================================================

def payment_method_analysis(merchant_id):

    transactions = load_transactions()

    merchant_transactions = transactions[
        transactions["merchant_id"] == merchant_id
    ]

    if merchant_transactions.empty:

        return {
            "success": False,
            "error": "No transactions found."
        }

    analysis = (
        merchant_transactions
        .groupby("payment_method")
        .agg(
            transactions=("transaction_id", "count"),
            failures=("status", lambda x:
                      (x == "Failed").sum())
        )
    )

    analysis["failure_rate"] = (
        analysis["failures"] /
        analysis["transactions"]
    )

    analysis = (
        analysis
        .sort_values(
            "failure_rate",
            ascending=False
        )
    )

    return {
        "success": True,
        "merchant_id": merchant_id,
        "payment_method_analysis":
            analysis.reset_index().to_dict(
                orient="records"
            )
    }


# ============================================================
# TOOL 4 — HOURLY ANALYSIS
# ============================================================

def hourly_analysis(merchant_id):

    transactions = load_transactions()

    merchant_transactions = transactions[
        transactions["merchant_id"] == merchant_id
    ].copy()

    if merchant_transactions.empty:

        return {
            "success": False,
            "error": "No transactions found."
        }

    merchant_transactions["hour"] = (
        merchant_transactions["timestamp"]
        .dt.hour
    )

    hourly = (
        merchant_transactions
        .groupby("hour")
        .agg(
            transactions=("transaction_id", "count"),
            failures=("status", lambda x:
                      (x == "Failed").sum())
        )
    )

    hourly["failure_rate"] = (
        hourly["failures"] /
        hourly["transactions"]
    )

    hourly = (
        hourly
        .sort_values(
            "failure_rate",
            ascending=False
        )
    )

    return {
        "success": True,
        "merchant_id": merchant_id,
        "hourly_analysis":
            hourly.reset_index().to_dict(
                orient="records"
            )
    }


# ============================================================
# TOOL 5 — TRANSACTION ANALYSIS
# ============================================================

def transaction_analysis(merchant_id):

    transactions = load_transactions()

    merchant_transactions = transactions[
        transactions["merchant_id"] == merchant_id
    ]

    if merchant_transactions.empty:

        return {
            "success": False,
            "error": "No transactions found."
        }

    top_transactions = (
        merchant_transactions
        .sort_values(
            "amount",
            ascending=False
        )
        .head(10)
    )

    return {
        "success": True,
        "merchant_id": merchant_id,
        "highest_value_transactions":
            top_transactions[
                [
                    "transaction_id",
                    "timestamp",
                    "amount",
                    "payment_method",
                    "status",
                    "failure_reason"
                ]
            ].to_dict(
                orient="records"
            )
    }