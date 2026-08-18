# Webhook Response Actor Reference

The WebhookResponseActor sends a custom HTTP response back to the caller of a WebhookTriggerActor. It must be used when the webhook trigger has `respondImmediately: false`.

## Table of Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [Emitted Message](#emitted-message)
- [Examples](#examples)
- [Usage with WebhookTriggerActor](#usage-with-webhooktriggeractor)
- [Multiple Response Paths](#multiple-response-paths)
- [Use Cases](#use-cases)

## Overview

When a WebhookTriggerActor receives an HTTP request, it can either:
1. Respond immediately with a configured response (`respondImmediately: true`)
2. Wait for a WebhookResponseActor to provide a dynamic response (`respondImmediately: false`)

Use WebhookResponseActor when you need to:
- Return dynamic response data based on workflow processing
- Set custom status codes based on conditions
- Include computed headers in the response
- Return different responses based on routing logic

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: WebhookResponseActor
    version: 1
    name: Webhook Response
    msgVar: webhook_response
    description: Respond to webhook request
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        statusCode: 200
        body: ${{ msg.process_data.result }}
        headers:
          content-type: application/json
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
| `statusCode` | number | No | 200 | HTTP status code to return |
| `body` | any | No | - | Response body (can be string, object, etc.) |
| `headers` | object | No | - | Custom headers to include in the response |

## TypeScript Schema Definition

The complete TypeScript schema for WebhookResponseActor options:

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

/** The options schema for the WebhookResponseActor */
export const WebhookResponseActorOptionsSchema = z.object({
  statusCode: z.number().nullish()
    .describe('The status code of the response to return to the webhook request, defaults to 200'),
  body: z.unknown().nullish()
    .describe('The body of the response to return to the webhook request'),
  headers: z.record(z.string(), z.unknown()).nullish()
    .describe('The headers of the response to return to the webhook request'),
});

export type WebhookResponseActorOptions = z.infer<typeof WebhookResponseActorOptionsSchema>;

export const WebhookResponseActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    statusCode: {
      type: BIQJsonSchemaType.Number,
      title: 'Status Code',
      description: 'The status code of the response to return to the webhook request, defaults to 200',
      default: 200,
    },
    body: {
      type: BIQJsonSchemaType.Any,
      title: 'Body',
      description: 'The body of the response to return to the webhook request',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
    headers: {
      type: BIQJsonSchemaType.Any,
      title: 'Headers',
      description: 'The headers of the response to return to the webhook request',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
  },
};

/** The result schema for the WebhookResponseActor */
export const WebhookResponseActorResultSchema = z.object({
  statusCode: z.number()
    .describe('The status code of the response to return to the webhook request'),
  body: z.unknown()
    .describe('The body of the response to return to the webhook request'),
  headers: z.record(z.string(), z.unknown()).nullable()
    .describe('The headers of the response to return to the webhook request'),
});

export type WebhookResponseActorResult = z.infer<typeof WebhookResponseActorResultSchema>;
```

## Emitted Message

The WebhookResponseActor emits the response it sent:

```json
{
  "statusCode": 200,
  "body": { "message": "Success", "id": "12345" },
  "headers": { "content-type": "application/json" }
}
```

## Examples

### Simple JSON Response

```yaml
configuration:
  options:
    statusCode: 200
    body:
      success: true
      message: Request processed successfully
    headers:
      content-type: application/json
```

### Dynamic Response from Upstream Actor

```yaml
configuration:
  options:
    statusCode: 200
    body: ${{ msg.process_data.result }}
    headers:
      content-type: application/json
      x-request-id: ${{ msg.webhook_trigger.headers['x-request-id'] }}
```

### Error Response

```yaml
configuration:
  options:
    statusCode: 400
    body:
      error: true
      message: Invalid request payload
    headers:
      content-type: application/json
```

### Conditional Status Code

```yaml
configuration:
  inputs:
    success: ${{ msg.api_call.statusCode >= 200 && msg.api_call.statusCode < 300 }}
  options:
    statusCode: ${{ inputs.success ? 200 : 500 }}
    body: ${{ inputs.success ? msg.api_call.body : { error: 'Processing failed' } }}
    headers:
      content-type: application/json
```

### Echo Back Request Body

```yaml
configuration:
  options:
    statusCode: 200
    body: ${{ msg.webhook_trigger.body }}
    headers:
      content-type: application/json
```

## Usage with WebhookTriggerActor

The WebhookResponseActor works in conjunction with a WebhookTriggerActor that has `respondImmediately: false`:

```yaml
# Webhook Trigger (does not respond immediately)
ACTR01trigger:
  type: WebhookTriggerActor
  msgVar: webhook_trigger
  configuration:
    options:
      allowedMethods:
        - post
      respondImmediately: false  # Wait for WebhookResponseActor
      emitRawBody: false

# ... processing actors ...

# Webhook Response (sends the actual response)
ACTR01response:
  type: WebhookResponseActor
  msgVar: webhook_response
  configuration:
    options:
      statusCode: 200
      body: ${{ msg.process_result }}
      headers:
        content-type: application/json
```

## Multiple Response Paths

When using RouterActor, you can have multiple WebhookResponseActors for different paths:

```yaml
# Router decides which response to send
ACTR01router:
  type: RouterActor
  sourcePorts:
    - id: SPRT5d5gj2s
      name: Success
    - id: SPRTg5vsvui
      name: Error
    - id: SPRTdefault
      name: F
  configuration:
    options:
      emitType: singleRoute
      conditions:
        Success: ${{ msg.api_call.statusCode === 200 }}
        Error: ${{ msg.api_call.statusCode !== 200 }}

# Success response
ACTR01successResponse:
  type: WebhookResponseActor
  msgVar: success_response
  configuration:
    options:
      statusCode: 200
      body: ${{ msg.api_call.body }}

# Error response
ACTR01errorResponse:
  type: WebhookResponseActor
  msgVar: error_response
  configuration:
    options:
      statusCode: 500
      body:
        error: true
        message: Processing failed
```

## Use Cases

| Scenario | Description |
|----------|-------------|
| API Gateway | Process and transform request before responding |
| Webhook Handler | Validate and process webhook payloads |
| Dynamic Responses | Return different responses based on business logic |
| Error Handling | Return appropriate error codes based on processing results |
| Request Echo | Debug by echoing back the request for inspection |
