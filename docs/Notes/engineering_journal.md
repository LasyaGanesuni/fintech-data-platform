## 2026-08-23 — Databricks + Unity Catalog Setup

### What we did
- Created Azure Databricks workspace
- Validated Spark environment
- Connected ADLS Gen2 with Unity Catalog
- Created storage credential and external location
- Connected Databricks Git folder to GitHub

### Troubleshooting

#### 1. Serverless RDD limitation
Attempted to use `df.rdd.getNumPartitions()` on Serverless compute.

**Result:** Not supported on Serverless.

**Learning:** Serverless has restrictions on PySpark RDD APIs. Use DataFrame-based APIs where possible.

#### 2. Unity Catalog external location access
Initial external location used the workspace default credential.

**Problem:** Access to the ADLS path was denied because the credential was restricted to the workspace's managed storage path.

**Fix:** Created a dedicated Azure Managed Identity storage credential and associated it with the external location.

#### 3. File Events permission issue
External location creation initially showed File Events permission failures.

**Decision:** Disabled File Events for now and used directory listing.

**Why:** File Events are optional. We can revisit them when implementing incremental ingestion.

#### 4. GitHub authentication
Initial Git push failed because no Git credential was configured.

**Fix:** Linked GitHub using the Databricks GitHub integration and granted the Databricks app access only to this repository.

**Result:** Successfully pushed the first Databricks notebook to GitHub.
