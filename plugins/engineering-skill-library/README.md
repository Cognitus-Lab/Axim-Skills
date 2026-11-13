# Engineering Skill Library

> Safely discover and import compatible Agent Skills from verified engineering repositories into AXIM.

## Overview

This plugin teaches AXIM how to use its Settings-based Engineering Library. The importer supports one-skill-at-a-time review, source attribution, conflict-safe namespacing, and executable-resource quarantine.

## Verified Sources

- Matt Pocock Engineering Skills — MIT
- Google Skills — Apache-2.0
- Hugging Face Skills — Apache-2.0
- Android Skills — Apache-2.0
- Microsoft Skills — MIT
- Cloudflare Skills — Apache-2.0
- Anthropic Skills — Apache-2.0; importable as skill packages

Vercel Labs Agent Skills remains visible but blocked because the repository does not declare a redistribution license.

## Berry Compatibility

Berry can import a local plugin folder. It copies only directories containing `SKILL.md`. It does not import or enable hooks, MCP servers, agents, commands, or plugin runtime configuration. Bundled scripts are copied as non-executable review resources.

## Safety

Imported skills are namespaced by source and carry provenance metadata. Scripts are quarantined and require explicit user review before any separate execution request.
