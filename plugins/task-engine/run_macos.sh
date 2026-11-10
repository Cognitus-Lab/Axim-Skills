#!/usr/bin/env bash
# ⚡ task_engine macOS Terminal Runner
# Run from terminal on any Mac: ./run_macos.sh [-o dataset.jsonl] [--csv dataset.csv]

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

chmod +x "$DIR/task_engine" "$DIR/task_engine_macos" 2>/dev/null
exec "$DIR/task_engine" "$@"
