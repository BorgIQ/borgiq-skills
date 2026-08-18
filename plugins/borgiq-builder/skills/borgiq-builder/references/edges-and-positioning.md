# Actor Connections and Edges

Actors are connected together via **edges** to form workflows. Each edge defines a connection from a source actor's output port to a target actor's input port.

## Table of Contents

- [Edge Structure](#edge-structure)
- [Edge Properties](#edge-properties)
- [Port IDs](#port-ids)
- [Generating Edge IDs](#generating-edge-ids)
- [Actor Positioning](#actor-positioning)
- [Router Edges with Multiple Source Ports](#router-edges-with-multiple-source-ports)

## Edge Structure

```yaml
edges:
  EDGE01kd6gqx5k7tvzs86y40w8etms:
    id: EDGE01kd6gqx5k7tvzs86y40w8etms
    sourceActorId: ACTR01kd6gqghj04j8765nnqyp09a3
    sourcePortId: SPRTdefault
    targetActorId: ACTR01kd6gqx5k7tvzs86y40w8etmr
    targetPortId: TPRTdefault
    label: ''
    type: borgiqEdge
```

## Edge Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | string | Yes | Unique edge identifier (30-character ULID with `EDGE` prefix) |
| `sourceActorId` | string | Yes | ID of the actor where the edge originates |
| `sourcePortId` | string | Yes | ID of the source port on the source actor |
| `targetActorId` | string | Yes | ID of the actor where the edge terminates |
| `targetPortId` | string | Yes | ID of the target port on the target actor (always `TPRTdefault`) |
| `label` | string | No | Optional label for the edge (used for router conditions) |
| `type` | string | Yes | Always `borgiqEdge` |

## Port IDs

**Source Ports (`sourcePortId`):**
- `SPRTdefault` - Default source port (most actors have only this)
- `SPRTxxxxxxx` - Custom source ports (used by RouterActor and AiRouterActor for conditional routing)

**Target Ports (`targetPortId`):**
- `TPRTdefault` - All actors have a single target port

## Generating Edge IDs

```bash
# Generate edge ID (30-character ULID)
borgiq generate id edge
# Output: EDGE01kd6gqx5k7tvzs86y40w8etms
```

## Actor Positioning

Workflows flow **top-to-bottom** in the BorgIQ canvas. Position actors accordingly:

- **Increase `position.y`** as you move downstream in the flow (each subsequent actor should have a larger `y` value)
- **Adjust `position.x`** only when you have multiple actors at the same level (e.g., parallel branches from a router)

**Recommended spacing:**

| Scenario | Spacing |
|----------|---------|
| Sequential actors | `y += 200` |
| After Interface actors | `y += 600` (renders larger in UI) |
| Parallel branches | `x += 600` or `x -= 600` |

**Example positioning:**

```yaml
# Sequential flow (top to bottom)
ACTR01trigger:
  position:
    x: 0
    'y': 0      # First actor at top

ACTR01process:
  position:
    x: 0
    'y': 200    # Below trigger

ACTR01output:
  position:
    x: 0
    'y': 400    # Below process

# Branching flow (router with two outputs)
ACTR01router:
  position:
    x: 0
    'y': 200    # Router in middle

ACTR01successHandler:
  position:
    x: -300     # Left branch
    'y': 400    # Below router

ACTR01errorHandler:
  position:
    x: 300      # Right branch
    'y': 400    # Same level as success (parallel)
```

## Router Edges with Multiple Source Ports

RouterActor and AiRouterActor can have multiple source ports, each representing a different routing condition:

```yaml
# RouterActor with multiple output routes
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
  edges:
    # Edge from Success port to success handler
    EDGE01successedge:
      id: EDGE01successedge
      sourceActorId: ACTR01router
      sourcePortId: SPRT5d5gj2s
      targetActorId: ACTR01successhandler
      targetPortId: TPRTdefault
      label: Success
      type: borgiqEdge
    # Edge from Error port to error handler
    EDGE01erroredge:
      id: EDGE01erroredge
      sourceActorId: ACTR01router
      sourcePortId: SPRTg5vsvui
      targetActorId: ACTR01errorhandler
      targetPortId: TPRTdefault
      label: Error
      type: borgiqEdge
```

**Key points:**
- Each condition in `conditions` maps to a named source port
- `SPRTdefault` with name `F` is the fallback port when no conditions match
- Edge labels should match the condition names for clarity
