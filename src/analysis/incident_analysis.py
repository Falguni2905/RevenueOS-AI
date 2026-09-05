import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

TRANSACTIONS_FILE = "data/raw/transactions.csv"
MERCHANTS_FILE = "data/raw/merchants.csv"

INCIDENT_MERCHANTS = [
    "M00008",
    "M00028",
    "M00005",
    "M00003"
]


# ============================================================
# LOAD DATA
# ============================================================

transactions_df = pd.read_csv(
    TRANSACTIONS_FILE
)

merchants_df = pd.read_csv(
    MERCHANTS_FILE
)


# ============================================================
# MERCHANT-LEVEL AGGREGATION
# ============================================================

merchant_analysis = (
    transactions_df
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

        failed_transactions=(
            "status",
            lambda x: (
                x == "Failed"
            ).sum()
        ),

        successful_transactions=(
            "status",
            lambda x: (
                x == "Success"
            ).sum()
        )
    )
    .reset_index()
)


# ============================================================
# FAILURE RATE
# ============================================================

merchant_analysis["failure_rate"] = (
    merchant_analysis["failed_transactions"]
    /
    merchant_analysis["transaction_count"]
)


# ============================================================
# INCIDENT LABEL
# ============================================================

merchant_analysis["merchant_type"] = (
    merchant_analysis["merchant_id"]
    .apply(
        lambda x:
        "Incident"
        if x in INCIDENT_MERCHANTS
        else "Normal"
    )
)


# ============================================================
# MERGE MERCHANT ATTRIBUTES
# ============================================================

merchant_analysis = merchant_analysis.merge(
    merchants_df,
    on="merchant_id",
    how="left"
)


# ============================================================
# INCIDENT MERCHANTS
# ============================================================

incident_df = merchant_analysis[
    merchant_analysis["merchant_type"]
    == "Incident"
]


# ============================================================
# NORMAL MERCHANTS
# ============================================================

normal_df = merchant_analysis[
    merchant_analysis["merchant_type"]
    == "Normal"
]


# ============================================================
# COMPARISON
# ============================================================

comparison = pd.DataFrame({

    "Metric": [

        "Average Failure Rate",

        "Average Failed Transactions",

        "Average Transaction Count",

        "Average Transaction Value",

        "Average Monthly Transaction Volume",

        "Average Baseline Success Rate",

        "Average Transaction Value per Transaction"
    ],

    "Incident Merchants": [

        incident_df["failure_rate"].mean(),

        incident_df["failed_transactions"].mean(),

        incident_df["transaction_count"].mean(),

        incident_df[
            "total_transaction_value"
        ].mean(),

        incident_df[
            "monthly_transaction_volume"
        ].mean(),

        incident_df[
            "baseline_success_rate"
        ].mean(),

        (
            incident_df[
                "total_transaction_value"
            ]
            /
            incident_df[
                "transaction_count"
            ]
        ).mean()
    ],

    "Normal Merchants": [

        normal_df["failure_rate"].mean(),

        normal_df["failed_transactions"].mean(),

        normal_df["transaction_count"].mean(),

        normal_df[
            "total_transaction_value"
        ].mean(),

        normal_df[
            "monthly_transaction_volume"
        ].mean(),

        normal_df[
            "baseline_success_rate"
        ].mean(),

        (
            normal_df[
                "total_transaction_value"
            ]
            /
            normal_df[
                "transaction_count"
            ]
        ).mean()
    ]
})


# ============================================================
# DIFFERENCE %
# ============================================================

comparison["Difference %"] = (
    (
        comparison["Incident Merchants"]
        -
        comparison["Normal Merchants"]
    )
    /
    comparison["Normal Merchants"]
    * 100
)


# ============================================================
# DISPLAY
# ============================================================

print("\n")
print("=" * 70)
print("INCIDENT VS NORMAL MERCHANT ANALYSIS")
print("=" * 70)

print("\nIncident Merchants:")
print(
    incident_df[
        [
            "merchant_id",
            "failure_rate",
            "failed_transactions",
            "transaction_count",
            "total_transaction_value",
            "merchant_category",
            "merchant_size"
        ]
    ]
    .sort_values(
        "failure_rate",
        ascending=False
    )
    .to_string(index=False)
)


print("\n")
print("Average Comparison:")

print(
    comparison.to_string(
        index=False
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

comparison.to_csv(
    "data/processed/incident_vs_normal.csv",
    index=False
)

merchant_analysis.to_csv(
    "data/processed/merchant_analysis.csv",
    index=False
)

print("\nAnalysis files saved successfully.")