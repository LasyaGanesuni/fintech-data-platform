import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


# -----------------------------
# Configuration
# -----------------------------

NUM_MERCHANTS = 10_000
SEED = 42

OUTPUT_FILE = Path(
    "data/source/merchants/merchants.json"
)

random.seed(SEED)


# -----------------------------
# Reference data
# -----------------------------

MERCHANT_CATEGORIES = [
    "GROCERY",
    "RESTAURANT",
    "E_COMMERCE",
    "TRAVEL",
    "FUEL",
    "HEALTHCARE",
    "ENTERTAINMENT",
    "ELECTRONICS",
]

COUNTRIES = [
    "IN",
    "UK",
    "US",
    "CA",
    "DE",
]

RISK_LEVELS = [
    "LOW",
    "MEDIUM",
    "HIGH",
]

STATUSES = [
    "ACTIVE",
    "INACTIVE",
]


# -----------------------------
# Helper
# -----------------------------

def random_timestamp():

    start = datetime(2022, 1, 1)
    end = datetime(2026, 8, 1)

    seconds = int(
        (end - start).total_seconds()
    )

    return start + timedelta(
        seconds=random.randint(0, seconds)
    )


# -----------------------------
# Generate merchant
# -----------------------------

def generate_merchant(merchant_id):

    created_at = random_timestamp()

    return {
        "merchant_id": merchant_id,
        "merchant_name": (
            f"Merchant_{merchant_id}"
        ),
        "merchant_category": random.choice(
            MERCHANT_CATEGORIES
        ),
        "country": random.choice(
            COUNTRIES
        ),
        "risk_level": random.choice(
            RISK_LEVELS
        ),
        "status": random.choice(
            STATUSES
        ),
        "created_at": created_at.isoformat(),
        "updated_at": created_at.isoformat(),
    }


# -----------------------------
# Main
# -----------------------------

def main():

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    records = []

    for i in range(1, NUM_MERCHANTS + 1):

        merchant_id = f"M{i:06d}"

        records.append(
            generate_merchant(
                merchant_id
            )
        )

    df = pd.DataFrame(records)

    df.to_json(
        OUTPUT_FILE,
        orient="records",
        indent=2
    )

    print(
        "Merchant API response generation completed."
    )
    print(
        f"Records generated: {len(df):,}"
    )
    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()