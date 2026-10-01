# Call Flow Actor Reference

The CallFlowActor starts a sub-flow by sending `payload` to a [CallableTriggerActor](callable-trigger-actor.md) in the same canvas, another canvas or another workspace, and, when it waits, emits what the sub-flow's [CallableResponseActor](callable-response-actor.md) returns. Read this for its options, what it emits, and its errors and timeouts.

## Options

| Option | Type | Default | Meaning |
|---|---|---|---|
| `callableTriggerActorId` | string | — (required) | Id of the CallableTriggerActor to start: `ACTR` + 26 lowercase ULID characters (digits and letters except `i`, `l`, `o`, `u`). Copy it from the sub-flow's trigger. |
| `payload` | any | — (required) | The sub-flow's input. Its keys must match the trigger's `schemas.inputs`; send only what the sub-flow reads. |
| `workspaceSlug` | string, 5–10 chars, lowercase kebab-case | current workspace | Workspace of the sub-flow; it must be in the same organization |
| `canvasSlug` | string, 2–255 chars, lowercase kebab-case | current canvas | Canvas of the sub-flow |
| `waitForResponse` | boolean | `true` when omitted | Wait for the sub-flow's CallableResponseActor. Always set it: the editor form pre-fills `false`. Use `false` only when you do not need the result. |
| `timeoutInSeconds` | number > 0 | no timeout | Longest wait for the response (waiting calls only). The editor pre-fills `900`. |

- Put expressions straight into `payload`. The CallFlowActor ignores `configuration.inputs`; when an AI agent calls it as a tool, the tool's arguments become the payload.
- Always set `timeoutInSeconds` on a waiting call; without it the call can wait forever.

Exact schema: [typescript/actorSchemas/task/callFlow.md](typescript/actorSchemas/task/callFlow.md).

## Example

```yaml
type: CallFlowActor
version: 1
name: Look Up User
msgVar: lookup_result
continueOnError: true
sourcePorts:
  - id: SPRTdefault
configuration:
  options:
    workspaceSlug: shared-ws      # omit for the current workspace
    canvasSlug: lookup-user       # omit for the current canvas
    callableTriggerActorId: ACTR01ke28jt97kb6cq643dzvmxxqk
    payload:
      userId: ${{ msg.trigger.body.userId }}
      profile: ${{ msg.fetch_user.body }}
    waitForResponse: true
    timeoutInSeconds: 30
schemas: {}
```

## What it emits

| `waitForResponse` | Emits |
|---|---|
| `true` | the `payload` of the sub-flow's CallableResponseActor, when it runs |
| `false` | at once: `{ flowrunId, flowrunJobId }` of the started sub-flow run, for tracking or debugging |

## Errors and timeouts

With `continueOnError: true` the error lands in `err.<msgVar>`; without it the parent run fails.

| Case | Error `name` |
|---|---|
| The sub-flow's CallableResponseActor sets `throwError: true` | `CallableResponseError`, with the response `payload` in `metadata` |
| No response within `timeoutInSeconds` | `TimeoutError` |
| The sub-flow cannot be started (unknown workspace, canvas or trigger id, or a trigger missing from a deployed canvas's active build) | `InvocationError` on a fire-and-forget call; a waiting call gets no error and ends only at its timeout |

```yaml
# Downstream of the CallFlowActor above
configuration:
  inputs:
    hasError: ${{ !Q.isNil(err.lookup_result) }}
    timedOut: ${{ err.lookup_result?.name === 'TimeoutError' }}
    result: ${{ msg.lookup_result ?? err.lookup_result?.metadata }}
```
