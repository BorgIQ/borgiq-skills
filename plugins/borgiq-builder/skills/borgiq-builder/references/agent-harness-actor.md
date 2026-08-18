# Agent Harness Actor Reference

The AgentHarnessActor is **Claude in a Box** — it packages Claude Code into a workflow node so that any business process codified as Claude Code commands or skills can run as an actor in a BorgIQ automation. Instead of scripting each step imperatively, you describe what you want done in a prompt, and Claude Code executes it in an isolated sandbox (E2B or Daytona) with full filesystem access, code execution, and session persistence.

**The core idea:** If a task can be done by a human sitting at a terminal running Claude Code — writing code, running commands, installing packages, calling APIs, using slash commands — then AgentHarnessActor can do that same task as a node in a workflow, triggered by upstream actors and feeding results to downstream actors.

## Table of Contents

- [Overview](#overview)
- [Key Differences from AiAgentActor](#key-differences-from-aiagentactor)
- [When to Use AgentHarnessActor vs AiAgentActor](#when-to-use-agentharnessactor-vs-aiagentactor)
- [The "Claude in a Box" Pattern](#the-claude-in-a-box-pattern)
- [Configuration Structure](#configuration-structure)
- [Source Ports](#source-ports)
- [Options Reference](#options-reference)
- [Sandbox Providers](#sandbox-providers)
- [Sandbox Architecture](#sandbox-architecture)
- [Network Control](#network-control)
- [Session Continuation](#session-continuation)
- [MCP Servers](#mcp-servers)
- [Connecting Tools](#connecting-tools)
- [Volume Zip File and Working Directory](#volume-zip-file-and-working-directory)
- [Building Context with a DenoActor](#building-context-with-a-denoactor)
- [Extracting Output Files](#extracting-output-files)
- [Results Object](#results-object)
- [Credentials and Environment Variables](#secrets-and-environment-variables)
- [Common Patterns](#common-patterns)
- [Complete Example: Deep Research Agent with Context Building](#complete-example-deep-research-agent-with-context-building)
- [Accessing Agent Harness Data in Downstream Actors](#accessing-agent-harness-data-in-downstream-actors)
- [Use Cases](#use-cases)
- [Best Practices](#best-practices)
- [TypeScript Schema Hint](#typescript-schema-hint)

## Overview

AgentHarnessActor creates an isolated sandbox (via an external vendor — E2B or Daytona, **not** AWS Lambda) where Claude Code runs with:

- **Full filesystem access**: Read, write, create, delete files
- **Command execution**: Run Bash commands, scripts, install packages
- **Session persistence**: Reuse sessions via `sessionId` — the sandbox state and Claude conversation history are restored
- **Queued execution**: When a session ID is reused, inbound messages are processed one at a time using a Redis-backed queue with mutex locking
- **Connected BorgIQ tools**: Tool actors are exposed as Claude Code skills via an auto-generated BorgIQ plugin
- **MCP server support**: remote servers proxied through BorgIQ, MCP Server Actors inside BorgIQ, and stdio subprocess servers
- **Network isolation**: Fine-grained allow/deny lists enforced via iptables firewall
- **Output artifacts**: Returns workspace zip and Claude session data zip

### Execution Flow

1. A sandbox is provisioned (E2B or Daytona)
2. `volumeZipFile` (if provided) is extracted to `~/workspace/`
3. Claude Code starts in the working directory with the given prompt
4. Claude executes commands, writes files, calls tools as needed
5. On completion, the workspace is zipped and returned as `outputZipFile`
6. The Claude session data (`~/.claude`) is returned as `claudeSessionDataFile`
7. The sandbox remains hot for 5 minutes for fast continuation, then shuts down

## Key Differences from AiAgentActor

> Both actors are now coding agents with a workspace, bash, sessions, and BorgIQ actor tools. AiAgentActor runs a pi coding agent in checkpointed serverless segments; AgentHarnessActor runs Claude Code in a full sandbox VM. See [ai-agent-actor.md](ai-agent-actor.md) for the AI Agent's own reference (and [deprecated-ai-agent.md](deprecated-ai-agent.md) if you're looking at the pre-2026 loop agent this table used to compare against).

| Aspect | AiAgentActor | AgentHarnessActor |
|--------|-------------|-------------------|
| **Runtime** | Serverless segments on the workspace runtime (checkpointed) | Isolated sandbox VM (E2B or Daytona) |
| **Harness** | pi coding agent | Claude Code (skills, slash commands, plugins) |
| **Code execution** | Built-in `read`/`write`/`edit`/`bash`/`grep`/`find`/`ls` against a private workspace, plus an opt-in `deno` tool (`enableDenoTool`) that runs workspace TypeScript/JavaScript; no package installs | Full machine: Bash, file I/O, package installs, PTY |
| **Startup latency** | Low (serverless invoke; cold restore adds seconds) | Sandbox provision + harness install (tens of seconds to minutes) |
| **Session reuse** | `sessionId` + checkpoint restore (7-day sliding TTL) | `sessionId` + sandbox/session zips, queued messages |
| **Background processes** | Not supported (nothing survives a segment boundary) | Supported within sandbox lifetime |
| **Network control** | Deno-level allow/deny lists across the whole tool runtime, bash included | Fine-grained allow/deny lists enforced with iptables |
| **MCP servers** | Remote (`type: http`) + BorgIQ (`type: borgiq`) | Those two plus stdio subprocess servers |
| **Output artifacts** | Final text + workspace zip + pi session data zip | Final text + workspace zip + Claude session data zip |
| **Environment vars** | Supported (encrypted in transit; reserved names rejected) | Full support (encrypted in transit) |
| **Tools** | Built-ins + BorgIQ actors via `aiAgentToolActorIds` | Claude Code built-in tools + BorgIQ actors + MCP servers |
| **Timeout** | `timeoutInMinutes` across segments (default 30); no per-invocation wall-clock cap | Explicit timeout in minutes (default 15) |
| **Cost model** | Serverless billing on the workspace runtime | Sandbox VM wall-clock billing |

## When to Use AgentHarnessActor vs AiAgentActor

| Scenario | Recommended Actor |
|----------|-------------------|
| File/data processing, scripting, code-run-iterate loops | **AiAgentActor** |
| Orchestrate BorgIQ tool actors (API calls, sub-flows) | **AiAgentActor** |
| Multi-turn sessions with persistent workspace | Either — both support `sessionId` continuation |
| Claude Code skills / slash commands / plugins | **AgentHarnessActor** |
| Need a stdio MCP server or custom CLI tools | **AgentHarnessActor** |
| Background processes (dev servers, daemons) | **AgentHarnessActor** |
| Firewall-enforced network isolation for all processes | **AgentHarnessActor** |
| Heavy environments (large installs, big builds) | **AgentHarnessActor** |
| Cost-sensitive / minimize startup latency | **AiAgentActor** |

Rule of thumb: start with AiAgentActor; step up to AgentHarnessActor when you need Claude Code itself, stdio MCP servers, daemons, or a full VM.

## The "Claude in a Box" Pattern

The power of AgentHarnessActor is that **any business process you can codify as Claude Code commands or skills becomes a reusable workflow node**. This inverts the traditional automation approach:

- **Traditional:** Write imperative code for every step (parse this, transform that, call this API, format the output)
- **Claude in a Box:** Describe the outcome, supply the right context (skills, CLAUDE.md, input files), and let Claude Code figure out the steps

### How It Works

1. **Codify the process** — Create Claude Code skills (slash commands, CLAUDE.md instructions, reference files) that encode your business logic, conventions, and domain knowledge
2. **Package as context** — Use a `volumeZipFile` to deliver those skills, instructions, and input data into the sandbox workspace
3. **Prompt the outcome** — The actor's `prompt` describes what needs to be done, referencing the skills available in the workspace
4. **Extract the result** — Downstream actors pull specific output files from the `outputZipFile` or read structured data from the result

### Examples of Codified Business Processes

| Business Process | Claude Code Skill/Command | As a Workflow Node |
|-----------------|--------------------------|-------------------|
| Code review against team standards | `/review` skill with team conventions in CLAUDE.md | PR webhook → AgentHarness runs review → posts comments |
| Generate API client from OpenAPI spec | `/generate-client` skill with language templates | Spec file uploaded → AgentHarness generates code → zip output |
| Data migration between schemas | Migration skill with schema mappings | Scheduled trigger → AgentHarness runs migration → reports results |
| Security audit of dependencies | `/audit` skill with policy rules | Nightly trigger → AgentHarness audits → sends email report |
| Document generation from structured data | `/generate-report` skill with templates | Data arrives via webhook → AgentHarness generates PDF → stores in collection |
| Competitive analysis research | `/research` skill with search + extraction tools | Button trigger → AgentHarness researches → returns structured findings |

### Why Skills Matter

Without skills, the AgentHarnessActor is a general-purpose Claude Code session — capable but unbounded. With skills loaded into the workspace:

- **Consistency** — The same skill produces the same kind of output every time, regardless of prompt variation
- **Domain encoding** — Business rules, naming conventions, output formats, and quality checks are encoded once and reused
- **Composability** — A skill that works at a terminal works identically as a workflow node — no rewriting required
- **Versioning** — Update the skill zip, and every workflow using it gets the new behavior

### Minimal Pattern

```yaml
# 1. Build context zip with skills and input files
ACTR01context:
  type: DenoActor
  name: Build Context
  msgVar: build_context
  configuration:
    code: |
      import JSZip from "npm:jszip@3.10.1";
      import type { Request, Response } from "@borgiq/actors";
      import { stashFile } from "@borgiq/actors";
      export default async function receive(req: Request): Promise<Response> {
        const zip = new JSZip();
        // Add CLAUDE.md with instructions
        zip.file("CLAUDE.md", "# Instructions\nUse /analyze to process the input data.");
        // Add the skill
        zip.file(".claude/skills/analyze/SKILL.md", req.inputs.skillContent);
        // Add input data
        zip.file("input/data.json", JSON.stringify(req.inputs.data));
        // Generate the zip and stash it to BorgIQ storage (requires allowNet: true)
        const zipBuffer = await zip.generateAsync({ type: "uint8array", compression: "DEFLATE" });
        const contextZip = await stashFile(zipBuffer, "context.zip", "application/zip");
        return { results: { contextZip } };
      }
    options:
      allowNet: true  # required for stashFile

# 2. Run Claude Code with the context
ACTR01agent:
  type: AgentHarnessActor
  name: Run Analysis
  msgVar: run_analysis
  configuration:
    options:
      prompt: "Read the input data in input/data.json and run /analyze on it. Write results to output/results.json."
      volumeZipFile: ${{ msg.build_context.contextZip }}
      maxLoopCount: 50
      sandboxProvider: e2b
```

The key insight: the `prompt` stays simple because the complexity lives in the skills. The skill encodes *how* to analyze; the prompt just says *what* to analyze.

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: AgentHarnessActor
    version: 1
    name: Research Agent
    msgVar: research_agent
    description: Run Claude Code in a sandbox to research and generate reports
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
      options:
        prompt: |
          Research the given topic and write findings to output.md
        model: claude-sonnet-4-6
        systemPrompt: |
          You are a research assistant with access to search tools.
          Always save your findings to files in the workspace.
        sandboxProvider: e2b
        sessionId: ''
        volumeZipFile: ${{ msg.build_context.file }}
        workingDirectory: ''
        timeoutInMinutes: 15
        maxLoopCount: 50
        maxTokens: 16384
        temperature: 1
        allowNet: true
        env:
          API_KEY: ${{ credentials.my_api_key }}
        returnOutputZipFile: true
        returnClaudeSessionDataFile: true
      credentials:
        my_api_key:
          workspaceKey: my-api-key
      aiAgentToolActorIds:
        - ACTR01toolactor1
        - ACTR01toolactor2
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Source Ports

AgentHarnessActor has two source ports:

| Port ID | Name | Description |
|---------|------|-------------|
| `SPRTdone000` | Done | Emits final result when agent completes (success, timeout, or error) |
| `SPRTdefault` | Status | Emits real-time updates during execution |

### Done Port Output

The Done port emits when the agent completes:

```json
{
  "sessionId": "session-abc123",
  "success": true,
  "result": "...",
  "outputZipFile": {
    "id": "file-xyz",
    "name": "workspace-output.zip",
    "mimeType": "application/zip",
    "size": 12345
  },
  "claudeSessionDataFile": {
    "id": "file-abc",
    "name": "claude-session-data.zip",
    "mimeType": "application/zip",
    "size": 6789
  },
  "meta": {
    "endReason": "completed",
    "model": "claude-sonnet-4-20250514",
    "duration": 45000,
    "usage": {
      "promptTokens": 1500,
      "completionTokens": 800,
      "totalTokens": 2300
    }
  }
}
```

| Field | Description |
|-------|-------------|
| `sessionId` | The session ID (auto-generated or the custom ID you provided) |
| `success` | Whether the execution completed successfully |
| `result` | The result text/data from the agent |
| `outputZipFile` | BIQFile reference to the workspace zip (if `returnOutputZipFile` is true) |
| `claudeSessionDataFile` | BIQFile reference to the Claude session data zip (if `returnClaudeSessionDataFile` is true) |
| `meta.endReason` | Why the agent stopped: `completed`, `timeout`, or `error` |
| `meta.model` | The Claude model used |
| `meta.duration` | Total execution time in milliseconds |
| `meta.usage` | Cumulative token usage |

### Status Port Output

The Status port emits real-time updates with five message types:

**Agent Loop (response + tool calls):**

```json
{
  "type": "agent-harness-loop",
  "response": "I'll search for information on this topic using the available tools.",
  "toolCalls": [
    {
      "toolCallId": "toolu_01abc",
      "toolName": "exa_search",
      "input": { "query": "AI trends 2025" }
    }
  ],
  "meta": {
    "cwd": "/home/user/workspace",
    "timestamp": 1711234567890
  }
}
```

**Tool Result:**

```json
{
  "type": "tool-result",
  "toolCallId": "toolu_01abc",
  "toolName": "exa_search",
  "output": { "type": "json", "value": { "results": [...] } },
  "isError": false,
  "meta": { "cwd": "/home/user/workspace", "timestamp": 1711234567891 }
}
```

**Error:**

```json
{
  "type": "agent-harness-error",
  "message": "Sandbox process died unexpectedly",
  "code": "SANDBOX_DIED",
  "meta": { "timestamp": 1711234567892 }
}
```

**Notification:**

```json
{
  "type": "agent-harness-notification",
  "notificationType": "permission_prompt",
  "title": "Permission Required",
  "message": "Claude is requesting permission to install npm packages",
  "meta": { "timestamp": 1711234567893 }
}
```

**Complete:**

```json
{
  "type": "agent-harness-complete",
  "message": "Execution completed successfully",
  "meta": { "timestamp": 1711234567894 }
}
```

## Options Reference

### Required

| Option | Type | Description |
|--------|------|-------------|
| `prompt` | string | The task instruction sent to Claude Code. This is the main directive. |

### Optional

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `harness` | `claude` \| `codex` \| `opencode` \| `pi` | `claude` | The agent harness CLI to run in the sandbox. Use the exact lowercase string value (e.g. `claude`, not `Claude` or `BIQAgentHarnessType.Claude`). `model` must be one valid for the selected harness. |
| `model` | string | `claude-sonnet-4-20250514` | The model to use in the agent harness. Must be valid for the selected `harness`; defaults to that harness's default model. For the default `claude` harness, a Claude model (Sonnet, Opus, or Haiku variants). |
| `systemPrompt` | string | - | Additional context/instructions for Claude Code |
| `sandboxProvider` | `e2b` \| `daytona` | `e2b` | The sandbox infrastructure provider |
| `sessionId` | string | auto-generated | Session ID to continue or create (max 64 characters) |
| `volumeZipFile` | BIQFile | - | Zip file to extract into `~/workspace/` |
| `workingDirectory` | string | - | Working directory relative to workspace (e.g., `my-project`) |
| `timeoutInMinutes` | integer | `15` | Maximum execution time before session is terminated |
| `maxLoopCount` | integer | unlimited | Maximum number of agentic loops (tool calls) |
| `maxTokens` | integer | `16384` | Maximum tokens per Claude response |
| `temperature` | number | `1` | Creativity level (0-1, lower = more deterministic) |
| `allowedTools` | string[] | all tools | Whitelist specific Claude Code tools (empty = all allowed) |
| `disallowedTools` | string[] | - | Blacklist specific Claude Code tools |
| `allowNet` | boolean | `true` | Allow outbound network access from sandbox |
| `allowNetList` | string[] | - | Whitelist hosts/CIDRs (only when `allowNet: false`) |
| `denyNetList` | string[] | - | Blacklist hosts/CIDRs (even when `allowNet: true`) |
| `mcpServers` | object[] | - | MCP servers: `type: http` (remote, proxied), `type: borgiq` (an MCP Server Actor), `type: stdio` (subprocess) |
| `env` | object | - | Environment variables (encrypted in transit) |
| `returnOutputZipFile` | boolean | `true` | Include workspace zip in done port result |
| `returnClaudeSessionDataFile` | boolean | `true` | Include Claude session data zip in done port result |

### aiAgentToolActorIds (for connected tools)

| Field | Type | Description |
|-------|------|-------------|
| `aiAgentToolActorIds` | array | Array of actor IDs that Claude can use as tools in the sandbox |

**Location:** `configuration.aiAgentToolActorIds` (sibling to `options`, NOT inside `options`)

Connected tools are exposed as Claude Code skills via the auto-generated BorgIQ plugin in `~/borgiq-plugin/`.

## Sandbox Providers

### E2B (Default)

- **Full internet access** by default
- Ubuntu-based environment
- Faster startup time
- Pre-installed: Claude CLI, Node.js 22 LTS, uv, iptables, jq, zip
- Best for: Tasks requiring external resources, npm/pip installs, API integrations

### Daytona

- **Isolated network** by default (no external internet)
- Persistent volumes available
- Best for: Sensitive code processing, internal-only workflows

## Sandbox Architecture

```
$HOME/
├── workspace/                      # Main working directory
│   └── [contents of volumeZipFile] # Your uploaded files are extracted here
│
├── .claude/                        # Claude Code configuration
│   ├── settings.json              # Claude Code settings and hooks
│   ├── projects/                  # Conversation history (for session continuation)
│   └── .credentials.json          # Authentication credentials
│
└── borgiq-plugin/                  # BorgIQ tools plugin (if tools connected)
    ├── .claude-plugin/
    │   └── plugin.json            # Plugin manifest
    ├── scripts/
    │   ├── invoke.sh              # Tool invocation script
    │   └── .env                   # Session credentials
    └── skills/                    # Tool skill definitions
        └── {tool-name}/
            └── SKILL.md           # Tool documentation
```

### How `workingDirectory` Affects Execution

| Scenario | Claude runs from | Output zip contains |
|----------|-----------------|---------------------|
| `workingDirectory` not set | `~/workspace/` | Everything in `~/workspace/` |
| `workingDirectory: "my-project"` | `~/workspace/my-project/` | Everything in `~/workspace/my-project/` |
| `workingDirectory: "/tmp/work"` | `/tmp/work/` | Everything in `/tmp/work/` |

**Key**: `volumeZipFile` always extracts to `~/workspace/` regardless of `workingDirectory`.

## Network Control

| Scenario | Properties | Effect |
|----------|-----------|--------|
| Allow all (default) | `allowNet: true` | Full outbound access |
| Block all outbound | `allowNet: false` | No network except AI provider & BorgIQ API |
| Block all except specific | `allowNet: false`, `allowNetList: ["api.example.com"]` | Only whitelisted hosts |
| Allow all except specific | `allowNet: true`, `denyNetList: ["internal.corp.com"]` | All traffic except blacklisted |

Network rules are enforced via iptables at sandbox launch. System endpoints (AI provider API, BorgIQ API) are always allowed and cannot be denied.

## Session Continuation

### How It Works

1. **First execution** — no `sessionId` provided, auto-generated ID returned in result
2. **Subsequent executions** — pass the `sessionId` to continue the session
3. **Queue pattern** — if a session is already active, the new execution is queued and starts when the current one completes

### Session Lifecycle

1. **Active Execution**: Sandbox runs Claude Code
2. **Hot Duration (5 minutes)**: After completion, sandbox stays alive for fast continuation
3. **Scheduled Shutdown**: Workspace snapshot saved, Claude session data saved, sandbox destroyed, queue drained
4. **Cold Restoration**: New sandbox created, workspace and session data restored from snapshots
5. **Expiration**: Sessions expire after 7 days

### Queuing & Locking

Only one execution can use a session at a time:

- New executions targeting an active session are **queued**
- Queued jobs are processed FIFO when the current execution completes
- Locks have a TTL (timeout + 5 minute buffer) to prevent deadlocks
- Queue operations are atomic via Redis Lua scripts

### Session ID Best Practices

```yaml
# Auto-generated session ID (one-off execution)
sessionId: ''

# Custom session ID for deterministic continuation
sessionId: my-research-session-001

# Dynamic session ID from upstream data
sessionId: ${{ msg.trigger.customerId }}
```

## MCP Servers

Configure MCP servers available to the harness. Three kinds, distinguished by `type`:

```yaml
options:
  mcpServers:
    # Remote server, proxied through BorgIQ. The sandbox only ever receives the
    # BorgIQ gateway URL and its own session token — never the upstream URL or
    # your credentials. Auth resolves per request, so OAuth tokens refresh mid-session.
    - type: http
      name: linear
      url: https://mcp.linear.app/mcp
      auth: ${{ credentials.linearMcp }}

    # An MCP Server Actor elsewhere in BorgIQ. No auth — the agent's session is
    # already scoped to exactly the servers listed here. Slugs default to this
    # actor's own workspace/canvas.
    - type: borgiq
      name: support-tools
      actorId: ACTR01mcpserveractorid00000000   # the McpServerActor on your canvas
      canvasSlug: support-desk        # optional
      workspaceSlug: otherws          # optional

    # Subprocess inside the sandbox. Not supported by the Pi harness.
    - type: stdio
      name: filesystem-server
      command: npx
      args: ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
      env:
        LOG_LEVEL: info
```

Every entry needs a unique `name` (letters, numbers, hyphens, underscores). `type: http`
also requires `url`; `type: borgiq` requires `actorId`; `type: stdio` requires `command`
and treats `args`/`env` as optional. An entry with no `type` is read as stdio, for
back-compat with configs written before remote servers existed.

Protocol versions are the CLI's business, not yours. Each harness ships its own MCP client and
negotiates MCP `2026-07-28` (the stateless core) or the older `initialize` handshake with the
server directly; BorgIQ forwards the traffic without reshaping it. The BorgIQ tool server generated
into the sandbox for Codex and OpenCode serves both, so it works whichever the CLI picks.

Secrets never travel in the clear: stdio `env` values and literal `http` auth values are
encrypted in transit, and connection-backed auth is resolved server-side per request.

## Connecting Tools

Tool actors are connected to AgentHarnessActor via `aiAgentToolActorIds`, exactly like AiAgentActor. Connected tools become Claude Code skills inside the sandbox.

### Tool Invocation Pattern (fire-then-poll)

1. Claude calls a tool via the BorgIQ plugin's `invoke.sh`
2. `invoke.sh` sends `POST /sandbox/invoke-tool` to BorgIQ API
3. BorgIQ queues the tool actor and initializes a pending Redis key
4. `invoke.sh` long-polls `POST /sandbox/poll-tool-result` (25-second intervals)
5. When the tool completes, the result is returned to Claude
6. Default tool timeout: 30 seconds

### Tool Actor Configuration

Tool actors follow the same pattern as AiAgentActor tools:

```yaml
ACTR01toolactor:
  type: HttpRequestActor
  version: 1
  name: Exa Search
  msgVar: exa_search
  description: Search the web using Exa API
  isActive: true
  continueOnError: true
  sourcePorts:
    - id: SPRTdefault
  configuration:
    inputs:
      query: ${{aiInput}}
    options:
      url: https://api.exa.ai/search
      method: POST
      body:
        query: ${{ inputs.query }}
      auth: ${{ connection.auth }}
    connection:
      key: exa
  schemas:
    inputs:
      type: object
      properties:
        query:
          type: string
          description: The search query
      required:
        - query
  edges: {}  # IMPORTANT: Empty edges for tool actors
```

## Volume Zip File and Working Directory

The `volumeZipFile` provides initial files to the sandbox. Common pattern: use a DenoActor to build a context zip containing skills, configuration, and project files, then pass it to the AgentHarnessActor.

### What Goes in the Volume Zip

```
volumeZipFile contents:
├── CLAUDE.md                   # Instructions for Claude Code
├── .claude/
│   └── skills/                 # Claude Code skills
│       └── my-skill/
│           └── SKILL.md
├── inputs/                     # Input files for the task
│   └── data.csv
└── outputs/                    # Directory for Claude to write results
```

### Passing the Volume

```yaml
# From a DenoActor that builds the zip
options:
  volumeZipFile: ${{ msg.build_context.file }}
  workingDirectory: ''  # Claude runs from ~/workspace/ where the zip was extracted
```

## Building Context with a DenoActor

A powerful pattern is using a DenoActor upstream to build a context zip file with skills, CLAUDE.md instructions, and input/output directories. The DenoActor downloads skills from GitHub, creates the directory structure, and returns a zip file via `stashFile()`.

**Key elements of a context-building DenoActor:**

1. **Create CLAUDE.md** at the zip root — this becomes Claude Code's project instructions
2. **Create `.claude/skills/`** — populate with skill directories from GitHub or other sources
3. **Create `inputs/` and `outputs/`** — standard directories for task data
4. **Use `stashFile()`** to upload the zip to BorgIQ storage and return a BIQFile reference
5. **Pass environment variables** via `env` and `secrets` on the AgentHarnessActor for API keys needed by skills

```yaml
# DenoActor builds context, then AgentHarnessActor uses it
# DenoActor -> AgentHarnessActor -> DenoActor (extract output)

# Agent harness receives the zip
ACTR01agent:
  type: AgentHarnessActor
  configuration:
    options:
      prompt: Research the topic and write results to outputs/report.md
      volumeZipFile: ${{ msg.build_context.file }}
      model: claude-sonnet-4-5
      env:
        API_KEY: ${{ credentials.api_key }}
      sessionId: ''
    credentials:
      api_key:
        workspaceKey: my-api-key
    aiAgentToolActorIds: []
```

## Extracting Output Files

After the AgentHarnessActor completes, the `outputZipFile` contains all files in the working directory. Use a downstream DenoActor to extract specific files:

```yaml
# Extract specific files from the output zip
ACTR01extract:
  type: DenoActor
  name: Extract Output
  msgVar: extract_output
  configuration:
    code: |
      import JSZip from "npm:jszip@3.10.1";
      import type { Request, Response } from "@borgiq/actors";
      import { mountFile } from "@borgiq/actors";

      export default async function receive(req: Request): Promise<Response> {
        const { file, paths } = req.inputs;
        const filePath = await mountFile(file);
        const fileBytes = await Deno.readFile(filePath);
        const zip = await JSZip.loadAsync(fileBytes);

        const extracted = [];
        for (const requestedPath of paths) {
          const normalizedPath = requestedPath.replace(/^\/+/, "");
          const zipEntry = zip.files[normalizedPath];
          if (!zipEntry || zipEntry.dir) {
            extracted.push({ fileName: normalizedPath, content: "" });
            continue;
          }
          const content = await zipEntry.async("string");
          extracted.push({ fileName: normalizedPath.split("/").pop() || normalizedPath, content });
        }

        return { results: { files: extracted } };
      }
    inputs:
      file: ${{ msg.research_agent.outputZipFile }}
      paths:
        - outputs/report.md
    options:
      allowNet: true
      allowFs: true
```

## Results Object

### Done Port Result

```typescript
interface AgentHarnessActorResult {
  sessionId: string;
  success: boolean;
  result?: unknown;
  outputZipFile?: BIQFile;        // Workspace zip (if returnOutputZipFile is true)
  claudeSessionDataFile?: BIQFile; // Claude session data zip (if returnClaudeSessionDataFile is true)
  meta: {
    endReason: 'completed' | 'timeout' | 'error';
    model?: string;
    duration?: number;             // Milliseconds
    usage?: {
      promptTokens?: number;
      completionTokens?: number;
      totalTokens?: number;
    };
  };
}
```

### Status Port Result

```typescript
type AgentHarnessStatusPortResult =
  | {
      type: 'agent-harness-loop';
      response: string;
      toolCalls?: AiToolCall[];
      meta: { cwd?: string; timestamp: number };
    }
  | {
      type: 'tool-result';
      toolCallId: string;
      toolName: string;
      output: AiToolMessageOutput;
      isError?: boolean;
      meta: { cwd?: string; timestamp: number };
    }
  | {
      type: 'agent-harness-error';
      message: string;
      code?: string;
      meta: { cwd?: string; timestamp: number };
    }
  | {
      type: 'agent-harness-notification';
      notificationType?: string;
      title?: string;
      message?: string;
      meta: { cwd?: string; timestamp: number };
    }
  | {
      type: 'agent-harness-complete';
      message?: string;
      meta: { cwd?: string; timestamp: number };
    };
```

## Credentials and Environment Variables

AgentHarnessActor supports passing secrets to the sandbox as environment variables:

```yaml
configuration:
  options:
    env:
      FIRECRAWL_API_KEY: ${{ credentials.firecrawl }}
      SERPAPI_API_KEY: ${{ credentials.serpapi }}
      CUSTOM_VAR: some-value
  credentials:
    firecrawl:
      workspaceKey: firecrawl
    serpapi:
      workspaceKey: serpapi
```

- `credentials` maps a local key to a workspace connection key
- `${{ credentials.firecrawl }}` resolves the credential value at runtime
- Values are encrypted during transit to the sandbox
- Environment variables are available to Claude Code and any processes it spawns

## Common Patterns

### Simple Code Generation (No Volume)

```yaml
options:
  prompt: |
    Create a Python script that reads a CSV file and generates
    a summary report. Save it as report_generator.py
  model: claude-sonnet-4-6
  timeoutInMinutes: 10
  returnOutputZipFile: true
```

### Session Continuation

```yaml
# First execution
options:
  prompt: Set up a Node.js project with Express and write a basic REST API
  sessionId: my-project-session

# Second execution (continues the session)
options:
  prompt: Now add authentication middleware and a /users endpoint
  sessionId: my-project-session
```

### Deep Research with Skills

```yaml
# Agent harness with skills loaded via volumeZipFile
options:
  prompt: |
    Research the topic and write a comprehensive report to outputs/report.md.
    Use the SerpAPI skill to search and Firecrawl to extract page content.
  volumeZipFile: ${{ msg.build_context.file }}
  model: claude-sonnet-4-5
  env:
    FIRECRAWL_API_KEY: ${{ credentials.firecrawl }}
    SERPAPI_API_KEY: ${{ credentials.serpapi }}
```

### Network-Restricted Code Processing

```yaml
options:
  prompt: Review the uploaded codebase for security vulnerabilities
  volumeZipFile: ${{ msg.upload.file }}
  allowNet: false
  sandboxProvider: daytona
  timeoutInMinutes: 30
```

### Agent with Connected BorgIQ Tools

```yaml
# AgentHarnessActor with tool actors
ACTR01agent:
  type: AgentHarnessActor
  configuration:
    options:
      prompt: |
        Search for information about the topic, get page contents,
        then write a summary to output.md
      model: claude-sonnet-4-6
      allowNet: false
    aiAgentToolActorIds:
      - ACTR01exasearch   # Exa Search tool
      - ACTR01exacontents # Exa Get Contents tool
```

### Fast Execution (No File Output)

```yaml
options:
  prompt: What is 2 + 2? Reply with just the number.
  returnOutputZipFile: false
  returnClaudeSessionDataFile: false
  timeoutInMinutes: 5
```

## Complete Example: Deep Research Agent with Context Building

This example shows the full pattern: DenoActor builds context zip -> AgentHarnessActor runs research -> DenoActor extracts output.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  # Step 1: Build context zip with skills and CLAUDE.md
  ACTR01kd6build0000000000000000:
    type: DenoActor
    version: 1
    name: Build Context
    msgVar: build_context
    description: Downloads skills from GitHub, builds .claude/skills/ directory, creates CLAUDE.md
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      code: |
        import JSZip from "npm:jszip@3.10.1";
        import type { Request, Response } from "@borgiq/actors";
        import { stashFile } from "@borgiq/actors";

        export default async function receive(req: Request): Promise<Response> {
          const { skills, claudeMd } = req.inputs;
          if (!Array.isArray(skills) || skills.length === 0) {
            throw new Error("Missing required input: skills (array of GitHub URLs)");
          }

          const zip = new JSZip();
          zip.file("CLAUDE.md", claudeMd);
          zip.folder("inputs");
          zip.folder("outputs");

          // Download and add skills to .claude/skills/
          // (skill downloading logic here — fetch from GitHub tree API)

          const zipBuffer = await zip.generateAsync({
            type: "uint8array",
            compression: "DEFLATE",
            compressionOptions: { level: 6 },
          });

          const biqFile = await stashFile(zipBuffer, "skills-directory.zip", "application/zip");
          return { results: { success: true, file: biqFile } };
        }
      inputs:
        skills:
          - https://github.com/vm0-ai/vm0-skills/tree/main/firecrawl
          - https://github.com/vm0-ai/vm0-skills/tree/main/serpapi
        claudeMd: |
          # Deep Research Agent
          You are a deep research agent. Use SerpAPI for discovery and
          Firecrawl for content extraction. Write results to outputs/.
      options:
        allowNet: true
        allowFs: true
    schemas:
      inputs:
        type: object
        properties:
          skills:
            type: array
            title: Skill URLs
            items:
              type: string
          claudeMd:
            type: string
            title: CLAUDE.md Content
        required:
          - skills
          - claudeMd
    id: ACTR01kd6build0000000000000000
    position:
      x: 0
      'y': -200
    edges:
      EDGE01build_to_agent:
        id: EDGE01build_to_agent
        sourceActorId: ACTR01kd6build0000000000000000
        sourcePortId: SPRTdefault
        targetActorId: ACTR01kd6agent0000000000000000
        targetPortId: TPRTdefault
        label: ''
        type: borgiqEdge

  # Step 2: Run Claude Code in sandbox with context
  ACTR01kd6agent0000000000000000:
    type: AgentHarnessActor
    version: 1
    name: Deep Research Agent
    msgVar: deep_research_agent
    description: Run Claude Code with skills to research and generate reports
    isActive: true
    continueOnError: false
    enableLTM: true
    enableSTM: false
    sourcePorts:
      - id: SPRTdone000
        name: Done
      - id: SPRTdefault
        name: Status
    configuration:
      options:
        prompt: |
          Research the given topic thoroughly using the available skills.
          Write your findings to outputs/report.md with proper citations.
        volumeZipFile: ${{ msg.build_context.file }}
        model: claude-sonnet-4-5
        env:
          FIRECRAWL_API_KEY: ${{ credentials.firecrawl }}
          SERPAPI_API_KEY: ${{ credentials.serpapi }}
        sessionId: ''
      credentials:
        firecrawl:
          workspaceKey: firecrawl
        serpapi:
          workspaceKey: serpapi
      aiAgentToolActorIds: []
    schemas: {}
    id: ACTR01kd6agent0000000000000000
    position:
      x: 0
      'y': 0
    edges:
      EDGE01agent_to_extract:
        id: EDGE01agent_to_extract
        sourceActorId: ACTR01kd6agent0000000000000000
        sourcePortId: SPRTdone000
        targetActorId: ACTR01kd6extract000000000000000
        targetPortId: TPRTdefault
        label: Done
        type: borgiqEdge

  # Step 3: Extract output files from workspace zip
  ACTR01kd6extract000000000000000:
    type: DenoActor
    version: 1
    name: Extract Output
    msgVar: extract_output
    description: Extracts specific files from the agent harness output zip
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      code: |
        import JSZip from "npm:jszip@3.10.1";
        import type { Request, Response } from "@borgiq/actors";
        import { mountFile } from "@borgiq/actors";

        export default async function receive(req: Request): Promise<Response> {
          const { file, paths } = req.inputs;
          if (!file) throw new Error("Missing required input: file");
          if (!paths?.length) throw new Error("Missing required input: paths");

          const filePath = await mountFile(file);
          const fileBytes = await Deno.readFile(filePath);
          const zip = await JSZip.loadAsync(fileBytes);

          const extracted = [];
          for (const requestedPath of paths) {
            const normalizedPath = requestedPath.replace(/^\/+/, "");
            const zipEntry = zip.files[normalizedPath];
            if (!zipEntry || zipEntry.dir) {
              extracted.push({ fileName: normalizedPath, content: "" });
              continue;
            }
            const content = await zipEntry.async("string");
            extracted.push({
              fileName: normalizedPath.split("/").pop() || normalizedPath,
              content,
            });
          }

          return {
            results: {
              totalExtracted: extracted.filter(r => r.content.length > 0).length,
              files: extracted,
            },
          };
        }
      inputs:
        file: ${{ msg.deep_research_agent.outputZipFile }}
        paths:
          - outputs/report.md
      options:
        allowNet: true
        allowFs: true
    schemas:
      inputs:
        type: object
        properties:
          file:
            type: any
            title: Zip File
          paths:
            type: array
            title: File Paths
            items:
              type: string
        required:
          - file
          - paths
    id: ACTR01kd6extract000000000000000
    position:
      x: 0
      'y': 200
    edges: {}
```

## Accessing Agent Harness Data in Downstream Actors

### From Done Port

```yaml
# Access session ID, output files, and metadata
configuration:
  inputs:
    sessionId: ${{ msg.research_agent.sessionId }}
    success: ${{ msg.research_agent.success }}
    outputZip: ${{ msg.research_agent.outputZipFile }}
    endReason: ${{ msg.research_agent.meta.endReason }}
    duration: ${{ msg.research_agent.meta.duration }}
    totalTokens: ${{ msg.research_agent.meta.usage.totalTokens }}
```

### From Status Port

```yaml
# Process real-time status updates
configuration:
  inputs:
    eventType: ${{ msg.research_agent.type }}
    content: ${{ msg.research_agent.type === 'agent-harness-loop' ? msg.research_agent.response : msg.research_agent.message }}
```

## Use Cases

### Code Generation & Review
Run Claude Code to generate, review, or refactor code in an isolated sandbox with full development tooling.

### Deep Research
Build context with skills (web search, content extraction), run research tasks, and extract structured output.

### Data Processing
Process uploaded data files with Python/Node.js, generate analytics, and return results as zip.

### Multi-Turn Development
Use session continuation to iteratively build projects across multiple executions.

### Secure Code Processing
Use Daytona provider with `allowNet: false` for processing sensitive code without external network access.

### Automated Testing
Upload a codebase via `volumeZipFile`, run tests, and extract results.

## Best Practices

1. **Use `volumeZipFile` for context** — Build a context zip with CLAUDE.md, skills, and input files using a DenoActor
2. **Extract specific files from output** — Use a downstream DenoActor to pull specific files from `outputZipFile` rather than processing the entire zip
3. **Set `maxLoopCount`** — Prevent runaway executions and control costs
4. **Use `timeoutInMinutes` appropriately** — Default is 15 minutes; increase for complex tasks, decrease for simple ones
5. **Use sessions for multi-step work** — Pass a consistent `sessionId` for iterative development tasks
6. **Pass secrets via `env` + `secrets`** — Never hardcode API keys in prompts
7. **Choose the right sandbox provider** — E2B for internet access, Daytona for isolation
8. **Set `continueOnError: true` on tool actors** — Let Claude handle tool failures gracefully
9. **Use lower temperature for deterministic tasks** — Code generation benefits from `temperature: 0` or `0.3`
10. **Disable file output for fast tasks** — Set `returnOutputZipFile: false` and `returnClaudeSessionDataFile: false` when you don't need workspace files

## TypeScript Schema Hint

See [typescript/actor-schemas-task-core.md](typescript/actor-schemas-task-core.md) for the complete TypeScript definitions of AgentHarnessActor options, result schemas, and status port types.
