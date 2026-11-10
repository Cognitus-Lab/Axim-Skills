#!/usr/bin/env bash
# ============================================================================
# ⚡ task_engine Linux Launcher
# Run on any Linux PC from flash drive
# ============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ -f "$DIR/task_engine_linux" ]; then
    chmod +x "$DIR/task_engine_linux"
    exec "$DIR/task_engine_linux" "$@"
fi

if command -v cargo >/dev/null 2>&1; then
    echo "[task_engine] Running via Cargo using offline vendored crates..."
    exec cargo run --release -- "$@"
fi

echo "[ERROR] Neither task_engine_linux nor cargo found."
exit 1
