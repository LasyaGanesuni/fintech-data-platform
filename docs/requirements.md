# FinTech Transaction & Fraud Data Platform

## 1. Business Problem
The organisation gets huge amounts of data from multiple systems, making it difficult to integrate, maintain consistency, and provide reliable data for analytics. Therefore, the organisation needs a centralized data platform that enables reliable decision-making and reporting for multiple teams.
## 2. Data Consumers
### 2.1 Consumer 1: Business users / Clients
Business users / Clients need dashboards to support decision-making based on reliable data and analytics.
### 2.2 Fraud / Compliance Teams
Fraud / Compliance teams need fraud information to identify suspicious patterns and recurring incidents and take appropriate preventive action.
### 2.3 Finance Team
Finance teams need transaction and payment information for financial reconciliation, reporting, and amount-related analytics.
### 2.4 Data Scientists / ML Team
Data Scientists need customer, transaction, and fraud data to build machine learning models, identify patterns, and generate predictive insights.
### 2.5 Data Engineering / Operations Team
Data Engineering and Operations teams need pipeline metadata, logs, and data-quality information to monitor pipeline health, troubleshoot failures, and ensure reliable data delivery.
### 2.6 Business / Analytics Teams
Business and analytics teams need customer, merchant, and transaction data to perform detailed analysis and generate business insights.

## 3. Data Sources & Ingestion

The platform receives data from multiple source systems. Different ingestion patterns are used based on the nature and frequency of the data.

| Entity | Source | Ingestion Pattern | Frequency | Reason |
|---|---|---|---|---|
| Customer | Relational Database | CDC | Continuous | Customer data is maintained in a transactional system and only changes need to be captured. |
| Account | Relational Database | CDC | Continuous | Account information can be inserted, updated, or deleted and changes need to be captured incrementally. |
| Merchant | Third-party REST API | API ingestion | Daily/Hourly | Merchant information is provided by an external provider through an API. |
| Transaction | Files | Batch ingestion | Hourly | Transactions are high-volume data received as periodic files. |
| Fraud Event | Kafka | Streaming | Near real-time | Fraud/risk events need to be processed quickly for timely detection and analysis. |


## 4. Expected Data Volume

The platform is initially designed to handle the following approximate volumes:

| Entity | Initial Volume |
|---|---:|
| Customers | 5 million |
| Accounts | 15 million |
| Merchants | 1 million |
| Transactions | 3 million/day |
| Fraud/Risk Events | 500,000/day |

### Scalability Requirement

The platform should initially support approximately 3 million transactions per day and be designed to scale towards approximately 100 million transactions per day without requiring a complete redesign of the architecture.


## 5. Service Level Requirements

### Batch Processing SLA

Transaction files received by the **5:00 PM cutoff** must be processed and available in the Gold layer by **6:00 PM**.

This provides a one-hour processing window for the batch pipeline.

### Streaming Data Freshness

Fraud/risk events should become available in the target data layer within **5 minutes** of the event being received.

### Pipeline Reliability

The platform should target a minimum pipeline success rate of **99%** for scheduled processing.


## 6. Failure Scenarios

The platform should be designed to handle failures and data-quality issues across different layers.

### Customer Database

- Duplicate customer records
- Missing or invalid mandatory customer attributes

### Account Database

- Account records referencing non-existent customers
- Missing account information

### Merchant API

- API connection or availability failure
- Unexpected or invalid API response data

### Transaction Files

- Delayed file arrival
- High transaction volume causing processing delays

### Kafka / Streaming

- Delayed events
- Missing events between the producer and consumer

### Databricks / Spark

- Spark job failure
- Data skew causing uneven partition sizes and slow processing

### Data Quality Handling

Individual invalid records should not necessarily cause the entire pipeline to fail. Valid records should continue through the pipeline while invalid records should be moved to a quarantine area with the reason for rejection.

However, if the percentage of invalid records exceeds a defined threshold, the pipeline should fail and generate an alert.


## 7. Gold Data Products

The Gold layer will provide business-ready datasets for downstream consumers.

### New Merchant Analytics

Used to track newly added merchants, merchant onboarding, and merchant growth.

### Fraud Analytics

Used by Fraud and Compliance teams to monitor fraud/risk activity, identify suspicious patterns, and analyze recurring incidents.

### Regional Customer Analytics

Used to analyze customer distribution and customer activity across different regions.

### Transaction Analytics

Used to analyze transaction volume, transaction value, successful/failed transactions, and refunds.

### Customer Transaction / ML Features

Provides customer-level transaction and fraud-related features that can be used by Data Scientists for machine learning models and predictive analysis.

### Finance Reconciliation

Provides transaction and payment information required for financial reconciliation, reporting, and amount-related analytics.
