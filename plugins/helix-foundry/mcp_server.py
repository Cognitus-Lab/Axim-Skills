#!/usr/bin/env python3
"""
mcp_server.py — Model Context Protocol (MCP) stdio server for Helix Foundry in AXIM / Berry.

Implements JSON-RPC 2.0 stdio transport exposing Helix Foundry tools:
- helix_foundry_status
- helix_foundry_stack_up
- helix_foundry_stack_down
- helix_foundry_stack_logs
- helix_foundry_list_ontologies
- helix_foundry_get_ontology
- helix_foundry_list_connectors
- helix_foundry_list_connector_kinds
- helix_foundry_list_documents
- helix_foundry_send_pieces
- helix_foundry_ask
"""

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional


FOUNDRY_ORIGIN = os.environ.get("FOUNDRY_ORIGIN", "http://localhost:3000").rstrip("/")
HELIX_WFE_ORIGIN = os.environ.get("HELIX_WFE_ORIGIN", "http://127.0.0.1:8081").rstrip("/")
REPO_ROOT = Path(__file__).parent.resolve()


def _http_request(url: str, method: str = "GET", data: Optional[Dict[str, Any]] = None, timeout: float = 5.0) -> Dict[str, Any]:
    req = urllib.request.Request(url, method=method)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "AXIM-Helix-Foundry-MCP/1.0")
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    else:
        body = None

    try:
        with urllib.request.urlopen(req, data=body, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read().decode("utf-8")
            if "application/json" in content_type or raw.strip().startswith("{") or raw.strip().startswith("["):
                try:
                    return {"status": resp.status, "data": json.loads(raw)}
                except Exception:
                    return {"status": resp.status, "data": raw}
            return {"status": resp.status, "data": raw}
    except urllib.error.HTTPError as e:
        raw_err = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw_err)
        except Exception:
            parsed = raw_err
        return {"error": f"HTTP {e.code}: {e.reason}", "status": e.code, "details": parsed}
    except urllib.error.URLError as e:
        return {"error": f"Connection failed: {e.reason}", "offline": True}
    except Exception as e:
        return {"error": str(e)}


TOOLS = [
    {
        "name": "helix_foundry_status",
        "description": "Check if Helix Foundry (local stack or server) is running, accessible, and healthy.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "helix_foundry_stack_up",
        "description": "Start the local Helix Foundry stack via Docker Compose in the background.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "profile": {
                    "type": "string",
                    "description": "Optional Docker Compose profile (e.g. 'ollama')"
                }
            },
            "required": []
        }
    },
    {
        "name": "helix_foundry_stack_down",
        "description": "Stop the local Helix Foundry stack cleanly without removing data volumes.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "helix_foundry_stack_logs",
        "description": "Fetch recent logs from running Helix Foundry services.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lines": {
                    "type": "integer",
                    "description": "Number of log lines to retrieve (default: 40)",
                    "default": 40
                }
            },
            "required": []
        }
    },
    {
        "name": "helix_foundry_list_ontologies",
        "description": "List all ontologies in the current Helix Foundry workspace.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {
                    "type": "string",
                    "description": "Workspace ID (defaults to 'ws_acme' or local workspace)"
                }
            },
            "required": []
        }
    },
    {
        "name": "helix_foundry_get_ontology",
        "description": "Get complete ontology schema, entity types, relationships, rules, and load status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ontology_id": {
                    "type": "string",
                    "description": "Ontology ID to inspect"
                },
                "workspace_id": {
                    "type": "string",
                    "description": "Workspace ID"
                }
            },
            "required": ["ontology_id"]
        }
    },
    {
        "name": "helix_foundry_list_connectors",
        "description": "List all active connectors and synced database tables in the workspace.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {
                    "type": "string",
                    "description": "Workspace ID"
                }
            },
            "required": []
        }
    },
    {
        "name": "helix_foundry_list_connector_kinds",
        "description": "List connector kinds supported by Helix Foundry (PostgreSQL, MySQL, S3, Stripe, Slack, Notion, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "helix_foundry_list_documents",
        "description": "List documents in document sets uploaded to Helix Foundry.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {
                    "type": "string",
                    "description": "Workspace ID"
                },
                "set_id": {
                    "type": "string",
                    "description": "Optional document set ID"
                }
            },
            "required": []
        }
    },
    {
        "name": "helix_foundry_send_pieces",
        "description": "Send pieces of structured JSON data into a Helix Foundry event/API source.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_source_id": {
                    "type": "string",
                    "description": "Event / API connector ID"
                },
                "pieces": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of JSON records with an 'id' and payload"
                },
                "client_token": {
                    "type": "string",
                    "description": "Unique client UUID for idempotency"
                },
                "workspace_id": {
                    "type": "string",
                    "description": "Workspace ID"
                }
            },
            "required": ["event_source_id", "pieces"]
        }
    },
    {
        "name": "helix_foundry_ask",
        "description": "Ask the Helix Foundry Analyst a question against a loaded graph ontology.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Natural language question to ask"
                },
                "ontology_id": {
                    "type": "string",
                    "description": "Target ontology ID"
                },
                "workspace_id": {
                    "type": "string",
                    "description": "Workspace ID"
                }
            },
            "required": ["question"]
        }
    }
]


