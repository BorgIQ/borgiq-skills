---
name: borgiq-agent-builder
description: Choose and configure autonomous AI in BorgIQ — AiAgentActor (serverless coding agent with a workspace, bash, sessions and actors as tools), AgentHarnessActor (a harness CLI such as Claude Code or Codex in a sandbox VM), McpServerActor (BorgIQ tools for external MCP clients). Use for multi-step, tool-using AI. Triggers on "AI agent", "AiAgentActor", "AgentHarnessActor", "Claude Code sandbox", "MCP server", "autonomous AI", "tool-using LLM", "research agent", "multi-step AI", "coding agent".
---

# BorgIQ Agent Builder

Choose the AI actor here, then configure it from the references. Pair this skill with `borgiq-builder` (the hub: wiring, IDs, deploy) and `borgiq-json-schema-builder` (tool input and output contracts). The references ship in the `borgiq-builder` skill's `references/` folder; install that skill too.

## Which AI actor

| The user wants | Use | Why |
|---|---|---|
| Text generation, summarization, classification, extraction | **AiActor** | One LLM call |
| Structured JSON output | **AiActor** with `outputSchema` | Design it with `borgiq-json-schema-builder` |
| Route a message by its category | **AiRouterActor** | Classifies and routes in one actor |
| Tool *definitions* the model picks from, run by you | **AiActor** with `tools` | Returns `toolCalls`, executes nothing |
| Multi-step research or orchestration, the model deciding what to call | **AiAgentActor** | Agent loop, BorgIQ actors as tools |
| File or data work: unzip, transform, edit, re-zip | **AiAgentActor** | Built-in filesystem and bash |
| Write TypeScript/JavaScript and run it | **AiAgentActor** with `enableCodeExecution: true` | `code_execution` runs it with Deno; `bash` cannot run programs |
| Run Python or another language, install packages, use a real shell | **AgentHarnessActor** | Full machine; the AI Agent runs only Deno TS/JS, no installs |
| Resume a workspace and conversation later | **AiAgentActor** (or AgentHarnessActor), stable `sessionId` | Checkpointed sessions |
| A harness CLI's own features: Claude Code skills, slash commands, plugins; Codex, OpenCode, pi | **AgentHarnessActor** | Runs that CLI |
| A remote MCP server, or an McpServerActor, as agent tools | **AiAgentActor** or **AgentHarnessActor** | `mcpServers`: `type: http` / `type: borgiq` |
| A stdio (subprocess) MCP server as agent tools | **AgentHarnessActor**, not `harness: pi` | `type: stdio`; the AI Agent has no subprocess host |
| An MCP server that asks the caller for input (elicitation, sampling, roots) | **AgentHarnessActor** with a CLI that answers them | The AI Agent answers none |
| Background processes (dev server, daemon), PTY | **AgentHarnessActor** | Nothing survives an AI Agent segment |
| Big installs or builds, a workspace beyond the AI Agent's cap, firewall isolation | **AgentHarnessActor** | Sandbox VM |
| Expose BorgIQ tools to external agents (Claude Desktop, Cursor, custom clients) | **McpServerActor** | MCP endpoint; the client drives the calls |
| Multi-agent systems | **AiAgentActor** with CallFlowActor tools | Sub-agents as callable sub-flows |
| An existing flow contains `DeprecatedAiAgent` | Read or migrate it; never create one | Legacy loop agent |

Start agentic work on AiAgentActor; AgentHarnessActor takes tens of seconds to minutes to start and bills sandbox time.

## Key decisions: AiAgentActor

Values: [`ai-agent-actor.md`](../borgiq-builder/references/ai-agent-actor.md).

1. **Prompts.** `systemPrompt`: role, conventions, and each wired tool's `msgVar` with what it does. `prompt`: the task, from `inputs`.
2. **Model.** Always set `model` ([`ai-models.md`](../borgiq-builder/references/ai-models.md)). `thinkingLevel` (default `medium`) is billed every turn: `off` for cheap agents, `high` for hard work. Custom providers (`<slug>/<model-id>`) need a public `https://` base URL and no `agent: false` ([`custom-ai-providers.md`](../borgiq-builder/references/custom-ai-providers.md)).
3. **Sessions.** Blank `sessionId` for one-shot runs, a stable ID to resume; persist the returned ID for a later flowrun. An expired session starts fresh. A `volumeZipFile` sent to a reused session resets the files it contains: send it only on the first run to keep the agent's edits.
4. **Runtime.** The workspace is a fraction of the runtime's ephemeral storage: size the runtime for real file work. `timeoutInMinutes` bounds the run; the runtime timeout, one segment.
5. **Code and tools.** `bash` runs no programs; `enableCodeExecution: true` is the Code Execution tool's only switch. `disallowedTools: [write, edit, bash]` makes a read-only agent. Tool actors must not take a built-in tool's name.
6. **Network.** `allowNet` is off by default and covers bash's `curl` and scripts; `allowNetList` needs it on.
7. **Ports.** Done fires once (`result`, zips, `meta.endReason`); Status streams turns and tool results. Branch on `success` / `meta.endReason`: `result` can be absent.
8. **Tools.** [`agent-tools.md`](../borgiq-builder/references/agent-tools.md). Put a complex sub-task in its own agent behind a callable sub-flow, exposed as a CallFlowActor tool.
9. **Side effects.** Bash is at-least-once across segment retries: do exactly-once API work in tool actors.

