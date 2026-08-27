# Stream API Reference

The Stream API provides **append-only, ordered, cursor-addressed record logs** scoped to a workspace. Where a [Collection](collection-api.md) answers "what is the current value of X", a stream answers "what happened, in order, and what have I already seen". It is accessed via:

- **StreamActor** — YAML configuration with `action` field. See [stream-actor.md](stream-actor.md).
- **DenoActor** — `biqApi('/streams')` from `@borgiq/actors`. See [deno-actor.md](deno-actor.md).
- **PythonActor** — `biq_api('/streams')` from `borgiq`. See [python-actor.md](python-actor.md).
- **REST API** — `/orgs/:org/workspaces/:workspace/streams` with a Personal Access Token, for external systems, scripts, and the CLI. See [Public REST API](#public-rest-api).

From actor code, every operation goes through a single `POST /streams` runtime endpoint with an `action` field in the request body, exactly like `POST /collections`. Authentication and tenant scoping are handled automatically.

## Table of Contents

- [Overview](#overview)
- [Collections vs Streams](#collections-vs-streams)
- [Lifecycle: TTL and persistence](#lifecycle-ttl-and-persistence)
- [Cursors](#cursors)
- [Stream Management Actions](#stream-management-actions)
- [Record Operations](#record-operations)
- [Inspection](#inspection)
- [Reading a Stream: one page at a time](#reading-a-stream-one-page-at-a-time)
- [SDK Interface (DenoActor / PythonActor)](#sdk-interface-denoactor--pythonactor)
- [Tailing from actor code](#tailing-from-actor-code)
- [Public REST API](#public-rest-api)
- [Tailing over Server-Sent Events](#tailing-over-server-sent-events)
- [Response Format Reference](#response-format-reference)
- [Error Codes](#error-codes)
- [Input Validation Constraints](#input-validation-constraints)
- [Patterns](#patterns)

## Overview

A stream is a named, workspace-scoped log. Records are appended at the end, each one gets an arrival timestamp and an opaque **cursor**, and readers walk the log forward from a cursor they hold. Nothing is ever updated in place.

- **Records are opaque text.** A record is `{ kind: "text", payload: string }`; `text` is the only kind in this version. Put JSON in the payload if you want structure — the platform does not inspect it.
- **Records are immutable and ordered.** Order is arrival order at the platform. Clients cannot backdate, edit, or delete individual records.
- **Every read is a snapshot.** A read returns what is in the stream *now* and never waits for more. An empty stream returns an empty page with a usable cursor. Following a stream as records land is what [tailing](#tailing-over-server-sent-events) is for.
- **Appends are all-or-nothing.** A batch of up to 500 records is either fully stored or the call fails. There is no partial success.
- **Payloads are encrypted at rest** by the platform, and no actor, app, or client ever holds a storage credential — every surface goes through BorgIQ endpoints.
- **There is no record count.** A stream reports `storedBytes` (approximate, refreshed periodically), not a count. Keep your own counters in a Collection if you need them.
- **Streams expire unless told otherwise.** A stream that is neither given an idle TTL nor marked `persistent` is deleted **one hour** after its last append. See [Lifecycle](#lifecycle-ttl-and-persistence).

**Stream Management:** Create, edit metadata, list, delete streams

**Record Operations:** Append a batch; read one page from a cursor

**Inspection:** `getStreamInfo` — the live tail cursor, last record time, stored bytes

**Tailing:** Server-sent events from a cursor, for live consumers

## Collections vs Streams

| You need… | Use |
|---|---|
| The current value of a key (`getItem`), or to change it in place | **Collection** |
| To model an app's entities and query them by key prefix or label | **Collection** ([single-collection design](collection-api.md#single-collection-design)) |
| Atomic counters, conditional writes, transactions | **Collection** |
| To record that something happened, in order, and never lose the order | **Stream** |
| To process events incrementally and **resume where you left off** across flowruns | **Stream** (persist the cursor in a Collection or DataStore) |
| An activity feed, an audit trail, event ingestion from webhooks, agent/flow progress | **Stream** |
| A queue with claim/complete/retry semantics | **Collection** ([queue pattern](collection-api.md#queue-pattern-using-collections)) — a stream cannot mark a record consumed |
| To show a live view of records as they arrive | **Stream** (tail over SSE) |

Modelling event-shaped data as `event:<ts>` items in a Collection forces client-side ordering and pagination that a stream gives you for free; modelling current state as a stream forces a replay to find the latest value. Use each for what it is.

## Lifecycle: TTL and persistence

Every stream is in exactly one of two lifecycle modes, chosen at `createStream` and changeable with `editMetadata`:

| Mode | How | Behaviour |
|---|---|---|
| **Idle TTL** (default) | `idleTtlSeconds` between `60` and `2592000` (30 days); omitting both fields gives **3600** (1 hour) | The stream — and every record in it — is hard-deleted once it has gone `idleTtlSeconds` without an append. Each append resets the clock. |
| **Persistent** | `persistent: true` | Lives until `deleteStream` or a `DELETE` call. |

`idleTtlSeconds` and `persistent: true` are **mutually exclusive**; sending both is rejected by validation with `path: ["persistent"]`.

Details worth designing around:

- **The clock measures appends, not reads.** Reading or tailing a stream does not keep it alive.
- **A never-appended stream gets a 15-minute grace.** Before the first record, the deadline is `createdAt + max(idleTtlSeconds, 15 min)`, so a flow that creates a stream in one actor and appends in a later one (behind an AI call or a retry) does not lose the stream in between. After the first append the idle TTL applies untouched.
- **`expiresAt` and `lastActivityAt` in list responses are hints**, refreshed asynchronously — treat them as approximate. `getStreamInfo` reads the tail live from storage and is the truth.
- **Deletion is hard.** No tombstone, no undo, no confirmation. An expired stream returns `STREAM_NOT_FOUND` (404) from every surface, including an open tail.
- **Streams must be created before use.** An append to a slug that was never created — or that has expired — fails with `STREAM_NOT_FOUND`; nothing auto-creates. Provision streams the way you provision collections (see [collection-migrations.md](collection-migrations.md)), and use `persistent: true` for anything an app depends on.

## Cursors

A cursor is an **opaque string** that names a position in one specific stream. It is the only handle you get and the only one you need.

- Treat it as a token: compare for equality, pass it back, persist it. **Never parse it, never do arithmetic on it, never construct one.**
- A cursor is bound to the stream that issued it. Presenting it to another stream fails with `INVALID_CURSOR`.
- Every record carries its own `cursor`. Every read returns `nextCursor` (where to resume) and `tailCursor` (the current end). Every append returns `firstCursor`, `lastCursor`, and `tailCursor`.
- The three ways to start a read are `"start"` (the oldest retained record), `"tail"` (only records appended after now), or a cursor from a previous response.
- A cursor stays valid across the stream's whole life. Persist `nextCursor` in a Collection or DataStore to resume across flowruns; there is no server-side "consumer offset".

## Stream Management Actions

### createStream

Creates a new stream in the workspace. Fails with `STREAM_ALREADY_EXISTS` (409) if the slug is taken and `STREAM_LIMIT_EXCEEDED` (409) at 100 streams per workspace.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"createStream"` | Yes | Must be `createStream` |
| `slug` | string | Yes | Unique within the workspace. Must match `^[a-z0-9][a-z0-9_-]{0,63}$` |
| `name` | string | No | Display name, max 120 chars. Defaults to the slug |
| `description` | string | No | Max 500 chars |
| `idleTtlSeconds` | integer | No | Delete after this long without an append, `60`–`2592000`. Mutually exclusive with `persistent`. Omit both for the 1-hour default |
| `persistent` | `true` | No | Keep the stream until explicitly deleted. Mutually exclusive with `idleTtlSeconds` |
| `maxRecordSizeInKiloBytes` | integer | No | Largest single payload this stream accepts. Defaults to `256` |

**Example:**
```yaml
configuration:
  options:
    action: createStream
    slug: order-events
    name: Order Events
    description: Every state change on an order, in order
    persistent: true
```

**Emitted Message:**
```json
{
  "streamId": "STRM01...",
  "slug": "order-events",
  "name": "Order Events",
  "description": "Every state change on an order, in order",
  "persistent": true,
  "idleTtlSeconds": null,
  "maxRecordSizeInKiloBytes": 256,
  "storedBytes": 0,
  "lastActivityAt": null,
  "expiresAt": null,
  "createdAt": "2026-08-27T10:00:00.000Z",
  "updatedAt": null
}
```

---

### editMetadata

Changes a stream's name, description, record-size ceiling, or lifecycle mode. Switching from a TTL to `persistent: true` cancels the pending expiry; switching back starts the clock from the last append.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"editMetadata"` | Yes | Must be `editMetadata` |
| `stream` | string | Yes | Slug or id of the stream |
| `name` | string | No | New display name, max 120 chars |
| `description` | string | No | New description, max 500 chars |
| `idleTtlSeconds` | integer | No | New idle TTL, `60`–`2592000`. Mutually exclusive with `persistent` |
| `persistent` | `true` | No | Convert to persistent. Mutually exclusive with `idleTtlSeconds` |
| `maxRecordSizeInKiloBytes` | integer | No | New per-record ceiling |

**Example:**
```yaml
configuration:
  options:
    action: editMetadata
    stream: order-events
    idleTtlSeconds: 86400
```

**Emitted Message:** the same stream summary shape as `createStream`, with `idleTtlSeconds: 86400`, `persistent: false`, and a fresh `expiresAt`.

---

### listStreams

Lists every stream in the workspace (at most 100). No pagination and no filter — filter client-side.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"listStreams"` | Yes | Must be `listStreams` |

**Emitted Message:** an array of stream summaries.
```json
[
  {
    "streamId": "STRM01...",
    "slug": "order-events",
    "name": "Order Events",
    "description": null,
    "persistent": false,
    "idleTtlSeconds": 3600,
    "maxRecordSizeInKiloBytes": 256,
    "storedBytes": 18342,
    "lastActivityAt": "2026-08-27T10:41:12.000Z",
    "expiresAt": "2026-08-27T11:41:12.000Z",
    "createdAt": "2026-08-27T10:00:00.000Z",
    "updatedAt": null
  }
]
```

`storedBytes`, `lastActivityAt`, and `expiresAt` are asynchronously refreshed hints. `updatedAt` moves only on `editMetadata`, never on an append.

---

### deleteStream

Hard-deletes the stream and every record in it. No confirmation, no undo.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"deleteStream"` | Yes | Must be `deleteStream` |
| `stream` | string | Yes | Slug or id of the stream |

**Emitted Message:**
```json
{ "streamId": "STRM01...", "slug": "order-events" }
```

## Record Operations

### appendData

Appends a batch of records. Either every record is durably stored or the call fails — there is no partial result. Each append resets the idle-TTL clock.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"appendData"` | Yes | Must be `appendData` |
| `stream` | string | Yes | Slug or id of the stream |
| `records` | array | Yes | 1–500 records. Each is `{ payload: string, kind?: "text" }`; `kind` defaults to `text` and is the only supported kind |

Limits: each `payload` must be within the stream's `maxRecordSizeInKiloBytes` (`RECORD_TOO_LARGE`); the whole batch must be under 1 MiB (`BATCH_BYTES_EXCEEDED`); at most 50 appends/second per stream and 200/second per workspace (`APPEND_RATE_EXCEEDED`, 429 — retry after a short delay).

**Example:**
```yaml
configuration:
  options:
    action: appendData
    stream: order-events
    records:
      - payload: ${{ Q.toJSON(msg.trigger.body) }}
```

**Emitted Message:**
```json
{
  "streamId": "STRM01...",
  "recordsAccepted": 1,
  "firstCursor": "s2:...",
  "lastCursor": "s2:...",
  "tailCursor": "s2:..."
}
```

`tailCursor` is the end of the stream *after* this append — hand it to a reader that only wants what comes next.

---

### readStream

Returns **one bounded page** of records from a position. A read is a snapshot: it never waits for records to arrive. See [Reading a Stream](#reading-a-stream-one-page-at-a-time) for the paging loop.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"readStream"` | Yes | Must be `readStream` |
| `stream` | string | Yes | Slug or id of the stream |
| `from` | string | No | `"start"`, `"tail"`, or a cursor from a previous response. Defaults to `"start"` |
| `maxRecords` | integer | No | 1–1000. The page may stop earlier when the byte budget runs out |
| `maxBytes` | integer | No | Byte budget for the page (runtime endpoint and REST only; the StreamActor budgets by the workspace message-size limit instead) |

**Example:**
```yaml
configuration:
  options:
    action: readStream
    stream: order-events
    from: ${{ msg.load_cursor.value ?? 'start' }}
    maxRecords: 200
```

**Emitted Message:**
```json
{
  "streamId": "STRM01...",
  "records": [
    { "cursor": "s2:...", "timestamp": "2026-08-27T10:41:12.317Z", "payload": "{\"orderId\":\"O-1\",\"state\":\"paid\"}" },
    { "cursor": "s2:...", "timestamp": "2026-08-27T10:41:13.002Z", "payload": "{\"orderId\":\"O-1\",\"state\":\"shipped\"}" }
  ],
  "count": 2,
  "hasMore": false,
  "cursor": "s2:...",
  "nextCursor": "s2:...",
  "tailCursor": "s2:...",
  "skippedRecords": 0
}
```

| Field | Meaning |
|---|---|
| `cursor` | Where this page started |
| `nextCursor` | Where to resume. **Usable even when the page is empty** — persist it |
| `tailCursor` | The current end of the stream. `nextCursor === tailCursor` means you are caught up |
| `hasMore` | More records exist after this page *right now* |
| `skippedRecords` | Records this version could not interpret (a newer record kind) and skipped |
| `truncatedByByteBudget` | Present and `true` when the page stopped short of `maxRecords` because the byte budget ran out first |

## Inspection

### getStreamInfo

The cheap "is there anything new?" probe. It reads the tail **live** from storage rather than from the cached summary, so it is never stale — which is what makes a polling consumer viable without reading records.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"getStreamInfo"` | Yes | Must be `getStreamInfo` |
| `stream` | string | Yes | Slug or id of the stream |

**Emitted Message:**
```json
{
  "streamId": "STRM01...",
  "slug": "order-events",
  "name": "Order Events",
  "description": null,
  "tailCursor": "s2:...",
  "lastRecordAt": "2026-08-27T10:41:13.002Z",
  "storedBytes": 18342,
  "persistent": false,
  "idleTtlSeconds": 3600,
  "expiresAt": "2026-08-27T11:41:13.002Z",
  "createdAt": "2026-08-27T10:00:00.000Z"
}
```

`lastRecordAt` is `null` for a stream that has never been appended to. Compare `tailCursor` with the cursor you last consumed: equal means nothing new.

## Reading a Stream: one page at a time

`readStream` deliberately emits **a page, never the stream**. When called from the StreamActor, the page is budgeted against the workspace's message-size limit (`maxMessageAndSignalPayloadSizeInKiloBytes`, 64 KB by default), so a 10,000-record stream never becomes a 10,000-record flowrun message. A single record larger than that budget fails the read with `RECORD_EXCEEDS_MESSAGE_BUDGET` rather than being silently truncated — raise the workspace limit, or read from DenoActor/PythonActor code where the budget is `maxBytes` (up to 1 MiB) instead.

The consumer loop is always the same:

1. Load the last `nextCursor` you persisted, or use `"start"` (everything) / `"tail"` (only new records).
2. `readStream` with `from` set to it.
3. Process `records`; persist `nextCursor` **after** processing succeeds (at-least-once) or before (at-most-once) — your choice, made explicit.
4. If `hasMore`, go to 2 with the new `nextCursor`. Otherwise you are caught up until the next run.

On a canvas, step 4 is an edge from the StreamActor back into itself (or into a RouterActor that checks `hasMore`); across flowruns, step 1 and 3 are a Collection `getItem`/`putItem` or a DataStore `get`/`set`. See [Patterns](#patterns).

## SDK Interface (DenoActor / PythonActor)

All actions use the same request body as the actor options above, sent to `POST /streams`. The response is the standard envelope `{ ok: boolean, value: T, error?: { code, message } }`.

### API Helper Pattern (Deno)

```typescript
import { biqApi } from "@borgiq/actors";

async function streamsApi<T = unknown>(body: Record<string, unknown>): Promise<T> {
  const res = await biqApi("/streams", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const json = (await res.json()) as { ok: boolean; value: T; error?: { code: string; message: string } };
  if (!json.ok) {
    const err = new Error(json.error?.message || "Stream action failed");
    (err as any).code = json.error?.code;
    throw err;
  }
  return json.value;
}
```

**Quick reference:**

```typescript
// createStream — persistent, so an app can depend on it
await streamsApi({ action: "createStream", slug: "order-events", persistent: true });

// appendData — a batch is stored in full or not at all
const ack = await streamsApi<{ tailCursor: string }>({
  action: "appendData",
  stream: "order-events",
  records: [{ payload: JSON.stringify({ orderId: "O-1", state: "paid" }) }],
});

// readStream — walk forward from a persisted cursor
let from = (await loadCursor()) ?? "start";
while (true) {
  const page = await streamsApi<{
    records: { cursor: string; timestamp: string; payload: string }[];
    nextCursor: string; hasMore: boolean;
  }>({ action: "readStream", stream: "order-events", from, maxRecords: 500, maxBytes: 512 * 1024 });
  for (const record of page.records) await handle(JSON.parse(record.payload));
  await saveCursor(page.nextCursor);
  if (!page.hasMore) break;
  from = page.nextCursor;
}

// getStreamInfo — did anything land since last time?
const info = await streamsApi<{ tailCursor: string }>({ action: "getStreamInfo", stream: "order-events" });
if (info.tailCursor === (await loadCursor())) return; // nothing new
```

`loadCursor`/`saveCursor` are yours — typically a Collection item keyed `cursor:order-events` (see [collection-api.md](collection-api.md)).

### Python

```python
from borgiq import Request, Response, biq_api

def receive(req: Request) -> Response:
    # appendData
    biq_api('/streams', method='POST', json={
        'action': 'appendData', 'stream': 'order-events',
        'records': [{'payload': '{"orderId": "O-1", "state": "paid"}'}],
    })

    # readStream — one page from a persisted cursor
    page = biq_api('/streams', method='POST', json={
        'action': 'readStream', 'stream': 'order-events',
        'from': req.inputs.get('cursor') or 'start', 'maxRecords': 500,
    }).json()['value']

    # getStreamInfo — the live tail
    info = biq_api('/streams', method='POST', json={
        'action': 'getStreamInfo', 'stream': 'order-events',
    }).json()['value']

    return Response(results={'records': page['records'], 'nextCursor': page['nextCursor'], 'tail': info['tailCursor']})
```

## Tailing from actor code

Actor code can hold a tail open instead of polling — useful when an actor wants records **as they land** for a bounded window. The runtime endpoint is:

```
GET /streams/:streamIdOrSlug/tail?from=<start|tail|cursor>&maxSeconds=<1..120>&maxRecords=<1..10000>
```

- `maxSeconds` defaults to **30** and is capped at **120**. `maxRecords` closes the tail after that many records. An actor pays for the whole time it waits and has its own invocation timeout, so state the budget you mean.
- The wire format is identical to the public tail below. The connection closes with `event: end` carrying `nextCursor` when either bound is reached, or when the idle bound (half of `maxSeconds`) passes with no record.
- Do not tail from a ScheduledTrigger loop when `getStreamInfo` + `readStream` would do; a tail holds one of the workspace's 20 concurrent tail slots for its whole duration.

```typescript
const res = await biqApi("/streams/order-events/tail", { queryParams: { from: cursor, maxSeconds: "60", maxRecords: "100" } });
const text = await res.text(); // the whole SSE transcript, since the tail closes itself at the bound
for (const frame of text.split("\n\n")) {
  const data = frame.split("\n").find((l) => l.startsWith("data: "))?.slice(6);
  if (frame.includes("event: record") && data) handle(JSON.parse(data));
  if (frame.includes("event: end") && data) cursor = JSON.parse(data).nextCursor ?? cursor;
}
```

## Public REST API

External systems, scripts, and the CLI reach streams over the workspace REST API with a Personal Access Token. Token creation and scopes: [api-tokens.md](api-tokens.md).

### URL pattern

```
/orgs/:orgSlugOrId/workspaces/:workspaceSlugOrId/streams
```

```http
POST /orgs/my-org/workspaces/my-workspace/streams/order-events/records
Authorization: Bearer biq_abc123...
Content-Type: application/json

{ "records": [ { "payload": "{\"orderId\":\"O-1\",\"state\":\"paid\"}" } ] }
```

### Routes and scopes

Scopes are **per verb**: a workspace viewer can read and tail, and cannot create, append, edit, or delete.

| Method | Path | Body / query | Scope | Returns |
|---|---|---|---|---|
| `GET` | `/streams` | — | `stream:read` | array of stream summaries |
| `POST` | `/streams` | `{ slug, name?, description?, idleTtlSeconds? \| persistent?, maxRecordSizeInKiloBytes? }` | `stream:write` | `201` + stream summary |
| `PUT` | `/streams/:streamIdOrSlug` | `{ name?, description?, idleTtlSeconds? \| persistent?, maxRecordSizeInKiloBytes? }` | `stream:write` | stream summary |
| `DELETE` | `/streams/:streamIdOrSlug` | — | `stream:delete` | `{ streamId, slug }` |
| `GET` | `/streams/:streamIdOrSlug/records` | `?from=&maxRecords=&maxBytes=` | `stream:read` | one page (the `readStream` shape) |
| `POST` | `/streams/:streamIdOrSlug/records` | `{ records: [{ payload, kind? }] }` | `stream:write` | the `appendData` shape |
| `GET` | `/streams/:streamIdOrSlug/tail` | `?from=` | `stream:read` | `text/event-stream` — see below |

Every JSON response is the `{ ok, value }` envelope; errors are `{ ok: false, error: { code, message } }` with the HTTP status from the [Error Codes](#error-codes) table. There is no `GET /streams/:id` — the list already carries every summary field, and the live tail comes from `getStreamInfo` via the runtime endpoint or from the paged read's `tailCursor`.

Auth failures use HTTP status codes: `401` for a missing or invalid token, `403` for a token without the required scope or for a workspace the token's user is not a member of.

## Tailing over Server-Sent Events

`GET …/streams/:streamIdOrSlug/tail` holds the connection open and pushes records as they arrive. It is the only stream surface that waits, and it is capped for exactly that reason.

### Request

```http
GET /orgs/my-org/workspaces/my-workspace/streams/order-events/tail?from=start
Authorization: Bearer biq_abc123...
Accept: text/event-stream
```

- `from` is `start`, `tail`, or a cursor. **Omitting it means `tail`** — only records appended after the connection opens.
- A `Last-Event-ID` header **overrides `from`**. Browser `EventSource` sets it automatically on reconnect to the last `id` it received, which is why resume is free.

### Frames

Every record is one SSE event whose `id` **is** its cursor:

```
id: s2:...
event: record
data: {"cursor":"s2:...","timestamp":"2026-08-27T10:41:12.317Z","payload":"{\"orderId\":\"O-1\",\"state\":\"paid\"}"}

: heartbeat

event: end
data: {"nextCursor":"s2:...","records":2}
```

| Frame | When | What to do |
|---|---|---|
| `event: record` | a record landed | handle `data`; remember `data.cursor` |
| `: heartbeat` (comment) | every 15 s while quiet | nothing — it keeps proxies from reaping the connection. Treat 45 s of silence as a dead connection |
| `event: end` | the server closed the session cleanly | **reconnect with `from = data.nextCursor`**. `nextCursor` is absent when the session emitted no records — reuse the `from` you sent |
| `event: error` | a failure after the headers were sent | reconnect with backoff from the last cursor you received |

**A clean `end` is the normal path, not a failure.** The public tail closes after **60 s without a record** or **300 s in total**; a consumer that stays subscribed simply reconnects from `nextCursor` and misses nothing. Records are never duplicated across a correct resume because the cursor names an exact position.

### Errors before the stream starts

| Status | Meaning |
|---|---|
| `404 STREAM_NOT_FOUND` | the stream does not exist — or **has idle-expired** while you were tailing it. This is lifecycle, not a transient error: stop reconnecting |
| `429 TAIL_LIMIT_EXCEEDED` + `Retry-After: 30` | the workspace already has **20** open tails. Wait out `Retry-After`, then retry |
| `401` / `403` | token missing, invalid, or without `stream:read` |

## Response Format Reference

| Action / route | `value` |
|---|---|
| `createStream`, `editMetadata`, `POST`/`PUT /streams` | stream summary: `{ streamId, slug, name, description, persistent, idleTtlSeconds, maxRecordSizeInKiloBytes, storedBytes, lastActivityAt, expiresAt, createdAt, updatedAt }` |
| `listStreams`, `GET /streams` | array of stream summaries |
| `deleteStream`, `DELETE /streams/:ref` | `{ streamId, slug }` |
| `appendData`, `POST …/records` | `{ streamId, recordsAccepted, firstCursor, lastCursor, tailCursor }` |
| `readStream`, `GET …/records` | `{ streamId, records[], count, hasMore, cursor, nextCursor, tailCursor, skippedRecords, truncatedByByteBudget? }` |
| `getStreamInfo` | `{ streamId, slug, name, description, tailCursor, lastRecordAt, storedBytes, persistent, idleTtlSeconds, expiresAt, createdAt }` |

Each `records[]` entry is `{ cursor, timestamp, payload }` — `timestamp` is the platform's arrival time in ISO 8601, `payload` is the string you appended.

## Error Codes

| Code | HTTP | Meaning |
|---|---|---|
| `INVALID_ACTION` | 400 | Unknown `action` |
| `INVALID_STREAM_SLUG` | 400 | Slug does not match `^[a-z0-9][a-z0-9_-]{0,63}$` |
| `INVALID_IDLE_TTL` | 400 | `idleTtlSeconds` outside 60–2592000, or combined with `persistent` |
| `INVALID_RECORD_SIZE` | 400 | `maxRecordSizeInKiloBytes` below 1 or above the platform ceiling (just under 1 MiB) |
| `EMPTY_APPEND` | 400 | `records` is empty |
| `INVALID_RECORD_KIND` | 400 | `kind` other than `text` |
| `INVALID_CURSOR` | 400 | Cursor is malformed, or belongs to a different stream |
| `RECORD_TOO_LARGE` | 400 | One payload exceeds the stream's `maxRecordSizeInKiloBytes` |
| `BATCH_LIMIT_EXCEEDED` | 400 | More than 500 records in one append |
| `BATCH_BYTES_EXCEEDED` | 400 | One append over 1 MiB in total |
| `READ_LIMIT_EXCEEDED` | 400 | `maxRecords` above 1000 |
| `RECORD_EXCEEDS_MESSAGE_BUDGET` | 400 | StreamActor read: a single record is larger than the workspace message budget and cannot be emitted without truncation |
| `STREAM_NOT_FOUND` | 404 | No such stream — never created, deleted, or **idle-expired** |
| `BACKEND_STREAM_MISSING` | 404 | The stream's storage is gone; the platform reconciles this shortly |
| `STREAM_ALREADY_EXISTS` | 409 | Slug already in use in this workspace |
| `STREAM_LIMIT_EXCEEDED` | 409 | Workspace already has 100 streams |
| `APPEND_RATE_EXCEEDED` | 429 | Over 50 appends/s on the stream or 200/s in the workspace — retry after a brief delay |
| `TAIL_LIMIT_EXCEEDED` | 429 | 20 tails already open in the workspace — honour `Retry-After` |
| `RECORD_DECRYPTION_FAILED`, `INTERNAL_ERROR` | 500 | Platform-side failure — retry, then report |
| `BACKEND_UNSUPPORTED` | 501 | The stream's storage backend cannot perform this operation |
| `BACKEND_UNAVAILABLE`, `BACKEND_ERROR` | 503 | Storage temporarily unavailable — retry with backoff |

## Input Validation Constraints

| Constraint | Value |
|---|---|
| Streams per workspace | 100 |
| Slug | `^[a-z0-9][a-z0-9_-]{0,63}$` |
| `name` / `description` | ≤ 120 / ≤ 500 chars |
| `idleTtlSeconds` | 60 – 2 592 000 (30 days); default 3 600 |
| Grace before the first append | 15 minutes, regardless of TTL |
| `maxRecordSizeInKiloBytes` | default 256; ceiling just under 1 MiB |
| Records per append | 1 – 500 |
| Bytes per append | ≤ 1 MiB |
| Append rate | 50/s per stream, 200/s per workspace |
| `readStream` `maxRecords` / `maxBytes` | ≤ 1000 / ≤ 1 MiB (StreamActor: the workspace message budget) |
| Runtime tail `maxSeconds` / `maxRecords` | default 30, ≤ 120 / ≤ 10 000 |
| Public tail | closes at 60 s idle or 300 s total; 20 concurrent per workspace |
| Record `kind` | `text` only |

## Patterns

### Resumable consumer (cursor in a Collection)

A ScheduledTriggerActor runs every few minutes; the flow reads `cursor:<stream>` from the app's collection, `readStream`s from it, processes the page, and writes `nextCursor` back. Persisting the cursor *after* processing gives at-least-once delivery — make the processing idempotent (a Collection `putItem` keyed by something in the payload is the usual way).

### Cheap change detection

Before reading, call `getStreamInfo` and compare `tailCursor` to the persisted cursor. Equal means nothing new and the flow ends without a read. This is the v1 substitute for a "record arrived" trigger and is what makes a one-minute schedule affordable.

### Fan-in event log

Several canvases append to one persistent stream (`audit-log`, `order-events`). Because appends are ordered at the platform, consumers see a single interleaved history without any coordination between producers.

### Live view

A web app or an external dashboard opens the public tail from `start` (replay, then follow) or `tail` (follow only) and reconnects from `nextCursor` on every `end`. Records the UI has captured stay on screen through a reconnect.

### What a stream is not

Not a queue — nothing marks a record consumed and two consumers reading the same cursor both get it; use the [queue pattern](collection-api.md#queue-pattern-using-collections) on a Collection for claim/complete semantics. Not a place for current state — replaying a stream to find "the latest value" is what a Collection `getItem` is for.
