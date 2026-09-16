# Incremental Processing: Auto Loader vs Watermarking vs CDC

## 1. Auto Loader

### What is Auto Loader?
Databricks Auto Loader is used to incrementally ingest new files arriving in cloud storage such as ADLS.

It uses Structured Streaming internally and keeps track of files that have already been processed using a checkpoint.

### Problem it solves
> "Which NEW FILES have arrived?"

### Simple Architecture
```
ADLS
  ↓
New Files
  ↓
Auto Loader (cloudFiles)
  ↓
Bronze Delta Table
```

### Key Concepts
- `cloudFiles` → Auto Loader format
- `cloudFiles.schemaLocation` → stores schema information
- `checkpointLocation` → stores streaming progress/state
- `availableNow=True` → processes files currently available and then stops
- `_metadata.file_path` → identifies source file
- Schema evolution can be configured using `cloudFiles.schemaEvolutionMode`

### Important
Auto Loader works at the **file ingestion level**.

It does NOT tell us which business records changed.

### Our Project
Transactions arrive as multiple files in ADLS.

We used Auto Loader to ingest:

- 24 files
- 240,500 source rows
- 240,000 unique transaction IDs

Bronze preserves the source duplicates.

---

# 2. Watermarking

### What is Watermarking?
A watermark stores the last successfully processed value of a column, usually a timestamp or increasing ID.

The next pipeline processes records after that point.

### Problem it solves
> "Which NEW/CHANGED RECORDS should I process?"

### Simple Architecture
```
Source
  ↓
Read last watermark
  ↓
Filter:
updated_at > last_watermark
  ↓
Transform / DQ
  ↓
MERGE into Silver
  ↓
Successful?
  ↓
Update watermark
```

### Control Table

metadata.watermark_control

- pipeline_name
- source_table
- target_table
- watermark_column
- last_watermark
- watermark_updated_at

### Important Rule

Update the watermark ONLY after the target load succeeds.

Otherwise, failed records could be skipped in the next run.

### Our Project
Customer data arrives as daily snapshots.

We used `updated_at` as the business watermark to process only records newer than the last successful watermark.

### Important Distinction

`_source_date`
→ When the snapshot/file arrived.

`updated_at`
→ When the customer record was changed from a business perspective.

# 2A. Watermarking at ADF Pipeline Level

### What does it mean?

ADF can manage the orchestration of incremental processing by:
- Reading the last successful watermark
- Passing it to the processing activity
- Running the incremental load
- Updating the watermark after successful processing

The watermark itself can still be stored in a control table.

### Problem it solves

> "How does the orchestration layer know where the previous successful processing stopped?"

---

### Simple Architecture

                    ADF PIPELINE
                         ↓
                  Lookup Activity
                         ↓
              Read last_watermark
                         ↓
              Pipeline Parameter
                         ↓
               Databricks Notebook
                         ↓
              Filter / Process data
                         ↓
                MERGE into Silver
                         ↓
                      Success?
                     /       \
                   YES        NO
                    ↓          ↓
          Update watermark    Failure
             in control
               table

---

### Typical ADF Flow

1. **Lookup Activity**
   - Reads `last_watermark` from the control table.

2. **Set Variable / Parameter**
   - Stores or passes the retrieved watermark.

3. **Databricks Notebook Activity**
   - Receives the watermark as a parameter.

4. **Databricks Processing**
   - Filters records such as:

   `updated_at > last_watermark`

5. **MERGE**
   - Loads the incremental records into Silver.

6. **Success Dependency**
   - Only after successful processing, update the watermark.

7. **Failure Dependency**
   - If processing fails, do NOT advance the watermark.


---

# 3. CDC — Change Data Capture

### What is CDC?
CDC captures changes made to source data and provides information about what changed.

Depending on the source system, CDC can contain:
- INSERT
- UPDATE
- DELETE

