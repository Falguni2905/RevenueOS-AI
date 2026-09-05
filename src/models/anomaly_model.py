import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

df = pd.read_csv(
    "data/processed/merchant_incident_features.csv"
)

features = [
    "transaction_count",
    "total_transaction_value",
    "average_transaction_value",
    "failed_transactions",
    "failure_rate"
]

X = df[features]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = IsolationForest(
    n_estimators=200,
    contamination=0.10,
    random_state=42
)

df["anomaly_prediction"] = model.fit_predict(X_scaled)

df["anomaly_score"] = model.decision_function(X_scaled)

df["predicted_anomaly"] = (
    df["anomaly_prediction"] == -1
).astype(int)

df.to_csv(
    "data/processed/anomaly_results.csv",
    index=False
)

print("=" * 60)
print("ANOMALY DETECTION")
print("=" * 60)

print("\nPredicted anomalies:")
print(
    df["predicted_anomaly"].value_counts()
)

print("\nKnown incident merchants:")

print(
    df[
        df["has_injected_incident"] == 1
    ][
        [
            "merchant_id",
            "failure_rate",
            "predicted_anomaly",
            "anomaly_score"
        ]
    ]
)