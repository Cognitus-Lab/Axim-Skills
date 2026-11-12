---
name: bruno
description: Automated API testing, collection execution, and OpenAPI/cURL specification imports using the team's offline CLI.
keywords:
  - bruno
  - api testing
  - collection runner
  - openapi import
  - curl import
  - api documentation
  - http automation
  - rest api
  - graphql
---

# Bruno API Automation & Testing Skill

Run, test, and automate HTTP, REST, and GraphQL API endpoints in bulk from AXIM / Berry.

---

## Capabilities

1. **Verify or Provision CLI**:
   - `bruno_ensure_cli`: Provision or verify the `bru` CLI on the local machine from the team's local checkout or internal mirror.

2. **Run Collections & Requests**:
   - `bruno_run`: Execute one or more API requests or complete folders in a collection with custom environments and outputs.

3. **Import Specifications**:
   - `bruno_import`: Convert existing OpenAPI or cURL definitions directly into runnable collections.

4. **Generate API Documentation**:
   - `bruno_docs`: Output standalone HTML API documentation from collections.

---

## Tool Reference

### `bruno_ensure_cli`
Provision or verify the local CLI binary:
```json
{
  "name": "bruno_ensure_cli",
  "arguments": {
    "force_reinstall": false
  }
}
```

### `bruno_run`
Run API collection requests:
```json
{
  "name": "bruno_run",
  "arguments": {
    "collection_path": "tests/api_collection",
    "environment": "staging",
    "output": "json"
  }
}
```

### `bruno_import`
Import OpenAPI or cURL specifications into a collection:
```json
{
  "name": "bruno_import",
  "arguments": {
    "source_path": "spec/openapi.yaml",
    "format": "openapi",
    "collection_path": "collections/api"
  }
}
```

### `bruno_docs`
Generate API documentation from collections:
```json
{
  "name": "bruno_docs",
  "arguments": {
    "collection_path": "collections/api",
    "output_path": "docs/api.html"
  }
}
```
