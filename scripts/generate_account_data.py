import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


# -----------------------------
# Configuration
# -----------------------------

NUM_ACCOUNTS = 200_000
NUM_CUSTOMERS = 100_000
SEED = 42

OUTPUT_FILE = Path(
    "data/source/accounts/accounts.csv"
)

random.seed(SEED)


# -----------------------------
# Reference data
# -----------------------------

ACCOUNT_TYPES = [
    "CHECKING",
    "SAVINGS",
    "CREDIT",
]

CURRENCIES = [
    "INR",
    "GBP",
    "USD",
    "EUR",
]

STATUSES = [
    "ACTIVE",
    "BLOCKED",
    "CLOSED",
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
# Generate one account
# -----------------------------

def generate_account(account_id):

    customer_number = random.randint(
        1,
        NUM_CUSTOMERS
    )

    customer_id = f"C{customer_number:06d}"

    created_at = random_timestamp()

    return {
        "account_id": account_id,
        "customer_id": customer_id,
        "account_type": random.choice(
            ACCOUNT_TYPES
        ),
        "currency": random.choice(
            CURRENCIES
        ),
        "status": random.choice(
            STATUSES
        ),
        "created_at": created_at,
        "updated_at": created_at,
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

    for i in range(1, NUM_ACCOUNTS + 1):

        account_id = f"A{i:07d}"

        records.append(
            generate_account(account_id)
        )

    df = pd.DataFrame(records)

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("Account data generation completed.")
    print(
        f"Records generated: {len(df):,}"
    )
    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()