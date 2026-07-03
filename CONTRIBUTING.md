# Contributing to AXIM Plugins

Thank you for your interest in contributing to the AXIM plugin ecosystem!

## How to Submit a Plugin

1. **Fork** this repository
2. **Create** your plugin directory under `plugins/<your-plugin-name>/`
3. **Follow** the plugin structure (see below)
4. **Test** your plugin locally
5. **Submit** a pull request

## Plugin Requirements

### Required
- `.axim-plugin/plugin.json` — Valid manifest with name, version, description
- `README.md` — Clear documentation with installation and usage instructions

### Optional
- `skills/` — One or more SKILL.md files
- `mcp.json` — MCP server configuration
- `agents/` — Custom agent definitions
- `scripts/` — Executable scripts
- `assets/` — Static resources

## Plugin Manifest (`plugin.json`)

```json
{
  "name": "your-plugin-name",
  "version": "1.0.0",
  "description": "Clear, one-line description",
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

## Skill Format (`SKILL.md`)

```markdown
---
name: your-skill-name
description: One-line description.
keywords:
  - keyword1
  - keyword2
---

# Skill Title

Instructions for the agent.
```

### Skill Guidelines

- **Keywords**: 3-10 phrases, include variations
- **Body**: Actionable instructions, not passive documentation
- **Size**: Keep under 5000 characters for fast injection
- **Name**: lowercase, hyphenated

## Testing Your Plugin

```bash
# Clone and install
git clone https://github.com/GRRN-MAKER/Axim-plugins.git

# In AXIM, install your plugin
window.axim.pluginsInstall('/path/to/Axim-plugins/plugins/your-plugin')

# Verify it loaded
window.axim.pluginsList()

# Test skill matching
window.axim.skillsMatch('your keyword here')
```

## Code of Conduct

- Be respectful and constructive
- No malicious code, data collection, or network calls on install
- Plugins must work offline after installation
- Follow the MIT license

## Questions?

Open an issue at https://github.com/GRRN-MAKER/Axim-plugins/issues
