#!/usr/bin/env python3
"""
mcp_server.py - Model Context Protocol (MCP) stdio server for the team's
Bruno-based CLI in AXIM / Berry.

Lets an agent run, test, and automate HTTP/REST/GraphQL/gRPC/WebSocket API
endpoints in bulk by wrapping the `bru` CLI. The CLI is provisioned on demand:
first from the team's own local source checkout, then from the internal mirror
as a fallback. Each user's install lives in their own home cache dir, so multiple
users can invoke the skill concurrently without colliding.

Tools exposed:
- bruno_ensure_cli: provision / verify the bru CLI on this machine
- bruno_run: run one or more requests/folders in a collection
- bruno_import: import an OpenAPI/cURL spec into a collection
- bruno_docs: generate standalone HTML API documentation from a collection
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Provisioning sources, in priority order. Override via env vars to point at
# your own infrastructure; defaults target the team's local checkout and mirror.
CLI_CACHE_DIR = Path(os.environ.get("BRUNO_CLI_DIR", str(Path.home() / ".axim" / "bruno-cli")))
CLI_NAME = os.environ.get("BRUNO_CLI_NAME", "bru")
LOCAL_SRC_DIR = Path(os.environ.get("BRUNO_LOCAL_SRC", str(Path.home() / "bruno")))
MIRROR_REPO = os.environ.get("BRUNO_MIRROR_REPO", "https://git.grrn.io/axim-agent/bruno.git")
CLI_TIMEOUT = int(os.environ.get("BRUNO_CLI_TIMEOUT", "900"))

TOOLS = [
    {"name": "bruno_ensure_cli",
     "description": "Provision or verify the bru CLI on this machine. Idempotent; builds from the local source checkout or pulls from the internal mirror.",
     "inputSchema": {"type": "object", "properties": {"force_reinstall": {"type": "boolean", "default": False}}, "required": []}},
    {"name": "bruno_run",
     "description": "Run one or more requests or folders in a collection and return results.",
     "inputSchema": {"type": "object", "properties": {"collection_path": {"type": "string"}, "targets": {"type": "array", "items": {"type": "string"}}, "environment": {"type": "string"}, "output": {"type": "string", "default": "console"}}, "required": ["collection_path"]}},
    {"name": "bruno_import",
     "description": "Import an OpenAPI or cURL spec into a collection.",
     "inputSchema": {"type": "object", "properties": {"source_path": {"type": "string"}, "format": {"type": "string", "enum": ["openapi", "curl"]}, "collection_path": {"type": "string"}}, "required": ["source_path", "collection_path"]}},
    {"name": "bruno_docs",
     "description": "Generate standalone HTML API documentation from a collection.",
     "inputSchema": {"type": "object", "properties": {"collection_path": {"type": "string"}, "output_path": {"type": "string"}}, "required": ["collection_path"]}},
]

def _run(cmd, timeout=CLI_TIMEOUT):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", f"command timed out after {timeout}s"
    except FileNotFoundError as e:
        return -1, "", str(e)


def _cli_path():
    return CLI_CACHE_DIR / "node_modules" / ".bin" / CLI_NAME


def _cli_installed():
    p = _cli_path()
    return p.exists() and _run([str(p), "--version"], timeout=60)[0] == 0

def _provision_local():
    src = LOCAL_SRC_DIR
    if not (src / "package.json").exists():
        return False, f"local source checkout not found at {src}"
    CLI_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    rc, out, err = _run(["npm", "install", "--prefix", str(CLI_CACHE_DIR), str(src)])
    if rc == 0 and _cli_installed():
        return True, f"built CLI from local checkout {src}"
    return False, f"local build failed: {err or out}"

def _provision_mirror():
    if not MIRROR_REPO:
        return False, "no internal mirror configured (set BRUNO_MIRROR_REPO)"
    CLI_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    dest = CLI_CACHE_DIR / "src"
    if not (dest / ".git").exists():
        rc, out, err = _run(["git", "clone", MIRROR_REPO, str(dest)])
        if rc != 0:
            return False, f"mirror clone failed: {err or out}"
    rc, out, err = _run(["npm", "install", "--prefix", str(CLI_CACHE_DIR), str(dest)])
    if rc == 0 and _cli_installed():
        return True, f"built CLI from internal mirror {MIRROR_REPO}"
    return False, f"mirror build failed: {err or out}"

def ensure_cli(force_reinstall=False):
    if _cli_installed() and not force_reinstall:
        return {"ok": True, "status": "already_installed", "path": str(_cli_path())}
    if force_reinstall:
        shutil.rmtree(CLI_CACHE_DIR, ignore_errors=True)
        CLI_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ok, msg = _provision_local()
    if not ok:
        ok, msg2 = _provision_mirror()
        if ok:
            return {"ok": True, "status": "installed_from_mirror", "path": str(_cli_path()), "note": msg2}
        return {"ok": False, "error": f"local: {msg}; mirror: {msg2}"}
    return {"ok": True, "status": "installed_from_local", "path": str(_cli_path()), "note": msg}

def tool_bruno_ensure_cli(args):
    return ensure_cli(bool(args.get("force_reinstall", False)))


def _collection_arg(args):
    return args.get("collection_path", "")


def tool_bruno_run(args):
    cp = _collection_arg(args)
    if not cp:
        return {"ok": False, "error": "collection_path is required"}
    if not _cli_installed():
        return {"ok": False, "error": "CLI not installed; call bruno_ensure_cli first"}
    cmd = [str(_cli_path()), "run", cp]
    for t in args.get("targets", []):
        cmd += ["--request", t]
    if args.get("environment"):
        cmd += ["--environment", args["environment"]]
    if args.get("output"):
        cmd += ["--format", args["output"]]
    rc, out, err = _run(cmd)
    return {"ok": rc == 0, "returncode": rc, "stdout": out, "stderr": err}

def tool_bruno_import(args):
    src = args.get("source_path", "")
    cp = _collection_arg(args)
    fmt = args.get("format", "openapi")
    if not src or not cp:
        return {"ok": False, "error": "source_path and collection_path are required"}
    if not _cli_installed():
        return {"ok": False, "error": "CLI not installed; call bruno_ensure_cli first"}
    cmd = [str(_cli_path()), "import", src, "--format", fmt, cp]
    rc, out, err = _run(cmd)
    return {"ok": rc == 0, "returncode": rc, "stdout": out, "stderr": err}


def tool_bruno_docs(args):
    cp = _collection_arg(args)
    if not cp:
        return {"ok": False, "error": "collection_path is required"}
    if not _cli_installed():
        return {"ok": False, "error": "CLI not installed; call bruno_ensure_cli first"}
    cmd = [str(_cli_path()), "docs", cp]
    if args.get("output_path"):
        cmd += ["--output", args["output_path"]]
    rc, out, err = _run(cmd)
    return {"ok": rc == 0, "returncode": rc, "stdout": out, "stderr": err}


def handle_tool_call(name: str, args: dict) -> dict:
    if name == "bruno_ensure_cli":
        return tool_bruno_ensure_cli(args)
    elif name == "bruno_run":
        return tool_bruno_run(args)
    elif name == "bruno_import":
        return tool_bruno_import(args)
    elif name == "bruno_docs":
        return tool_bruno_docs(args)
    else:
        return {"ok": False, "error": f"Unknown tool: {name}"}


def _respond(msg_id, result):
    resp = {"jsonrpc": "2.0", "id": msg_id, "result": result}
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()


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
                _respond(msg_id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "bruno-mcp",
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

