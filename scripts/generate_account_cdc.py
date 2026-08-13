import random
from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "data/source/accounts/accounts.csv"
)

OUTPUT_FILE = Path(
    "data/source/accounts/account_cdc.csv"
)

SEED = 42
NUM_CHANGES = 5_000

random.seed(SEED)


def main():

    df = pd.read_csv(INPUT_FILE)

    changed_accounts = df.sample(
        n=NUM_CHANGES,
        random_state=SEED
    ).copy()

    changes = []

    for _, row in changed_accounts.iterrows():

        change_type = random.choice(
            ["ACCOUNT_TYPE_UPDATE", "STATUS_UPDATE"]
        )

        if change_type == "ACCOUNT_TYPE_UPDATE":

            new_type = random.choice(
                ["CHECKING", "SAVINGS", "CREDIT"]
            )

            changes.append({
                "account_id": row["account_id"],
                "change_type": "UPDATE",
                "changed_column": "account_type",
                "old_value": row["account_type"],
                "new_value": new_type,
                "change_timestamp": pd.Timestamp.now(),
            })

        else:

            new_status = random.choice(
                ["ACTIVE", "BLOCKED", "CLOSED"]
            )

            changes.append({
                "account_id": row["account_id"],
                "change_type": "UPDATE",
                "changed_column": "status",
                "old_value": row["status"],
                "new_value": new_status,
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

    print("Account CDC generation completed.")
    print(f"Changes generated: {len(cdc_df):,}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()