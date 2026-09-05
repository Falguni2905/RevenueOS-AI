import pandas as pd


transactions = pd.read_csv(
    "data/processed/transactions_with_incidents.csv",
    parse_dates=["timestamp"]
)

merchants = pd.read_csv(
    "data/raw/merchants.csv"
)


def get_merchant_summary(merchant_id):

    df = transactions[
        transactions["merchant_id"] == merchant_id
    ]

    if len(df) == 0:
        return None

    return {
        "merchant_id": merchant_id,
        "transaction_count": len(df),
        "total_value": round(
            df["amount"].sum(),
            2
        ),
        "failed_transactions": int(
            (df["status"] == "Failed").sum()
        ),
        "failure_rate": round(
            (df["status"] == "Failed").mean(),
            4
        )
    }


def get_failure_breakdown(merchant_id):

    df = transactions[
        (transactions["merchant_id"] == merchant_id)
        &
        (transactions["status"] == "Failed")
    ]

    return (
        df["failure_reason"]
        .value_counts()
        .to_dict()
    )


def get_payment_method_breakdown(merchant_id):

    df = transactions[
        transactions["merchant_id"] == merchant_id
    ]

    result = (
        df.groupby("payment_method")
        .agg(
            transactions=("transaction_id", "count"),
            failures=(
                "status",
                lambda x: (x == "Failed").sum()
            )
        )
        .reset_index()
    )

    result["failure_rate"] = (
        result["failures"]
        /
        result["transactions"]
    )

    return result.to_dict(
        orient="records"
    )


def get_hourly_failure_pattern(merchant_id):

    df = transactions[
        transactions["merchant_id"] == merchant_id
    ].copy()

    df["hour"] = df["timestamp"].dt.hour

    result = (
        df.groupby("hour")
        .agg(
            transactions=("transaction_id", "count"),
            failures=(
                "status",
                lambda x: (x == "Failed").sum()
            )
        )
        .reset_index()
    )

    result["failure_rate"] = (
        result["failures"]
        /
        result["transactions"]
    )

    return result.to_dict(
        orient="records"
    )


def get_merchant_profile(merchant_id):

    merchant = merchants[
        merchants["merchant_id"] == merchant_id
    ]

    if merchant.empty:
        return None

    return merchant.iloc[0].to_dict()