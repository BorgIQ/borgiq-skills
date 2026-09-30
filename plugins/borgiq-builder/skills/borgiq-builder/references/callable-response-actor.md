# Callable Response Actor Reference

The CallableResponseActor returns data from a sub-flow to the waiting [CallFlowActor](call-flow-actor.md) of the parent run. Put one at the end of each path of a flow started by a [CallableTriggerActor](callable-trigger-actor.md). What the parent emits, and its errors and timeouts: [call-flow-actor.md](call-flow-actor.md).

## Options

| Option | Type | Default | Meaning |
|---|---|---|---|
| `payload` | any | `{}` | Returned to the parent CallFlowActor, which emits it as `msg.<callFlowMsgVar>`. This is the sub-flow's return type: keep its shape stable and documented. |
| `throwError` | boolean | `false` | Return the payload as an error: the parent CallFlowActor fails with `CallableResponseError` and the `payload` in the error's `metadata`. With `continueOnError: true` on the CallFlowActor it lands in `err.<callFlowMsgVar>`; otherwise the parent run fails. |

- It returns data only when the run was started by a CallFlowActor that waits (`waitForResponse` true). After a fire-and-forget call, or in a flow started by any other trigger, nothing is returned.
- It also emits `payload` on `SPRTdefault` in the sub-flow.
- An actor's `results` never reach the parent: wire the last actor into the CallableResponseActor with `payload: ${{ msg.<last_actor_msgVar> }}`. The only other way back is a DenoActor returning `signal: Signal.callableResponse({ payload, throwError })`.

Exact schema: [typescript/actorSchemas/task/callableResponse.md](typescript/actorSchemas/task/callableResponse.md).

## Example

Return the upstream result, or its error (the upstream `api_call` has `continueOnError: true`):

```yaml
type: CallableResponseActor
version: 1
name: Return Result
msgVar: callable_response
sourcePorts:
  - id: SPRTdefault
configuration:
  inputs:
    hasError: ${{ !Q.isNil(err.api_call) }}
  options:
    payload: "${{ inputs.hasError ? err.api_call : msg.api_call.body }}"   # quoted: contains ': '
    throwError: ${{ inputs.hasError }}
schemas: {}
```

An explicit failure with a fixed shape:

```yaml
configuration:
  options:
    payload:
      error: Validation failed
      details: ${{ msg.validation.errors }}
    throwError: true
```
