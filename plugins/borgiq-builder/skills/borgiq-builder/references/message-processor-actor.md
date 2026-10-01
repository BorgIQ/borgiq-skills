# MessageProcessorActor Reference

MessageProcessorActor transforms data and controls message flow without calling an external API: inject values, render
templates, extract with regex, filter, delay, split and collect arrays, fork and join, dedupe, callback tokens and file
downloads. Read it for any of these actions. It is also the home of the fan-out rule and of fork/join.

## Contents

- [Rules](#rules)
- [Actions](#actions)
- [Message actions](#message-actions)
- [Split and collect](#split-and-collect)
- [Fork Actions](#fork-actions)
- [Callback Actions](#callback-actions)
- [Accumulating state](#accumulating-state)

## Rules

- Set one action per actor in `configuration.options.action`; its options sit beside it. Exact option and result
  schemas: `typescript/actorSchemas/task/messageProcessor/<action>.md` (see [typescript/index.md](typescript/index.md)).
- The actor has only the `SPRTdefault` source port, whatever the action. Parallel paths are several edges from that
  port ([port table](edges-and-positioning.md#port-ids)).
- `dedupeByCount` and `dedupeByTime` need `enableLTM: true`. `collect` and `forkJoin` need `enableSTM: true`.
- Every actor between `split` and `collect`, or between `fork` and `forkJoin`, needs `continueOnError: true`; otherwise
  one failure leaves the join waiting forever ([error-handling.md](error-handling.md#joins-hang-when-a-branch-fails)).
- Transform with `inject` and `${{ }}` / Q-lib before reaching for a DenoActor.

Skeleton, as a bundle `actor.yaml` (edges and position live in `canvas.yaml`):

```yaml
id: ACTR01kx4b00000000000000000011
version: 1
type: MessageProcessorActor
name: Message Processor
msgVar: message_processor
description: Adds computed values to the message.
isActive: true
continueOnError: false
enableLTM: false   # true for dedupeByCount / dedupeByTime
enableSTM: false   # true for collect / forkJoin
sourcePorts:
  - id: SPRTdefault
configuration:
  options:
    action: inject
    payload:
      now: ${{ Q.now() }}
      ulid: ${{ Q.ulid() }}
      formattedDate: ${{ Q.dateFns.format(Q.now(), 'dd-MM-yyyy') }}
schemas: {}
```

## Actions

`*` marks a required option.

| Action | Options | Emits |
|---|---|---|
| `inject` | `payload`* | the `payload` value |
| `renderTemplate` | `template`* (LiquidJS) | the rendered string |
| `regexExtract` | `rules`*: a list of `regex`* (valid pattern), `regexOptions` (flags such as `gi`), `extractFrom`*, `extractTo`* | `{ <extractTo>: [...] }`: every match with `g`, else the first; `[]` when none |
| `filter` | `filter`* (boolean) | `true` when `filter` is true; otherwise nothing, and the branch stops |
| `delayBySeconds` | `seconds`* (0 or more) | `{ delayUntil: <ISO time> }`, after the delay |
| `delayUntil` | `until`* (ISO date-time) | `{ delayUntil }`, at that time |
| `split` | `valueToSplit`* (array), `emitKey` (default `item`), `limit` (max messages, default 1000) | one message per element: `{ splitId, index, size, <emitKey>: element }` |
| `collect` | `splitId`*, `size`* (> 0), `captureValue`*, `emitKey` (default `items`), `if` (default `true`) | `{ <emitKey>: [captured values] }`, once `size` messages arrived |
| `fork` | — | `{ forkId }` |
| `forkJoin` | `forkId`*, `size`* | `{ <sourceMsgVar>: <its message>, … }` ([forkJoin](#forkjoin)) |
| `dedupeByCount` | `dedupeKey`*, `lookbackAsCount`* (integer > 0), `emitAlways`* | `{ dedupeKey, unique: true }`; a duplicate emits nothing unless `emitAlways: true` (then `unique: false`) |
| `dedupeByTime` | `dedupeKey`*, `lookbackInSeconds`* (> 0), `emitAlways`* | as `dedupeByCount` |
| `issueCallbackToken` | `expiresAfterInSeconds` (default 604800, 7 days), `multipleResponse` (ignored) | `{ token, url, expiresAt, multipleResponse: false }` |
| `waitForCallbackToken` | `token`*, `timeoutInSeconds`* | the resolution ([Callback Actions](#callback-actions)) |
| `notifyCallbackToken` | `token`*, `payload`* | `true` |
| `downloadFileUrl` | `file`* (BIQFile), `expiresInMinutes` (default 1), `downloadAsAttachment` (default `false`: open inline) | `{ file, url }` (a temporary download URL) |
| `downloadFileAsBase64` | `file`* (BIQFile) | `{ file, base64 }` |

Example values: `until: ${{ Q.dateFns.addHours(Q.now(), 2).toISOString() }}`; `dedupeKey: ${{ msg.webhook.body.orderId }}`
with `lookbackAsCount: 100`; `file: ${{ msg.interface_form.body.attachment }}`.

## Message actions

**renderTemplate.** Read data through Liquid tags on `inputs`. A `${{ }}` inside the template is interpolated before
Liquid runs, where loop variables such as `item` do not exist:

```yaml
configuration:
  inputs:
    name: ${{ msg.form.body.name }}
    items: ${{ msg.data.items }}
  options:
    action: renderTemplate
    template: |
      Hello {{ inputs.name }},
      {% for item in inputs.items %}
      - {{ item.name }}: {{ item.price }}
      {% endfor %}
```

**regexExtract.** Each rule writes one key:

```yaml
configuration:
  inputs:
    text: ${{ msg.email.body }}
  options:
    action: regexExtract
    rules:
      - regex: '[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}'
        regexOptions: gi
        extractFrom: ${{ inputs.text }}
        extractTo: emails     # { emails: ["user@example.com", …] }
```

**filter as a gate.** Use `filter` instead of a RouterActor when there is one path and the false case needs no handling:
the flow stops there.

| Need | Use |
|---|---|
| One path; drop the rest (a guard) | `filter` |
| If/else, a switch, or handling the false case | RouterActor ([router-actor.md](router-actor.md)) |

```yaml
configuration:
  inputs: ${{ msg.webhook.body.message }}
  options:
    action: filter
    filter: ${{ inputs.startsWith('Hello') }}
    # also: ${{ inputs.items?.length > 0 }}, ${{ !Q.isNil(inputs.userId) }}, ${{ inputs.email?.endsWith('@company.com') }}
```

## Split and collect

`split` emits one message per array element, all sharing a `splitId`; the actors after it run once per element.
`collect` gathers them back. Keep `captureValue` to the fields you need: the collected array grows in short-term memory
with every element, and capturing whole responses slows the flow.

```yaml
# split_users
configuration:
  options:
    action: split
    valueToSplit: ${{ msg.api_response.users }}
    emitKey: user
    limit: 100
---
# collect_users (enableSTM: true); process_user has continueOnError: true
configuration:
  options:
    action: collect
    splitId: ${{ msg.split_users.splitId }}
    size: ${{ msg.split_users.size }}
    captureValue:
      id: ${{ msg.split_users.user.id }}
      status: ${{ msg.process_user?.status }}
    emitKey: processedUsers
    if: ${{ msg.process_user?.status === 'success' }}   # skip values that fail the condition
```

How to capture a failed element (`err.<msgVar>`): [error-handling.md](error-handling.md#joins-hang-when-a-branch-fails).

## Fork Actions

**Fan-out is automatic.** When an actor has edges to B and C, both run concurrently when it emits. An actor reached by
N edges runs N times, once per arriving message. No `fork` is needed for parallelism.

```
     A                    A
    / \                   |
   B   C                fork
    \ /                  / \
     D                  B   C
 D runs twice            \ /
                       forkJoin
                          |
                          D     D runs once, with B's and C's results
```

Use `fork` before the branches and `forkJoin` after them only when a step must run **once** with the results of every
branch:

| Scenario | fork/forkJoin? |
|---|---|
| Query several APIs or databases, then normalize or merge all results | Yes |
| Fetch a profile and its settings, then merge them into one object | Yes |
| Call several AI models and compare the answers | Yes |
| Send email and Slack; log to several systems; call several webhooks | No: connect each directly |
| Handle each branch's result on its own path | No |

Mistakes to avoid:

- **Merging with `inject` after parallel calls.** The inject actor runs once per upstream message and sees one result
  each time, so the merge never happens. Put `fork` before the branches and `forkJoin` after.
- **Extra `sourcePorts` on the fork actor.** `fork` only adds a `forkId` to the message; the branches are plain edges
  from `SPRTdefault`.
- **A fork for fire-and-forget branches.** It only adds a wait for the slowest branch.

### fork

`action: fork` takes no other option and emits `{ forkId }` to every connected actor.

### forkJoin

- Set `enableSTM: true` and `forkId: ${{ msg.<fork>.forkId }}`.
- `size` is the number of distinct actors that will send the join a message with this `forkId`.
  `${{ ctx.actor.upstreamActorCount }}` counts the distinct actors with an edge into the join (several edges from one
  actor count once; disabled actors don't count), which is right for `fork` → N parallel actors → `forkJoin`. The editor
  fills it in; YAML must set it. Set a number instead when a connected actor won't send one for that `forkId`: a path
  that can filter its message out or route it to another port, or an actor wired in from outside the fork. A `size`
  larger than the number of actors that send one means the join never emits.
- The join emits once, when `size` distinct sources have arrived. A source that sends twice counts once and its last
  message wins; messages after the emit are ignored.
- Read results as `msg.<forkJoinMsgVar>.<sourceMsgVar>`. Only the actors wired directly into the join are in it:
  `msg.<sourceMsgVar>` is `undefined` after the join, and the messages of earlier actors on a path are lost. To keep them,
  end each path with an `inject` that bundles what you need.

```yaml
# fork_requests
configuration:
  options:
    action: fork
---
# bundle_path_a: last actor on path A (continueOnError: true), after fetch_data_a and process_data_a
configuration:
  options:
    action: inject
    payload:
      fetchResult: ${{ msg.fetch_data_a }}
      processResult: ${{ msg.process_data_a }}
---
# join_results (enableSTM: true); bundle_path_a and bundle_path_b are wired into it
configuration:
  options:
    action: forkJoin
    forkId: ${{ msg.fork_requests.forkId }}
    size: ${{ ctx.actor.upstreamActorCount }}   # 2
---
# after the join
configuration:
  inputs:
    pathAFetch: ${{ msg.join_results.bundle_path_a?.fetchResult }}   # not msg.fetch_data_a
    pathB: ${{ msg.join_results.bundle_path_b }}
```

## Callback Actions

A callback token pauses a flowrun until a person or another system answers.

- `issueCallbackToken` returns `{ token, url, expiresAt, multipleResponse: false }`: a `TOKN…` token, a `url` of the
  form `https://<api-host>/tkn/<token>`, valid for `expiresAfterInSeconds`. A token resolves once.
- `waitForCallbackToken` pauses until the token resolves or `timeoutInSeconds` passes. Issue and wait in the same
  flowrun. A resolution that arrives before the wait starts is kept and delivered when it does.
- Resolve a token in one of two ways:
  - **POST to its `url`.** The waiter emits the request as `{ headers, body }`; read `msg.<wait>.body`. The endpoint
    answers 200 with `{ status: 'processed' | 'unprocessed', reason }`. A browser link sends GET, which it does not accept.
  - **`notifyCallbackToken`** with `token` and `payload`, from any flow. The waiter emits `payload` as-is (read
    `msg.<wait>.approved`); the notify actor emits `true`. An unknown or expired token fails it with a `SignalError`.
- Catch the timeout with `continueOnError: true` on the waiter. The error arrives as `err.<wait>`:
  `{ location: 'orchestrator', name: 'TimeoutError', message, stack, retry: false, canEmit: true }`.

### Human approval pattern

Main flow: trigger → `issue_token` → a SendEmailActor ([send-email-actor.md](send-email-actor.md)) → `wait_for_approval`
→ `route_approval`. The email links to a WebhookTriggerActor on the same canvas that accepts GET, is public and responds
immediately ([webhook-trigger-actor.md](webhook-trigger-actor.md)):
`${{ ctx.canvas.webhookTriggers.approval_link.url }}?token=${{ msg.issue_token.token }}&decision=approve`, and a
`reject` link. That second flow is `approval_link` → `notify_decision`.

```yaml
# issue_token
configuration:
  options:
    action: issueCallbackToken
    expiresAfterInSeconds: 86400
---
# wait_for_approval (continueOnError: true)
configuration:
  options:
    action: waitForCallbackToken
    token: ${{ msg.issue_token.token }}
    timeoutInSeconds: 86400
---
# route_approval: RouterActor with ports Approved and Timeout, plus SPRTdefault named Rejected
configuration:
  options:
    emitType: singleRoute
    conditions:
      Approved: ${{ msg.wait_for_approval?.approved === true }}
      Timeout: ${{ err.wait_for_approval?.name === 'TimeoutError' }}
---
# notify_decision, in the approval_link flow
configuration:
  options:
    action: notifyCallbackToken
    token: ${{ msg.approval_link.queryParams.token }}
    payload:
      approved: ${{ msg.approval_link.queryParams.decision === 'approve' }}
```

When the resolver knows only a correlation id (a thread id, an order id), store the token in a collection under that id
with a CollectionActor `putItem`, and have the resolving flow, for example a scheduled poller that detects the reply,
`getItem` it before notifying.

## Accumulating state

A msgVar must be unique in a canvas (validation reports duplicates), so give each state step its own msgVar and merge
the previous step's message into it:

```yaml
# state_after_api (after state_init and api_call)
configuration:
  inputs:
    apiData: ${{ msg.api_call.body }}
  options:
    action: inject
    payload: ${{ Object.assign({}, msg.state_init, inputs) }}
```

Each step adds fields and keeps the earlier ones: `state_init` `{ company }` → `state_after_api` `{ company, apiData }`
→ `state_final` `{ company, apiData, result }`. Downstream actors read the last step (`msg.state_final`).
