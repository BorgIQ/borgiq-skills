# Callable Trigger Actor Reference

The CallableTriggerActor starts a workflow when invoked by another flow (sub-flow invocation).

## Table of Contents

- [Overview](#overview)
- [Input Schema — the Sub-Flow Contract](#input-schema--the-sub-flow-contract)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [Emitted Message](#emitted-message)
- [Calling a Sub-Flow](#calling-a-sub-flow)
- [Returning Results to Parent Flow](#returning-results-to-parent-flow)
- [Common Patterns](#common-patterns)
- [Accessing Payload in Sub-Flow](#accessing-payload-in-sub-flow)
- [Use Cases](#use-cases)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

Callable triggers enable workflows to call other workflows, creating reusable sub-flows. When a parent flow invokes a sub-flow, the CallableTriggerActor receives the payload and starts execution. Use callable triggers for:

- Creating reusable workflow components
- Breaking complex workflows into smaller, manageable pieces
- Building shared utility flows (data transformation, notifications, etc.)
- Implementing hierarchical workflow architectures

## Input Schema — the Sub-Flow Contract

A CallableTriggerActor is a **public entry point**: other flows invoke it blind, handing it a `payload`. Treat it like a typed function signature — **always declare the expected payload as `schemas.inputs` on the trigger** instead of leaving `schemas: {}`. That schema is the sub-flow's contract:

- **It drives the editor.** The parent CallFlowActor's payload form is generated from this schema, and it renders UI hints when the sub-flow is invoked manually. Without it, callers configure the payload blind.
- **It documents the interface** for callers and for agents editing the canvas later.
- **It is the single source of field names** that every downstream actor reads from.

> **The schema is not enforced at runtime.** The platform passes the caller's `payload` into the sub-flow as-is — a caller that omits a `required` field or sends the wrong type does **not** fail at the boundary; the bad value surfaces as `undefined` (or a wrong type) wherever a downstream actor reads it. The contract holds only as long as you keep both sides in lockstep — which is exactly why declaring it and reading only from it matters.

> Reminder (see [Common Actor Structure](../SKILL.md#common-actor-structure)): the input schema lives at **`schemas.inputs`** (actor level). `configuration.options` for a CallableTriggerActor is always `{}`.

### The rule: schema the trigger, then read from it everywhere

1. **Declare every payload field** in the trigger's `schemas.inputs`, marking the genuinely-required ones in `required`. Mirror each field in `configuration.inputs` with an empty default (e.g. `topic: ''`) so the actor's input surface is explicit.
2. **Every downstream actor reads its values from those exact fields** — `${{ msg.<callable_msgVar>.<field> }}` — and declares them in its *own* `schemas.inputs`. No downstream actor should invent a field that isn't in the trigger's schema, and the trigger shouldn't declare a field nobody reads. Keep them in lockstep.
3. **The caller's `payload` keys must match** the trigger's `schemas.inputs` properties (see [call-flow-actor.md](call-flow-actor.md)). Drift between the caller `payload`, the trigger `schemas.inputs`, and the downstream `msg.*` reads is the single most common sub-flow bug — and because nothing validates at the boundary, it fails silently, not fast.

This makes the sub-flow a typed function: the trigger schema is its **signature**, the downstream actors are its **body**, and the [CallableResponseActor](callable-response-actor.md) schema is its **return type**. For schema design itself (tight vs loose, enums, `$ref`, the `type: any` convention), use the `borgiq-json-schema-builder` spoke.

A complete schema'd example is in [Callable Trigger with Input Schema](#callable-trigger-with-input-schema) below.

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: CallableTriggerActor
    version: 1
    name: Callable Trigger
    msgVar: callable_trigger
    description: Entry point for sub-flow invocation from parent flows
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options: {}
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Options Reference

The CallableTriggerActor currently has no configurable options. It simply receives the payload sent by the parent flow.

| Option | Type | Description |
|--------|------|-------------|
| (none) | - | No options currently available |

## Emitted Message

The callable trigger emits the payload sent by the parent flow:

```json
{
  "...payload from parent flow..."
}
```

The message structure depends entirely on what the parent flow sends when invoking the sub-flow.

## Calling a Sub-Flow

Parent flows invoke sub-flows using **CallFlowActor**. This actor calls a CallableTriggerActor and optionally waits for the response from CallableResponseActor.

See [call-flow-actor.md](call-flow-actor.md) for complete documentation.

```yaml
# CallFlowActor invokes a sub-flow
ACTR01callSubFlow:
  type: CallFlowActor
  msgVar: sub_flow_result
  configuration:
    options:
      workspaceSlug: my-workspace  # Optional, defaults to current workspace
      canvasSlug: my-subflow       # Optional, defaults to current canvas
      callableTriggerActorId: ACTR01kd6tesvky0mh8x1css3sv5yg
      payload:
        userId: ${{ msg.trigger.body.userId }}
        action: process
        data: ${{ msg.trigger.body.data }}
      waitForResponse: true
      timeoutInSeconds: 60
```

### CallFlowActor Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `callableTriggerActorId` | string | Yes | - | Actor ID of the CallableTriggerActor to invoke |
| `payload` | any | Yes | - | Data to pass to the sub-flow |
| `workspaceSlug` | string | No | Current workspace | Workspace containing the sub-flow |
| `canvasSlug` | string | No | Current canvas | Canvas containing the sub-flow |
| `waitForResponse` | boolean | No | false | Wait for sub-flow to complete |
| `timeoutInSeconds` | number | No | No timeout | Maximum wait time for response |

### Synchronous vs Asynchronous Calls

**Synchronous (waitForResponse: true)**
- Parent flow waits for sub-flow to complete
- Sub-flow result is returned to the parent
- Use for: data processing, transformations, lookups

**Asynchronous (waitForResponse: false)**
- Parent flow continues immediately
- Sub-flow runs independently
- Use for: fire-and-forget tasks, parallel processing

## Returning Results to Parent Flow

When `waitForResponse: true`, the sub-flow can return results to the parent using **CallableResponseActor**. This actor is specifically designed for callable flows and can **only** be used in workflows triggered by CallableTriggerActor.

See [callable-response-actor.md](callable-response-actor.md) for complete documentation.

```typescript
// In sub-flow's DenoActor (final actor)
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // Process the data from callable trigger
  const result = await processData(req.inputs);

  // This results value is sent back to the parent flow
  return {
    results: {
      success: true,
      processedData: result,
      processedAt: new Date().toISOString(),
    },
  };
}
```

## Common Patterns

### Data Processing Sub-Flow

Create a reusable data transformation flow:

**Sub-Flow (callable):**
```yaml
# CallableTriggerActor receives: { data: [...], format: "csv" }
# DenoActor transforms data
# CallableResponseActor returns transformed data to parent
```

**Parent Flow (CallFlowActor):**
```yaml
ACTR01transformData:
  type: CallFlowActor
  msgVar: transform_result
  configuration:
    options:
      workspaceSlug: shared-utils
      canvasSlug: transform-data
      callableTriggerActorId: ACTR01transformxxxxxxxxxxxxxxxx
      payload:
        data: ${{ msg.raw_data.items }}
        format: csv
      waitForResponse: true
      timeoutInSeconds: 60
```

### Notification Sub-Flow

Create a reusable notification flow:

**Sub-Flow (callable):**
```yaml
# CallableTriggerActor receives: { channel: "email", recipient: "...", message: "..." }
# Routes to appropriate notification channel
# Sends notification
```

**Parent Flow (fire-and-forget):**
```yaml
ACTR01sendNotification:
  type: CallFlowActor
  msgVar: notification_result
  configuration:
    options:
      workspaceSlug: shared-utils
      canvasSlug: send-notification
      callableTriggerActorId: ACTR01notifyxxxxxxxxxxxxxxxx
      payload:
        channel: email
        recipient: ${{ msg.user.email }}
        subject: Task Completed
        message: Your task has been completed.
      waitForResponse: false  # Fire-and-forget
```

### Lookup Sub-Flow

Create a reusable data lookup flow:

**Sub-Flow:**
```typescript
// CallableTriggerActor passes inputs to DenoActor
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const userId = req.inputs.userId;

  // Fetch user from database
  const user = await fetchUser(userId);

  if (!user) {
    return { results: { found: false, user: null } };
  }

  return {
    results: {
      found: true,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
      },
    },
  };
}
```

**Parent Flow (CallFlowActor):**
```yaml
ACTR01lookupUser:
  type: CallFlowActor
  msgVar: lookup_result
  configuration:
    options:
      workspaceSlug: shared-utils
      canvasSlug: lookup-user
      callableTriggerActorId: ACTR01lookupxxxxxxxxxxxxxx
      payload:
        userId: ${{ msg.trigger.body.userId }}
      waitForResponse: true
      timeoutInSeconds: 30

# Downstream actor can access: msg.lookup_result.found, msg.lookup_result.user
```

## Accessing Payload in Sub-Flow

The CallableTriggerActor's output is available to downstream actors via `msg`:

```yaml
# In downstream HttpRequestActor
configuration:
  inputs:
    userId: ${{ msg.callable_trigger.userId }}
    action: ${{ msg.callable_trigger.action }}
```

```typescript
// In downstream DenoActor
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // req.inputs contains the payload from callable trigger
  const { userId, action, data } = req.inputs;

  console.log(`Processing ${action} for user ${userId}`);

  return { results: { processed: true } };
}
```

## Use Cases

### Modular Workflow Architecture

Break large workflows into smaller, reusable components:

```
Main Flow
├── CallableTrigger: Data Validation Flow
├── CallableTrigger: Data Enrichment Flow
└── CallableTrigger: Notification Flow
```

### Shared Business Logic

Centralize common operations:

- User lookup and validation
- Data format conversion
- External API integration
- Notification dispatch

### Parallel Processing

Use MessageProcessorActor's `split` action combined with CallFlowActor to process multiple items in parallel:

```yaml
# Split tasks into individual items
ACTR01splitTasks:
  type: MessageProcessorActor
  msgVar: split_tasks
  configuration:
    options:
      action: split
      valueToSplit: ${{ msg.trigger.body.tasks }}
      emitKey: task

# Call sub-flow for each task (fire-and-forget for parallel execution)
ACTR01processTask:
  type: CallFlowActor
  msgVar: task_result
  continueOnError: true
  configuration:
    options:
      workspaceSlug: workers
      canvasSlug: process-task
      callableTriggerActorId: ACTR01workerxxxxxxxxxxxxxx
      payload: ${{ msg.split_tasks.task }}
      waitForResponse: false  # Fire-and-forget for parallel
```

## Best Practices

1. **Design for reusability** - Make sub-flows generic enough to be useful in multiple contexts
2. **Declare the input schema** - Define the expected payload as `schemas.inputs` on the CallableTriggerActor, have every downstream actor read from those fields, and document the return shape via CallableResponseActor. The schema is editor-enforced only, not runtime-validated — see [Input Schema — the Sub-Flow Contract](#input-schema--the-sub-flow-contract).
3. **Use meaningful names** - Name flows and triggers clearly (e.g., "Validate User Data", "Send Email Notification")
4. **Handle errors gracefully** - Sub-flows should handle errors and return meaningful error responses
5. **Consider timeouts** - Long-running sub-flows with `waitForResponse: true` can timeout; design accordingly
6. **Keep sub-flows focused** - Each sub-flow should do one thing well

## Examples

### Basic Callable Trigger

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kd2998w8c3rmqb498xwzb8r1:
    type: CallableTriggerActor
    version: 1
    name: Process Order Sub-Flow
    msgVar: process_order_sub_flow
    description: Reusable sub-flow for processing orders from parent workflows
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options: {}
    schemas: {}
    id: ACTR01kd2998w8c3rmqb498xwzb8r1
    position:
      x: 0
      'y': 0
    edges: {}
```

### Callable Trigger with Input Schema

This example shows a callable trigger with a defined input schema, useful for sub-flows that require specific input parameters — the schema generates the caller's payload form and UI hints (it is not runtime-validated; see [Input Schema — the Sub-Flow Contract](#input-schema--the-sub-flow-contract)).

**Important:** Input schemas are defined at `schemas.inputs` (at the actor level), NOT inside `configuration.options`. The `options` field for CallableTriggerActor must always be empty `{}`.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kcddpqxsakc25fn5c0hz9a35:
    type: CallableTriggerActor
    version: 1
    name: Research Sub Agent
    msgVar: research_sub_agent
    description: >-
      This is a research sub agent with capability to do web research for a
      topic, ask it to summarize the exact information you need. Use this agent
      to keep your context free from too many tool calls.
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        topic: ''
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
              options: {}
        required:
          - topic
          - fileSystemId
    id: ACTR01kcddpqxsakc25fn5c0hz9a35
    position:
      x: 0
      'y': 0
    edges: {}
```

**Key features of this example:**

- **Schema Location**: The input schema is at `schemas.inputs` (actor-level), NOT inside `configuration.options`
- **Empty Options**: `configuration.options: {}` - CallableTriggerActor never has options
- **Input Schema**: Defines required parameters (`topic`, `fileSystemId`) with types and validation
- **UI Hints**: Uses `ui` properties to control how inputs are rendered in the BorgIQ UI
  - `component: textarea` for multi-line text input
  - `component: input` for single-line input
  - `order` to control field display order
- **Placeholder and Sizing**: Configures textarea with placeholder text and auto-resize behavior

**Calling this sub-flow from a parent:**

Invoke the sub-flow from the parent with a **CallFlowActor** (the `callFlow` signal is no longer set from actor code):

```yaml
ACTR01callResearch:
  type: CallFlowActor
  msgVar: research_result
  configuration:
    options:
      workspaceSlug: my-workspace
      canvasSlug: research-agent
      callableTriggerActorId: ACTR01kcddpqxsakc25fn5c0hz9a35
      waitForResponse: true
      payload:
        topic: 'Latest trends in AI automation'
        fileSystemId: 'fs_12345'
```
