from datetime import datetime
from pathlib import Path

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    current_timestamp,
    input_file_name,
    lit,
)
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    TimestampType,
    LongType
)


# --------------------------------
# Configuration
# --------------------------------

RAW_FILE = (
    "data/raw/customers/2026-08-17/customers.csv"
)

BRONZE_PATH = (
    "data/bronze/customers"
)

AUDIT_PATH = (
    "data/bronze/_audit/ingestion_audit"
)

SOURCE_SYSTEM = "customer_db"

SOURCE_FILE = str(
    Path(RAW_FILE)
)

BATCH_ID = (
    datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )
)


# --------------------------------
# Spark + Delta configuration
# --------------------------------

builder = (
    SparkSession.builder
    .appName("CustomerBronzeIngestion")
    .master("local[*]")
    .config(
        "spark.sql.extensions",
        "io.delta.sql.DeltaSparkSessionExtension"
    )
    .config(
        "spark.sql.catalog.spark_catalog",
        "org.apache.spark.sql.delta.catalog.DeltaCatalog"
    )
)

spark = configure_spark_with_delta_pip(
    builder
).getOrCreate()


# --------------------------------
# Check ingestion audit
# --------------------------------

audit_df = (
    spark.read
    .format("delta")
    .load(AUDIT_PATH)
)

already_processed = (
    audit_df
    .filter(
        (audit_df.source_system == SOURCE_SYSTEM)
        &
        (audit_df.source_file == SOURCE_FILE)
        &
        (audit_df.status == "SUCCESS")
    )
    .limit(1)
    .count()
    > 0
)


if already_processed:

    print(
        "Customer Bronze ingestion skipped."
    )

    print(
        "Reason: source file already "
        "processed successfully."
    )

    print(
        f"Source file: {SOURCE_FILE}"
    )

    spark.stop()

    raise SystemExit(0)


# --------------------------------
# Customer schema
# --------------------------------

customer_schema = StructType([
    StructField(
        "customer_id",
        StringType(),
        False
    ),
    StructField(
        "name",
        StringType(),
        False
    ),
    StructField(
        "email",
        StringType(),
        False
    ),
    StructField(
        "phone",
        StringType(),
        False
    ),
    StructField(
        "country",
        StringType(),
        False
    ),
    StructField(
        "customer_type",
        StringType(),
        False
    ),
    StructField(
        "created_at",
        TimestampType(),
        False
    ),
    StructField(
        "updated_at",
        TimestampType(),
        False
    ),
])


# --------------------------------
# Read Raw
# --------------------------------

df = (
    spark.read
    .schema(customer_schema)
    .option("header", True)
    .csv(RAW_FILE)
)


# --------------------------------
# Add metadata
# --------------------------------

bronze_df = (
    df
    .withColumn(
        "ingestion_timestamp",
        current_timestamp()
    )
    .withColumn(
        "source_file",
        input_file_name()
    )
    .withColumn(
        "batch_id",
        lit(BATCH_ID)
    )
)


# --------------------------------
# Write Bronze
# --------------------------------

(
    bronze_df.write
    .format("delta")
    .mode("append")
    .save(BRONZE_PATH)
)


row_count = bronze_df.count()


# --------------------------------
# Write audit record
# --------------------------------

audit_record = [(
    SOURCE_SYSTEM,
    SOURCE_FILE,
    BATCH_ID,
    datetime.now(),
    "SUCCESS",
    row_count,
)]

audit_schema = StructType([
    StructField(
        "source_system",
        StringType(),
        False
    ),
    StructField(
        "source_file",
        StringType(),
        False
    ),
    StructField(
        "batch_id",
        StringType(),
        False
    ),
    StructField(
        "ingestion_timestamp",
        TimestampType(),
        False
    ),
    StructField(
        "status",
        StringType(),
        False
    ),
    StructField(
        "row_count",
        LongType(),
        True
    ),
])


audit_record_df = spark.createDataFrame(
    audit_record,
    audit_schema
)

(
    audit_record_df.write
    .format("delta")
    .mode("append")
    .save(AUDIT_PATH)
)


# --------------------------------
# Validation
# --------------------------------

print(
    "Customer Bronze ingestion completed."
)

print(
    f"Rows written: {row_count:,}"
)

print(
    f"Batch ID: {BATCH_ID}"
)

print(
    f"Source file: {SOURCE_FILE}"
)

spark.stop()