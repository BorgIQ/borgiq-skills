# StreamActor Reference

Streams are append-only, ordered, cursor-addressed record logs scoped to a workspace: a collection holds the current
value of things, a stream holds what happened, in order. This file holds the stream rules (provisioning, expiry,
paging, cursors, no arrival trigger), every StreamActor action and its result, and worked canvases. Read it before
creating, appending to or consuming a stream. Code, REST, SSE tails and the React app surface are in
[stream-api.md](stream-api.md).

## Contents

- [Rules](#rules)
- [Collections vs streams](#collections-vs-streams)
- [Configuration](#configuration)
- [Actions](#actions)
- [Examples](#examples)
- [Patterns](#patterns)

## Rules

1. **Create streams before use.** `appendData` or `readStream` on a slug that was never created, or that expired, fails
   with `STREAM_NOT_FOUND` (404); nothing auto-creates a stream. Create every stream an app or a scheduled consumer
   depends on with `persistent: true` in the app's migration runner
   ([collection-migrations.md → Provisioning streams](collection-migrations.md#provisioning-streams)).
2. **A stream expires unless you say otherwise.** Each stream is in one lifecycle mode, set by `createStream` and
   changed by `editMetadata`:

   | Mode | How | Behaviour |
   |---|---|---|
   | Idle TTL (default) | `idleTtlSeconds` 60–2,592,000 (30 days); neither field gives **3,600** (1 hour) | The stream and every record in it are hard-deleted once it goes `idleTtlSeconds` without an append. Each append resets the clock |
   | Persistent | `persistent: true` | Lives until `deleteStream` (or a REST `DELETE`) |

   - `idleTtlSeconds` and `persistent: true` are mutually exclusive (rejected at validation, `path: ["persistent"]`).
     `persistent: false` on `createStream` is the same as omitting it; on `editMetadata` it converts a persistent
     stream back, applying `idleTtlSeconds` if sent and the 1-hour default otherwise. Switching to `persistent: true`
     cancels the pending expiry; switching back starts the clock from the last append.
   - The clock counts appends, not reads: reading or tailing does not keep a stream alive.
   - Before its first record a stream gets a 15-minute grace (`createdAt + max(idleTtlSeconds, 15 min)`), so a flow
     that creates it in one actor and appends later, behind an AI call or a retry, does not lose it.
   - Deletion is hard: no tombstone, no undo, no confirmation. An expired stream returns `STREAM_NOT_FOUND` from every
     surface; an open tail on it closes and the 404 arrives on the reconnect.
   - Use `persistent: true` for anything an app or consumer depends on, a TTL for scratch logs.
3. **A read returns one page, never the stream.** From actor code (StreamActor, DenoActor and PythonActor all use the
   same runtime endpoint) a `readStream` page is budgeted by the workspace's message soft maximum size
   (`softMaxMessagePayloadSizeInKiloBytes`, 64 KB by default); `maxBytes` can lower that budget, never raise it. A
   record larger than the budget fails the read with `RECORD_EXCEEDS_MESSAGE_BUDGET` rather than being truncated: raise
   the workspace limit, or read over REST (`GET …/records`, bounded only by `maxBytes` up to 1 MiB). A read is a
   snapshot and never waits; an empty stream returns an empty page with a usable cursor. Consume in a loop:
   1. Load the last `nextCursor` you persisted, or use `"start"` (everything) or `"tail"` (only new records).
   2. `readStream` with `from` set to it.
   3. Process `records`, then persist `nextCursor` (at-least-once), or persist first (at-most-once); say which in the
      actor description.
   4. If `hasMore`, repeat from 2 with the new `nextCursor`; otherwise you are caught up until the next run.

   On a canvas, step 4 is an edge back into the reader through a RouterActor on `hasMore`. Across flowruns, steps 1 and
   3 are a Collection `getItem` and a `putItem` with `options.overwrite: true` in the app's collection.
4. **Cursors are opaque tokens.** Compare them for equality, pass them back and persist them; never parse, construct
   or do arithmetic on one.
   - A cursor is bound to the stream that issued it; another stream rejects it with `INVALID_CURSOR`.
   - Every record carries its own `cursor`. Reads return `nextCursor` (where to resume) and `tailCursor` (the current
     end); appends return `firstCursor`, `lastCursor` and `tailCursor`.
   - Reads are inclusive: reading from a record's `cursor` returns that record again. Every resume cursor the platform
     hands out (a page's `nextCursor`, an SSE `id:` line, an `end` frame's `nextCursor`) points past the last record
     it delivered: pass it back unchanged and you neither skip nor repeat.
   - `from` is `"start"` (the oldest retained record), `"tail"` (only records appended after now) or a cursor. A
     cursor stays valid for the stream's life; there is no server-side consumer offset.
5. **Nothing triggers when a record arrives.** Poll instead: a ScheduledTriggerActor calls `getStreamInfo`, compares
   `tailCursor` with the persisted cursor (equal means nothing new) and reads only when it moved, which is cheap enough
   for a one-minute schedule. For records as they land, tail the stream
   ([stream-api.md → Tailing](stream-api.md#tailing-over-server-sent-events)): React apps with `useStreamTail`,
   external dashboards over the REST API.
6. **Payloads are strings.** Stringify on the way in (`Q.toJSON(...)`) and parse on the way out. Records are
   immutable, ordered by arrival at the platform and encrypted at rest; nothing can backdate, edit or delete one. A
   stream reports `storedBytes`, never a record count: keep counters in a collection.

## Collections vs streams

| Need | Use |
|---|---|
| The current value of a key, changed in place | [CollectionActor](collection-actor.md) |
| An app's entities queried by key prefix or label; counters, conditional writes, transactions | [CollectionActor](collection-actor.md) ([design](collection-design.md)) |
| A queue with claim, complete and retry | CollectionActor [queue pattern](collection-actor.md#queue-pattern): nothing marks a stream record consumed, and two readers of one cursor both get it |
| Record what happened, in order, and never lose the order (webhook events, audit trails, activity feeds, agent progress) | **StreamActor** |
| Process events incrementally and resume where the last run stopped | **StreamActor**: `readStream` from a cursor persisted in a collection |
| Know whether anything new arrived without reading it | **StreamActor**: `getStreamInfo` |
| Show records live as they arrive | **StreamActor**: tail over SSE |

Event data kept as `event:<timestamp>` collection items forces client-side ordering and paging a stream gives for free;
current state kept in a stream forces a replay to find the latest value.

## Configuration

Options live under `configuration.options`; `action` selects the action. The actor always has exactly one source port,
`SPRTdefault`, and emits the action's result as `msg.<msgVar>`. Exact schemas:
[typescript/actorSchemas/task/stream/index.md](typescript/actorSchemas/task/stream/index.md) (one module per action
alongside it, plus `limits.md` and `summary.md`).

```yaml
type: StreamActor
version: 1
name: Append Event
msgVar: append_event
sourcePorts:
  - id: SPRTdefault
configuration:
  options:
    action: appendData
    stream: order-events
    records:
      - payload: ${{ Q.toJSON(msg.trigger.body) }}
```

## Actions

`stream` takes the stream's slug or id. Error codes and limits: [stream-api.md → Errors](stream-api.md#error-codes).

| Action | Options | Emits |
|---|---|---|
| `createStream` | `slug` (required; `^[a-z0-9][a-z0-9_-]{0,63}$`, unique in the workspace); `name` (≤ 120 characters, defaults to the slug); `description` (≤ 500); `idleTtlSeconds` or `persistent`; `maxRecordSizeInKiloBytes` (largest payload, default 256) | The stream summary. A taken slug fails `STREAM_ALREADY_EXISTS` (409); the 101st stream `STREAM_LIMIT_EXCEEDED` (409) |
| `editMetadata` | `stream`; `name`; `description` (`null` clears it); `idleTtlSeconds` or `persistent`; `maxRecordSizeInKiloBytes` (future appends only) | The stream summary |
| `listStreams` | — | An array of every stream summary in the workspace (at most 100; no paging or filter) |
| `deleteStream` | `stream` | `{ streamId, slug }`. Deletes every record, with no undo |
| `appendData` | `stream`; `records`: 1–500 `{ payload: string, kind?: "text" }` (`text` is the only kind) | `{ streamId, recordsAccepted, firstCursor, lastCursor, tailCursor }`; `tailCursor` is the end after this append, for a reader that wants only what comes next |
| `readStream` | `stream`; `from` (`"start"` by default, `"tail"`, or a cursor); `maxRecords` (1–1000; a page may stop earlier on bytes); `maxBytes` (≤ 1 MiB, only narrows the budget) | One page, below |
| `getStreamInfo` | `stream` | `{ streamId, slug, name, description, tailCursor, lastRecordAt, storedBytes, persistent, idleTtlSeconds, expiresAt, createdAt }`; the tail is read live, never stale. `lastRecordAt` is `null` before the first append |

- An append stores every record or fails: there is no partial success. Each payload must fit the stream's
  `maxRecordSizeInKiloBytes`, the batch 1 MiB, and appends are limited to 50/s per stream and 200/s per workspace
  (`APPEND_RATE_EXCEEDED`, 429: retry after a short delay).
- The **stream summary** is `{ streamId, slug, name, description, persistent, idleTtlSeconds, maxRecordSizeInKiloBytes,
  storedBytes, lastActivityAt, expiresAt, createdAt, updatedAt }`. `storedBytes`, `lastActivityAt` and `expiresAt` are
  hints refreshed asynchronously; `updatedAt` moves only on `editMetadata`, never on an append.

A `readStream` page is `{ streamId, records, count, hasMore, cursor, nextCursor, tailCursor, skippedRecords,
truncatedByByteBudget? }`; each record is `{ cursor, timestamp, payload }`, with the platform's arrival time in ISO 8601.

| Field | Meaning |
|---|---|
| `cursor` | Where this page started |
| `nextCursor` | Where to resume; usable even when the page is empty, so persist it |
| `tailCursor` | The current end; `nextCursor === tailCursor` means caught up |
| `hasMore` | More records exist after this page right now |
| `skippedRecords` | Records of a newer kind this version could not read, skipped |
| `truncatedByByteBudget` | `true` when the byte budget ran out before `maxRecords` |

## Examples

Each example lists its actors in flow order with only `type`, `msgVar` and `configuration`. Wire them in the bundle's
`canvas.yaml` under `graph.edges`, one edge object per connection: `{ id, sourceActorId, sourcePortId, targetActorId,
targetPortId: TPRTdefault, type: borgiqEdge }` ([edges-and-positioning.md](edges-and-positioning.md)). Ids come from
`borgiq generate`.

### Ingest webhook events

`order_webhook` (WebhookTriggerActor with `options.webhook.respondImmediately: false`) → `append_order_event` → `ack`
(WebhookResponseActor). `order-events` is persistent, created by the migration runner. When the body is an array,
append up to 500 records in one call.

```yaml
# StreamActor, msgVar append_order_event
configuration:
  options:
    action: appendData
    stream: order-events
    records:
      - payload: ${{ Q.toJSON(msg.order_webhook.body) }}
---
# WebhookResponseActor, msgVar ack
configuration:
  options:
    statusCode: 202
    body:
      accepted: ${{ msg.append_order_event.recordsAccepted }}
      cursor: ${{ msg.append_order_event.lastCursor }}
```

### Page through a backlog

`read_page` → `process_page` (a DenoActor that parses `msg.read_page.records[i].payload`) → `more` (RouterActor), whose
`More` port loops back into `read_page`. On the loop pass `msg.read_page` is the previous page, because a message
carries every upstream result and an actor's new result replaces its old one.

```yaml
# StreamActor, msgVar read_page
configuration:
  options:
    action: readStream
    stream: order-events
    from: "${{ msg.read_page ? msg.read_page.nextCursor : 'start' }}"
    maxRecords: 200
---
# RouterActor, msgVar more
sourcePorts:
  - id: SPRTmore000
    name: More
  - id: SPRTdefault
    name: Default
configuration:
  options:
    emitType: singleRoute
    conditions:
      More: ${{ msg.read_page.hasMore === true }}
```

The loop-back edge, in `canvas.yaml`:

```yaml
- id: EDGE01...                  # borgiq generate
  sourceActorId: <more actor id>
  sourcePortId: SPRTmore000
  targetActorId: <read_page actor id>
  targetPortId: TPRTdefault
  type: borgiqEdge
```

A 10,000-record stream becomes fifty 200-record messages, never one enormous one.

### Scheduled consumer that resumes across flowruns

`every_minute` (ScheduledTriggerActor) → `load_cursor` → `tail_moved` → `changed` (RouterActor; its `Changed` port →
`read_new_records`) → `handle_records` (a DenoActor that processes records idempotently) → `save_cursor`. Most ticks
end after the cheap `getStreamInfo` probe.

```yaml
# CollectionActor, msgVar load_cursor (emits null the first time)
configuration:
  options:
    action: getItem
    collection: orders-app
    key: cursor:order-events
---
# StreamActor, msgVar tail_moved
configuration:
  options:
    action: getStreamInfo
    stream: order-events
---
# RouterActor, msgVar changed (sourcePorts: SPRTchange0 named Changed, SPRTdefault named Default)
configuration:
  options:
    emitType: singleRoute
    conditions:
      Changed: ${{ !msg.load_cursor || msg.load_cursor.value.cursor !== msg.tail_moved.tailCursor }}
---
# StreamActor, msgVar read_new_records
configuration:
  options:
    action: readStream
    stream: order-events
    from: "${{ msg.load_cursor ? msg.load_cursor.value.cursor : 'start' }}"
    maxRecords: 500
---
# CollectionActor, msgVar save_cursor: overwrite, since the cursor row exists after the first save
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

Saving `nextCursor` after handling gives at-least-once delivery, so make the handler idempotent: a create-only
`putItem` keyed by something in the payload fails a replay with `ITEM_ALREADY_EXISTS`, which means done. If a page
reports `hasMore`, loop as in the previous example or let the next tick continue from the saved cursor.

### Per-run log that expires

`create_run_log` → `agent` (AiAgentActor; its Status port, `SPRTdefault`) → `log_progress`. The stream expires two hours
after the last append, so there is nothing to clean up; a web app can tail `run-<id>` live while the run is in progress.

```yaml
# StreamActor, msgVar create_run_log. Flowrun ids have an upper-case prefix; slugs are lower-case only.
configuration:
  options:
    action: createStream
    slug: run-${{ ctx.flowrun.id.toLowerCase() }}
    name: Agent run log
    idleTtlSeconds: 7200
---
# StreamActor, msgVar log_progress
configuration:
  options:
    action: appendData
    stream: ${{ msg.create_run_log.slug }}
    records:
      - payload: ${{ Q.toJSON(msg.agent) }}
```

## Patterns

| Pattern | Shape | Notes |
|---|---|---|
| Event log | `WebhookTrigger → StreamActor appendData → WebhookResponse` | Producers only append; consumers are separate flows reading from a cursor |
| Fan-in log | Several canvases append to one persistent stream (`audit-log`) | Appends are ordered at the platform, so producers need no coordination |
| Resumable consumer | `ScheduledTrigger → getItem cursor → getStreamInfo → Router → readStream → process → putItem cursor (overwrite)` | The `getStreamInfo` gate keeps a one-minute schedule cheap |
| Chunked backlog | `readStream → process → Router (hasMore) → readStream` | The stream never enters a flowrun message whole |
| Per-run log | `createStream (idleTtlSeconds) → long-running work → appendData` | Expiry cleans up; a UI tails it while the run is active |
| Live view | An app or dashboard tails from `start` (replay, then follow) or `tail` (follow only) | Reconnect from `nextCursor` on every `end` ([stream-api.md](stream-api.md#tailing-over-server-sent-events)) |
| Provisioning | `createStream` (`persistent: true`) in the migration runner beside `createCollection` | Swallow `STREAM_ALREADY_EXISTS` ([collection-migrations.md](collection-migrations.md#provisioning-streams)) |

Other uses: `readStream` with `from: tail` reads only records appended from now on; `editMetadata` with
`persistent: true` keeps a scratch stream that turned out to matter; `deleteStream` frees the space; `listStreams`
audits what exists.
