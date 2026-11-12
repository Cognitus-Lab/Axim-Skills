#!/usr/bin/env python3
"""
mcp_server.py — Root Model Context Protocol (MCP) server for Axim-Skills.
Repository: https://github.com/Cognitus-Lab/Axim-Skills

Enables any MCP client (Berry, Claude Desktop, Cursor, etc.) to connect to
Axim-Skills over standard JSON-RPC 2.0 stdio to discover, inspect, and invoke
all bundled skills and plugins.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).parent.resolve()
SKILLS_DIR = ROOT_DIR / "skills"
PLUGINS_DIR = ROOT_DIR / "plugins"

CORE_TOOLS = [
    {
        "name": "axim_list_skills",
        "description": "List all skills available in the Axim-Skills catalog with summaries and categories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filter": {"type": "string", "description": "Optional keyword filter for skill names or summaries"}
            },
            "required": []
        }
    },
    {
        "name": "axim_get_skill",
        "description": "Retrieve the full documentation, system directives, and instructions (SKILL.md) for a specific skill.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "skill_name": {"type": "string", "description": "Exact name or directory of the skill"}
            },
            "required": ["skill_name"]
        }
    },
    {
        "name": "axim_list_plugins",
        "description": "List all plugins available in Axim-Skills, their manifests, tools, and MCP servers.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "axim_call_plugin_tool",
        "description": "Invoke an MCP tool provided by one of the Axim plugins (e.g. bruno, sql, task-engine, helix-foundry).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "plugin": {"type": "string", "description": "Plugin name (e.g. 'bruno', 'sql', 'task-engine')"},
                "tool_name": {"type": "string", "description": "Tool to invoke (e.g. 'bruno_run', 'sql_query')"},
                "arguments": {"type": "object", "description": "Tool argument payload"}
            },
            "required": ["plugin", "tool_name"]
        }
    }
]


def list_skills(keyword: str = "") -> List[Dict[str, Any]]:
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    kw = (keyword or "").lower().strip()
    for entry in sorted(SKILLS_DIR.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            skill_md = entry / "SKILL.md"
            summary = ""
            if skill_md.exists():
                try:
                    lines = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
                    for line in lines[:20]:
                        if line.startswith("# "):
                            summary = line[2:].strip()
                            break
                        elif line.lower().startswith("description:"):
                            summary = line.split(":", 1)[1].strip()
                            break
                except Exception:
                    pass
            if not kw or kw in entry.name.lower() or kw in summary.lower():
                skills.append({
                    "name": entry.name,
                    "path": str(entry),
                    "summary": summary or f"Axim skill: {entry.name}"
                })
    return skills


def get_skill(name: str) -> Dict[str, Any]:
    target = SKILLS_DIR / name
    if not target.exists():
        for d in SKILLS_DIR.iterdir():
            if d.name.lower() == name.lower():
                target = d
                break
    skill_md = target / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8", errors="replace")
        return {"ok": True, "skill": target.name, "content": content}
    return {"ok": False, "error": f"Skill '{name}' not found at {target}"}


def list_plugins() -> List[Dict[str, Any]]:
    plugins = []
    if not PLUGINS_DIR.exists():
        return plugins
    for entry in sorted(PLUGINS_DIR.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            mcp_json = entry / "mcp.json"
            mcp_server = entry / "mcp_server.py"
            plugin_json = entry / ".axim-plugin" / "plugin.json"
            manifest = {}
            if plugin_json.exists():
                try:
                    manifest = json.loads(plugin_json.read_text())
                except Exception:
                    pass
            plugins.append({
                "name": entry.name,
                "has_mcp": mcp_json.exists() or mcp_server.exists(),
                "description": manifest.get("description", f"Axim plugin: {entry.name}"),
                "path": str(entry)
            })
    return plugins


def call_plugin_mcp(plugin_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    target_dir = PLUGINS_DIR / plugin_name
    server_py = target_dir / "mcp_server.py"
    if not server_py.exists():
        return {"ok": False, "error": f"No MCP server found for plugin '{plugin_name}'"}

    call_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }
    try:
        proc = subprocess.Popen(
            [sys.executable, str(server_py)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(target_dir)
        )
        stdout, stderr = proc.communicate(input=json.dumps(call_req) + "\n", timeout=120)
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                resp = json.loads(line)
                if "result" in resp:
                    return resp["result"]
                elif "error" in resp:
                    return {"ok": False, "error": resp["error"]}
            except Exception:
                continue
        return {"ok": False, "error": "No valid JSON-RPC response from plugin MCP", "raw": stdout, "stderr": stderr}
    except Exception as e:
        return {"ok": False, "error": f"Failed to invoke plugin tool: {e}"}


def handle_tool_call(name: str, args: Dict[str, Any]) -> Any:
    if name == "axim_list_skills":
        return list_skills(args.get("filter", ""))
    elif name == "axim_get_skill":
        return get_skill(args.get("skill_name", ""))
    elif name == "axim_list_plugins":
        return list_plugins()
    elif name == "axim_call_plugin_tool":
        return call_plugin_mcp(args.get("plugin", ""), args.get("tool_name", ""), args.get("arguments", {}))
    # Route plugin tools directly if called
    for p in ["bruno", "sql", "task-engine"]:
        if name.startswith(f"{p}_") or name.startswith("sql_") or name.startswith("task_engine_"):
            return call_plugin_mcp(p, name, args)
    return {"error": f"Unknown tool: {name}"}


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
                        "name": "axim-skills-mcp",
                        "version": "1.0.0"
                    }
                })

            elif method == "notifications/initialized":
                pass

            elif method == "tools/list":
                _respond(msg_id, {"tools": CORE_TOOLS})

            elif method == "tools/call":
                params = msg.get("params", {})
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                result_data = handle_tool_call(tool_name, tool_args)
                _respond(msg_id, {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result_data, indent=2, default=str)
                        }
                    ]
                })

            elif method == "ping":
                _respond(msg_id, {})

            else:
                if msg_id is not None:
                    err_resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method '{method}' not found"
                        }
                    }
                    sys.stdout.write(json.dumps(err_resp) + "\n")
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
