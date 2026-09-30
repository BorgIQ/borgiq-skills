# Migrating from Other Automation Platforms

Maps the building blocks of other workflow-automation tools (workflows, nodes, connectors, expressions, triggers, flow
control) to BorgIQ. Read it when rebuilding an existing automation in BorgIQ.

## Migration steps

1. **Inventory** each workflow: its trigger, its integrations, its transformations and its branches.
2. **Map the trigger** ([Triggers](#triggers)).
3. **Map integrations: templates and recipes first.** Search the template catalog for each connector action
   (`borgiq templates apps --search "<vendor>"`), and for a multi-step flow check `borgiq recipes list` (CLI 0.13.0 or
   later) ([borgiq-cli.md](borgiq-cli.md)). A template is a vetted, preconfigured actor, usually an HttpRequestActor.
   Only when none fits, hand-build an HttpRequestActor from the service's API docs (endpoint, method, headers) with a
   workspace connection ([http-request-actor.md](http-request-actor.md)).
4. **Map transformations** (formatter, set and code steps) to a MessageProcessorActor: field mapping → `inject` with
   `${{ }}`; arrays → `split` / `collect`; conditions → `filter` or a RouterActor
   ([message-processor-actor.md](message-processor-actor.md)).
5. **Map flow control.** Parallel paths are automatic; use `fork`/`forkJoin` only to combine results.
6. **Consider AI steps**: AiActor for classification, extraction or summarization; AiAgentActor for multi-step
   decisions with tools; AgentHarnessActor to run a harness CLI such as Claude Code on a process already written as
   skills.
7. **Test incrementally**: migrate one workflow at a time and compare its outputs.

## Concept map

| Elsewhere | BorgIQ |
|---|---|
| Workflow / scenario | **Canvas**, holding one or more workflows |
| Trigger | **Trigger actor**, one per workflow |
| Node / action / module | **Task actor** |
| Connection between steps | **Edge** |
| Execution / run | **Flowrun** |
| Credential / connection | **Connection** (and credentials) |
| Expression | **`${{ }}`** with [Q-lib](q-lib.md) |
| Code step | **DenoActor** or **PythonActor** |
| HTTP request step, SaaS connector | **Template**, else **HttpRequestActor** |
| If / filter | **RouterActor**, or MessageProcessorActor `filter` |
| Switch / paths / router | **RouterActor** (one source port per route) |
| Set / formatter | MessageProcessorActor `inject` |
| Loop / iterator + aggregator | MessageProcessorActor `split` / `collect` |
| Merge | MessageProcessorActor `fork` → paths → `forkJoin` |
| Wait / delay / sleep | MessageProcessorActor `delayBySeconds` / `delayUntil` |
| Wait for approval | MessageProcessorActor `issueCallbackToken` / `waitForCallbackToken` |
| Sub-workflow | **CallFlowActor** → **CallableTriggerActor** (+ **CallableResponseActor** to return data), across canvases or workspaces via `workspaceSlug` / `canvasSlug` |
| Tables / data store | **CollectionActor** |
| Send email | **SendEmailActor** (no SMTP setup) |
| — | **AiActor**, **AiAgentActor**, **AiRouterActor** (LLM classification routing), **AgentHarnessActor** |
| — | **ReactAppTriggerActor** (web app), **InterfaceTriggerActor** / **InterfaceActor** (forms), **WebhookResponseActor** (custom HTTP reply) |

## Authentication

Every connection auth type reaches an HttpRequestActor as `auth: ${{ connection.auth }}`: OAuth2 (refreshed and sent as
a bearer token), API key in a header or the query, basic auth, and custom headers or parameters
([auth-types.md](auth-types.md)).

## Expressions

| Need | BorgIQ |
|---|---|
| A field of an earlier step's output | `${{ msg.<msgVar>.field }}` |
| Now | `${{ Q.now() }}` |
| Array length | `${{ msg.<msgVar>.items.length }}` |
| Upper case | `${{ msg.<msgVar>.name.toUpperCase() }}` |
| Format a date | `${{ Q.dateFns.format(Q.now(), 'yyyy-MM-dd') }}` |

## Triggers

| Trigger elsewhere | BorgIQ |
|---|---|
| Webhook / catch hook | **WebhookTriggerActor** |
| Schedule / cron | **ScheduledTriggerActor** |
| Polling ("watch new rows") | **WebhookTriggerActor** when the service sends webhooks, else **ScheduledTriggerActor** → HttpRequestActor |
| Email received | **EmailTriggerActor** (a workspace email address) |
| Manual / button | **ButtonTriggerActor** |
| Form submission | **InterfaceTriggerActor** |
| Web app | **ReactAppTriggerActor** (AppTriggerActor for legacy raw-HTML apps) |
| Called by another workflow | **CallableTriggerActor** |

To pick among them: [choosing-actors.md](choosing-actors.md).

## Flow control and errors

- **Parallel branches** need no configuration: connect one actor to several. A router gives conditional branches.
- **Combining branches**: `fork` → paths → `forkJoin`, or `split` → item steps → `collect`
  ([fork/join](message-processor-actor.md#fork-actions)).
- **Error handling**: the `error` block (`if`, `retryIf`, `message`, `includeResult`) marks and retries failures;
  `continueOnError: true` routes the failure to `err.<msgVar>`, and a RouterActor branches on it
  ([error-handling.md](error-handling.md)).

A migrated connector step, when no template fits:

```yaml
type: HttpRequestActor
name: Send Slack message
msgVar: send_slack_message
description: Posts a message to a Slack channel.
configuration:
  options:
    url: https://slack.com/api/chat.postMessage
    method: POST
    auth: ${{ connection.auth }}
    contentType: json
    body:
      channel: general
      text: Hello from BorgIQ!
  connection:
    key: my-slack              # the workspace connection's key
    type: slack-oauth2         # a registered connection type
  error:
    if: ${{ !Q.isHTTPStatusInRange(results.statusCode, ["200-299"]) }}
    retryIf: ${{ Q.isHTTPStatusInRange(results.statusCode, ["429", "500-599"]) }}
    includeResult: true
    message: ${{ Q.toJSON(results) }}
```

The full actor document shape: [Common Actor Structure](../SKILL.md#common-actor-structure).
