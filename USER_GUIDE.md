# AXIM Plugins — User Guide

This guide explains how to install, use, and troubleshoot AXIM plugins, including skills, MCP servers, agents, and scripts.

## Overview

- **Skills**: Inject knowledge into the agent’s context when matched keywords appear.
- **MCP Servers**: Connect external tools/services via Model Context Protocol.
- **Agents**: Define custom agent behaviors for multi-agent workflows.
- **Scripts**: Automation scripts executed by the AXIM runtime.

## Installing Plugins

### Via the AXIM Console

```js
// Inside the AXIM app console
window.axim.pluginsInstall('/absolute/path/to/plugin-directory')
```

### Via GitHub (Manual)

1. Clone the official repo:
   ```bash
   git clone https://github.com/GRRN-MAKER/Axim-Skills.git
   ```
2. Navigate to the desired plugin folder inside `plugins/`.
3. Run `window.axim.pluginsInstall()` pointing to that folder.

### Verifying Installation

```js
// Lists all installed plugins and their statuses
window.axim.pluginsList()
```

## Using Plugins

After installation, restart the AXIM app. The loader scans `~/.axim/plugins/installed/` and activates matching skills/integrations automatically.

### Skills
- Triggered implicitly by keyword matches in user input.
- View active skills via the AXIM UI sidebar → "Active Skills" panel.

### MCP Integrations
- Appear as new tools in the AXIM console.
- Use `window.axim.mcpStatus()` to verify connectivity.

### Agents
- Registered agents show up in "Multi-Agent Workflows" tab.
- Launch agents by invoking their defined entry points.

### Scripts
- Found under "Automation" in the sidebar.
- Run via `window.axim.runScript('script-id')`.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Plugin doesn’t activate | Wrong path during install | Re-install with correct absolute path |
| Skill not triggering | Keywords mismatch | Edit SKILL.md keywords, reinstall |
| MCP connection fails | Network/auth issue | Check logs (`~/.axim/logs/mcp.log`) |
| Agent not listed | Invalid manifest | Validate manifest.json schema |

## Logs & Diagnostics

- Main log: `~/.axim/logs/axim.log`
- Plugin loader: `~/.axim/logs/loader.log`
- MCP traffic: `~/.axim/logs/mcp.log`

If issues persist, contact AXIM support with relevant log excerpts.