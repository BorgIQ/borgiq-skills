# AI Router Actor Reference

The AiRouterActor classifies input and routes messages to different outputs based on AI-powered classification. It combines the functionality of an AI Actor and a Router into a single actor.

## Table of Contents

- [When to Use](#when-to-use)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [Source Ports](#source-ports)
- [Route Descriptions](#route-descriptions)
- [Results Object](#results-object)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Examples](#examples)

## When to Use

Use AiRouterActor instead of separate AiActor + Router when:
- You need to classify input into categories
- Different downstream workflows should handle different input types
- You want to reduce actor count and simplify the flow

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: AiRouterActor
    version: 1
    name: Actor Name Here
    msgVar: actor_name_here
    description: What this actor does
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTj50dtyn
        name: Route Name
        description: When to choose this route
      - id: SPRTdefault
        name: Default Route
        description: Fallback route
    configuration:
      inputs:
        key: value
      options:
        model: claude-haiku-4-5
        input: ${{ Q.toJSON(inputs) }}
        emitType: singleRoute
        routeDescriptions:
          RouteName: When to choose this route
    schemas:
      inputs:
        type: object
        properties:
          userMessage:
            type: string
            title: User Message
        required:
          - userMessage
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Options Reference

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `model` | string | No | AI model to use. Default: `claude-haiku-4-5` |
| `input` | string | Yes | The input text to classify |
| `emitType` | string | No | Routing behavior: `singleRoute` (default) or `multiRoute` |
| `routeDescriptions` | object | Yes | Map of route names to their selection criteria |

**Default:** Always start with `claude-haiku-4-5` unless the task requires more advanced reasoning capabilities.

**Input Best Practice:** Use `${{ Q.toJSON(inputs) }}` for the `input` option. This serializes all schema-backed inputs as a JSON object, ensuring the AI model receives structured, complete context for classification. This is preferred over manually concatenating individual input fields.

## TypeScript Schema Definition

The complete TypeScript schema for AiRouterActor options:

```typescript
import { z } from 'zod';

export enum AiRouterActorEmitType {
  SingleRoute = 'singleRoute',
  MultiRoute = 'multiRoute',
}

/** The options schema builder for the AiRouterActor since it changes for the sourcePorts configuration */
export const buildAiRouterActorOptionsSchema = (sourcePorts: RuntimeActorSourcePort[]) => z.object({
  model: z.string().nullish()
    .describe('The model to use for the AI provider. Defaults to claude-haiku-4-5 if not provided'),
  emitType: z.enum(['singleRoute', 'multiRoute']).nullish()
    .describe('How the AI router actor will function: singleRoute emits on one condition being true, multiRoute emits on all matching conditions'),
  input: z.any()
    .describe('The input to the AI router actor'),
  routeDescriptions: z.record(z.string(), z.string())
    .describe('The text definitions for the routes. Keys are route names from sourcePorts, values are selection criteria descriptions'),
});

export type AiRouterActorOptions = {
  input: unknown,
  model?: string,
  emitType?: AiRouterActorEmitType,
  routeDescriptions: { [portName: string]: string },
};

/** The result schema for the AiRouterActor */
export const AiRouterResultSchema = z.object({
  route: z.string()
    .describe('The port name that the message was emitted from'),
  meta: z.object({
    model: z.string()
      .describe('The model used to generate the response to determine the route'),
    usage: z.object({
      promptTokens: z.number().int()
        .describe('The number of tokens in the prompt'),
      completionTokens: z.number().int()
        .describe('The number of tokens in the completion'),
      totalTokens: z.number().int()
        .describe('The total number of tokens used'),
    }),
    fromCache: z.boolean()
      .describe('Whether the response was fetched from the cache'),
  }),
});
```

### Emit Types

| Value | Description |
|-------|-------------|
| `singleRoute` | Emit to exactly one route (most common) |
| `multiRoute` | Emit to multiple routes if input matches multiple categories |

## Source Ports

Each route requires a corresponding source port:

```yaml
sourcePorts:
  - id: SPRTt2vfgz2
    name: Sales
    description: Choose this route if the input is related to Sales related questions
  - id: SPRT0jmq08b
    name: Support
    description: Choose this route if the input is related to Support
  - id: SPRTdefault
    name: Others
    description: Fallback for unmatched inputs
```

**Important:** The `name` field in source ports must match the keys in `routeDescriptions`.

## Route Descriptions

Define when each route should be selected:

```yaml
options:
  routeDescriptions:
    Sales: Choose this route if the input is related to Sales related questions
    Support: Choose this route if the input is related to Support
```

Write clear, specific descriptions that help the AI model distinguish between routes.

## Results Object

After the AI router executes, the `results` object contains:

```json
{
  "route": "Support",
  "meta": {
    "model": "claude-haiku-4-5",
    "usage": {
      "promptTokens": 120,
      "completionTokens": 15,
      "totalTokens": 135
    },
    "fromCache": false
  }
}
```

| Field | Description |
|-------|-------------|
| `route` | The port name that the message was emitted from |
| `meta.model` | The model used to determine the route |
| `meta.usage` | Token usage statistics |
| `meta.fromCache` | Whether the response was fetched from cache |

## Common Patterns

### Customer Support Routing

```yaml
sourcePorts:
  - id: SPRTrc1wrnm
    name: Billing
    description: Billing inquiries, payment issues, subscription questions
  - id: SPRT4bdkvxf
    name: Technical
    description: Technical problems, bugs, feature issues
  - id: SPRTabc6ui4
    name: Sales
    description: Pricing questions, upgrades, enterprise plans
  - id: SPRTdefault
    name: General
    description: General inquiries
configuration:
  inputs:
    customerMessage: ''
  options:
    model: claude-haiku-4-5
    input: ${{ Q.toJSON(inputs) }}
    emitType: singleRoute
    routeDescriptions:
      Billing: Billing inquiries, payment issues, invoice questions, subscription management
      Technical: Technical problems, bugs, errors, feature not working, integration issues
      Sales: Pricing questions, plan upgrades, enterprise inquiries, volume discounts
```

### Intent Classification

```yaml
sourcePorts:
  - id: SPRTkf9q81q
    name: Question
    description: User is asking a question
  - id: SPRTwiyxlxr
    name: Command
    description: User is giving a command or instruction
  - id: SPRT9ihx8lz
    name: Feedback
    description: User is providing feedback
  - id: SPRTdefault
    name: Other
    description: Unclassified intent
configuration:
  inputs:
    userText: ''
  options:
    model: claude-haiku-4-5
    input: ${{ Q.toJSON(inputs) }}
    emitType: singleRoute
    routeDescriptions:
      Question: The user is asking a question and expects an answer
      Command: The user is giving a direct instruction or command to perform an action
      Feedback: The user is providing feedback, suggestions, or complaints
```

### Multi-Route Classification

Use `emitType: multiRoute` when input can belong to multiple categories:

```yaml
configuration:
  inputs:
    content: ''
  options:
    model: claude-haiku-4-5
    input: ${{ Q.toJSON(inputs) }}
    emitType: multiRoute
    routeDescriptions:
      Urgent: Content indicates urgency or time-sensitivity
      Confidential: Content contains sensitive or confidential information
      ActionRequired: Content requires a response or action
```

## Best Practices

1. **Use `Q.toJSON(inputs)` for input** - Serialize all schema-backed inputs as JSON for structured, complete context
2. **Write clear route descriptions** - Be specific about when each route should be selected
3. **Use mutually exclusive routes** - For `singleRoute`, ensure routes don't overlap
4. **Include a default route** - Always have a fallback for unmatched inputs
5. **Keep route count reasonable** - 2-6 routes work best; more routes reduce accuracy
6. **Test with edge cases** - Verify classification works for ambiguous inputs
7. **Use appropriate model** - Start with `claude-haiku-4-5`; upgrade only if classification accuracy is insufficient

## Examples

### Basic Sales/Support Router

Routes user messages to Sales, Support, or a default fallback based on content classification.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kcx1vexr5902g9mp2xbhbjan:
    name: AI Router
    type: AiRouterActor
    msgVar: ai_router
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: The AI router actor will emit messages based on various route definitions.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRT5d5gj2s
        name: Sales
        description: Choose this route if the input is related to Sales related questions
      - id: SPRT5d5gjl4
        name: Support
        description: Choose this route if the input is related to Support
      - id: SPRTdefault
        name: Others
        description: ''
    configuration:
      options:
        model: gemini-3-flash-preview
        input: I need your help to setup this software
        emitType: singleRoute
        routeDescriptions:
          Sales: Choose this route if the input is related to Sales related questions
          Support: Choose this route if the input is related to Support
    continueOnError: false
    id: ACTR01kcx1vexr5902g9mp2xbhbjan
    position:
      x: 452.3401951839253
      'y': 6486.932328041766
    edges: {}
```

**Key Features:**
- Three routes: Sales, Support, and Others (default fallback)
- Uses `singleRoute` emit type to route to exactly one destination
- Route descriptions match the source port names
- Default route (`SPRTdefault`) catches unmatched inputs

---

## Quick Example

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01example:
    type: AiRouterActor
    version: 1
    name: Support Ticket Router
    msgVar: support_ticket_router
    description: Routes support tickets to appropriate teams based on content
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTjyka6ql
        name: Sales
        description: Sales related questions
      - id: SPRTn7gduk5
        name: Support
        description: Support related questions
      - id: SPRTdefault
        name: Others
        description: Fallback route
    configuration:
      inputs:
        message: ''
      options:
        model: claude-haiku-4-5
        input: ${{ Q.toJSON(inputs) }}
        emitType: singleRoute
        routeDescriptions:
          Sales: Choose this route if the input is related to Sales related questions
          Support: Choose this route if the input is related to Support
    schemas:
      inputs:
        type: object
        properties:
          message:
            type: string
            title: Message
            description: The message to classify and route
        required:
          - message
    id: ACTR01example
    position:
      x: 0
      'y': 0
    edges: {}
```
