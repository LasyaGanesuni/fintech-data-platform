
# Delta Lake — Interview & Project Notes

## 1. What is Delta Lake?

Delta Lake is a storage layer that adds reliability and transactional capabilities on top of data files such as Parquet.

A Delta table consists conceptually of:

    Delta Table
       │
       ├── Data Files (Parquet)
       │      └── Actual data
       │
       └── _delta_log
              └── Transaction log

The transaction log maintains the transactional state/history of the table.

---

# 2. Delta Transaction Log

The `_delta_log` is the foundation of Delta Lake.

It records information about changes to the table, such as:

- Data file additions/removals
- Table metadata
- Schema information
- Transactions
- Table versions

Conceptually:

    Version 0
        ↓
    Version 1
        ↓
    Version 2
        ↓
    Version 3

Each committed transaction can create a new Delta table version.

### Important distinction

Parquet files:
- Store the actual data

`_delta_log`:
- Maintains the transactional state and history of the table

Do NOT think of `_delta_log` as containing copies of the table data.

---

# 3. Delta Table History

Use:

```sql
DESCRIBE HISTORY table_name;
````

Example:

```sql
DESCRIBE HISTORY
dbx_fintech_data_platform.silver.delta_learning_test;
```

History can contain information such as:

* version
* timestamp
* operation
* operationParameters
* operationMetrics
* userName

Example:

```
Version 0 → CREATE TABLE
Version 1 → WRITE
Version 2 → UPDATE
Version 3 → OPTIMIZE
Version 4 → MERGE
Version 5 → DELETE
```

### Production use cases

Table history is useful for:

* Auditing
* Debugging
* Investigating data changes
* Understanding which operation affected a table
* Supporting recovery investigations

---

# 4. ACID Transactions

Delta Lake provides ACID transactional guarantees for operations on Delta tables.

### A — Atomicity

A transaction is all-or-nothing.

Example:

```
MERGE 10,000 records
       ↓
   Success
       ↓
Transaction committed
```

If the transaction fails before commit, the incomplete transaction isn't presented as the new table state.

### C — Consistency

The table remains in a valid state according to its schema and transaction rules.

### I — Isolation

Concurrent operations don't expose an inconsistent intermediate table state.

### D — Durability

Once a transaction is committed, the change persists.

### Interview answer

"Delta Lake provides ACID transactional guarantees for operations on Delta tables by maintaining table state through its transaction log."

---

# 5. Time Travel

Time Travel allows us to query a Delta table as it existed at a previous version or timestamp.

## By version

```sql
SELECT *
FROM table_name
VERSION AS OF 1;
```

## By timestamp

```sql
SELECT *
FROM table_name
TIMESTAMP AS OF '2026-09-17 20:00:00';
```

Example:

```
Version 1
    ↓
A002 = ACTIVE

Version 2
    ↓
A002 = CLOSED
```

Querying:

```sql
SELECT *
FROM table_name
VERSION AS OF 1;
```

returns the table state from Version 1.

---

# 6. Copying a Previous Version

A previous Delta version can be copied into a new Delta table using CTAS + Time Travel.

```sql
CREATE TABLE recovery_table
USING DELTA
AS
SELECT *
FROM table_name
VERSION AS OF 1;
```

This creates a NEW Delta table.

It does not create a branch of the original table's history.

Conceptually:

```
Original table
Version 0 → 1 → 2 → 3
                     ↓
                  Current

New table
     ↓