## Key decisions: AgentHarnessActor

Values: [`agent-harness-actor.md`](../borgiq-builder/references/agent-harness-actor.md).

1. **Harness and model.** `harness`: `claude` (default), `codex`, `opencode` or `pi`; `model` must be one of that harness's agent models; no custom providers.
2. **Provider.** E2B (default) has full internet, for research and external APIs; Daytona is isolated, for sensitive code. Tune with `allowNet` / `allowNetList` / `denyNetList`.
3. **Sessions.** Blank `sessionId` for one-shot runs, a stable ID (`user-123-research`) to resume; runs on one session queue FIFO.
4. **Context in, files out.** An upstream DenoActor builds the `volumeZipFile` (e.g. `CLAUDE.md`, skills, input data), extracted to `~/workspace/`. Read results from `outputZipFile`; turn off the `return…` zips for fast runs.
5. **MCP servers.** Give every entry a `type` (`http`, `borgiq`, `stdio`): an untyped one is stdio here.
6. **Secrets.** Never in prompts: map each in `configuration.credentials` (`github: { workspaceKey: github-token }`), then `env: { GITHUB_TOKEN: ${{ credentials.github }} }`.

## Key decisions: McpServerActor

Values: [`mcp-server-actor.md`](../borgiq-builder/references/mcp-server-actor.md). Wire its tools like an agent's and write their descriptions for the calling model. Clients authenticate with an [API token](../borgiq-builder/references/api-tokens.md) scoped `org:access`, `workspace:access`, `canvas:read`, `Trigger:manual:create` (`borgiq tokens create`), or with OAuth.

## Producing skill directories for an agent (file-handle export pattern)

When a harness's context (skills, instructions, input data) lives in **Collections**, do not assemble the zip at every call site. One callable flow or DenoActor reads the items, writes the layout (`skills/<name>/SKILL.md`, `CLAUDE.md`, …), zips it and returns the file handle (`stashFile`, CallableResponseActor) for callers to pass as `volumeZipFile`. Keep this packaging endpoint apart from the CRUD endpoints that own the data (the hub's [Universal Trigger vs Webhook Trigger](../borgiq-builder/SKILL.md#universal-trigger-vs-webhook-trigger-http-endpoints) matrix), and provision the Collections with a migration runner ([`collection-migrations.md`](../borgiq-builder/references/collection-migrations.md)).

## Anti-patterns

1. **AiActor for a loop**: it executes no tools.
2. **AgentHarnessActor for plain file work**: the AI Agent is faster and cheaper.
3. **File-system tool actors on an AI Agent**, or a tool named after a built-in.
4. **Tool data through the parent's `options`**: tools take `${{aiInput}}` in their own `inputs` (CallFlowActor: in `payload`).
5. **Only Done wired** while expecting live progress: wire Status.
6. **Accidental `sessionId` use**: no ID isolates runs; one ID across concurrent calls serializes them.
7. **MCP direction**: McpServerActor exposes tools outward; agents consume one via `type: borgiq`, not its endpoint.
8. **Secret hints in tool schemas**: the calling model sees titles and descriptions.

## References

| File | What's inside |
|---|---|
| [`ai-actor.md`](../borgiq-builder/references/ai-actor.md) | One LLM call: options, structured output, messages, tools |
| [`ai-models.md`](../borgiq-builder/references/ai-models.md) | Model references, defaults, picks with prices |
| [`ai-agent-actor.md`](../borgiq-builder/references/ai-agent-actor.md) | Options, built-in tools, ports, sessions, runtime; legacy DeprecatedAiAgent |
| [`agent-tools.md`](../borgiq-builder/references/agent-tools.md) | Tool actors and `mcpServers` for every host |
| [`agent-harness-actor.md`](../borgiq-builder/references/agent-harness-actor.md) | Harnesses, sandbox, network, sessions, ports |
| [`mcp-server-actor.md`](../borgiq-builder/references/mcp-server-actor.md) | Endpoint, auth, protocol, errors, limits |
| [`api-tokens.md`](../borgiq-builder/references/api-tokens.md) | `borgiq tokens`, every scope |
| [`custom-ai-providers.md`](../borgiq-builder/references/custom-ai-providers.md) | OpenAI-compatible providers as `<slug>/<model-id>` |
| [`message-processor-actor.md`](../borgiq-builder/references/message-processor-actor.md) | Callback tokens for human-in-the-loop flows |

## When to hand off to other skills

| Customer ask | Hand off to |
|---|---|
| "Design the schema for this tool's input" | `borgiq-json-schema-builder` |
| "Pause for human approval mid-agent" | `borgiq-form-builder` (InterfaceActor with callback token) |
| "Render the agent's findings in a custom UI" | `borgiq-react-app-builder` |
| Edges, msgVars, deploy, debug, CommentActor | Hub: `borgiq-builder` |
