# Button Trigger Actor Reference

The ButtonTriggerActor starts a workflow when manually triggered via a button click in the BorgIQ UI.

## Table of Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [Emitted Message](#emitted-message)
- [Common Patterns](#common-patterns)
- [Accessing in Downstream Actors](#accessing-in-downstream-actors)
- [Quick Example](#quick-example)

## Overview

Button triggers provide a manual way to start workflows. They emit a message containing the payload defined in the configuration options. Use button triggers for:

- Manual workflow execution
- Testing and debugging workflows
- Ad-hoc data processing tasks
- User-initiated actions

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: ButtonTriggerActor
    version: 1
    name: Button Trigger
    msgVar: button_trigger
    description: Trigger the workflow manually with a button click
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        key1: value1
        key2: value2
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Options Reference

The `options` object defines the payload that will be emitted when the button is clicked. Any key-value pairs defined here become the trigger's output message.

| Option | Type | Description |
|--------|------|-------------|
| (any key) | any | Custom payload fields emitted as the trigger message |

### Dynamic Values

Options can include BorgIQ expressions for dynamic values:

```yaml
options:
  staticValue: "hello"
  dynamicTimestamp: ${{ Date.now() }}
  escapedExpression: '''${{ Date.now() }}'''
  arrayValue:
    - item1
    - 42
    - ${{ Date.now() }}
```

**Note:** To emit a literal string containing `${{ }}` without evaluation, wrap it in triple quotes: `'''${{ ... }}'''`

## Emitted Message

The button trigger emits a message containing the options payload. Downstream actors access this via `msg.button_trigger` (or the configured `msgVar`).

### Example Output

Given this configuration:

```yaml
options:
  key1: value1
  key2:
    - a
    - 42
    - 3.14
```

The emitted message will be:

```json
{
  "key1": "value1",
  "key2": ["a", 42, 3.14]
}
```

## Common Patterns

### Static Payload

```yaml
configuration:
  options:
    action: process
    environment: production
    maxItems: 100
```

### Dynamic Payload with Timestamp

```yaml
configuration:
  options:
    triggeredAt: ${{ Date.now() }}
    triggeredAtISO: ${{ new Date().toISOString() }}
```

### Mixed Static and Dynamic

```yaml
configuration:
  options:
    action: sync
    config:
      batchSize: 50
      startTime: ${{ Date.now() }}
```

## Accessing in Downstream Actors

In downstream actors, access the button trigger's payload:

```yaml
# In HttpRequestActor
configuration:
  inputs:
    action: ${{ msg.button_trigger.action }}
    config: ${{ msg.button_trigger.config }}
```

```typescript
// In DenoActor
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const triggerPayload = req.inputs.triggerData;
  console.log(`Action: ${triggerPayload.action}`);
  return { results: { processed: true } };
}
```

## Quick Example

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kd296g3a05smjmm9exvxhsxj:
    type: ButtonTriggerActor
    version: 1
    name: Process Data Button
    msgVar: process_data_button
    description: Manually trigger data processing workflow
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: processAll
        batchSize: 100
        dryRun: false
    schemas: {}
    id: ACTR01kd296g3a05smjmm9exvxhsxj
    position:
      x: 0
      'y': 0
    edges: {}
```
