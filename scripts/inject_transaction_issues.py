import random
from pathlib import Path

import pandas as pd


BASE_DIR = Path(
    "data/source/transactions/2026-08-13"
)

SEED = 42

random.seed(SEED)


def main():

    # -------------------------
    # Pick one hourly file
    # -------------------------

    target_file = (
        BASE_DIR / "transactions_18.csv"
    )

    df = pd.read_csv(target_file)

    original_count = len(df)

    # -------------------------
    # 1. Duplicate transactions
    # -------------------------

    duplicate_count = 500

    duplicate_rows = df.sample(
        n=duplicate_count,
        random_state=SEED
    )

    df = pd.concat(
        [df, duplicate_rows],
        ignore_index=True
    )

    # -------------------------
    # 2. Create Spark skew
    # -------------------------

    skew_count = 5_000

    skew_indices = df.sample(
        n=skew_count,
        random_state=SEED + 1
    ).index

    df.loc[
        skew_indices,
        "account_id"
    ] = "A0000001"

    # -------------------------
    # Write modified file
    # -------------------------

    df.to_csv(
        target_file,
        index=False
    )

    print(
        "Transaction issue injection completed."
    )

    print(
        f"Original records : {original_count:,}"
    )

    print(
        f"Final records    : {len(df):,}"
    )

    print(
        f"Duplicates added : {duplicate_count:,}"
    )

    print(
        f"Skewed records   : {skew_count:,}"
    )

    print(
        f"Modified file    : {target_file}"
    )


if __name__ == "__main__":
    main()