Snapshot of Version 1
```

The new table has its own Delta history.

---

# 7. Time Travel — Production Use Cases

## 7.1 Debugging

If incorrect data appears after a pipeline run, compare table versions.

```sql
SELECT *
FROM silver.accounts
VERSION AS OF 10
WHERE account_id = 'A002';
```

Compare with:

```sql
SELECT *
FROM silver.accounts
VERSION AS OF 11
WHERE account_id = 'A002';
```

This helps identify when the table state changed.

---

## 7.2 Recovery

If a bad pipeline modifies data:

```
Version 20 → Correct
Version 21 → Correct
Version 22 → BAD UPDATE
```

Version 21 can be inspected:

```sql
SELECT *
FROM silver.accounts
VERSION AS OF 21;
```

A historical version can also be used to create a recovery table:

```sql
CREATE TABLE recovery_table
USING DELTA
AS
SELECT *
FROM silver.accounts
VERSION AS OF 21;
```

The exact recovery approach depends on the situation.

---

## 7.3 Auditing

Time Travel can help investigate historical table states.

Example:

```sql
SELECT *
FROM silver.accounts_scd2
VERSION AS OF 15
WHERE customer_id = 'C001';
```

Useful when investigating what the table looked like at a particular point in time.

---

## 7.4 Comparing Pipeline Runs

Different Delta versions can be compared to understand the impact of a pipeline.

Example:

```sql
SELECT COUNT(*)
FROM gold.customer_summary
VERSION AS OF 100;
```

vs.

```sql
SELECT COUNT(*)
FROM gold.customer_summary
VERSION AS OF 101;
```

Can be useful for:

* Pipeline validation
* Debugging
* Data reconciliation
* Investigating unexpected changes

---

# 8. Important: Time Travel vs SCD2

These are NOT the same thing.

## SCD2

SCD2 provides business-level historical tracking.

Example:

```
A001 | ACTIVE | Aug 1 → Sep 10
A001 | CLOSED | Sep 10 → current
```

It answers:

> "How did this business entity change over time?"

---

## Delta Time Travel

Time Travel provides table-level historical states.

Example:

```
Delta Version 10
Delta Version 11
Delta Version 12
```

It answers:

> "What did the Delta table look like at a previous point in time?"

### Key distinction

SCD2:

* Business history
* Deliberately modeled in the table
* Entity-level history

Time Travel:

* Delta table history
* Maintained through Delta's transaction log
* Table-state-level history

---

# 9. UPDATE

Delta supports SQL UPDATE operations.

Example:

```sql
UPDATE table_name
SET status = 'CLOSED'
WHERE account_id = 'A002';
```

An UPDATE is a transactional Delta operation and can create a new table version.

---

# 10. DELETE

Delta supports SQL DELETE.

Example:

```sql
DELETE FROM table_name
WHERE account_id = 'A004';
```

The record is removed from the current table state.

However, an earlier Delta version may still contain the record and can be queried using Time Travel, provided the required historical information/files are still available.

---

# 11. MERGE / UPSERT

`MERGE` allows matched and unmatched records to be handled in one operation.

Conceptually:

```
Incoming Data
      ↓
    MERGE
   /     \
Match   No Match
  ↓         ↓
```

UPDATE     INSERT

Example:

```sql
MERGE INTO target AS target

USING source AS source

ON target.account_id = source.account_id

WHEN MATCHED THEN
    UPDATE SET
        target.account_type = source.account_type,
        target.status = source.status

WHEN NOT MATCHED THEN
    INSERT (
        account_id,
        account_type,
        status
    )
    VALUES (
        source.account_id,
        source.account_type,
        source.status
    );
```

### Example

Target:

```
A001 | SAVINGS | ACTIVE
A002 | CURRENT | ACTIVE
A003 | SAVINGS | ACTIVE
```

Incoming:

```
A002 | CURRENT | CLOSED
A004 | SAVINGS | ACTIVE
```

After MERGE:

```
A001 | SAVINGS | ACTIVE
A002 | CURRENT | CLOSED   ← UPDATE
A003 | SAVINGS | ACTIVE
A004 | SAVINGS | ACTIVE   ← INSERT
```

### Interview answer

"Delta MERGE allows me to atomically handle matched and unmatched records, making it useful for incremental upserts and CDC-based processing."

---

# 12. DELETE + SCD1

SCD1 keeps only the current state.

If CDC provides:

```
A002 | DELETE
```

Then SCD1 can physically remove the current record:

```sql
DELETE FROM silver.accounts
WHERE account_id = 'A002';
```

Or using MERGE:

```sql
MERGE INTO silver.accounts AS target

USING account_cdc AS source

ON target.account_id = source.account_id

WHEN MATCHED
AND source.change_type = 'DELETE'
THEN DELETE;
```

### SCD1 DELETE

```
CDC DELETE
    ↓
Match target
    ↓
DELETE
    ↓
Record removed from current state
```

No historical version is retained by SCD1.

---

# 13. DELETE + SCD2

SCD2 preserves historical versions.

For a DELETE event, we normally don't physically delete the historical record.

Instead:

```
Current record
     ↓
expire it
     ↓
is_current = false
     ↓
is_deleted = true
```

Example:

Before:

```
A002 | CURRENT | CLOSED
effective_from = 2026-09-17
effective_to   = 9999-12-31
is_current     = true
is_deleted     = false
```

After DELETE:

```
A002 | CURRENT | CLOSED
effective_from = 2026-09-17
effective_to   = 2026-09-18
is_current     = false
is_deleted     = true
```

Example MERGE:

```sql
MERGE INTO silver.accounts_scd2 AS target

USING (
    SELECT
        account_id,
        change_timestamp
    FROM account_cdc
    WHERE change_type = 'DELETE'
) AS source

ON target.account_id = source.account_id
AND target.is_current = true

WHEN MATCHED THEN
    UPDATE SET
        target.effective_to = source.change_timestamp,
        target.is_current = false,
        target.is_deleted = true;
```

### SCD2 DELETE mental model

```
DELETE event
     ↓
Expire current version
     ↓
Preserve history
     ↓
Mark as deleted
```

---

# 14. SCD2 UPDATE

For an UPDATE event:

```
Old version
     ↓
Expire old version
     ↓
