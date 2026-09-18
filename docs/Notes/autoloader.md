
# Databricks Auto Loader

## 1. Objective

Use **Databricks Auto Loader** to incrementally ingest transaction files from **ADLS Gen2** into a **Bronze Delta table**.

### Architecture

```text
ADF
 ↓
ADLS Gen2
 ↓
Databricks Auto Loader
 ↓
Bronze Delta Table
````

### Why Auto Loader?

Instead of manually tracking which files have already been processed, Auto Loader:

* discovers new files incrementally
* maintains processing state through a checkpoint
* supports schema inference and schema evolution
* integrates with Structured Streaming
* can process currently available files and terminate using `availableNow`

### Project Source

```text
abfss://raw@fintechdllasya.dfs.core.windows.net/transactions/
```

### Initial Source

* Files: **24**
* Total records: **240,500**
* Unique transaction IDs: **240,000**
* Source-level duplicates: **500**

The 500 duplicate rows are preserved in Bronze because Bronze represents the ingested source.

> Deduplication is a Silver-layer responsibility.

---

# 2. Auto Loader Reader

Auto Loader is enabled using:

```python
spark.readStream.format("cloudFiles")
```

Our configuration:

```python
transactions_stream = (
    spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.schemaLocation", SCHEMA_LOCATION)
        .option("cloudFiles.inferColumnTypes", "true")
        .option("header", "true")
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
        .load(SOURCE_PATH)
)
```

### Important Options

| Option                           | Purpose                                  |
| -------------------------------- | ---------------------------------------- |
| `cloudFiles.format`              | Specifies the source file format         |
| `cloudFiles.schemaLocation`      | Stores Auto Loader schema information    |
| `cloudFiles.inferColumnTypes`    | Infers appropriate data types            |
| `header`                         | Treats the first CSV row as column names |
| `cloudFiles.schemaEvolutionMode` | Controls how new columns are handled     |

---

# 3. Schema Location

Auto Loader requires a schema location.

Our final schema location:

```text
abfss://raw@fintechdllasya.dfs.core.windows.net/_autoloader_schema/transactions_final/
```

The schema location stores information about the schema inferred by Auto Loader.

### Important distinction

Schema location and checkpoint are **not the same thing**.

```text
Schema Location
    ↓
"What does the incoming data look like?"

Checkpoint
    ↓
"What has this stream already processed?"
```

---

# 4. Checkpointing

Our final checkpoint:

```text
abfss://raw@fintechdllasya.dfs.core.windows.net/_autoloader_checkpoint/transactions_final/
```

Configured using:

```python
.option("checkpointLocation", CHECKPOINT_LOCATION)
```

The checkpoint stores the streaming state required for the pipeline to resume processing.

It is also important for preventing already-processed files from being processed again by the same stream.

## Rerun Test

The pipeline was initially run against the 24 transaction files.

Result:

```text
240,500 records processed
```

The same pipeline was then rerun using the **same checkpoint**.

No previously processed records were added.

This demonstrated incremental file processing and checkpoint-based state management.

### Key takeaway

> A checkpoint should be treated as persistent state for a specific streaming pipeline.

Changing or deleting the checkpoint effectively creates a new processing state.

---

# 5. `availableNow`

We used:

```python
.trigger(availableNow=True)
```

This allows the pipeline to:

1. Start
2. Process currently available files
3. Process any required incremental batches
4. Terminate after available data has been processed

Conceptually:

```text
Start Job
    ↓
Discover New Files
    ↓
Process Files
    ↓
