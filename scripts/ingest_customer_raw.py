from datetime import datetime
from pathlib import Path
import shutil


# --------------------------------
# Configuration
# --------------------------------

SOURCE_FILE = Path(
    "data/source/customers/customers.csv"
)

RAW_BASE_DIR = Path(
    "data/raw/customers"
)


# --------------------------------
# Main
# --------------------------------

def main():

    # Use today's date as ingestion date
    ingestion_date = datetime.now().strftime(
        "%Y-%m-%d"
    )

    raw_dir = (
        RAW_BASE_DIR / ingestion_date
    )

    raw_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    destination_file = (
        raw_dir / SOURCE_FILE.name
    )

    # --------------------------------
    # Copy source → Raw
    # --------------------------------

    shutil.copy2(
        SOURCE_FILE,
        destination_file
    )

    # --------------------------------
    # Logging
    # --------------------------------

    print(
        "Customer Raw ingestion completed."
    )

    print(
        f"Source      : {SOURCE_FILE}"
    )

    print(
        f"Destination : {destination_file}"
    )

    print(
        f"Ingestion date: {ingestion_date}"
    )


if __name__ == "__main__":
    main()