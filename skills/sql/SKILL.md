---
name: sql
description: Store, query, and retrieve structured datasets using local and remote SQL databases (SQLite, PostgreSQL, MySQL) with automatic CSV/JSON ingestion, schema inspection, and data export.
keywords:
  - sql
  - database
  - sqlite
  - dataset
  - store dataset
  - retrieve dataset
  - sql query
  - select query
  - create table
  - insert data
  - import csv
  - export json
  - relational database
  - data analytics
---

# SQL Database & Dataset Management Skill

The `sql` plugin provides local, zero-configuration SQL database capabilities for AXIM / Berry agents running on personal computers. It uses an embedded SQLite database by default (`~/.axim/data/default.db` or workspace `./data/default.db`) with zero external service dependencies, allowing agents to store, structure, transform, and retrieve datasets seamlessly.

---

## Capabilities

1. **Store Datasets**:
   - Automatically ingest CSV, TSV, JSON, and JSON Lines datasets into typed SQL tables (`sql_import_dataset`).
   - Create custom tables with primary keys, indexes, and constraints (`sql_execute`).
   - Insert and update records transactionally (`sql_execute`).

2. **Retrieve Datasets**:
   - Run complex relational queries (`SELECT`, `JOIN`, `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`) (`sql_query`).
   - Paginate and format query results as structured JSON (`sql_query`).
   - Discover tables and row counts across the database (`sql_tables_list`).
   - Inspect table schemas, column types, and constraints (`sql_schema_inspect`).

3. **Export Datasets**:
   - Export query results or complete tables directly into CSV or JSON files (`sql_export_dataset`).

---

## Tool Reference & Invocation

### 1. `sql_import_dataset`
Ingest an existing file (CSV, TSV, JSON, JSONL) into a new or existing SQL table. Automatically infers column data types (`INTEGER`, `REAL`, `TEXT`).
```json
{
  "name": "sql_import_dataset",
  "arguments": {
    "file_path": "data/sales_q3.csv",
    "table_name": "sales_q3",
    "if_exists": "replace"
  }
}
```

### 2. `sql_query`
Execute a SELECT query against the local database to retrieve datasets and analytics.
```json
{
  "name": "sql_query",
  "arguments": {
    "query": "SELECT category, COUNT(*) AS total_sales, ROUND(AVG(amount), 2) AS avg_ticket FROM sales_q3 GROUP BY category ORDER BY total_sales DESC LIMIT 10",
    "limit": 50
  }
}
```

### 3. `sql_execute`
Execute DDL or DML statements (table creation, schema changes, updates, insertions, deletions).
```json
{
  "name": "sql_execute",
  "arguments": {
    "statement": "CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
  }
}
```

### 4. `sql_tables_list`
List all tables and views in the database with their current row counts and column counts.
```json
{
  "name": "sql_tables_list",
  "arguments": {}
}
```

### 5. `sql_schema_inspect`
Inspect columns, types, primary keys, and indexes for any table.
```json
{
  "name": "sql_schema_inspect",
  "arguments": {
    "table_name": "sales_q3"
  }
}
```

### 6. `sql_export_dataset`
Export table records or query results to a CSV or JSON file.
```json
{
  "name": "sql_export_dataset",
  "arguments": {
    "output_path": "exports/top_sales.csv",
    "query_or_table": "SELECT * FROM sales_q3 WHERE amount > 500",
    "format": "csv"
  }
}
```

---

## Database Path Resolution
- **Default Database**: If `db_path` is omitted, data is persisted to `~/.axim/data/default.db` (or `./data/default.db` in workspace).
- **Custom Project Database**: Pass `db_path="my_project.db"` to maintain an isolated database inside your project repository.
- **In-Memory**: Pass `db_path=":memory:"` for ephemeral scratch analysis that leaves no disk footprint.

---

## Best Practices
- **Safe Escaping**: All table and column names are escaped to prevent SQL injection during dataset import.
- **Transactions**: DDL and DML statements are executed with automatic commits; if an error occurs, changes are safely rolled back.
- **Performance**: For large datasets, create indexes on frequently filtered or joined columns (`CREATE INDEX idx_col ON table(col)`).