Finish
```

This is useful for a scheduled ingestion workflow where we don't need a continuously running streaming query.

---

# 6. Ingestion Metadata

Auto Loader provides file-level metadata through the `_metadata` column.

We added:

```python
transactions_stream_with_metadata = (
    transactions_stream
    .withColumn("_ingestion_timestamp", F.current_timestamp())
    .withColumn("_source_file", F.col("_metadata.file_path"))
    .withColumn(
        "_source_date",
        F.to_date(
            F.regexp_extract(
                F.col("_metadata.file_path"),
                r"/transactions/(\d{4}-\d{2}-\d{2})/",
                1
            )
        )
    )
)
```

## `_ingestion_timestamp`

```text
_ingestion_timestamp
```

Records when the record was ingested into Bronze.

Useful for:

* operational monitoring
* troubleshooting
* audit
* identifying ingestion timing

## `_source_file`

```text
_source_file
```

Stores the original source file path using:

```python
F.col("_metadata.file_path")
```

Useful for:

* traceability
* debugging
* reconciliation
* audit
* identifying which file produced a record

## `_source_date`

The source date is extracted from the ADLS folder structure.

Example:

```text
transactions/2026-08-13/transactions_00.csv
                     ↓
                2026-08-13
```

Implementation:

```python
F.to_date(
    F.regexp_extract(
        F.col("_metadata.file_path"),
        r"/transactions/(\d{4}-\d{2}-\d{2})/",
        1
    )
)
```

### Important timestamp distinction

```text
_source_date
    → source / arrival date from the folder path

transaction_timestamp
    → business event timestamp

created_at / updated_at
    → record lifecycle timestamps
```

These represent different concepts and should not be treated interchangeably.

---

# 7. Writing to Bronze Delta

Final target:

```text
dbx_fintech_data_platform.bronze.transactions_autoloader_final
```

Final write:

```python
transactions_query = (
    transactions_stream_with_metadata.writeStream
        .format("delta")
        .option("checkpointLocation", CHECKPOINT_LOCATION)
        .option("mergeSchema", "true")
        .outputMode("append")
        .trigger(availableNow=True)
        .toTable(BRONZE_TABLE)
)
```

### Why `append`?

Bronze is an ingestion layer.

New source data should be appended rather than replacing previously ingested records.

---

# 8. Schema Evolution

We separately tested Auto Loader schema evolution.

A new column called:

```text
risk_score
```

was introduced into a new source file.

We used:

```python
.option(
    "cloudFiles.schemaEvolutionMode",
    "addNewColumns"
)
```

The test demonstrated:

```text
New column arrives
       ↓
Auto Loader detects new column
       ↓
Schema is updated
       ↓
Stream stops
       ↓
Stream needs to be recreated/restarted
```

The Delta target also needed schema evolution enabled:

```python
.option("mergeSchema", "true")
```

## Auto Loader vs Delta Schema Evolution

These are **two separate concepts**.

```text
Auto Loader
     ↓
Manages incoming/source schema

Delta Lake
     ↓
Manages target table schema
```

Therefore:

```text
cloudFiles.schemaEvolutionMode
```

and

```text
mergeSchema
```

solve different problems.

---

# 9. Schema Evolution Modes

Important Auto Loader schema evolution modes:

### `addNewColumns`

Automatically adds newly detected columns to the schema.

The stream may stop when a new column is detected and require a restart.

### `rescue`

Unexpected fields can be captured in:

```text
_rescued_data
```

instead of being added as normal columns.

### `failOnNewColumns`

The stream fails when a new column is detected.

### `none`

New columns are not automatically added to the schema.

### Project Choice

We used:

```text
addNewColumns
```

because we want to explicitly handle schema evolution in the project.

---

# 10. Bronze vs Silver Responsibility

Auto Loader is an **ingestion mechanism**, not a business transformation layer.

## Bronze

```text
Source
 ↓
Auto Loader
 ↓
Bronze
```

Bronze preserves:

* source records
* source duplicates
* ingestion metadata
* source file information

Therefore:

```text
240,500 source records
        ↓
240,500 Bronze records
```

even though:

```text
240,000 unique transaction IDs
```

## Silver

```text
Bronze
 ↓
Cleaning
 ↓
Data Quality
 ↓
Deduplication
 ↓
Business Rules
 ↓
