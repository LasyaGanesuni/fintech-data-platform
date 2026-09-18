

# ⚡ Spark / Databricks Optimization — 10 Interview Scenarios

---

## 1. Job suddenly becomes much slower

**Scenario:**
Job normally takes 30 min → suddenly takes 3 hours.

### Investigation

* Start with **Spark UI**
* Identify slow stages
* Check:

  * Shuffle read/write
  * Task duration
  * Input/output records
  * Spill
  * CPU/memory
  * Skew

### If shuffle is high

Investigate:

* Large joins
* `groupBy`
* `distinct`
* `repartition`
* Window functions

### If skew is present

Look for:

* Few tasks significantly slower
* Uneven shuffle data
* Hot keys

### Interview line

> “I’d start with Spark UI to identify the bottleneck rather than immediately changing compute. I’d inspect shuffle, skew, spill, CPU and memory to determine the root cause.”

---

# 2. Large Shuffle + Data Skew

**Scenario:**
A join has huge shuffle and 1–2 tasks take much longer.

### Investigation

Check:

* Task-level shuffle read/write
* Partition sizes
* Join-key distribution
* Hot keys

Example:

```text
A001 → 100 records
A002 → 200 records
A999 → 50 million records
```

`A999` can create a heavily skewed partition.

### Possible solutions

**1. Broadcast**

If one side is sufficiently small:

```text
Large table
     ↓
   JOIN
     ↑
Broadcast small table
```

Avoids shuffling the large side.

**2. Filter early**

Reduce rows before the join.

**3. Select required columns**

Reduce data being shuffled.

**4. AQE skew handling**

Allow Spark to handle certain skewed partitions.

**5. Salting**

For severe hot-key skew:

```text
A999 → A999_0
       A999_1
       A999_2
       ...
```

### Important

`repartition(account_id)` **doesn't automatically fix hot-key skew** because all records for the same key can still land together.

---

# 3. Large `groupBy` + One Very Slow Task

**Scenario:**

```python
df.groupBy("account_id").agg(...)
```

One task = 25 min
Other tasks = 2–3 min.

### Reasoning

`groupBy` is a **wide transformation**.

Therefore:

```text
groupBy
  ↓
Shuffle expected
```

But one task being dramatically slower suggests **possible skew**.

### Investigation

Check:

* Shuffle read/write
* Task sizes
* Task duration
* Distribution of `account_id`

### Solutions

* AQE skew handling
* Reduce data before aggregation
* Filter unnecessary records
* Select required columns
* Investigate hot keys
* Salting for severe aggregation skew

### Important

**Broadcast isn't relevant here** because there is no join.

---

# 4. High Spill During Window / Sort

**Scenario:**

Spark UI shows significant spill to disk during:

```text
Window
Sort
```

### Why?

Intermediate data doesn't fit comfortably in execution memory.

### Investigate

* Which stage is spilling?
* How much data reaches the operation?
* Is there skew?
* Are there unnecessary columns?
* Is the window processing more rows than necessary?

### Optimize

**Filter early**

```text
10M rows
   ↓
filter
   ↓
100K rows
   ↓
window
```

instead of:

```text
10M rows
   ↓
window
   ↓
filter
```

when logically safe.

Also:

* Select only required columns
* Avoid unnecessary windows
* Check window partition-key skew
* Review join/sort strategy if relevant

### If genuinely resource constrained

Consider:

* Memory-optimized compute
* More capacity

But **investigate the workload first**.

---

# 5. High CPU Utilization

**Scenario:**

* CPU consistently very high
* Memory reasonable
* Shuffle reasonable
* Spill not significant

### Diagnosis

Likely **CPU-bound workload**.

### Investigate

Look at:

* CPU utilization
* Expensive transformations
* Aggregations
* Complex expressions
* UDFs
* Overall task parallelism

### Possible solution

Use a more **CPU-oriented worker type** or increase compute capacity where appropriate.

Then:

```text
Change
 ↓
Run again
 ↓
Compare execution time
 ↓
Check Spark UI
```

### Interview line

> “If the workload is genuinely CPU-bound after ruling out other bottlenecks, I’d consider CPU-optimized compute and benchmark the workload again.”

---

# 6. High Memory + Spill

**Scenario:**

```text
Memory → Very high
Spill → High
```

### Don't immediately say:

> “I'll add more workers.”

First investigate.

### Check

* Large joins?
* Large sort?
* Window?
* Aggregation?
* Data skew?
* Too many columns?
* Too many rows?
* Inefficient transformation?

### Important distinction

If:

```text
Worker 1 → 95%
Worker 2 → 40%
Worker 3 → 35%
Worker 4 → 40%
```

→ investigate **skew**.

If:

```text
All workers → 90%+
All workers → spill
```

→ genuine **capacity/memory pressure** is more likely.

### Solutions

Depending on root cause:

