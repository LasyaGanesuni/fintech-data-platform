PYTEST
→ Python testing framework

UNIT TEST
→ Tests one isolated piece of logic

INTEGRATION TEST
→ Tests multiple components working together

ASSERTION
→ Checks actual result vs expected result

FIXTURE
→ Reusable test setup

MOCK
→ Replaces external dependency

ARRANGE → ACT → ASSERT
→ Common test structure

REGRESSION TEST
→ Ensures existing functionality still works after changes

UNIT TEST ≠ DQ
→ Unit test checks code
→ DQ checks data

PySpark testing
→ Small deterministic DataFrames
→ Test reusable transformations/functions

---
## 🧪 Pytest / Unit Testing — Data Engineering

The goal here is to understand **what to test, why, and where**, rather than just knowing Pytest syntax.

### 1. What is unit testing?

A **unit test tests one small piece of logic independently**.

In your project, you created reusable functions such as:

```text id="h9ldm1"
schema_validator.py
deduplication.py
quarantine.py
```

These are excellent candidates for unit testing because each contains relatively isolated logic.

Think:

```text id="8l4wpg"
Reusable function
      ↓
   Unit test
      ↓
Expected result?
```

---

# 2. Why do we need unit tests?

Imagine your reusable deduplication function is used by:

```text id="h4q3j5"
Customer pipeline
Account pipeline
Transaction pipeline
```

You change the function.

Without tests:

```text id="9xj7vl"
Change function
      ↓
Hope nothing broke
```

With tests:

```text id="t1h7bf"
Change function
      ↓
Run tests
      ↓
Detect regression
```

That's why unit testing is especially valuable for **reusable modules**.

---

# 3. Unit Test vs Integration Test

This is a common interview question.

### Unit test

Tests one component in isolation.

Example:

```text id="9jbrg4"
deduplicate_latest()
        ↓
Does it return the correct latest record?
```

You don't need the entire pipeline.

### Integration test

Tests whether multiple components work together.

Example:

```text id="8q5xkn"
ADF
 ↓
ADLS
 ↓
Databricks
 ↓
Bronze
 ↓
Silver
```

You might verify that the components correctly work together.

### Simple distinction

> **Unit test = “Does this piece work?”**

> **Integration test = “Do these pieces work together?”**

---

# 4. What would you test in your project?

### Schema validator

You could test:

```text id="xkq7j2"
Expected schema = actual schema
→ PASS

Missing column
→ FAIL

Unexpected column
→ FAIL

Wrong datatype
→ FAIL
```

For example:

```text id="5y3t9f"
Expected:
transaction_amount → DECIMAL

Actual:
transaction_amount → STRING

Expected result:
validation fails
```

---

### Deduplication

Test cases:

```text id="6s6c7j"
No duplicates
→ same number of rows

Duplicate key
→ latest record retained

Multiple duplicates
→ exactly one record per key

Older record
→ removed
```

Example:

```text id="f6g8b2"
customer_id | updated_at
C001        | 10:00
C001        | 12:00
```

Expected:

```text id="6r6z2q"
C001 | 12:00
```

---

### Quarantine

Test:

```text id="k5s6pj"
Invalid record
      ↓
Quarantine metadata added
      ↓
Reason exists
      ↓
Timestamp exists
```

You can verify that:

* `_quarantine_reason` exists
* reason is correct
* `_quarantine_timestamp` exists

---

# 5. Arrange → Act → Assert

A very common testing pattern.

### Arrange

Prepare test data.

```text id="x9v8me"
Create test DataFrame
```

### Act

Run the function.

```text id="4k0gzn"
result = deduplicate_latest(...)
```

### Assert

Verify expected result.

```text id="s8d1rm"
Expected rows == actual rows
Expected values == actual values
```

Think:

```text id="2v8jhm"
ARRANGE
   ↓
ACT
   ↓
ASSERT
```

---

# 6. What is Pytest?

**Pytest** is a Python testing framework.

A typical test function starts with:

```python id="m3xv5j"
def test_something():
    ...
```

Pytest discovers test files/functions and executes them.

Typical naming:

```text id="8v6qjz"
tests/
├── test_schema_validator.py
├── test_deduplication.py
└── test_quarantine.py
```

---

# 7. What is an assertion?

An assertion checks whether the actual result matches what you expect.

