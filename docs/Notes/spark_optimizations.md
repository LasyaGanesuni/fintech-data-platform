

# Spark & Delta Optimization — Interview Skim Notes

## 1. Spark Execution Fundamentals

### Lazy Evaluation

* Spark transformations are **lazy**.
* Spark builds an execution plan but doesn't execute immediately.
* Execution begins when an **action** is called.
* Benefits: Spark can optimize the complete plan before execution.

```text
Transformations → Execution Plan → Action → Execution
```

### Transformations vs Actions

**Transformations**

* `filter()`
* `select()`
* `withColumn()`
* `join()`
* `groupBy()`
* `repartition()`

Return a new DataFrame and are generally lazy.

**Actions**

* `count()`
* `show()`
* `collect()`
* `first()`
* `take()`
* `write`

Trigger execution.

---

## 2. Logical vs Physical Plan

```python
df.explain("formatted")
```

### Logical Plan

What Spark intends to do.

### Physical Plan

How Spark will actually execute it.

Typical flow:

```text
PySpark / SQL
      ↓
Logical Plan
      ↓
Catalyst Optimization
      ↓
Physical Plan
      ↓
Execution
```

---

## 3. Catalyst Optimizer

Spark SQL's query optimizer.

It analyzes and optimizes the query plan before execution.

Examples of optimizations include:

* Predicate/filter pushdown
* Column pruning
* Simplifying expressions
* Choosing execution strategies

**Interview:**

> Catalyst optimizes Spark SQL/DataFrame execution plans before execution.

---

## 4. Tungsten / Whole-Stage Code Generation

### Tungsten

Spark's execution improvements focused on:

* Memory efficiency
* CPU efficiency
* Binary/compact data representation
* Reduced object overhead

### Whole-stage code generation

Spark can combine multiple operations and generate optimized code for execution.

**Remember:**

```text
Catalyst → optimizes the plan
Tungsten/codegen → improves execution efficiency
```

---

# 5. Narrow vs Wide Transformations

### Narrow Transformation

Data doesn't need to be redistributed across partitions.

Examples:

* `filter`
* `select`
* many `withColumn` operations

```text
Partition 1 → Partition 1
Partition 2 → Partition 2
```

### Wide Transformation

Data needs redistribution → **shuffle**.

Examples:

* `groupBy`
* `join`
* `distinct`
* `orderBy`
* many window operations

```text
Partition 1 ─┐
Partition 2 ─┼→ Shuffle → New partitions
Partition 3 ─┘
```

---

# 6. Shuffle

Shuffle = redistribution of data across Spark partitions.

Common causes:

* `groupBy`
* joins
* `distinct`
* `orderBy`
* windows
* `repartition`

### Why expensive?

* Network data movement
* Serialization
* Disk I/O
* Scheduling overhead

**Interview:**

> Shuffle isn't automatically bad; it's expensive when the amount of data redistributed is large or poorly distributed.

---

# 7. Partitioning

Spark divides data into partitions so work can execute in parallel.

```text
100 GB
 ↓
Partition 1
Partition 2
...
Partition N
```

More partitions ≠ automatically better.

Too few → poor parallelism.

Too many → scheduling/metadata overhead.

---

# 8. `repartition()` vs `coalesce()`

### `repartition()`

```python
df.repartition(10)
```

* Can increase or decrease partitions
* Causes shuffle
* Can repartition by a column

```python
df.repartition(10, "account_id")
```

### `coalesce()`

```python
df.coalesce(10)
```

* Primarily reduces partitions
* Generally avoids a full shuffle
* Usually cheaper when simply reducing partitions

### Trap

```python
df.repartition(1)
```

on large data can create a single-task bottleneck.

---

# 9. Partition Pruning

Used when a Delta/table is physically partitioned.

Example:

```text
transaction_date=2026-08-13
transaction_date=2026-08-14
transaction_date=2026-08-15
```

Query:

```sql
WHERE transaction_date = '2026-08-14'
```

Spark can skip the other partitions.

> **Partition pruning = skip entire physical partitions.**

---

# 10. Predicate Pushdown

Push filters closer to the data source/scan.

Instead of:

```text
Read everything
 ↓
Filter
```

Spark/data source can often do:

```text
Read only relevant data
 ↓
Filter
```

Reduces data read.

---

# 11. Column Pruning

Read only the columns required by the query.

Instead of:

```python
df.select("*")
```

if you only need:

```python
df.select("account_id", "amount")
```

Spark can avoid unnecessary columns where supported.

> Less data read → less memory → less processing.

---

# 12. Avoid Unnecessary Scans

General principle:

> **Don't process data you don't need.**

Use:

* Early filtering
* Column pruning
* Partition pruning
* Data skipping
* Appropriate joins

---

# 13. Data Skew

Data skew = uneven distribution of records across partitions.

Example:

```text
A001 → 1K
A002 → 2K
A999 → 50M   🚨
```

One partition/task may become much larger.

Symptoms in Spark UI:

* One/few tasks much slower
* Uneven shuffle sizes
* Straggler tasks

Solutions:

