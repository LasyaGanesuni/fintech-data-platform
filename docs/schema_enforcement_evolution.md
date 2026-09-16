# Schema Enforcement

## What is Schema Enforcement?

Schema enforcement ensures that data written to a Delta table is compatible with the table's existing schema.

If incoming data has an incompatible datatype or structure, the write is rejected instead of silently changing the target schema.

### Simple Architecture
```
Incoming Data
     ↓
Delta Target Schema
     ↓
Schema Enforcement
     ↓
 ┌───┴────┐
Valid    Invalid
 ↓          ↓
Write      Reject ❌
✅
```
---

## Example

Expected Silver schema:

transaction_amount → DECIMAL(18,2)

Incoming data:

transaction_amount → STRING

Result:

Schema mismatch
     ↓
Write fails ❌

The existing Delta table remains unchanged.

---

## Why is Schema Enforcement Important?

It prevents unexpected source changes from introducing inconsistent schemas into downstream tables.

Example:

Expected:

transaction_amount → DECIMAL(18,2)

Unexpected:

transaction_amount → STRING

Without proper schema controls, downstream transformations and aggregations can become unreliable.

---

# Schema Enforcement vs Schema Evolution

### Schema Enforcement

> "Does the incoming data conform to the existing target schema?"

Example:
```
Target:
transaction_amount → DECIMAL(18,2)

Incoming:
transaction_amount → STRING
```
→ Reject ❌

### Schema Evolution

> "Should the target schema be allowed to change?"

Example:
```
Existing:

transaction_id
account_id
transaction_amount

Incoming:

transaction_id
account_id
transaction_amount
risk_score
```
With supported schema evolution:

→ `risk_score` can be added to the target schema.

---

## Important

`mergeSchema = true` is related to **schema evolution**, not a replacement for schema enforcement or data validation.

It should NOT be interpreted as:

> "Accept any incoming schema."

Compatible schema changes can be evolved, but incompatible datatype changes are still a different problem.

---

# Bronze vs Silver

### Bronze

Purpose:

> Preserve source data as received.

Bronze should generally avoid aggressive transformations.

Source
 ↓
Bronze

Preserve:
- Source values
- Source metadata
- Source files
- Ingestion information

### Silver

Purpose:

> Provide clean, predictable, business-ready data.
```
Bronze
 ↓
Schema controls
 ↓
DQ / transformations
 ↓
Silver
```
Silver should have controlled and consistent datatypes.

---

# Schema Enforcement vs Schema Validation vs DQ

These are related but different.

### Schema Enforcement

Structural/type compatibility with the Delta target.

> "Can this data be written to the target?"

### Schema Validation

Explicitly checks whether incoming data matches our defined schema expectations.

Examples:
- Required columns exist
- Expected datatype
- Unexpected columns
- Nullable/non-nullable expectations

> "Does this data match our schema contract?"

### Data Quality

Checks data/content/business rules.

Examples:
- NULL values
- Duplicate records
- Invalid country
- Invalid transaction status
- Referential integrity
- Negative amounts when not allowed

> "Is the data actually valid?"

---

# Our FinTech Project

For transactions, we expect:
```
transaction_id        → STRING
account_id            → STRING
merchant_id           → STRING
transaction_amount    → DECIMAL(18,2)
currency              → STRING
transaction_type      → STRING
transaction_status    → STRING
transaction_timestamp → TIMESTAMP
created_at            → TIMESTAMP
updated_at            → TIMESTAMP
```
Example:

transaction_amount
        ↓
DECIMAL(18,2)

This provides a consistent datatype for downstream Silver/Gold processing.

---

# What We Tested

### Test 1 — Valid schema
```
Expected schema
      ↓
Incoming schema
      ↓
Compatible
      ↓
Write succeeds ✅
```
### Test 2 — Incompatible datatype
```
transaction_amount
STRING
      ↓
Target expects DECIMAL(18,2)
      ↓
Write fails ❌
```
### Test 3 — Missing column
```
Required column missing
      ↓
Schema mismatch
      ↓
Write fails ❌
```
### Test 4 — Additional column
```
New column such as `risk_score`
      ↓
Schema evolution becomes relevant
```
---

# Interview Points

### What is schema enforcement?

"Schema enforcement ensures that data written to a Delta table is compatible with the existing table schema. Incompatible data types or structures are rejected rather than silently changing the target schema."

### Schema enforcement vs schema evolution?

"Schema enforcement protects the existing schema, while schema evolution allows supported changes to the target schema, such as adding new columns."

### Where would you use stronger schema controls?

"Bronze is generally kept close to the source to preserve raw data, while Silver should have a more controlled and predictable schema for downstream consumers."

---

# Quick Mental Model
```
Schema Enforcement
→ Can I WRITE this data?

Schema Validation
→ Does it MATCH my expected schema?

Data Quality
→ Is the DATA actually valid?

Schema Evolution
→ Should the TARGET SCHEMA change?
```
---

# One-Line Summary

> Schema enforcement protects the structural integrity of the Delta target by preventing incompatible data from being written.