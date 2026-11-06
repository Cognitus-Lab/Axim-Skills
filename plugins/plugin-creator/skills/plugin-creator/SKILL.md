---
name: plugin-creator
description: Create AXIM / Berry plugins — bundles of skills, tools, MCP servers, and agents.
keywords:
  - create plugin
  - new plugin
  - make plugin
  - build plugin
  - plugin template
  - add plugin
  - write plugin
---

# AXIM / Berry Plugin Creator

Create installable AXIM plugins that bundle skills (`skills/<name>/SKILL.md`), Python tool extensions (`tools.py`), and MCP server configurations (`mcp.json`).

## Plugin Structure

```
my-plugin/
  .axim-plugin/
    plugin.json       ← Required: manifest
  skills/             ← Optional: plugin-specific skills
    my-skill/
      SKILL.md
  tools.py            ← Optional: exposes register_tools(tool_registry)
  mcp.json            ← Optional: MCP server configuration
  README.md           ← Recommended: documentation
```

## plugin.json (Manifest)

```json
{
  "name": "my-plugin",
  "description": "What this plugin does",
  "version": "1.0.0",
  "author": "Cognitus",
  "license": "MIT",
  "repository": "https://github.com/Cognitus-Lab/Axim-Skills",
  "capabilities": {
    "skills": true,
    "tools": false,
    "mcp": false
  }
}
```

## Installing & Exporting

1. Create `.axim-plugin/plugin.json` and `skills/<name>/SKILL.md` using `file_write`.
2. Install into the active plugin store (`~/.axim/plugins/installed/`) using `skill_import`:
   ```json
   {"name": "skill_import", "arguments": {"source_path": "my-plugin"}}
   ```
3. Export into `Cognitus-Lab/Axim-Skills` (`plugins/<name>`) using `skill_export`:
   ```json
   {"name": "skill_export", "arguments": {"name_or_path": "my-plugin"}}
   ```
