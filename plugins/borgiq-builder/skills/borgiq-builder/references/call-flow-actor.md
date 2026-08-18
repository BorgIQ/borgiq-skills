# Call Flow Actor Reference

The CallFlowActor invokes a sub-flow by calling a CallableTriggerActor in another workflow. It enables parent flows to execute reusable sub-flows and optionally wait for their response.

## Table of Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [Emitted Message](#emitted-message)
- [Identifying the Target Sub-Flow](#identifying-the-target-sub-flow)
- [Examples](#examples)
- [Workflow Diagram](#workflow-diagram)
- [Use Cases](#use-cases)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Related Actors](#related-actors)

## Overview

CallFlowActor is the counterpart to CallableTriggerActor. While CallableTriggerActor starts a sub-flow when invoked, CallFlowActor is the actor that performs the invocation from the parent flow. This enables:

- Invoking reusable sub-flows from parent workflows
- Passing payload data to sub-flows
- Waiting for sub-flow completion and receiving results
- Fire-and-forget execution for asynchronous processing
- Cross-workspace and cross-canvas sub-flow invocation

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: CallFlowActor
    version: 1
    name: Call Flow
    msgVar: call_flow
    description: Call a sub-flow and wait for response
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        workspaceSlug: target-workspace
        canvasSlug: target-canvas
        callableTriggerActorId: ACTR01kd6tesvky0mh8x1css3sv5yg
        payload: ${{ msg.trigger.body }}
        waitForResponse: true
        timeoutInSeconds: 60
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Options Reference

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `callableTriggerActorId` | string | Yes | - | The actor ID of the CallableTriggerActor to invoke (must match pattern `ACTR` + 26 alphanumeric chars) |
| `payload` | any | Yes | - | The data to send to the sub-flow's CallableTriggerActor |
| `workspaceSlug` | string | No | Current workspace | The workspace slug where the target CallableTriggerActor resides |
| `canvasSlug` | string | No | Current canvas | The canvas slug where the target CallableTriggerActor resides |
| `waitForResponse` | boolean | No | false | Whether to wait for the sub-flow to complete and return a response |
| `timeoutInSeconds` | number | No | No timeout | Maximum time to wait for sub-flow response (only applies when `waitForResponse: true`) |

## TypeScript Schema Definition

The complete TypeScript schema for CallFlowActor options:

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

/** The options schema for the CallFlowActor */
export const CallFlowActorOptionsSchema = z.object({
  workspaceSlug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'need a valid borgIQ workspace slug')
    .min(5, 'must be 5 or more characters long').max(10, 'must be 10 or fewer characters long').nullish()
    .describe('The workspace the Callable Trigger Actor is in, defaults to the current workspace'),
  canvasSlug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'need a valid borgIQ canvas slug')
    .min(2, 'must be 2 or more characters long').max(255, 'must be 255 or fewer characters long').nullish()
    .describe('The canvas the Callable Trigger Actor is in, defaults to the current canvas'),
  callableTriggerActorId: z.string().regex(new RegExp('ACTR[0123456789abcdefghjkmnpqrstvwxyz]{26}$'), 'need a valid borgIQ callable trigger actor id')
    .describe('The actor id of the Callable Trigger Actor that wants to be triggered'),
  waitForResponse: z.boolean().nullish()
    .describe('If this actor should wait for a response from the Callable Response Actor from the called flow or emit a message immediately'),
  timeoutInSeconds: z.number().positive().nullish()
    .describe('The timeout in seconds for the sub-flow to return a response, defaults to no timeout'),
  payload: z.any()
    .describe('The payload to send to the Callable Trigger Actor, the parameters of the callable trigger flow'),
});

export type CallFlowActorOptions = z.infer<typeof CallFlowActorOptionsSchema>;

export const CallFlowActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    workspaceSlug: {
      type: BIQJsonSchemaType.String,
      title: 'Workspace Slug',
      description: 'The workspace the Callable Trigger Actor is in, defaults to the current workspace',
    },
    canvasSlug: {
      type: BIQJsonSchemaType.String,
      title: 'Canvas Slug',
      description: 'The canvas the Callable Trigger Actor is in, defaults to the current canvas',
    },
    callableTriggerActorId: {
      type: BIQJsonSchemaType.String,
      title: 'Callable Trigger Actor ID',
      description: 'The actor id of the Callable Trigger Actor that wants to be triggered',
      pattern: 'ACTR[0123456789abcdefghjkmnpqrstvwxyz]{26}$',
    },
    waitForResponse: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Wait for Response',
      description: 'If this actor should wait for a response from the Callable Response Actor from the called flow or emit a message immediately',
      default: false,
      ui: {
        component: 'switch',
      },
    },
    timeoutInSeconds: {
      type: BIQJsonSchemaType.Number,
      title: 'Timeout in Seconds',
      description: 'The timeout in seconds for the sub-flow to return a response, defaults to no timeout',
      default: 60,
    },
    payload: {
      type: BIQJsonSchemaType.Any,
      title: 'Payload',
      description: 'The payload to send to the Callable Trigger Actor, the parameters of the callable trigger flow',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
  },
  required: ['callableTriggerActorId', 'payload'],
};

