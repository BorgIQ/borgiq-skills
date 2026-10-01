# AI Agent Actor Reference

The AiAgentActor runs an autonomous AI coding agent (pi) with a private workspace filesystem, bash, and BorgIQ actors
as tools, in checkpointed serverless segments; a session continues across invocations via `sessionId`. Read it to
configure one: options, built-in tools, ports, sessions and runtime sizing. Tool wiring and MCP servers are in
[agent-tools.md](agent-tools.md), models in [ai-models.md](ai-models.md), exact types in
[typescript/actorSchemas/task/aiAgent.md](typescript/actorSchemas/task/aiAgent.md).

## Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [Built-in Tools](#built-in-tools)
- [Running Code with the Code Execution Tool](#running-code-with-the-code-execution-tool)
- [Tools and MCP Servers](#tools-and-mcp-servers)
- [Source Ports](#source-ports)
- [Sessions and Continuation](#sessions-and-continuation)
- [Runtime Requirements](#runtime-requirements)
- [Limitations](#limitations)
- [Common Patterns](#common-patterns)
- [Accessing Agent Data in Downstream Actors](#accessing-agent-data-in-downstream-actors)
- [Legacy: DeprecatedAiAgent](#legacy-deprecatedaiagent)

## Overview

The agent loops: it receives the task prompt (and, on continuation, the prior session state), decides which tools to
call, runs them against its private session workspace or as child flowrun jobs, and continues until the task is done.

- **Filesystem + bash**: built-in `read`, `write`, `edit`, `bash`, `grep`, `find`, `ls` tools run against a private
  session workspace. Seed it with `volumeZipFile`; receive it back as `outputZipFile` on the Done port.
- **Code execution (opt-in)**: with `enableCodeExecution`, a `code_execution` tool runs TypeScript/JavaScript the agent
  writes in its workspace with Deno.
- **Tools**: BorgIQ actors wired via `aiAgentToolActorIds`, and MCP servers.
- **Sessions**: re-invoking with the same `sessionId` restores the workspace and conversation from the last checkpoint.
- **No wall-clock cap**: the run is split into serverless segments, each bounded by the runtime's timeout. At each
  boundary the workspace and session state are checkpointed and the next segment resumes seamlessly, with no synthetic
  messages in the conversation. `meta.segments` on the Done port reports how many segments the run spanned.
- **Status streaming**: assistant turns, the model's thinking and tool results stream on the Status port.

Choose between AiActor, AiAgentActor and AgentHarnessActor with the `borgiq-agent-builder` skill's matrix. Start with
AiAgentActor; use AgentHarnessActor only for a harness CLI, stdio MCP servers, background processes, package installs
or a persistent full machine.

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
        description: Final result when the session ends
      - id: SPRTdefault
        name: Status
        description: Assistant turns and tool results while the agent runs
    configuration:
      inputs:
        # Wire upstream actor data DIRECTLY into inputs (not into vars).
        reportZip: ${{ msg.upload_trigger.file }}
        instructions: ${{ msg.upload_trigger.instructions }}
      options:
        model: claude-sonnet-5
        systemPrompt: |
          You are a data analyst. Work inside your workspace; the report
          archive is already extracted there.
        prompt: ${{ inputs.instructions }}
        volumeZipFile: ${{ inputs.reportZip }}   # extracted into the workspace; a later run on the same session re-applies it (resets those files)
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

## Options Reference

All options live under `configuration.options`.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | the runtime's default Anthropic model (the editor fills in `claude-sonnet-5`) | Always set it. A known agent model id, `<provider>/<model-id>`, or `<custom-provider-slug>/<model-id>` for a workspace [custom provider](custom-ai-providers.md) whose catalog entry does not say `agent: false`; see [ai-models.md](ai-models.md). LLM calls route through the BorgIQ AI gateway using the workspace's credential for that provider |
| `prompt` | string | — | **Required.** The task prompt for the agent |
| `systemPrompt` | string | — | Background instructions appended to the agent's system prompt. Put the role, conventions and the wired-tool inventory here; put the task in `prompt` |
| `thinkingLevel` | `off` \| `minimal` \| `low` \| `medium` \| `high` | `medium` | How much the model thinks before each turn. Clamped to what the selected model supports (a level on a non-thinking model is a no-op; a custom model needs `reasoning: true` in its catalog entry). Thinking is billed as output tokens, shows in the editor timeline, and streams as `reasoning` on the Status port; `off` stops paying for it, `high` suits hard multi-step work |
| `autoCompaction` | boolean | true | Summarise the conversation when it grows past the context budget, so a long session keeps running. `false` leaves only the emergency compaction after a context-overflow error. Each compaction emits an `ai-agent-notification` on the Status port |
| `compactionInstructions` | string | — | Extra focus for the compaction summary, e.g. what must never be dropped (`keep the list of files changed`) |
| `contextBudgetTokens` | integer (≥ 32000) | 200000 | How large the conversation may grow before it is compacted: compaction starts at 85% of this budget, capped at the model's context window. Raise it on a 1M-context model to keep more history at a higher input cost |
| `sessionId` | string | auto-generated | Session ID to continue or create (max 64 characters). Same ID = continue the session |
| `volumeZipFile` | BIQFile | — | Zip file extracted into the session workspace at session creation. Each later run that reuses the session with a zip extracts it again over the restored workspace: files at the paths it names are reset to the zip's version, other files are kept |
| `workingDirectory` | string | workspace root | Working directory for the agent, relative to the session workspace |
| `timeoutInMinutes` | integer | 30 | Session timeout in minutes, measured across segments |
| `maxLoopCount` | integer | unlimited | Maximum number of assistant turns |
| `allowedTools` | string[] | all | Allow-list of the always-on built-in tools (`read`/`write`/`edit`/`bash`/`grep`/`find`/`ls`). Empty = all allowed. Does not affect the Code Execution tool |
| `disallowedTools` | string[] | — | Deny-list of the same seven built-in tools. Does not affect the Code Execution tool |
| `enableCodeExecution` | boolean | **false** | Give the agent the `code_execution` tool ("Code Execution" in the editor), so it can run TypeScript/JavaScript it writes in its workspace with Deno. The tool's only switch. See [Running code with the Code Execution tool](#running-code-with-the-code-execution-tool) |
| `allowNet` | boolean | **false** | Allow outbound network access from the tool runtime. Applies to `bash` too — with it off, `bash` has no `curl` at all |
| `allowNetList` | string[] | — | Only these hosts/CIDRs allowed for tool-runtime egress (system endpoints always included). Takes effect only with `allowNet: true`. Mutually exclusive with `denyNetList` |
| `denyNetList` | string[] | — | Block these hosts/CIDRs for tool-runtime egress (system endpoints cannot be denied). Mutually exclusive with `allowNetList` |
| `env` | record | — | Environment variables exposed to tools and bash. Values encrypted in transit. Reserved names rejected: `HOME`, `PATH`, `TMPDIR`, `NODE_OPTIONS`, `LD_PRELOAD`, `LD_LIBRARY_PATH`, and anything starting with `AWS_`, `DENO_`, or `BORGIQ_` |
| `mcpServers` | object[] | — | MCP servers exposed to the agent as tools: `type: http` or `type: borgiq`; stdio is not supported here. See [agent-tools.md](agent-tools.md#mcp-servers-mcpservers) |
| `returnOutputZipFile` | boolean | true | Include the workspace zip in the done-port result |
| `returnSessionDataFile` | boolean | true | Include the pi session data zip in the done-port result |

Validation rules enforced before the session starts:

- `prompt` must be non-empty.
- `allowNetList` and `denyNetList` are mutually exclusive.
- `env` keys matching a reserved name (case-insensitive) are rejected.
- A wired tool actor whose `msgVar` collides (case-insensitively) with a built-in tool name (`read`, `write`, `edit`, `bash`, `grep`, `find`, `ls`, plus `code_execution` while `enableCodeExecution` is on) is rejected — rename the tool actor.

## Built-in Tools

The agent always has (subject to `allowedTools`/`disallowedTools`) seven built-in tools that operate on its private
session workspace, plus `code_execution` when `enableCodeExecution` is set:

| Tool | Purpose |
|------|---------|
| `read` / `write` / `edit` | Read, create, and surgically edit files in the workspace |
| `bash` | Run shell commands — an **in-process bash interpreter**, not a real shell (below) |
| `grep` / `find` / `ls` | Search and explore the workspace |
| `code_execution` | Run a TypeScript/JavaScript file from the workspace with Deno. **Only present when `enableCodeExecution: true`**; the allow/deny lists do not apply to it |

- These names are **reserved** — a wired BorgIQ tool actor may not use them as its `msgVar`. `code_execution` is
  reserved only while `enableCodeExecution: true`. `deno` is **not** reserved, so a DenoActor wired as a tool under its
  default `deno` msgVar is fine.
- Do not wire file-system tool actors: the built-ins already cover file work.
- To build a read-only agent, set `disallowedTools: [write, edit, bash]` and leave `enableCodeExecution` off (a script
  could otherwise write to the workspace).
- Bash runs with a minimal environment: your `options.env` entries are exposed; platform and cloud-provider credentials
  are not.

**`bash` cannot run other programs.** `bash`, `grep` and `find` run in-process as a TypeScript bash interpreter over
the workspace filesystem: there is no `/bin/bash` and no child process. No `python`, `node`, `git`, `curl`-the-binary,
package managers or PTY, and nothing can be installed; only the interpreter's own built-ins (`ls`, `cat`, `sed`, `awk`,
`grep`, `curl`, and the usual shell constructs) are available. So:

- **To run code, use the [Code Execution tool](#running-code-with-the-code-execution-tool).** Do not write a prompt
  that tells the agent to "run a Python script".
- **`curl` is a built-in of the interpreter**, and its egress obeys `allowNet`/`allowNetList`/`denyNetList`. With
  `allowNet` off (the default) there is no network at all and `curl` reports "command not found".

## Running Code with the Code Execution Tool

Set `enableCodeExecution: true`. The agent writes a script with `write`/`edit`, then calls `code_execution` with a
path:

```json
{ "path": "analyze.ts", "args": ["--verbose"] }
```

- `path` is relative to the working directory and must stay inside the workspace; `args` is optional and arrives as
  `Deno.args`.
- The tool returns stdout and stderr. Output over 50KB is truncated from the middle (the start and end are kept, so a
  stack trace survives); a non-zero exit comes back as an error with the diagnostics, so the agent can fix the script.
- **The file runs as a module.** Top-level code and top-level `await` run, but `import.meta.main` is **false**: a
  script shaped like a CLI (`if (import.meta.main) { main() }`) does nothing and reports success.
- **Imports must stay inside the workspace.** An import that resolves outside it, even through a symlink, is refused
  and the script does not run. Deno and Web built-ins (`fetch`, `crypto`, streams, `Deno.readTextFile`) and `node:`
  modules work; treat `npm:`, `jsr:` and `https:` imports as unavailable, since nothing can be downloaded or installed.
- **Same sandbox as the other tools:** the workspace and scratch directory only, the same network policy, your
  `options.env`, and no spawning of programs. Enabling the tool does not widen what the agent can reach.
- A run that would outlast the current segment is terminated and does **not** resume (unlike an interrupted actor or
  MCP tool call): the agent re-runs it after the boundary, so keep scripts restartable and check for partially written
  files. A per-call timeout also applies.
- Scripts share bash's at-least-once retry semantics ([Limitations](#limitations)): keep external side effects
  idempotent.

## Tools and MCP Servers

Wire BorgIQ actors as tools with `aiAgentToolActorIds`, and add MCP servers with `mcpServers` (`type: http` or
`type: borgiq`; no stdio): see [agent-tools.md](agent-tools.md). Specific to the AI Agent:

- A wired tool's `msgVar` must not be a [built-in tool name](#built-in-tools).
- Name each wired tool in `systemPrompt` with what it does; the agent chooses tools by name, description and schema.
- Put exactly-once API work in wired tool actors, not in bash + `curl` (bash is at-least-once).
- MCP tools are discovered at session start, and each call is bridged through BorgIQ, so it resumes across segments.
- The agent cannot answer MCP input requests: it runs headless, declares no `elicitation`, `sampling` or `roots`
  capability, and a server that needs one reports that it cannot proceed. Use an AgentHarnessActor if you need a harness
  CLI that can.
- A tool that declares an `outputSchema` has its structured result passed to the model as structured data.

## Source Ports

| Port ID | Name | Emits |
|---------|------|-------|
| `SPRTdone000` | Done | Once, when the session ends (completed, timeout, error, or max loop count) |
| `SPRTdefault` | Status | Assistant turns, tool results and notices while the agent runs |

Wire Done to the next task actor; wire Status to a UI or logging actor for real-time visibility.

### Done Port Output

| Field | Description |
|-------|-------------|
| `sessionId` | The session ID (pass it back in `options.sessionId` to continue this session) |
| `success` | Whether the execution succeeded |
| `result` | Final assistant message, or the error message on failure. May be absent: branch on `success` / `meta.endReason`, not on `result` |
| `outputZipFile` | Zip of the session workspace (omitted when `returnOutputZipFile: false`) |
| `sessionDataFile` | Zip of the pi session data, portable to the harness tier (omitted when `returnSessionDataFile: false`) |
| `meta.endReason` | `completed`, `timeout`, `error`, or `max-loop-count` |
| `meta.model` | The model used |
| `meta.segments` | How many serverless segments the run spanned |

The result type also declares an optional `meta.duration`; it is not set. Token usage is not reported on the Done
port; it is metered per segment into the workspace AI log.

### Status Port Output

| `type` | When | Fields |
|---|---|---|
| `ai-agent-loop` | Each assistant turn | `response`; `toolCalls` (`toolCallId`, `toolName`, `input`) when the turn calls tools; optional `reasoning`; `meta.cwd`, `meta.timestamp` |
| `tool-result` | Each tool call resolves | `toolCallId`, `toolName`, `output` (e.g. `{ type: json, value }`), `isError`, `meta` |
| `agent-harness-error` | The session ends unsuccessfully (Done still fires, with `success: false`) | `message`, `meta.timestamp` |
| `ai-agent-notification` | The runtime compacted the conversation | `notificationType: compaction`, `message` (`Compacted context: N → ~M tokens`), optional `title`, `meta` |

`reasoning` is the model's thinking for the turn. The platform clips it at 16 000 characters (a clipped one ends with
`… [thinking truncated]`). A turn in which the model only thought arrives as a **reasoning-only loop**: `response: ''`,
`toolCalls: []`, `reasoning` set, so a consumer that renders `response` should skip or collapse turns whose `response`
is empty. With `thinkingLevel: off`, or on a model that does not think, no loop carries `reasoning`.

## Sessions and Continuation

- **Starting**: leave `sessionId` empty to auto-generate one (returned on the done port), or set a custom ID (max 64 chars). Leave it blank for one-shot runs.
- **Continuing**: re-invoke the actor with the same `sessionId` — the workspace and full conversation state restore from the last checkpoint and the agent picks up where it left off. Works within a flow (loop back into the agent) and across flowruns. To continue in a later flowrun, persist the returned `sessionId` (e.g. in a Collection).
- **Session TTL**: 7 days, sliding — every session activity refreshes it. After the TTL lapses, the same `sessionId` starts a **clean fresh session** (deterministic; never a partial state).
- **Seeding and resetting files**: `volumeZipFile` is extracted into the workspace at session creation, and again by **every later run that reuses the session with a zip**. That includes a loop back into the agent within one flow, since each message into the actor is a new run. The workspace is restored from the last checkpoint, then the zip is extracted over it. Files at the paths the zip names are reset to the zip's version, even where the zip has a file and the workspace a folder of the same name, or the reverse. Files only in the old workspace are kept. Sending a zip is therefore a deliberate reset of those files: use it to hand a continuing session updated inputs. To keep the agent's edits, send the zip only on the first run, for example by wiring it to an input that is empty on later loops. Within one run the zip is applied once, so the agent's edits across its own long-running segments are kept. A zip that cannot be downloaded or extracted fails the run, with a message naming the zip, and leaves the session's previous workspace as it was.
- **Getting files out**: the done port carries `outputZipFile` (the workspace) and `sessionDataFile` (pi session data; portable — it can seed a harness-tier pi session).
- **Scope**: sessions are scoped to the actor instance (not shared across actors) and bound to the runtime they started on — repointing the actor at a different runtime starts fresh sessions.

## Runtime Requirements

The agent runs on the workspace's serverless runtime (or a per-actor runtime override):

- **Ephemeral storage sizes the workspace.** The durable workspace is capped at **20% of the runtime's ephemeral
  storage**. The 512 MB default yields only ~100 MB of workspace — **provision a runtime with ≥ 4 GB ephemeral storage
  (~800 MB workspace) for real agent work**. Exceeding the cap ends the session with `endReason: 'error'` (state is
  snapshotted first); a follow-up invoke with a cleanup prompt starts in a grace mode that lets the agent delete files
  before the cap re-enforces.
- **The runtime timeout is the segment length**, not the session limit. Each segment is bounded by the runtime's
  configured timeout (up to 14 minutes); total runtime is governed by `timeoutInMinutes`. Short runtime timeouts still
  work — they just checkpoint more often.
- **AI credential**: the workspace needs one for the model's provider — for a `<slug>/<model-id>` reference, a custom
  provider with that slug, at a public `https://` base URL (private-network endpoints are refused). A custom provider
  with no effective base URL is refused before the segment is dispatched.
- **Isolation**: agent segments share the workspace runtime's concurrency pool. For isolation, create a dedicated
  runtime and point the actor at it via the per-actor runtime setting.

## Limitations

- **Bash side effects are at-least-once.** If a segment dies before its checkpoint, the session retries from the
  previous checkpoint and re-runs any bash executed since then. The workspace stays consistent (it always restores from
  the checkpoint), but **external** side effects from bash (API calls, emails) may repeat — make them idempotent.
- **No background processes.** Daemons and dev servers started by bash do not survive a segment boundary; long-running
  listeners belong on the harness tier.
- **No stdio MCP servers**, no programs from `bash`, no PTY or interactive programs (see [Built-in Tools](#built-in-tools)).
- **Workspace size cap**: 20% of runtime ephemeral storage ([Runtime Requirements](#runtime-requirements)).

## Common Patterns

**File-processing agent** — the built-in tools cover unpack, transform, edit and re-zip without tool actors; add
`enableCodeExecution: true` when the work needs real code:

```yaml
options:
  model: claude-sonnet-5
  systemPrompt: |
    You are a data processor. The input archive is extracted in your workspace.
    Use bash built-ins for simple passes; for real computation write a TypeScript
    file and run it with the code_execution tool. Produce results as files.
  prompt: ${{ inputs.instructions }}
  volumeZipFile: ${{ inputs.archive }}
  enableCodeExecution: true
```

**Continuable session** — the first invoke returns an auto-generated `sessionId`; pass it back to continue:

```yaml
options:
  model: claude-sonnet-5
  prompt: ${{ inputs.followUpInstruction }}
  sessionId: ${{ inputs.sessionId }}   # empty on first call, set on follow-ups
```

**Read-only analysis agent**:

```yaml
options:
  model: claude-haiku-4-5
  thinkingLevel: off
  prompt: ${{ inputs.question }}
  volumeZipFile: ${{ inputs.dataZip }}
  disallowedTools: [write, edit, bash]
  returnOutputZipFile: false   # nothing to return; skip the zip
```

A research agent wires web-search and HTTP tool actors, and a multi-agent system wires sub-agents as CallFlowActor
tools: see [agent-tools.md](agent-tools.md).

## Accessing Agent Data in Downstream Actors

From the Done port:

```yaml
configuration:
  inputs:
    finalText: "${{ msg.report_agent.result || 'agent ended: ' + msg.report_agent.meta.endReason }}"
    succeeded: ${{ msg.report_agent.success }}
    endReason: ${{ msg.report_agent.meta.endReason }}
    workspaceZip: ${{ msg.report_agent.outputZipFile }}
    sessionId: ${{ msg.report_agent.sessionId }}   # store to continue the session later
```

From the Status port, read `reasoning` and `response` separately, since a loop may be reasoning-only:

```yaml
configuration:
  options:
    action: inject
    payload:
      eventType: ${{ msg.report_agent.type }}
      thinking: ${{ msg.report_agent.reasoning || '' }}
      content: "${{ msg.report_agent.type === 'ai-agent-loop' ? msg.report_agent.response : msg.report_agent.output }}"
```

A plain YAML value cannot hold `: ` (a ternary, or a string such as `'agent ended: '`), so quote such an expression.

## Legacy: DeprecatedAiAgent

`DeprecatedAiAgent` is the orchestrator-loop agent that carried the `AiAgentActor` type name until mid-2026: no
filesystem, bash or sessions. It is hidden from the palette and still runs; read or migrate it, never create one.
Options: `model` (default `gpt-6-luna`), `prompt` or `messages`, `systemPrompt`, `temperature` (0.2), `maxTokens`
(10000), `maxLoopCount`, `enableTodoTool`; no `outputSchema`. Tool wiring is the same. Done port: `response` (the whole
`BIQAiMessage[]` history; the final text is the last message's `content`) and `meta` (`model`, `usage`, `endReason`:
`done`, `max_loop_count_reached`, `max_output`); its Status loops carry `meta.model` and `meta.usage`. To migrate:
drop `temperature`, `maxTokens` and `enableTodoTool`; replace `messages` with `sessionId` continuation; set `model`
explicitly; downstream, read `result` instead of `response`; rename tools whose `msgVar` is a built-in name. Types:
[typescript/legacy/actorSchemas/task/deprecatedAiAgent.md](typescript/legacy/actorSchemas/task/deprecatedAiAgent.md).
