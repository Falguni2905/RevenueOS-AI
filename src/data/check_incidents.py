import pandas as pd

df = pd.read_csv(
    "data/processed/transactions_with_incidents.csv"
)

print("Shape:", df.shape)

print("\nGround-truth anomalies:")

print(
    df["is_injected_anomaly"]
    .value_counts()
)

print("\nIncident types:")

print(
    df[
        df["is_injected_anomaly"] == 1
    ]["incident_type"]
    .value_counts()
)

print("\nIncident merchants:")

print(
    df[
        df["is_injected_anomaly"] == 1
    ]["merchant_id"]
    .unique()
)