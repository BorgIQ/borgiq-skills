---
name: borgiq-agent-builder
description: Design autonomous AI behavior in BorgIQ — AiAgentActor (serverless coding agent with filesystem/bash, sessions, and BorgIQ actors as tools), AgentHarnessActor (sandboxed Claude Code with MCP + session persistence), and McpServerActor (expose BorgIQ tools to external agents like Claude Desktop). Use when the user wants autonomous agents, multi-step tool-using AI, agent harness sandboxes, or MCP integration. Triggers on "AI agent", "AiAgentActor", "AgentHarnessActor", "Claude Code sandbox", "MCP server", "autonomous AI", "tool-using LLM", "research agent", "multi-step AI", "coding agent".
---

# BorgIQ Agent Builder

Design autonomous AI in BorgIQ. Pair with `borgiq-builder` (hub) for wiring, and with `borgiq-json-schema-builder` whenever a tool input needs a real contract.

## Mental model

BorgIQ has three execution modes for AI work plus one endpoint pattern:

- **AiActor** — a single LLM call. Stateless. Returns text, structured output, or tool *definitions* — but does not execute tools in a loop. One round trip, done.
- **AiAgentActor** — an autonomous coding agent (pi) running in checkpointed serverless segments. Has a private workspace with built-in `read`/`write`/`edit`/`bash`/`grep`/`find`/`ls` tools (plus an opt-in `deno` tool for running code, via `enableDenoTool`) **plus** connected BorgIQ actors as tools. Sessions continue via `sessionId` (7-day sliding TTL); workspace goes in via `volumeZipFile` and comes out as `outputZipFile`. Two output ports: **Done** (final result + zips) and **Status** (assistant turns + tool results).
- **AgentHarnessActor** — Claude Code running in an isolated sandbox VM (E2B or Daytona) with a full machine, MCP servers, background processes, and session persistence via `sessionId`. Inbound messages are queued FIFO with mutex. Returns workspace + session zips on completion.
- **McpServerActor** — *not* an agent. An MCP endpoint that exposes its child tool actors so external clients (Claude Desktop, Cursor, custom agents) can call BorgIQ actors via the Model Context Protocol.

> **Legacy note:** flows built before mid-2026 may contain `DeprecatedAiAgent` — the old orchestrator-loop agent (no filesystem, options like `temperature`/`maxTokens`/`messages`) that used to own the `AiAgentActor` type name. It still runs but must not be used for new work. See [`references/deprecated-ai-agent.md`](../borgiq-builder/references/deprecated-ai-agent.md).

## "Which one do I use" matrix

| User wants | Use | Why |
|---|---|---|
| Text generation, summarization, classification | **AiActor** | One LLM call, no loop overhead |
| Structured JSON output | **AiActor** with `outputSchema` | Deterministic, see `borgiq-json-schema-builder` |
| Tool *definitions* without execution (single round) | **AiActor** | LLM lists tools, you invoke them yourself |
| Multi-step research / orchestration / "agent figures it out" | **AiAgentActor** | Autonomous loop, BorgIQ actors as tools |
| File/data processing: unzip, transform, script, re-zip | **AiAgentActor** | Built-in filesystem + bash on a private workspace |
| Code generation that must also *run* the code | **AiAgentActor** | `bash` executes against the workspace |
| Resumable session across invocations | **AiAgentActor** (or AgentHarnessActor) with stable `sessionId` | Checkpointed sessions, 7-day sliding TTL |
| Claude Code skills / slash commands / plugins | **AgentHarnessActor** | The harness runs Claude Code itself |
| Remote MCP server, or a BorgIQ MCP Server Actor, as agent tools | **AiAgentActor** or **AgentHarnessActor** | `mcpServers` array: `type: http` / `type: borgiq` on both |
| stdio (subprocess) MCP server as agent tools | **AgentHarnessActor** | `type: stdio` runs in the sandbox; AiAgentActor has no subprocess host |
| Background processes (dev server, daemon) | **AgentHarnessActor** | Nothing survives an AiAgentActor segment boundary |
| Heavy environments (big installs/builds, >10 GB, PTY) | **AgentHarnessActor** | Full sandbox VM |
| Expose BorgIQ tools to Claude Desktop / Cursor / external agents | **McpServerActor** | MCP endpoint, external client drives tool calls |
| Multi-agent systems | **AiAgentActor** with CallFlowActor tools | Sub-agents as callable sub-flows |

## Key decisions — AiAgentActor

