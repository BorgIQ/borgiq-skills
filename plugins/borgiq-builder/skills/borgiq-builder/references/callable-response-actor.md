# Callable Response Actor Reference

The CallableResponseActor sends a response back to the parent flow that invoked the current sub-flow via a CallFlowActor.

> **Important:** CallableResponseActor can **only** be used in workflows that are triggered by a CallableTriggerActor. Using it in flows with other trigger types (WebhookTriggerActor, ButtonTriggerActor, etc.) will result in an error.

## Table of Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [Emitted Message](#emitted-message)
- [Examples](#examples)
- [Usage with CallableTriggerActor and CallFlowActor](#usage-with-callabletriggeractor-and-callflowactor)
- [Workflow Diagram](#workflow-diagram)
- [Use Cases](#use-cases)
- [Error Handling](#error-handling)

## Overview

When a parent workflow invokes a sub-flow using CallFlowActor, the sub-flow can return data back to the parent using CallableResponseActor. This enables:
- Returning computed results from sub-flows
- Passing processed data back to parent workflows
- Signaling errors to the calling flow
- Creating reusable workflow modules

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: CallableResponseActor
    version: 1
    name: Callable Response
    msgVar: callable_response
    description: Send response to parent flow
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        payload: ${{ msg.process_data.result }}
        throwError: false
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
| `payload` | any | Yes | - | The data to return to the CallFlowActor in the parent flow |
| `throwError` | boolean | No | false | If true, throws an error to the CallFlowActor instead of returning normally |

## TypeScript Schema Definition

The complete TypeScript schema for CallableResponseActor options:

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

/** The options schema for the CallableResponseActor */
export const CallableResponseActorOptionsSchema = z.object({
  payload: z.any().describe('The payload to emit on the Call flow actor that trigged the flow'),
  throwError: z.boolean().nullish()
    .describe('If the callable response actor should throw an error to the call flow actor'),
});

export type CallableResponseActorOptions = z.infer<typeof CallableResponseActorOptionsSchema>;

export const CallableResponseActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    payload: {
      type: BIQJsonSchemaType.Any,
      title: 'Payload',
      description: 'The payload to emit on the Call flow actor that trigged the flow',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
    throwError: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Throw Error',
      description: 'If the callable response actor should throw an error to the call flow actor',
      default: false,
      ui: {
        component: 'switch',
      },
    },
  },
};

/** The response schema for the CallableResponseActor */
export const CallableResponseActorResultSchema = z.any().describe('The payload provided from the options of the CallableResponseActor');

export type CallableResponseActorResult = z.infer<typeof CallableResponseActorResultSchema>;
```

## Emitted Message

The CallableResponseActor emits the payload it sent back to the parent flow:

```json
{
  "result": "processed data",
  "status": "success"
}
```

The exact structure depends on what you configure in the `payload` option.

## Examples

### Simple Response with Static Data

```yaml
configuration:
  options:
    payload:
      success: true
      message: Sub-flow completed successfully
```

### Dynamic Response from Upstream Actor

```yaml
configuration:
  options:
    payload: ${{ msg.process_data.result }}
```

### Conditional Response with Computed Data

```yaml
configuration:
  inputs:
    processedItems: ${{ msg.collect_items.items }}
    totalCount: ${{ msg.collect_items.items.length }}
  options:
    payload:
      items: ${{ inputs.processedItems }}
      count: ${{ inputs.totalCount }}
      processedAt: ${{ Q.currentDateTime() }}
```

### Error Response

```yaml
configuration:
  options:
    payload:
      error: Validation failed
      details: ${{ msg.validation.errors }}
    throwError: true
```

### Conditional Error Handling

```yaml
configuration:
  inputs:
    hasError: ${{ !Q.isNil(err.api_call) }}
  options:
    payload: ${{ inputs.hasError ? err.api_call : msg.api_call.body }}
    throwError: ${{ inputs.hasError }}
```

## Usage with CallableTriggerActor and CallFlowActor

The CallableResponseActor works in a parent-child flow relationship:

**Parent Flow (calls the sub-flow):**
```yaml
ACTR01callFlow:
  type: CallFlowActor
  msgVar: call_result
  configuration:
    options:
      flowId: sub-flow-id
      payload: ${{ msg.trigger.body }}
```

**Sub-Flow (returns response to parent):**
```yaml
# CallableTriggerActor starts the sub-flow
ACTR01trigger:
  type: CallableTriggerActor
  msgVar: callable_trigger
  configuration:
    options: {}

# ... processing actors ...

# CallableResponseActor returns data to parent
ACTR01response:
  type: CallableResponseActor
  msgVar: callable_response
  configuration:
    options:
      payload: ${{ msg.process_result }}
```

## Workflow Diagram

```
Parent Flow:
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Trigger   │────>│ CallFlowActor│────>│  Continue   │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │ calls              ▲
                           ▼                    │ returns
Sub-Flow:                                       │
┌─────────────────┐     ┌─────────┐     ┌──────┴────────────┐
│CallableTrigger  │────>│ Process │────>│CallableResponse   │
└─────────────────┘     └─────────┘     └───────────────────┘
```

## Use Cases

| Scenario | Description |
|----------|-------------|
| Reusable Processing | Create sub-flows for common operations (data transformation, API calls) |
| Error Isolation | Isolate complex error-prone logic in sub-flows |
| Modular Workflows | Break large workflows into manageable sub-flows |
| Parallel Sub-flow Execution | Call multiple sub-flows and collect their responses |
| Conditional Processing | Route to different sub-flows based on conditions |

## Error Handling

When `throwError: true`:
- The CallFlowActor in the parent flow will receive an error
- If the parent's CallFlowActor has `continueOnError: true`, the error is stored in `err.call_result`
- If `continueOnError: false` (default), the parent flow will fail

```yaml
# Sub-flow with error
configuration:
  options:
    payload:
      error: Processing failed
      code: VALIDATION_ERROR
    throwError: true

# Parent flow handling error
ACTR01callFlow:
  type: CallFlowActor
  msgVar: sub_flow_result
  continueOnError: true  # Handle error gracefully

# Downstream actor in parent
configuration:
  inputs:
    hasError: ${{ !Q.isNil(err.sub_flow_result) }}
    result: ${{ msg.sub_flow_result ?? err.sub_flow_result?.payload }}
```
