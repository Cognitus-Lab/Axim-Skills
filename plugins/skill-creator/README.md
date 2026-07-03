# skill-creator

> Create new AXIM skills — define knowledge modules that extend the agent's capabilities.

## Overview

The **skill-creator** plugin teaches the AXIM agent how to create new skills. When a user asks to "create a skill", "build a new skill", or "make a skill template", this plugin's skill is injected into the agent's context with full instructions on:

- The correct SKILL.md format (YAML frontmatter + Markdown body)
- Directory structure conventions
- Keyword selection best practices
- A complete working example

## Installation

```js
window.axim.pluginsInstall('/path/to/Axim-plugins/plugins/skill-creator')
```

## Triggered By

Any user message containing:
- `create skill`, `new skill`, `make skill`
- `add skill`, `write skill`, `build skill`
- `skill template`

## What It Does

When triggered, the agent receives instructions on how to:

1. Create a directory under `~/.axim/skills/user/<skill-name>/`
2. Write a `SKILL.md` file with proper YAML frontmatter
3. Choose effective keywords (3-10 phrases)
4. Write actionable agent guidance (not documentation)
5. Reload skills with `window.axim.skillsReload()`

## Example Interaction

**User:** "Create a skill for Docker Compose best practices"

**Agent:** Creates `~/.axim/skills/user/docker-compose/SKILL.md` with:
- Keywords: `docker compose`, `docker-compose`, `compose file`, `multi-container`
- Body: Best practices for writing docker-compose.yml files

## File Structure

```
skill-creator/
  .axim-plugin/
    plugin.json          ← Plugin manifest
  skills/
    skill-creator/
      SKILL.md           ← Skill instructions
  README.md              ← This file
```
