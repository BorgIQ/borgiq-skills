# Run, monitor and debug a flowrun

How to start a flowrun from the CLI, poll it to the end, read what each actor received and emitted, and debug a
failed job. States are lowercase, and a `completed` flowrun is not necessarily a successful one: read the summary's
`errors`. On a deployed workspace every run executes the canvas's active build ([deployment.md](deployment.md)).

## Contents

- [Run a flow](#run-a-flow)
- [Flowrun states and counters](#flowrun-states-and-counters)
- [Poll until done](#poll-until-done)
- [Job states](#job-states)
- [What an actor received and emitted](#what-an-actor-received-and-emitted)
- [Debug a failed job](#debug-a-failed-job)

## Run a flow

```bash
borgiq triggers run --canvas <canvasId> --actor-id <triggerActorId> --json
# { flowrun: { id, createdAt }, flowrunJob: { id }, actorId }
```

`triggers run` fires the named trigger with **no payload**; it has no payload option. `--canvas` takes the ULID, not
the slug (`metadata.id` from `borgiq canvases get <slug> --json`). List a canvas's triggers with
`borgiq canvas-actors list <canvas> --json`.

**With a payload**, POST it to the trigger's webhook URL. Only a WebhookTriggerActor, or a UniversalTriggerActor with
`webhook.enabled: true`, has one: `<apiUrl>/msg/<org>/<workspace>/<canvasId>/<actorId>/<triggerKey>`, with `apiUrl`,
the org and the workspace from `borgiq auth status --json` and `triggerKey`, `authorizationLevel` and
`allowedMethods` (default POST) from the actor's `configuration.webhook`. The flowrun ID comes back in the
`X-BIQ-Flowrun-Id` response header. Authorization level `public` (or none) needs no credentials; `apiKey` and
`appsAndApiKey` need `Authorization: Bearer <token>` with a personal access token the user supplies (never the CLI's
stored token); `apps` accepts only app tokens, so test it through its app.

**One actor:** `borgiq flowrun-jobs test-run --canvas <canvasId> --actor-id <actorId> --json` runs it on the latest
message its upstream actors emitted; `--publish` passes its output on to connected actors.

**Earlier flowruns:** `borgiq flowruns list --canvas <canvas> --json` returns the 10 newest (`id`, `createdAt`;
`--page-size`, `--all` for more). It has no outcome filter: a failed flowrun is one whose summary has `errors`.

## Flowrun states and counters

A flowrun is one execution of a canvas; its state is computed from its counters.

| State | Meaning |
|---|---|
| `running` | At least one counter is above zero |
| `completed` | Every counter is zero. **Not necessarily a success**: a flowrun whose actors failed still ends `completed`, with the failures in its summary's `errors` |
| `user-interrupted` | Stopped with `borgiq flowruns interrupt <flowrunId>` (`-y` skips the prompt) or Stop in the UI |

`borgiq flowruns status <flowrunId> --json` returns `state` and `counters`, which say why a flowrun is still running:

| Counter | Above zero while |
|---|---|
| `actorInboxMessagesCounter` | messages are queued for an actor |
| `postProcessingCounter` | finished actors' results are being processed |
| `delayedCounter` | an actor waits out a delay (`delayBySeconds`, `delayUntil`) |
| `callbackTokenWaitingCounter` | an actor waits for an external callback: check the callback URL was sent correctly |
| `interfaceSubmissionWaitingCounter` | an actor waits for a person to submit an interface form (its URL should have been emitted) |
| `callableResponseWaitingCounter` | a CallFlowActor waits for its sub-flow: check the child flowrun |
| `agentHarnessWaitingCounter` | an AiAgentActor or AgentHarnessActor is working |
| `agentHarnessToolWaitingCounter` | such an agent waits for one of its tool actors |
| `aiAgentToolWaitingCounter` | a legacy `DeprecatedAiAgent` waits for one of its tool actors |

## Poll until done

Poll `flowruns status` every few seconds (back off: 3, 5, 10 s) while `state` is `running`, then read the summary:

```bash
while [ "$(borgiq flowruns status "$FLOWRUN_ID" --json | jq -r .state)" = running ]; do sleep 5; done
borgiq flowruns summary "$FLOWRUN_ID" --json | jq '{state, errors}'
```

The summary has `state`, `actors[]` (each with `jobs[]`: `jobId`, `state`, `status`, `error`, `resultId`, timing) and
`errors[]` (`actorId`, `actorName`, `jobId`, `error`). **The flowrun succeeded only if `state` is `completed` and
`errors` is empty.** An actor missing from `actors[]` never ran, often because it is downstream of a failure. A
flowrun that waits for a callback or a form submission (a human step) stays `running`: report that instead of polling
on.

## Job states

Each actor execution in a flowrun is a job.

| State | Meaning |
|---|---|
| `queued` | Waiting for a worker; the actor has not started |
| `post-processing` | The actor finished; its messages are being routed downstream |
| `emitted` | Success: its messages went downstream ([read them](#what-an-actor-received-and-emitted)) |
| `error` | Retries exhausted, or an error that cannot be retried: [debug it](#debug-a-failed-job) |
| `delayed` | Waiting out a MessageProcessorActor `delayBySeconds` / `delayUntil` |
| `waiting` | Waiting for an external event (callback, interface, sub-flow): see the matching counter |
| `rendered-interface` | Success for InterfaceTriggerActor and InterfaceActor jobs: the page was rendered. The submission runs as a separate job (for an InterfaceTriggerActor, a separate flowrun) |
| `unknown` | The state could not be determined: possibly a system issue |

## What an actor received and emitted

```bash
# Emitted: the actor's messages in a flowrun (the 10 newest), then one message's { msg, err }, keyed by msgVar
borgiq flowrun-messages list --canvas <canvas> --flowrun-id <flowrunId> --actor-id <actorId> --json
borgiq flowrun-messages data <messageId> --json          # the actor's own output is msg.<msgVar>

# Received: the message the job was given, i.e. msg.<msgVar> of each upstream actor
borgiq flowrun-jobs source-message <jobId> --json        # { sourceFlowrunMessage: { id, messageType } }
borgiq flowrun-messages data <sourceFlowrunMessage.id> --json
```

- `borgiq flowrun-jobs list --canvas <canvas> --actor-id <actorId> [--flowrun-id <id>] --json`: an actor's jobs,
  newest first.
- `borgiq flowrun-results summaries --job-id <jobId> --json`: one entry per attempt, with `status` (`success` or
  `error`), timing and the error.
- `borgiq flowrun-jobs ai-timeline <jobId> --json`: an AiAgentActor job's tool-use timeline.
- `borgiq flowrun-jobs runtime-data <jobId> --root-path <path> --json` takes three paths: `ctx`, the run context (org,
  workspace, canvas, flowrun, trigger and actor ids and names; not the actor's configuration or secrets); `trigger`,
  the trigger event (webhook request, schedule time, …), on trigger actors' jobs only; `inputs`, the tool-call input,
  only on jobs that ran as an agent or MCP tool call. CLI X.Y.Z and later reject any other value; older CLIs also list
  `request` and `user` in the help, and the API rejects both.
- `borgiq flowrun-results data <resultId> --root-path <memory|messages> --json` (CLI X.Y.Z or later) returns one root
  of an attempt's result: `memory`, the actor's `{ ltm, stm }` as that attempt left it, or `messages`, what it emitted,
  keyed by source port id. `--root-path` is required. The `resultId` is an `id` from `flowrun-results summaries`, or
  a job's `resultId` in `flowruns summary`. Older CLIs have no `--root-path` and get a 400 on every call; read a job's
  output with `flowrun-messages` there.
- The actor's current configuration: `borgiq canvas-actors get <canvas> <actorId> --json`, or its `actor.yaml` in the
  bundle.

## Debug a failed job

1. `flowruns summary`: the failed jobs are in `errors`, in job state `error`.
2. `flowrun-results summaries --job-id <jobId>`: every attempt's error. Read it literally; patterns and fixes are in
   [error-handling.md](error-handling.md) and the failing actor type's reference.
3. What the job received: `flowrun-jobs source-message`, then `flowrun-messages data`
   ([above](#what-an-actor-received-and-emitted)). A `${{ inputs.X }}` that is `undefined` means the upstream message
   has no `X`, or its msgVar was renamed.
4. Fix the actor: in a bundle, edit its files and push ([canvas-bundles.md](cli/canvas-bundles.md)); without one,
   `canvas-actors update` or `batch` ([cli-data-formats.md](cli/cli-data-formats.md)). On a deployed workspace, build
   the canvas too, or the fix never runs.
5. `borgiq flowrun-jobs re-run --job-id <jobId> --json` runs the job again in the same flowrun on the same input with
   the current configuration (on a deployed workspace, the active build); `--no-publish` keeps its output from
   connected actors. Judge it by the actor's newest job in `flowruns summary`: the original job stays in `errors`.
