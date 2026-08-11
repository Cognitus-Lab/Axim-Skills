# AXIM Plugins — Regular Update Schedule

This document defines a recurring maintenance cadence for keeping integrations, plugins, and third-party dependencies secure, stable, and compatible.

## Monthly Tasks

1. **Dependency Audits**
   - Run automated dependency scanners (`npm audit`, `pip-audit`).
   - Upgrade packages with critical vulnerabilities.
   - Test plugins against latest major releases of integrated services.

2. **Log Reviews**
   - Inspect `~/.axim/logs/` for anomalies, repeated errors, and deprecated API warnings.
   - Archive older logs (>3 months).

3. **Health Checks**
   - Validate all MCP server connections and token refresh cycles.
   - Verify agent registration and workflow execution in staging.

## Quarterly Tasks

1. **Plugin Compatibility Testing**
   - Re-test all installed skills against the latest AXIM core release notes.
   - Patch SKILL.md keyword sets if upstream terminology changes.

2. **Security Review**
   - Refresh cryptographic materials (certificates, signing keys).
   - Rotate long-lived tokens or secrets stored in `~/.axim/config/secrets.env`.

3. **Documentation Updates**
   - Sync this repo’s README, USER_GUIDE, and SECURITY pages with actual behavior.
   - Add examples for newly added features.

## Annual Tasks

1. **Architecture Review**
   - Evaluate plugin architecture against emerging best practices (modularity, observability, least privilege).
   - Deprecate or refactor legacy plugins that violate security or performance SLAs.

2. **Compliance Checks**
   - Verify adherence to GDPR, HIPAA, or other regulatory frameworks as applicable.
   - Conduct penetration tests on exposed MCP endpoints.

## Change Management

All updates must be logged in `CHANGELOG.md` and deployed via pull requests. Major version bumps require regression tests and stakeholder approval.