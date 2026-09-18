# Databricks Compute — Interview Skim Notes

## 1. Cluster Sizing

Cluster sizing = deciding **worker type + worker count** based on workload requirements.

Don't determine cluster size from data volume alone.

Consider:

* Data volume
* Batch vs streaming
* SLA / latency requirement
* CPU vs memory intensity
* Join / aggregation / window complexity
* Shuffle volume
* Data skew
* Data distribution
* Workload variability

### Basic process

```text
Workload
   ↓
Understand requirements
   ↓
CPU / Memory / Shuffle characteristics
   ↓
Choose worker type
   ↓
Choose initial worker count
   ↓
Run representative workload
   ↓
Spark UI
   ↓
Tune & benchmark
```

**Interview:**

> "I size compute based on workload characteristics and SLA rather than row count alone."

---

## 2. CPU-Heavy Workload

Examples:

* Complex transformations
* Heavy expressions
* Large aggregations

Think:

```text
CPU-heavy
   ↓
CPU-oriented compute
   ↓
Monitor CPU utilization
   ↓
Tune worker capacity / parallelism
```

If CPU is consistently saturated while memory is healthy, increasing CPU capacity/parallelism may help.

---

## 3. Memory-Heavy Workload

Examples:

* Large joins
* Large sorts
* Windows
* Memory-intensive aggregations

Think:

```text
Memory-heavy
   ↓
Memory-optimized compute
   ↓
Monitor memory + spill
   ↓
Tune memory capacity
```

Don't immediately add workers—first understand whether the bottleneck is **memory per worker** or overall parallelism.

---

## 4. Batch Workload

Batch = data processed in discrete jobs.

For batch sizing, consider:

* Data volume per run
* Processing complexity
* SLA
* Frequency
* Variability in data volume

Example:

```text
100 GB → 200 GB → 800 GB
```

Variable workload → autoscaling may be useful.

Predictable:

```text
500 GB every day
```

→ stable compute configuration can be evaluated.

**Important:** Batch itself doesn't tell you whether the workload is CPU- or memory-heavy.

---

## 5. Streaming Workload

For streaming, **historical data volume isn't the main sizing metric**.

Focus on:

* Input/arrival rate
* Processing rate
* Processing latency
* Backlog
* SLA
* CPU
* Memory
* Shuffle
* Spill
* Workload variability

Key requirement:

```text
Processing rate ≥ Input rate
```

Otherwise backlog grows.

For your FinTech project:

```text
Kafka
 ↓
Structured Streaming
 ↓
Bronze
```

If the freshness SLA is <5 minutes, compute needs to keep processing fast enough to maintain that SLA.

---

## 6. Autoscaling

Autoscaling dynamically adjusts worker capacity within configured limits.

Example:

```text
Min = 2
Max = 8

Low demand  → 2 workers
High demand → 8 workers
```

Useful for **variable workloads**.

### Important

Autoscaling does NOT fix:

* Data skew
* `repartition(1)`
* Excessive shuffle
* Bad joins
* Poor query design

> **Autoscaling manages compute capacity; it doesn't replace Spark optimization.**

---

## 7. Workload-Specific Compute

Different workloads may require different compute characteristics.

```text
Batch ETL
Streaming
SQL / BI
Large joins
ML
Development
```

Examples:

```text
CPU-heavy → CPU-oriented compute
Memory-heavy → Memory-oriented compute
Variable workload → Autoscaling
Interactive workload → Responsive compute
```

Separating workloads can provide:

* Performance isolation
* Predictable SLAs
* Independent scaling
* Better cost management
* Easier troubleshooting

---

# ⭐ Interview Scenario Framework

### "You have 500 GB. How do you size the cluster?"

Don't say:

> "500 GB → 8 workers."

Instead:

> **"I wouldn't determine cluster size from the 500 GB volume alone. I'd first understand the workload type, SLA, transformation complexity, join and aggregation patterns, data distribution, and expected shuffle. Based on whether it's CPU- or memory-intensive, I'd select an appropriate worker type and establish an initial worker count. If the workload varies, I'd consider autoscaling. Then I'd run a representative workload, inspect Spark UI for CPU, memory, shuffle, spill, skew and task distribution, and tune based on the observed bottleneck."**

---

## If interviewer gives more information

| They say...            | Think...                               |
| ---------------------- | -------------------------------------- |
| **CPU-heavy**          | CPU-oriented compute                   |
| **Memory-heavy**       | Memory-oriented compute                |
| **Large join**         | Broadcast / shuffle / memory / skew    |
| **Large aggregation**  | Shuffle + CPU                          |
| **Large window**       | Shuffle + sort + memory                |
| **Data skew**          | AQE / salting / broadcast              |
| **Batch**              | SLA + volume + variability             |
| **Streaming**          | Input rate + processing rate + latency |
| **Variable volume**    | Autoscaling                            |
| **Predictable volume** | Stable compute can be evaluated        |
| **High spill**         | Investigate memory/workload            |
| **High CPU**           | Investigate CPU capacity/parallelism   |
| **One slow task**      | Investigate skew                       |

---

## ⭐ The most important mental model

```text
DATA VOLUME
     ↓
WORKLOAD TYPE
     ↓
SLA
     ↓
CPU vs MEMORY
     ↓
WORKER TYPE
     ↓
INITIAL WORKER COUNT
     ↓
AUTOSCALING?
     ↓
RUN
     ↓
SPARK UI
     ↓
CPU / MEMORY / SHUFFLE / SPILL / SKEW
     ↓
TUNE
     ↓
BENCHMARK AGAIN
```

### One line to remember

> **"Cluster sizing is an iterative capacity-planning process, not a fixed formula based on data volume."**
