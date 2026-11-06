---
name: skill-installer
description: Install, import, export, and manage AXIM / Berry skills and plugins from local paths or Cognitus-Lab/Axim-Skills.
keywords:
  - install skill
  - install all skills
  - uninstall skill
  - remove skill
  - list skills
  - manage skills
  - skill manager
  - show skills
---

# AXIM / Berry Skill Installer

Use the native Berry / AXIM skill and plugin tools to list, install, import, activate, or export skills.

## Native Agent Tools

### 1. Install all skills (or a specific skill/plugin)
```json
{"name": "skill_install", "arguments": {"target": "all"}}
```

### 2. List installed plugins and skills
```json
{"name": "plugin_list", "arguments": {}}
```

### 3. Search skills by keyword
```json
{"name": "skill_search", "arguments": {"query": "sql"}}
```

### 4. Activate / read a skill's instructions
```json
{"name": "skill_use", "arguments": {"name": "sql"}}
```

### 5. Import a skill or plugin from a local directory or SKILL.md
```json
{"name": "skill_import", "arguments": {"source_path": "/path/to/skill-directory"}}
```

### 6. Export skills or plugins into Cognitus-Lab/Axim-Skills
```json
{"name": "skill_export", "arguments": {"name_or_path": "all"}}
```

## Interactive Slash Commands
- `/skills` or `/skills list` — List all loaded skills
- `/skills use <name>` — Pin and activate a skill
- `/skills install [all|<path>]` — Install all or specific skills
- `/skills import <path>` — Import a skill or plugin directory
- `/skills export [name_or_path]` — Export skills to the GitHub skills repo
- `/plugins` — List, use, install, import, or export plugins
