# SQL Plugin for AXIM & Berry

> Local and remote SQL database management, dataset ingestion, and query engine for AXIM agents.

## Overview

The `sql` plugin enables AXIM / Berry agents running on personal computers to store and retrieve structured datasets with zero external dependencies. Powered by SQLite and Python's built-in database drivers, it allows agents to:

- Create and modify relational database tables.
- Ingest CSV, TSV, and JSON datasets with automatic schema and type inference.
- Run rich analytical queries (`SELECT`, `JOIN`, `GROUP BY`, `ORDER BY`).
- Retrieve and paginate records directly into LLM agent contexts.
- Export query results to clean CSV or JSON formats.

## Included Tools

| Tool | Purpose |
|------|---------|
| `sql_query` | Run analytical SELECT queries and retrieve dataset records |
| `sql_execute` | Execute DDL/DML statements (`CREATE`, `INSERT`, `UPDATE`, `DELETE`) |
| `sql_tables_list` | Discover tables and inspect row counts |
| `sql_schema_inspect` | Inspect table columns, types, primary keys, and indexes |
| `sql_import_dataset` | Import CSV, TSV, JSON, or JSONL files into SQL tables |
| `sql_export_dataset` | Export table or query results to CSV or JSON files |

## Default Database Location
- `~/.axim/data/default.db` (or `./data/default.db` in workspace if home directory is sandboxed).
- Custom database files can be designated by passing `db_path="path/to/custom.db"`.