Conceptually:

```python id="6g2t8a"
assert actual == expected
```

For Data Engineering, assertions might verify:

```text id="e2k7hv"
Row count
Column names
Data types
Expected values
Null counts
Duplicate counts
```

---

# 8. Testing PySpark functions

This is slightly different from ordinary Python because you're working with **Spark DataFrames**.

Conceptually:

```text id="0i5m9r"
Create small test DataFrame
        ↓
Pass to PySpark function
        ↓
Collect small result
        ↓
Compare against expected result
```

For unit tests, the test data should generally be **small and deterministic**.

You don't want:

```text id="r8f4k1"
5 million production records
        ↓
Unit test
```

Instead:

```text id="6q9w3m"
5–10 carefully chosen records
        ↓
Test specific behavior
```

---

# 9. Fixtures

Pytest has **fixtures** for reusable test setup.

For example, you might need a Spark session for many PySpark tests.

Instead of creating it repeatedly:

```text id="1h7z5d"
Test 1 → SparkSession
Test 2 → SparkSession
Test 3 → SparkSession
```

you can use a fixture:

```text id="4k8f2s"
             Spark fixture
             ↙    ↓    ↘
          Test1 Test2 Test3
```

This keeps test setup reusable.

---

# 10. Mocking

Sometimes your code interacts with external systems:

```text id="c8n3qp"
API
Database
ADLS
ADF
External service
```

You generally don't want a unit test to depend on the real external system.

**Mocking** allows you to replace that dependency with a controlled fake/test object.

Mental model:

```text id="7f4b2w"
Production:
Function → Real API

Unit test:
Function → Mock API
```

This makes tests:

* Faster
* Deterministic
* Independent of external systems

---

# 11. What should NOT be a unit test?

Don't try to test the entire production pipeline as a unit test.

For example:

```text id="r7h1cz"
ADF → ADLS → Databricks → Delta → Power BI
```

That's closer to **integration/end-to-end testing**.

Unit testing should focus on isolated logic.

---

# 12. Unit Testing vs Data Quality

Another important distinction.

### Unit test

Tests whether **your code behaves correctly**.

> “Does my deduplication function retain the latest record?”

### Data Quality check

Tests whether **the data itself is valid**.

> “Does customer_id contain nulls?”

So:

```text id="j9k2xv"
Unit Testing
→ Code correctness

Data Quality
→ Data correctness
```

They complement each other.

---

# 13. Regression Testing

You also have **regression testing** on your resume.

Regression testing asks:

> **“Did a change break something that previously worked?”**

Example:

```text id="b7c4pn"
Version 1
deduplication → PASS

Change function

Version 2
deduplication → ?
```

Run the existing tests again:

```text id="j3m8vy"
All previous tests → PASS
```

Then you have confidence that the change didn't break existing behavior.

---

# 14. Your project testing strategy

For your FinTech platform, think:

```text id="j2s8qf"
Reusable PySpark functions
          ↓
       Pytest
          ↓
     Unit testing
          ↓
─────────────────────────
Schema validation
Deduplication
Quarantine
Transformations
Business rules
─────────────────────────
          ↓
Integration tests
          ↓
Pipeline components together
```

And separately:

```text id="x5h7kp"
Production data
      ↓
Data Quality checks
      ↓
Nulls / duplicates / domains /
referential integrity / reconciliation
```

---

## 🎯 Interview skim sheet

```text id="q4m8vz"
PYTEST
→ Python testing framework

UNIT TEST
→ Tests one isolated piece of logic

INTEGRATION TEST
→ Tests multiple components working together

ASSERTION
→ Checks actual result vs expected result

FIXTURE
→ Reusable test setup

MOCK
→ Replaces external dependency

ARRANGE → ACT → ASSERT
→ Common test structure

REGRESSION TEST
→ Ensures existing functionality still works after changes

UNIT TEST ≠ DQ
→ Unit test checks code
→ DQ checks data

PySpark testing
→ Small deterministic DataFrames
→ Test reusable transformations/functions
```

### One interview answer to remember

> **“I use Pytest to unit test reusable PySpark modules by creating small deterministic test DataFrames, applying the function under test, and asserting the expected schema, row counts, values, and business behavior. For pipeline-level interactions I would use integration testing separately, while data-quality checks validate the correctness of the actual data.”**
