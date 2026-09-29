

# Customer SCD Type 2 — Documentation

## 1. Objective

Implement **Slowly Changing Dimension Type 2 (SCD2)** for the Customer dimension to preserve the complete historical state of customer attributes.

Instead of overwriting an existing customer record when an attribute changes, a new version is created.

### Target table

```text
dbx_fintech_data_platform.silver.customers_scd2
```

---

# 2. Why SCD2?

The normal Customer Silver table represents the **latest customer state**.

For example:

```text
C001 | PREMIUM | 333333 | new@email.com
```

If the phone changes from `111111` → `222222` → `333333`, simply updating the row would lose the historical values.

SCD2 preserves those states:

```text
C001 | REGULAR | 111111 | old@email.com | 10:00 | 14:00 | false
C001 | REGULAR | 222222 | old@email.com | 14:00 | 18:00 | false
C001 | PREMIUM | 333333 | new@email.com | 18:00 | NULL | true
```

This allows historical questions such as:

* What was the customer's information at a particular point in time?
* When did an attribute change?
* What was the customer's state when a transaction occurred?
* What was the customer's previous state?

---

# 3. CDC Design

For this project, Customer CDC was simulated because we didn't have a real source-system CDC feed.

The Bronze CDC table was:

```text
dbx_fintech_data_platform.bronze.customer_cdc
```

### CDC structure

| Column            | Description                      |
| ----------------- | -------------------------------- |
| `customer_id`     | Customer identifier              |
| `column_name`     | Attribute that changed           |
| `old_value`       | Value before the change          |
| `new_value`       | Value after the change           |
| `event_timestamp` | Business timestamp of the change |

Example:

```text
C001 | phone | 111111 | 222222 | 10:00
C001 | email | old@x.com | new@x.com | 10:00
C001 | phone | 222222 | 333333 | 14:00
```

### Important design decision

CDC uses **one row per changed attribute**.

This allows multiple attributes to change independently and makes attribute-level change tracking explicit.

---

# 4. Multiple Changes at the Same Timestamp

If multiple attributes change at exactly the same timestamp:

```text
C001 | phone | 111 → 222 | 10:00
C001 | email | A → B     | 10:00
```

we treat them as **one customer state transition**.

After pivoting:

```text
C001 | 10:00 | phone=222 | email=B
```

### Why?

There is no evidence that an intermediate state existed between the two changes.

Therefore:

> **One SCD2 version per customer + event timestamp.**

If changes occur at different timestamps, they produce separate versions.

---

# 5. CDC Pivot

The row-level CDC was transformed into a customer-level event state using:

```text
customer_id + event_timestamp
```

as the grouping keys.

Conceptually:

```text
Row-based CDC
      ↓
Pivot by column_name
      ↓
Customer state change per timestamp
```

Example:

### Before

```text
C001 | phone | 111 | 222 | 10:00
C001 | email | A   | B   | 10:00
```

### After

```text
C001 | 10:00 | phone_new=222 | email_new=B
```

---

# 6. Carrying State Forward

A CDC row only contains the attributes that changed.

Example:

```text
10:00 → phone = 222, email = B
14:00 → phone = 333, email = NULL
```

At 14:00, email should still be `B`.

Therefore we used a Spark window:

```python
Window
    .partitionBy("customer_id")
    .orderBy("event_timestamp")
    .rowsBetween(
        Window.unboundedPreceding,
        Window.currentRow
    )
```

and `last_value(..., True)` to carry the latest non-null value forward.

Result:

```text
10:00 → phone=222 | email=B
14:00 → phone=333 | email=B
```

### Key concept

> **CDC tells us what changed; the previous state tells us what remained unchanged.**

---

# 7. Handling the Initial State

A major issue is that the CDC starts **at the first change**.

Suppose:

```text
09:30 → customer_type REGULAR → PREMIUM
15:00 → email old → new
```

At 09:30, email is still the old email.

We cannot simply use the **current Silver value**, because Silver represents today's/latest state.

Instead, the first `old_value` for each:

```text
customer_id + column_name
```

was used to reconstruct the initial historical state.

Conceptually:

```text
First CDC change for attribute
        ↓
old_value = initial value
        ↓
Apply new_value chronologically
```

