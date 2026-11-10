---
name: task-engine
description: Scope real workstation usage (active apps, typing cadence, focus/idle, app switches) into streamable ML/AI-ready JSONL and CSV datasets using the Nuuk task_engine, for training personal productivity and behavior models.
keywords:
  - task-engine
  - nuuk engine
  - task engine
  - activity telemetry
  - scope pc data
  - ml dataset
  - ai training data
  - usage tracking
  - focus tracking
  - app usage
  - typing cadence
  - jsonl dataset
  - csv dataset
  - personal ml
---

# Task Engine (Nuuk Engine)

The `task-engine` plugin wraps **Nuuk Engine** (`task_engine`), an ultra-lightweight, zero-dependency Rust binary that passively captures what you do on your PC — active window titles, application switches, typing cadence, and focus/idle transitions — and converts it into clean, machine-learning-ready datasets.

Use it to **scope data from your workstation** and train your own ML/AI models (productivity scoring, focus prediction, task-completion likelihood, behavior sequences).

---

## When to Use This Skill

Reach for `task-engine` when the user wants to:
- Collect real usage/activity data from their PC for ML/AI training.
- Build a personal dataset of app usage, focus patterns, or typing behavior.
- Feed a JSONL/CSV telemetry dataset into a training pipeline (PyTorch, MLP, etc.).
- Analyze their own work habits from scoped telemetry.

---

## Capabilities

1. **Scope PC Activity** (`task_engine_start`): Launch the engine in the background to begin capturing raw OS events (active app, clicks, typing, focus/idle) on macOS, Windows, or Linux.
2. **Inspect Capture** (`task_engine_status`): Check whether the engine is running, how many raw events and ML samples have been collected, and the current active app.
3. **Read Datasets** (`task_engine_read_dataset`): Read back the scoped JSONL or CSV dataset so it can be loaded into a training pipeline.
4. **Stop Capture** (`task_engine_stop`): Gracefully stop the engine and flush all buffered samples to disk.
5. **Pipeline into SQL** (`sql_import_dataset`): Feed the resulting JSONL/CSV straight into the `sql` plugin to build a queryable SQLite table for analysis or training.

---

## Tool Reference & Invocation

### 1. `task_engine_start`
Begin background capture of workstation activity.
```json
{
  "name": "task_engine_start",
  "arguments": {
    "output_jsonl": "~/.axim/data/tasks_ml_dataset.jsonl",
    "output_csv": "~/.axim/data/tasks_ml_dataset.csv",
    "interval_ms": 500
  }
}
```

### 2. `task_engine_status`
Report engine health and collection progress.
```json
{
  "name": "task_engine_status",
  "arguments": {}
}
```

### 3. `task_engine_read_dataset`
Read the scoped dataset (last N records) for training or inspection.
```json
{
  "name": "task_engine_read_dataset",
  "arguments": {
    "format": "jsonl",
    "limit": 100
  }
}
```

### 4. `task_engine_stop`
Gracefully stop and flush.
```json
{
  "name": "task_engine_stop",
  "arguments": {}
}
```

---

## Dataset Schema

Each JSONL record contains:
- `metadata`: version, timestamp, platform, engine_version, arch
- `session`: session_id, duration_secs, current_app, focused_time, idle_time, switches, typing_speed, total_clicks
- `ml_sample`: 
  - `features`: hour_of_day, day_of_week, time_since_last_switch, session_duration, typing_speed, apps_in_rotation, focus_entropy, idle_ratio, app_categories (one-hot), time_of_day_bin, is_work_hours, switch_frequency, click_rate
  - `labels`: next_action, productivity_score, task_completion_probability

---

## Typical Workflow: Scope Data → Train ML/AI

1. **Start** capture and let it run while the user works:
   `task_engine_start` with a chosen output path.
2. **Monitor** with `task_engine_status` until enough samples are collected.
3. **Stop** to flush: `task_engine_stop`.
4. **Ingest** into a queryable store for training:
   `sql_import_dataset` with `file_path` = the JSONL/CSV and a table name.
5. **Train** using the SQL dataset or load the JSONL directly into PyTorch (see README for a `TaskDataset` example).

---

## Best Practices
- **Privacy first**: This captures app names and activity, not keystroke content or screen pixels. Confirm the user is comfortable before starting.
- **Run long enough**: Meaningful ML samples need real usage over time; check `task_engine_status` for sample counts before training.
- **Keep datasets out of git**: JSONL/CSV outputs are gitignored; store them in `~/.axim/data/` or a local data dir.
- **Feed the SQL plugin**: For large datasets, import into SQLite and query/aggregate there rather than loading raw files.
