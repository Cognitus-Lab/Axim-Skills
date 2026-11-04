---
name: skill-creator
description: Create new AXIM skills — define knowledge modules that extend the agent's capabilities.
keywords:
  - create skill
  - new skill
  - make skill
  - add skill
  - write skill
  - build skill
  - skill template
---

# AXIM Skill Creator

You are helping the user create a new AXIM skill. A skill is a knowledge module that gets injected into the agent's context when a user message matches the skill's keywords.

## Skill Structure

Each skill is a directory under `~/.axim/skills/user/` containing a `SKILL.md` file:

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

Instructions for the agent when this skill is activated.
Include: best practices, code patterns, API references, constraints.
```

## Rules

1. **name**: lowercase, hyphenated (e.g., `react-hooks`, `docker-compose`)
2. **description**: One clear sentence — this is shown in skill listings
3. **keywords**: 3-10 phrases that trigger this skill. Include variations.
4. **Body**: Actionable instructions the agent can follow. Not documentation — guidance.
5. Skills are stored at `~/.axim/skills/user/<skill-name>/SKILL.md`
6. After creating, tell the user to run `window.axim.skillsReload()` or restart AXIM

## Example

```markdown
---
name: react-testing
description: Best practices for testing React components with Testing Library.
keywords:
  - test react
  - testing library
  - react test
  - component test
  - jest react
---

# React Testing Best Practices

When writing tests for React components:

1. Use `@testing-library/react` — never use enzyme
2. Query by role, label, or text — never by class or ID
3. Use `userEvent` over `fireEvent` for realistic interactions
4. Test behavior, not implementation details
5. Use `screen` for queries: `screen.getByRole('button', { name: /submit/i })`
```

Now create the skill based on what the user asked for.
