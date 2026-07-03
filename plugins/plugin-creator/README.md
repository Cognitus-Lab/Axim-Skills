# plugin-creator

> Create AXIM plugins — bundles of skills, tools, MCP servers, and agents.

## Overview

The **plugin-creator** plugin teaches the AXIM agent how to scaffold and create new plugins. When a user asks to "create a plugin" or "build a plugin", the agent receives full instructions on the plugin directory structure, manifest format, MCP configuration, and marketplace submission process.

## Installation

```js
window.axim.pluginsInstall('/path/to/Axim-plugins/plugins/plugin-creator')
```

## Triggered By

Any user message containing:
- `create plugin`, `new plugin`, `make plugin`
- `build plugin`, `add plugin`, `write plugin`
- `plugin template`

## What It Creates

When triggered, the agent will scaffold:

1. **Directory structure** — `.axim-plugin/`, `skills/`, `scripts/`, `assets/`
2. **plugin.json** — Manifest with name, version, capabilities
3. **SKILL.md** — If the plugin includes skills
4. **mcp.json** — If the plugin includes MCP server integration
5. **README.md** — Documentation

## Plugin Capabilities

| Capability | Description |
|------------|-------------|
| `skills` | Knowledge modules injected into agent context |
| `mcp` | MCP server configuration for external tools |
| `agents` | Custom agent definitions for multi-agent workflows |
| `scripts` | Executable automation scripts |

## Marketplace

All AXIM plugins are published to: **https://github.com/GRRN-MAKER/Axim-plugins**

## File Structure

```
plugin-creator/
  .axim-plugin/
    plugin.json
  skills/
    plugin-creator/
      SKILL.md
  README.md
```
