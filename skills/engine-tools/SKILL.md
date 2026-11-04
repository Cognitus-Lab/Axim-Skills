---
name: engine-tools
description: AXIM Engine tools — manage agents, callbacks, sessions, events, and tool schemas at runtime.
keywords:
  - list agents
  - show agents
  - registered agents
  - agent registry
  - callbacks
  - list callbacks
  - register callback
  - event history
  - events
  - session state
  - create session
  - manage session
  - tool schema
  - validate tool
  - describe tool
  - engine status
  - multi-agent
  - sequential agent
  - parallel agent
  - loop agent
---

# AXIM Engine Tools

You are helping the user interact with the AXIM engine — the runtime that powers agent execution, callbacks, sessions, events, and tool validation.

## Agent Registry

AXIM supports multiple agent types that can be composed into workflows:

### List Registered Agents
```js
window.axim.engineListAgents()
// Returns: [{ name, type, description, model, subAgents }]
```

### Agent Types

| Type | Description |
|------|-------------|
| `LlmAgent` | LLM-powered agent (Odyssey or Magnus) with instruction templating |
| `SequentialAgent` | Runs sub-agents in order — each sees state from the previous |
| `ParallelAgent` | Runs sub-agents concurrently — all share session state |
| `LoopAgent` | Repeats sub-agents until max iterations or escalation |
| `AgentTool` | Wraps an agent as a callable tool for parent agents |

### Instruction Templating
LlmAgent instructions support `{state_key}` placeholders that auto-resolve from session state:
- `{user:preference}` → user-scoped state
- `{app:version}` → app-wide state
- `{myKey}` → session-scoped state

## Callback Framework

6 lifecycle hooks intercept the execution pipeline:

| Hook | When | Can Block? |
|------|------|-----------|
| `before_agent` | Before agent starts | Yes — return content to skip |
| `after_agent` | After agent completes | Yes — override result |
| `before_model` | Before LLM request | Yes — return response to skip LLM (guardrail) |
| `after_model` | After LLM response | Yes — modify/replace response |
| `before_tool` | Before tool executes | Yes — return dict to skip (approval gate) |
| `after_tool` | After tool returns | Yes — transform result |

### List Callbacks
```js
window.axim.engineListCallbacks()
// Returns: { before_agent: [...], after_model: [...], ... }
```

### Built-in Callbacks
- **contentFilter** — blocks messages matching regex patterns
- **requireApproval** — pauses for user approval on specific tools
- **outputSanitizer** — redacts patterns from model responses
- **executionLogger** — logs all tool executions with timing
- **rateLimiter** — limits requests per minute

## Session Service

Sessions provide scoped state with 4 prefix levels:

| Prefix | Scope | Persists |
|--------|-------|----------|
| `app:key` | All users, all sessions | Yes |
| `user:key` | Per-user, across sessions | Yes |
| `temp:key` | Current invocation only | No (cleared after each run) |
| `key` | Current session only | Yes (within session) |

### Session API
```js
window.axim.engineSessionCreate('user-id', 'session-id')
window.axim.engineSessionGet('session-id')
window.axim.engineSessionList('user-id')  // or omit for all
window.axim.engineSessionDelete('session-id')
```

Sessions are stored as JSON files at `~/.axim/sessions/`.

## Event System

Every action produces a typed Event with full audit trail:

| Event Type | Description |
|------------|-------------|
| `user_message` | User sent a message |
| `agent_response` | Agent produced a response |
| `agent_thinking` | Agent thinking/reasoning content |
| `tool_call` | Agent requested a tool call |
| `tool_result` | Tool returned a result |
| `model_request` | LLM request sent |
| `model_response` | LLM response received |
| `state_change` | Session state was modified |
| `transfer` | Agent delegation/transfer |
| `error` | Error occurred |
| `callback_block` | Callback blocked an action |

### View Event History
```js
window.axim.engineGetEventHistory()              // Last 50 events
window.axim.engineGetEventHistory('tool_call', 10) // Last 10 tool calls
```

### Subscribe to Events (renderer)
```js
window.axim.onEngineEvent((event) => {
  console.log(event.type, event.author, event.content);
});
```

## Tool Schema Validation

All 27+ tools have JSON Schema definitions that validate arguments before execution:

```js
window.axim.engineListSchemas()        // List all tool names with schemas
window.axim.engineDescribeSchema('bash') // Human-readable schema description
```

### How Validation Works
1. Arguments are validated against the schema before tool execution
2. Missing required fields return an error with the expected schema
3. Type coercion is automatic (string "10" → number 10)
4. Unknown tools pass through without validation
5. String arguments are auto-wrapped for single-required-field tools

When helping users with engine features, use these APIs and explain the concepts clearly.
