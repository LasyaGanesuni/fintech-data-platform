

# ☁️ Azure / ADF — 10 Interview Scenarios

---

## 1. ADF Pipeline Suddenly Becomes Slow

### Scenario

Pipeline normally takes 30 min → suddenly takes 2 hours.

### Approach

Start with:

**ADF Monitor → identify the slow activity**

Then determine whether the bottleneck is:

### Copy Activity

Check:

* Source performance
* Sink performance
* Data volume
* File sizes
* Integration Runtime
* Network/connectivity
* Throughput

### Databricks Activity

Check Spark UI for:

* Shuffle
* Skew
* Spill
* CPU
* Memory
* Execution plan
* Data-volume changes

### Mental model

```text
ADF Monitor
     ↓
Which activity is slow?
     ↓
 ┌──────────────┬──────────────┐
 Copy          Databricks
  ↓                ↓
Source/sink      Spark UI
IR               Shuffle/skew
Network          Spill/CPU/memory
  ↓                ↓
     Find bottleneck
           ↓
        Optimize
```

### Interview line

> “I would first identify which activity is responsible for the additional execution time rather than assuming ADF itself is the bottleneck.”

---

# 2. Late-Arriving Source File

### Scenario

Pipeline scheduled at 6 PM.

File arrives at 6:15 PM.

### Approach

Don't immediately fail because the file isn't there.

Possible approaches:

### Fixed schedule

```text
6:00
 ↓
Check file
 ↓
Not available
 ↓
Wait
 ↓
Check again
 ↓
File arrives
 ↓
Continue
```

Use:

* File existence check
* Wait activity
* Controlled retry/check loop
* Timeout

### Event-driven

If the process is naturally **file-arrival driven**, use an event-based trigger.

```text
File arrives
    ↓
Event trigger
    ↓
ADF pipeline
```

### Important distinction

**Wait/check**

→ File hasn't arrived yet.

**Retry**

→ Activity encountered a transient failure.

### Interview line

> “If the process is file-arrival driven, I'd consider an event-based trigger. If it must run on a schedule, I'd use a controlled file-existence check with a timeout and appropriate failure handling.”

---

# 3. On-Prem SQL Connection Timeout

### Scenario

ADF → On-prem SQL Server suddenly gives a connection timeout.

### First check

**ADF Monitor → exact error**

Then:

```text
ADF
 ↓
Self-hosted Integration Runtime
 ↓
Network
 ↓
On-prem SQL Server
```

### Investigate

**Self-hosted IR**

* Is it online?
* Is it healthy?
* Are other pipelines using it affected?

**Network**

* Firewall
* DNS
* Port accessibility
* Connectivity

**SQL Server**

* Is server available?
* Is it overloaded?
* Is the query/source operation slow?

### Mental model

```text
ADF Monitor
     ↓
Exact error
     ↓
Self-hosted IR
     ↓
Network / firewall / DNS / port
     ↓
SQL Server
     ↓
Source query performance
```

### Interview line

> “For an on-premises source, I'd specifically investigate the Self-hosted Integration Runtime and the connectivity path between ADF and the SQL Server.”

---

# 4. Full Load → Incremental Load

### Scenario

100 million records daily.

Current design:

```text
Full load every day
```

Business wants only new/changed records.

### Approach

Use an **incremental mechanism**.

For SQL Server, a common approach is a **watermark** such as:

```text
updated_at
```

Maintain:

```text
last_successful_watermark
```

### Flow

```text
Control table
     ↓
ADF Lookup
     ↓
Last watermark
     ↓
SQL Server
     ↓
WHERE updated_at > watermark
     ↓
ADLS
     ↓
Databricks
     ↓
SUCCESS
     ↓
Update watermark
```

### Critical rule

**Update watermark only after successful processing.**

Otherwise:

```text
Watermark updated
      ↓
Pipeline fails
      ↓
Records may be skipped next run
```

### Alternatives

Depending on source capability:

* Watermark
* CDC
* Change Tracking

### Interview distinction

```text
File source
→ processed-file tracking

Database source
→ watermark / CDC / Change Tracking
```

---

# 5. ADF Activity Dependencies

### Scenario

```text
Copy Customer
      ↓
Copy Account
      ↓
Databricks Silver
      ↓
Databricks Gold
      ↓
Success Notification
```

`Copy Account` fails.

### Expected behavior

If Silver requires both Customer and Account:

```text
Copy Account
     ↓
   FAIL
     ↓
Silver → NOT RUN
     ↓
Gold → NOT RUN
```

Instead:

```text
Failure
   ↓
Failure handling
   ├── Log
   ├── Alert
   └── Retry if appropriate
```

### ADF dependency conditions

Remember:

* **Succeeded**
* **Failed**
* **Skipped**
* **Completed**

For normal downstream processing:

> **Use Succeeded dependency when the downstream activity requires successful upstream completion.**

### Interview line

> “I would explicitly configure dependencies based on the business dependency between activities rather than simply connecting activities sequentially.”

---

# 6. Transient Failure → Retry + Logging

### Scenario

Copy Activity occasionally fails because of a temporary network issue but succeeds when manually rerun.

### Solution

Use:

```text
Copy Activity
      ↓
Retry policy
      ↓
Still failing?
      ↓
Failure path
      ↓
Log
      ↓
Alert
```

### Retry

Useful for:

* Temporary network problems
* Transient service errors
* Temporary connectivity issues

### Failure logging

Maintain an audit/control table such as:

```text
pipeline_name
run_id
activity_name
status
error_message
error_code
start_time
end_time
logged_at
```

### Remember

