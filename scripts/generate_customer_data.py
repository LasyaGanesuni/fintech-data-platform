import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


# -----------------------------
# Configuration
# -----------------------------

NUM_CUSTOMERS = 100_000
SEED = 42

OUTPUT_DIR = Path("data/source/customers")


# -----------------------------
# Reproducibility
# -----------------------------

random.seed(SEED)


# -----------------------------
# Reference data
# -----------------------------

FIRST_NAMES = [
    "Ananya",
    "Rahul",
    "Priya",
    "Arjun",
    "Sneha",
    "Kiran",
    "Neha",
    "Vikram",
    "Meera",
    "Rohan",
]

LAST_NAMES = [
    "Rao",
    "Shah",
    "Reddy",
    "Patel",
    "Kumar",
    "Singh",
    "Iyer",
    "Nair",
]

COUNTRIES = ["IN", "UK", "US", "CA", "DE"]

CUSTOMER_TYPES = [
    "STANDARD",
    "PREMIUM",
    "VIP",
]


# -----------------------------
# Helper functions
# -----------------------------

def random_timestamp(start_year=2022, end_year=2026):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 8, 1)

    seconds = int((end - start).total_seconds())

    return start + timedelta(
        seconds=random.randint(0, seconds)
    )


def generate_customer(customer_id):
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)

    name = f"{first_name} {last_name}"

    created_at = random_timestamp()

    return {
        "customer_id": customer_id,
        "name": name,
        "email": f"{first_name.lower()}.{last_name.lower()}"
                f"{customer_id.lower()}@example.com",
        "phone": f"{random.randint(6000000000, 9999999999)}",
        "country": random.choice(COUNTRIES),
        "customer_type": random.choice(CUSTOMER_TYPES),
        "created_at": created_at,
        "updated_at": created_at,
    }


# -----------------------------
# Main generation
# -----------------------------

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    records = []

    for i in range(1, NUM_CUSTOMERS + 1):

        customer_id = f"C{i:06d}"

        records.append(
            generate_customer(customer_id)
        )

    df = pd.DataFrame(records)

    output_file = OUTPUT_DIR / "customers.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print("Customer data generation completed.")
    print(f"Records generated: {len(df):,}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
