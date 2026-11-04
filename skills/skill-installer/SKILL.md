---
name: skill-installer
description: Install, uninstall, and manage AXIM skills from local paths or repositories.
keywords:
  - install skill
  - uninstall skill
  - remove skill
  - list skills
  - manage skills
  - skill manager
  - show skills
---

# AXIM Skill Installer

You are helping the user manage their AXIM skills.

## Commands

### List installed skills
Show all skills from both system and user directories:
- System: `~/.axim/skills/.system/` (built-in, not removable)
- User: `~/.axim/skills/user/` (user-installed, removable)

Use `window.axim.skillsList()` to get the full list.

### Install a skill
To install a skill from a local directory:
```js
window.axim.skillsInstall('/path/to/skill-directory')
```

The directory must contain a `SKILL.md` file with valid frontmatter.

### Uninstall a skill
```js
window.axim.skillsUninstall('skill-name')
```

Only user-installed skills can be uninstalled. System skills are protected.

### Reload skills
After manually editing skill files:
```js
window.axim.skillsReload()
```

## Skill Locations
- **System skills**: `~/.axim/skills/.system/` — shipped with AXIM
- **User skills**: `~/.axim/skills/user/` — installed by the user
- **Plugin skills**: `~/.axim/plugins/installed/<plugin>/skills/` — bundled with plugins

## Troubleshooting
- **Skill not matching**: Check that keywords in SKILL.md frontmatter match user queries
- **Skill not loading**: Ensure SKILL.md has valid YAML frontmatter between `---` markers
- **Skill too large**: Keep SKILL.md under 5000 characters for fast injection
