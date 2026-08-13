# FinTech Transaction & Fraud Data Platform

## 1. Architecture Overview
The FinTech Transaction & Fraud Data Platform is a cloud-based data platform designed to ingest, process, govern, and serve large volumes of batch and real-time financial data.

The platform supports multiple ingestion patterns including CDC, API-based ingestion, batch file ingestion, and real-time streaming. Data is stored and progressively refined through Raw, Bronze, Silver, and Gold layers.

The platform is designed to support analytics, fraud monitoring, financial reconciliation, and machine learning use cases while providing data quality, reliability, security, governance, monitoring, and CI/CD capabilities.

### High-Level Architecture

```text
                         SOURCE SYSTEMS
                              │
             ┌────────────────┴────────────────┐
             │                                 │
       BATCH / API                         STREAMING
             │                                 │
             ↓                                 ↓
      Azure Data Factory                    Kafka
             │                                 │
             ↓                                 ↓
       ADLS Raw/Landing             Spark Structured Streaming
             │                                 │
             └──────────────┬──────────────────┘
                            ↓
                         BRONZE
                            ↓
                         SILVER
                            ↓
                          GOLD
                            │
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
          Analytics      Finance          ML
          & Reporting  Reconciliation    Models

        ┌─────────────────────────────────────┐
        │     Security & Governance           │
        │     Unity Catalog / RBAC / PII      │
        └─────────────────────────────────────┘

        ┌─────────────────────────────────────┐
        │     Reliability & Operations        │
        │ Monitoring / Alerts / DQ / SLA      │
        └─────────────────────────────────────┘

        ┌─────────────────────────────────────┐
        │       Engineering & CI/CD           │
        │ GitHub / Actions / Terraform        │
        └─────────────────────────────────────┘
```
## 2. Ingestion Layer

The platform receives data from multiple source systems using different ingestion patterns based on the characteristics of each source.

### Batch and API Ingestion
```text
Customer DB ──────┐
Account DB ───────┤
Merchant API ─────┤──→ Azure Data Factory ──→ ADLS
Transaction Files ┘
```
Azure Data Factory (ADF) is used as the orchestration and data movement layer for batch and API-based sources. It connects to external source systems, schedules and executes ingestion pipelines, handles dependencies, and moves data into Azure Data Lake Storage (ADLS).

### Streaming Ingestion

```text
Fraud Detection System
          │
          ↓
        Kafka
          │
          ↓
Spark Structured Streaming
          │
          ↓
   Databricks / Delta Lake
```

Fraud events follow a separate streaming ingestion path because they need to be processed with low latency rather than waiting for batch ingestion.
## 3. Storage Layer

The platform uses Azure Data Lake Storage (ADLS) as the central storage layer.

The data is organized using a Medallion Architecture:

Raw → Bronze → Silver → Gold
### Raw / Landing Layer

The Raw/Landing layer stores an unchanged copy of the data received from the source systems.

The original data is preserved for:

- Reprocessing when downstream transformations fail or change
- Troubleshooting and auditing
- Comparing source data with downstream layers to identify discrepancies

### Bronze Layer

The Bronze layer stores the ingested source data in a reliable, queryable format with minimal transformation and ingestion metadata.

The Bronze layer provides a stable starting point for downstream data processing.

The overall flow is:
```text
Source
  ↓
ADF / Kafka
  ↓
ADLS Raw / Landing
  ↓
Bronze
  ↓
Silver
  ↓
Gold
```
### Batch vs Streaming Data Flow

The platform uses different ingestion paths for batch/API sources and streaming sources.

#### Batch / API Sources

For Customer, Account, Merchant, and Transaction data:
```text
Source System
    ↓
Azure Data Factory
    ↓
ADLS Raw / Landing
    ↓
Bronze
```
ADF is responsible for orchestrating and moving batch/API data into the data lake. The raw copy is preserved before downstream transformations.

#### Streaming Source

