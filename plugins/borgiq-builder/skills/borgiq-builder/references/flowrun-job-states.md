# Flowrun and Job States

Understanding flowrun states, job states, and counters is essential for monitoring execution and debugging failures via the CLI or API.

## Flowrun States

A flowrun represents a single execution of a workflow (canvas). Its state is determined dynamically from internal counters.

| State | Meaning | When |
|-------|---------|------|
| `running` | Flow is still executing | At least one counter > 0 |
| `completed` | Flow finished — **not necessarily successfully** | All counters are zero. A flowrun whose actors failed still ends `completed`; its summary's `errors` array lists the failures |
| `user-interrupted` | Flow was manually stopped | User called `borgiq flowruns interrupt` or clicked Stop in the UI |

State values are lowercase on the wire.

### Flowrun Counters

When polling `borgiq flowruns status <id>`, the `counters` object tells you *why* a flow is still running:

| Counter | What it tracks |
|---------|---------------|
| `actorInboxMessagesCounter` | Messages queued for actor execution |
| `postProcessingCounter` | Actors that finished executing but results are still being processed |
| `delayedCounter` | Actors waiting for a delay to expire (`delayBySeconds`, `delayUntil`) |
| `callbackTokenWaitingCounter` | Actors waiting for an external callback token response |
| `interfaceSubmissionWaitingCounter` | Actors waiting for a user to submit an interface form |
| `callableResponseWaitingCounter` | Actors waiting for a sub-flow (CallFlowActor) to return |
| `aiAgentToolWaitingCounter` | Legacy `DeprecatedAiAgent` instances waiting for a tool actor to complete |
| `agentHarnessWaitingCounter` | Agent actors (AiAgentActor, AgentHarnessActor) waiting for agent execution |
| `agentHarnessToolWaitingCounter` | Agent actors (AiAgentActor, AgentHarnessActor) waiting for a tool invocation result |

**Debugging with counters:**
- If `callbackTokenWaitingCounter > 0` — the flow is waiting for an external system to call back. Check if the callback URL was sent correctly.
- If `interfaceSubmissionWaitingCounter > 0` — the flow is waiting for a user to fill out a form. The interface URL should have been emitted.
- If `callableResponseWaitingCounter > 0` — a sub-flow hasn't returned yet. Check the child flowrun's status.
- If `agentHarnessWaitingCounter > 0` or `agentHarnessToolWaitingCounter > 0` — an agent (AiAgentActor or AgentHarnessActor) is still executing or waiting on one of its tool actors.
- If `aiAgentToolWaitingCounter > 0` — a legacy `DeprecatedAiAgent` is waiting for one of its tool actors to finish.

## Job States

Each actor execution within a flowrun creates a "job." Jobs have these states (lowercase on the wire):

| State | Meaning | Action |
|-------|---------|--------|
| `queued` | Waiting to be processed by a worker | Normal — the actor hasn't started yet |
| `post-processing` | Actor finished executing, results being processed | Normal — messages are being routed downstream |
| `emitted` | Completed successfully, messages sent downstream | Success — read its output with `borgiq flowrun-messages list --canvas <canvas> --actor-id <id> --flowrun-id <id>`, then `borgiq flowrun-messages data <messageId>` |
| `error` | Retries exhausted, or an error that cannot be retried | Debug — see [Debug a failed job](#debug-a-failed-job) |
| `delayed` | Waiting for a configured delay to expire | Normal for `delayBySeconds` / `delayUntil` MessageProcessorActor actions |
| `waiting` | Waiting for external event (callback, interface, sub-flow) | Normal — check the corresponding counter in flowrun status |
| `rendered-interface` | Interface data rendered | Success state for InterfaceTriggerActor and InterfaceActor jobs; the submission runs as a separate job (for InterfaceTriggerActor, a separate flowrun) |
| `unknown` | State could not be determined | Investigate — may indicate a system issue |

## Using States with the CLI

### Monitor a flow until completion

```bash
# Trigger (canvas ULID, not slug; the manual trigger sends no payload)
borgiq triggers run --canvas <canvasId> --actor-id <triggerActorId> --json
# Returns { flowrun: { id, createdAt }, flowrunJob: { id }, actorId }

# Poll status (every 2-3 seconds)
borgiq flowruns status <flowrunId> --json
# Done when: .state != "running"

# Get full summary; success means .errors is empty
borgiq flowruns summary <flowrunId> --json
```

To run a flow with a payload, POST it to a WebhookTriggerActor's (or a webhook-enabled UniversalTriggerActor's) URL, `<apiUrl>/msg/<org>/<workspace>/<canvasId>/<actorId>/<triggerKey>` (`apiUrl` from `borgiq auth status --json`, `triggerKey` from the actor's `configuration.webhook`); the flowrun ID comes back in the `X-BIQ-Flowrun-Id` response header. `borgiq flowrun-jobs test-run --canvas <canvasId> --actor-id <actorId>` runs one actor on the latest message its upstream actors emitted (`--publish` passes its output on).

### Debug a failed job

```bash
# 1. Find failures in summary: the .errors array ({ actorId, actorName, jobId, error }), jobs in state "error"
borgiq flowruns summary <flowrunId> --json

# 2. Get error details, one entry per attempt
borgiq flowrun-results summaries --job-id <jobId> --json

# 3. See the message the job received (msg.<msgVar> of each upstream actor)
borgiq flowrun-jobs source-message <jobId> --json          # { sourceFlowrunMessage: { id, messageType } }
borgiq flowrun-messages data <sourceFlowrunMessageId> --json

# 4. Fix and re-run (same flowrun, same input, current configuration)
borgiq canvas-actors batch <canvasSlugOrId> --file fix.json --json
borgiq flowrun-jobs re-run --job-id <jobId> --json
```

`borgiq flowrun-jobs runtime-data <jobId> --root-path <path>` accepts three paths: `ctx` (the run context: org, workspace, canvas, flowrun, trigger and actor ids and names — not the actor's configuration or secrets), `trigger` (the trigger event; trigger actors' jobs only) and `inputs` (the tool-call input; only jobs that ran as an agent or MCP tool call). The CLI's help also lists `request` and `user`; the API rejects both. `borgiq flowrun-results data <resultId>` fails against the current API, which requires a `rootPath` query the CLI does not send; read what a job emitted with `flowrun-messages` instead.

### Understand why a flow is stuck

```bash
borgiq flowruns status <flowrunId> --json
```

Check the counters:
- `callbackTokenWaitingCounter > 0` → waiting for external callback
- `interfaceSubmissionWaitingCounter > 0` → waiting for user form submission
- `callableResponseWaitingCounter > 0` → waiting for sub-flow to return
- `agentHarnessWaitingCounter > 0` or `agentHarnessToolWaitingCounter > 0` → an AiAgentActor or AgentHarnessActor is running or waiting on a tool
- `aiAgentToolWaitingCounter > 0` → a legacy DeprecatedAiAgent tool call in progress
