#!/usr/bin/env python3
"""MCP stdio server for the Nuuk task_engine in AXIM / Berry.

Drives the compiled task_engine binary to scope PC activity into ML/AI-ready
datasets. Exposes: task_engine_start, task_engine_stop, task_engine_status,
task_engine_read_dataset.
"""

import json
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

PLUGIN_DIR = Path(__file__).parent.resolve()
HOME = Path.home()
AXIM_DATA = HOME / ".axim" / "data"
DEFAULT_OUT = AXIM_DATA / "task_ml_dataset.jsonl"
DEFAULT_CSV = AXIM_DATA / "task_ml_dataset.csv"
STATE_FILE = AXIM_DATA / ".task_engine_state.json"


def _find_binary() -> str:
    cands = [
        PLUGIN_DIR / "target/release" / "task_engine",
        PLUGIN_DIR / "task_engine",
        HOME / ".axim" / "bin" / "task_engine",
    ]
    for c in cands:
        if c.exists():
            return str(c)
    return "task_engine"


def _load_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def _save_state(st: Dict[str, Any]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(st))


def _is_running(pid: Optional[int]) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError, OSError):
        return False


TOOLS = [
    {
        "name": "task_engine_start",
        "description": "Start the Nuuk task_engine to begin scoping workstation activity (window focus, app switches, typing cadence) into ML-ready JSONL/CSV datasets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output": {"type": "string", "description": "Path for JSONL output dataset (default: ~/.axim/data/task_ml_dataset.jsonl)"},
                "csv": {"type": "string", "description": "Optional path for a simultaneous CSV dataset stream"},
                "interval_ms": {"type": "integer", "description": "Hook polling interval in ms (default 500)"}
            },
            "required": []
        }
    },
    {
        "name": "task_engine_stop",
        "description": "Stop the running task_engine and flush buffered ML samples to disk.",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "task_engine_status",
        "description": "Report whether the engine is running, its PID, dataset paths, and captured sample/event counts.",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "task_engine_read_dataset",
        "description": "Read the scoped JSONL (or CSV) dataset produced by the engine for ML/AI training.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Dataset file path (default: the configured JSONL output)"},
                "limit": {"type": "integer", "description": "Max records to return (default 50)"}
            },
            "required": []
        }
    },
]


def _count_lines(path: str) -> int:
    p = Path(path).expanduser()
    if not p.exists():
        return 0
    n = 0
    with open(p, "r", encoding="utf-8") as f:
        for _ in f:
            n += 1
    return n


def _read_last(path: str, limit: int) -> list:
    p = Path(path).expanduser()
    if not p.exists():
        return []
    with open(p, "r", encoding="utf-8") as f:
        lines = [ln for ln in f if ln.strip()]
    out = []
    for ln in lines[-limit:]:
        if path.lower().endswith(".jsonl"):
            try:
                out.append(json.loads(ln))
            except Exception:
                out.append({"_raw": ln.strip()})
        else:
            out.append(ln.strip())
    return out


def handle_tool_call(name: str, args: Dict[str, Any]) -> Any:
    st = _load_state()

    if name == "task_engine_start":
        if st.get("running") and _is_running(st.get("pid")):
            return {"started": False, "reason": "already_running", "pid": st.get("pid")}
        AXIM_DATA.mkdir(parents=True, exist_ok=True)
        out = args.get("output") or str(DEFAULT_OUT)
        csvp = args.get("csv") or str(DEFAULT_CSV)
        interval = int(args.get("interval_ms", 500))
        binary = _find_binary()
        cmd = [binary, "--output", out]
        if csvp:
            cmd += ["--csv", csvp]
        cmd += ["--interval", str(interval)]
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            return {"started": False, "error": f"binary not found: {binary}. Run 'cargo build --release' in the plugin dir first."}
        _save_state({"running": True, "pid": proc.pid, "output": out, "csv": csvp, "interval_ms": interval, "binary": binary})
        return {"started": True, "pid": proc.pid, "output": out, "csv": csvp}

    if name == "task_engine_stop":
        pid = st.get("pid")
        if not (pid and _is_running(pid)):
            _save_state({"running": False, "pid": None})
            return {"stopped": False, "reason": "not_running"}
        try:
            os.kill(pid, signal.SIGINT)
            for _ in range(20):
                if not _is_running(pid):
                    break
                import time
                time.sleep(0.25)
        except Exception as e:
            return {"stopped": False, "error": str(e)}
        try:
            os.kill(pid, signal.SIGKILL)
        except Exception:
            pass
        out = st.get("output")
        csvp = st.get("csv")
        _save_state({"running": False, "pid": None})
        return {
            "stopped": True,
            "output": out,
            "csv": csvp,
            "jsonl_records": _count_lines(out) if out else 0,
            "csv_rows": max(_count_lines(csvp) - 1, 0) if csvp else 0,
        }

    if name == "task_engine_status":
        pid = st.get("pid")
        running = bool(pid and _is_running(pid))
        out = st.get("output") or str(DEFAULT_OUT)
        csvp = st.get("csv")
        info = {
            "running": running,
            "pid": pid if running else None,
            "output_jsonl": out,
            "output_csv": csvp,
            "jsonl_records": _count_lines(out),
        }
        if csvp:
            info["csv_rows"] = max(_count_lines(csvp) - 1, 0)
        return info

    if name == "task_engine_read_dataset":
        path = args.get("path") or st.get("output") or str(DEFAULT_OUT)
        limit = int(args.get("limit", 50))
        records = _read_last(path, limit)
        return {"path": str(Path(path).expanduser()), "returned": len(records), "records": records}

    return {"error": f"Unknown tool: {name}"}


def _respond(msg_id: Any, result: Any) -> None:
    resp = {"jsonrpc": "2.0", "id": msg_id, "result": result}
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()


def main() -> None:
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = msg.get("method")
        msg_id = msg.get("id")

        if method == "initialize":
            _respond(msg_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "task-engine-mcp", "version": "1.0.0"},
            })
        elif method == "notifications/initialized":
            pass
        elif method == "tools/list":
            _respond(msg_id, {"tools": TOOLS})
        elif method == "tools/call":
            params = msg.get("params", {})
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            data = handle_tool_call(tool_name, tool_args)
            _respond(msg_id, {"content": [{"type": "text", "text": json.dumps(data, indent=2, default=str)}]})
        else:
            if msg_id is not None:
                _respond(msg_id, {"_note": f"unhandled method: {method}"})


if __name__ == "__main__":
    main()
