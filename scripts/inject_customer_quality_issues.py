import random
from pathlib import Path

import pandas as pd


# -----------------------------
# Configuration
# -----------------------------

INPUT_FILE = Path("data/source/customers/customers.csv")
OUTPUT_FILE = Path("data/source/customers/customers_bad.csv")

SEED = 42

DUPLICATE_RATE = 0.01
NULL_PHONE_RATE = 0.005
NULL_EMAIL_RATE = 0.002
INVALID_COUNTRY_RATE = 0.002
INVALID_CUSTOMER_TYPE_RATE = 0.002
CASING_ISSUE_RATE = 0.005


random.seed(SEED)


# -----------------------------
# Main
# -----------------------------

def main():

    df = pd.read_csv(INPUT_FILE)

    original_count = len(df)

    # -------------------------
    # 1. Inject duplicates
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
    # 2. Missing phone numbers
    # -------------------------

    phone_count = int(
        original_count * NULL_PHONE_RATE
    )

    phone_indices = df.sample(
        n=phone_count,
        random_state=SEED + 1
    ).index

    df.loc[phone_indices, "phone"] = None

    # -------------------------
    # 3. Missing emails
    # -------------------------

    email_count = int(
        original_count * NULL_EMAIL_RATE
    )

    email_indices = df.sample(
        n=email_count,
        random_state=SEED + 2
    ).index

    df.loc[email_indices, "email"] = None

    # -------------------------
    # 4. Invalid countries
    # -------------------------

    country_count = int(
        original_count * INVALID_COUNTRY_RATE
    )

    country_indices = df.sample(
        n=country_count,
        random_state=SEED + 3
    ).index

    df.loc[country_indices, "country"] = "XX"

    # -------------------------
    # 5. Invalid customer types
    # -------------------------

    customer_type_count = int(
        original_count * INVALID_CUSTOMER_TYPE_RATE
    )

    customer_type_indices = df.sample(
        n=customer_type_count,
        random_state=SEED + 4
    ).index

    df.loc[
        customer_type_indices,
        "customer_type"
    ] = "UNKNOWN_TYPE"

    # -------------------------
    # 6. Inconsistent casing
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
        "customer_type"
    ] = df.loc[
        casing_indices,
        "customer_type"
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

    print("Customer quality issue injection completed.")
    print(f"Original records : {original_count:,}")
    print(f"Final records    : {len(df):,}")
    print(f"Duplicates added : {duplicate_count:,}")
    print(f"Null phones      : {phone_count:,}")
    print(f"Null emails      : {email_count:,}")
    print(f"Invalid countries: {country_count:,}")
    print(
        f"Invalid customer types: "
        f"{customer_type_count:,}"
    )
    print(f"Casing issues    : {casing_count:,}")
    print(f"Output           : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()