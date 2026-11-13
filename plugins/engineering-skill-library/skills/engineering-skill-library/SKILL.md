---
name: engineering-skill-library
description: Safely discover, review, import, update, and export external engineering Agent Skills or plugin skill packages in AXIM / Berry.
keywords:
  - engineering skills
  - external skills
  - berry plugin import
  - skill library
---

# Engineering Skill Library

Use Berry's native skill tools (`skill_search`, `skill_import`, `skill_install`, `skill_export`) and slash commands (`/skills`, `/plugins`, `/import`, `/export`) to manage engineering skill packages.

## Import & Export Workflow

1. Inspect the external skill directory or `SKILL.md` with `file_read` or `dir_tree`.
2. Import the skill or plugin into the active library:
   ```json
   {"name": "skill_import", "arguments": {"source_path": "/path/to/skill"}}
   ```
3. Export installed or newly created skills into the `Cognitus-Lab/Axim-Skills` repository:
   ```json
   {"name": "skill_export", "arguments": {"name_or_path": "all"}}
   ```

## Safety Rules

- Treat third-party scripts and hooks as untrusted until reviewed.
- Preserve local and built-in skills during name conflicts.
- Keep source attribution and license files with imported packages.