Silver
```

Transaction deduplication will happen in Silver.

---

# 11. Troubleshooting: The 491K Records Issue

During development, the final table temporarily showed:

```text
491,000 records
```

This initially looked like Auto Loader had reprocessed the source files.

We investigated the Delta table history.

The previous experiments had already written:

```text
100,000
+ 140,500
+ 10,000
-----------
250,500
```

The final clean pipeline then wrote:

```text
100,000
+ 140,500
-----------
240,500
```

Therefore:

```text
250,500
+ 240,500
-----------
491,000
```

## Root Cause

The final target table contained data from previous Auto Loader experiments.

It was **not an Auto Loader duplicate-processing issue**.

## Resolution

We:

1. Dropped the contaminated final target table.
2. Removed the final checkpoint.
3. Re-ran the final pipeline using a clean target and checkpoint.
4. Validated the resulting data.

## Production Lesson

Each independent streaming pipeline should have isolated:

```text
Target Table
Checkpoint
Schema Location
```

Do not mix experimental and final pipeline state.

---

# 12. Final Validation

After resetting the final target and checkpoint, the pipeline produced:

| Metric                 |  Result |
| ---------------------- | ------: |
| Total records          | 240,500 |
| Unique transaction IDs | 240,000 |
| Source files           |      24 |
| Source dates           |       1 |

Per-file validation also confirmed that all 24 source files were ingested.

Therefore:

```text
24 source files
       ↓
240,500 Bronze records
       ↓
240,000 unique transactions
       +
500 source-level duplicate rows
```

This confirms that the ingestion pipeline is behaving as expected.

---

# 13. Key Interview Questions

### What is Auto Loader?

Auto Loader is a Databricks incremental file ingestion mechanism designed to efficiently process files arriving in cloud storage.

### Why use Auto Loader?

It provides incremental file discovery and processing while maintaining processing state through checkpoints.

### What does the checkpoint do?

It stores the streaming state required to resume processing and track files already processed by the stream.

### What is `schemaLocation`?

It stores the schema information used by Auto Loader.

### Schema location vs checkpoint?

```text
Schema Location → schema state
Checkpoint      → processing state
```

### Why use `availableNow`?

It allows a scheduled job to process currently available data and terminate after processing completes.

### Should duplicates be removed in Bronze?

No. Bronze should generally preserve the source data for traceability and reconciliation.

### Where should transaction deduplication happen?

Silver.

### Is Auto Loader schema evolution the same as Delta schema evolution?

No.

Auto Loader manages the incoming schema, while Delta manages the target table schema.

### What happens when a new column arrives with `addNewColumns`?

Auto Loader detects the new column, updates the schema, and the stream may stop and require a restart.

### Why should checkpoints be isolated?

A checkpoint contains pipeline-specific processing state. Reusing checkpoints across unrelated pipelines can lead to incorrect or confusing ingestion behavior.

---

# 14. Current Implementation

```text
                    ADF
                     │
                     ▼
                  ADLS Gen2
                     │
                     ▼
              ┌──────────────┐
              │ Auto Loader  │
              └──────────────┘
                     │
            ┌────────┴────────┐
            │                 │
     Schema Location      Checkpoint
            │                 │
            └────────┬────────┘
                     ▼
              Bronze Delta
                     │
                     ▼
                  Silver
```

---

# 15. Future Improvements

The core Auto Loader implementation is complete.

Next improvements planned for this project:

* Integrate Auto Loader with the existing audit/ingestion framework
* Add operational monitoring
* Connect Auto Loader to downstream Silver processing
* Evaluate file events for scalable file discovery
* Add CI/CD deployment using Databricks Asset Bundles
* Add automated testing and regression checks

---

# Key Takeaway

> **Auto Loader handles incremental file discovery and ingestion. Bronze preserves the source and ingestion metadata. Silver handles data quality, deduplication, and business rules.**

The architectural separation is:

```text
File Discovery & Incremental Ingestion
                ↓
           Auto Loader

Raw Data Preservation
                ↓
             Bronze

Data Quality & Deduplication
                ↓
             Silver

Business Consumption
                ↓
              Gold
```

```
```
