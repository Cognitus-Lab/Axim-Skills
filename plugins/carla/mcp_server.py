#!/usr/bin/env python3
"""
mcp_server.py — CARLA plugin MCP bridge for Axim-Skills.

The root Axim-Skills aggregator (mcp_server.py) only auto-launches Python MCP
servers. CARLA's agentic-tools server is Node.js (Util/AgenticTools in the
carla-simulator/carla repo), so this bridge:

  * spawns the upstream Node server over stdio,
  * proxies initialize / tools/list / tools/call / ping JSON-RPC frames to it,
  * exposes the CARLA skill catalog as axim_carla_* tools so any MCP client can
    discover and read the 69 vetted skills without a Node runtime of its own.

Upstream CARLA server tools (proxied, namespaced with carla_):
  list_skills, read_skill, check_prerequisites, get_config, set_config
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PLUGIN_ROOT = Path(__file__).resolve().parent
# Default: plugins/carla -> plugins -> axim-skills, so carla-src is a SIBLING of
# the axim-skills repo (one level above it). Users with a non-standard CARLA
# location can override this with the CARLA_SRC env var (absolute or $HOME-relative).
def _resolve_carla_src() -> Path:
    override = os.environ.get("CARLA_SRC", "").strip()
    if override:
        p = Path(override)
        if not p.is_absolute():
            p = Path.home() / override
        return p.resolve()
    repo_root = PLUGIN_ROOT.parent.parent.parent.resolve()
    return repo_root / "carla-src"

CARLA_SRC = _resolve_carla_src()
AGENTIC_TOOLS = CARLA_SRC / "Util" / "AgenticTools"
CARLA_SKILLS = CARLA_SRC / "Skills"

# Node may live outside the inherited PATH (e.g. Homebrew on Apple Silicon).
# Probe common locations so the upstream server is found regardless of env.
def _find_node() -> Optional[str]:
    found = shutil.which("node")
    if found:
        return found
    for cand in (
        "/opt/homebrew/bin/node",
        "/usr/local/bin/node",
        "/opt/local/bin/node",
    ):
        if Path(cand).exists():
            return cand
    return None

NODE_BIN = _find_node()
# Ensure the upstream Node process can resolve its own runtime + deps.
_NODE_DIR = str(Path(NODE_BIN).parent) if NODE_BIN else None
UPSTREAM_CMD = [NODE_BIN, str(AGENTIC_TOOLS / "bin" / "carla-agentic-tools.js")] if NODE_BIN else None
UPSTREAM_CWD = str(AGENTIC_TOOLS)
UPSTREAM_ENV = {
    **os.environ,
    "PATH": (_NODE_DIR + os.pathsep + os.environ.get("PATH", "/usr/bin:/bin")) if _NODE_DIR else os.environ.get("PATH", ""),
}

# Upstream Node server tool names -> bridged (namespaced) names.
UPSTREAM_TOOLS = [
    "list_skills",
    "read_skill",
    "check_prerequisites",
    "get_config",
    "set_config",
]


def _node_available() -> bool:
    return NODE_BIN is not None and AGENTIC_TOOLS.exists()


def _skill_summary(skill_md: Path) -> str:
    try:
        for line in skill_md.read_text(encoding="utf-8", errors="replace").splitlines()[:20]:
            if line.startswith("# "):
                return line[2:].strip()
            if line.lower().startswith("description:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return ""


def carla_list_skills() -> Dict[str, Any]:
    if not CARLA_SKILLS.exists():
        return {"ok": False, "error": f"CARLA skills dir not found at {CARLA_SKILLS}"}
    skills = []
    for sub in sorted(CARLA_SKILLS.iterdir()):
        if not sub.is_dir() or sub.name.startswith("."):
            continue
        for skill_md in sorted(sub.glob("*/SKILL.md")):
            skills.append({
                "name": skill_md.parent.name,
                "subsystem": sub.name,
                "summary": _skill_summary(skill_md) or skill_md.parent.name,
                "path": str(skill_md),
            })
    return {"ok": True, "count": len(skills), "skills": skills}


def carla_read_skill(name: str) -> Dict[str, Any]:
    if not CARLA_SKILLS.exists():
        return {"ok": False, "error": f"CARLA skills dir not found at {CARLA_SKILLS}"}
    matches = list(CARLA_SKILLS.glob(f"*/{name}/SKILL.md"))
    if not matches:
        # case-insensitive fallback
        low = name.lower()
        matches = [m for m in CARLA_SKILLS.glob("*/SKILL.md") if m.parent.name.lower() == low]
    if not matches:
        return {"ok": False, "error": f"CARLA skill '{name}' not found"}
    skill_md = matches[0]
    return {
        "ok": True,
        "skill": skill_md.parent.name,
        "subsystem": skill_md.parent.parent.name,
        "content": skill_md.read_text(encoding="utf-8", errors="replace"),
    }


class Upstream:
    """Lazily-spawned proxy to the CARLA Node MCP server over stdio."""

    def __init__(self) -> None:
        self._proc: Optional[subprocess.Popen] = None
        self._id = 0

    def available(self) -> bool:
        return _node_available()

    def _ensure(self) -> Optional[subprocess.Popen]:
        if not self.available():
            return None
        if self._proc is None or self._proc.poll() is not None:
            try:
                self._proc = subprocess.Popen(
                    UPSTREAM_CMD,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=UPSTREAM_CWD,
                    env=UPSTREAM_ENV,
                )
            except Exception:
                self._proc = None
        return self._proc

    def _next_id(self) -> int:
        self._id += 1
        return self._id

    def _roundtrip(self, method: str, params: Dict[str, Any]) -> Any:
        proc = self._ensure()
        if proc is None or proc.stdin is None or proc.stdout is None:
            return {"ok": False, "error": "Node runtime or CARLA agentic-tools server unavailable"}
        req_id = self._next_id()
        frame = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
        try:
            proc.stdin.write(json.dumps(frame) + "\n")
            proc.stdin.flush()
        except Exception as e:
            return {"ok": False, "error": f"Failed to send frame to upstream: {e}"}
        try:
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    resp = json.loads(line)
                except Exception:
                    continue
                if resp.get("id") == req_id:
                    if "result" in resp:
                        return resp["result"]
                    if "error" in resp:
                        err = resp["error"]
                        return {"ok": False, "error": err.get("message", str(err))}
        except Exception as e:
            return {"ok": False, "error": f"Upstream read error: {e}"}
        return {"ok": False, "error": "No matching JSON-RPC response from upstream"}

    def call(self, tool: str, arguments: Dict[str, Any]) -> Any:
        return self._roundtrip("tools/call", {"name": tool, "arguments": arguments or {}})


UPSTREAM = Upstream()


def build_tools() -> List[Dict[str, Any]]:
    tools: List[Dict[str, Any]] = [
        {
            "name": "carla_list_skills",
            "description": "List all vetted CARLA skills across subsystems (python-api, ros2, scenic, leaderboard, scenario-runner, docs, setup, ue4/ue5/ue58).",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "carla_read_skill",
            "description": "Read the full SKILL.md for a specific CARLA skill by name.",
            "inputSchema": {
                "type": "object",
                "properties": {"skill_name": {"type": "string"}},
                "required": ["skill_name"],
            },
        },
    ]
    # Native tools win; skip any upstream tool that would collide with a name
    # already registered above (e.g. carla_list_skills / carla_read_skill).
    native_names = {t["name"] for t in tools}
    if UPSTREAM.available():
        for t in UPSTREAM_TOOLS:
            name = f"carla_{t}"
            if name in native_names:
                continue
            tools.append({
                "name": name,
                "description": f"CARLA agentic tool: {t} (proxied to the upstream Node MCP server).",
                "inputSchema": {"type": "object", "properties": {}, "required": []},
            })
    return tools


def handle_call(name: str, arguments: Dict[str, Any]) -> Any:
    if name == "carla_list_skills":
        return carla_list_skills()
    if name == "carla_read_skill":
        return carla_read_skill((arguments or {}).get("skill_name", ""))
    # Everything else is proxied to the upstream Node server.
    if name.startswith("carla_"):
        return UPSTREAM.call(name[len("carla_"):], arguments or {})
    return {"ok": False, "error": f"Unknown tool: {name}"}


def _serve() -> None:
    tools = build_tools()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        method = req.get("method")
        rid = req.get("id")
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "carla-bridge", "version": "1.0"},
            }
        elif method == "tools/list":
            result = {"tools": tools}
        elif method == "tools/call":
            params = req.get("params") or {}
            result = handle_call(params.get("name", ""), params.get("arguments") or {})
        elif method == "ping":
            result = {}
        else:
            if rid is not None:
                sys.stdout.write(json.dumps({
                    "jsonrpc": "2.0", "id": rid,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }) + "\n")
                sys.stdout.flush()
            continue
        if rid is not None:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": rid, "result": result}) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    _serve()
