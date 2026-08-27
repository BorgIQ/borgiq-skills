---
name: borgiq-builder
description: Build Actors, Triggers, AI Agents, and web apps for BorgIQ. Supports HttpRequestActor, DenoActor, PythonActor, AiActor, AiAgentActor (serverless coding agent with filesystem/bash, sessions, and BorgIQ tools), AgentHarnessActor (sandboxed Claude Code with session persistence), CollectionActor, StreamActor, AppTriggerActor, InterfaceTriggerActor, WebhookTriggerActor. Use for workflow automations, REST API integrations, custom Deno/Python actors, AI-powered tasks, autonomous AI agents with tools, agent harness sandboxed execution, triggers (scheduled, webhook, email, button, interface, app, callable), or web apps with actor-backed APIs. Triggers on "create an actor", "build HTTP request", "write Deno/Python code", "use AI to process", "build an AI agent", "agent harness", "run Claude Code in sandbox", "store data", "collection", "stream", "append-only log", "set up webhook", "build a web app", "theme an app", or workflow tasks.
---

# BorgIQ Builder

Build Actors and Triggers that power BorgIQ automation workflows.

## Table of Contents

- [BorgIQ Platform Overview](#borgiq-platform-overview)
- [Routing to Specialized Skills](#routing-to-specialized-skills)
- [TypeScript Definitions](#typescript-definitions)
- [Task Actor Types](#task-actor-types)
- [Trigger Actor Types](#trigger-actor-types)
- [Common Actor Structure](#common-actor-structure)
- [Actor Naming Conventions](#actor-naming-conventions)
- [Configuration Interpolation Order](#configuration-interpolation-order)
- [BorgIQ Expressions](#borgiq-expressions)
- [Context Variables](#context-variables)
- [Q-lib Functions](#q-lib-functions)
- [Actor Source Files](#actor-source-files)
- [Actor Memory](#actor-memory)
- [Authentication](#authentication)
- [Actor ID, Validation, and Post-Processing](#actor-id-validation-and-post-processing)
- [Generation Instructions](#generation-instructions)
- [Workflow Composition](#workflow-composition)
- [Actor Connections and Edges](#actor-connections-and-edges)
- [Workflow Examples](#workflow-examples)
- [Workflow Patterns](#workflow-patterns)
  - [Web apps and forms — handed off to spokes](#web-apps-and-forms--handed-off-to-spokes)
  - [Collection migrations and provisioning](#collection-migrations-and-provisioning)
  - [Streams: events in order, consumed by cursor](#streams-events-in-order-consumed-by-cursor)
- [Editing Existing Workflows](#editing-existing-workflows)
- [Migration from Other Platforms](#migration-from-other-platforms)
- [Deploying and Testing with the CLI](#deploying-and-testing-with-the-cli)
  - [Canvas Bundles](references/cli/canvas-bundles.md)
  - [CLI Command Reference](references/cli/cli-command-reference.md)
  - [CLI Data Formats](references/cli/cli-data-formats.md)
  - [CLI Scaffolding Scripts](references/cli/cli-setup-scripts.md)
  - [CLI Troubleshooting](references/cli/cli-troubleshooting.md)

## BorgIQ Platform Overview

BorgIQ is an automation platform where nodes are called **Actors**. Workflows chain Actors together with connections (edges). Each actor emits messages stored under `msg.ActorName`.

### Workspaces and Canvases

BorgIQ organizes workflows in a hierarchical structure:

| Concept | Description | Identifier |
|---------|-------------|------------|
| **Workspace** | A container for canvases, connections, and team members. Workspaces provide isolation and access control. | `workspaceSlug` (e.g., `my-team`, `prod-ws`) |
| **Canvas** | A container for one or more workflows and their connections. Each workflow within a canvas has its own trigger actor. | `canvasSlug` (e.g., `process-orders`, `send-notifications`) |
| **Actor** | An individual node within a canvas that performs work or triggers execution. | `actorId` (e.g., `ACTR01kd6tesvky0mh8x1css3sv5yg`) |

**Slug Format:**
- Workspace slugs: 5-10 lowercase alphanumeric characters with hyphens (e.g., `john-dev`)
- Canvas slugs: 2-255 lowercase alphanumeric characters with hyphens (e.g., `skill-test`)

**Cross-Canvas/Workspace Calls:**
Actors can invoke sub-flows in other canvases or workspaces using CallFlowActor. When `workspaceSlug` or `canvasSlug` is omitted, the current workspace/canvas is assumed.

### Actor Categories

There are two categories of actors:

| Category | Description | Examples |
|----------|-------------|----------|
| **Trigger Actors** | Start workflows (flowruns). Each workflow has exactly one trigger. A canvas can contain multiple workflows, each with its own trigger. | ButtonTriggerActor, WebhookTriggerActor, ScheduledTriggerActor |
| **Task Actors** | Perform work within the workflow. Process data, make API calls, route messages, etc. | HttpRequestActor, DenoActor, AiActor, RouterActor |

**Example workflow:** `TriggerActor -> TaskActor1 -> TaskActor2` produces:
```json
{
  "msg": {
    "trigger_actor": { "...output from trigger..." },
    "task_actor_1": { "...output from task 1..." },
    "task_actor_2": { "...output from task 2..." }
  }
}
```

### Concurrent Execution Model

**BorgIQ executes all downstream actors concurrently by default.** When an actor emits a message, all connected downstream actors start executing in parallel without any explicit configuration.

```
     A
    / \
   B   C      <- B and C run concurrently when A emits
    \ /
     D        <- D receives TWO separate messages (one from B, one from C)
```

**Key behavior:**
- If A connects to both B and C, both B and C execute concurrently when A emits
- D will receive **two separate messages** and execute **twice** (once for B's output, once for C's output)
- No `fork` action is needed for parallel execution—it happens automatically

**When to use `fork`/`forkJoin`:**

Only use the `fork` and `forkJoin` MessageProcessorActor actions when you need to **synchronize** parallel paths and emit a **single combined message**. See [message-processor-actor.md](references/message-processor-actor.md#fork-actions) for detailed documentation, [workflow-patterns.md](references/workflow-patterns.md#pattern-1-multi-source-data-aggregation) for complete examples, and [fork-join-common-mistakes.md](references/fork-join-common-mistakes.md) for common pitfalls to avoid.

| Scenario | Use Fork/ForkJoin? |
|----------|-------------------|
| Run B and C in parallel, D processes each separately | **No** - just connect A→B→D and A→C→D |
| Run B and C in parallel, D needs combined results from both | **Yes** - use `fork` before split, `forkJoin` to recombine |
| Fire-and-forget parallel notifications (email + Slack) | **No** - just connect to both actors |
| Parallel API calls where you need all results together | **Yes** - use `fork`/`forkJoin` pattern |

**Critical rules:**
- `forkJoin` requires `enableSTM: true`
- MessageProcessorActor always uses only `SPRTdefault` (fork uses multiple edges, not multiple sourcePorts)
- Only RouterActor, AiRouterActor, InterfaceActor, AiAgentActor, and AgentHarnessActor use multiple sourcePorts

## Routing to Specialized Skills

This skill is the **hub** of the `borgiq-builder` plugin. It covers actor wiring, edges, msgVars, expressions, and overall workflow composition. Four **spoke** skills ship in the same plugin and load automatically when their domain appears in the user's request. Pull them in actively when the work crosses into their area — they're more opinionated and focused than this hub.

| Spoke | Load when the user is doing… | What it owns |
|---|---|---|
| **`borgiq-form-builder`** | Interface pages, forms, signups, surveys, approval forms, data-entry UIs, web-viewer embeds | InterfaceTriggerActor + InterfaceActor + form components + themes + webViewer styling |
| **`borgiq-react-app-builder`** | Custom app UIs — dashboards, data explorers, SPAs, any component-based or multi-file frontend, npm UI libraries, `useEndpoint`, `useGetSession` (who is viewing the app); also owns maintaining legacy raw-HTML AppTriggerActor apps | ReactAppTriggerActor + server-side Vite build + `codeDir`/`options.files` model + `@borgiq/actors` SDK + webhook endpoints + viewer session + the app theme library |
| **`borgiq-agent-builder`** | Autonomous AI behavior — AiAgentActor (serverless coding agent with filesystem/bash + tools), AgentHarnessActor (sandboxed Claude Code), McpServerActor (expose tools to external agents) | AiActor when-not-to-use + AiAgentActor + AgentHarnessActor + McpServerActor |
| **`borgiq-json-schema-builder`** | Non-trivial JSON schemas — AiActor `outputSchema`, agent tool input schemas, Collection item schemas, Callable response schemas | All schema-design decisions, anti-patterns, and the BorgIQ `type: any` convention |

Cross-domain example: _"build a flow with an interface form that takes a customer name, hands it to an AI agent that researches them, posts the result to Slack"_ → hub orchestrates + `borgiq-form-builder` designs the form + `borgiq-agent-builder` designs the agent + `borgiq-json-schema-builder` defines the research output schema. The hub stays in context throughout and handles wiring, edges, IDs, and the Slack HTTP actor.

## TypeScript Definitions

Complete TypeScript/Zod schema definitions for all actors are available in [references/typescript/](references/typescript/). Use these to understand exact data structures, validation rules, and type constraints.

| Reference File | Description |
|-------------|-------------|
| [actor-schemas-triggers.md](references/typescript/actor-schemas-triggers.md) | Trigger actor options and results (Button, Webhook, Email, Interface, App, Scheduled, Universal, Callable) |
| [actor-schemas-task-core.md](references/typescript/actor-schemas-task-core.md) | Core task actor schemas (AiActor, AiAgentActor, DenoActor, PythonActor, RouterActor, etc.) |
| [actor-schemas-task-http.md](references/typescript/actor-schemas-task-http.md) | HttpRequestActor options and authentication types |
| [actor-schemas-task-datastore.md](references/typescript/actor-schemas-task-datastore.md) | DataStoreActor actions (legacy — kept for TypeScript type reference) |
| [actor-schemas-task-collection.md](references/typescript/actor-schemas-task-collection.md) | CollectionActor actions (query, getItem, putItem, batchGet, batchWrite, etc.) |
| [actor-schemas-task-stream.md](references/typescript/actor-schemas-task-stream.md) | StreamActor actions (createStream, appendData, readStream, getStreamInfo, etc.) |
| [actor-schemas-task-messageprocessor.md](references/typescript/actor-schemas-task-messageprocessor.md) | MessageProcessorActor actions (inject, split, collect, fork, forkJoin, delay, etc.) |
| [actor-schemas-comment.md](references/typescript/actor-schemas-comment.md) | CommentActor schema |
| [form-components.md](references/typescript/form-components.md) | Interface form component schemas (InterfaceTriggerActor and InterfaceActor only, not used by AppTriggerActor) |
| [schemas.md](references/typescript/schemas.md) | Common schemas (IDs, files, runtime types, context, signals) |
| [common-types.md](references/typescript/common-types.md) | Shared types, AI model definitions, canvas, runtime, sandbox types |

**Usage:** When building actors or understanding output structures, read the relevant TypeScript reference markdown file to find exact field names, types, and validation rules. Each file contains a table of contents linking to individual type definitions.

## Task Actor Types

| Type | Description | Reference |
|------|-------------|-----------|
| **HttpRequestActor** | Makes REST API calls to external services (Gmail, GitHub, Airtable, etc.) | [http-request-actor.md](references/http-request-actor.md) |
| **DenoActor** | Executes custom TypeScript/JavaScript code in a sandboxed Deno runtime | [deno-actor.md](references/deno-actor.md) |
| **PythonActor** | Executes custom Python code in a sandboxed Python runtime with UV package management | [python-actor.md](references/python-actor.md) |
| **AiActor** | Invokes AI models (LLMs) for text generation, structured output, and AI-powered tasks | [ai-actor.md](references/ai-actor.md) |
| **AiAgentActor** | Autonomous AI coding agent running in checkpointed serverless segments. Has a private workspace with built-in filesystem/bash tools (`read`/`write`/`edit`/`bash`/`grep`/`find`/`ls`, plus an opt-in `deno` tool for running code) plus BorgIQ actors as tools, session continuation via `sessionId`, and workspace zip in/out (`volumeZipFile` → `outputZipFile`). Has two output ports: Done (final result + zips) and Status (assistant turns + tool results). Tool actors are rendered inside the agent boundary with empty edges. | [ai-agent-actor.md](references/ai-agent-actor.md) |
| **DeprecatedAiAgent** | Legacy orchestrator-loop AI agent (pre-2026 `AiAgentActor`) — no filesystem or sessions. Hidden from the palette; existing instances keep running. **Do not create new instances — use AiAgentActor.** | [deprecated-ai-agent.md](references/deprecated-ai-agent.md) |
| **AgentHarnessActor** | Runs Claude Code in an isolated sandbox (E2B or Daytona) with full filesystem access, code execution, session persistence via `sessionId`, and queued inbound messages. Supports `volumeZipFile` for context, network control, MCP servers, environment variables, and returns workspace + session data zips. Use when the agent needs to execute code, install packages, or persist state across sessions. Has two output ports: Done (final result with output files) and Status (real-time execution updates). | [agent-harness-actor.md](references/agent-harness-actor.md) |
| **AiRouterActor** | Routes messages to different outputs based on AI-powered classification | [ai-router-actor.md](references/ai-router-actor.md) |
| **RouterActor** | Routes messages based on boolean conditions (if/else, switch logic) | [router-actor.md](references/router-actor.md) |
| **MessageProcessorActor** | Processes, transforms, and controls message flow (inject data, delay, split/collect arrays, dedupe, filter, fork/forkJoin, callbacks). **Important:** Always has only `SPRTdefault` sourcePort—fork uses multiple edges to create parallel paths, not multiple sourcePorts. | [message-processor-actor.md](references/message-processor-actor.md) |
| **WebhookResponseActor** | Sends custom HTTP responses back to WebhookTriggerActor callers | [webhook-response-actor.md](references/webhook-response-actor.md) |
| **CallableResponseActor** | Returns data from sub-flows back to parent flows (CallFlowActor). **Only valid in flows triggered by CallableTriggerActor.** | [callable-response-actor.md](references/callable-response-actor.md) |
| **CallFlowActor** | Invokes sub-flows by calling a CallableTriggerActor in another canvas/workspace | [call-flow-actor.md](references/call-flow-actor.md) |
| **InterfaceActor** | Renders a web form/page mid-workflow with two output ports: Meta (URL info on render) and Event (form submission data) | [interface-actor.md](references/interface-actor.md) |
| **SendEmailActor** | Sends text/HTML emails with optional attachments | [send-email-actor.md](references/send-email-actor.md) |
| **CollectionActor** | Persistent structured storage organized into named collections with labels, TTL, queries, batch operations, and transactions. Recommended for all new storage needs. **One collection per app** — model all entity types with key prefixes ([single-collection design](references/collection-api.md#single-collection-design)). | [collection-actor.md](references/collection-actor.md) |
| **StreamActor** | Append-only, ordered, cursor-addressed record logs — event ingestion, audit trails, activity feeds, and incremental processing that resumes from a persisted cursor. Reads return **one bounded page**, never the stream. **Streams must be created before use** and **expire one hour after the last append** unless created `persistent: true` or with an explicit `idleTtlSeconds`. Use for "what happened, in order"; use CollectionActor for "the current value of X" ([Collections vs Streams](references/stream-api.md#collections-vs-streams)). | [stream-actor.md](references/stream-actor.md) |
| **McpServerActor** | Exposes its child tool actors as an [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server endpoint that external AI agents (Claude Desktop, Cursor, custom agents) can connect to. Reuses the AiAgentActor tool-actor pattern (`aiAgentToolActorIds`, `${{aiInput}}` schema filtering) — the difference is that an external MCP client drives tool invocations instead of an internal LLM loop. | [mcp-server-actor.md](references/mcp-server-actor.md) |
| **CommentActor** | Non-functional UI element for adding notes, TODOs, and documentation to workflows | [comment-actor.md](references/comment-actor.md) |

> **⚠️ Before hand-building an integration actor — especially an `HttpRequestActor` — search the template catalog first.** BorgIQ ships vetted templates for most third-party actions (Gmail, Slack, GitHub, Google, Notion, …). Adapting a template is the single biggest defense against the most common failure mode: hand-writing an actor's `options`, `sourcePorts`, and schemas from scratch and getting them subtly wrong. **Only hand-build when no template fits.**
>
> ```bash
> borgiq templates apps --search "<vendor>" --json     # run a few queries, e.g. gmail, google, slack
> borgiq templates list --app-id TAPP... --json        # list that app's templates (paginates/sorts)
> borgiq templates get ATMP... --json \                # fetch the chosen template, then convert it:
>   | borgiq scaffold actor-from-template --output actor.json --print-id
> borgiq canvas-actors create <canvasSlugOrId> <actorId> --file actor.json --json
> ```
>
> In a bundle, write the `templates get` actor payload (already ExportedCanvasActor object shape) as `actor.yaml`, apply the [template fixups](references/cli/canvas-bundles.md#templates-and-the-starter-limitation) (fresh actor ID and trigger keys, keep `template` provenance), and complete the [three-edit rule](references/cli/canvas-bundles.md#add-and-remove-actors-the-three-edit-rule). `scaffold actor-from-template` produces the YAML-string CanvasActor mutation shape for the direct/batch fallback and performs those fixups automatically. Full flow: [Deploying and Testing with the CLI](#deploying-and-testing-with-the-cli).

### Choosing a Task Actor Type

**Important: DenoActor vs MessageProcessorActor**

Use **MessageProcessorActor** as the default for data transformations. It handles most transformation needs via YAML configuration and `${{ }}` expressions without custom code.

Use **DenoActor** (or PythonActor) ONLY when you need:
- **Fetch/HTTP requests** - Making API calls within custom logic
- **I/O operations** - File handling, network calls, or async operations
- **NPM/external libraries** - Using third-party packages not available in Q-lib
- **Complex imperative logic** - Loops, recursion, or stateful algorithms that can't be expressed declaratively

**Important: Prefer PythonActor when CLI tools are needed.** If the workflow needs to run command line applications available on the Lambda image (e.g., `git`, `aws-cli`, `jq`, `ImageMagick`, `tar`), use **PythonActor**. DenoActor has no shell access. PythonActor can invoke these tools via `subprocess.run()`.

If the task can be done with `${{ }}` expressions and Q-lib functions, use MessageProcessorActor.

**Important: Avoid overusing DenoActor for data transformation.** Any actor's `vars` and `outputs` configuration sections support `${{ }}` expressions. Use `vars` for intermediate computations and `outputs` for formatting the final result. Only reach for DenoActor when you need fetch, I/O, or imperative logic.

| Scenario | Use |
|----------|-----|
| Single API call | HttpRequestActor |
| Multiple sequential API calls that depend on each other | **DenoActor** or **PythonActor** |
| Data transformation with expressions and Q-lib | **MessageProcessorActor** (`inject`) |
| Data transformation requiring fetch, I/O, or NPM libraries | DenoActor or PythonActor |
| API call + data processing | DenoActor or PythonActor |
| Data science / ML operations (pandas, numpy, scikit-learn) | **PythonActor** |
| Custom Python code execution | PythonActor |
| Shell command execution (git, aws-cli, jq, ImageMagick, tar, etc.) | **PythonActor** |
| Text generation, summarization, or classification | AiActor |
| Structured data extraction from unstructured text | AiActor |
| Multi-turn conversations or chatbot interactions | AiActor |
| AI with function/tool calling (single call, returns tool calls) | AiActor |
| Autonomous AI agent with tool execution loop | **AiAgentActor** |
| Complex tasks requiring multiple tool calls | **AiAgentActor** |
| Research agents that search and synthesize information | **AiAgentActor** |
| AI-driven file/data processing (unzip, script, edit, re-zip) | **AiAgentActor** (built-in filesystem + bash) |
| AI agent that writes AND runs code | **AiAgentActor** |
| Resumable AI sessions across invocations | **AiAgentActor** (`sessionId`) |
| Agent needing MCP servers, daemons, or a full sandbox VM | AgentHarnessActor |
| Multi-agent systems with sub-agents | AiAgentActor (with CallFlowActor tools) |
| Route messages based on AI classification | AiRouterActor |
| Intent detection with branching workflows | AiRouterActor |
| If/else branching with boolean conditions | RouterActor |
| Switch-case routing based on data values | RouterActor |
| Inject constants or computed values | MessageProcessorActor (`inject`) |
| Delay workflow execution | MessageProcessorActor (`delayBySeconds`, `delayUntil`) |
| Process array items individually | MessageProcessorActor (`split`) |
| Recombine processed array items | MessageProcessorActor (`collect`) |
| Deduplicate messages | MessageProcessorActor (`dedupeByCount`, `dedupeByTime`) |
| Filter messages conditionally | MessageProcessorActor (`filter`) |
| Run parallel paths and join results | MessageProcessorActor (`fork`, `forkJoin`) |
| Human-in-the-loop approval workflows | MessageProcessorActor (`issueCallbackToken`, `waitForCallbackToken`) |
| Render LiquidJS templates | MessageProcessorActor (`renderTemplate`) |
| Extract data with regex | MessageProcessorActor (`regexExtract`) |
| Get file download URL or base64 content | MessageProcessorActor (`downloadFileUrl`, `downloadFileAsBase64`) |
| Return dynamic HTTP response to webhook caller | WebhookResponseActor |
| Return data from sub-flow to parent flow (requires CallableTriggerActor) | CallableResponseActor |
| Invoke a sub-flow and wait for response | CallFlowActor |
| Fire-and-forget sub-flow execution | CallFlowActor (`waitForResponse: false`) |
| Call sub-flows in other workspaces or canvases | CallFlowActor |
| Display a form mid-workflow and capture user input | InterfaceActor |
| Send a form URL via email/Slack for async user input | InterfaceActor |
| Build approval workflows without InterfaceTriggerActor | InterfaceActor |
| Send notification emails | SendEmailActor |
| Distribute reports via email with attachments | SendEmailActor |
| Send HTML formatted emails | SendEmailActor |
| Store structured data persistently | CollectionActor (`putItem`, `getItem`) |
| Model an app's entities (users, orders, comments, …) | CollectionActor — **one collection per app**, entity key prefixes ([single-collection design](references/collection-api.md#single-collection-design)) |
| Query stored data | CollectionActor (`query`) |
| Batch read/write operations | CollectionActor (`batchGetItem`, `batchWriteItem`) |
| Atomic counter increment/decrement | CollectionActor (`updateItem` with `atomicCounters`) |
| Transactional operations | CollectionActor (`transactWrite`, `transactGet`) |
| Job queue / task queue | CollectionActor (queue pattern — `putItem` to enqueue, `query` + `updateItem` to dequeue) |
| Record events in order (webhook events, audit trail, activity feed, agent progress) | StreamActor (`appendData`) — **not** `event:<timestamp>` Collection items |
| Process a backlog incrementally / resume where the last run stopped | StreamActor (`readStream` from a cursor persisted in a Collection; loop `nextCursor` while `hasMore`) |
| Only run when new records arrived | StreamActor (`getStreamInfo` — compare `tailCursor` to the persisted cursor) |
| Look up or update the current value of something | CollectionActor — a stream is not a place for current state |

## Trigger Actor Types

Trigger actors start workflows (flowruns). Each workflow must have exactly one trigger, but a canvas can contain multiple workflows, each with its own trigger.

| Type | Description | Reference |
|------|-------------|-----------|
| **ButtonTriggerActor** | Manual trigger via button click in the UI | [button-trigger-actor.md](references/button-trigger-actor.md) |
| **WebhookTriggerActor** | Receives HTTP requests at a unique webhook URL | [webhook-trigger-actor.md](references/webhook-trigger-actor.md) |
| **EmailTriggerActor** | Receives emails at a unique email address | [email-trigger-actor.md](references/email-trigger-actor.md) |
| **InterfaceTriggerActor** | Displays a web form and triggers on submission | [interface-trigger-actor.md](references/interface-trigger-actor.md) |
| **AppTriggerActor** | Hosts a web application (HTML/CSS/JS) with no form semantics. Does not emit messages. | [app-trigger-actor.md](references/app-trigger-actor.md) |
| **ScheduledTriggerActor** | Runs on a cron-based schedule | [scheduled-trigger-actor.md](references/scheduled-trigger-actor.md) |
| **UniversalTriggerActor** | Code-first trigger that fires on webhook requests, a cron schedule, or manual Invoke — user TypeScript (`receive(req: TriggerRequest)`) runs on every fire and branches on `req.trigger.type` | [universal-trigger-actor.md](references/universal-trigger-actor.md) |
| **CallableTriggerActor** | Invoked by parent flows (sub-flow entry point) | [callable-trigger-actor.md](references/callable-trigger-actor.md) |

### Choosing a Trigger Type

| Scenario | Use |
|----------|-----|
| Manual/ad-hoc execution | ButtonTriggerActor |
| External service notifications (GitHub, Stripe, Slack) | WebhookTriggerActor |
| Build an API endpoint | WebhookTriggerActor |
| Process incoming emails | EmailTriggerActor |
| User-facing forms and data collection | InterfaceTriggerActor |
| Web applications (SPA, dashboards, interactive tools) | AppTriggerActor |
| Periodic/scheduled tasks (hourly, daily, weekly) | ScheduledTriggerActor |
| One workflow fired by webhook **and** schedule (and manual testing) | UniversalTriggerActor |
| Custom code at trigger time (normalize, filter, dedupe, respond before emitting) | UniversalTriggerActor |
| Reusable sub-flows called by other workflows | CallableTriggerActor |

#### Universal Trigger vs Webhook Trigger (HTTP endpoints)

Both build HTTP endpoints, but they sit at opposite ends of a spectrum: a UniversalTriggerActor *is* the whole handler (request parsing, auth, storage, validation, and response all run inside its `receive` code), while a WebhookTriggerActor is the *entrance* to a multi-actor flow that does the work downstream.

| Decision | Use |
|----------|-----|
| The endpoint can fully handle request parsing, auth checks, Collection API calls, validation, and the response from its own code | **UniversalTriggerActor** (respond with `Signal.webhookRespond` under `options.webhook.respondImmediately: false`) |
| The request needs to enter a multi-actor flow — especially AiActor, integration actors (HttpRequestActor/template actors), routers, or a WebhookResponseActor | **WebhookTriggerActor** |
| One canvas exposes several endpoints with materially different latency, response, or orchestration needs | **Multiple triggers** — one per endpoint, mixing Universal and Webhook as each route requires |

**Rules of thumb:**

- **Self-contained CRUD / lookups → Universal.** If a route is "parse the request, read/write a Collection, return JSON," keep it inside one UniversalTriggerActor and respond from its code. No edges, no downstream actors.
- **Orchestration → Webhook.** The moment a route needs an LLM call, a third-party API, conditional routing, or a fan-out/fork, use a WebhookTriggerActor feeding the real actors and a WebhookResponseActor (or AiActor → WebhookResponseActor) for the reply.
- **Don't collapse endpoints into one Universal Trigger just to reduce actor count.** If even one route needs downstream actor orchestration, give that route its own WebhookTriggerActor rather than forcing AI/integration logic into trigger code. Mixed canvases (some Universal routes, some Webhook routes) are normal and correct.

**URL wiring note:** the two trigger types expose their URLs under **different context maps** — `${{ ctx.canvas.webhookTriggers.<msgVar>.url }}` for a WebhookTriggerActor, `${{ ctx.canvas.universalTriggers.<msgVar>.url }}` for a UniversalTriggerActor (which appears there only when `configuration.webhook.enabled: true`). The URL shape is identical; only the map differs.

See [universal-trigger-actor.md](references/universal-trigger-actor.md) and [webhook-trigger-actor.md](references/webhook-trigger-actor.md) for full configuration. For app frontends calling these endpoints, the `borgiq-react-app-builder` spoke owns the wiring (see [Web apps and forms — handed off to spokes](#web-apps-and-forms--handed-off-to-spokes)).

### Trigger Output

All triggers emit a message accessible to downstream actors via `msg.<trigger_msgVar>`. The message structure varies by trigger type—see the TypeScript schemas in [references/typescript/actor-schemas-triggers.md](references/typescript/actor-schemas-triggers.md) for exact definitions:

- **ButtonTriggerActor**: Emits the configured `options` payload
- **WebhookTriggerActor**: Emits `{ meta, method, headers, body, queryParams, rawBody?, response? }`
- **EmailTriggerActor**: Emits `{ messageId, from, to, subject, date, hasAttachments, textBody, htmlBody, attachments, headers }`
- **InterfaceTriggerActor**: Emits `{ meta: { submissionInterfaceId, user }, body: { ...field values... } }`
- **AppTriggerActor**: Does **not** emit messages (no downstream workflow). Hosts a web application only.
- **ScheduledTriggerActor**: Emits `{ triggeredAt, lastTriggeredAt }`
- **UniversalTriggerActor**: Emits whatever `results` the user code returns (free-form; `results: undefined` emits nothing)
- **CallableTriggerActor**: Emits the payload passed by the parent flow

**Important:** When a task requires multiple HTTP requests stitched together, use a **DenoActor** or **PythonActor** instead of chaining multiple HttpRequestActors. See [multi-api-examples.md](references/multi-api-examples.md) for TypeScript and Python examples.

## Common Actor Structure

All actors share a common YAML structure.

**Important: Do not confuse actor-level `schemas` with actor-specific schema options.**

- **`actors.ACTRxxxxx.schemas.inputs`** and **`actors.ACTRxxxxx.schemas.outputs`** define the actor's reusable interface—what inputs the actor accepts and what outputs it produces. These are used for templatization and validation at the actor boundary.

- **`actors.ACTRxxxxx.configuration.options.inputSchema`** or **`outputSchema`** are actor-specific configuration options with different purposes. For example, AiActor's `configuration.options.outputSchema` tells the AI model to produce structured output matching that schema—it's a directive to the LLM, not a definition of the actor's interface.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: HttpRequestActor  # or DenoActor, AiActor
    version: 1
    name: Actor Name Here
    msgVar: actor_name_here
    description: What this actor does
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        # Map upstream data and parameters here, e.g.
        userId: ${{ msg.fetch_user.id }}
        limit: 50
      # vars: (optional — only if you need to reuse a derived value within this actor)
      #   - intermediateName: ${{ Q.lo.camelCase(inputs.userId) }}
      options:
        # Actor-type-specific options — reference ${{ inputs.* }} (or ${{ vars.* }} if defined)
      outputs: ${{ results.body }}
      connection:
        key: connection-key-from-workspace
      error:
        if: ${{ error_condition }}
        retryIf: ${{ retry_condition }}
        message: ${{ error_message }}
    schemas:
      inputs:
        type: object
        properties:
          fieldName:
            type: string
            title: Field Title
            description: Field description
        required:
          - fieldName
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Actor Naming Conventions

Use concise, descriptive names with proper noun capitalization.

**Good names:**
- Fetch user profile from Gmail
- Create Issue in GitHub
- Process calendar events
- Transform data for Airtable

**Bad names:**
- Gmail: Fetch user profile (wrong format)
- Create Issue (missing context)
- Find users (too vague)

## Configuration Interpolation Order

BorgIQ actors are designed to be **templatized and reusable**. Configuration sections are processed in order:

1. **inputs** — The actor's parameter surface. **Map all upstream actor data here** using `${{ msg.<upstream_msgVar>.field }}`, `${{ ctx.* }}`, or `${{ err.* }}`. Every parameter the actor consumes should pass through `inputs` and be declared in `schemas.inputs`. Inputs are interpolated first.

2. **vars** — *Optional.* Intermediate values reused within **this actor's own** `options`/`outputs`. Only add `vars` when the same derived value is referenced from more than one place inside the actor (e.g. building an email body that's then base64-encoded and referenced from `options`). Can reference `inputs`. If the value is used once, inline it instead — `vars` is not a wiring layer.

3. **options** — Actor-specific configuration. Has access to `inputs`, `vars`, `msg`, `ctx`, and `err`.

4. **Actor executes** — Results are stored in `results`.

5. **error** — Error handling. Has access to `results`. Determines if the actor failed and whether to retry.

6. **outputs** — Output transformation. Only evaluated if no error. Transforms `results` for downstream actors.

### inputs vs vars — the rule

**Inputs are the wire.** `vars` is local scratch space. Mapping upstream `msg.*` data into `vars` is wrong even though both can hold any expression: it leaves the actor's declared input schema empty, breaks reusability, and forces `options`/`prompt`/`body` to reference `vars.X` instead of the actor's real parameter surface.

**Anti-pattern (do not generate this):**
```yaml
configuration:
  vars:
    - name: ${{ msg.normalize_lead.name }}        # WRONG — upstream data belongs in inputs
    - company: ${{ msg.normalize_lead.company }}
  inputs:
    name: ''                                       # WRONG — declared inputs left empty
    company: ''
  options:
    prompt: 'Research ${{ vars.name }} at ${{ vars.company }}'  # WRONG — should reference inputs
```

**Correct:**
```yaml
configuration:
  inputs:
    name: ${{ msg.normalize_lead.name }}
    company: ${{ msg.normalize_lead.company }}
  options:
    prompt: 'Research ${{ inputs.name }} at ${{ inputs.company }}'
# No vars needed — single-use values stay inline.
```

**Correct use of `vars` (intermediate reused inside the actor):**
```yaml
configuration:
  inputs:
    from: ${{ msg.trigger.from }}
    to: ${{ msg.trigger.to }}
    body: ${{ msg.trigger.body }}
  vars:
    - rawEmail:
        - 'From: ${{ inputs.from }}'
        - 'To: ${{ inputs.to }}'
        - ''
        - ${{ inputs.body }}
    - encoded: ${{ Q.toBase64(vars.rawEmail.join('\r\n')) }}
  options:
    body:
      raw: ${{ vars.encoded }}     # vars.encoded is reused; building it inline would duplicate logic
```

## BorgIQ Expressions

Use `${{ <javascript-expression> }}` for Deno-compatible JavaScript expressions. Only YAML values can contain expressions.

**Available:** `Q.*` utility functions (see [q-lib.md](references/q-lib.md)), all JavaScript web standard globals (`btoa`, `JSON.parse`, `Math.*`, array/string methods, etc.)

**Restrictions:** NO I/O operations (`fetch`, file system). Pure computation only.

**Examples:**
```yaml
url: https://api.example.com/users/${{ inputs.userId }}
body: ${{ Q.toJSON(inputs.data) }}
data: ${{ msg.previous_actor.body }}
```

## Context Variables

See [references/context.md](references/context.md) for full documentation.

| Variable | Description |
|----------|-------------|
| `inputs` | Actor input parameters |
| `msg` | Upstream actor messages (`msg.ActorName`) |
| `ctx` | Runtime context (org, workspace, canvas, flowrun, actor info) |
| `credentials` | Mapped credentials from workspace |
| `connection` | Single connection for authentication |
| `connections` | Multiple connections (access via `connections.auth`) |
| `results` | Response after actor invocation |
| `vars` | Computed variables |
| `err` | Error information from upstream actors |

For error handling patterns (continueOnError, split/collect, fork/forkJoin), see [error-handling.md](references/error-handling.md).

## Q-lib Functions

Access utility functions via `Q.*`. See [references/q-lib.md](references/q-lib.md) for complete reference.

**Common functions:** `Q.toJSON()`, `Q.toBase64()`, `Q.isHTTPStatusInRange()`, `Q.lo.*` (Lodash), `Q.dateFns.*` (date-fns)

## Actor Source Files

Code-running actors — **DenoActor, DenoTestActor, UniversalTriggerActor, PythonActor** — carry their source in `configuration.codeDir`: a list of `{path, content}` files forming a small project, a sibling of `options` and **never interpolated**.

```yaml
configuration:
  options: {}
  codeDir:
    - path: main.ts          # required entrypoint (main.py for PythonActor)
      content: |
        import type { Request, Response } from "@borgiq/actors";

        import { format } from "./lib/format.ts";

        export default async function receive(req: Request): Promise<Response> {
          return { results: format(req.inputs) };
        }
    - path: lib/format.ts
      content: |
        export const format = (inputs: unknown) => ({ inputs });
```

- Exactly one entry must be the **entrypoint**: `main.ts` for the three Deno-family types, `main.py` for PythonActor. Everything else is yours to arrange in folders.
- Import your own files relatively — `./lib/format.ts` in Deno (extension included), `from lib.format import format` in Python (packages need `__init__.py`). Imports may not leave the actor's own files.
- `${{ }}` inside source is literal text, never an expression: pass runtime values through `configuration.inputs` and read `req.inputs`.
- Some filenames are reserved by the runtime, and the tree is capped at 200 files / 1 MiB. Per-type details: [deno-actor.md → Code Files](references/deno-actor.md#code-files), [python-actor.md → Code Files](references/python-actor.md#code-files), [universal-trigger-actor.md → Code Files](references/universal-trigger-actor.md#code-files). In a canvas bundle the same tree is real files under the actor's `code/` directory ([canvas-bundles.md](references/cli/canvas-bundles.md#code-actor-project-trees)).
- Actors written before multi-file support carry a single `configuration.code` string instead. They keep running and convert on the next save; write `codeDir` for anything new, and never set both fields.

(ReactAppTriggerActor also uses `configuration.codeDir`, for a whole Vite project — see the `borgiq-react-app-builder` spoke. AppTriggerActor keeps `configuration.options.html` / `.css` / `.script`.)

## Actor Memory

Code-running actors (DenoActor, PythonActor, UniversalTriggerActor) carry two
key-value memory stores, **STM** and **LTM**. Every actor has **both**, always
present on `req.memory`. The read/write API is **identical** for the two — they
differ only in **lifetime**:

| Type | Field | Lifetime / Scope | Use for |
|------|-------|------------------|---------|
| **STM** (Short-Term Memory) | `req.memory.stm` | One flowrun, this actor. **Reclaimed when the flowrun completes.** | Run-local state across messages within a single run (counters, running totals, fork/join bookkeeping, dedup sets) |
| **LTM** (Long-Term Memory) | `req.memory.ltm` | **Survives across all flowruns** for this actor (until you overwrite it) | State that must outlive a run: last-processed timestamp/cursor, registered webhook IDs, poll checkpoints |

The split is deliberate: STM is **garbage-collected promptly once its flowrun
ends**, while LTM is kept indefinitely — separating them keeps that cleanup cheap.
So **default to STM for anything run-local** (it cleans itself up) and reserve LTM
for the few values that genuinely must survive to the next run.

### The contract: value-in / value-out

Memory is **not** a mutable global. You **read** the current state from
`req.memory`, and **persist** changes by **returning** a `memory` object in the
`Response`. There is no other way to write it.

**Whatever you return for a half becomes the new stored value of that half — it
replaces, it does not merge.** Return `memory: { ltm: { cursor: 5 } }` and the
stored LTM becomes *exactly* `{ cursor: 5 }`; any other LTM key you held before is
gone. So always return the **complete** state you want to keep:

- **Read-modify-write: spread the prior half, then set your keys.** Build the next
  snapshot from `req.memory` so existing keys survive —
  `memory: { ltm: { ...req.memory?.ltm, cursor: 5 } }`. The spread is undefined-safe
  (an empty store spreads to nothing), so no `?? {}` guard is needed.
- **The two halves are independent.** `memory: { ltm }` replaces LTM and leaves STM
  untouched (and vice versa) — you only overwrite the half you actually return.
- **Omit `memory` entirely to change nothing.** `return { results }` persists no
  memory; both halves keep their stored values.
- **To clear a key, just don't include it** in the half you return (it's a replace,
  so omission drops it). To clear a whole half, return it empty: `{ ltm: {} }`.

```typescript
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // READ — optional chaining is undefined-safe; each store is empty on first use
  const lastCursor = req.memory?.ltm?.cursor ?? 0;

  // ...do work...

  // WRITE — return the FULL LTM you want stored (spread the old, set the new).
  // Returning bare `{ cursor: ... }` would drop every other LTM key.
  return {
    results: { lastCursor },
    memory: { ltm: { ...req.memory?.ltm, cursor: lastCursor + 1 } },
  };
}
```

When several keys change together, build the snapshot once with spread (or
`Object.assign`) — both treat a missing/undefined prior store as empty:

```typescript
const ltm = { ...req.memory?.ltm, cursor: lastCursor + 1, lastRunAt: req.inputs.triggeredAt };
// equivalently: const ltm = Object.assign({}, req.memory?.ltm, { cursor: ..., lastRunAt: ... });
return { results, memory: { ltm } };
```

### Enabling memory

Set the matching flag in the actor config. Returning a **non-empty** `stm`/`ltm`
for a store that isn't enabled is a **runtime error** (`STM is not enabled for the
actor` / `LTM is not enabled for the actor`):

```yaml
enableSTM: true   # required to write req.memory.stm
enableLTM: true   # required to write req.memory.ltm
```

This is another reason to return **only** the half you use — echoing back the
other, unenabled half trips this error. Enabling a store also **serializes** the
actor's message processing — one message at a time **within a flowrun** for STM,
and **across all flowruns** for LTM — so read-modify-write is race-free. (LTM
additionally roots the actor's temp-file directory at the actor scope so files
persist across runs; see [deno-actor.md → LTM and File Persistence](references/deno-actor.md).)

### Clean-code rules

1. **Default to STM; reach for LTM only for state that must survive the run.** STM is auto-reclaimed when the flowrun ends; LTM lives until overwritten.
2. **Return only the half you mutated** (`memory: { ltm }` or `memory: { stm }`); omit `memory` to persist nothing. The half you return replaces the stored value; the half you omit is left as-is.
3. **Return the full half — spread the prior state, then set your keys.** `memory: { ltm: { ...req.memory?.ltm, cursor } }` (spread is undefined-safe). What you return *replaces* the stored half, so a bare `{ cursor }` drops every other key; clear a key by omitting it from the snapshot.
4. **Read with optional chaining + default** — `req.memory?.ltm?.cursor ?? 0`; each store is empty on first use.
5. **Keep payloads small** — STM and LTM each have a size cap (`MAX_STM_PAYLOAD_SIZE` / `MAX_LTM_PAYLOAD_SIZE`). Store IDs/cursors, not whole datasets.

See [deno-actor.md → Memory Types](references/deno-actor.md#memory-types) for the
full reference and the LTM cursor example.

## Authentication

**Key rule:** An actor can have **only ONE connection**, but **multiple credentials**.

| Scenario | Use | Example |
|----------|-----|---------|
| Single auth source | `connection` | `auth: ${{ connection.auth }}` with `connection: { key: my-connection }` |
| Multiple auth sources | `credentials` with `source: connection` | Access via `credentials['name'].auth` in code |

See [auth-types.md](references/auth-types.md) for authentication type details and [flow-consolidation.md](references/flow-consolidation.md) for multi-connection patterns.

## Actor ID, Validation, and Post-Processing

For ID generation, validation, and post-processing, see [validation.md](references/validation.md).

**Quick reference:**
```bash
borgiq generate id actor                   # Generate actor ID
borgiq generate id edge                    # Generate edge ID
borgiq generate msgvar "Name"              # Generate msgVar
borgiq validate file.yaml                  # Validate YAML
borgiq validate file.yaml --post-process -i # Post-process
```

**Always validate and post-process** generated or edited YAML before presenting to the user.

## Generation Instructions

1. Return ONLY YAML, no explanations
2. Return ONE actor per request (unless building a complete flow)
3. Generate actor ID using the script before building
4. Use URL concatenation: `https://api.example.com/${{ inputs.id }}`
5. Only use `outputs` section if user requests custom output formatting
6. Use `|` for multiline strings with special characters, properly indented
7. Generate appropriate input schemas; keep them simple
8. Define input keys with empty values in the `inputs` section
9. Use 2-space indentation consistently
10. Always use `connection` for authentication
11. Never ask for secrets via `inputs`
12. For object schemas without defined properties, use `type: any`. For example `type: object\ntitle: UserInfo\ndescription: User information` should be `type: any` thus it would be written as `type: any\ntitle: UserInfo\ndescription: User information`
13. Actors are single-purpose; suggest variants for different options
14. Assume inputs may be missing; use `?.` operator for optional access
15. Expressions can be `undefined` `${{ inputs?.field }}` will be `undefined` if `inputs` or `inputs.field` is `undefined`
16. Handle empty arrays gracefully: `${{ inputs.field?.length > 0 ? inputs.field : undefined }}`
17. **For parallel workflows**, see [Concurrent Execution Model](#concurrent-execution-model) - use fork/forkJoin only when combining results, not for fire-and-forget
18. **Always validate generated YAML** using `borgiq validate` before presenting to the user
19. **Always include a CommentActor** at the top of every workflow with setup instructions, prerequisites, and a brief spec. Position it above all other actors (negative `y` value). Use markdown in the `description` field. See [comment-actor.md](references/comment-actor.md) for details.

## Workflow Composition

Actors can be chained together to form workflows:

```
TriggerActor -> ProcessActor -> OutputActor
```

Each downstream actor has access to all upstream messages via `msg`:
- `msg.trigger_actor` - Output from trigger
- `msg.process_actor` - Output from process step

When building complex automations, consider splitting into multiple actors:
- **HttpRequestActor** for API calls
- **DenoActor** for data transformation and business logic (TypeScript/JavaScript)
- **PythonActor** for data transformation, business logic, and data science tasks (Python)
- **AiActor** for AI-powered processing (summarization, classification, extraction)
- Chain them for reliability and reusability

First plan the workflow in a flowchart or sequence diagram. Then build the actors one by one. Use subagents to build the actors, to reduce the complexity of the main agent. Provide enough context to the subagents to build the actors.

**Converting flows to single actors:** When asked to consolidate a flow into a single actor, always use DenoActor. See [flow-consolidation.md](references/flow-consolidation.md) for connection handling patterns (single connection vs multiple connections via secrets).

### Sub-flow input contracts

When you build a sub-flow, treat its **CallableTriggerActor as a typed function signature**: declare the expected payload as `schemas.inputs` on the trigger (don't leave `schemas: {}`). Be aware that this schema is **not enforced at runtime** — the platform hands the caller's payload to the sub-flow as-is. The schema drives the editor (it renders the parent CallFlowActor's payload form and the manual-invoke UI) and documents the interface. Precisely because nothing validates the payload at the boundary, keep three things in lockstep by discipline: the parent CallFlowActor's `payload` keys, the trigger's `schemas.inputs`, and the downstream `${{ msg.<callable_msgVar>.<field> }}` reads. Drift between them does not fail fast — the missing or mistyped field arrives as `undefined` deep in the flow. See [callable-trigger-actor.md → Input Schema](references/callable-trigger-actor.md#input-schema--the-sub-flow-contract); for schema design, use the `borgiq-json-schema-builder` spoke.

## Actor Connections and Edges

For detailed documentation on edges, ports, positioning, and router configurations, see [edges-and-positioning.md](references/edges-and-positioning.md).

**Quick reference:**
- Edges connect actors via `sourcePortId` → `targetPortId` (always `TPRTdefault`)
- Generate edge IDs: `borgiq generate id edge`
- Position actors top-to-bottom: increment `y` by 200 (600 after Interface actors)
- RouterActor uses custom source ports (`SPRTxxxxxxx`) for conditional routing

## Workflow Examples

For complete workflow examples with full YAML, see [workflow-example.md](references/workflow-example.md). This includes:
- Webhook-based workflow with routing and conditional responses
- Edge configuration and actor positioning
- Router with multiple source ports

For advanced patterns (callback tokens, sub-flows, data storage, LTM), see [email-reply-workflow-example.md](references/email-reply-workflow-example.md).

## Workflow Patterns

For common workflow patterns including multi-source aggregation, fire-and-forget notifications, conditional branching, and more, see [workflow-patterns.md](references/workflow-patterns.md).

Key patterns:
- **Multi-Source Aggregation** - Use `fork`/`forkJoin` when combining results from multiple parallel API calls
- **Fire-and-Forget** - Direct connections without fork for independent parallel operations
- **Split/Collect** - Process array items individually and recombine results

### Web apps and forms — handed off to spokes

Building a custom app UI (dashboards, data explorers, SPAs — ReactAppTriggerActor, compiled server-side and served in a sandboxed iframe) is covered by the **`borgiq-react-app-builder`** spoke, which also owns maintaining legacy raw-HTML AppTriggerActor apps (configuration in [app-trigger-actor.md](references/app-trigger-actor.md)). Building forms, interface pages, signup flows, and surveys (InterfaceTriggerActor / InterfaceActor with form components) is covered by the **`borgiq-form-builder`** spoke. All auto-load when their domain appears in the user's request — see [Routing to Specialized Skills](#routing-to-specialized-skills) above.

Key wiring facts this hub still owns: **App and Webhook triggers connect via URL reference, not via edges.** For an AppTriggerActor, use `${{ ctx.canvas.webhookTriggers.<msgVar>.url }}` in its inputs. A ReactAppTriggerActor instead declares named **endpoints** targeting webhook-capable triggers and calls them with `useEndpoint('<name>')` — but the hub still builds the same `WebhookTrigger → task actors → WebhookResponse` backend chain. A webhook-enabled **UniversalTriggerActor** can also serve as an endpoint: its URL lives under `${{ ctx.canvas.universalTriggers.<msgVar>.url }}` (a separate map from `webhookTriggers`), and a self-contained route can respond from its own code via `Signal.webhookRespond` with no downstream chain — see [Universal Trigger vs Webhook Trigger](#universal-trigger-vs-webhook-trigger-http-endpoints).

### Collection migrations and provisioning

**One collection per app.** Model *all* of an app's entity types in a **single collection**, separated by key prefixes (`ticket:<id>`, `user:<id>`, `comment:<ticketId>:<at>`) — never one collection per entity type. The platform is already single-table (every collection in every workspace shares one DynamoDB table; a collection is one partition key, the item key is the sort key), so a prefix query (`ticket:*`) is exactly as fast and as isolated as a dedicated collection, and transactions, batch ops, and provisioning all stay simpler. One partition key carries an internal app of ~100,000 users with headroom **provided items stay small (children as `comment:<ticketId>:<at>` rows, never embedded arrays), you label only what you query by (each label is a GSI write), and no single item takes a write per request** — see the [capacity model](references/collection-api.md#capacity-model-what-one-collection-carries). Reads are eventually consistent: use what a write returns rather than re-reading it. Split into multiple collections **only** when a security/access boundary requires it, the user explicitly asks, or sustained writes approach the ~1,000 WCU/s partition limit (shard by collection). Because the Collections UI lists keys in byte order one page at a time, every app collection also carries a **`$meta` manifest** — a `$`-prefixed row sorts before every entity row, so it is the first thing anyone sees and it lists every key prefix in the collection (`$` is also the namespace for the `$migration:<id>` ledger and `$counter:<name>` rows). Full rules, the worked ticketing example, the `$meta` shape, and label guidance: [collection-api.md → Single-Collection Design](references/collection-api.md#single-collection-design).

**Collections are not implicit — a `putItem`/`query` against a slug that was never created fails with `COLLECTION_NOT_FOUND`.** So any app or flow backed by a [CollectionActor](references/collection-actor.md) needs a **provisioning step** that creates its collection and seeds default data before it serves traffic — and that step must be safe to re-run on every deploy and in every workspace.

Treat this like database migrations: when you design a collection-backed app, also design an **idempotent migration runner** that brings a workspace's storage up to the shape the app expects. Think through collection management as part of the build — don't bolt it on later. The pattern:

- Build the runner as a **UniversalTriggerActor fired with the `manual` trigger type only** — set `webhook.enabled: false` and `schedule.enabled: false` so it can never run off an HTTP request, a cron tick, a button, or a sub-flow call. Provisioning is a deliberate operator action.
- It holds an ordered list of migrations (each with a stable `id`), reads `$migration:<id>` ledger keys stored in the app's own collection, **skips already-applied** migrations, runs the rest in order, records each success, and finally rewrites the `$meta` manifest (the one `overwrite: true` write — it is derived from code) with the applied `schemaVersion` and the app's entity prefixes.
- The runner **ensures the app's collection exists** (`createCollection`, swallowing `COLLECTION_ALREADY_EXISTS`) and each migration **seeds defaults idempotently** — `putItem` is create-only by default, so catch `ITEM_ALREADY_EXISTS` on re-runs; never pass `overwrite: true` for seed data, which would clobber user-edited rows on every deploy.
- Run it via canvas Invoke or `borgiq triggers run` (the manual invoke) after deploying to a new workspace and after appending migrations. Re-running is always safe.

A collection-backed app shipped without a migration actor is a gap: it works in the dev workspace where collections were hand-created, then 404s in prod. Full guidance, the worked migration-manager trigger, and idempotency techniques are in [collection-migrations.md](references/collection-migrations.md).

### Streams: events in order, consumed by cursor

**Event-shaped data goes in a Stream, not a Collection.** Anything that is "what happened, in order" — webhook deliveries, an audit trail, an activity feed, an agent's progress — is appended to a [StreamActor](references/stream-actor.md) stream and consumed by walking a cursor forward. Modelling it as `event:<timestamp>` Collection items forces client-side ordering and pagination a stream gives you for free; modelling *current state* as a stream forces a replay to find the latest value. The decision table: [Collections vs Streams](references/stream-api.md#collections-vs-streams).

Three rules an agent must design around:

- **Streams are not implicit and they expire.** `appendData` against a slug that was never created fails with `STREAM_NOT_FOUND`, and a stream created with neither `persistent: true` nor `idleTtlSeconds` is hard-deleted one hour after its last append. Any app or scheduled consumer that depends on a stream creates it `persistent: true` in the same idempotent provisioning step as its collection ([collection-migrations.md](references/collection-migrations.md)); scratch logs get a TTL and clean themselves up.
- **`readStream` returns one bounded page, never the stream.** The page is budgeted by the workspace message-size limit and carries `nextCursor` and `hasMore`. Loop the cursor on a canvas edge for a backlog; persist it in the app's collection to resume across flowruns.
- **There is no "record arrived" trigger in v1.** A ScheduledTriggerActor calls `getStreamInfo`, compares `tailCursor` to the persisted cursor, and reads only when it moved — cheap enough for a one-minute schedule. Live views (a web app, a dashboard) tail the stream over SSE from the REST API instead.

Worked canvases for all three — ingestion, a chunked backlog loop, and the scheduled resumable consumer — are in [stream-actor.md](references/stream-actor.md); the full action, cursor, lifecycle, SDK, REST, and SSE reference is [stream-api.md](references/stream-api.md).

## Editing Existing Workflows

For detailed guidance on editing workflows, see [editing-workflows.md](references/editing-workflows.md).

**Key points:**
- When renaming actors, regenerate `msgVar` and update all `msg.<msgVar>` references
- Always validate and post-process after editing
- See reference for common editing patterns and checklists

## Migration from Other Platforms

For teams migrating automations from n8n, Zapier, or Make, see [migration-from-automation-platforms.md](references/migration-from-automation-platforms.md).

**Key principles:**
- **Most integrations → HttpRequestActor** — any SaaS with a REST API maps to a single HttpRequestActor with the appropriate Connection for auth
- **Data transformations → MessageProcessorActor** — use `inject` action with `${{ }}` expressions instead of platform-specific formatters or code nodes
- **Parallel execution is automatic** — no need to configure; all downstream actors run concurrently
- The reference includes concept mapping tables, expression migration guides, and per-platform examples

## Deploying and Testing with the CLI

> **Requires shell access (Claude Code, terminal).** If you don't have shell access (Claude.ai projects), skip this section — present the generated YAML to the user for manual deployment via the BorgIQ web UI.

The `borgiq` CLI (`@borgiq/cli`) lets you deploy workflows to the platform, trigger flows, monitor execution, and debug failures. For full reference, see [borgiq-cli.md](references/borgiq-cli.md).

**Install:** `npm install -g @borgiq/cli`

Canvas bundles require **`@borgiq/cli` >= 0.8.0**. Detect the capability directly and fall back to the direct path if missing:

```bash
borgiq bundle --help >/dev/null 2>&1 || echo "upgrade: npm install -g @borgiq/cli"
```

**End-to-end workflow:**

1. **Discover resources** — Check what connections, secrets, and assets exist in the workspace:
   ```bash
   borgiq connections list --json
   borgiq secrets list --json
   borgiq assets list --json
   ```
   Use the returned keys in actor configurations. If a needed resource doesn't exist, instruct the user to create it with a specific key name.

2. **Discover actor types** — Check available actor types and their configuration schemas:
   ```bash
   borgiq actors list
   borgiq actors schema HttpRequestActor --json
   ```

   **Check the template catalog first** — when the user's ask matches an existing template (e.g. "send a Slack message", "open a GitHub issue", "summarize with OpenAI"), prefer adapting a template over hand-building the actor. Search supports name/description/tags, filters by type (`TASK`/`TRIGGER`) and template app, and paginates with `--page` / `--page-size`:
   ```bash
   borgiq templates list --search slack --type TASK --json
   borgiq templates apps --search slack --json                     # discover app ids
   borgiq templates list --app-id TAPP01... --page 2 --json        # filter + paginate
   borgiq templates get TMPL01... --json                           # fetch full actor payload
   ```
   The template's `actor` payload is in ExportedCanvasActor object shape. In a bundle, write it as `actor.yaml` with fresh IDs/trigger keys and the `template` provenance block per [the template fixups](references/cli/canvas-bundles.md#templates-and-the-starter-limitation), then follow the [three-edit rule](references/cli/canvas-bundles.md#add-and-remove-actors-the-three-edit-rule). For the direct fallback (`canvas-actors create` / `batch`), convert it to the CanvasActor YAML-string shape with `borgiq scaffold actor-from-template` (which performs those fixups automatically):
   ```bash
   ACTOR_ID=$(borgiq templates get TMPL01... --json \
     | borgiq scaffold actor-from-template \
         --name "My instance" --output actor.json --print-id 2>&1 >/dev/null)
   borgiq canvas-actors create CANV01... "$ACTOR_ID" --file actor.json --json
   ```
   See [borgiq-cli.md](references/borgiq-cli.md#browse-the-template-catalog-faster-than-building-from-scratch) for the search/paginate pattern and [cli-setup-scripts.md](references/cli/cli-setup-scripts.md#convert-a-template-to-an-actor-borgiq-scaffold-actor-from-template) for the full converter reference.

3. **Start the canvas bundle** — This is the `rails new` moment: every canvas is built and maintained as a bundle folder. Initialize a new one, or pull an existing canvas:
   ```bash
   # New canvas:
   borgiq bundle init ./my-flow.borgiq-canvas --name "My Flow" --slug my-flow
   # Existing canvas:
   borgiq bundle pull <canvasSlugOrId> ./my-flow.borgiq-canvas
   ```
   Initialize git and commit the baseline. Read [canvas-bundles.md](references/cli/canvas-bundles.md) before editing the bundle.

4. **Build in the bundle** — Design actors and wiring in `actor.yaml`, `code/*`, and `canvas.yaml` using the actor references. Mint IDs with `borgiq generate`. Adding an actor follows the [three-edit rule](references/cli/canvas-bundles.md#add-and-remove-actors-the-three-edit-rule): actor folder, `actors[]` index entry, `graph.nodes` entry — then wire it in `graph.edges`.

5. **Validate and push** — Commit, then deploy from the files:
   ```bash
   borgiq bundle validate ./my-flow.borgiq-canvas --strict
   borgiq bundle push ./my-flow.borgiq-canvas --create --auto-layout   # first deploy of a new canvas
   borgiq bundle push ./my-flow.borgiq-canvas                          # existing canvas; --dry-run to preview,
                                                                       # --auto-layout when actors were added/removed/rewired
   ```
   `bundle push` validates, applies only changed actors with three-way (content-hash + `editVersion`) conflict detection, and refreshes the local bundle.

6. **Validate on server** — Catch issues local validation can't detect (missing connections, invalid references):
   ```bash
   borgiq canvases validate <canvasSlugOrId> --json
   ```

7. **Layout** — `push --auto-layout` already arranges actors; to re-run it separately:
   ```bash
   borgiq canvases layout <canvasSlugOrId>
   ```

8. **Execute** — Trigger the flow and monitor:
   ```bash
   borgiq triggers run --canvas <canvasId> --actor-id <triggerActorId> --json
   borgiq flowruns status <flowrunId> --json    # poll until Completed
   borgiq flowruns summary <flowrunId> --json   # full execution summary
   ```

9. **Debug** — If something fails, inspect runtime data, fix the bundle files, and push again:
   ```bash
   borgiq flowrun-jobs runtime-data <jobId> --root-path ctx --json   # actor config
   borgiq flowrun-jobs runtime-data <jobId> --root-path inputs --json   # input data
   borgiq flowrun-results summaries --job-id <jobId> --json          # error details
   # Fix the responsible actor.yaml / code/* in the bundle, then bundle push.
   borgiq flowrun-jobs re-run --job-id <jobId> --json                # re-run with fixed config
   ```

### Fallback — direct document/batch workflow (no bundle)

Use this only when a bundle is not possible: no shell/filesystem access, a CLI without `borgiq bundle` that cannot be upgraded, or a one-off patch to a canvas nobody maintains locally. Never patch out of band when a local bundle is the source of truth — edit the bundle and push it instead.

**Two formats with different rules** for the configuration fields (`options`, `inputs`, `vars`, `outputs`, `secrets`, `error`) and `schemas.inputs`:

| Command | Format | Configuration fields |
|---|---|---|
| `canvases create-with-data` | ExportedCanvasData envelope (YAML or JSON) | Native objects |
| `canvas-actors create/update/batch` | CanvasActor mutation (JSON only) | Each configuration/schema field serialized as a **YAML string** |

**New canvas** — validate the generated `metadata` + `actors` document, then restructure it into the envelope: move `metadata.schemaVersion` to `data.schemaVersion`, nest `actors` under `data`, remove the now-empty `metadata` block, and add top-level `name`, `slug`, and `messageTTLInDays`:

```bash
borgiq validate outputs/my-flow.yaml
borgiq canvases create-with-data --file outputs/my-flow.yaml --json
```

**Existing canvas without a local bundle** — validate the actor definitions in document form first, then build `add`/`update`/`remove` operations. Each operation requires `type`, `actorId`, `timestamp` (epoch ms — omitting it is a 400), and `data` with YAML-string configuration fields:

```bash
borgiq canvas-actors batch <canvasSlugOrId> --file changes.json --json
```

See [cli-data-formats.md](references/cli/cli-data-formats.md) for field-by-field schemas and common mistakes, and `borgiq scaffold actor|actor-from-template|canvas|batch` to generate correctly-shaped payloads instead of hand-writing them.

See [borgiq-cli.md](references/borgiq-cli.md) for complete command reference, debugging workflows, and export/import patterns.

See [flowrun-job-states.md](references/flowrun-job-states.md) for understanding flowrun states, job states, and counters when interpreting CLI debug output.
