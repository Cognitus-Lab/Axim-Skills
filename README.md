# AXIM Plugins

> Official plugin repository for [AXIM](https://cognitus.grrn.io) — the dual-model AI agent desktop application.

GRRN PROPRIETARY LICENSE
AXIM Software and Associated Materials
Version 1.0 — August 6, 2026

Copyright © 2026 GRRN. All Rights Reserved.


---

## What Are AXIM Plugins?

AXIM plugins are installable bundles that extend the agent's capabilities with:

- **Skills** — Knowledge modules injected into the agent's context when keywords match
- **MCP Servers** — Model Context Protocol integrations for external tool access
- **Agents** — Custom agent definitions for multi-agent workflows
- **Scripts** — Executable automation scripts

Plugins are installed to `~/.axim/plugins/installed/` on the user's machine and loaded automatically on startup.

---

## Available Plugins

| Plugin | Description | Skills | MCP | Agents |
|--------|-------------|--------|-----|--------|
| [`skill-creator`](plugins/skill-creator/) | Create new AXIM skills with proper SKILL.md format | ✅ | — | — |
| [`skill-installer`](plugins/skill-installer/) | Install, uninstall, and manage AXIM skills | ✅ | — | — |
| [`plugin-creator`](plugins/plugin-creator/) | Create new AXIM plugins with manifest and structure | ✅ | — | — |
| [`axim-engine`](plugins/axim-engine/) | Engine tools — agents, callbacks, sessions, events, schemas | ✅ | — | — |
| [`openmath-reasoning`](plugins/openmath-reasoning/) | Structured mathematical derivation, executable checks, and answer verification | ✅ | — | — |
| [`opencode-reasoning`](plugins/opencode-reasoning/) | Specification-driven code generation, execution validation, critique, and repair | ✅ | — | — |
| [`engineering-skill-library`](plugins/engineering-skill-library/) | Safe discovery, review, import, and Claude-compatible skill package integration | ✅ | — | — |
| [`scientific-research-mode`](plugins/scientific-research-mode/) | Evidence-gated scientific research sessions from question through publication | ✅ | — | — |

---

## Installation

### From the AXIM App

```js
// In the AXIM console or via the agent
window.axim.pluginsInstall('/path/to/plugin-directory')
```

### From This Repository

```bash
# Clone the repo
git clone https://github.com/GRRN-MAKER/Axim-plugins.git

# Install a specific plugin
# (from within AXIM or programmatically)
window.axim.pluginsInstall('/path/to/Axim-plugins/plugins/skill-creator')
```

### Verify Installation

```js
// List installed plugins
window.axim.pluginsList()

// Reload after manual changes
window.axim.pluginsReload()
```

---

## Plugin Structure

Every plugin follows this structure:

```
my-plugin/
  .axim-plugin/
    plugin.json          ← Required: manifest
  skills/                ← Optional: knowledge modules
    my-skill/
      SKILL.md           ← Skill definition (frontmatter + instructions)
  mcp.json               ← Optional: MCP server configuration
  agents/                ← Optional: custom agent definitions
    agent.json
  scripts/               ← Optional: executable scripts
  assets/                ← Optional: static resources
  README.md              ← Recommended: documentation
```

### plugin.json (Manifest)

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "What this plugin does",
  "author": "Your Name",
  "license": "MIT",
  "repository": "https://github.com/GRRN-MAKER/Axim-plugins",
  "axim": {
    "minVersion": "1.0.0"
  },
  "capabilities": {
    "skills": true,
    "mcp": false,
    "agents": false,
    "scripts": false
  }
}
```

### SKILL.md Format

Skills use YAML frontmatter for metadata and Markdown for instructions:

```markdown
---
name: my-skill
description: One-line description of what this skill does.
keywords:
  - keyword1
  - keyword2
  - related phrase
---

# Skill Title

