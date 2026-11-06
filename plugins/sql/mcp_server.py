#!/usr/bin/env python3
"""
mcp_server.py — Model Context Protocol (MCP) stdio server for SQL operations in AXIM / Berry.

Exposes native SQL database tools over JSON-RPC 2.0 stdio:
- sql_query: Run SELECT queries and retrieve datasets
- sql_execute: Run DDL/DML statements (CREATE, INSERT, UPDATE, DELETE)
- sql_tables_list: List all database tables and row counts
- sql_schema_inspect: Inspect schema, column types, and constraints
- sql_import_dataset: Ingest CSV/TSV/JSON datasets into SQL tables
- sql_export_dataset: Export tables or queries to CSV/JSON files
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure local sql_engine is importable
plugin_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(plugin_dir))

import sql_engine


TOOLS = [
    {
        "name": "sql_query",
        "description": "Execute a SQL SELECT query against a SQLite database and return formatted columns and rows.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL SELECT query string (e.g. 'SELECT id, name, price FROM products WHERE price > 50 ORDER BY price DESC')"
                },
                "db_path": {
                    "type": "string",
                    "description": "Path to SQLite database file. Defaults to ~/.axim/data/default.db"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of rows to return (default: 100)",
                    "default": 100
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "sql_execute",
        "description": "Execute a SQL DDL or DML statement (CREATE TABLE, INSERT, UPDATE, DELETE, ALTER, CREATE INDEX).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "statement": {
                    "type": "string",
                    "description": "SQL statement to execute (e.g. 'CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE)')"
                },
                "db_path": {
                    "type": "string",
                    "description": "Path to SQLite database file. Defaults to ~/.axim/data/default.db"
                }
            },
            "required": ["statement"]
        }
    },
    {
        "name": "sql_tables_list",
        "description": "List all tables and views in the database with their row and column counts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "db_path": {
                    "type": "string",
                    "description": "Path to SQLite database file. Defaults to ~/.axim/data/default.db"
                }
            },
            "required": []
        }
    },
    {
        "name": "sql_schema_inspect",
        "description": "Inspect the schema of a specific table, including column names, data types, primary keys, and indexes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Name of the table to inspect"
                },
                "db_path": {
                    "type": "string",
                    "description": "Path to SQLite database file. Defaults to ~/.axim/data/default.db"
                }
            },
            "required": ["table_name"]
        }
    },
    {
        "name": "sql_import_dataset",
        "description": "Import a CSV, TSV, JSON, or JSONL dataset into a SQL table with automatic schema and type inference.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to dataset file (.csv, .tsv, .json, .jsonl)"
                },
                "table_name": {
                    "type": "string",
                    "description": "Target SQL table name (derived from filename if omitted)"
                },
                "db_path": {
                    "type": "string",
                    "description": "Path to SQLite database file. Defaults to ~/.axim/data/default.db"
                },
                "if_exists": {
                    "type": "string",
                    "enum": ["replace", "append", "fail"],
                    "description": "Action if table exists ('replace', 'append', or 'fail'). Default: 'replace'",
                    "default": "replace"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "sql_export_dataset",
        "description": "Export a table or the result of a SQL query to a CSV or JSON file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_path": {
                    "type": "string",
                    "description": "Destination file path for the export (.csv or .json)"
                },
                "query_or_table": {
                    "type": "string",
                    "description": "Table name or SQL query to export"
                },
                "format": {
                    "type": "string",
                    "enum": ["csv", "json"],
                    "description": "Output format ('csv' or 'json'). Default: 'csv'",
                    "default": "csv"
                },
                "db_path": {
                    "type": "string",
                    "description": "Path to SQLite database file. Defaults to ~/.axim/data/default.db"
                }
            },
            "required": ["output_path", "query_or_table"]
        }
    }
]


def handle_tool_call(name: str, args: Dict[str, Any]) -> Any:
    db_path = args.get("db_path")

    if name == "sql_query":
        query = args["query"]
        limit = args.get("limit", 100)
        return sql_engine.execute_query(query, db_path=db_path, limit=limit)

    elif name == "sql_execute":
        stmt = args["statement"]
        return sql_engine.execute_statement(stmt, db_path=db_path)

    elif name == "sql_tables_list":
        return sql_engine.list_tables(db_path=db_path)

    elif name == "sql_schema_inspect":
        tbl = args["table_name"]
        return sql_engine.inspect_schema(tbl, db_path=db_path)

    elif name == "sql_import_dataset":
        fp = args["file_path"]
        tbl = args.get("table_name")
        if_exists = args.get("if_exists", "replace")
        return sql_engine.import_dataset(fp, table_name=tbl, db_path=db_path, if_exists=if_exists)

    elif name == "sql_export_dataset":
        out = args["output_path"]
        q_or_t = args["query_or_table"]
        fmt = args.get("format", "csv")
        return sql_engine.export_dataset(out, q_or_t, format=fmt, db_path=db_path)

    else:
        return {"error": f"Unknown tool: {name}"}


def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line_str = line.strip()
            if not line_str:
                continue

            msg = json.loads(line_str)
            msg_id = msg.get("id")
            method = msg.get("method")

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "sql-mcp",
                            "version": "1.0.0"
                        }
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "notifications/initialized":
                pass

            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": TOOLS
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "tools/call":
                params = msg.get("params", {})
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                result_data = handle_tool_call(tool_name, tool_args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result_data, indent=2, default=str)
                            }
                        ]
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            else:
                if msg_id is not None:
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method '{method}' not found"
                        }
                    }
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()

        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal MCP server error: {e}"
                }
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
