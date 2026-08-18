# Flowrun and Job States

Understanding flowrun states, job states, and counters is essential for monitoring execution and debugging failures via the CLI or API.

## Flowrun States

A flowrun represents a single execution of a workflow (canvas). Its state is determined dynamically from internal counters.

| State | Meaning | When |
|-------|---------|------|
| **Running** | Flow is still executing | At least one counter > 0 |
| **Completed** | Flow finished successfully | All counters are zero |
| **UserInterrupted** | Flow was manually stopped | User called `borgiq flowruns interrupt` or clicked Stop in the UI |

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
- If all counters are 0 but state is `Running` — this is a transient state; poll again.

## Job States

Each actor execution within a flowrun creates a "job." Jobs have these states:

| State | Meaning | Action |
|-------|---------|--------|
| **Queued** | Waiting to be processed by a worker | Normal — the actor hasn't started yet |
| **PostProcessing** | Actor finished executing, results being processed | Normal — messages are being routed downstream |
| **Emitted** | Completed successfully, messages sent downstream | Success — check `borgiq flowrun-results summaries --job-id <id>` for output |
| **Error** | Execution failed | Debug — use `borgiq flowrun-jobs runtime-data <id> --root-path ctx` and `--root-path inputs` to see what the actor received |
| **Delayed** | Waiting for a configured delay to expire | Normal for `delayBySeconds` / `delayUntil` MessageProcessorActor actions |
| **Waiting** | Waiting for external event (callback, interface, sub-flow) | Normal — check the corresponding counter in flowrun status |
| **RenderedInterface** | Interface data rendered, waiting for user interaction | Normal for InterfaceActor — user needs to submit the form |
| **Unknown** | State could not be determined | Investigate — may indicate a system issue |

## Using States with the CLI

### Monitor a flow until completion

```bash
# Trigger
borgiq triggers run --canvas <id> --actor-id <id> --json
# Returns flowrun.id

# Poll status (every 2-3 seconds)
borgiq flowruns status <flowrunId> --json
# Check: state === "Completed"

# Get full summary
borgiq flowruns summary <flowrunId> --json
```

### Debug a failed job

```bash
# 1. Find failures in summary
borgiq flowruns summary <flowrunId> --json
# Look for actors with job state "Error"

# 2. Get error details
borgiq flowrun-results summaries --job-id <jobId> --json

# 3. See what the actor received
borgiq flowrun-jobs runtime-data <jobId> --root-path ctx --json   # configuration
borgiq flowrun-jobs runtime-data <jobId> --root-path inputs --json   # interpolated inputs

# 4. Fix and re-run
borgiq canvas-actors batch <canvasSlugOrId> --file fix.json --json
borgiq flowrun-jobs re-run --job-id <jobId> --json
```

### Understand why a flow is stuck

```bash
borgiq flowruns status <flowrunId> --json
```

Check the counters:
- `callbackTokenWaitingCounter > 0` → waiting for external callback
- `interfaceSubmissionWaitingCounter > 0` → waiting for user form submission
- `callableResponseWaitingCounter > 0` → waiting for sub-flow to return
- `aiAgentToolWaitingCounter > 0` → AI agent tool in progress
