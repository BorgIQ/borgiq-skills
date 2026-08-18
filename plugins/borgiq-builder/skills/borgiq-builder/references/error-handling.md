# Error Handling Patterns

## Table of Contents

- [Error Handling with continueOnError](#error-handling-with-continueonerror)
- [Error Handling in Split/Collect and Fork/ForkJoin Patterns](#error-handling-in-splitcollect-and-forkforkjoin-patterns)

**See also:** [flowrun-job-states.md](flowrun-job-states.md) for understanding flowrun states, job states, and counters when debugging execution via the CLI.

## Error Handling with continueOnError

When an actor has `continueOnError: true` and encounters an error:
- The actor's output is stored in `err.ActorName` (not `msg.ActorName`)
- `msg.ActorName` will be `undefined`
- Downstream actors can check for errors and handle them gracefully

```yaml
# Upstream actor with continueOnError
ACTR01upstream:
  continueOnError: true
  # ... rest of config

# Downstream actor checking for error
configuration:
  inputs:
    # Check if upstream failed
    hasError: ${{ !Q.isNil(err.upstream_actor) }}
    # Access error details if present
    errorMessage: ${{ err.upstream_actor?.message }}
    # Access success data if present
    data: ${{ msg.upstream_actor?.body }}
```

## Error Handling in Split/Collect and Fork/ForkJoin Patterns

**Critical:** When using `split`/`collect` or `fork`/`forkJoin` patterns, actors between the split and collect (or fork and forkJoin) **must** have `continueOnError: true`. Otherwise, if any actor fails, the workflow will get stuck waiting for messages that will never arrive.

```
Split -> Actor A -> Actor B -> Collect
         ↑                      ↑
    continueOnError: true   Handle missing msg
```

**Why this matters:**
- `collect` and `forkJoin` wait for a specific number of messages (based on `size`)
- If an actor fails without `continueOnError: true`, it stops execution and never emits a message
- The `collect`/`forkJoin` actor will wait indefinitely for the missing message

**Example: Safe split/collect pattern**

```yaml
# Split actor
ACTR01split:
  type: MessageProcessorActor
  msgVar: split_items
  configuration:
    options:
      action: split
      valueToSplit: ${{ msg.data.items }}
      emitKey: item

# Processing actor - MUST have continueOnError: true
ACTR01process:
  type: HttpRequestActor
  msgVar: process_result
  continueOnError: true  # Critical!
  configuration:
    options:
      url: https://api.example.com/process/${{ msg.split_items.item.id }}
      method: POST

# Collect actor - handle both success and error cases
ACTR01collect:
  type: MessageProcessorActor
  msgVar: collected
  enableSTM: true
  configuration:
    options:
      action: collect
      splitId: ${{ msg.split_items.splitId }}
      size: ${{ msg.split_items.size }}
      # Handle missing msg on error - use err fallback
      captureValue:
        id: ${{ msg.split_items.item.id }}
        success: ${{ !Q.isNil(msg.process_result) }}
        result: ${{ msg.process_result ?? err.process_result }}
      emitKey: results
```

**Key points:**
1. Set `continueOnError: true` on all actors between split and collect
2. In `captureValue`, check if `msg.ActorName` exists to determine success
3. Access error details via `err.ActorName` when the actor failed
4. Use `??` operator to fallback: `${{ msg.actor ?? err.actor }}`
