#!/usr/bin/env python3
"""
mcp_server.py — Model Context Protocol (MCP) Server for the AXIM Scan Plugin.
Author: Cognitus
Repository: https://github.com/Cognitus-Lab/Axim-Skills
License: LGPL-2.1-only / Apache-2.0

Allows Berry, Claude Desktop, Cursor, and any MCP client to perform automated static
analysis, bug discovery, supply-chain auditing, and secret detection over standard JSON-RPC 2.0 stdio.
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
    from axim_scan_engine import AximScanEngine, BUILTIN_RULES, SECRET_RULES, SUPPLY_CHAIN_PATTERNS
except ImportError:
    import axim_scan_engine
    AximScanEngine = axim_scan_engine.AximScanEngine
    BUILTIN_RULES = axim_scan_engine.BUILTIN_RULES
    SECRET_RULES = axim_scan_engine.SECRET_RULES
    SUPPLY_CHAIN_PATTERNS = axim_scan_engine.SUPPLY_CHAIN_PATTERNS

def _runtime_prologue() -> None:
    """Fail fast with an actionable message if the interpreter or engine is unusable.

    Berry users may install this plugin on machines where `python3` resolves to a
    different interpreter, or where the engine's imports are unavailable. Rather than
    crashing mid-session with a bare traceback, emit a clear diagnostic to stderr and
    exit non-zero so the MCP client reports a clean startup failure.
    """
    if sys.version_info < (3, 8):
        sys.stderr.write(
            "[axim-scan] ERROR: Python 3.8+ is required (found {}.{}).\n"
            "            Install Python 3.8 or newer, then restart Berry.\n".format(
                sys.version_info[0], sys.version_info[1]
            )
        )
        sys.exit(2)
    try:
        AximScanEngine()
    except Exception as exc:  # noqa: BLE001 - surface any import/init failure clearly
        sys.stderr.write(
            "[axim-scan] ERROR: failed to initialize the scan engine: {}\n"
            "            Verify `python3` on your PATH is a working interpreter and that\n"
            "            this plugin's files are intact, then restart Berry.\n".format(exc)
        )
        sys.exit(2)

engine = AximScanEngine()

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "axim_scan",
        "description": "Full-spectrum security scan across 30+ languages for OWASP Top 10 vulnerabilities, CWE bugs, supply-chain risks, and hardcoded secrets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_path": {
                    "type": "string",
                    "description": "Directory or file to scan (e.g. '.', 'src/', 'AXIM/Sources/')"
                },
                "config": {
                    "type": "string",
                    "description": "Rule configuration: 'default', 'builtin', 'p/security-audit', 'p/owasp-top-ten', 'p/secrets', 'p/supply-chain'",
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
                    "description": "Programming language (python, javascript, typescript, go, java, swift, rust, php, ruby, c, csharp, etc.)",
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
        "name": "axim_scan_pattern",
        "description": "Search code using semantic patterns with metavariables and wildcards (e.g. '$X == $X', 'os.system(...)', 'eval($X)').",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Semantic code pattern (e.g. '$X == $X', 'open(...)', 'dangerouslySetInnerHTML={...}')"
                },
                "target_path": {
                    "type": "string",
                    "description": "Directory or file to search",
                    "default": "."
                },
                "language": {
                    "type": "string",
                    "description": "Language filter",
                    "default": "python"
                }
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "axim_scan_supply_chain",
        "description": "Scan package manifests (package.json, go.mod, Cargo.toml, requirements.txt, Package.swift, pom.xml) for dependency risks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_path": {
                    "type": "string",
                    "description": "Directory or file path of package manifest",
                    "default": "."
                }
            },
            "required": []
        }
    },
    {
        "name": "axim_scan_secrets",
        "description": "Dedicated secrets and credential scanner: audits files for private keys, AWS tokens, JWTs, Stripe keys, and database passwords.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_path": {
                    "type": "string",
                    "description": "Directory or file to audit for secrets",
                    "default": "."
                }
            },
            "required": []
        }
    },
    {
        "name": "axim_scan_rules_list",
        "description": "List all built-in static analysis, supply chain, and secret rules across 30+ languages.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "description": "Optional language filter (e.g. 'python', 'javascript', 'swift', 'go')"
                }
            },
            "required": []
        }
    },
    {
        "name": "axim_scan_explain",
        "description": "Retrieve comprehensive AI remediation guidance, secure coding alternatives, and CWE/OWASP analysis for a specific vulnerability rule.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rule_id": {
                    "type": "string",
                    "description": "Vulnerability rule ID (e.g. 'axim.security.injection.sql-concat')"
                }
            },
            "required": ["rule_id"]
        }
    },
    {
        "name": "axim_scan_ensure_cli",
        "description": "Verify the AXIM Scan engine and check optional external CLI accelerators on the local machine.",
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

    elif name == "axim_scan_pattern":
        pattern = args.get("pattern", "")
        target = args.get("target_path", ".")
        lang = args.get("language", "python")
        return engine.scan_pattern(pattern, target, language=lang)

    elif name == "axim_scan_supply_chain":
        target = args.get("target_path", ".")
        res = engine.scan_path(target)
        sc_findings = [f for f in res.get("findings", []) if f.get("category") == "supply-chain"]
        res["findings"] = sc_findings
        res["findings_count"] = len(sc_findings)
        return engine.format_markdown(res)

    elif name == "axim_scan_secrets":
        target = args.get("target_path", ".")
        res = engine.scan_path(target)
        sec_findings = [f for f in res.get("findings", []) if f.get("category") == "secrets"]
        res["findings"] = sec_findings
        res["findings_count"] = len(sec_findings)
        return engine.format_markdown(res)

    elif name == "axim_scan_rules_list":
        lang = args.get("language")
        rules = engine.list_rules()
        if lang:
            rules = [r for r in rules if "all" in r["languages"] or lang.lower() in [l.lower() for l in r["languages"]]]
        return rules

    elif name == "axim_scan_explain":
        rule_id = args.get("rule_id", "")
        all_rules = BUILTIN_RULES + SECRET_RULES + SUPPLY_CHAIN_PATTERNS
        matched = next((r for r in all_rules if r["id"] == rule_id), None)
        if not matched:
            return {"error": f"Rule '{rule_id}' not found in catalog."}
        return {
            "id": matched["id"],
            "name": matched["name"],
            "severity": matched["severity"],
            "cwe": matched.get("cwe", "CWE-General"),
            "owasp": matched.get("owasp", "General"),
            "message": matched["message"],
            "remediation": matched["fix"],
            "languages": matched.get("languages", ["all"])
        }

    elif name == "axim_scan_ensure_cli":
        cli = shutil.which("semgrep")
        return {
            "status": "ready",
            "native_engine": "axim-scan-native (active, 30+ languages supported)",
            "external_cli": cli or "not_installed (optional accelerator)",
            "capabilities": ["sast", "sca_supply_chain", "secrets", "semantic_pattern_search", "ai_remediation"]
        }

    return {"error": f"Unknown tool '{name}'"}


def _respond(msg_id: Any, result: Any) -> None:
    resp = {"jsonrpc": "2.0", "id": msg_id, "result": result}
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()


def main() -> None:
    _runtime_prologue()
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
