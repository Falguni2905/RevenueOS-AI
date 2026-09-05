import pandas as pd

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score
)

df = pd.read_csv(
    "data/processed/anomaly_results.csv"
)

y_true = df["has_injected_incident"]
y_pred = df["predicted_anomaly"]

precision = precision_score(
    y_true,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_true,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_true,
    y_pred,
    zero_division=0
)

print("=" * 60)
print("MODEL EVALUATION")
print("=" * 60)

print("\nPrecision:", round(precision, 3))
print("Recall:", round(recall, 3))
print("F1:", round(f1, 3))

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_true,
        y_pred
    )
)

print("\nClassification Report:")

print(
    classification_report(
        y_true,
        y_pred,
        zero_division=0
    )
)