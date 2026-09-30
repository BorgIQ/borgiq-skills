# Choosing Actors

Which task actor or trigger fits a scenario, and when an HTTP endpoint is a UniversalTriggerActor or a
WebhookTriggerActor. Read it when you plan a flow and are unsure which actor type a step needs; each type's options
are in its own reference.

## Contents

- [Rules](#rules)
- [Task actors](#task-actors)
- [Trigger actors](#trigger-actors)
- [Universal Trigger vs Webhook Trigger](#universal-trigger-vs-webhook-trigger)

## Rules

- Search templates, and recipes for multi-actor flows, before hand-building an integration
  ([borgiq-cli.md](borgiq-cli.md)).
- Transform data with a MessageProcessorActor (`inject` with `${{ }}` and Q-lib) by default. Non-code actors can also
  compute in `vars` and format in `outputs`; code actors skip both.
- Use a DenoActor or PythonActor only for fetch inside custom logic, I/O (files, network, async work), npm or other
  libraries, or imperative logic (loops, recursion, stateful algorithms). Several dependent API calls go in one of
  them, not a chain of HttpRequestActors.
- Shell tools on the runtime image (`git`, `aws-cli`, `jq`, ImageMagick, `tar`) need a PythonActor
  (`subprocess.run()`); a DenoActor has no shell.
- Between AI actors, the `borgiq-agent-builder` skill decides; the AI rows below are the short form.

## Task actors

| Scenario | Use |
|---|---|
| One API call | HttpRequestActor |
| Several API calls that depend on each other; an API call plus processing; transforms that need fetch, I/O or npm | DenoActor or PythonActor |
| Data science (pandas, numpy, scikit-learn), custom Python, shell commands | PythonActor |
| Generate, summarize or classify text; extract structured data; multi-turn chat; one call that returns tool calls | AiActor |
| An agent that loops over tool calls; research that searches and synthesizes; AI file work (unzip, script, edit, re-zip, with the built-in filesystem and bash); code it writes **and** runs (`enableCodeExecution: true`); a session resumed across invocations (`sessionId`); sub-agents (CallFlowActor tools) | AiAgentActor |
| stdio MCP servers, a harness CLI, daemons, or a full sandbox machine | AgentHarnessActor |
| Route by AI classification; intent detection | AiRouterActor |
| If/else or switch on data | RouterActor |
| Transform or inject values; continue only when a condition holds (`filter`); delay; split an array and recombine it (`split`, `collect`); join parallel paths (`fork` + `forkJoin`); dedupe; wait for a human or external callback (`issueCallbackToken` + `waitForCallbackToken`); LiquidJS templates; regex extraction; a file's download URL or base64 content | MessageProcessorActor ([actions](message-processor-actor.md#actions)) |
| Answer a webhook caller | WebhookResponseActor |
| Return data from a sub-flow (flow started by a CallableTriggerActor) | CallableResponseActor |
| Call a sub-flow and wait; fire and forget (`waitForResponse: false`); call one in another canvas or workspace | CallFlowActor |
| Show a form mid-flow, send its URL by email or Slack, or build an approval without an InterfaceTriggerActor | InterfaceActor |
| Send notification, report (with attachments) or HTML email | SendEmailActor |
| Store, read or query structured data; batch reads and writes; atomic counters (`updateItem` with `atomicCounters`); transactions (`transactWrite`, `transactGet`); a job queue (`putItem` to enqueue, `query` + `updateItem` to dequeue); an app's entities (one collection per app, entity key prefixes) | CollectionActor |
| Record events in order (webhook events, audit trail, activity feed, agent progress) | StreamActor `appendData`, not `event:<timestamp>` collection items |
| Process a backlog incrementally, resuming where the last run stopped | StreamActor `readStream` from a cursor persisted in a collection; loop `nextCursor` while `hasMore` |
| Run only when new records arrived | StreamActor `getStreamInfo`: compare `tailCursor` with the persisted cursor |
| Look up or update the current value of something | CollectionActor, never a stream |

## Trigger actors

Each workflow has exactly one trigger; a canvas can hold several workflows.

| Scenario | Use |
|---|---|
| Manual or ad-hoc runs | ButtonTriggerActor |
| Notifications from external services (GitHub, Stripe, Slack); an API endpoint that feeds a flow | WebhookTriggerActor |
| Incoming email | EmailTriggerActor |
| Forms and data collection for signed-in workspace members | InterfaceTriggerActor |
| Web apps: SPAs, dashboards, interactive tools | ReactAppTriggerActor (AppTriggerActor only for legacy raw-HTML apps) |
| Periodic tasks (hourly, daily, weekly) | ScheduledTriggerActor |
| One workflow fired by a webhook **and** a schedule (and manual tests); custom code at trigger time (normalize, filter, dedupe, respond before emitting) | UniversalTriggerActor |
| Reusable sub-flows called by other workflows | CallableTriggerActor |

## Universal Trigger vs Webhook Trigger

Both serve HTTP endpoints. A UniversalTriggerActor *is* the whole handler, run in its `receive` code; a
WebhookTriggerActor is the *entrance* to a multi-actor flow that does the work downstream.

| Decision | Use |
|---|---|
| The endpoint's own code can parse the request, check auth, call the Collection API, validate and respond | **UniversalTriggerActor**, responding with `Signal.webhookRespond` under `options.webhook.respondImmediately: false` |
| The request must enter a multi-actor flow: an AiActor, integration actors (HttpRequestActor or templates), routers, a WebhookResponseActor | **WebhookTriggerActor** |
| One canvas has endpoints with different latency, response or orchestration needs | **One trigger per endpoint**, Universal or Webhook as each route needs |

- **Self-contained CRUD and lookups → Universal**, with no edges. **Orchestration** (an LLM call, a third-party API,
  routing, a fork) **→ Webhook**, replying with a WebhookResponseActor (or AiActor → WebhookResponseActor).
- Don't merge endpoints into one UniversalTriggerActor to save actors; a mixed canvas is normal.
- **URLs sit in different context maps:** `${{ ctx.canvas.webhookTriggers.<msgVar>.url }}` for a WebhookTriggerActor,
  `${{ ctx.canvas.universalTriggers.<msgVar>.url }}` for a UniversalTriggerActor (listed only with
  `configuration.webhook.enabled: true`). The URL shape is the same.

Configuration: [universal-trigger-actor.md](universal-trigger-actor.md), [webhook-trigger-actor.md](webhook-trigger-actor.md).
