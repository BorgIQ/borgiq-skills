# AI Agent Actor Reference

The AiAgentActor runs an autonomous AI coding agent with a private workspace filesystem, bash, and BorgIQ actor tools. It executes a pi coding agent in checkpointed serverless segments: the agent works in a real (ephemeral) workspace, its state is checkpointed between segments, and a session can be continued across invocations via `sessionId` — so tasks like "unzip this report, run a script over it, edit three files, zip the result" work without provisioning a full sandbox VM.

> **Type-name history:** before mid-2026 the `AiAgentActor` type name referred to a legacy orchestrator-loop agent with **no filesystem or bash** and options like `temperature`/`maxTokens`/`messages`. That actor still runs for existing flows as `DeprecatedAiAgent` (hidden from the palette). If you are reading or debugging an existing flow whose agent has those options, see [deprecated-ai-agent.md](deprecated-ai-agent.md). Do not create new `DeprecatedAiAgent` instances.

## Table of Contents

- [Overview](#overview)
- [Choosing an Agent Tier](#choosing-an-agent-tier)
- [Configuration Structure](#configuration-structure)
- [Source Ports](#source-ports)
- [Options Reference](#options-reference)
- [Built-in Tools](#built-in-tools)
- [Running Code with the deno Tool](#running-code-with-the-deno-tool)
- [Connecting BorgIQ Tools with aiAgentToolActorIds](#connecting-borgiq-tools-with-aiagenttoolactorids)
- [Tool Actor Configuration](#tool-actor-configuration)
- [Results Object](#results-object)
- [Available Models](#available-models)
- [Sessions and Continuation](#sessions-and-continuation)
- [Runtime Requirements](#runtime-requirements)
- [Limitations](#limitations)
- [Common Patterns](#common-patterns)
- [Complete Example: Report Processing Agent](#complete-example-report-processing-agent)
- [Accessing Agent Data in Downstream Actors](#accessing-agent-data-in-downstream-actors)
- [Migrating from DeprecatedAiAgent](#migrating-from-deprecatedaiagent)
- [Use Cases](#use-cases)
- [Best Practices](#best-practices)
- [TypeScript Schema Hint](#typescript-schema-hint)

## Overview

AiAgentActor gives an AI model a working environment plus your BorgIQ actors as tools. The agent loops through:

1. Receiving the task prompt (and, on continuation, the prior session state)
2. Deciding which tools to call — built-in filesystem/bash tools or wired BorgIQ actor tools
3. Executing the tools against its private session workspace or as child flowrun jobs
4. Processing tool results and continuing until the task is complete

**Key capabilities:**

- **Filesystem + bash**: built-in `read`, `write`, `edit`, `bash`, `grep`, `find`, `ls` tools run against a private session workspace
- **Code execution (opt-in)**: with `enableDenoTool`, a `deno` tool runs TypeScript/JavaScript the agent writes in its workspace
- **BorgIQ actor tools**: any actor wired via `aiAgentToolActorIds` is exposed to the agent as a callable tool (same mechanism as before)
- **Sessions**: re-invoking with the same `sessionId` continues the session — workspace and conversation state restore from the last checkpoint
- **Workspace in/out**: seed the workspace with `volumeZipFile`; receive the final workspace as `outputZipFile` on the done port
- **No wall-clock cap**: execution is segmented and checkpointed, so a session is not limited by any single serverless invocation's timeout
- **Status streaming**: assistant turns and tool results stream on the Status port during execution

**How it executes (what you'll observe):** the run is split into serverless segments, each bounded by the runtime's configured timeout. At each segment boundary the workspace and session state are checkpointed and the next segment resumes seamlessly — no synthetic messages appear in the conversation. `meta.segments` on the done port reports how many segments the run spanned. See [Limitations](#limitations) for the two user-visible consequences (at-least-once bash side effects; no background processes across segments).

## Choosing an Agent Tier

| Aspect | AiActor | **AiAgentActor** | AgentHarnessActor |
|--------|---------|------------------|-------------------|
| Execution | Single LLM call | Agent loop in checkpointed serverless segments | Harness CLI inside a sandbox VM (E2B/Daytona) |
| Filesystem / bash | None | Private session workspace + bash | Full machine |
| Tools | Describes tools, returns tool calls | Built-ins (read/write/edit/bash/grep/find/ls, + opt-in deno) + BorgIQ actor tools + MCP servers | Harness built-ins + BorgIQ tools + MCP servers |
| Startup latency | ~0 | Low (serverless invoke; cold restore adds seconds) | Sandbox provision + harness install (tens of seconds to minutes) |
| Sessions | No | Yes — `sessionId`, checkpoint/restore, 7-day sliding TTL | Yes — sandbox session zips |
| Background processes | — | No (nothing survives a segment boundary) | Yes (within sandbox lifetime) |
| MCP servers | No | Remote + BorgIQ (no stdio) | Remote + BorgIQ + stdio |
| Use case | Simple generation, structured output | File/data tasks, coding, research with tools — most agent work | Long-lived dev environments, stdio MCP, daemons, PTY |

Rule of thumb: start with AiAgentActor. Drop to AiActor when a single structured LLM call is enough; step up to AgentHarnessActor only when you need stdio MCP servers, background processes, or a persistent full machine.

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: AiAgentActor
    version: 1
    name: Report Processor
    msgVar: report_processor
    description: Agent that unpacks, analyzes, and summarizes uploaded reports
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdone000
        name: Done
      - id: SPRTdefault
        name: Status
    configuration:
      inputs:
        # Wire upstream actor data DIRECTLY into inputs (not into vars).
        reportZip: ${{ msg.upload_trigger.file }}
        instructions: ${{ msg.upload_trigger.instructions }}
      options:
        model: claude-sonnet-4-6
        systemPrompt: |
          You are a data analyst. Work inside your workspace; the report
          archive is already extracted there.
        prompt: ${{ inputs.instructions }}
        volumeZipFile: ${{ inputs.reportZip }}   # extracted into the workspace at session creation
        timeoutInMinutes: 30
        # sessionId: fixed-id-to-continue-later  # optional; auto-generated if empty
      aiAgentToolActorIds:
        - ACTR01toolactor1
        - ACTR01toolactor2
    schemas:
      inputs:
        type: object
        properties:
          reportZip:
            type: object
            title: Report Zip
            description: The uploaded report archive
          instructions:
            type: string
            title: Instructions
            description: What to do with the report
        required:
          - instructions
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Source Ports

AiAgentActor has two required source ports:

| Port ID | Name | Description |
|---------|------|-------------|
| `SPRTdone000` | Done | Emits the final result when the session completes (task done, timeout, error, or max loop count) |
| `SPRTdefault` | Status | Emits assistant turns and tool results while the agent runs |

### Done Port Output

```json
{
  "sessionId": "sess_01hxyz...",
  "success": true,
  "result": "I extracted the report, ran the aggregation script, and wrote summary.md. Revenue grew 14% QoQ...",
  "outputZipFile": { "id": "FILE01...", "name": "workspace.zip", "...": "..." },
  "sessionDataFile": { "id": "FILE01...", "name": "session.zip", "...": "..." },
  "meta": {
    "endReason": "completed",
    "model": "claude-sonnet-4-6",
    "segments": 2
  }
}
```

| Field | Description |
|-------|-------------|
| `sessionId` | The session ID (pass it back in `options.sessionId` to continue this session) |
| `success` | Whether the execution succeeded |
| `result` | Final assistant message, or the error message on failure. May be absent — do not depend on it unconditionally |
| `outputZipFile` | Zip of the session workspace (omitted when `returnOutputZipFile: false`) |
| `sessionDataFile` | Zip of the pi session data, portable to the harness tier (omitted when `returnSessionDataFile: false`) |
| `meta.endReason` | `completed`, `timeout`, `error`, or `max-loop-count` |
| `meta.model` | The model used |
| `meta.segments` | How many serverless segments the run spanned |

Token usage is not reported on the done port; it is metered per segment into the workspace AI log.

### Status Port Output

**Assistant turn** (`ai-agent-loop`) — emitted for each assistant turn; `toolCalls` is present when the turn invokes tools:

```json
{
  "type": "ai-agent-loop",
  "response": "The archive is extracted. I'll run the aggregation script next.",
  "toolCalls": [
    {
      "toolCallId": "toolu_01Kss5SfgsQUA7UGsuXCjhT1",
      "toolName": "deno",
      "input": { "path": "aggregate.ts", "args": ["data"] }
    }
  ],
  "meta": { "cwd": "/workspace", "timestamp": 1751791234567 }
}
```

**Tool result** (`tool-result`) — emitted after each tool call resolves:

```json
{
  "type": "tool-result",
  "toolCallId": "toolu_01Kss5SfgsQUA7UGsuXCjhT1",
  "toolName": "deno",
  "output": { "type": "json", "value": "wrote summary.csv (412 rows)" },
  "isError": false,
  "meta": { "cwd": "/workspace", "timestamp": 1751791236789 }
}
```

**Error** (`agent-harness-error`) — emitted on the Status port when the session ends unsuccessfully (the done port still fires, carrying `success: false`):

```json
{
  "type": "agent-harness-error",
  "message": "Agent execution failed",
  "meta": { "timestamp": 1751791240000 }
}
```

The `ai-agent-loop`/`tool-result` envelope (`type` / `response` / `toolCalls` / tool-result fields) is the same shape the legacy agent used, so status-port consumers built for the old actor keep working. Note that `meta` now carries `cwd` and `timestamp` (the legacy actor's status `meta` carried `model` and `usage`).

## Options Reference

All options live under `configuration.options`.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | `claude-sonnet-4-6` | The model to use. Any `AiAgentModels` value (see [Available Models](#available-models)); LLM calls route through the BorgIQ AI gateway using the workspace's AI credential for that provider |
| `prompt` | string | — | **Required.** The task prompt for the agent |
| `systemPrompt` | string | — | Background instructions appended to the agent's system prompt |
| `sessionId` | string | auto-generated | Session ID to continue or create (max 64 characters). Same ID = continue the session |
| `volumeZipFile` | BIQFile | — | Zip file extracted into the session workspace at session creation |
| `workingDirectory` | string | workspace root | Working directory for the agent, relative to the session workspace |
| `timeoutInMinutes` | integer | 30 | Session timeout in minutes, measured across segments |
| `maxLoopCount` | integer | unlimited | Maximum number of assistant turns |
| `allowedTools` | string[] | all | Allow-list of built-in tools (`read`/`write`/`edit`/`bash`/`grep`/`find`/`ls`/`deno`). Empty = all allowed |
| `disallowedTools` | string[] | — | Deny-list of built-in tools |
| `enableDenoTool` | boolean | **false** | Give the agent the `deno` tool, so it can run TypeScript/JavaScript it writes in its workspace. See [Running code with the deno tool](#running-code-with-the-deno-tool) |
| `allowNet` | boolean | **false** | Allow outbound network access from the tool runtime. Applies to `bash` too — with it off, `bash` has no `curl` at all |
| `allowNetList` | string[] | — | Only these hosts/CIDRs allowed for tool-runtime egress (system endpoints always included). Mutually exclusive with `denyNetList` |
| `denyNetList` | string[] | — | Block these hosts/CIDRs for tool-runtime egress (system endpoints cannot be denied). Mutually exclusive with `allowNetList` |
| `env` | record | — | Environment variables exposed to tools and bash. Values encrypted in transit. Reserved names rejected: `HOME`, `PATH`, `TMPDIR`, `NODE_OPTIONS`, `LD_PRELOAD`, `LD_LIBRARY_PATH`, and anything starting with `AWS_`, `DENO_`, or `BORGIQ_` |
| `mcpServers` | object[] | — | MCP servers exposed to the agent as tools. Remote (`type: http`) or internal (`type: borgiq`); stdio is not supported here. See [MCP Servers](#mcp-servers) |
| `returnOutputZipFile` | boolean | true | Include the workspace zip in the done-port result |
| `returnSessionDataFile` | boolean | true | Include the pi session data zip in the done-port result |

Validation rules enforced before the session starts:

- `prompt` must be non-empty.
- `allowNetList` and `denyNetList` are mutually exclusive.
- `env` keys matching a reserved name (case-insensitive) are rejected.
- A wired tool actor whose `msgVar` collides (case-insensitively) with a built-in tool name (`read`, `write`, `edit`, `bash`, `grep`, `find`, `ls`, `deno`) is rejected — rename the tool actor.

## Built-in Tools

The agent always has (subject to `allowedTools`/`disallowedTools`) seven built-in tools that operate on its private session workspace, plus `deno` when `enableDenoTool` is set:

| Tool | Purpose |
|------|---------|
| `read` / `write` / `edit` | Read, create, and surgically edit files in the workspace |
| `bash` | Run shell commands — an **in-process bash interpreter**, not a real shell. See the note below |
| `grep` / `find` / `ls` | Search and explore the workspace |
| `deno` | Run a TypeScript/JavaScript file from the workspace. **Only present when `enableDenoTool: true`** |

Notes:

- These names are **reserved** — a wired BorgIQ tool actor may not use them as its `msgVar`. `deno` is reserved only when `enableDenoTool: true`, so an existing canvas that wires a DenoActor named `deno` as a tool keeps working until you turn the option on (at which point rename that actor).
- To build a read-only agent, set `disallowedTools: [write, edit, bash]` and leave `enableDenoTool` off (a script could otherwise write to the workspace).
- Bash runs with a minimal environment: your `options.env` entries are exposed; platform and cloud-provider credentials are not.

### What `bash` can and cannot do

`bash`, `grep`, and `find` run **in-process** as a TypeScript bash interpreter over the workspace filesystem. There is no `/bin/bash` and no child processes, which has one consequence worth designing around:

> **`bash` cannot run other programs.** No `python`, `node`, `git`, `curl`-the-binary, or package managers, and nothing can be installed. Only the interpreter's own built-ins (`ls`, `cat`, `sed`, `awk`, `grep`, `curl`, and the usual shell constructs) are available.

Two things follow:

- **To run code, use the [`deno` tool](#running-code-with-the-deno-tool)** — that is what it is for. Do not write a prompt that tells the agent to "run a Python script".
- **`curl` is a built-in of the interpreter, not the binary**, and its egress obeys `allowNet`/`allowNetList`/`denyNetList`. With `allowNet` off (the default) there is no network at all and `curl` reports "command not found".

## Running Code with the deno Tool

Set `enableDenoTool: true` and the agent gains a `deno` tool that executes a TypeScript or JavaScript file from its workspace. This is how an agent runs code it has written — `bash` cannot.

```yaml
options:
  prompt: Compute the churn rate from data.csv and write result.json
  enableDenoTool: true
```

The agent writes the script with `write`/`edit`, then calls `deno` with a path:

```json
{ "path": "analyze.ts", "args": ["--verbose"] }
```

`path` is relative to the working directory and must stay inside the workspace; `args` is optional and arrives as `Deno.args`. The tool returns the script's stdout and stderr (truncated at 50KB); a non-zero exit comes back as an error with the diagnostics attached, so the agent can read its own stack trace and fix the script.

**The file runs as a module.** Top-level code and top-level `await` execute, but `import.meta.main` is **false** — a script shaped like a CLI (`if (import.meta.main) { main() }`) does nothing and reports success. Put the work at the top level, or call `main()` unconditionally.

**Imports must stay inside the workspace too.** A script may import other files it wrote (`./helper.ts`, `./lib/parse.ts`), but an import that resolves outside the workspace is refused and the script does not run — including one that reaches out through a symlink. Split multi-file scripts within the workspace rather than pointing at anything beyond it.

**What scripts can use:**

| | |
|---|---|
| ✅ Deno and Web built-ins | `fetch`, `crypto`, streams, `Deno.readTextFile`, TypeScript types |
| ✅ `node:` standard modules | `node:crypto`, `node:path`, `node:fs`, … |
| ⚠️ `npm:`, `jsr:`, `https:` imports | **Treat as unavailable.** Nothing can be downloaded or installed — only a version already cached in the runtime image resolves, and which those are is an implementation detail you should not rely on |

**Sandbox.** Scripts run under the same permissions as the agent's other tools — the workspace and scratch directory only, the same `allowNet`/`allowNetList`/`denyNetList` policy, your `options.env` variables, and no ability to spawn further programs. Enabling the tool does not widen what the agent can reach; it only lets it execute code within those bounds.

**Notes:**

- A run that would outlast the current segment is terminated and reported as such. Unlike an interrupted actor/MCP tool call it does **not** resume — the agent re-runs it after the boundary, so keep scripts restartable and check for partially written files.
- A single run is also capped by a per-call timeout, and output over 50KB is truncated from the middle (the start and the end are kept, so a failing script's stack trace survives).
- Scripts are subject to the same at-least-once retry semantics as bash (see [Limitations](#limitations)), so keep external side effects idempotent.
- `deno` respects `allowedTools`/`disallowedTools`. If you set an `allowedTools` list, it must include `deno` or the tool stays absent even with `enableDenoTool: true`.

## Connecting BorgIQ Tools with aiAgentToolActorIds

The `aiAgentToolActorIds` array is the mechanism to give the agent BorgIQ actors as tools, unchanged from the legacy agent.

**Location:** `configuration.aiAgentToolActorIds` (sibling to `inputs` and `options`, NOT inside `options`)

**CRITICAL:** To give an agent access to multiple tools, you MUST list ALL tool actor IDs in this array:

```yaml
configuration:
  inputs:
    topic: ''
  options:
    model: claude-sonnet-4-6
    # ... other options
  aiAgentToolActorIds:
    - ACTR01tool1  # First tool
    - ACTR01tool2  # Second tool
    - ACTR01tool3  # Third tool (add as many as needed)
```

### Key Rules

1. **All tools must be listed** — every tool the agent should access must have its actor ID in this array
2. **Order doesn't matter** — the agent selects tools based on their descriptions and schemas, not array order
3. **Location is critical** — `aiAgentToolActorIds` is a sibling to `inputs` and `options`, NOT nested inside `options`
4. **Names must not collide with built-ins** — a tool actor whose `msgVar` is `read`, `write`, `edit`, `bash`, `grep`, `find`, `ls`, or `deno` fails validation
5. **Tool actors are rendered inside the agent's boundary in the UI** and have **empty edges** — their output flows back to the agent

### Tool Actor Input Pattern

Tool actors receive input from the agent using the `${{aiInput}}` placeholder. The placement depends on the actor type:

**HttpRequestActor, DenoActor, PythonActor** — use `${{aiInput}}` in `configuration.inputs`:

```yaml
ACTR01httptool:
  type: HttpRequestActor
  msgVar: my_tool  # This becomes the tool name
  configuration:
    inputs:
      query: ${{aiInput}}      # Receives 'query' from agent's tool call
      limit: ${{aiInput}}      # Receives 'limit' from agent's tool call
    options:
      url: https://api.example.com/search
      body:
        q: ${{ inputs.query }}
        max: ${{ inputs.limit }}
```

**CallFlowActor** — use `${{aiInput}}` in `configuration.options.payload` (NOT in inputs):

```yaml
ACTR01callflowtool:
  type: CallFlowActor
  msgVar: sub_agent  # This becomes the tool name
  configuration:
    options:
      workspaceSlug: my-workspace
      canvasSlug: my-flow
      callableTriggerActorId: ACTR01trigger
      payload:
        query: ${{aiInput}}    # Receives 'query' from agent's tool call
        options: ${{aiInput}}  # Receives 'options' from agent's tool call
      waitForResponse: true
```

The agent calls tools using the `msgVar` as the tool name and passes parameters that match the tool's input schema.

### Tool Actor Types

Any BorgIQ actor can be used as a tool:

| Actor Type | Use Case |
|------------|----------|
| **HttpRequestActor** | API calls, web requests |
| **DenoActor** | Custom TypeScript/JavaScript logic |
| **PythonActor** | Custom Python logic, data science |
| **CallFlowActor** | Sub-agents, complex workflows |

### Tool Schema Definition

Each tool actor must define its input schema in `schemas.inputs` to tell the agent what parameters it accepts:

```yaml
schemas:
  inputs:
    type: object
    properties:
      query:
        type: string
        title: Search Query
        description: The search query to execute
      limit:
        type: integer
        title: Result Limit
        description: Maximum number of results to return
        default: 10
    required:
      - query
```

## Tool Actor Configuration

Tool actors have a specific structure. Key requirements:
- **edges must be empty** — tool output flows back to the agent
- **inputs use `${{aiInput}}`** — to receive values from the agent's tool calls
- **continueOnError: true** is recommended — so the agent can handle failures gracefully
- **msgVar must not be a built-in tool name** (`read`/`write`/`edit`/`bash`/`grep`/`find`/`ls`/`deno`)

```yaml
ACTR01toolactor:
  type: HttpRequestActor
  version: 1
  name: Exa Search
  msgVar: exa_search  # This becomes the tool name the agent uses
  description: Search the web using Exa API
  isActive: true
  continueOnError: true  # Recommended: let agent handle errors
  enableLTM: false
  enableSTM: false
  sourcePorts:
    - id: SPRTdefault
  configuration:
    inputs:
      query: ${{aiInput}}  # Receives 'query' from agent's tool call
      limit: ${{aiInput}}  # Receives 'limit' from agent's tool call
    options:
      url: https://api.exa.ai/search
      method: POST
      headers:
        Content-Type: application/json
      body:
        query: ${{ inputs.query }}
        type: neural
        numResults: ${{ inputs.limit || 10 }}
      auth: ${{ connection.auth }}
    connection:
      key: exa-api
  schemas:
    inputs:
      type: object
      properties:
        query:
          type: string
          title: Search Query
          description: The search query to execute
        limit:
          type: integer
          title: Result Limit
          description: Maximum number of results to return
          default: 10
      required:
        - query
  id: ACTR01toolactor
  position:
    x: 0
    'y': 100
  edges: {}  # IMPORTANT: Empty edges for tool actors
```

## Results Object

### Done Port Result

```typescript
interface AiAgentActorResult {
  sessionId: string;          // Session ID (reuse to continue the session)
  success: boolean;
  result?: string;            // Final assistant message or error message
  outputZipFile?: BIQFile;    // Workspace zip (when returnOutputZipFile !== false)
  sessionDataFile?: BIQFile;  // pi session data zip (when returnSessionDataFile !== false)
  meta: {
    endReason: 'completed' | 'timeout' | 'error' | 'max-loop-count';
    model?: string;
    segments?: number;        // Serverless segments the run spanned
  };
}
```

### Status Port Result

```typescript
type AiAgentStatusPortResult =
  | {
      type: 'ai-agent-loop';
      response: string;
      toolCalls?: AiToolCall[] | null;
      meta: { cwd: string; timestamp: number };
    }
  | {
      type: 'tool-result';
      toolCallId: string;
      toolName: string;
      output: AiToolMessageOutput;
      isError?: boolean;
      meta: { cwd: string; timestamp: number };
    };
```

## Available Models

`model` accepts any `AiAgentModels` value — a curated cross-provider list of models proficient at agentic tool use. The workspace must have an AI credential configured for the chosen model's provider (the run fails fast otherwise).

**Default:** `claude-sonnet-4-6`.

| Provider | Models |
|----------|--------|
| Anthropic | `claude-sonnet-4-6` (default), `claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`, `claude-sonnet-4-5`, `claude-haiku-4-5`, `claude-opus-4-5` |
| OpenAI | `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.2`, `gpt-5.1`, `gpt-5`, `gpt-5-mini` |
| Google | `gemini-3.1-pro-preview`, `gemini-3.5-flash`, `gemini-3.1-flash-lite`, `gemini-2.5-pro` |
| xAI | `grok-4.3`, `grok-4-fast-reasoning`, `grok-code-fast-1` |

For complex multi-step tasks, prefer `claude-opus-4-8` or `claude-sonnet-4-6`. For simple high-volume agents, `claude-haiku-4-5` or `gpt-5-mini` keep costs down.

## Sessions and Continuation

- **Starting**: leave `sessionId` empty to auto-generate one (returned on the done port), or set a custom ID (max 64 chars).
- **Continuing**: re-invoke the actor with the same `sessionId` — the workspace and full conversation state restore from the last checkpoint and the agent picks up where it left off. Works within a flow (loop back into the agent) and across flowruns.
- **Session TTL**: 7 days, sliding — every session activity refreshes it. After the TTL lapses, the same `sessionId` starts a **clean fresh session** (deterministic; never a partial state).
- **Seeding files**: `volumeZipFile` is extracted into the workspace **at session creation only** — it does not re-apply on continuation.
- **Getting files out**: the done port carries `outputZipFile` (the workspace) and `sessionDataFile` (pi session data; portable — it can seed a harness-tier pi session).
- **Scope**: sessions are scoped to the actor instance (not shared across actors) and bound to the runtime they started on — repointing the actor at a different runtime starts fresh sessions.

## Runtime Requirements

The agent runs on the workspace's serverless runtime (or a per-actor runtime override), and two runtime settings directly shape agent behavior:

- **Ephemeral storage sizes the workspace.** The durable workspace is capped at **20% of the runtime's ephemeral storage**. The 512 MB default yields only ~100 MB of workspace — **provision a runtime with ≥ 4 GB ephemeral storage (~800 MB workspace) for real agent work**. Exceeding the cap ends the session with `endReason: 'error'` (state is snapshotted first); a follow-up invoke with a cleanup prompt starts in a grace mode that lets the agent delete files before the cap re-enforces.
- **The runtime timeout is the segment length**, not the session limit. Each segment is bounded by the runtime's configured timeout (up to 14 minutes); the session checkpoints and continues across segments, so total runtime is governed by `timeoutInMinutes`, not the runtime timeout. Short runtime timeouts still work — they just checkpoint more often.
- **AI credential**: the workspace needs an AI credential for the chosen model's provider.
- **Isolation**: agent segments share the workspace runtime's concurrency pool. For isolation, create a dedicated runtime and point the actor at it via the per-actor runtime setting.

## MCP Servers

The agent can call tools from MCP servers alongside its built-ins and any wired BorgIQ actor tools.
Two kinds are supported — stdio subprocess servers are not (use AgentHarnessActor for those).

```yaml
options:
  prompt: Summarise this week's open issues.
  mcpServers:
    # A remote MCP server, proxied through BorgIQ. Auth resolves per request, so an
    # OAuth-backed connection refreshes mid-session without restarting the agent.
    - type: http
      name: linear
      url: https://mcp.linear.app/mcp
      auth: ${{ credentials.linearMcp }}

    # An McpServerActor elsewhere in BorgIQ. No auth and no URL — the agent's session is
    # already scoped to exactly the servers listed here. Slugs default to this actor's
    # own workspace/canvas.
    - type: borgiq
      name: support-tools
      actorId: ACTR01mcpserveractorid00000000
      canvasSlug: support-desk        # optional
      workspaceSlug: otherws          # optional
```

| Field | Applies to | Required | Description |
|-------|-----------|----------|-------------|
| `type` | both | no on `http` (the default), **yes** on `borgiq` | `http` or `borgiq` |
| `name` | both | yes | Tool namespace for this server. Letters, numbers, hyphens and underscores; must be unique across the list |
| `url` | `http` | yes | The MCP server endpoint |
| `transport` | `http` | no | Only `streamable-http` is supported |
| `auth` | `http` | no | Credential for the upstream server, usually `${{ credentials.<key> }}` |
| `actorId` | `borgiq` | yes | The McpServerActor to expose |
| `canvasSlug` | `borgiq` | no | Canvas holding that actor; defaults to this actor's canvas |
| `workspaceSlug` | `borgiq` | no | Workspace holding that canvas; defaults to this actor's workspace |

Notes:

- A `borgiq` entry **must** carry `type: borgiq`. Omitting `type` means `http`, which is what a
  legacy entry without a discriminant is treated as.
- Internal MCP calls are depth-limited, so an agent and an MCP server that call each other in a loop
  terminate with a tool error rather than running away.
- **Protocol versions are negotiated automatically.** The agent speaks MCP `2026-07-28` (the
  stateless core) where the upstream server supports it, and falls back to the older `initialize`
  handshake where it does not. Nothing to configure; a server on either protocol works.
- **The agent cannot answer input requests.** It runs headless inside a flow, with no user to
  prompt, so it declares no `elicitation` / `sampling` / `roots` capability. A server that requires
  one of those to complete a call will report that it cannot proceed rather than hanging. Use an
  AgentHarnessActor if you need a harness CLI that can.
- A tool that declares an `outputSchema` has its structured result passed through to the model as
  structured data, not flattened to text.

## Limitations

- **Bash side effects are at-least-once.** If a segment dies before its checkpoint, the session retries from the previous checkpoint and re-runs any bash executed since then. The workspace state stays consistent (it always restores from the checkpoint), but **external** side effects from bash (API calls, emails) may repeat — design them to be idempotent, as with webhook deliveries elsewhere in the platform.
- **No background processes.** Daemons/dev-servers started by bash do not survive a segment boundary. Long-running listeners belong on the harness tier.
- **No stdio MCP servers** — `type: http` (an external server, proxied through BorgIQ) and `type: borgiq` (an MCP Server Actor inside BorgIQ, dispatched in-process with no transport) are supported; stdio subprocess servers are not. Use AgentHarnessActor when you need a stdio server.
- **`bash` cannot run programs** — it is an in-process interpreter, so `python`/`node`/`git` and installing anything are out. Use the [`deno` tool](#running-code-with-the-deno-tool) to run code. No PTY, no interactive programs.
- **Workspace size cap** — 20% of runtime ephemeral storage (see [Runtime Requirements](#runtime-requirements)).

## Common Patterns

### File-Processing Agent

```yaml
options:
  model: claude-sonnet-4-6
  systemPrompt: |
    You are a data processor. The input archive is extracted in your workspace.
    Produce results as files; your workspace is returned to the caller as a zip.
  prompt: ${{ inputs.instructions }}
  volumeZipFile: ${{ inputs.archive }}
```

### Continuable Session (multi-invoke conversation)

```yaml
# First invoke: auto-generated sessionId comes back on the done port.
# Later invokes: pass it back to continue with full workspace + conversation state.
options:
  model: claude-sonnet-4-6
  prompt: ${{ inputs.followUpInstruction }}
  sessionId: ${{ inputs.sessionId }}   # empty on first call, set on follow-ups
```

### Read-Only Analysis Agent

```yaml
options:
  model: claude-haiku-4-5
  prompt: ${{ inputs.question }}
  volumeZipFile: ${{ inputs.dataZip }}
  disallowedTools:
    - write
    - edit
    - bash
  returnOutputZipFile: false   # nothing to return; skip the zip
```

### Research Agent with Web Search Tools

```yaml
options:
  model: claude-sonnet-4-6
  systemPrompt: |
    You are a research assistant. Use the available tools:
    - web_search: Search for information on the web
    - extract_content: Extract detailed content from URLs
    Save findings as markdown files in your workspace.
  prompt: ${{ inputs.researchQuestion }}
# aiAgentToolActorIds (sibling of options) lists the two HttpRequestActor tools
```

### Sub-Agent Pattern (Agent-as-Tool)

Use CallFlowActor to invoke sub-agents. Note: use `${{aiInput}}` inside `payload`, not in `inputs`:

```yaml
ACTR01subagent:
  type: CallFlowActor
  name: Research Sub Agent
  msgVar: research_sub_agent
  description: Sub-agent specialized in web research
  configuration:
    options:
      workspaceSlug: my-workspace
      canvasSlug: research-agent-flow
      callableTriggerActorId: ACTR01kcddpqxsakc25fn5c0hz9a35
      payload:
        topic: ${{aiInput}}  # Receives value from agent
      waitForResponse: true
      timeoutInSeconds: 120
  schemas:
    inputs:
      type: object
      properties:
        topic:
          type: string
          title: Research Topic
          description: Topic for the sub-agent to research
      required:
        - topic
  edges: {}  # Empty for tool actors
```

## Complete Example: Report Processing Agent

An agent that receives a zip of CSV reports, analyzes them in its workspace, publishes a summary through a wired HTTP tool, and returns the processed workspace:

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  # Main Agent
  ACTR01kd6agent00000000000000000:
    type: AiAgentActor
    version: 1
    name: Report Processing Agent
    msgVar: report_agent
    description: Unpacks report archives, analyzes them, and publishes a summary
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdone000
        name: Done
      - id: SPRTdefault
        name: Status
    configuration:
      inputs:
        reportZip: ${{ msg.upload_trigger.file }}
        period: ${{ msg.upload_trigger.period }}
      options:
        model: claude-sonnet-4-6
        systemPrompt: |
          You are a data analyst. The report archive is extracted in your
          workspace. Analyze the CSVs — use bash built-ins for simple passes,
          and for real computation write a TypeScript file and run it with the
          deno tool. Write summary.md with your findings, and publish the
          summary using the publish_summary tool.
        prompt: |
          Analyze the ${{ inputs.period }} reports in the workspace,
          write summary.md, and publish it.
        volumeZipFile: ${{ inputs.reportZip }}
        enableDenoTool: true    # the agent runs TypeScript to crunch the CSVs
        timeoutInMinutes: 30
      # IMPORTANT: List ALL tool actor IDs here
      aiAgentToolActorIds:
        - ACTR01kd6publish000000000000000   # publish_summary
    schemas:
      inputs:
        type: object
        properties:
          reportZip:
            type: object
            title: Report Zip
            description: The report archive to analyze
          period:
            type: string
            title: Reporting Period
            description: e.g. 2026-Q2
        required:
          - period
    id: ACTR01kd6agent00000000000000000
    position:
      x: 0
      'y': 0
    edges:
      SPRTdone000:
        - target: ACTR01kd6notify0000000000000000

  # Tool: publish summary via internal API
  ACTR01kd6publish000000000000000:
    type: HttpRequestActor
    version: 1
    name: Publish Summary
    msgVar: publish_summary
    description: Publish a report summary to the internal reporting API
    isActive: true
    continueOnError: true  # Let agent handle errors
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        title: ${{aiInput}}    # Receives 'title' from agent's tool call
        summary: ${{aiInput}}  # Receives 'summary' from agent's tool call
      options:
        url: https://reports.internal.example.com/api/summaries
        method: POST
        headers:
          Content-Type: application/json
        body:
          title: ${{ inputs.title }}
          summary: ${{ inputs.summary }}
        auth: ${{ connection.auth }}
      connection:
        key: reporting-api
    schemas:
      inputs:
        type: object
        properties:
          title:
            type: string
            title: Summary Title
            description: Title for the published summary
          summary:
            type: string
            title: Summary Body
            description: Markdown body of the summary
        required:
          - title
          - summary
    id: ACTR01kd6publish000000000000000
    position:
      x: -200
      'y': 100
    edges: {}  # IMPORTANT: Empty edges for tool actors

  # Downstream: notify with the final result + workspace zip
  ACTR01kd6notify0000000000000000:
    type: SendEmailActor
    version: 1
    name: Notify Analyst
    msgVar: notify_analyst
    description: Email the final summary and workspace zip link
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        agentResult: ${{ msg.report_agent.result }}
        endReason: ${{ msg.report_agent.meta.endReason }}
      options:
        to: analyst@example.com
        subject: 'Report analysis: ${{ inputs.endReason }}'
        body: ${{ inputs.agentResult }}
    id: ACTR01kd6notify0000000000000000
    position:
      x: 0
      'y': 200
    edges: {}
```

## Accessing Agent Data in Downstream Actors

### From Done Port (final result)

```yaml
configuration:
  inputs:
    finalText: ${{ msg.report_agent.result }}
    succeeded: ${{ msg.report_agent.success }}
    endReason: ${{ msg.report_agent.meta.endReason }}
    workspaceZip: ${{ msg.report_agent.outputZipFile }}
    sessionId: ${{ msg.report_agent.sessionId }}   # store to continue the session later
```

`result` can be absent (e.g. some error paths) — guard with a fallback where it matters:

```yaml
    finalText: ${{ msg.report_agent.result || 'agent ended: ' + msg.report_agent.meta.endReason }}
```

### From Status Port (intermediate results)

Connect to the Status port to process assistant turns and tool results in real time:

```yaml
configuration:
  options:
    action: inject
    payload:
      eventType: ${{ msg.report_agent.type }}
      content: ${{ msg.report_agent.type === 'ai-agent-loop' ? msg.report_agent.response : msg.report_agent.output }}
```

## Migrating from DeprecatedAiAgent

Existing flows built on the legacy loop agent keep running as `DeprecatedAiAgent`. When rebuilding one on the new actor:

| Legacy option | Replacement |
|---------------|-------------|
| `temperature`, `maxTokens`, `enableTodoTool` | Removed — no equivalent (the agent manages its own generation and planning) |
| `messages` (multi-turn history) | Use `sessionId` continuation — re-invoke the same session instead of replaying message arrays |
| `prompt` / `systemPrompt` / `maxLoopCount` | Same names, same intent |
| `model: gpt-4.1-nano` (legacy default) | Pick an agent-grade model; default is `claude-sonnet-4-6` |

Output contract changes for downstream actors:

| Legacy done port | New done port |
|------------------|---------------|
| `response` (full `BIQAiMessage[]` history) | `result` (final text only). Conversation history lives in the session, not the payload |
| `meta.endReason: done \| max_loop_count_reached \| max_output` | `meta.endReason: completed \| timeout \| error \| max-loop-count` |
| `meta.usage` (token totals) | Not on the done port — usage is metered to the workspace AI log |
| — | New: `sessionId`, `success`, `outputZipFile`, `sessionDataFile`, `meta.segments` |

Tool wiring (`aiAgentToolActorIds`, `${{aiInput}}`, tool schemas) is unchanged — tool actors migrate as-is, unless their `msgVar` collides with a built-in tool name (`read`/`write`/`edit`/`bash`/`grep`/`find`/`ls`/`deno`), which now requires a rename.

See [deprecated-ai-agent.md](deprecated-ai-agent.md) for the full legacy reference.

## Use Cases

### File & Data Processing

Unpack archives, transform data, edit files, and return the workspace — the built-in tools cover the whole loop without any custom tool actors. Enable `enableDenoTool` when the transformation needs real code rather than bash built-ins.

### Code Generation & Execution

Write code, run it, read the output, and iterate — set `enableDenoTool: true` and the agent can execute what it writes.

### Research & Information Gathering

Wire web-search/HTTP tool actors; the agent searches, extracts, and synthesizes findings into workspace files.

### Long-Running / Resumable Work

Sessions checkpoint automatically and continue via `sessionId` — a task can span many invocations, or a conversation can resume days later (within the 7-day TTL).

### Multi-Agent Systems

Compose agents hierarchically using CallFlowActor tools to create specialized sub-agents.

## Best Practices

1. **Size the runtime for the workspace** — ≥ 4 GB ephemeral storage for real file work; the workspace cap is 20% of ephemeral storage
2. **Use agent-grade models** — default `claude-sonnet-4-6`; step up to `claude-opus-4-8` for complex multi-step tasks
3. **Make bash side effects idempotent** — bash is at-least-once across segment retries; external calls (APIs, emails) may repeat
4. **Prefer built-in tools for file work** — don't wire file-system tool actors; the agent already has `read`/`write`/`edit`/`bash`
5. **Define clear tool schemas** — the agent uses tool descriptions and schemas to decide when and how to call wired tools
6. **Handle tool errors** — set `continueOnError: true` on tool actors so the agent can recover from failures
7. **Restrict tools when you can** — `disallowedTools` for read-only agents; `denyNetList`/`allowNetList` for tool-runtime egress (remember bash is not constrained)
8. **Store `sessionId` when you need continuation** — persist it (e.g. in a Collection) to resume the session in a later flowrun
9. **Guard `result` downstream** — it is optional; branch on `success`/`meta.endReason` for control flow

## TypeScript Schema Hint

See [typescript/actor-schemas-task-core.md](typescript/actor-schemas-task-core.md) for the complete TypeScript definitions of AiAgentActor options and result schemas (`actorSchemas/task/aiAgent` section).
