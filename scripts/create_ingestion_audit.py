from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    TimestampType,
    LongType,
)


# --------------------------------
# Configuration
# --------------------------------

AUDIT_PATH = "data/bronze/_audit/ingestion_audit"


# --------------------------------
# Spark + Delta
# --------------------------------

builder = (
    SparkSession.builder
    .appName("CreateIngestionAudit")
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
# Audit schema
# --------------------------------

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


# --------------------------------
# Create empty Delta table
# --------------------------------

empty_df = spark.createDataFrame(
    [],
    audit_schema
)

(
    empty_df.write
    .format("delta")
    .mode("ignore")
    .save(AUDIT_PATH)
)


print("Ingestion audit table created.")
print(f"Audit path: {AUDIT_PATH}")

spark.stop()