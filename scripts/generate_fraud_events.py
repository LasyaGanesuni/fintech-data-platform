import json
import random
from pathlib import Path

import pandas as pd


# -----------------------------
# Configuration
# -----------------------------

TRANSACTION_DIR = Path(
    "data/source/transactions/2026-08-13"
)

OUTPUT_FILE = Path(
    "data/source/fraud_events/fraud_events.jsonl"
)

NUM_EVENTS = 20_000
DUPLICATE_RATE = 0.02
SEED = 42

random.seed(SEED)


# -----------------------------
# Reference data
# -----------------------------

FRAUD_TYPES = [
    "CARD_TESTING",
    "ACCOUNT_TAKEOVER",
    "UNUSUAL_LOCATION",
    "HIGH_VALUE",
    "RAPID_TRANSACTIONS",
]

EVENT_STATUSES = [
    "DETECTED",
    "REVIEW",
]


# -----------------------------
# Main
# -----------------------------

def main():

    # -------------------------
    # Read transaction files
    # -------------------------

    files = sorted(
        TRANSACTION_DIR.glob("*.csv")
    )

    transaction_frames = [
        pd.read_csv(file)
        for file in files
    ]

    transactions = pd.concat(
        transaction_frames,
        ignore_index=True
    )

    # Remove duplicate transaction IDs
    # from the intentionally corrupted
    # transaction file.
    transactions = transactions.drop_duplicates(
        subset=["transaction_id"]
    )

    # -------------------------
    # Select transactions
    # -------------------------

    selected = transactions.sample(
        n=NUM_EVENTS,
        random_state=SEED
    ).copy()

    events = []

    for index, (_, row) in enumerate(
        selected.iterrows(),
        start=1
    ):

        transaction_id = row[
            "transaction_id"
        ]

        event_timestamp = pd.to_datetime(
            row["transaction_timestamp"]
        )

        # Fraud detection happens shortly
        # after the transaction.
        event_timestamp = (
            event_timestamp
            + pd.Timedelta(
                seconds=random.randint(1, 120)
            )
        )

        fraud_score = round(
            random.uniform(0.70, 0.99),
            4
        )

        event = {
            "fraud_event_id":
                f"F{index:08d}",

            "transaction_id":
                transaction_id,

            "account_id":
                row["account_id"],

            "merchant_id":
                row["merchant_id"],

            "fraud_score":
                fraud_score,

            "fraud_type":
                random.choice(FRAUD_TYPES),

            "event_status":
                random.choice(EVENT_STATUSES),

            "event_timestamp":
                event_timestamp.isoformat(),
        }

        events.append(event)

    # -------------------------
    # Add duplicate events
    # -------------------------

    duplicate_count = int(
        NUM_EVENTS * DUPLICATE_RATE
    )

    duplicate_events = random.sample(
        events,
        duplicate_count
    )

    events.extend(
        duplicate_events
    )

    # -------------------------
    # Shuffle events
    # -------------------------

    # This simulates events arriving
    # out of order.
    random.shuffle(events)

    # -------------------------
    # Write JSON Lines
    # -------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for event in events:

            file.write(
                json.dumps(event)
                + "\n"
            )

    print(
        "Fraud event generation completed."
    )

    print(
        f"Base events generated : "
        f"{NUM_EVENTS:,}"
    )

    print(
        f"Duplicate events added: "
        f"{duplicate_count:,}"
    )

    print(
        f"Total events written  : "
        f"{len(events):,}"
    )

    print(
        f"Output                : "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()