* AQE skew optimization
* Broadcast join where appropriate
* Salting for severe skew
* Better key/distribution strategy

---

# 14. Broadcast Join

If one side of a join is sufficiently small, Spark can broadcast it to executors.

```python
transactions.join(
    F.broadcast(accounts),
    "account_id"
)
```

Conceptually:

```text
Small table
   ↓
Broadcast to executors

Large table
   ↓
No need to redistribute the entire large side
```

Benefits:

* Can avoid large shuffle
* Often faster for large + small joins

Risk:

* Broadcasting something too large can cause memory pressure/OOM.

Look for:

```text
BroadcastHashJoin
```

in the execution plan.

---

# 15. AQE — Adaptive Query Execution

AQE adapts Spark's execution plan **at runtime** using actual statistics.

Important capabilities:

* Coalescing post-shuffle partitions
* Handling skewed joins
* Potentially changing join strategies

If you see:

```text
AdaptiveSparkPlan
```

AQE is involved.

### Remember

> AQE does not mean "no shuffle."

AQE can optimize a plan that still contains shuffle.

---

# 16. Caching / Persistence

Use when an expensive DataFrame is **reused multiple times**.

```python
df.cache()
```

or:

```python
df.persist(StorageLevel.MEMORY_AND_DISK)
```

Caching is lazy; an action materializes it.

Remove when no longer needed:

```python
df.unpersist()
```

### Don't cache everything.

Caching consumes executor resources and can cause memory pressure.

---

# 17. Avoid `collect()`

```python
df.collect()
```

brings all rows to the **driver**.

Dangerous for large datasets.

Safer for small results:

```python
df.limit(10).collect()
```

---

# 18. Avoid Unnecessary Actions

Actions trigger execution:

```python
count()
show()
collect()
write()
```

Repeated actions can cause repeated computation.

Avoid production code like:

```python
df.count()
df.count()
df.show()
df.write(...)
```

unless those actions are actually required.

---

# 19. Small Files Problem

Many tiny files create overhead:

```text
10,000 tiny files
      ↓
File listing/opening
Task scheduling
Metadata overhead
      ↓
Slower processing
```

Common with frequent incremental/streaming writes.

### Solution

Delta:

```sql
OPTIMIZE table_name;
```

compacts/reorganizes files.

---

# 20. OPTIMIZE

Improves physical layout by compacting/reorganizing Delta files.

It doesn't change the logical business data.

```sql
OPTIMIZE table_name;
```

Can create a new Delta table version because it is a transactional operation.

---

# 21. Z-Ordering

Organizes data based on selected columns to improve data locality and data skipping.

```sql
OPTIMIZE transactions
ZORDER BY (account_id);
```

Good candidates are columns frequently used in selective filters.

Don't Z-Order every column.

### Mental model

```text
Z-Order
   ↓
Better data organization
   ↓
Better data skipping
   ↓
Fewer files read
```

---

# 22. Data Skipping

Delta can use **file-level statistics** to determine whether a file could contain matching records.

Statistics can include information such as:

* Min values
* Max values
* Null information
* Record counts

Example:

```text
File 1 → amount 10–500
File 2 → amount 501–1000
File 3 → amount 1001–5000
```

Query:

```sql
WHERE amount > 4000
```

Files 1 and 2 can potentially be skipped.

> **Data skipping = skip irrelevant files using file-level statistics.**

---

# 23. Liquid Clustering

A modern Delta data-layout approach.

Conceptually:

```text
CLUSTER BY (account_id)
```

It provides a more flexible/adaptive approach to organizing data around commonly queried columns.

Think:

```text
Traditional:
Partitioning + Z-Ordering

Modern approach:
Liquid Clustering
```

Don't automatically introduce it everywhere; choose based on workload and table characteristics.

---

# 24. Delta Partitioning

Physical organization based on partition column values.

Example:

```text
transaction_date=2026-08-13/
transaction_date=2026-08-14/
```

Good partition candidates generally have:

* Appropriate cardinality
* Frequent filtering
* Meaningful data per partition

Avoid high-cardinality columns such as:

```text
transaction_id
```

for typical partitioning.

---

# 25. Over-Partitioning

Too many partitions can cause:

* Many small files
* Metadata overhead
* File-management overhead
* Poor performance

Don't partition every frequently filtered column.

> Partitioning is a workload/data-volume decision, not a default requirement.

---

# 26. File Size

Goal:

> **Reasonable number of reasonably sized files.**

Too small:

```text
Many files → overhead
```

Too large:

```text
Very few huge files → can limit parallelism
```

OPTIMIZE can help maintain a healthier physical layout.

---

# 27. Delta Statistics

Delta maintains file-level statistics used by query optimization/data skipping.

Think:

```text
Data file
 ↓
Statistics
 ↓
Query predicate
 ↓
Can file contain matching data?
 ↓
No → Skip
Yes/maybe → Read
```

---

# 28. Bucketing

Bucketing distributes data into a fixed number of **hash-based buckets**.

Conceptually:

```text
hash(account_id) % number_of_buckets
```

Example:

```text
hash("A1001") % 10
       ↓
bucket 7
```

