#!/bin/bash
# ⚡ task_engine macOS Double-Clickable Launcher
# Double-click this file from Finder on ANY Mac (Intel or Apple Silicon)

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

chmod +x "$DIR/task_engine" "$DIR/task_engine_macos" 2>/dev/null

echo "================================================================================"
echo "⚡ Starting task_engine from flash drive..."
echo "📂 Working Directory: $DIR"
echo "================================================================================"

"$DIR/task_engine" "$@"
