# Source Data

This directory contains simulated source-system data used to develop and test the FinTech Transaction & Fraud Data Platform.

The data intentionally contains realistic data-quality and operational issues so that the ingestion and transformation pipelines can be tested under production-like conditions.

## Sources

### Customers
Simulates customer records received from a relational database through CDC.

### Accounts
Simulates account records received from a relational database through CDC.

### Merchants
Simulates merchant information received from a third-party API.

### Transactions
Simulates high-volume transaction files received hourly.

### Fraud Events
Simulates real-time fraud/risk events received through Kafka.