Insert new version
```

Example:

Before:

```
A002 | CURRENT | ACTIVE
effective_from = 2026-08-01
effective_to   = 9999-12-31
is_current     = true
```

After update:

```
A002 | CURRENT | ACTIVE
2026-08-01 → 2026-09-17
is_current = false

A002 | CURRENT | CLOSED
2026-09-17 → 9999-12-31
is_current = true
```

### Key distinction

SCD1 UPDATE:

* Overwrite current value

SCD2 UPDATE:

* Expire old version
* Insert new version

---

# 15. OPTIMIZE

Purpose:

> Improve physical data layout and query performance.

Conceptually:

```
Many small files
      ↓
   OPTIMIZE
      ↓
Fewer/larger files
      ↓
Better read performance
```

OPTIMIZE primarily affects the physical organization of data, not the logical/business meaning of the records.

OPTIMIZE is also a transactional Delta operation and can create a new table version.

Example history:

```
Version 2 → UPDATE
Version 3 → OPTIMIZE
```

---

# 16. VACUUM

Purpose:

> Remove obsolete physical data files that are no longer needed after the configured retention period.

Conceptually:

```
Current files
    ↓
  KEEP

Old obsolete files
    ↓
  VACUUM
    ↓
  REMOVE
```

VACUUM is primarily a storage cleanup operation.

---

# 17. OPTIMIZE vs VACUUM

| OPTIMIZE                       | VACUUM                                           |
| ------------------------------ | ------------------------------------------------ |
| Performance optimization       | Storage cleanup                                  |
| Reorganizes/compacts files     | Removes obsolete files                           |
| Improves physical file layout  | Reduces storage usage                            |
| Can create a new Delta version | Can remove files needed for very old Time Travel |

### Interview answer

"OPTIMIZE improves Delta table performance by compacting/reorganizing data files, while VACUUM removes obsolete data files that are no longer needed after the configured retention period."

---

# 18. VACUUM Retention

VACUUM retention can be configured.

Example:

```sql
VACUUM table_name RETAIN 168 HOURS;
```

168 hours = 7 days.

Example for 30 days:

```sql
VACUUM table_name RETAIN 720 HOURS;
```

720 hours = 30 days.

### Production consideration

Retention should be chosen based on:

* Recovery requirements
* Time Travel requirements
* Concurrent job requirements
* Storage cost

Do not casually use very short retention periods.

### Important

VACUUM does NOT simply mean:

> "Delete old Delta versions."

It removes obsolete **physical data files** that are outside the configured retention period.

---

# 19. Time Travel + VACUUM

Time Travel requires the historical information and underlying historical data files needed to reconstruct the requested table state.

Therefore:

```
Time Travel
     ↓
Historical files available?
     ↓
   YES → Query old version
     ↓
    NO → Old state may no longer be available
```

So Time Travel should not be treated as the only backup/recovery mechanism.

---

# 20. Important Delta Mental Model

```
DELTA TABLE
     │
     ├── Data Files
     │      └── Actual data
     │
     └── Transaction Log
            │
            ├── ACID
            ├── Table Versions
            ├── History
            ├── Time Travel
            └── Transactional Changes

Delta DML
     │
     ├── INSERT
     ├── UPDATE
     ├── DELETE
     └── MERGE

Delta Maintenance
     │
     ├── OPTIMIZE → Performance
     └── VACUUM   → Storage Cleanup
```

---

# 21. Interview Quick Answers

### What is Delta Lake?

"Delta Lake is a storage layer that provides reliable transactional capabilities such as ACID transactions, schema enforcement, Time Travel, and DML operations on data stored in formats such as Parquet."

### What is the Delta transaction log?

"The transaction log maintains the transactional state and history of a Delta table, including changes to data files and table metadata."

### What is Time Travel?

"Time Travel allows querying a Delta table as it existed at a previous version or timestamp."

### What is MERGE?

"MERGE allows matched and unmatched source records to be handled in a single transactional operation, commonly used for upserts and CDC processing."

### OPTIMIZE vs VACUUM?

"OPTIMIZE is for physical file/layout optimization and query performance; VACUUM removes obsolete physical data files after the configured retention period."

### SCD2 vs Time Travel?

"SCD2 models business-level historical changes for entities, while Delta Time Travel provides access to previous states of the Delta table itself."

---

# 22. Project Mapping

In the FinTech Data Platform:

```
Bronze
  ↓
Delta tables
  ↓
Silver
  ↓
Delta tables
  ↓
Gold
  ↓
Delta tables
```

Delta capabilities used/learned across the project:

* Delta tables
* Transaction log
* ACID transactions
* Time Travel
* MERGE
* UPDATE
* DELETE
* OPTIMIZE
* VACUUM
* Schema enforcement
* Schema evolution
* SCD1
* SCD2
* CDC

Important:
Schema enforcement and schema evolution were covered separately as dedicated project topics.