1. **System vs user prompt.** `systemPrompt` declares role, conventions, and the wired-tool inventory (list each tool's `msgVar`). The `prompt` field holds the task wired from `inputs`. Don't mix — role definition stays stable; task changes per invocation.
2. **Session strategy.** Leave `sessionId` blank for one-shot runs (auto-generated, returned on the done port). Use a stable ID when the agent should resume its workspace + conversation later. After the 7-day sliding TTL, the same ID starts fresh.
3. **Runtime sizing.** The workspace is capped at 20% of the runtime's ephemeral storage — recommend a runtime with ≥ 4 GB ephemeral for real file work. The runtime timeout only sets the segment length; total time is governed by `timeoutInMinutes` (default 30).
4. **Built-in tool filtering.** `disallowedTools: [write, edit, bash]` makes a read-only analyst. `allowedTools` for a strict allow-list. Built-in names (`read`/`write`/`edit`/`bash`/`grep`/`find`/`ls`) are reserved — wired tool actors must not use them as `msgVar`; `deno` joins them only when `enableDenoTool: true`. Note `bash` cannot spawn programs (no python/node/git); set `enableDenoTool: true` when the agent needs to run code it writes — and if you do, don't also exclude `deno` via `allowedTools`/`disallowedTools`, which is now rejected as a contradiction.
5. **Network lists.** `allowNet`/`allowNetList`/`denyNetList` govern the whole tool runtime, bash included — `curl` is one of bash's built-ins and is subject to the same allowlist, so with `allowNet` off it reports "command not found". Default is `allowNet: false`.
6. **Done vs Status ports.** **Done** fires once with `result` + zips + `meta.endReason`. **Status** streams assistant turns and tool results. Wire Done to the next task actor; wire Status to a UI/logging actor for real-time visibility. `result` is optional — branch on `success`/`meta.endReason`.
7. **Sub-agents via CallFlowActor.** Wrap complex sub-tasks in their own AiAgentActor inside a callable sub-flow; expose it as a tool. Use `${{aiInput}}` in the callable's `payload` (not `inputs`). Keeps the parent agent's tool surface flat.
8. **Idempotent bash side effects.** Bash is at-least-once across segment retries — external calls made from bash may repeat. Put exactly-once API work in wired tool actors, not bash + curl.

## Key decisions — AgentHarnessActor

1. **E2B vs Daytona.** E2B has full internet by default — good for research and external APIs. Daytona is isolated by default — good for sensitive code. Tune both with `allowNet` / `allowNetList` / `denyNetList`.
2. **`sessionId` strategy.** Leave blank for one-shot runs (auto-generated). Use a stable ID (`user-123-research`) when the agent should resume context. Concurrent calls with the same `sessionId` queue FIFO under a mutex.
3. **`volumeZipFile`.** Upstream DenoActor builds a zip with CLAUDE.md, skills, input data; harness extracts to `~/workspace/`. Set `workingDirectory: my-project` to `cd` before the run.
4. **MCP servers.** Add to the `mcpServers` array when the agent needs external tools (`type: http`, e.g. Linear/GitHub), an MCP Server Actor elsewhere in BorgIQ (`type: borgiq`, no auth — the agent's session is already scoped to the servers listed), or a subprocess server (`type: stdio`, AgentHarnessActor only). BorgIQ tool actors auto-inject separately; MCP servers are additive.
5. **Env vars vs credentials.** Never hardcode secrets in prompts. Pattern: `env: { GITHUB_TOKEN: ${{ credentials.github.token }} }`.
6. **Return zips.** Set `returnOutputZipFile: true` if downstream actors need workspace files. Set `returnClaudeSessionDataFile: true` to archive the conversation. Both false for fast, fire-and-forget runs.

## Producing skill directories for an agent (file-handle export pattern)

An AgentHarnessActor receives its context as a `volumeZipFile` — a BorgIQ file handle that the harness extracts to `~/workspace/`. When the directory's contents (a skill bundle, CLAUDE.md, reference docs, input data) live in **Collections** rather than as a static asset, don't hand-assemble the zip inline at every call site. Instead:

- **Expose a callable actor/flow that reconstructs the directory and emits a BorgIQ file handle.** Build a CallableTriggerActor sub-flow (or a DenoActor) that reads the relevant Collection items, writes them into the right directory layout (`skills/<name>/SKILL.md`, `CLAUDE.md`, …), zips it, and returns the file handle via `stashFile` / CallableResponseActor. Upstream flows call it and pass the handle straight into `volumeZipFile`.
- **Treat this as a packaging/export endpoint, not as normal CRUD.** Its job is to *materialize* a directory tree from stored state and produce a file artifact — it is not a getItem/putItem accessor. Keep it separate from the CRUD endpoints that mutate the underlying Collection: those own the data; this one only renders a snapshot into a file handle. (Endpoint-first split: the export route and the CRUD routes are different triggers — see the hub's [Universal Trigger vs Webhook Trigger](../borgiq-builder/SKILL.md#universal-trigger-vs-webhook-trigger-http-endpoints) matrix.)

This keeps the directory definition in one reusable place: any agent or flow that needs the bundle calls the export actor instead of duplicating zip-assembly logic. If the Collections backing it must exist before first use, provision them with a migration runner — see [collection-migrations.md](../borgiq-builder/references/collection-migrations.md).

## Anti-patterns

1. **Using AiActor when you need a loop.** A single LLM call doesn't *execute* tools — it just lists them. If the customer wants "the AI figures out which API to call and then uses the result to call another one," that's AiAgentActor.
2. **Using AgentHarnessActor for plain file work.** Unzipping, scripting, and editing files doesn't need a sandbox VM — AiAgentActor's built-in tools do it with far less latency and cost. Reserve the harness for Claude Code features, stdio MCP servers, and daemons.
3. **Wiring file-system tool actors into AiAgentActor.** The agent already has `read`/`write`/`edit`/`bash` against its workspace — don't rebuild them as HTTP/Deno tools, and never name a wired tool after a built-in (validation rejects it).
4. **Wiring tool inputs through `options` instead of the agent boundary.** Tools must be listed in `aiAgentToolActorIds`; tool actors consume `${{aiInput}}` in their `inputs`. Trying to route data via the parent's `options` breaks the loop.
5. **Ignoring the Done/Status port distinction.** Wiring only Done and expecting real-time progress means you'll see nothing until completion. Wire Status for in-flight visibility.
6. **`sessionId` footguns.** No `sessionId` = every run is isolated. Same `sessionId` across concurrent calls = serialized execution. A `sessionId` past its TTL silently starts fresh. Pick the strategy on purpose — and persist the returned `sessionId` if a later flowrun must continue the session.
7. **MCP scope confusion.** `McpServerActor` exposes BorgIQ tools *outward*. To *consume* tools from a BorgIQ agent, use its `mcpServers` array — `type: http` for an external server, `type: borgiq` to point at an McpServerActor (which is how an agent reuses one internally, rather than calling its public endpoint with a token).
8. **Leaking secrets via tool schemas.** Tool input schemas are visible to the agent; description and title fields can accidentally include secret hints. Audit them before deploy.

## References

| File | What's inside |
|---|---|
| [`references/ai-actor.md`](../borgiq-builder/references/ai-actor.md) | Single LLM call: text generation, structured output, tool *definitions*. When NOT to use it. |
| [`references/ai-agent-actor.md`](../borgiq-builder/references/ai-agent-actor.md) | Serverless coding agent: built-in filesystem/bash tools, BorgIQ actor tools, sessions, Done/Status ports, runtime sizing. |
| [`references/deprecated-ai-agent.md`](../borgiq-builder/references/deprecated-ai-agent.md) | Legacy orchestrator-loop agent (`DeprecatedAiAgent`) — read/debug existing flows only. |
| [`references/ai-agent-api-guide.md`](../borgiq-builder/references/ai-agent-api-guide.md) | Programmatic agent workflow API: creation, editing, execution, flowrun monitoring. |
| [`references/agent-harness-actor.md`](../borgiq-builder/references/agent-harness-actor.md) | Sandboxed Claude Code: full VM, session persistence, MCP, network controls. |
| [`references/mcp-server-actor.md`](../borgiq-builder/references/mcp-server-actor.md) | Expose BorgIQ tools as MCP endpoint, PAT auth, JSON-RPC protocol. |
| [`references/message-processor-actor.md`](../borgiq-builder/references/message-processor-actor.md) | `issueCallbackToken` / `waitForCallbackToken` for human-in-the-loop agent flows. |

## When to hand off to other spokes

| Customer ask | Hand off to |
|---|---|
| "Design the schema for this tool's input" | `borgiq-json-schema-builder` |
| "Pause for human approval mid-agent" | `borgiq-form-builder` (InterfaceActor with callback token) |
| "Render the agent's findings in a custom UI" | `borgiq-react-app-builder` |
| Edges, msgVars, deploy, debug, CommentActor | Hub: `borgiq-builder` |
