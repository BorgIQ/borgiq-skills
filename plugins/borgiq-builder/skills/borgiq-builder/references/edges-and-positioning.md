# Edges, Ports and Positions

How actors are wired: the edge shape, the source ports each actor type has, and where edges and positions live. Read it
before wiring actors or adding ports.

## Where edges and positions live

- **In a bundle**, edges live only in `canvas.yaml` `graph.edges` and positions only in `canvas.yaml` `graph.nodes`;
  `actor.yaml` never carries `edges` or `position` ([canvas-bundles.md](cli/canvas-bundles.md)).
- **In an exported document or a CanvasActor payload** (the no-bundle fallback), each source actor carries its own
  `edges` map, keyed by edge ID, and its own `position`.
- Mint edge IDs with `borgiq generate id edge` (`EDGE` + a 26-character ULID) and custom port IDs with
  `borgiq generate id sourceport`.

## Edge shape

```yaml
# canvas.yaml graph.edges entry (a document's edges map has the same fields, keyed by id)
- id: EDGE01kd6gqx5k7tvzs86y40w8etms
  sourceActorId: ACTR01kd6gqghj04j8765nnqyp09a3
  sourcePortId: SPRTdefault
  targetActorId: ACTR01kd6gqx5k7tvzs86y40w8etmr
  targetPortId: TPRTdefault
  type: borgiqEdge
```

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Unique edge ID |
| `sourceActorId` | yes | Actor the edge leaves |
| `sourcePortId` | yes | Must match an `id` in the source actor's `sourcePorts` |
| `targetActorId` | yes | Actor the edge enters |
| `targetPortId` | yes | Always `TPRTdefault`: every actor has one target port |
| `label` | no | Display only. Routing ignores it: a router matches its `conditions` keys to source port `name`s |
| `type` | yes | Always `borgiqEdge` |

## Port IDs

| Actor | Source ports |
|---|---|
| Most actors, including MessageProcessorActor | `SPRTdefault` only |
| RouterActor, AiRouterActor | one custom port per route (`SPRT` + 7 lowercase letters or digits) plus `SPRTdefault` as the fallback |
| AiAgentActor, AgentHarnessActor | `SPRTdone000` (Done) and `SPRTdefault` (Status) |
| InterfaceActor | `SPRTevent00` (Event) and `SPRTdefault` (Meta) |
| AppTriggerActor, ReactAppTriggerActor, CommentActor | none (`sourcePorts: []`) |

A router's port `name`s are its `conditions` keys, and the default port takes no condition
([router-actor.md](router-actor.md)). Several downstream actors on one port run in parallel
([fan-out](message-processor-actor.md#fork-actions)).

## Positions and auto-layout

- Let the CLI lay out the canvas: `borgiq bundle push <dir> --auto-layout` after adding, removing or rewiring actors,
  or `borgiq canvases layout <canvas>`. It flows top to bottom.
- Placing actors by hand: increase `y` downstream (`y += 200` per step, `y += 600` after an InterfaceActor, which
  renders larger), and change `x` only to separate parallel branches (±300 to ±600 from the parent, e.g. `x: -300`
  and `x: 300` under a router).