This prevents historical states from accidentally containing today's values.

---

# 8. Initial SCD2 Version

The original Customer Silver record is used to create the initial version.

For a customer with CDC:

```text
effective_from = created_at
effective_to   = first CDC event
is_current     = false
```

Example:

```text
C001
created_at = 2026-08-01
first CDC = 2026-08-20 10:00
```

Initial version:

```text
effective_from = 2026-08-01
effective_to   = 2026-08-20 10:00
is_current     = false
```

For a customer with **no CDC changes**:

```text
effective_from = created_at
effective_to   = NULL
is_current     = true
```

---

# 9. Generating SCD2 Time Boundaries

Once complete customer states were reconstructed, `LEAD()` was used to determine when each version ends.

Window:

```python
Window
    .partitionBy("customer_id")
    .orderBy("event_timestamp")
```

Logic:

```text
effective_from = event_timestamp

effective_to =
    next event_timestamp
```

Example:

```text
10:00 → next event = 14:00
14:00 → next event = NULL
```

Therefore:

```text
10:00 → 14:00 → false
14:00 → NULL   → true
```

---

# 10. Final SCD2 Structure

Target columns:

| Column           | Purpose                              |
| ---------------- | ------------------------------------ |
| `customer_id`    | Business key                         |
| `customer_type`  | Customer classification              |
| `phone`          | Customer phone                       |
| `email`          | Customer email                       |
| `created_at`     | Original customer creation timestamp |
| `updated_at`     | Source customer update timestamp     |
| `effective_from` | Start of this version                |
| `effective_to`   | End of this version                  |
| `is_current`     | Indicates latest active version      |

---

# 11. Complete Pipeline

```text
Bronze Customer CDC
        │
        ▼
Pivot attribute-level changes
        │
        ▼
customer_id + event_timestamp
        │
        ▼
Carry latest non-null values forward
        │
        ▼
Reconstruct complete customer state
        │
        ├───────────────┐
        ▼               ▼
Initial Customer     CDC states
Silver state
        │               │
        └───────┬───────┘
                ▼
          Union versions
                │
                ▼
       LEAD(event_timestamp)
                │
                ▼
      effective_from/to
                │
                ▼
          is_current
                │
                ▼
       Silver Customer SCD2
```

---

# 12. Validation Checks

We validated the resulting SCD2 table using several business rules.

### Check 1 — Exactly one current record

For every customer:

```text
COUNT(is_current = true) = 1
```

Expected:

```text
0 invalid customers
```

---

### Check 2 — No overlapping versions

For each customer:

```text
current effective_from >= previous effective_to
```

Expected:

```text
0 overlapping records
```

---

### Check 3 — Current record has no end date

```text
is_current = true
AND effective_to IS NOT NULL
```

Expected:

```text
0 rows
```

---

### Check 4 — Historical records have an end date

```text
is_current = false
AND effective_to IS NULL
```

Expected:

```text
0 rows
```

---

# 13. Example Final History

Suppose C001 starts as:

```text
REGULAR | phone=111 | email=A
```

Changes:

```text
10:00 → phone 111 → 222
10:00 → email A → B
14:00 → phone 222 → 333
```

Final SCD2:

| Customer | Type    | Phone | Email | From    | To    | Current |
| -------- | ------- | ----- | ----- | ------- | ----- | ------- |
| C001     | REGULAR | 111   | A     | Initial | 10:00 | No      |
| C001     | REGULAR | 222   | B     | 10:00   | 14:00 | No      |
| C001     | REGULAR | 333   | B     | 14:00   | NULL  | Yes     |

Notice that the two 10:00 attribute changes become **one version**.

---

# 14. Important Spark Concepts Used

This implementation gave you hands-on experience with:

```text
groupBy()
pivot()
row_number()
Window.partitionBy()
Window.orderBy()
rowsBetween()
last_value(..., True)
lead()
unionByName()
join()
when()
coalesce()
Delta Lake
```

More importantly, you practiced the **reasoning behind the transformations**, rather than just implementing a pre-written SCD2 template.

### The core mental model

Remember this:

> **CDC → reconstruct complete states → assign time boundaries → preserve every state as a separate SCD2 version.**

That's the part I'd emphasize if you explain this project in an interview.