Can be useful for large datasets with repeated joins on the same key.

### Important

Don't memorize:

> High cardinality = bucket.

Instead:

> **Large data + suitable cardinality/distribution + repeated joins on the same key = situation where bucketing may be worth evaluating.**

---

# 29. Salting

Used for severe data skew.

Hot key:

```text
A999 → 50M records
```

Add artificial salt:

```text
A999_0
A999_1
...
A999_9
```

This spreads the hot key across multiple partitions.

Often requires corresponding salted keys on the smaller side.

### Don't use by default.

Only use after identifying genuine skew.

---

# 30. Window Optimization

Windows can be expensive because they may require:

```text
Shuffle
 +
Sort
```

Optimize by:

* Filtering early
* Selecting only required columns
* Avoiding unnecessary windows
* Checking for skew in partitioning keys

Your deduplication:

```python
row_number().over(
    Window
    .partitionBy("customer_id")
    .orderBy(F.col("updated_at").desc())
)
```

is appropriate because you genuinely need the latest record.

---

# 31. Join Optimization

Before a large join:

### Reduce data

```text
Filter early
 ↓
Select required columns
 ↓
Join
```

Check:

* Join cardinality
* Join key
* Broadcast possibility
* Shuffle
* Skew
* Join explosion

Avoid accidental many-to-many joins.

---

# 32. Spark UI

Use Spark UI to diagnose **actual execution**, not just theoretical plans.

Look for:

* Stage duration
* Task duration
* Shuffle read/write
* Input/output size
* Memory spill
* Disk spill
* Uneven task distribution

### Example

```text
99 tasks → 10 sec
1 task  → 5 min
```

Investigate skew.

---

# 33. `explain("formatted")`

Useful for understanding the physical plan.

Look for:

```text
Exchange
```

→ Shuffle

```text
BroadcastHashJoin
```

→ Broadcast join

```text
SortMergeJoin
```

→ Shuffle/sort-based join

```text
Window
```

→ Window processing

```text
AdaptiveSparkPlan
```

→ AQE

```text
Photon...
```

→ Photon execution

---

# 34. Spill / Memory Pressure

When Spark doesn't have enough memory for intermediate data, it may spill data.

Common operations:

* Join
* Sort
* GroupBy
* Window
* OrderBy

Spark UI can show:

```text
Memory Spill
Disk Spill
```

Don't immediately increase memory.

First investigate:

* Excessive data
* Large shuffle
* Skew
* Unnecessary columns
* Inefficient join
* Expensive sort/window

---

# 35. Common Performance Traps

### ❌ `collect()` on huge data

→ Driver memory problem

### ❌ `repartition(1)`

→ Single-task bottleneck

### ❌ Excessive `repartition()`

→ Unnecessary shuffle

### ❌ Cache everything

→ Memory pressure

### ❌ Repeated actions

→ Repeated execution

### ❌ Filter after expensive operations

→ Process unnecessary data

### ❌ Carry unnecessary columns

→ More data through shuffle/join

### ❌ Ignore skew

→ Straggler tasks

### ❌ Use windows unnecessarily

→ Extra shuffle/sort

### ❌ Partition by high-cardinality columns

→ Too many partitions/files

---

# 36. Photon

Databricks' high-performance execution engine for supported workloads.

```text
PySpark / SQL
     ↓
Execution plan
     ↓
Photon
```

Photon and AQE are different:

```text
Photon → execution engine
AQE    → adaptive execution planning
```

Photon does **not** eliminate shuffle.

---

# 37. Serverless

Serverless means Databricks manages much of the underlying compute infrastructure.

Benefits:

* Less infrastructure management
* Managed scaling
* Simplified compute experience

But:

> **Serverless doesn't eliminate the need for Spark optimization.**

You still need to handle:

* Shuffle
* Skew
* Spill
* Data volume
* Joins
* File layout

---

# 38. Predictive Optimization

Databricks capability that automates certain supported Delta table maintenance/optimization tasks for eligible Unity Catalog managed tables.

Think:

```text
Manual:
OPTIMIZE → you decide when

Predictive Optimization:
Databricks automates supported maintenance decisions
```

Don't say it automatically makes every query faster.

---

# ⭐ Ultimate Interview Mental Model

If they ask:

**"How would you optimize a slow Spark job?"**

Your answer can follow this sequence:

```text
1. Check execution plan
        ↓
2. Check Spark UI
        ↓
3. Identify bottleneck
        ↓
 ┌──────────────┬──────────────┬──────────────┐
 ↓              ↓              ↓
Shuffle        Skew           Spill
 ↓              ↓              ↓
Join/groupBy   AQE/salting    Reduce data
 ↓
Broadcast?
        ↓
4. Check data volume
        ↓
Filter early
Column pruning
        ↓
5. Check Delta layout
        ↓
Partition pruning
Data skipping
Z-Order / clustering
Small files
        ↓
6. Re-run and compare
```

### The one sentence I'd remember most:

> **I don't optimize Spark blindly; I first use the execution plan and Spark UI to identify the actual bottleneck, then choose the appropriate optimization based on data volume, distribution, query pattern, and physical layout.**


