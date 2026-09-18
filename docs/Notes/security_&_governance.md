### Security & Governance — PII & Compliance Monitoring

Now we're moving from **preventing unauthorized access** to **monitoring and proving what happened**.

## 1. What is PII?

**PII = Personally Identifiable Information**

Data that can identify or help identify an individual.

In your FinTech platform, examples could include:

* Customer name
* Email
* Phone
* Address
* Government identifiers
* Other sensitive customer attributes

The exact classification depends on the organization's policies and applicable regulations.

---

## 2. Why do we need compliance monitoring?

Imagine someone accesses:

```text
silver.customers
```

containing:

```text
customer_id
name
email
phone
```

RLS and masking can **restrict** what they see.

But the organization may also need to know:

> **Who accessed the data? When? What did they access?**

That's where monitoring/auditing comes in.

Think:

```text id="d8h5qh"
                 Sensitive Data
                       ↓
              ┌────────┴────────┐
              ↓                 ↓
          Protection         Monitoring
              ↓                 ↓
        RLS / Masking       Audit / Logs
```

---

## 3. What would you monitor?

Typical governance monitoring can include:

### Access

* Who accessed the data?
* Which user/service principal?
* Which table?
* When?

### Sensitive-data access

* Was a PII-containing table accessed?
* Which sensitive columns were involved?
* Was access successful?

### Governance events

* Permission changes
* Grants/revokes
* Policy changes
* Access failures

### Operational information

* Pipeline execution
* Data-quality failures
* Quarantined records
* Schema changes

---

## 4. Your FinTech example

Suppose:

```text
silver.customers
```

contains PII.

You could have a governance dashboard showing something like:

```text
User              Table              Access Time
---------------------------------------------------
analyst_01        customers          10:32
compliance_02     customers          10:45
service_account   transactions      11:02
```

Then management/compliance teams can investigate unusual access patterns.

---

## 5. RLS vs Masking vs Monitoring

This is **very important for interviews**:

| Control              | Question it answers          |
| -------------------- | ---------------------------- |
| **RLS**              | Which rows can the user see? |
| **Column masking**   | What value can the user see? |
| **Audit/monitoring** | Who accessed what and when?  |

So:

```text id="i8zq9s"
RLS       → Prevent/restrict row access
Masking   → Protect sensitive values
Monitoring → Track/audit access and governance events
```

They solve **different problems** and can work together.

---

## 6. What would a compliance dashboard contain?

For your project, you could conceptually have:

### Access Summary

```text
Total sensitive-data accesses
Unique users
Tables accessed
Failed access attempts
```

### PII Access

```text
User
Table
Timestamp
Access type
```

### Governance Changes

```text
Permission changes
Policy changes
Masking changes
```

### Data Quality / Pipeline

```text
Pipeline success rate
DQ failures
Quarantined records
Schema failures
```

---

## 7. Important interview distinction

Don't say:

> “The compliance dashboard provides security.”

Instead:

> **“Security controls such as RLS and masking restrict access, while audit and monitoring provide visibility into access and governance activity.”**

That's much more accurate.

---

## 8. Your resume bullet

You have a resume claim around:

> **Compliance/monitoring dashboards for data access, governance, and PII.**

If asked about it, a good explanation would be:

> **“I used governance and audit information to build monitoring views around sensitive-data access, permissions, and pipeline/data-quality activity. The purpose was to provide compliance teams with visibility into who accessed sensitive datasets and whether governance controls were operating as expected.”**

Keep the distinction clear:

**Control = prevent/restrict**

**Monitoring = observe/detect**

**Audit = retain evidence**

---

### 🧠 Skim note

```text
PII
→ Sensitive customer information

RLS
→ Controls which ROWS a user can access

Column Masking
→ Controls what VALUE is returned from sensitive columns

Audit
→ Records access/governance activity

Monitoring
→ Analyzes that activity for visibility/compliance

Dashboard
→ Presents access + governance + DQ/operational information
```

