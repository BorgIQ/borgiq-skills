# Router Actor Reference

RouterActor sends each message to one or more named source ports by evaluating boolean conditions: if/else, switch and
error routing. Read it when a flow branches on data. For classification by an LLM, use an
[AiRouterActor](ai-router-actor.md); for a single gate with no else path, a MessageProcessorActor
[`filter`](message-processor-actor.md#message-actions).

## Rules

- Give each route a source port: an `id` (`SPRT` + 7 lowercase letters or digits, from `borgiq generate id sourceport`)
  and a `name`. Keep `SPRTdefault` as the fallback port.
- Key `conditions` by port **name**. A key that names no port is rejected, and so is a key equal to the default port's
  name: that name is reserved for the default route, which takes no condition.
- Conditions are evaluated in the order of the `conditions` keys. `emitType: singleRoute` (the default) emits on the
  first true one; `multiRoute` emits on every true one. When none is true, the message goes to `SPRTdefault`.
- The router's result is the name of the port it emitted on, e.g. `"Yes"`.
- Keep conditions simple and put the most important first; compute anything complex upstream (a DenoActor or `vars`).
- Wire each route's port to its downstream actors; edge `label`s are display only
  ([edges-and-positioning.md](edges-and-positioning.md)).

## Options

| Option | Type | Default | Meaning |
|---|---|---|---|
| `emitType` | `singleRoute` \| `multiRoute` | `singleRoute` | First true condition, or every true condition |
| `conditions` | map of port name → boolean | required | When each route emits |

Exact schema: [router.md](typescript/actorSchemas/task/router.md).

## Example

As a bundle `actor.yaml` (edges and position live in `canvas.yaml`):

```yaml
id: ACTR01kx4b00000000000000000031
version: 1
type: RouterActor
name: Check User Status
msgVar: check_user_status
description: Routes by the user's status.
isActive: true
continueOnError: false
enableLTM: false
enableSTM: false
sourcePorts:
  - id: SPRTz7r3lca
    name: Active
    description: User is active
  - id: SPRTgzuftoe
    name: Inactive
    description: User is inactive
  - id: SPRTdefault
    name: Unknown
    description: Status unknown
configuration:
  options:
    emitType: singleRoute
    conditions:
      Active: ${{ msg.user.status === 'active' }}
      Inactive: ${{ msg.user.status === 'inactive' }}
schemas: {}
```

## Condition patterns

If/else: the default port is the else branch.

```yaml
sourcePorts:
  - id: SPRTvnkbb93
    name: 'Yes'
    description: Value exists
  - id: SPRTdefault
    name: 'No'            # no condition
configuration:
  options:
    conditions:
      'Yes': ${{ !Q.isNil(msg.fetch_data.value) }}
```

| Route on | Condition |
|---|---|
| Priority switch | `High: ${{ msg.ticket.priority === 'high' }}`, `Medium: …`, `Low: …` |
| HTTP status class | `Success: ${{ Q.isHTTPStatusInRange(msg.api_call.statusCode, ["200-299"]) }}`, `ClientError: …["400-499"]`, `ServerError: …["500-599"]` |
| Non-empty array | `HasItems: ${{ msg.search_results.items?.length > 0 }}` |
| Several notifications at once (`multiRoute`) | `SendEmail: ${{ inputs.notifyEmail }}`, `SendSlack: ${{ inputs.notifySlack }}`, `LogToDatabase: ${{ inputs.logEnabled }}` |
| Upstream success, with `continueOnError: true` upstream (default port: error) | `Success: ${{ Q.isNil(err.fetch_data) && !Q.isNil(msg.fetch_data) }}` |

A failed upstream actor with `continueOnError: true` leaves `msg.<msgVar>` undefined and sets `err.<msgVar>`
([error-handling.md](error-handling.md)). Quote port names such as `'Yes'` and `'No'`, which YAML would otherwise read as
booleans.
