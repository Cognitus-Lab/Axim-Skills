---
name: helix-foundry
description: Connect business databases, tools, and documents into unified ontologies and knowledge graphs, run entity extraction, manage local Docker stacks, and ask natural language questions with source-cited answers.
keywords:
  - helix
  - foundry
  - helix-foundry
  - ontology
  - knowledge graph
  - data connector
  - helixdb
  - graph database
  - document extraction
  - enterprise graph
  - ontology agent
  - foundry analyst
  - postgresql connector
  - mysql connector
  - s3 connector
---

# Helix Foundry Skill & MCP Tools

Helix Foundry connects your business data — databases (PostgreSQL, MySQL), SaaS tools (Stripe, GitHub, Slack, Notion, Linear, Cal.com, PostHog), documents (PDF, Markdown, Text), and tabular files (CSV, TSV, Parquet) — into a unified, queryable knowledge graph powered by HelixDB.

You can run Helix Foundry locally on your computer with Docker or connect to an existing hosted instance.

---

## Capabilities & Workflows

1. **Local Stack Lifecycle**: Launch, inspect, and stop the local multi-container Foundry stack.
2. **Data Connector Management**: Discover available connector kinds and inspect synced tables.
3. **Document Ingestion**: List, upload, and organize document sets.
4. **Ontology Generation**: Inspect drafted types, relationships, properties, and load state.
5. **Event Streaming**: Ingest real-time JSON pieces into API event sources.
6. **Foundry Analyst**: Query the graph ontology with natural language to get cited answers and visual query breakdowns.

---

## MCP Server & Tool Calling

When the `helix-foundry` MCP server is enabled in AXIM / Berry, use these structured tools:

### 1. `helix_foundry_status`
Check whether Helix Foundry web UI and backend APIs are responsive.
```json
{"name": "helix_foundry_status", "arguments": {}}
```

### 2. `helix_foundry_stack_up`
Start the local Docker Compose stack in the background.
```json
{"name": "helix_foundry_stack_up", "arguments": {"profile": "ollama"}}
```

### 3. `helix_foundry_stack_down`
Stop the running local containers safely without wiping volumes or secrets.
```json
{"name": "helix_foundry_stack_down", "arguments": {}}
```

### 4. `helix_foundry_stack_logs`
View recent container and backend service logs.
```json
{"name": "helix_foundry_stack_logs", "arguments": {"lines": 50}}
```

### 5. `helix_foundry_list_ontologies`
List all ontologies and their draft/loaded statuses in the workspace.
```json
{"name": "helix_foundry_list_ontologies", "arguments": {"workspace_id": "ws_acme"}}
```

### 6. `helix_foundry_get_ontology`
Fetch full schema definitions, entities, links, and active load IDs for an ontology.
```json
{"name": "helix_foundry_get_ontology", "arguments": {"ontology_id": "ont_123", "workspace_id": "ws_acme"}}
```

### 7. `helix_foundry_list_connectors`
List connected data sources, credentials status, and table row counts.
```json
{"name": "helix_foundry_list_connectors", "arguments": {"workspace_id": "ws_acme"}}
```

### 8. `helix_foundry_list_connector_kinds`
List all available connectors (PostgreSQL, MySQL, S3, Stripe, Slack, Notion, GitHub, Linear, etc.).
```json
{"name": "helix_foundry_list_connector_kinds", "arguments": {}}
```

### 9. `helix_foundry_list_documents`
List uploaded documents and their extraction states across document sets.
```json
{"name": "helix_foundry_list_documents", "arguments": {"workspace_id": "ws_acme", "set_id": "set_docs"}}
```

### 10. `helix_foundry_send_pieces`
Send structured JSON events or records directly to an API event connector.
```json
{
  "name": "helix_foundry_send_pieces",
  "arguments": {
    "event_source_id": "conn_events_1",
    "pieces": [
      {
        "id": "order_1001",
        "data": {
          "customer": "Alice",
          "amount": 250.00,
          "status": "completed"
        }
      }
    ],
    "client_token": "uuid-12345"
  }
}
```

### 11. `helix_foundry_ask`
Query the Helix Foundry Analyst for answers grounded in your business ontology.
```json
{
  "name": "helix_foundry_ask",
  "arguments": {
    "question": "What were our top 5 revenue-generating enterprise accounts last quarter?",
    "ontology_id": "ont_acme"
  }
}
```

---

## Quickstart: Local Computer Deployment

To spin up Helix Foundry on this machine:
1. Ensure Docker Desktop or Docker Engine is running.
2. In the plugin directory or via tool:
   ```sh
   docker compose up -d --wait
   ```
3. Open `http://localhost:3000` in your browser.
4. Default ports:
   - Web UI: `http://localhost:3000`
   - Store: `http://localhost:8333`
   - API / WFE: `http://127.0.0.1:8081`

---

## Best Practices & Security
- **Data Privacy**: Stored credentials (database passwords, API keys) are sealed with local AES connector keys in the `secrets` Docker volume.
- **Never Run `docker compose down -v`**: Preserves connector keys and synced data.
- **Loopback Bound**: In local mode, the application listens on `127.0.0.1` only for local sovereign control.