CDC can come from databases, Kafka/Debezium, APIs, files, or Delta Change Data Feed.

### Problem it solves
> "WHAT EXACTLY CHANGED?"

### Simple Architecture
```
Source System
  ↓
CDC Events
  ↓
Bronze CDC
  ↓
Transform Changes
  ↓
SCD1 / SCD2
  ↓
Silver
```

### Our CDC Structure

account_id
change_type
changed_column
old_value
new_value
change_timestamp

Example:

account_id | changed_column | old_value | new_value
A1001      | status         | ACTIVE    | CLOSED

### Our Project

We used the account CDC file to implement:

CDC
 ↓
Bronze Account CDC
 ↓
SCD Type 1
 ↓
Current Account State

and separately:

CDC
 ↓
SCD Type 2
 ↓
Historical Account Versions

### Important
Our CDC test data contains UPDATE events only.

Therefore, we should NOT claim that our implementation demonstrates full INSERT/UPDATE/DELETE CDC handling.

---

# 4. Auto Loader vs Watermark vs CDC

These solve different problems.

### Auto Loader
> "What NEW FILES arrived?"

Works at the **file level**.

### Watermark
> "What NEW/CHANGED RECORDS should I process?"

Works at the **record level using a progression column**, such as `updated_at`.

### CDC
> "WHAT EXACTLY CHANGED?"

Works at the **change-event level**.

### Simple Comparison
```
AUTO LOADER
    ↓
New files?

WATERMARK
    ↓
New/changed records?

CDC
    ↓
What exactly changed?

SCD1 / SCD2
    ↓
How should the change be represented in the target?
```

---

# 5. Can They Be Used Together?

Yes.

They are not mutually exclusive.

Example:
```
ADLS
  ↓
Auto Loader
  ↓
Bronze
  ↓
Watermark / CDC processing
  ↓
Silver
  ↓
SCD1 / SCD2
```

For example, Auto Loader can ingest CDC files, while the CDC events themselves contain a `change_timestamp` that can be used for downstream processing.

### Key Interview Point

Auto Loader, Watermarking and CDC operate at different layers of the ingestion/change-processing problem.

They are complementary rather than competing technologies.

---

# 6. Event Time vs Ingestion Time

This is especially important for CDC and SCD2.

### `change_timestamp`
When the business/source change actually happened.

### `_ingestion_timestamp`
When our data platform received/processed the event.

Example:

Change happened:
10:00

Received by platform:
12:00

For SCD2 history, the business validity should generally be based on the source change/event time, not simply the ingestion time.

---

# 7. Late-Arriving CDC

Late-arriving CDC means a change arrives after a later change has already been processed.

Example:
```
10:00 → SAVINGS → CHECKING
11:00 → CHECKING → CLOSED
```

But the 10:00 event arrives after the 11:00 event.

For SCD2, we should use the CDC event/change timestamp to reconstruct the correct historical timeline rather than simply appending the late event as the newest version.

Expected history:
```
SAVINGS
09:00 → 10:00

CHECKING
10:00 → 11:00

CLOSED
11:00 → NULL
```

### Interview Line

"For late-arriving CDC, I distinguish event time from ingestion time and use the source change timestamp to maintain the correct SCD2 effective timeline. If a late event affects an already-built history, the affected business key needs to be corrected or reprocessed rather than blindly appended."

---

# 8. Quick Interview Summary

### Auto Loader
Used when the source is continuously or periodically dropping files into cloud storage.

### Watermark
Used when the source has a reliable progression column such as `updated_at` and we want to process only records beyond the last successful point.

### CDC
Used when the source explicitly provides change events and we need to know what changed.

### SCD1
Keeps the latest/current state.

### SCD2
Preserves historical versions.

### One-line mental model
```
Auto Loader → NEW FILES

Watermark → NEW/CHANGED RECORDS

CDC → EXACT CHANGES

SCD1 → CURRENT STATE

SCD2 → HISTORY
```