# skill-installer

> Install, uninstall, and manage AXIM skills from local paths or repositories.

## Overview

The **skill-installer** plugin teaches the AXIM agent how to manage the skill system. When a user asks to "install a skill", "list skills", or "remove a skill", the agent receives full instructions on the skill management API.

## Installation

```js
window.axim.pluginsInstall('/path/to/Axim-plugins/plugins/skill-installer')
```

## Triggered By

Any user message containing:
- `install skill`, `uninstall skill`, `remove skill`
- `list skills`, `manage skills`, `show skills`
- `skill manager`

## API Reference

| Method | Description |
|--------|-------------|
| `window.axim.skillsList()` | Returns array of all loaded skills with name, description, type |
| `window.axim.skillsMatch(message)` | Returns skills matching a user message with scores |
| `window.axim.skillsInstall(path)` | Installs a skill from a local directory path |
| `window.axim.skillsUninstall(name)` | Removes a user-installed skill (system skills protected) |
| `window.axim.skillsReload()` | Reloads all skills from disk |

## Skill Directories

| Location | Type | Removable |
|----------|------|-----------|
| `~/.axim/skills/.system/` | System (built-in) | No |
| `~/.axim/skills/user/` | User-installed | Yes |
| `~/.axim/plugins/installed/<plugin>/skills/` | Plugin-bundled | Via plugin uninstall |

## File Structure

```
skill-installer/
  .axim-plugin/
    plugin.json
  skills/
    skill-installer/
      SKILL.md
  README.md
```
