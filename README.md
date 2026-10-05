# ❄️ snow-shield

**snow-shield** is a lightweight command-line intelligence tool built for risk, fraud, and regulatory audit ingestion into Snowflake.

## 💡 The Problem

In compliance-heavy sectors (GDPR, PCI-DSS, HIPAA), data engineers frequently handle transaction and audit logs that contain hidden Personally Identifiable Information (PII) like unencrypted emails or credit card details. Directly uploading these raw logs into a cloud environment creates a massive regulatory liability.

## 🚀 The Solution

`snow-shield` serves as a local gatekeeper utility that intercepts ingestion scripts:
1. **PII Risk Scopes:** Runs a local semantic audit on column metadata.
2. **Deterministic Masking:** Automatically masks exposed user fields (emails, credit card formats) on the fly before data ever leaves local systems.
3. **Structured Ingestion:** Handles zero-config schema inference and streams compliance-ready tables straight into Snowflake.

## 📋 Prerequisites

- Python 3.8+
- A Snowflake account with an active warehouse

## 🔧 Installation

```bash
pip install pandas snowflake-connector-python
```

## ⚙️ Configuration

snow-shield reads all Snowflake connection details from environment variables. Set the following before running the tool:

| Variable | Description |
|---|---|
| `SNOWFLAKE_USER` | Your Snowflake username |
| `SNOWFLAKE_PASSWORD` | Your Snowflake password |
| `SNOWFLAKE_ACCOUNT` | Your Snowflake account identifier (e.g. `xy12345.eu-west-1`) |
| `SNOWFLAKE_WAREHOUSE` | The warehouse to use for ingestion |
| `SNOWFLAKE_DATABASE` | Target database |
| `SNOWFLAKE_SCHEMA` | Target schema |

> **Security note:** Never hardcode credentials or commit `.env` files to version control. Use environment variables or a secrets manager.

## 🛠️ Usage

```bash
python snowshield.py ingest --file <path-to-csv> --table <target-table>
```

### Example

```bash
python snowshield.py ingest --file financial_logs.csv --table regulatory_audit_log
```

## 📖 Output
![alt text](image-1.png)

## 📖 CLI Reference

### `ingest`

Scans a local CSV file for PII, masks sensitive columns, and uploads the sanitized data to Snowflake.

| Flag | Required | Description |
|---|---|---|
| `--file` | ✅ | Path to the local transaction or audit log CSV file |
| `--table` | ✅ | Name of the target compliance table in Snowflake |

### PII Masking Rules

snow-shield automatically detects and masks the following column types based on column name:

| Column pattern | Masking applied |
|---|---|
| Contains `email` | First character preserved, domain kept — e.g. `j***@example.com` |
| Contains `card` or `cc` | Last 4 digits preserved — e.g. `****-****-****-1234` |

## 📄 License

This project is provided as-is for internal compliance tooling purposes.
