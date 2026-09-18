

# ADF Parameterization & Orchestration — Quick Interview Notes

## 1. Parameters vs Variables

### Parameter
- Read-only input to a pipeline.
- Used to make pipelines reusable/dynamic.
- Example:
  ```text
  file_name
  folder_path


### Variable

* Mutable runtime value.
* Used for status, counters, flags, etc.
* Example:

  ```text
  pipeline_status = FAILED
  ```

### Remember

```text
Parameter → What should I process?
Variable   → What is happening during execution?
```

---

## 2. Dynamic Content

Used to create values dynamically at runtime.

### Pipeline parameter

```text
@pipeline().parameters.file_name
```

### Dataset parameter

```text
@dataset().sink_folder
```

---

## 3. Pipeline vs Dataset Parameters

```text
Pipeline Parameter
       ↓
passes value
       ↓
Dataset Parameter
       ↓
actual source/sink path
```

Example:

```text
Pipeline:
file_name = customers.csv

        ↓

Dataset:
sink_file_name = customers.csv
```

**Names don't have to match.**

---

## 4. Why Parameterization?

Instead of hardcoding:

```text
raw/customers/2026-08-17/customers.csv
```

we use:

```text
raw/@pipeline().parameters.folder_path/@pipeline().parameters.file_name
```

### Benefits

* Reusable pipelines
* Less hardcoding
* Easier maintenance
* Supports metadata-driven ingestion

---

# 5. ADF Activity Dependencies

Controls when a downstream activity runs based on the previous activity's status.

### Four conditions

```text
Succeeded
Failed
Skipped
Completed
```

Example:

```text
Copy_customers
      |
      +── Succeeded ──→ Continue
      |
      +── Failed ─────→ Failure handling
```

---

# 6. Execute Pipeline

Used when one pipeline needs to **invoke another pipeline**.

```text
Parent Pipeline
      |
      ↓
Execute Pipeline
      |
      ↓
Child Pipeline
```

Our project:

```text
pl_fintech_ingestion_orchestration
            |
            ↓
Execute_Account_Ingestion
            |
            ↓
pl_account_ingestion
```

---

## Direct Dependency vs Execute Pipeline

### Same pipeline → Dependency

```text
Activity A
    ↓
Activity B
```

### Separate pipelines → Execute Pipeline

```text
Pipeline A
    ↓
Execute Pipeline
    ↓
Pipeline B
```

### Interview line

> **Dependencies control the order of activities; Execute Pipeline allows one pipeline to invoke another pipeline.**

---

# 7. Wait on Completion

### Checked

Parent waits for child to finish.

```text
Parent
  ↓
Start Child
  ↓
WAIT
  ↓
Child finishes
  ↓
Parent continues
```

Useful for sequential orchestration.

---

# 8. Parent vs Child Pipeline

### Parent

Responsible for **orchestration**:

* What runs first?
* What runs next?
* What happens on failure?

### Child

Responsible for **domain-specific processing**.

Example:

```text
Parent
 ├── Customer Pipeline
 ├── Account Pipeline
 └── Transaction Pipeline
```

### Key principle

> **Parent = orchestration | Child = processing**

---

# 9. Our Project Implementation

```text
pl_fintech_ingestion_orchestration
              |
              ↓
       Copy_customers
          /       \
   Succeeded      Failed
       |             |
       ↓             ↓
Execute_Account   Handle Failure
       |
       ↓
pl_account_ingestion
```

Implemented:

* Pipeline parameters ✅
* Dataset parameters ✅
* Dynamic content ✅
* Parameterized source/sink ✅
* Variables ✅
* Activity dependencies ✅
* Failure dependency ✅
* Execute Pipeline ✅
* Parent/child pipelines ✅
* Wait on completion ✅

---

# 10. Interview Cheat Sheet

```text
Parameter       → Read-only pipeline input
Variable        → Mutable runtime state
Dynamic Content → Runtime expression
Dataset Param   → Dynamic dataset configuration
Dependency      → Controls activity execution
Execute Pipeline→ Invokes another pipeline
Wait Completion → Parent waits for child
Parent Pipeline → Orchestration
Child Pipeline  → Domain processing
```

### One-minute answer

> "I use ADF parameters to make pipelines reusable instead of hardcoding paths. Dataset parameters allow dynamic source and sink configuration. Variables are used for mutable runtime state such as processing status. I use activity dependencies to control execution flow, and Execute Pipeline when a process is implemented as a separate reusable child pipeline. With Wait on completion enabled, the parent waits for the child to finish. This gives us a modular parent-child orchestration architecture."


