---
name: plugin-creator
description: Create AXIM plugins — bundles of skills, tools, MCP servers, and agents.
keywords:
  - create plugin
  - new plugin
  - make plugin
  - build plugin
  - plugin template
  - add plugin
  - write plugin
---

# AXIM Plugin Creator

You are helping the user create a new AXIM plugin. Plugins are installable bundles that extend AXIM with skills, MCP server integrations, custom agents, and scripts.

## Plugin Structure

```
my-plugin/
  .axim-plugin/
    plugin.json       ← Required: manifest
  skills/             ← Optional: plugin-specific skills
    my-skill/
      SKILL.md
  mcp.json            ← Optional: MCP server configuration
  agents/             ← Optional: custom agent definitions
    agent.json
  scripts/            ← Optional: executable scripts
  assets/             ← Optional: static resources
  README.md           ← Recommended: documentation
```

## plugin.json (Manifest)

```json
{
  "name": "my-plugin",
  "description": "What this plugin does",
  "version": "1.0.0",
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

## MCP Server Configuration (mcp.json)

If the plugin provides an MCP server:

```json
{
  "name": "my-mcp-server",
  "transport": "stdio",
  "command": "node",
  "args": ["./scripts/mcp-server.js"],
  "env": {
    "API_KEY": "${AXIM_PLUGIN_API_KEY}"
  }
}
```

## Installation

Plugins are installed to `~/.axim/plugins/installed/`:

```js
window.axim.pluginsInstall('/path/to/my-plugin')
```

## Contributing to the Marketplace

Submit plugins to: https://github.com/GRRN-MAKER/Axim-plugins

1. Fork the repository
2. Add your plugin under `plugins/<your-plugin-name>/`
3. Include a README.md with usage instructions
4. Submit a pull request

## Rules

1. **name**: lowercase, hyphenated
2. **plugin.json**: Required — without it the plugin won't load
3. **Skills**: Follow the same SKILL.md format as standalone skills
4. **MCP**: Use standard MCP protocol (stdio or SSE transport)
5. **Scripts**: Must be executable, tested, and sandboxed
6. **No network on install**: Plugins must work offline after installation

Now create the plugin based on what the user asked for.