```text
Retry
→ Attempt automatic recovery

Logging
→ Record what happened

Alerting
→ Notify someone
```

### Interview line

> “I'd configure retries for transient failures and a failure dependency path that records the error details and triggers an alert if retries are exhausted.”

---

# 7. Metadata-Driven ADF Pipeline

### Scenario

50 source tables need to be ingested.

Don't create:

```text
50 separate pipelines
```

Instead use:

**Metadata-driven architecture**

### Control table

Could contain:

```text
table_name
target_path
load_type
watermark_column
```

Example:

```text
customers      | /customers      | FULL
accounts       | /accounts       | INCREMENTAL
transactions   | /transactions   | INCREMENTAL
```

### Pipeline

```text
Metadata table
      ↓
Lookup
      ↓
ForEach
      ↓
Copy Activity
      ↓
Dynamic source/target
```

Inside ForEach, configuration can drive:

```text
@item().table_name
@item().target_path
@item().load_type
```

### Why metadata-driven?

Instead of changing pipeline logic:

```text
Add new table
     ↓
Add metadata
     ↓
Same pipeline processes it
```

### Interview line

> “I would externalize table-specific configuration into a metadata/control table and build a reusable ADF pipeline around that metadata.”

---

# 8. Full vs Incremental Dynamically

### Scenario

Some tables are full load, others incremental.

### Solution

Add:

```text
load_type
```

to metadata.

Values:

```text
FULL
INCREMENTAL
```

### Pipeline

```text
Control Table
      ↓
Lookup
      ↓
ForEach
      ↓
Check load_type
   ↙          ↘
FULL       INCREMENTAL
 ↓              ↓
Full Copy    Read watermark
                 ↓
            Incremental query
```

For incremental tables, metadata could additionally contain:

```text
watermark_column
```

Example:

```text
accounts
load_type = INCREMENTAL
watermark_column = updated_at
```

### Interview line

> “I'd use metadata to determine the load strategy dynamically, so the same pipeline can support both full and incremental ingestion.”

---

# 9. Too Much ForEach Parallelism

### Scenario

50 tables run simultaneously and overload SQL Server.

### Problem

```text
50 tables
   ↓
High concurrency
   ↓
SQL Server overloaded
   ↓
Queries slow down
```

### Solution

Control ForEach concurrency using **batch count**.

Example concept:

```text
50 tables
   ↓
Batch count = 5
   ↓
5 tables at a time
```

Instead of:

```text
50 tables
   ↓
50 concurrent copies
```

### Investigate

* Source CPU/resource usage
* Copy durations
* Number of concurrent activities
* Whether performance improves when concurrency decreases

### Important

> **More parallelism ≠ always faster**

Too much concurrency can create contention and actually make the entire pipeline slower.

### Mental model

```text
Concurrency
     ↓
Source capacity
     ↓
Tune batch count
     ↓
Monitor throughput
```

---

# 10. Databricks Fails After ADF Copy Succeeds

### Scenario

```text
ADF Copy
   ↓
SUCCESS ✓
   ↓
ADLS
   ↓
Databricks
   ↓
FAIL ❌
```

You don't want to copy millions of records again.

### Solution

Design the pipeline to be **restartable**.

Since the data already exists in ADLS:

```text
ADLS
 ↓
Retry/restart Databricks
 ↓
Process landed data
```

Don't unnecessarily rerun the successful Copy Activity.

### But also ensure idempotency

If Databricks processes the same data again:

```text
Retry
 ↓
Same data
 ↓
No duplicates
```

Techniques can include:

* Processed-file tracking
* Checkpoints
* Business keys
* MERGE/upsert
* Deterministic transformations

### Key concepts

**Restartability**

→ Recover from the failed stage without repeating successful work.

**Idempotency**

→ Reprocessing the same input doesn't create incorrect duplicate results.

### Interview line

> “I would design the pipeline so that individual stages can be restarted independently and make the downstream processing idempotent. That allows me to retry the failed Databricks stage using the data already landed in ADLS.”

---

# 🧠 AZURE INTERVIEW MASTER CHEAT SHEET

```text
ADF PERFORMANCE ISSUE
→ Monitor
→ Identify slow activity
→ Investigate specific bottleneck

LATE FILE
→ File check + Wait/timeout
→ Or event-based trigger

CONNECTION TIMEOUT
→ Self-hosted IR
→ Network
→ Firewall/DNS/port
→ Source availability

FULL → INCREMENTAL
→ Watermark / CDC / Change Tracking
→ Update watermark after success

DEPENDENCIES
→ Succeeded / Failed / Skipped / Completed
→ Downstream only after required upstream success

TRANSIENT FAILURE
→ Retry
→ Failure path
→ Log
→ Alert

50 TABLES
→ Metadata/control table
→ Lookup
→ ForEach
→ Dynamic Copy

FULL + INCREMENTAL
→ load_type in metadata
→ If Condition

SOURCE OVERLOAD
→ Reduce ForEach batch count
→ Control concurrency

DATABRICKS FAILURE
→ Don't rerun successful ingestion unnecessarily
→ Restart failed stage
→ Ensure idempotency
```

## ⭐ The Azure interview mindset

For almost every ADF scenario:

> **Monitor → identify the failing/slow component → understand the root cause → use the appropriate ADF feature → make the pipeline restartable and observable.**

And keep these distinctions clear:

```text
Parameterization → make pipeline reusable

Metadata-driven → configuration controls behavior

Dependency → controls execution order

Retry → handles transient failures

Logging → records failures/execution

Trigger → determines when pipeline starts

Watermark → determines which data to process

Idempotency → makes reprocessing safe

Batch count → controls parallelism
```

