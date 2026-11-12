#!/usr/bin/env python3
"""
mcp_server.py — Model Context Protocol (MCP) Server for the AXIM Scan Plugin.
Author: Cognitus
Repository: https://github.com/Cognitus-Lab/Axim-Skills

Allows Berry, Claude Desktop, Cursor, and any MCP client to perform automated static
analysis, bug discovery, and security scans over standard JSON-RPC 2.0 stdio.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add current directory to import path for axim_scan_engine
PLUGIN_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(PLUGIN_DIR))

try:
    from axim_scan_engine import AximScanEngine, BUILTIN_RULES
except ImportError:
    import axim_scan_engine
    AximScanEngine = axim_scan_engine.AximScanEngine
    BUILTIN_RULES = axim_scan_engine.BUILTIN_RULES

engine = AximScanEngine()

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "axim_scan",
        "description": "Scan a directory, workspace, or file for security vulnerabilities, bugs, CWEs, OWASP Top 10 risks, and hardcoded secrets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_path": {
                    "type": "string",
                    "description": "Directory or file to scan (e.g. '.', 'src/', 'AXIM/Sources/')"
                },
                "config": {
                    "type": "string",
                    "description": "Rule configuration: 'default', 'builtin', 'p/security-audit', 'p/owasp-top-ten', 'p/secrets'",
                    "default": "default"
                },
                "severity": {
                    "type": "string",
                    "description": "Filter by minimum severity: 'INFO', 'WARNING', 'ERROR'",
                    "enum": ["INFO", "WARNING", "ERROR"]
                },
                "output_format": {
                    "type": "string",
                    "description": "Format for results: 'markdown', 'json', 'summary'",
                    "enum": ["markdown", "json", "summary"],
                    "default": "markdown"
                }
            },
            "required": ["target_path"]
        }
    },
    {
        "name": "axim_scan_code",
        "description": "Scan an arbitrary code snippet in memory for security vulnerabilities, OWASP flaws, and bugs without writing to disk.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Source code text to analyze"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language (python, javascript, typescript, go, java, swift, rust, php, ruby, c)",
                    "default": "python"
                },
                "output_format": {
                    "type": "string",
                    "description": "Format for results: 'markdown' or 'json'",
                    "enum": ["markdown", "json"],
                    "default": "markdown"
                }
            },
            "required": ["code"]
        }
    },
    {
        "name": "axim_scan_rules_list",
        "description": "List all built-in static analysis and security rules across languages (OWASP Top 10, CWEs, Secrets, Injections).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "description": "Optional language filter (e.g. 'python', 'javascript', 'swift')"
                }
            },
            "required": []
        }
    },
    {
        "name": "axim_scan_explain",
        "description": "Retrieve comprehensive remediation guidance, secure coding examples, and CWE/OWASP analysis for a specific vulnerability rule.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rule_id": {
                    "type": "string",
                    "description": "Vulnerability rule ID (e.g. 'axim.security.injection.sql-string-concat')"
                }
            },
            "required": ["rule_id"]
        }
    },
    {
        "name": "axim_scan_ensure_cli",
        "description": "Verify or provision the AXIM Scan engine and optional external AST scanner on the local machine.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


def handle_tool(name: str, args: Dict[str, Any]) -> Any:
    if name == "axim_scan":
        target = args.get("target_path", ".")
        config = args.get("config", "default")
        severity = args.get("severity")
        fmt = args.get("output_format", "markdown")

        res = engine.scan_path(target, config=config, severity=severity)
        if fmt == "json":
            return res
        elif fmt == "summary":
            return {
                "target": res.get("target"),
                "files_scanned": res.get("files_scanned"),
                "findings_count": res.get("findings_count"),
                "has_errors": any(f.get("severity") == "ERROR" for f in res.get("findings", []))
            }
        else:
            return engine.format_markdown(res)

    elif name == "axim_scan_code":
        code = args.get("code", "")
        lang = args.get("language", "python")
        fmt = args.get("output_format", "markdown")

        res = engine.scan_code(code, language=lang)
        if fmt == "json":
            return res
        return engine.format_markdown(res)

    elif name == "axim_scan_rules_list":
        lang = args.get("language")
        rules = engine.list_rules()
        if lang:
            rules = [r for r in rules if "all" in r["languages"] or lang.lower() in [l.lower() for l in r["languages"]]]
        return rules

    elif name == "axim_scan_explain":
        rule_id = args.get("rule_id", "")
        matched = next((r for r in BUILTIN_RULES if r["id"] == rule_id), None)
        if not matched:
            return {"error": f"Rule '{rule_id}' not found in catalog."}
        return {
            "id": matched["id"],
            "name": matched["name"],
            "severity": matched["severity"],
            "cwe": matched["cwe"],
            "owasp": matched["owasp"],
            "message": matched["message"],
            "remediation": matched["fix"],
            "languages": matched["languages"]
        }

    elif name == "axim_scan_ensure_cli":
        cli = shutil.which("semgrep")
        return {
            "status": "ready",
            "native_engine": "axim-scan-native (active)",
            "external_cli": cli or "not_installed (optional)",
            "message": "AXIM Scan engine is fully operational. Native multi-language rules are active."
        }

    return {"error": f"Unknown tool '{name}'"}


def _respond(msg_id: Any, result: Any) -> None:
    resp = {"jsonrpc": "2.0", "id": msg_id, "result": result}
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()


def main() -> None:
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
                _respond(msg_id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "axim-scan-mcp",
                        "version": "1.0.0"
                    }
                })

            elif method == "notifications/initialized":
                pass

            elif method == "tools/list":
                _respond(msg_id, {"tools": TOOLS})

            elif method == "tools/call":
                params = msg.get("params", {})
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                res = handle_tool(tool_name, tool_args)
                text_content = res if isinstance(res, str) else json.dumps(res, indent=2, default=str)
                _respond(msg_id, {
                    "content": [
                        {
                            "type": "text",
                            "text": text_content
                        }
                    ]
                })

            elif method == "ping":
                _respond(msg_id, {})

            else:
                if msg_id is not None:
                    _respond(msg_id, {"error": f"Method '{method}' not found"})

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