* Reduce data earlier
* Optimize joins
* Address skew
* Reduce columns
* Memory-optimized worker type
* Increase worker capacity

---

# 7. Thousands of Small Files

**Scenario:**

50 GB data but tens of thousands of tiny files.

### Investigation

Spark UI / scan metrics:

```text
Huge number of files
        ↓
Many small tasks
        ↓
File overhead
```

Investigate why files were created:

* Frequent small writes
* Poor partitioning
* Excessive partition creation
* Streaming/write patterns

### Delta solution

**OPTIMIZE**

Compacts/reorganizes files into a more efficient layout.

### Z-Order?

Only if query patterns justify it.

Think:

```text
Small files
    ↓
OPTIMIZE
```

Whereas:

```text
Need better data locality/data skipping
    ↓
Consider Z-Order
```

### Important

**Z-Order is not the solution to small files itself.**

---

# 8. Join Explosion

**Scenario:**

```text
Input → 100 GB
Intermediate result → 800 GB
```

### Suspect

**Join explosion / unintended many-to-many relationship**

### Investigate

1. Is there a `CROSS JOIN`?
2. Is the join condition correct?
3. Are join keys unique?
4. Are there duplicate keys?
5. Is there an accidental many-to-many relationship?
6. Was a filter missing?

Example:

```text
Transactions
A001 → 1,000 rows

Accounts
A001 → 50 rows
```

Join:

```text
1,000 × 50
= 50,000 rows
```

### Fix

Depending on business logic:

* Correct join condition
* Deduplicate appropriate side
* Filter before join
* Validate key cardinality
* Ensure expected relationship

### Interview line

> “I wouldn't just look for a literal cross join. I'd also investigate whether duplicate join keys are creating an unintended many-to-many join.”

---

# 9. Streaming Backlog Increasing

**Scenario:**

Freshness SLA = 5 min.

But data is now:

```text
20 minutes behind
```

### Key concept

Compare:

```text
Input rate
     vs
Processing rate
```

If:

```text
Input rate > Processing rate
        ↓
Backlog increases
```

### Investigate

Streaming metrics:

* Input rate
* Processing rate
* Batch duration
* Backlog
* Processing latency
* Slow stages
* CPU
* Memory
* Shuffle
* Spill
* Skew

Also check:

* Did input volume suddenly increase?
* Did transformation complexity change?
* Did data distribution change?

### If capacity is genuinely insufficient

Consider scaling compute appropriately.

Goal:

```text
Processing rate ≥ Input rate
```

so backlog can stabilize/decrease.

### Important

Don't automatically add workers before identifying the bottleneck.

---

# 10. Wrong Partitioning Strategy

**Scenario:**

Huge Delta table.

Common queries:

```sql
WHERE transaction_date = ...
```

But table is partitioned by:

```text
account_id
```

where there are millions of distinct values.

### Problem

`account_id` is **high cardinality**.

This can create:

* Huge number of partitions
* Small files
* File-management overhead
* Poor partition pruning for date-based queries

### Better approach

Review workload and consider a more appropriate partitioning strategy, potentially:

```text
transaction_date
```

if it provides meaningful partition pruning and reasonable file sizes.

### Don't say

> “Always partition by the column in WHERE.”

Instead consider:

* Query patterns
* Cardinality
* Data volume
* Partition size
* File size
* Write patterns

---

# 🔥 Bonus: Broadcast Join

This appeared in multiple scenarios, so remember it separately.

### Scenario

```text
Large table → 1 TB
Small table → 500 MB
```

Current plan:

```text
SortMergeJoin
     ↓
Large shuffle
```

### Investigate

Can the smaller side be **broadcast**?

Conceptually:

```text
          Small table
              ↓
         Broadcast
       ↙     ↓     ↘
   Worker  Worker  Worker
       ↘     ↓     ↙
        Large table
```

Potential benefit:

**Avoid large shuffle of the join side.**

### But

500 MB isn't automatically safe.

Consider:

* Executor memory
* Actual size after filtering
* Broadcast threshold/configuration
* Overall workload

---

# 🧠 Ultimate Optimization Framework

For almost any Spark performance question:

```text
                Spark UI
                   ↓
          Identify bottleneck
                   ↓
       ┌───────────┼───────────┐
       ↓           ↓           ↓
    Shuffle      Spill        CPU
       ↓           ↓           ↓
    Join?       Memory?      CPU-bound?
    GroupBy?    Sort?        Compute?
    Window?     Window?      
       ↓           ↓           ↓
      Skew?      Skew?
       ↓           ↓
     AQE /       Reduce
    Broadcast    workload
    / Salting
                   ↓
            Compute change
             if necessary
                   ↓
             Run again
                   ↓
          Compare metrics
```

### ⭐ One sentence to remember for interviews

> **“I first use Spark UI to identify the actual bottleneck, then optimize the data processing or execution strategy based on the evidence, and only change compute when the workload is genuinely resource-bound.”**