export const CallFlowActorReceiveResultSchema = z.any();

export type CallFlowActorResult = z.infer<typeof CallFlowActorReceiveResultSchema>;
```

## Emitted Message

The CallFlowActor emits different messages depending on `waitForResponse`:

**When `waitForResponse: true`:**
The actor emits the response from the sub-flow's CallableResponseActor:

```json
{
  "result": "processed data",
  "status": "success"
}
```

**When `waitForResponse: false`:**
The actor emits immediately with the invoked flowrun identifiers:

```json
{
  "flowrunId": "FLRN01kd6w17z2vqckyrp4a02yshdz",
  "flowrunJobId": "FJOB01kd6w17z2vqckyrp4a02yshe1"
}
```

These IDs can be used for tracking or debugging the spawned sub-flow execution.

## Identifying the Target Sub-Flow

CallFlowActor uses three attributes to identify the target CallableTriggerActor:

| Attribute | Description | Default |
|-----------|-------------|---------|
| `workspaceSlug` | The workspace containing the target sub-flow | Current workspace (CallFlowActor's workspace) |
| `canvasSlug` | The canvas (workflow) containing the target sub-flow | Current canvas (CallFlowActor's canvas) |
| `callableTriggerActorId` | The actor ID of the CallableTriggerActor | Required, no default |

### Slug Resolution

```yaml
# Call sub-flow in the SAME workspace and canvas
configuration:
  options:
    # workspaceSlug: omitted - uses current workspace
    # canvasSlug: omitted - uses current canvas
    callableTriggerActorId: ACTR01kd6tesvky0mh8x1css3sv5yg
    payload: ${{ msg.data }}

# Call sub-flow in a DIFFERENT canvas (same workspace)
configuration:
  options:
    # workspaceSlug: omitted - uses current workspace
    canvasSlug: data-processing
    callableTriggerActorId: ACTR01kd6tesvky0mh8x1css3sv5yg
    payload: ${{ msg.data }}

# Call sub-flow in a DIFFERENT workspace
configuration:
  options:
    workspaceSlug: shared-utils
    canvasSlug: notification-service
    callableTriggerActorId: ACTR01kd6tesvky0mh8x1css3sv5yg
    payload: ${{ msg.data }}
```

## Examples

### Synchronous Call (Wait for Response)

```yaml
configuration:
  options:
    canvasSlug: process-order
    callableTriggerActorId: ACTR01kd6tesvky0mh8x1css3sv5yg
    payload:
      orderId: ${{ msg.trigger.body.orderId }}
      items: ${{ msg.trigger.body.items }}
    waitForResponse: true
    timeoutInSeconds: 120
```

### Asynchronous Call (Fire-and-Forget)

```yaml
configuration:
  options:
    canvasSlug: send-notification
    callableTriggerActorId: ACTR01abcdefghijklmnopqrstuvwx
    payload:
      channel: email
      recipient: ${{ msg.user.email }}
      subject: Order Confirmed
      message: Your order has been confirmed
    waitForResponse: false
