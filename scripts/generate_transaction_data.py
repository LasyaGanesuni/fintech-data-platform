import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


# -----------------------------
# Configuration
# -----------------------------

TRANSACTIONS_PER_HOUR = 10_000
NUM_HOURS = 24

NUM_ACCOUNTS = 200_000
NUM_MERCHANTS = 10_000

SEED = 42

OUTPUT_BASE_DIR = Path(
    "data/source/transactions"
)

PROCESS_DATE = "2026-08-13"

random.seed(SEED)


# -----------------------------
# Reference data
# -----------------------------

TRANSACTION_TYPES = [
    "PURCHASE",
    "REFUND",
    "WITHDRAWAL",
    "TRANSFER",
]

TRANSACTION_STATUSES = [
    "SUCCESS",
    "FAILED",
    "PENDING",
]

CURRENCIES = [
    "INR",
    "GBP",
    "USD",
    "EUR",
]


# -----------------------------
# Generate transaction
# -----------------------------

def generate_transaction(
    transaction_number,
    hour
):

    transaction_id = (
        f"T{PROCESS_DATE.replace('-', '')}_"
        f"{transaction_number:08d}"
    )

    account_number = random.randint(
        1,
        NUM_ACCOUNTS
    )

    merchant_number = random.randint(
        1,
        NUM_MERCHANTS
    )

    account_id = (
        f"A{account_number:07d}"
    )

    merchant_id = (
        f"M{merchant_number:06d}"
    )

    transaction_timestamp = datetime(
        2026,
        8,
        13,
        hour,
        random.randint(0, 59),
        random.randint(0, 59)
    )

    amount = round(
        random.uniform(10, 100_000),
        2
    )

    return {
        "transaction_id": transaction_id,
        "account_id": account_id,
        "merchant_id": merchant_id,
        "transaction_amount": amount,
        "currency": random.choice(CURRENCIES),
        "transaction_type": random.choice(
            TRANSACTION_TYPES
        ),
        "transaction_status": random.choice(
            TRANSACTION_STATUSES
        ),
        "transaction_timestamp":
            transaction_timestamp,
        "created_at":
            transaction_timestamp,
        "updated_at":
            transaction_timestamp,
    }


# -----------------------------
# Main
# -----------------------------

def main():

    output_dir = (
        OUTPUT_BASE_DIR / PROCESS_DATE
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    transaction_number = 1

    total_records = 0

    for hour in range(NUM_HOURS):

        records = []

        for _ in range(
            TRANSACTIONS_PER_HOUR
        ):

            records.append(
                generate_transaction(
                    transaction_number,
                    hour
                )
            )

            transaction_number += 1

        df = pd.DataFrame(records)

        output_file = (
            output_dir
            / f"transactions_{hour:02d}.csv"
        )

        df.to_csv(
            output_file,
            index=False
        )

        total_records += len(df)

        print(
            f"Hour {hour:02d}: "
            f"{len(df):,} records → "
            f"{output_file}"
        )

    print("\nTransaction generation completed.")
    print(
        f"Total records: {total_records:,}"
    )


if __name__ == "__main__":
    main()