Instructions for the agent when this skill is activated.
```

**Key rules:**
- `name`: lowercase, hyphenated
- `description`: One sentence — shown in listings
- `keywords`: 3–10 phrases that trigger this skill (matched against user messages)
- Body: Actionable guidance the agent can follow

---

## Creating Your Own Plugin

1. Create a directory with the structure above
2. Write a `plugin.json` manifest
3. Add skills, MCP configs, agents, or scripts as needed
4. Test locally: `window.axim.pluginsInstall('/path/to/your-plugin')`
5. Submit a PR to this repository

Or use the **skill-creator** and **plugin-creator** plugins — they guide the agent through the process automatically.

---

## Documentation & Resources

For detailed guidance on using, developing, and securing AXIM plugins, see:

- **[User Guide](USER_GUIDE.md)** — Installation, usage, and troubleshooting
- **[Update Schedule](UPDATE_SCHEDULE.md)** — Maintenance cadence for integrations and dependencies
- **[Security Policy](SECURITY.md)** — Security audit procedures and sensitive data handling

---

## Architecture

### How Plugins Load

1. On startup, AXIM scans `~/.axim/plugins/installed/`
2. Each directory with a `.axim-plugin/plugin.json` manifest is loaded
3. Skills from `plugins/<name>/skills/` are indexed by the SkillLoader
4. MCP configs from `plugins/<name>/mcp.json` are available via `pluginsGetMcp()`
5. Plugin metadata is exposed via `window.axim.pluginsList()`

### How Skills Match

When a user sends a message:

1. The SkillLoader scans all loaded skills (system + user + plugin)
2. Each skill's `keywords` array is checked against the message (score +5 per match)
3. Skill name matches score +10, description word matches score +1
4. Top 2 matching skills are injected into the system prompt
5. The agent receives the skill instructions as `== Active Skills ==` context

### How the Engine Works

AXIM's engine provides 6 core systems:

| System | Module | Purpose |
|--------|--------|---------|
| **Events** | `engine/events.js` | Typed event bus with pub/sub, history, and audit trail |
| **Callbacks** | `engine/callbacks.js` | 6 lifecycle hooks (before/after agent, model, tool) |
| **Sessions** | `engine/session.js` | Pluggable session storage with scoped state (app:/user:/temp:) |
| **Runner** | `engine/runner.js` | Execution engine decoupled from UI |
| **Agents** | `engine/agents.js` | Multi-agent framework (Sequential, Parallel, Loop, AgentTool) |
| **Schema** | `engine/schema.js` | JSON Schema validation for 27+ tools |

---

## API Reference

### Plugin Manager (`window.axim.*`)

| Method | Description |
|--------|-------------|
| `pluginsList()` | List all installed plugins |
| `pluginsInstall(sourcePath)` | Install a plugin from a local directory |
| `pluginsUninstall(name)` | Uninstall a plugin by name |
| `pluginsReload()` | Reload all plugins from disk |
| `pluginsGetMcp(name)` | Get MCP server config for a plugin |

### Skill Manager (`window.axim.*`)

| Method | Description |
|--------|-------------|
| `skillsList()` | List all loaded skills (system + user + plugin) |
| `skillsMatch(message)` | Find skills matching a user message |
| `skillsInstall(sourcePath)` | Install a skill from a local directory |
| `skillsUninstall(name)` | Uninstall a user skill (system skills protected) |
| `skillsReload()` | Reload all skills from disk |

### Engine (`window.axim.*`)

| Method | Description |
|--------|-------------|
| `engineListAgents()` | List all registered agents |
| `engineListCallbacks()` | List all registered callback hooks |
| `engineListSchemas()` | List all tool schemas |
| `engineDescribeSchema(tool)` | Get human-readable schema for a tool |
| `engineGetEventHistory(type, limit)` | Get recent events from the event bus |
| `engineSessionCreate(userId, sessionId)` | Create a new session |
| `engineSessionGet(sessionId)` | Load a session |
| `engineSessionList(userId)` | List all sessions |
| `engineSessionDelete(sessionId)` | Delete a session |
| `onEngineEvent(callback)` | Subscribe to all engine events |

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

Built with 🖤 by [GRRN](https://grrn.io)
