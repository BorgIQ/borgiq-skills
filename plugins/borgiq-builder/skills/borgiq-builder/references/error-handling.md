# Error Handling

How an actor fails, how a failure reaches downstream actors as `err.<msgVar>`, and the `error` block that turns a
result into a failure. Read it when a flow must survive or route a failed step. Run and job states when debugging:
[flowrun-job-states.md](flowrun-job-states.md).

## continueOnError and err.<msgVar>

- By default a failed actor fails its job and emits nothing.
- With `continueOnError: true`, the failure is emitted to the connected actors as `err.<msgVar>`, and
  `msg.<msgVar>` is `undefined`. An error with `canEmit: false` still fails the job.
- Test for failure with `!Q.isNil(err.<msgVar>)`, for success with `Q.isNil(err.<msgVar>)`, and fall back with
  `${{ msg.<msgVar> ?? err.<msgVar> }}`.

```yaml
# downstream of fetch_data (continueOnError: true)
configuration:
  inputs:
    hasError: ${{ !Q.isNil(err.fetch_data) }}
    errorMessage: ${{ err.fetch_data?.message }}
    data: ${{ msg.fetch_data?.body }}
```

To branch on the outcome, use a RouterActor condition such as
`Success: ${{ Q.isNil(err.fetch_data) && !Q.isNil(msg.fetch_data) }}` with the default port as the error path
([router-actor.md](router-actor.md)).

## The err object

| Field | Meaning |
|---|---|
| `name` | Error name, e.g. `<ActorType>.ErrorIfConditionMet` (the `error` block), `<ActorType>.ReceiveError`, `TimeoutError` (a callback wait), `CallableResponseError` (a sub-flow's `throwError`) |
| `message` | The message: the `error` block's `message`, or the failure's own |
| `location` | `runtime` or `orchestrator` |
| `stack` | Stack text (may be empty) |
| `retry` | Whether the job is retried |
| `canEmit` | Whether the error can reach downstream actors at all |
| `metadata` | Extra data: `metadata.results` holds the actor's result when the `error` block sets `includeResult: true` |

## The error block

`configuration.error` decides from the actor's own result whether it failed. Its fields are exactly these
([schemas/error.md](typescript/schemas/error.md)):

| Field | Type | Meaning |
|---|---|---|
| `if` | boolean, required | The result is a failure when true |
| `retryIf` | boolean | Retry the job when true (rate limits, server errors) |
| `message` | string | The error's `message` |
| `includeResult` | boolean | Attach the result as `err.<msgVar>.metadata.results` |

It is interpolated after the actor runs, with the result in `results`:

```yaml
error:
  if: ${{ !Q.isHTTPStatusInRange(results.statusCode, ["200-299"]) }}
  retryIf: ${{ Q.isHTTPStatusInRange(results.statusCode, ["429", "500-599"]) }}
  includeResult: true
  message: ${{ Q.toJSON(results) }}
```

## Joins hang when a branch fails

`collect` and `forkJoin` wait for `size` messages. An actor between `split` and `collect`, or between `fork` and
`forkJoin`, that fails without `continueOnError: true` emits nothing, so the join waits forever. Set
`continueOnError: true` on every actor in between, and capture both outcomes:

```
split -> actor A -> actor B -> collect
         ^ continueOnError: true   ^ handle the missing msg
```

```yaml
# process_result: HttpRequestActor between split_items and collected, continueOnError: true
# collected (enableSTM: true)
configuration:
  options:
    action: collect
    splitId: ${{ msg.split_items.splitId }}
    size: ${{ msg.split_items.size }}
    captureValue:
      id: ${{ msg.split_items.item.id }}
      success: ${{ !Q.isNil(msg.process_result) }}
      result: ${{ msg.process_result ?? err.process_result }}
    emitKey: results
```
