import random
from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "data/source/customers/customers.csv"
)

OUTPUT_FILE = Path(
    "data/source/customers/customer_cdc.csv"
)

SEED = 42
NUM_CHANGES = 5_000

random.seed(SEED)


def main():

    df = pd.read_csv(INPUT_FILE)

    changed_customers = df.sample(
        n=NUM_CHANGES,
        random_state=SEED
    ).copy()

    changes = []

    for _, row in changed_customers.iterrows():

        change_type = random.choice(
            ["EMAIL_UPDATE", "PHONE_UPDATE", "TYPE_UPDATE"]
        )

        if change_type == "EMAIL_UPDATE":

            new_email = (
                f"updated_{row['customer_id'].lower()}"
                "@example.com"
            )

            changes.append({
                "customer_id": row["customer_id"],
                "change_type": "UPDATE",
                "changed_column": "email",
                "old_value": row["email"],
                "new_value": new_email,
                "change_timestamp": pd.Timestamp.now(),
            })

        elif change_type == "PHONE_UPDATE":

            new_phone = str(
                random.randint(6000000000, 9999999999)
            )

            changes.append({
                "customer_id": row["customer_id"],
                "change_type": "UPDATE",
                "changed_column": "phone",
                "old_value": str(row["phone"]),
                "new_value": new_phone,
                "change_timestamp": pd.Timestamp.now(),
            })

        else:

            new_type = random.choice(
                ["STANDARD", "PREMIUM", "VIP"]
            )

            changes.append({
                "customer_id": row["customer_id"],
                "change_type": "UPDATE",
                "changed_column": "customer_type",
                "old_value": row["customer_type"],
                "new_value": new_type,
                "change_timestamp": pd.Timestamp.now(),
            })

    cdc_df = pd.DataFrame(changes)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cdc_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("Customer CDC generation completed.")
    print(f"Changes generated: {len(cdc_df):,}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()