"""
sql_engine.py — Core SQL engine for dataset storage and retrieval in AXIM / Berry.

Features:
- Out-of-the-box local SQLite engine with zero configuration.
- Safe table & column escaping to protect against injection.
- Automatic dataset ingestion from CSV, TSV, JSON, and JSON Lines with column type inference.
- Query execution with result set serialization and truncation control.
- DDL and DML execution with transaction management.
- Schema inspection (columns, types, primary keys, indexes).
- Dataset export to CSV and JSON.
"""

from __future__ import annotations

import csv
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


DEFAULT_DB_PATH = Path.home() / ".axim" / "data" / "default.db"
FALLBACK_WORKSPACE_DB = Path("./data/default.db")
FALLBACK_TMP_DB = Path("/tmp/axim_data/default.db")


def resolve_db_path(db_path: Optional[str] = None) -> Path:
    """
    Resolve database path, creating parent directory if necessary.
    Gracefully falls back to workspace ./data or /tmp/axim_data if home dir is sandboxed.
    """
    if not db_path or db_path.strip() in ("", ":default:", "default"):
        candidates = [DEFAULT_DB_PATH, FALLBACK_WORKSPACE_DB, FALLBACK_TMP_DB]
        for candidate in candidates:
            try:
                candidate.parent.mkdir(parents=True, exist_ok=True)
                return candidate.resolve()
            except (PermissionError, OSError):
                continue
        # Fallback to local file in current directory
        return Path("default.db").resolve()

    target = Path(db_path).expanduser().resolve()
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        return target
    except (PermissionError, OSError):
        # Sandboxed or restricted parent: fallback to /tmp/axim_data
        fallback = FALLBACK_TMP_DB.parent / target.name
        fallback.parent.mkdir(parents=True, exist_ok=True)
        return fallback


def _escape_ident(name: str) -> str:
    """Escape SQL identifier (table or column name) safely."""
    clean = name.strip().replace('"', '""')
    return f'"{clean}"'


def _infer_type(values: List[str]) -> str:
    """Infer SQLite column type from non-empty string sample values."""
    is_int = True
    is_float = True

    has_non_empty = False
    for v in values:
        v_str = str(v).strip()
        if not v_str:
            continue
        has_non_empty = True

        # Check integer
        if is_int:
            try:
                int(v_str)
            except ValueError:
                is_int = False

        # Check float
        if is_float:
            try:
                float(v_str)
            except ValueError:
                is_float = False

    if not has_non_empty:
        return "TEXT"
    if is_int:
        return "INTEGER"
    if is_float:
        return "REAL"
    return "TEXT"


