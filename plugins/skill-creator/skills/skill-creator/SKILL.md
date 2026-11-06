---
name: skill-creator
description: Create new AXIM / Berry skills — define knowledge modules that extend the agent's capabilities.
keywords:
  - create skill
  - new skill
  - make skill
  - add skill
  - write skill
  - build skill
  - skill template
---

# AXIM / Berry Skill Creator

Create a new AXIM skill as a directory containing a `SKILL.md` file with YAML frontmatter, then register it with `skill_import` or `skill_export`.

## Skill Structure

```
my-skill/
  SKILL.md          ← Required: frontmatter + instructions
  examples/         ← Optional: example files
  templates/        ← Optional: code templates
```

## SKILL.md Format

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

Actionable instructions, code patterns, tool calls, and constraints for the agent when this skill is active.
```

## Registering & Exporting the Skill

1. Write the `SKILL.md` file using `file_write`.
2. Import and activate it into Berry's skill library using `skill_import`:
   ```json
   {"name": "skill_import", "arguments": {"source_path": "my-skill/SKILL.md"}}
   ```
3. Optionally export it to the `Cognitus-Lab/Axim-Skills` GitHub repository plugins directory using `skill_export`:
   ```json
   {"name": "skill_export", "arguments": {"name_or_path": "my-skill"}}
   ```