def handle_tool_call(name: str, args: Dict[str, Any]) -> Any:
    ws_id = args.get("workspace_id", "ws_acme")

    if name == "helix_foundry_status":
        # Check web UI and WFE/API
        web_res = _http_request(f"{FOUNDRY_ORIGIN}/")
        wfe_res = _http_request(f"{HELIX_WFE_ORIGIN}/v1/whoami")
        is_up = not web_res.get("offline") or not wfe_res.get("offline")
        return {
            "running": is_up,
            "origin": FOUNDRY_ORIGIN,
            "wfe_origin": HELIX_WFE_ORIGIN,
            "web_status": web_res,
            "wfe_status": wfe_res,
            "note": "Helix Foundry is operational." if is_up else "Helix Foundry stack is not responding on standard ports. Run helix_foundry_stack_up to launch with Docker Compose."
        }

    elif name == "helix_foundry_stack_up":
        cmd = ["docker", "compose", "up", "-d", "--wait"]
        profile = args.get("profile")
        if profile:
            cmd = ["docker", "compose", "--profile", profile, "up", "-d", "--wait"]
        try:
            res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60)
            return {
                "success": res.returncode == 0,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "returncode": res.returncode
            }
        except Exception as e:
            return {"error": f"Failed to execute docker compose: {e}"}

    elif name == "helix_foundry_stack_down":
        try:
            res = subprocess.run(["docker", "compose", "stop"], cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30)
            return {
                "success": res.returncode == 0,
                "stdout": res.stdout,
                "stderr": res.stderr
            }
        except Exception as e:
            return {"error": f"Failed to stop docker compose: {e}"}

    elif name == "helix_foundry_stack_logs":
        lines = str(args.get("lines", 40))
        try:
            res = subprocess.run(["docker", "compose", "logs", f"--tail={lines}"], cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=15)
            return {
                "stdout": res.stdout,
                "stderr": res.stderr
            }
        except Exception as e:
            return {"error": f"Failed to read logs: {e}"}

    elif name == "helix_foundry_list_ontologies":
        url = f"{HELIX_WFE_ORIGIN}/v1/workspaces/{ws_id}/foundry/ontologies"
        res = _http_request(url)
        if res.get("offline"):
            return {
                "error": "Helix Foundry backend is offline.",
                "hint": "Start the stack using 'helix_foundry_stack_up' or run 'pnpm dev:mock' in the plugin folder."
            }
        return res

    elif name == "helix_foundry_get_ontology":
        ont_id = args["ontology_id"]
        url = f"{HELIX_WFE_ORIGIN}/v1/workspaces/{ws_id}/foundry/ontologies/{ont_id}"
        return _http_request(url)

    elif name == "helix_foundry_list_connectors":
        url = f"{HELIX_WFE_ORIGIN}/v1/workspaces/{ws_id}/foundry/connectors"
        return _http_request(url)

    elif name == "helix_foundry_list_connector_kinds":
        url = f"{HELIX_WFE_ORIGIN}/v1/workspaces/{ws_id}/foundry/connector-kinds"
        return _http_request(url)

    elif name == "helix_foundry_list_documents":
        set_id = args.get("set_id")
        if set_id:
            url = f"{HELIX_WFE_ORIGIN}/v1/workspaces/{ws_id}/foundry/document-sets/{set_id}/documents"
        else:
            url = f"{HELIX_WFE_ORIGIN}/v1/workspaces/{ws_id}/foundry/document-sets"
        return _http_request(url)

    elif name == "helix_foundry_send_pieces":
        src_id = args["event_source_id"]
        pieces = args["pieces"]
        token = args.get("client_token", "axim-token-1")
        payload = {"client_token": token, "pieces": pieces}
        url = f"{HELIX_WFE_ORIGIN}/v1/workspaces/{ws_id}/foundry/connectors/{src_id}/pieces"
        return _http_request(url, method="POST", data=payload)

    elif name == "helix_foundry_ask":
        question = args["question"]
        ont_id = args.get("ontology_id", "default")
        payload = {"question": question}
        url = f"{HELIX_WFE_ORIGIN}/v1/workspaces/{ws_id}/foundry/ontologies/{ont_id}/ask"
        return _http_request(url, method="POST", data=payload)

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
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "helix-foundry-mcp",
                            "version": "1.0.0"
                        }
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "notifications/initialized":
                # No response needed for notification
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
                                "text": json.dumps(result_data, indent=2)
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
