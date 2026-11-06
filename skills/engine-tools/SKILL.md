---
name: engine-tools
description: AXIM / Berry Engine tools — manage subagents, workspace attachments, governance, skills, and tool schemas at runtime.
keywords:
  - list agents
  - show agents
  - registered agents
  - agent registry
  - engine status
  - multi-agent
  - parallel agent
  - subagents
---

# AXIM / Berry Engine Tools

Interact with the Berry / AXIM autonomous execution engine using native tools:

## 1. Parallel Sub-Agents (`run_subagents`)
Run up to two independent read-only investigations concurrently without spawning child models:
```json
{
  "name": "run_subagents",
  "arguments": {
    "tasks": [
      {"name": "Source", "task": "Inspect implementation files"},
      {"name": "Tests", "task": "Inspect test suite"}
    ]
  }
}
```

## 2. Workspace Attachment, Import, and Export
- `attach_folder`: `{"name": "attach_folder", "arguments": {"path": "/path/to/folder"}}`
- `import_folder`: `{"name": "import_folder", "arguments": {"source_path": "/path/to/src", "target_folder": "/path/to/dst"}}`
- `export_folder`: `{"name": "export_folder", "arguments": {"source_or_target": "/path/to/dst"}}`

## 3. Plugin & Skill Management
- `plugin_list`: `{"name": "plugin_list", "arguments": {}}`
- `skill_search`: `{"name": "skill_search", "arguments": {"query": "sql"}}`
- `skill_install`: `{"name": "skill_install", "arguments": {"target": "all"}}`
- `skill_use`: `{"name": "skill_use", "arguments": {"name": "opencode-reasoning"}}`
- `skill_import`: `{"name": "skill_import", "arguments": {"source_path": "/path/to/skill"}}`
- `skill_export`: `{"name": "skill_export", "arguments": {"name_or_path": "all"}}`
