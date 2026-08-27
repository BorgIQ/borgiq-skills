# StreamActor Reference

StreamActor is a **Task Actor** that provides YAML-based access to the [Stream API](stream-api.md): append-only, ordered, cursor-addressed record logs scoped to the workspace. It is the sibling of [CollectionActor](collection-actor.md) — a Collection holds the *current value* of things, a stream holds *what happened, in order*.

For full API documentation including every action's parameters, cursor semantics, lifecycle, the SDK helpers (Deno/Python), the REST routes, tailing over SSE, error codes and limits, see [stream-api.md](stream-api.md).

> **Streams must be created before use** — an `appendData` or `readStream` against a slug that was never created (or that has expired) fails with `STREAM_NOT_FOUND`. Nothing auto-creates a stream. Provision streams the same way you provision collections, in an idempotent migration step (see [collection-migrations.md](collection-migrations.md)).

> **A stream expires unless you say otherwise** — with neither `idleTtlSeconds` nor `persistent: true`, a stream is hard-deleted **one hour** after its last append, records and all. Set `persistent: true` for anything an app or a scheduled consumer depends on; use a TTL (60 s – 30 days) for scratch logs. The two are mutually exclusive. See [Lifecycle](stream-api.md#lifecycle-ttl-and-persistence).

> **Reads return one page, never the stream** — `readStream` emits a bounded page budgeted by the workspace message-size limit, plus a `nextCursor` to continue from. Loop the cursor on a canvas edge, or persist it in a Collection to resume across flowruns. See [Reading a Stream](stream-api.md#reading-a-stream-one-page-at-a-time).

## Table of Contents

- [Configuration Structure](#configuration-structure)
- [Actions Summary](#actions-summary)
- [Collections vs Streams](#collections-vs-streams)
- [Complete Examples](#complete-examples)
- [Use Cases](#use-cases)
- [Workflow Patterns](#workflow-patterns)
- [TypeScript Schema Hint](#typescript-schema-hint)

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: StreamActor
    version: 1
    name: Append Event
    msgVar: append_event
    description: Append the incoming event to the order-events stream
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: appendData
        stream: order-events
        records:
          - payload: ${{ Q.toJSON(msg.trigger.body) }}
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

StreamActor always has exactly one source port, `SPRTdefault`. Record payloads are **strings** — stringify structured data on the way in (`Q.toJSON(...)`) and parse it on the way out.

---

## Actions Summary

All actions are configured via the `action` field in `configuration.options`. For full parameter documentation, see [stream-api.md](stream-api.md).

| Action | Description | API Reference |
|--------|-------------|---------------|
| `createStream` | Create a stream — `slug`, optional `name`/`description`, and **either** `idleTtlSeconds` **or** `persistent: true` | [Details](stream-api.md#createstream) |
| `editMetadata` | Change name, description, record-size ceiling, or lifecycle mode | [Details](stream-api.md#editmetadata) |
| `listStreams` | List every stream in the workspace (max 100) | [Details](stream-api.md#liststreams) |
| `deleteStream` | Hard-delete the stream and every record in it | [Details](stream-api.md#deletestream) |
| `appendData` | Append 1–500 records; all stored or the call fails | [Details](stream-api.md#appenddata) |
| `readStream` | Read one bounded page from `start`, `tail`, or a cursor | [Details](stream-api.md#readstream) |
| `getStreamInfo` | The live tail cursor, last record time, stored bytes — the cheap "anything new?" probe | [Details](stream-api.md#getstreaminfo) |

**Key concepts** (see [stream-api.md](stream-api.md)):
- [Cursors](stream-api.md#cursors) — opaque tokens: compare, pass back, persist; never parse
- [Lifecycle: TTL and persistence](stream-api.md#lifecycle-ttl-and-persistence) — the 1-hour default, the 15-minute first-append grace, hard deletion
- [Reading a Stream](stream-api.md#reading-a-stream-one-page-at-a-time) — the paging loop and the message budget
- [Tailing over Server-Sent Events](stream-api.md#tailing-over-server-sent-events) — live consumers, for apps and external systems
- [Error Codes](stream-api.md#error-codes) — API error codes and meanings

---

## Collections vs Streams

| Need | Actor |
|---|---|
| Store or look up the current value of a key; update it in place | [CollectionActor](collection-actor.md) |
| Model an app's entities, query by prefix or label, counters, transactions | [CollectionActor](collection-actor.md) |
| Record events in order and never lose the order | **StreamActor** |
| Consume records incrementally and resume where you left off | **StreamActor** (`readStream` + a persisted cursor) |
| Know whether anything new arrived without reading it | **StreamActor** (`getStreamInfo`) |
| Queue with claim/complete/retry | [CollectionActor](collection-actor.md) queue pattern — a stream cannot mark a record consumed |

A stream is not a queue (nothing marks a record consumed) and not a place for current state (that is a `getItem`). Full comparison: [stream-api.md → Collections vs Streams](stream-api.md#collections-vs-streams).

---

## Complete Examples

### Event ingestion from a webhook

A WebhookTriggerActor receives order events; the StreamActor appends each one; a WebhookResponseActor acknowledges. The stream is persistent because downstream consumers depend on it.

```yaml
actors:
  ACTR01trigger:
    type: WebhookTriggerActor
    name: Order Webhook
    msgVar: order_webhook
    # ... webhook configuration
    edges:
      ACTR01append: SPRTdefault

  ACTR01append:
    type: StreamActor
    name: Append Order Event
    msgVar: append_order_event
    configuration:
      options:
        action: appendData
        stream: order-events
        records:
          - payload: ${{ Q.toJSON(msg.order_webhook.body) }}
    sourcePorts:
      - id: SPRTdefault
    edges:
      ACTR01respond: SPRTdefault

  ACTR01respond:
    type: WebhookResponseActor
    name: Ack
    msgVar: ack
    configuration:
      options:
        statusCode: 202
        body:
          accepted: ${{ msg.append_order_event.recordsAccepted }}
          cursor: ${{ msg.append_order_event.lastCursor }}
```

Batch several events in one append when the webhook body is an array — up to 500 records per call, stored in full or not at all.

### Chunked processing with a cursor loop

Read a large stream a page at a time on one canvas: the StreamActor reads from the cursor it last emitted, a RouterActor checks `hasMore`, and the "more" route loops back into the reader. The first pass reads from `start`.

```yaml
actors:
  ACTR01read:
    type: StreamActor
    name: Read Page
    msgVar: read_page
    configuration:
      options:
        action: readStream
        stream: order-events
        from: ${{ msg.read_page ? msg.read_page.nextCursor : 'start' }}
        maxRecords: 200
    sourcePorts:
      - id: SPRTdefault
    edges:
      ACTR01process: SPRTdefault

  ACTR01process:
    type: DenoActor
    name: Process Page
    msgVar: process_page
    # ... iterate msg.read_page.records, JSON.parse(record.payload)
    edges:
      ACTR01more: SPRTdefault

  ACTR01more:
    type: RouterActor
    name: More?
    msgVar: more
    configuration:
      options:
        emitType: singleRoute
        conditions:
          More: ${{ msg.read_page.hasMore === true }}
    sourcePorts:
      - id: SPRTmore0000
        name: More
        description: Another page remains
      - id: SPRTdefault
        name: Default
        description: Caught up
    edges:
      ACTR01read: SPRTmore0000
```

Every page is bounded by the workspace message budget, so a 10,000-record stream becomes fifty 200-record messages rather than one enormous one. A single record larger than the budget fails with `RECORD_EXCEEDS_MESSAGE_BUDGET` instead of being truncated.

### Scheduled consumer that resumes across flowruns

The v1 substitute for a "record arrived" trigger: a ScheduledTriggerActor fires every minute, the flow loads the cursor it persisted last time, asks `getStreamInfo` whether the tail moved, and only then reads. The cursor lives in the app's collection.

```yaml
actors:
  ACTR01schedule:
    type: ScheduledTriggerActor
    name: Every Minute
    msgVar: every_minute
    # ... schedule configuration
    edges:
      ACTR01loadcursor: SPRTdefault

  ACTR01loadcursor:
    type: CollectionActor
    name: Load Cursor
    msgVar: load_cursor
    configuration:
      options:
        action: getItem
        collection: orders-app
        key: cursor:order-events
    sourcePorts:
      - id: SPRTdefault
    edges:
      ACTR01info: SPRTdefault

  ACTR01info:
    type: StreamActor
    name: Tail Moved?
    msgVar: tail_moved
    configuration:
      options:
        action: getStreamInfo
        stream: order-events
    sourcePorts:
      - id: SPRTdefault
    edges:
      ACTR01changed: SPRTdefault

  ACTR01changed:
    type: RouterActor
    name: Changed?
    msgVar: changed
    configuration:
      options:
        emitType: singleRoute
        conditions:
          Changed: ${{ !msg.load_cursor || msg.load_cursor.value.cursor !== msg.tail_moved.tailCursor }}
    sourcePorts:
      - id: SPRTchanged0
        name: Changed
        description: The tail moved since the persisted cursor
      - id: SPRTdefault
        name: Default
        description: Nothing new
    edges:
      ACTR01readnew: SPRTchanged0

  ACTR01readnew:
    type: StreamActor
    name: Read New Records
    msgVar: read_new_records
    configuration:
      options:
        action: readStream
        stream: order-events
        from: ${{ msg.load_cursor ? msg.load_cursor.value.cursor : 'start' }}
        maxRecords: 500
    sourcePorts:
      - id: SPRTdefault
    edges:
      ACTR01handle: SPRTdefault

  ACTR01handle:
    type: DenoActor
    name: Handle Records
    msgVar: handle_records
    # ... process msg.read_new_records.records idempotently
    edges:
      ACTR01savecursor: SPRTdefault

  ACTR01savecursor:
    type: CollectionActor
    name: Save Cursor
    msgVar: save_cursor
    configuration:
      options:
        action: putItem
        collection: orders-app
        key: cursor:order-events
        value:
          cursor: ${{ msg.read_new_records.nextCursor }}
        options:
          overwrite: true
```

Saving `nextCursor` *after* handling gives at-least-once delivery; make the handler idempotent. If a page reports `hasMore`, either loop as in the previous example or let the next tick pick it up — the cursor is already saved.

### Short-lived activity log for an AI agent run

Create a stream per run with a two-hour TTL, append progress from the agent's Status port, and let it expire on its own. Nothing to clean up.

```yaml
actors:
  ACTR01create:
    type: StreamActor
    name: Create Run Log
    msgVar: create_run_log
    configuration:
      options:
        action: createStream
        slug: run-${{ ctx.flowrun.id }}
        name: Agent run log
        idleTtlSeconds: 7200
    sourcePorts:
      - id: SPRTdefault
    edges:
      ACTR01agent: SPRTdefault

  ACTR01agent:
    type: AiAgentActor
    name: Agent
    msgVar: agent
    # ... agent configuration; Status port feeds the append below
    sourcePorts:
      - id: SPRTdone000
      - id: SPRTdefault
    edges:
      ACTR01log: SPRTdefault

  ACTR01log:
    type: StreamActor
    name: Log Progress
    msgVar: log_progress
    configuration:
      options:
        action: appendData
        stream: ${{ msg.create_run_log.slug }}
        records:
          - payload: ${{ Q.toJSON(msg.agent) }}
```

A web app can tail `run-<id>` live over SSE while the run is in progress — see [stream-api.md → Tailing](stream-api.md#tailing-over-server-sent-events).

---

## Use Cases

| Scenario | Action |
|----------|--------|
| Record every event a webhook delivers, in order | `appendData` |
| Ingest a batch of events in one call | `appendData` with up to 500 `records` |
| Process a backlog a page at a time | `readStream` looping `nextCursor` while `hasMore` |
| Resume consumption where the last flowrun stopped | `readStream` from a cursor persisted in a Collection |
| Only react when something new arrived | `getStreamInfo` — compare `tailCursor` with the persisted cursor |
| Read only records appended from now on | `readStream` with `from: tail` |
| Provision an app's stream at deploy time | `createStream` with `persistent: true` (idempotent — catch `STREAM_ALREADY_EXISTS`) |
| Per-run scratch log that cleans itself up | `createStream` with a short `idleTtlSeconds` |
| Keep a stream that turned out to matter | `editMetadata` with `persistent: true` |
| Free the space when done | `deleteStream` |
| Audit which streams exist | `listStreams` |
| Live progress in a UI | tail over SSE from the app or a dashboard ([stream-api.md](stream-api.md#tailing-over-server-sent-events)) |

---

## Workflow Patterns

### Pattern 1: Event log

```
WebhookTrigger → StreamActor (appendData) → WebhookResponse
```

Producers only append. Consumers are separate flows that read from a cursor. Because ordering happens at the platform, several producers can share one stream with no coordination.

### Pattern 2: Resumable consumer

```
ScheduledTrigger → Collection getItem (cursor) → StreamActor getStreamInfo → Router (moved?)
  → StreamActor readStream → process → Collection putItem (nextCursor)
```

The `getStreamInfo` gate is what makes a one-minute schedule affordable: most ticks end after one cheap probe. Persist the cursor after processing for at-least-once, before for at-most-once — and say which in the actor description.

### Pattern 3: Chunked backlog

```
StreamActor readStream → process → Router (hasMore?) ─┐
        ▲                                             │
        └─────────────────────────────────────────────┘
```

Bounded pages looped on a canvas edge. The stream never enters a flowrun message whole.

### Pattern 4: Per-run log with TTL

```
StreamActor createStream (idleTtlSeconds) → long-running work → StreamActor appendData (Status port)
```

Slug from `ctx.flowrun.id`, expiry does the cleanup, a UI tails it live while the run is active.

### Pattern 5: Provisioning

Add a `createStream` (`persistent: true`) step to the app's migration runner, alongside its `createCollection`, and swallow `STREAM_ALREADY_EXISTS` on re-runs — see [collection-migrations.md](collection-migrations.md). A stream-backed app without a provisioning step works in the dev workspace where the stream was hand-created and then 404s in production.

---

## TypeScript Schema Hint

The Zod schemas for every action live in [typescript/actor-schemas-task-stream.md](typescript/actor-schemas-task-stream.md):

- `StreamActorCreateStreamOptionsSchema` / `StreamActorCreateStreamResultSchema`
- `StreamActorEditMetadataOptionsSchema` / `StreamActorEditMetadataResultSchema`
- `StreamActorAppendDataOptionsSchema` / `StreamActorAppendDataResultSchema`
- `StreamActorReadStreamOptionsSchema` / `StreamActorReadStreamResultSchema`
- `StreamActorDeleteStreamOptionsSchema` / `StreamActorDeleteStreamResultSchema`
- `StreamActorListStreamsOptionsSchema` / `StreamActorListStreamsResultSchema`
- `StreamActorGetStreamInfoOptionsSchema` / `StreamActorGetStreamInfoResultSchema`
- `StreamActorOptionsSchema` — the discriminated union on `action`
