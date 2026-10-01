# Callable Trigger Actor Reference

The CallableTriggerActor is the entry point of a sub-flow: another flow's [CallFlowActor](call-flow-actor.md) starts it with a `payload`, and a [CallableResponseActor](callable-response-actor.md) returns the result. Use sub-flows for reusable pieces (validation, enrichment, notifications, lookups) and to split a large flow. Read this for the sub-flow contract and a complete example.

## Contents

- [Input schema — the sub-flow contract](#input-schema--the-sub-flow-contract)
- [Example](#example)
- [Emitted message](#emitted-message)
- [Calling and returning](#calling-and-returning)

## Input schema — the sub-flow contract

A CallableTriggerActor is a public entry point: other flows invoke it blind and hand it a `payload`. Treat it as a typed function signature and **always declare the expected payload as `schemas.inputs` on the trigger**, never `schemas: {}`. That schema:

- **drives the editor**: the calling CallFlowActor's payload form is generated from it, and it renders the input hints when the sub-flow is run by hand;
- **documents the interface** for callers and for agents that edit the canvas later;
- **is the single source of field names** every downstream actor reads.

> **The schema is not enforced at runtime.** The caller's `payload` enters the sub-flow as-is. A missing `required` field or a wrong type does not fail at the boundary; it surfaces as `undefined` (or the wrong type) wherever a downstream actor reads it. Drift between the caller's `payload`, the trigger's `schemas.inputs` and the downstream `msg.*` reads is the most common sub-flow bug, and it fails silently.

Rules:

1. **Declare every payload field** in `schemas.inputs` (actor level, see [Common Actor Structure](../SKILL.md#common-actor-structure)), marking the genuinely required ones in `required`. Mirror each field in `configuration.inputs` with an empty default (e.g. `topic: ''`) so the input surface is explicit. `configuration.options` is always `{}`: the trigger has no options.
2. **Every downstream actor reads those exact fields**, `${{ msg.<callable_msgVar>.<field> }}`, and declares them in its own `schemas.inputs`. No actor reads a field the schema lacks; the schema declares no field nobody reads.
3. **The caller's `payload` keys match** the schema's properties (see [call-flow-actor.md](call-flow-actor.md)).

The trigger schema is the sub-flow's signature, the downstream actors its body, and the [CallableResponseActor](callable-response-actor.md) payload its return type. For schema design (tight vs loose, enums, `$ref`, the `type: any` convention), use the `borgiq-json-schema-builder` skill.

## Example

The sub-flow's trigger, with its contract and input hints (`ui.component` `textarea` or `input`, `ui.order`, and component `options` such as `placeholder`):

```yaml
ACTR01kcddpqxsakc25fn5c0hz9a35:
  type: CallableTriggerActor
  version: 1
  name: Research Sub Agent
  msgVar: research_sub_agent
  description: Researches a topic on the web and returns a summary of the exact information asked for.
  isActive: true
  sourcePorts:
    - id: SPRTdefault
  configuration:
    inputs:
      topic: ''
      fileSystemId: ''
    options: {}
  schemas:
    inputs:
      type: object
      properties:
        topic:
          type: string
          title: Research Topic
          description: The topic or subject to research
          ui:
            order: 0
            component: textarea
            options:
              placeholder: Enter the research topic or question...
              minLines: 2
              maxLines: 10
              autoResize: true
        fileSystemId:
          type: string
          title: File System ID
          ui:
            order: 1
            component: input
      required:
        - topic
        - fileSystemId
  id: ACTR01kcddpqxsakc25fn5c0hz9a35
```

The parent flow calls it with a CallFlowActor whose `payload` keys match:

```yaml
type: CallFlowActor
msgVar: research_result
configuration:
  options:
    workspaceSlug: my-workspace   # omit for the current workspace
    canvasSlug: research-agent    # omit for the current canvas
    callableTriggerActorId: ACTR01kcddpqxsakc25fn5c0hz9a35
    payload:
      topic: ${{ msg.request.body.topic }}
      fileSystemId: ${{ msg.request.body.fileSystemId }}
    waitForResponse: true
    timeoutInSeconds: 300
```

Downstream in the sub-flow, actors read `${{ msg.research_sub_agent.topic }}`; a code actor maps the payload through its `configuration.inputs` (e.g. `inputs: ${{ msg.research_sub_agent }}`, then `req.inputs.topic`). The last actor feeds a CallableResponseActor with `payload: ${{ msg.<last_actor_msgVar> }}`.

## Emitted message

The trigger emits the caller's `payload` exactly as sent; its shape is whatever the parent passes.

## Calling and returning

- Start the sub-flow from any flow with a [CallFlowActor](call-flow-actor.md) (code actors have no signal that starts a flow): options, what it emits, errors and timeouts live there. With `waitForResponse: true` the parent waits for the result (lookups, transformations); with `false` it continues at once and the sub-flow runs independently (fire-and-forget, parallel work).
- Return data with a [CallableResponseActor](callable-response-actor.md), or from a DenoActor with `signal: Signal.callableResponse({ payload, throwError })`. An actor's `results` never reach the parent.
- **One sub-flow per item:** `split` the array with a MessageProcessorActor (`valueToSplit: ${{ msg.trigger.body.tasks }}`, `emitKey: task`) and wire it to a CallFlowActor with `payload: ${{ msg.split_tasks.task }}` and `continueOnError: true`; with `waitForResponse: false` the sub-flows run in parallel.
- Keep each sub-flow to one job with a clear name, and return failures through the CallableResponseActor's `throwError` so the caller can handle them. A waiting caller should set `timeoutInSeconds`.
