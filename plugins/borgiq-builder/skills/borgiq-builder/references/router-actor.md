# Router Actor Reference

The RouterActor routes messages to different outputs based on boolean conditions. Use it for if/else logic, switch statements, and conditional message routing.

## Table of Contents

- [When to Use](#when-to-use)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [Source Ports](#source-ports)
- [Conditions](#conditions)
- [Results Object](#results-object)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Examples](#examples)

## When to Use

Use RouterActor when:
- You need if/else branching logic in your workflow
- You want to route messages based on data conditions
- You need switch-case style routing with multiple branches
- You want deterministic routing based on expression evaluation

**Note:** For AI-powered classification routing, use [AiRouterActor](ai-router-actor.md) instead.

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: RouterActor
    version: 1
    name: Actor Name Here
    msgVar: actor_name_here
    description: What this actor does
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTudmbfzw
        name: Route Name
        description: When to choose this route
      - id: SPRTdefault
        name: Default Route
        description: Fallback route
    configuration:
      options:
        emitType: singleRoute
        conditions:
          RouteName: ${{ boolean_expression }}
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Options Reference

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `emitType` | string | No | Routing behavior: `singleRoute` (default) or `multiRoute` |
| `conditions` | object | Yes | Map of route names to boolean expressions |

## TypeScript Schema Definition

The complete TypeScript schema for RouterActor options:

```typescript
import { z } from 'zod';

export enum RouterActorEmitType {
  SingleRoute = 'singleRoute',
  MultiRoute = 'multiRoute',
}

/** The options schema builder for the RouterActor since it changes for the sourcePorts configuration */
export const buildRouterActorOptionsSchema = (sourcePorts: RuntimeActorSourcePort[]) => z.object({
  emitType: z.enum(['singleRoute', 'multiRoute']).nullish()
    .describe('How the router actor will function: singleRoute emits on the first true condition, multiRoute emits on all true conditions. Defaults to singleRoute'),
  conditions: z.record(z.string(), z.any())
    .describe('The conditions for the routes. Keys are route names from sourcePorts, values are boolean expressions to evaluate'),
});

export type RouterActorOptions = {
  emitType?: RouterActorEmitType,
  conditions: { [portName: string]: boolean },
};

/** The result schema for the RouterActor */
export const RouterActionResultSchema = z.string()
  .describe('The port name that the message was emitted from');
```

### Emit Types

| Value | Description |
|-------|-------------|
| `singleRoute` | Emit to the first route with a true condition (default) |
| `multiRoute` | Emit to all routes with true conditions |

## Source Ports

Each route requires a corresponding source port:

```yaml
sourcePorts:
  - id: SPRTuvakyzc
    name: 'Yes'
    description: Condition is true
  - id: SPRTfs2bx3k
    name: 'No'
    description: Condition is false
  - id: SPRTdefault
    name: Default
    description: Fallback route
```

**Important:** The `name` field in source ports must match the keys in `conditions`. The default port (`SPRTdefault`) is used when no conditions match.

## Conditions

Define boolean expressions for each route:

```yaml
options:
  conditions:
    'Yes': ${{ !Q.isNil(msg.upstream_actor.value) }}
    'No': ${{ Q.isNil(msg.upstream_actor.value) }}
```

Conditions are evaluated in order. For `singleRoute`, the first true condition wins.

## Results Object

After the router executes, the `results` object contains:

```json
"Yes"
```

The result is simply the port name that the message was emitted from.

| Field | Description |
|-------|-------------|
| `results` | The port name that was selected |

## Common Patterns

### Simple If/Else

```yaml
sourcePorts:
  - id: SPRTvnkbb93
    name: 'Yes'
    description: Value exists
  - id: SPRTdefault
    name: 'No'
    description: Value does not exist
configuration:
  options:
    emitType: singleRoute
    conditions:
      'Yes': ${{ !Q.isNil(msg.fetch_data.value) }}
```

### Multiple Conditions (Switch)

```yaml
sourcePorts:
  - id: SPRTa59ivcy
    name: High
    description: Priority is high
  - id: SPRTitvoild
    name: Medium
    description: Priority is medium
  - id: SPRTwxoof07
    name: Low
    description: Priority is low
  - id: SPRTdefault
    name: Unknown
    description: Priority not recognized
configuration:
  options:
    emitType: singleRoute
    conditions:
      High: ${{ msg.ticket.priority === 'high' }}
      Medium: ${{ msg.ticket.priority === 'medium' }}
      Low: ${{ msg.ticket.priority === 'low' }}
```

### Status Code Routing

```yaml
sourcePorts:
  - id: SPRT4dgwd9g
    name: Success
    description: HTTP 2xx response
  - id: SPRT0zn4l1y
    name: ClientError
    description: HTTP 4xx response
  - id: SPRTibelbm8
    name: ServerError
    description: HTTP 5xx response
  - id: SPRTdefault
    name: Other
    description: Other status codes
configuration:
  options:
    emitType: singleRoute
    conditions:
      Success: ${{ Q.isHTTPStatusInRange(msg.api_call.statusCode, ["200-299"]) }}
      ClientError: ${{ Q.isHTTPStatusInRange(msg.api_call.statusCode, ["400-499"]) }}
      ServerError: ${{ Q.isHTTPStatusInRange(msg.api_call.statusCode, ["500-599"]) }}
```

### Array Check

```yaml
sourcePorts:
  - id: SPRTttvtjc1
    name: HasItems
    description: Array has items
  - id: SPRTdefault
    name: Empty
    description: Array is empty
configuration:
  options:
    emitType: singleRoute
    conditions:
      HasItems: ${{ msg.search_results.items?.length > 0 }}
```

### Multi-Route Emit

Use `emitType: multiRoute` to emit to multiple routes when conditions are true:

```yaml
configuration:
  options:
    emitType: multiRoute
    conditions:
      SendEmail: ${{ inputs.notifyEmail }}
      SendSlack: ${{ inputs.notifySlack }}
      LogToDatabase: ${{ inputs.logEnabled }}
```

### Error Routing

Route based on whether an upstream actor with `continueOnError: true` succeeded or failed:

```yaml
sourcePorts:
  - id: SPRTwcwzp1m
    name: Success
    description: Upstream actor succeeded
  - id: SPRTdefault
    name: Error
    description: Upstream actor failed
configuration:
  options:
    emitType: singleRoute
    conditions:
      Success: ${{ Q.isNil(err.fetch_data) && !Q.isNil(msg.fetch_data) }}
```

**Note:** When an upstream actor has `continueOnError: true` and encounters an error:
- The error output is stored in `err.ActorName` (not `msg.ActorName`)
- `msg.ActorName` will be `undefined`
- Use `Q.isNil(err.actor_name)` to check if the actor succeeded
- Use `!Q.isNil(err.actor_name)` to check if the actor failed

## Best Practices

1. **Use clear condition expressions** - Make conditions readable and self-documenting
2. **Order conditions by priority** - For `singleRoute`, put most important conditions first
3. **Always have a default route** - Ensure unmatched cases are handled
4. **Use Q-lib functions** - Leverage `Q.isNil`, `Q.isHTTPStatusInRange`, etc.
5. **Keep conditions simple** - Complex logic should be in a DenoActor before the router

## Examples

### Check for Existing Data

Routes based on whether upstream actor returned data.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01k61a7rnc6r27414vqjwade0p:
    name: Are there Existing Browser?
    type: RouterActor
    msgVar: are_there_existing_browser
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: The router actor will emit messages based on various expressions.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRT5d5gj2s
        name: 'Yes'
        description: Existing Browsers Found
      - id: SPRTdefault
        name: 'No'
        description: No Existing Browsers Found
    configuration:
      options:
        emitType: singleRoute
        conditions:
          'Yes': ${{!Q.isNil(msg.fetch_existing_browser.value)}}
    continueOnError: false
    id: ACTR01k61a7rnc6r27414vqjwade0p
    position:
      x: -1115.08984375
      'y': 1404.15625
    edges: {}
```

**Key Features:**
- Two routes: Yes (data exists) and No (default fallback)
- Uses `Q.isNil()` to check for null/undefined values
- Uses `singleRoute` emit type for exclusive routing
- Default route catches the negative case

---

## Quick Example

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01example:
    type: RouterActor
    version: 1
    name: Check User Status
    msgVar: check_user_status
    description: Routes based on user active status
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTz7r3lca
        name: Active
        description: User is active
      - id: SPRTgzuftoe
        name: Inactive
        description: User is inactive
      - id: SPRTdefault
        name: Unknown
        description: Status unknown
    configuration:
      options:
        emitType: singleRoute
        conditions:
          Active: ${{ msg.user.status === 'active' }}
          Inactive: ${{ msg.user.status === 'inactive' }}
    schemas: {}
    id: ACTR01example
    position:
      x: 0
      'y': 0
    edges: {}
```
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kb92kn6t3tar8ag2x34b7641:
    name: Router
    type: RouterActor
    msgVar: router
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: The router actor will emit messages based on various expressions.
    sourcePorts:
      - id: SPRT5d5gj2s
        name: SALES
        description: ''
      - id: SPRTtiklusf
        name: ENG
        description: ''
      - id: SPRTdefault
        name: OTHERS
        description: ''
    configuration:
      options:
        emitType: singleRoute
        conditions:
          SALES: ${{ true }}
    continueOnError: false
    id: ACTR01kb92kn6t3tar8ag2x34b7641
    position:
      x: -1678.883719665472
      'y': -414.2874024153003
    edges: {}
