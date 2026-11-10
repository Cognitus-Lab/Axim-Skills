# Task Engine (Nuuk Engine)

Portable workstation task & activity telemetry plugin for AXIM / Berry agents. Wraps **Nuuk Engine** (`task_engine`) — a zero-dependency Rust binary that passively scopes what you do on your PC into clean, ML/AI-ready datasets.

## What It Does

`task-engine` captures real workstation activity — active window titles, application switches, typing cadence, and focus/idle transitions — on macOS, Windows, or Linux. It runs in the background with minimal overhead (~362 KB binary, <5 MB RAM) and streams every captured session through a Unified Data Funnel into:

- `task_ml_dataset.jsonl` — structured records with `metadata`, `session`, and `ml_sample` (features + labels)
- optional dual CSV stream for spreadsheet / tabular tooling

Agents use it to **scope data from a user's PC** and train personal ML/AI models (productivity scoring, focus prediction, task-completion likelihood).

## MCP Tools

| Tool | Purpose |
|------|---------|
| `task_engine_start` | Launch the engine in the background to begin scoping PC activity |
| `task_engine_status` | Check if running, PID, dataset paths, and record counts |
| `task_engine_read_dataset` | Read back the scoped JSONL/CSV for training or inspection |
| `task_engine_stop` | Gracefully stop the engine and flush buffered samples to disk |

## Build & Run

The MCP server drives the compiled `task_engine` binary. If no binary is present, build it from the bundled source:

```bash
cargo build --release
```

The release binary lands at `target/release/task_engine`, which the server auto-discovers. Datasets are written to `~/.axim/data/` by default and are gitignored so raw data never enters the repo.

## Pipeline into Training

For large scoped datasets, feed them into the companion `sql` plugin (`sql_import_dataset`) to build a queryable SQLite table, then train against it — or load the JSONL directly into PyTorch (see `skills/task-engine/SKILL.md` for the full workflow).

## Privacy

Captures app names and activity metadata only — never keystroke content or screen pixels. Confirm the user is comfortable before starting a capture session.
