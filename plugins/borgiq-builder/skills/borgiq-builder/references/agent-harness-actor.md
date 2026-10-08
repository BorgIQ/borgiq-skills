# Agent Harness Actor Reference

The AgentHarnessActor runs a harness CLI (Claude Code by default; Codex, OpenCode or pi) in an isolated sandbox VM
with a full machine, session persistence and BorgIQ actors as tools. Anything a person can do at a terminal with that
CLI (write code, run commands, install packages, call APIs, use skills and slash commands) becomes a workflow node:
upstream actors trigger it and downstream actors use its results. Read it to configure one. Tool wiring and MCP
servers are in [agent-tools.md](agent-tools.md), models in [ai-models.md](ai-models.md), exact types in
[typescript/actorSchemas/task/agentHarness.md](typescript/actorSchemas/task/agentHarness.md).

## Contents

- [Overview](#overview)
- [Skills as a Workflow Node](#skills-as-a-workflow-node)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [Sandbox Providers and Network Control](#sandbox-providers-and-network-control)
- [Sandbox Layout and Working Directory](#sandbox-layout-and-working-directory)
- [Session Continuation](#session-continuation)
- [Tools and MCP Servers](#tools-and-mcp-servers)
- [Credentials and Environment Variables](#credentials-and-environment-variables)
- [Extracting Output Files](#extracting-output-files)
- [Source Ports](#source-ports)
- [Accessing Agent Harness Data in Downstream Actors](#accessing-agent-harness-data-in-downstream-actors)
- [Common Patterns](#common-patterns)

## Overview

The sandbox is provisioned from an external vendor (E2B or Daytona, **not** AWS Lambda). Inside it the harness has
full filesystem access, runs Bash commands and scripts (Python, Node.js), installs packages, keeps background
processes for the sandbox's lifetime, and gets a PTY. Network access is controlled by allow/deny lists enforced with
iptables.

| `harness` | CLI | Models | BorgIQ tools reach it as | Session data |
|---|---|---|---|---|
| `claude` (default) | Claude Code | Anthropic agent models | Skills in an auto-generated plugin, `~/borgiq-plugin/` | `~/.claude` |
| `codex` | Codex | OpenAI agent models | A BorgIQ MCP server in the sandbox | `~/.codex` |
| `opencode` | OpenCode | Every agent model | The same BorgIQ MCP server | `~/.local/share/opencode` |
| `pi` | pi | Every agent model | A generated pi extension (pi has no stdio MCP) | `~/.pi` |

A run:

1. provisions a sandbox, or reuses the session's hot one;
2. extracts `volumeZipFile` (if any) to `~/workspace/`;
3. starts the harness in the working directory with the prompt; it runs commands, writes files and calls tools;
4. on completion returns the workspace as `outputZipFile` and the harness session data as `sessionDataFile`;
5. keeps the sandbox hot for 5 minutes for fast continuation, then shuts it down.

Choose between the AI actors with the `borgiq-agent-builder` skill's matrix. Use the harness for a harness CLI itself
(skills, slash commands, plugins), stdio MCP servers, custom CLI tools, background processes (dev servers, daemons),
firewall-enforced isolation of every process, or heavy environments (large installs, big builds). It starts in tens
of seconds to minutes (sandbox provision plus harness install) and is billed by sandbox wall-clock time; for plain
file, script and tool-orchestration work, AiAgentActor starts in seconds on serverless billing.

## Skills as a Workflow Node

Codify the process once as skills, slash commands and project instructions (for Claude Code: `CLAUDE.md` and
`.claude/skills/`). Deliver them with the input data in a `volumeZipFile`, keep the `prompt` to *what* to do (the skills
encode *how*), and pull the results out of `outputZipFile` downstream. The same skill then produces the same kind of
output on every run, and updating the zip updates every workflow that uses it.

```yaml
# 1. Build the context zip (skills, instructions, input data)
ACTR01context:
  type: DenoActor
  name: Build Context
  msgVar: build_context
  configuration:
    codeDir:
      - path: main.ts
        content: |
          import JSZip from "npm:jszip@3.10.1";
          import type { Request, Response } from "@borgiq/actors";
          import { stashFile } from "@borgiq/actors";
          export default async function receive(req: Request): Promise<Response> {
            const zip = new JSZip();
            zip.file("CLAUDE.md", "# Instructions\nUse /analyze to process the input data.");
            zip.file(".claude/skills/analyze/SKILL.md", req.inputs.skillContent);
            zip.file("input/data.json", JSON.stringify(req.inputs.data));
            zip.folder("outputs");
            const zipBuffer = await zip.generateAsync({ type: "uint8array", compression: "DEFLATE" });
            const contextZip = await stashFile(zipBuffer, "context.zip", "application/zip");
            return { results: { contextZip } };
          }
    options:
      allowNet: true  # required for stashFile

# 2. Run the harness on it
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

The context DenoActor can also fetch skill directories (for example from GitHub) into the zip. Pass the API keys the
skills need through [credentials and `env`](#credentials-and-environment-variables).

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
        allowNet: true
        env:
          API_KEY: ${{ credentials.my_api_key }}
        returnOutputZipFile: true
        returnSessionDataFile: true
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

## Options Reference

All options live under `configuration.options`; only `prompt` is required.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `prompt` | string | — | **Required.** The task instruction sent to the harness |
| `harness` | `claude` \| `codex` \| `opencode` \| `pi` | `claude` | The harness CLI to run. Use the exact lowercase value (`claude`, not `Claude` or `BIQAgentHarnessType.Claude`) |
| `model` | string | the harness's first model | Must be valid for `harness`: `claude` takes the Anthropic agent models (default `claude-sonnet-5`), `codex` the OpenAI ones (default `gpt-6.1-sol`), `opencode` and `pi` any agent model (default `claude-sonnet-5`), with the credential of the model's provider. Enum-validated: no custom providers (`<slug>/<model-id>`); use AiAgentActor for those. See [ai-models.md](ai-models.md) |
| `systemPrompt` | string | — | Additional context and instructions for the harness |
| `sandboxProvider` | `e2b` \| `daytona` | `e2b` | The sandbox infrastructure provider |
| `sessionId` | string | auto-generated | Session ID to continue or create (max 64 characters) |
| `volumeZipFile` | BIQFile | — | Zip file to extract into `~/workspace/` |
| `workingDirectory` | string | — | Working directory relative to the workspace (e.g., `my-project`) |
| `timeoutInMinutes` | integer | `15` | Maximum execution time before the session is terminated; raise it for complex tasks |
| `maxLoopCount` | integer | unlimited | Maximum number of agentic loops (tool calls). Set it to bound runaway runs and cost |
| `maxTokens` | integer | — | Deprecated and ignored: not passed to the harness CLI, which applies its own output limit. Omit it |
| `temperature` | number | — | Deprecated and ignored: not passed to the harness CLI. Omit it |
| `allowedTools` | string[] | all tools | Allow-list of the harness's own tools (empty = all allowed) |
| `disallowedTools` | string[] | — | Deny-list of the harness's own tools |
| `allowNet` | boolean | `true` | Allow outbound network access from the sandbox |
| `allowNetList` | string[] | — | Only these hosts/CIDRs (plus system endpoints) are reachable. Ignored when `allowNet: false`, which blocks everything but system endpoints. Mutually exclusive with `denyNetList` |
| `denyNetList` | string[] | — | Block these hosts/CIDRs; everything else stays reachable. Ignored when `allowNet: false`. Mutually exclusive with `allowNetList` |
| `mcpServers` | object[] | — | MCP servers: `type: http`, `type: borgiq` or `type: stdio`; see [agent-tools.md](agent-tools.md#mcp-servers-mcpservers) |
| `env` | object | — | Environment variables (encrypted in transit) |
| `returnOutputZipFile` | boolean | `true` | Include the workspace zip in the Done result |
| `returnSessionDataFile` | boolean | `true` | Include the harness session data zip in the Done result. `returnClaudeSessionDataFile` is its deprecated alias |

Set both `return…` options to `false` for fast runs whose files nobody needs.

## Sandbox Providers and Network Control

- **E2B (default):** full internet access by default; Ubuntu-based; faster startup; pre-installed Claude CLI, Node.js
  22 LTS, uv, iptables, jq, zip. Best for tasks that need external resources, npm/pip installs and API integrations.
- **Daytona:** isolated network by default (no external internet); persistent volumes available. Best for sensitive
  code and internal-only workflows.

| Scenario | Properties | Effect |
|----------|-----------|--------|
| Allow all (default) | `allowNet: true` | Full outbound access |
| Block all outbound | `allowNet: false` | No network except AI provider & BorgIQ API |
| Block all except specific | `allowNetList: ["api.example.com"]` (leave `allowNet` unset or `true`) | Only the listed hosts |
| Allow all except specific | `allowNet: true`, `denyNetList: ["internal.corp.com"]` | All traffic except the listed hosts |

Network rules are enforced via iptables at sandbox launch. System endpoints (AI provider API, BorgIQ API) are always
allowed and cannot be denied.

## Sandbox Layout and Working Directory

```
$HOME/
├── workspace/                      # volumeZipFile is extracted here
├── .claude/                        # Claude Code: settings.json (settings, hooks), projects/ (history), .credentials.json
└── borgiq-plugin/                  # Claude Code: the BorgIQ tools plugin, when tools are connected
    ├── .claude-plugin/plugin.json
    ├── scripts/invoke.sh           # tool invocation script (+ .env with session credentials)
    └── skills/{tool-name}/SKILL.md # one skill per tool
```

| `workingDirectory` | The harness runs from | The output zip contains |
|---|---|---|
| not set | `~/workspace/` | Everything in `~/workspace/` |
| `my-project` | `~/workspace/my-project/` | Everything in `~/workspace/my-project/` |
| `/tmp/work` | `/tmp/work/` | Everything in `/tmp/work/` |

`volumeZipFile` always extracts to `~/workspace/`, whatever `workingDirectory` says.

## Session Continuation

- **First run**: leave `sessionId` empty (`''`) for an auto-generated ID, returned on the Done port. For
  deterministic continuation use a custom ID (`my-research-session-001`) or one from upstream data
  (`${{ msg.trigger.customerId }}`).
- **Later runs**: pass the same `sessionId` to continue with the sandbox state and conversation history.
- **One run per session at a time**: a run that targets an active session is queued, and queued runs start FIFO when
  the current one completes. The session lock expires after the timeout plus 5 minutes, so a crashed run cannot
  deadlock the session.
- **Lifecycle**: after a run the sandbox stays hot for 5 minutes. Then the workspace and harness session data are
  snapshotted, the sandbox is destroyed and the queue drained; the next run restores both into a new sandbox. Sessions
  expire after 7 days.

## Tools and MCP Servers

Wire BorgIQ actors as tools with `aiAgentToolActorIds`, exactly as for AiAgentActor, and add MCP servers with
`mcpServers` (`http`, `borgiq`, `stdio`): see [agent-tools.md](agent-tools.md). Specific to the harness:

- The tools reach each harness as the table in [Overview](#overview) shows. A call starts the tool actor, then polls
  BorgIQ for its result (with Claude Code, through the plugin's `invoke.sh`): up to 15 polls of 25 seconds, so a tool
  that takes longer than about six minutes fails the call.
- An `mcpServers` entry without `type` is **stdio**. The `pi` harness takes no stdio servers.
- Each harness CLI uses its own MCP client and negotiates the protocol version with the server; BorgIQ forwards the
  traffic unchanged. The BorgIQ tool server generated for Codex and OpenCode serves both protocol eras.
- For a remote server the sandbox receives only the BorgIQ gateway URL and its own session token, never the upstream
  URL or your credentials.

## Credentials and Environment Variables

Never put secrets in prompts. Map each one in `configuration.credentials` and pass it in `env`:

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

- `credentials` maps a local key to a workspace connection key; `${{ credentials.firecrawl }}` resolves the value at
  run time.
- Values are encrypted in transit to the sandbox, and the variables are visible to the harness and every process it
  spawns.

## Extracting Output Files

`outputZipFile` holds every file in the working directory. Pull out the ones you need with a downstream DenoActor
rather than processing the whole zip:

```yaml
ACTR01extract:
  type: DenoActor
  name: Extract Output
  msgVar: extract_output
  configuration:
    codeDir:
      - path: main.ts
        content: |
          import JSZip from "npm:jszip@3.10.1";
          import type { Request, Response } from "@borgiq/actors";
          import { mountFile } from "@borgiq/actors";

          export default async function receive(req: Request): Promise<Response> {
            const { file, paths } = req.inputs;
            if (!file) throw new Error("Missing required input: file");
            const filePath = await mountFile(file);
            const zip = await JSZip.loadAsync(await Deno.readFile(filePath));

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

## Source Ports

| Port ID | Name | Emits |
|---------|------|-------|
| `SPRTdone000` | Done | Once, when the run completes, times out or fails |
| `SPRTdefault` | Status | Real-time updates while the harness runs |

**Done port:**

| Field | Description |
|-------|-------------|
| `sessionId` | The session ID (auto-generated or the one you set) |
| `success` | Whether the run completed successfully |
| `result` | The final assistant text, or the error message |
| `outputZipFile` | The workspace zip (when `returnOutputZipFile` is true) |
| `sessionDataFile` | The harness session data zip (when `returnSessionDataFile` is true). The same file is also sent as the deprecated alias `claudeSessionDataFile` |
| `meta.endReason` | `completed`, `timeout`, or `error` |
| `meta.model` | The model used |

The result type also declares optional `meta.duration` and `meta.usage`; they are not set, so do not read them.

**Status port** (`type`, then fields; every message has `meta.timestamp`, most also `meta.cwd`):

| `type` | Fields |
|---|---|
| `agent-harness-loop` | `response`, `toolCalls` (`toolCallId`, `toolName`, `input`), optional `reasoning` |
| `tool-result` | `toolCallId`, `toolName`, `output` (e.g. `{ type: json, value }`), `isError` |
| `agent-harness-error` | `message`, optional `code` (e.g. `SANDBOX_DIED`) |
| `agent-harness-notification` | `notificationType` (e.g. `permission_prompt`, `idle_prompt`), `title`, `message` |
| `agent-harness-complete` | `message`, optional `response` (the final text) and `reasoning` |

`reasoning` is optional and clipped by the platform at 16 000 characters (a clipped one ends with `… [thinking truncated]`).
The Codex, pi and OpenCode harnesses buffer assistant text until the next tool call, so they post the turn's thinking
first as a **reasoning-only loop** (`response: ""`, `toolCalls: []`, `reasoning` set). Claude Code posts thinking on
the loop that carries the tool call, and the final text-only turn's thinking on `agent-harness-complete`. Anthropic
models whose thinking display is off return empty thinking, so those turns carry none. Old flowruns may carry Codex
reasoning as a notification with `notificationType: "reasoning"`.

## Accessing Agent Harness Data in Downstream Actors

```yaml
# From the Done port
configuration:
  inputs:
    sessionId: ${{ msg.research_agent.sessionId }}
    success: ${{ msg.research_agent.success }}
    outputZip: ${{ msg.research_agent.outputZipFile }}
    endReason: ${{ msg.research_agent.meta.endReason }}
```

```yaml
# From the Status port (quote the value: a plain YAML value cannot hold the ternary's ": ")
configuration:
  inputs:
    eventType: ${{ msg.research_agent.type }}
    content: "${{ msg.research_agent.type === 'agent-harness-loop' ? msg.research_agent.response : msg.research_agent.message }}"
```

## Common Patterns

```yaml
# Continue a session: the second run picks up the first one's project
options:
  prompt: Now add authentication middleware and a /users endpoint
  sessionId: my-project-session   # the first run used the same ID

# Sensitive code, no network
options:
  prompt: Review the uploaded codebase for security vulnerabilities
  volumeZipFile: ${{ msg.upload.file }}
  allowNet: false
  sandboxProvider: daytona
  timeoutInMinutes: 30

# BorgIQ tools only (the harness reaches them through BorgIQ even with allowNet: false)
options:
  prompt: Search for the topic, read the top pages, then write a summary to output.md
  allowNet: false
# aiAgentToolActorIds (sibling of options): the search and page-content tool actors

# Fast answer, no files back
options:
  prompt: What is 2 + 2? Reply with just the number.
  returnOutputZipFile: false
  returnSessionDataFile: false
  timeoutInMinutes: 5
```