For real-time Fraud Events:
```text
Fraud Detection System
    ↓
Kafka
    ↓
Spark Structured Streaming
    ↓
Bronze Delta
```
Kafka events are processed directly by Spark Structured Streaming and written to the Bronze Delta layer because these events require low-latency processing.

### Why are the paths different?

Batch/API data arrives periodically and can be stored in the Raw/Landing area before processing.

Streaming data arrives continuously and needs to be processed with low latency. Therefore, Spark Structured Streaming consumes events from Kafka and writes them directly to Bronze.

Both paths ultimately converge at the Bronze layer, allowing downstream Silver and Gold processing to follow a common data refinement process.
### Silver Layer

The Silver layer contains cleaned, validated, standardized, deduplicated, and enriched data.

Key responsibilities include:

- Deduplication
- Null and blank value handling
- Data-quality and business-rule validation
- Standardization of casing, formats, and data types
- Data enrichment by combining related datasets
- Quarantining invalid records

The Silver layer provides trustworthy data for downstream analytics and Gold data products.
### Gold Layer

The Gold layer contains business-ready data products designed for specific downstream consumers and use cases.

Gold datasets are not simply copies of Silver tables. They are modeled, aggregated, enriched, or feature-engineered according to business requirements.

| Gold Data Product | Primary Consumer | Purpose |
|---|---|---|
| New Merchant Analytics | Business / Analytics | Track merchant onboarding and growth |
| Fraud Analytics | Fraud / Compliance | Monitor suspicious activity and fraud trends |
| Regional Customer Analytics | Business / Analytics | Analyze customer distribution and activity by region |
| Transaction Analytics | Business / Finance | Analyze transaction volume, value, success/failure, and refunds |
| Customer Transaction / ML Features | Data Scientists / ML | Support machine learning and predictive analysis |
| Finance Reconciliation | Finance | Reconcile source and processed transaction amounts |

The Gold layer provides optimized and reliable datasets for dashboards, reporting, financial reconciliation, fraud analysis, and machine learning.
### Databricks / Spark Processing Layer

Azure Data Factory is primarily responsible for orchestration and data movement, while Databricks provides the distributed processing layer.

Databricks and Apache Spark are used to process large volumes of data across multiple compute resources.

Key responsibilities include:

- Data cleansing and validation
- Deduplication
- Complex transformations
- Large-scale joins and enrichment
- Aggregations
- Incremental processing
- Streaming processing
- Performance optimization

The distributed processing capability of Spark allows the platform to scale as transaction volumes grow from millions to potentially hundreds of millions of records per day.
## 4. Orchestration & Reliability

Azure Data Factory is used to orchestrate the batch data processing workflow.

A typical batch workflow is:
```text
Source
  ↓
Input/File Validation
  ↓
Bronze Ingestion
  ↓
Silver Processing
  ↓
Data Quality Checks
  ↓
Gold Processing
  ↓
Reconciliation
  ↓
Success / Failure
```

### Retry Strategy

Transient failures such as temporary network or infrastructure issues should be retried automatically.

Permanent failures such as invalid schemas or business-rule violations should not be repeatedly retried. They should be recorded, surfaced, and handled according to the appropriate failure process.

### Monitoring

The platform should monitor:

- Pipeline execution status
- Pipeline duration
- Records received and processed
- Records rejected
- Retry counts
- Data freshness
- Streaming latency
- Data-quality results
- SLA compliance
- Reconciliation results

### Alerting

Alerts should be generated for important operational conditions including:

- Pipeline failures
- Missing or delayed files
- SLA violations or risks
- Data-quality thresholds being exceeded
- Streaming latency exceeding the five-minute target
- Reconciliation mismatches
## 5. Security & Governance

The platform handles customer, account, transaction, and fraud-related data. Security and governance are therefore built into the architecture.

### Unity Catalog

Databricks Unity Catalog is used as the centralized governance layer for Databricks data assets.

It provides:

- Catalog and schema organization
- Table and view permissions
- Role-based access control
- Data lineage
- Centralized governance