```

### Cross-Workspace Call

```yaml
configuration:
  options:
    workspaceSlug: shared-ws
    canvasSlug: lookup-user
    callableTriggerActorId: ACTR01xyz123abc456def789ghi012
    payload:
      userId: ${{ msg.trigger.body.userId }}
    waitForResponse: true
    timeoutInSeconds: 30
```

### Dynamic Payload from Upstream Actor

```yaml
configuration:
  inputs:
    userData: ${{ msg.fetch_user.body }}
  options:
    canvasSlug: enrich-data
    callableTriggerActorId: ACTR01enrichdataactorxxxxxxxx
    payload: ${{ inputs.userData }}
    waitForResponse: true
```

## Workflow Diagram

```
Parent Flow:
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Trigger   │────>│ CallFlowActor│────>│  Continue   │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │ invokes           ▲
                           ▼                   │ returns (if waitForResponse)
Sub-Flow:                                      │
┌─────────────────┐     ┌─────────┐     ┌──────┴────────────┐
│CallableTrigger  │────>│ Process │────>│CallableResponse   │
└─────────────────┘     └─────────┘     └───────────────────┘
```

## Use Cases

| Scenario | Description |
|----------|-------------|
| Reusable Business Logic | Extract common operations (validation, enrichment) into callable sub-flows |
| Modular Architecture | Break complex workflows into smaller, maintainable sub-flows |
| Cross-Team Collaboration | Call sub-flows maintained by other teams in shared workspaces |
| Parallel Processing | Fire multiple async sub-flows for concurrent execution |
| Service Composition | Compose workflows from multiple specialized sub-flows |

## Error Handling

### Sub-Flow Errors

When the sub-flow's CallableResponseActor sets `throwError: true`:

```yaml
# CallFlowActor in parent flow
ACTR01callFlow:
  type: CallFlowActor
  msgVar: sub_flow_result
  continueOnError: true  # Handle error gracefully
  configuration:
    options:
      canvasSlug: validate-data
      callableTriggerActorId: ACTR01validateactor
      payload: ${{ msg.data }}
      waitForResponse: true

# Downstream actor handling the error
ACTR01handleResult:
  configuration:
    inputs:
      hasError: ${{ !Q.isNil(err.sub_flow_result) }}
      result: ${{ msg.sub_flow_result ?? err.sub_flow_result?.payload }}
```

### Timeout Handling

When `waitForResponse: true` and the sub-flow doesn't respond within `timeoutInSeconds`:

```yaml
ACTR01callFlow:
  type: CallFlowActor
  msgVar: call_result
  continueOnError: true
  configuration:
    options:
      callableTriggerActorId: ACTR01slowprocessor
      payload: ${{ msg.data }}
      waitForResponse: true
      timeoutInSeconds: 30  # Fail after 30 seconds

# Handle timeout in downstream actor
configuration:
  inputs:
    timedOut: ${{ !Q.isNil(err.call_result) && err.call_result?.message?.includes('timeout') }}
```

## Best Practices

1. **Set appropriate timeouts** - Always set `timeoutInSeconds` when using `waitForResponse: true` to prevent indefinite waiting
2. **Use fire-and-forget wisely** - Only use `waitForResponse: false` when you don't need the sub-flow result
3. **Handle errors gracefully** - Set `continueOnError: true` and check for errors in downstream actors
4. **Document sub-flow interfaces** - Clearly document what payload structure each CallableTriggerActor expects
5. **Consider workspace permissions** - Cross-workspace calls require appropriate access permissions
6. **Keep payloads focused** - Only send the data the sub-flow actually needs

## Related Actors

- [CallableTriggerActor](callable-trigger-actor.md) - Starts sub-flows when invoked by CallFlowActor
- [CallableResponseActor](callable-response-actor.md) - Returns data from sub-flows back to CallFlowActor
