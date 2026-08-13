import random
from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "data/source/accounts/accounts.csv"
)

OUTPUT_FILE = Path(
    "data/source/accounts/accounts_bad.csv"
)

SEED = 42

DUPLICATE_RATE = 0.01
NULL_CUSTOMER_RATE = 0.005
INVALID_CUSTOMER_RATE = 0.005
INVALID_ACCOUNT_TYPE_RATE = 0.005
INVALID_STATUS_RATE = 0.005
CASING_ISSUE_RATE = 0.005

random.seed(SEED)


def main():

    df = pd.read_csv(INPUT_FILE)

    original_count = len(df)

    # -------------------------
    # 1. Duplicate accounts
    # -------------------------

    duplicate_count = int(
        original_count * DUPLICATE_RATE
    )

    duplicate_rows = df.sample(
        n=duplicate_count,
        random_state=SEED
    )

    df = pd.concat(
        [df, duplicate_rows],
        ignore_index=True
    )

    # -------------------------
    # 2. NULL customer IDs
    # -------------------------

    null_customer_count = int(
        original_count * NULL_CUSTOMER_RATE
    )

    null_indices = df.sample(
        n=null_customer_count,
        random_state=SEED + 1
    ).index

    df.loc[
        null_indices,
        "customer_id"
    ] = None

    # -------------------------
    # 3. Invalid customer IDs
    # -------------------------

    invalid_customer_count = int(
        original_count * INVALID_CUSTOMER_RATE
    )

    invalid_indices = df.sample(
        n=invalid_customer_count,
        random_state=SEED + 2
    ).index

    df.loc[
        invalid_indices,
        "customer_id"
    ] = "C999999"

    # -------------------------
    # 4. Invalid account types
    # -------------------------

    invalid_type_count = int(
        original_count * INVALID_ACCOUNT_TYPE_RATE
    )

    invalid_type_indices = df.sample(
        n=invalid_type_count,
        random_state=SEED + 3
    ).index

    df.loc[
        invalid_type_indices,
        "account_type"
    ] = "INVALID_TYPE"

    # -------------------------
    # 5. Invalid statuses
    # -------------------------

    invalid_status_count = int(
        original_count * INVALID_STATUS_RATE
    )

    invalid_status_indices = df.sample(
        n=invalid_status_count,
        random_state=SEED + 4
    ).index

    df.loc[
        invalid_status_indices,
        "status"
    ] = "UNKNOWN_STATUS"

    # -------------------------
    # 6. Casing issues
    # -------------------------

    casing_count = int(
        original_count * CASING_ISSUE_RATE
    )

    casing_indices = df.sample(
        n=casing_count,
        random_state=SEED + 5
    ).index

    df.loc[
        casing_indices,
        "account_type"
    ] = df.loc[
        casing_indices,
        "account_type"
    ].str.lower()

    # -------------------------
    # Write output
    # -------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # -------------------------
    # Summary
    # -------------------------

    print("Account quality issue injection completed.")
    print(f"Original records       : {original_count:,}")
    print(f"Final records          : {len(df):,}")
    print(f"Duplicates added       : {duplicate_count:,}")
    print(f"NULL customer IDs      : {null_customer_count:,}")
    print(f"Invalid customer IDs   : {invalid_customer_count:,}")
    print(f"Invalid account types  : {invalid_type_count:,}")
    print(f"Invalid statuses       : {invalid_status_count:,}")
    print(f"Casing issues          : {casing_count:,}")
    print(f"Output                 : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()