def execute_query(
    query: str,
    db_path: Optional[str] = None,
    params: Optional[Union[List[Any], Dict[str, Any]]] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Execute a SELECT query and return structured column and row data."""
    target_path = resolve_db_path(db_path)
    p = params or []

    conn = sqlite3.connect(str(target_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(query, p)
        columns = [d[0] for d in cur.description] if cur.description else []
        rows_raw = cur.fetchmany(limit + 1)
        truncated = len(rows_raw) > limit
        selected_rows = rows_raw[:limit]

        results = []
        for r in selected_rows:
            results.append({col: r[col] for col in columns})

        return {
            "success": True,
            "database": str(target_path),
            "columns": columns,
            "rows": results,
            "row_count": len(results),
            "limit": limit,
            "truncated": truncated,
        }
    except Exception as e:
        return {
            "success": False,
            "database": str(target_path),
            "error": str(e),
        }
    finally:
        conn.close()


def execute_statement(
    statement: str,
    db_path: Optional[str] = None,
    params: Optional[Union[List[Any], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Execute a DDL or DML statement (CREATE, INSERT, UPDATE, DELETE, etc.)."""
    target_path = resolve_db_path(db_path)
    p = params or []

    conn = sqlite3.connect(str(target_path), timeout=30.0)
    try:
        cur = conn.cursor()
        cur.execute(statement, p)
        conn.commit()
        return {
            "success": True,
            "database": str(target_path),
            "rows_affected": cur.rowcount,
            "last_insert_rowid": cur.lastrowid,
        }
    except Exception as e:
        conn.rollback()
        return {
            "success": False,
            "database": str(target_path),
            "error": str(e),
        }
    finally:
        conn.close()


def list_tables(db_path: Optional[str] = None) -> Dict[str, Any]:
    """List all tables and views in the database with row counts."""
    target_path = resolve_db_path(db_path)
    if not target_path.exists():
        return {"success": True, "database": str(target_path), "tables": []}

    conn = sqlite3.connect(str(target_path), timeout=30.0)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        items = cur.fetchall()
        tables_info = []
        for name, item_type in items:
            try:
                cnt_cur = conn.cursor()
                cnt_cur.execute(f'SELECT COUNT(*) FROM "{name}"')
                row_count = cnt_cur.fetchone()[0]
            except Exception:
                row_count = -1

            try:
                col_cur = conn.cursor()
                col_cur.execute(f'PRAGMA table_info("{name}")')
                col_count = len(col_cur.fetchall())
            except Exception:
                col_count = 0

            tables_info.append({
                "name": name,
                "type": item_type,
                "row_count": row_count,
                "column_count": col_count,
            })

        return {
            "success": True,
            "database": str(target_path),
            "tables": tables_info,
            "total_tables": len(tables_info),
        }
    except Exception as e:
        return {"success": False, "database": str(target_path), "error": str(e)}
    finally:
        conn.close()


def inspect_schema(table_name: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Inspect schema for a specific table (columns, types, constraints, indexes)."""
    target_path = resolve_db_path(db_path)
    conn = sqlite3.connect(str(target_path), timeout=30.0)
    try:
        cur = conn.cursor()
        # Columns
        cur.execute(f'PRAGMA table_info("{table_name}")')
        cols = cur.fetchall()
        if not cols:
            return {
                "success": False,
                "database": str(target_path),
                "error": f"Table '{table_name}' does not exist",
            }

        columns = []
        for c in cols:
            columns.append({
                "cid": c[0],
                "name": c[1],
                "type": c[2],
                "notnull": bool(c[3]),
                "default_value": c[4],
                "primary_key": bool(c[5]),
            })

        # Foreign keys
        cur.execute(f'PRAGMA foreign_key_list("{table_name}")')
        fk_rows = cur.fetchall()
        foreign_keys = [
            {"id": fk[0], "table": fk[2], "from": fk[3], "to": fk[4]}
            for fk in fk_rows
        ]

        # Indexes
        cur.execute(f'PRAGMA index_list("{table_name}")')
        idx_rows = cur.fetchall()
        indexes = [
            {"name": idx[1], "unique": bool(idx[2]), "origin": idx[3]}
            for idx in idx_rows
        ]

        return {
            "success": True,
            "database": str(target_path),
            "table": table_name,
            "columns": columns,
            "foreign_keys": foreign_keys,
            "indexes": indexes,
        }
    except Exception as e:
        return {"success": False, "database": str(target_path), "error": str(e)}
    finally:
        conn.close()


def import_dataset(
    file_path: str,
    table_name: Optional[str] = None,
    db_path: Optional[str] = None,
    if_exists: str = "replace",  # "replace", "append", "fail"
) -> Dict[str, Any]:
    """
    Import CSV, TSV, or JSON file directly into a SQL table.
    Infers column types and automatically creates table if needed.
    """
    src = Path(file_path).expanduser().resolve()
    if not src.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    tbl = table_name.strip() if table_name else src.stem
    tbl = re.sub(r"[^\w_]", "_", tbl).lower()

    ext = src.suffix.lower()
    records: List[Dict[str, Any]] = []

    # 1. Read input data
    if ext in (".csv", ".tsv", ".txt"):
        delimiter = "\t" if ext == ".tsv" else ","
        with open(src, "r", encoding="utf-8", errors="replace") as f:
            sample = f.read(4096)
            f.seek(0)
            if ext != ".tsv":
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    delimiter = dialect.delimiter
                except Exception:
                    delimiter = ","
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                records.append(row)

    elif ext in (".json", ".jsonl"):
        with open(src, "r", encoding="utf-8", errors="replace") as f:
            if ext == ".jsonl":
                for line in f:
                    line_s = line.strip()
                    if line_s:
                        records.append(json.loads(line_s))
            else:
                data = json.load(f)
                if isinstance(data, list):
                    records = data
                elif isinstance(data, dict):
                    # Check for "rows", "data", "records", or "items"
                    for k in ("rows", "data", "records", "items", "results"):
                        if k in data and isinstance(data[k], list):
                            records = data[k]
                            break
                    if not records:
                        records = [data]
    else:
        return {"success": False, "error": f"Unsupported file extension: {ext}. Use .csv, .tsv, .json, or .jsonl"}

    if not records:
        return {"success": False, "error": "No records found in dataset file."}

    # 2. Extract columns and infer types
    all_keys = []
    seen_keys = set()
    for r in records[:500]:
        for k in r.keys():
            if k not in seen_keys:
                seen_keys.add(k)
                all_keys.append(k)

    type_samples: Dict[str, List[str]] = {k: [] for k in all_keys}
    for r in records[:200]:
        for k in all_keys:
            v = r.get(k)
            if v is not None:
                type_samples[k].append(str(v))

    col_types = {k: _infer_type(type_samples[k]) for k in all_keys}

    # 3. Connect and create table
    target_path = resolve_db_path(db_path)
    conn = sqlite3.connect(str(target_path), timeout=30.0)
    try:
        cur = conn.cursor()

        # Check existing table
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tbl,))
        exists = cur.fetchone() is not None

        if exists:
            if if_exists == "fail":
                return {"success": False, "error": f"Table '{tbl}' already exists and if_exists='fail'"}
            elif if_exists == "replace":
                cur.execute(f'DROP TABLE "{tbl}"')
                exists = False

        if not exists:
            col_defs = [f'{_escape_ident(k)} {col_types[k]}' for k in all_keys]
            create_sql = f'CREATE TABLE {_escape_ident(tbl)} ({", ".join(col_defs)})'
            cur.execute(create_sql)

        # 4. Insert rows
        cols_escaped = ", ".join([_escape_ident(k) for k in all_keys])
        placeholders = ", ".join(["?" for _ in all_keys])
        insert_sql = f'INSERT INTO {_escape_ident(tbl)} ({cols_escaped}) VALUES ({placeholders})'

        batch_data = []
        for r in records:
            vals = []
            for k in all_keys:
                val = r.get(k)
                if val is None or val == "":
                    vals.append(None)
                elif col_types[k] == "INTEGER":
                    try:
                        vals.append(int(val))
                    except (ValueError, TypeError):
                        vals.append(val)
                elif col_types[k] == "REAL":
                    try:
                        vals.append(float(val))
                    except (ValueError, TypeError):
                        vals.append(val)
                else:
                    if isinstance(val, (dict, list)):
                        vals.append(json.dumps(val))
                    else:
                        vals.append(str(val))
            batch_data.append(vals)

        cur.executemany(insert_sql, batch_data)
        conn.commit()

        return {
            "success": True,
            "database": str(target_path),
            "table": tbl,
            "rows_imported": len(batch_data),
            "columns": [{"name": k, "type": col_types[k]} for k in all_keys],
        }
    except Exception as e:
        conn.rollback()
        return {"success": False, "database": str(target_path), "error": str(e)}
    finally:
        conn.close()


def export_dataset(
    output_path: str,
    query_or_table: str,
    format: str = "csv",  # "csv" or "json"
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Export table or query results to CSV or JSON file."""
    target_path = resolve_db_path(db_path)
    out_file = Path(output_path).expanduser().resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    query = query_or_table.strip()
    if not query.upper().startswith("SELECT") and not query.upper().startswith("WITH"):
        query = f'SELECT * FROM {_escape_ident(query)}'

    conn = sqlite3.connect(str(target_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(query)
        columns = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()

        fmt = format.lower().strip()
        if fmt == "json":
            data = [{col: r[col] for col in columns} for r in rows]
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        else:
            with open(out_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                for r in rows:
                    writer.writerow([r[col] for col in columns])

        return {
            "success": True,
            "database": str(target_path),
            "output_path": str(out_file),
            "rows_exported": len(rows),
            "columns": columns,
            "format": fmt,
        }
    except Exception as e:
        return {"success": False, "database": str(target_path), "error": str(e)}
    finally:
        conn.close()
