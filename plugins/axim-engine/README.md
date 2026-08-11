# axim-engine

> AXIM Engine tools — manage agents, callbacks, sessions, events, and tool schemas at runtime.

## Overview

The **axim-engine** plugin exposes the AXIM engine's 6 core systems to the agent. When a user asks about agents, callbacks, sessions, events, or tool schemas, the agent receives comprehensive instructions on interacting with the engine API.

## Installation

```js
window.axim.pluginsInstall('/path/to/Axim-plugins/plugins/axim-engine')
```

## Triggered By

Any user message containing:
- `list agents`, `show agents`, `registered agents`, `agent registry`
- `callbacks`, `list callbacks`, `register callback`
- `event history`, `events`
- `session state`, `create session`, `manage session`
- `tool schema`, `validate tool`, `describe tool`
- `engine status`, `multi-agent`
- `sequential agent`, `parallel agent`, `loop agent`

## Engine Architecture

### 1. Event System (`engine/events.js`)

Typed event bus with pub/sub, wildcard subscriptions, and 500-event history.

```
Event {
  id:           string    — UUID
  type:         string    — EventType constant
  author:       string    — 'user', 'odyssey', 'magnus', 'system', agent name
  content:      object    — { text, toolCalls, toolResults, ... }
  actions:      object    — { stateDelta, escalate, transferToAgent }
  invocationId: string    — groups events from one interaction
  timestamp:    number    — milliseconds since epoch
}
```

**13 event types:** `user_message`, `agent_response`, `agent_thinking`, `tool_call`, `tool_result`, `model_request`, `model_response`, `state_change`, `transfer`, `error`, `system`, `callback_block`, `stream_chunk`

### 2. Callback Framework (`engine/callbacks.js`)

6 lifecycle hooks with priority ordering. Lower priority numbers run first. Any callback returning non-null blocks the pipeline.

| Hook | Data Received | Return to Block |
|------|--------------|-----------------|
| `before_agent` | `{ message, session }` | `{ message: '...' }` |
| `after_agent` | `{ session }` | Override result |
| `before_model` | `{ messages }` | `{ blocked: true, reason: '...' }` |
| `after_model` | `{ response }` | `{ text: '...' }` to override |
| `before_tool` | `{ toolName, args }` | `{ blocked: true, ... }` |
| `after_tool` | `{ toolName, args, result, durationMs }` | Modified result |

**5 built-in callbacks:**
- `BuiltInCallbacks.contentFilter(patterns)` — regex input filter
- `BuiltInCallbacks.requireApproval(toolNames)` — tool approval gate
- `BuiltInCallbacks.outputSanitizer(redactPatterns)` — output redaction
- `BuiltInCallbacks.executionLogger(stateManager)` — tool execution logging
- `BuiltInCallbacks.rateLimiter(maxPerMinute)` — request rate limiting

### 3. Session Service (`engine/session.js`)

Pluggable session storage with 4-level state scoping.

**Backends:**
- `InMemorySessionService` — volatile, for testing
- `JsonSessionService` — persistent, stored at `~/.axim/sessions/`

**State scoping:**
- `app:key` — shared across all users and sessions (persisted to `_app_state.json`)
- `user:key` — per-user across sessions (persisted to `_users/<userId>.json`)
- `temp:key` — current invocation only (auto-cleared after each run)
- `key` — session-scoped (persisted with session)

### 4. Runner (`engine/runner.js`)

Execution engine decoupled from the UI. Orchestrates: agent → LLM call → tool calls → tool results → repeat.

```
Runner {
  agent:          BaseAgent            — root agent to execute
  sessionService: BaseSessionService   — session backend
  callbacks:      CallbackRegistry     — lifecycle hooks
  eventBus:       EventBus             — event pub/sub
  toolRouter:     ToolRouter           — tool execution
  maxIterations:  number               — loop cap (default: 10)
}
```

The Runner yields `Event` objects via an async generator:
```js
for await (const event of runner.run({ userId, sessionId, message })) {
  // Process each event
}
```

### 5. Multi-Agent Framework (`engine/agents.js`)

Composable agent types for building complex workflows:

| Agent | Usage |
|-------|-------|
| `LlmAgent` | Single LLM-powered agent with instruction, tools, model |
| `SequentialAgent` | Pipeline: A → B → C (each sees previous state) |
| `ParallelAgent` | Fan-out: A + B + C concurrently |
| `LoopAgent` | Repeat: A → B → A → B until exit condition |
| `AgentTool` | Wrap any agent as a callable tool |
| `AgentRegistry` | Central registry with capability search |

**Instruction templating:** `{state_key}` in agent instructions auto-resolves from session state.

### 6. Schema Validation (`engine/schema.js`)

JSON Schema definitions for 27 tools. Validates arguments before execution.

**Features:**
- Required field checking
- Type validation with coercion (string → number)
- Enum validation
- Auto-wrapping of string args for single-required-field tools
- `describe(toolName)` for human-readable schema docs

## API Reference

| Method | Description |
|--------|-------------|
| `engineListAgents()` | List all registered agents |
| `engineListCallbacks()` | List all callback hooks |
| `engineListSchemas()` | List all tool schema names |
| `engineDescribeSchema(tool)` | Human-readable schema for a tool |
| `engineGetEventHistory(type?, limit?)` | Recent events from event bus |
| `engineSessionCreate(userId, sessionId)` | Create a session |
| `engineSessionGet(sessionId)` | Load a session |
| `engineSessionList(userId?)` | List sessions |
| `engineSessionDelete(sessionId)` | Delete a session |
| `onEngineEvent(callback)` | Subscribe to all engine events |

## File Structure

```
axim-engine/
  .axim-plugin/
    plugin.json
  skills/
    engine-tools/
      SKILL.md
  README.md
```
