import pandas as pd
import random

random.seed(42)

merchant_categories = [
    "Education",
    "E-commerce",
    "SaaS",
    "Travel",
    "Healthcare",
    "Food Delivery",
    "Gaming",
    "Professional Services",
    "Media",
    "Retail"
]

category_weights = [
    0.08,  # Education
    0.18,  # E-commerce
    0.10,  # SaaS
    0.06,  # Travel
    0.08,  # Healthcare
    0.15,  # Food Delivery
    0.08,  # Gaming
    0.10,  # Professional Services
    0.05,  # Media
    0.12   # Retail
]

merchant_sizes = [
    "Small",
    "Medium",
    "Large"
]

size_weights = [
    0.60,  # Small
    0.30,  # Medium
    0.10   # Large
]

geographies = [
    "North",
    "South",
    "East",
    "West",
    "Central"
]

payment_methods = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "Wallet"
]

payment_method_weights = {
    "Education": {
        "UPI": 0.35,
        "Credit Card": 0.20,
        "Debit Card": 0.15,
        "Net Banking": 0.20,
        "Wallet": 0.10
    },

    "E-commerce": {
        "UPI": 0.40,
        "Credit Card": 0.20,
        "Debit Card": 0.20,
        "Net Banking": 0.05,
        "Wallet": 0.15
    },

    "SaaS": {
        "UPI": 0.15,
        "Credit Card": 0.40,
        "Debit Card": 0.10,
        "Net Banking": 0.25,
        "Wallet": 0.10
    },

    "Travel": {
        "UPI": 0.15,
        "Credit Card": 0.35,
        "Debit Card": 0.10,
        "Net Banking": 0.30,
        "Wallet": 0.10
    },

    "Healthcare": {
        "UPI": 0.30,
        "Credit Card": 0.20,
        "Debit Card": 0.15,
        "Net Banking": 0.25,
        "Wallet": 0.10
    },

    "Food Delivery": {
        "UPI": 0.45,
        "Credit Card": 0.15,
        "Debit Card": 0.15,
        "Net Banking": 0.05,
        "Wallet": 0.20
    },

    "Gaming": {
        "UPI": 0.40,
        "Credit Card": 0.20,
        "Debit Card": 0.15,
        "Net Banking": 0.05,
        "Wallet": 0.20
    },

    "Professional Services": {
        "UPI": 0.20,
        "Credit Card": 0.30,
        "Debit Card": 0.10,
        "Net Banking": 0.30,
        "Wallet": 0.10
    },

    "Media": {
        "UPI": 0.30,
        "Credit Card": 0.25,
        "Debit Card": 0.10,
        "Net Banking": 0.20,
        "Wallet": 0.15
    },

    "Retail": {
        "UPI": 0.40,
        "Credit Card": 0.15,
        "Debit Card": 0.25,
        "Net Banking": 0.05,
        "Wallet": 0.15
    }
}

category_profiles = {
    "Education": {
        "avg_transaction_range": (1000, 8000),
        "subscription_probability": 0.60
    },
    "E-commerce": {
        "avg_transaction_range": (500, 5000),
        "subscription_probability": 0.10
    },
    "SaaS": {
        "avg_transaction_range": (3000, 15000),
        "subscription_probability": 0.85
    },
    "Travel": {
        "avg_transaction_range": (5000, 30000),
        "subscription_probability": 0.05
    },
    "Healthcare": {
        "avg_transaction_range": (1000, 10000),
        "subscription_probability": 0.20
    },
    "Food Delivery": {
        "avg_transaction_range": (200, 1500),
        "subscription_probability": 0.15
    },
    "Gaming": {
        "avg_transaction_range": (100, 3000),
        "subscription_probability": 0.30
    },
    "Professional Services": {
        "avg_transaction_range": (3000, 20000),
        "subscription_probability": 0.25
    },
    "Media": {
        "avg_transaction_range": (200, 3000),
        "subscription_probability": 0.50
    },
    "Retail": {
        "avg_transaction_range": (500, 5000),
        "subscription_probability": 0.05
    }
}


size_profiles = {
    "Small": {
        "volume_range": (500, 3000)
    },
    "Medium": {
        "volume_range": (3000, 15000)
    },
    "Large": {
        "volume_range": (15000, 100000)
    }
}


payment_success_rates = {
    "UPI": 0.96,
    "Credit Card": 0.94,
    "Debit Card": 0.93,
    "Net Banking": 0.92,
    "Wallet": 0.95
}

merchants = []

for i in range(1, 101):

    merchant_id = f"M{i:05d}"

    category = random.choices(
        merchant_categories,
        weights=category_weights,
        k=1
    )[0]

    size = random.choices(
        merchant_sizes,
        weights=size_weights,
        k=1
    )[0]

    geography = random.choice(geographies)

    payment_weights = payment_method_weights[category]

    payment_method = random.choices(
        list(payment_weights.keys()),
        weights=list(payment_weights.values()),
        k=1
    )[0]

    # These MUST be inside the loop
    transaction_range = category_profiles[category]["avg_transaction_range"]

    avg_transaction_value = random.uniform(
        transaction_range[0],
        transaction_range[1]
    )

    volume_range = size_profiles[size]["volume_range"]

    monthly_transaction_volume = random.randint(
        volume_range[0],
        volume_range[1]
    )

    base_rate = payment_success_rates[payment_method]

    category_success_adjustments = {
        "Education": 0.000,
        "E-commerce": -0.005,
        "SaaS": 0.005,
        "Travel": -0.010,
        "Healthcare": 0.000,
        "Food Delivery": -0.005,
        "Gaming": -0.005,
        "Professional Services": 0.005,
        "Media": 0.000,
        "Retail": -0.005
    }

    category_adjustment = category_success_adjustments[category]

    baseline_success_rate = base_rate + category_adjustment

    baseline_success_rate = round(
        baseline_success_rate,
        4
    )

    subscription_probability = category_profiles[category]["subscription_probability"]

    subscription_enabled = random.random() < subscription_probability

    merchant = {
        "merchant_id": merchant_id,
        "merchant_category": category,
        "merchant_size": size,
        "avg_transaction_value": round(avg_transaction_value, 2),
        "monthly_transaction_volume": monthly_transaction_volume,
        "baseline_success_rate": baseline_success_rate,
        "primary_payment_method": payment_method,
        "geography": geography,
        "subscription_enabled": subscription_enabled
    }

    merchants.append(merchant)


# Create DataFrame AFTER the loop
merchants_df = pd.DataFrame(merchants)

print("Number of merchants:", len(merchants_df))
print("Dataset shape:", merchants_df.shape)

merchants_df.to_csv(
    "data/raw/merchants.csv",
    index=False
)

print("Merchant dataset saved successfully.")