### Role-Based Access

Access to data is provided based on user roles and business requirements.

Examples:

- Data Engineers → Bronze, Silver, and required Gold datasets
- Finance Team → Finance and transaction-related Gold datasets
- Fraud / Compliance → Fraud-related datasets
- Data Scientists → Approved ML-ready datasets
- Business Users → Approved analytics and reporting datasets

Users should only receive the minimum access required for their responsibilities.

### PII Protection

Sensitive customer information such as names, email addresses, and phone numbers must be protected through appropriate access controls and, where required, masking or restricted datasets.

### Secrets Management

Credentials, API keys, database passwords, and other secrets must not be hard-coded in notebooks, source code, or configuration files.

Secrets should be securely managed and retrieved at runtime.

### Environment Separation

The platform will maintain separate environments:

DEV → TEST → PROD

Changes should be developed and validated in lower environments before being deployed to production.
## 6. CI/CD & Software Engineering Practices

The project follows a Git-based development and CI/CD workflow to ensure that data pipelines and application code are tested and reviewed before deployment.

### Development Workflow
```text
Developer
  ↓
Feature Branch
  ↓
Pull Request
  ↓
Automated Tests & Validation
  ↓
Code Review
  ↓
Merge
  ↓
CI/CD Deployment
  ↓
DEV → TEST → PROD
```

### CI Checks

The CI pipeline should perform:

- Python and PySpark code quality checks
- Unit tests
- Data transformation tests
- Configuration validation
- Secret detection

### Continuous Deployment

The CD pipeline will deploy application and data pipeline changes to the appropriate environment after successful validation.

GitHub Actions will be used for CI/CD automation, while Databricks will be used for data processing and pipeline execution.

Infrastructure will eventually be managed using Terraform.
## 7. Technology Stack

| Technology | Purpose |
|---|---|
| Azure Data Factory | Batch/API ingestion, orchestration, scheduling, and pipeline monitoring |
| Azure Data Lake Storage Gen2 | Central cloud storage for Raw, Bronze, Silver, and Gold data |
| Azure Databricks | Distributed data processing and pipeline execution |
| Apache Spark / PySpark | Large-scale batch transformations, joins, aggregations, and streaming |
| Delta Lake | Reliable ACID-based storage and table management for the data lake |
| Apache Kafka | Real-time ingestion of fraud/risk events |
| Spark Structured Streaming | Processing Kafka events with low latency |
| Unity Catalog | Data governance, access control, lineage, and data discovery |
| GitHub | Source control and collaborative development |
| GitHub Actions | CI/CD automation, testing, and deployment |
| Terraform | Infrastructure as Code for provisioning and managing cloud resources |
| Python | Pipeline utilities, testing, configuration, and supporting application logic |
| SQL / Spark SQL | Data transformation, validation, analysis, and querying |
## Data Model Summary

### Dimensions

- Customer
- Account
- Merchant

### Facts / Events

- Transaction
- Fraud Event

### Relationships
```text
Customer 1 ─── N Account
Account 1 ─── N Transaction
Merchant 1 ─── N Transaction
Transaction 1 ─── 0..N Fraud Event
```
## Data Quality Rules

### Customer
- customer_id cannot be NULL
- name cannot be NULL
- country must be valid
- email must follow an accepted format

### Account
- account_id cannot be NULL
- customer_id cannot be NULL
- customer_id must exist in Customer
- status must be from an accepted set

### Merchant
- merchant_id cannot be NULL
- merchant_category must be valid
- status must be valid
- API response must conform to the expected schema

### Transaction
- transaction_id cannot be NULL
- account_id must exist
- merchant_id must exist
- transaction_amount must be greater than 0
- currency must be valid
- transaction_status must be valid

### Fraud Event
- fraud_event_id cannot be NULL
- transaction_id cannot be NULL
- transaction_id should exist
- risk_score must be between 0 and 1
- event_type must be valid
