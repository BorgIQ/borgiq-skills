# Stream API Reference

Streams from code and from outside a canvas: the SDK for DenoActor and PythonActor, tailing from actor code, the public
REST API and its scopes, the Server-Sent Events tail, the React app surface, and the canonical error codes and limits.
Read [stream-actor.md](stream-actor.md) first: it holds the stream rules (provisioning, expiry, paging, cursors), every
action's options and results, and the collections-vs-streams choice.

## Contents

- [Surfaces](#surfaces)
- [SDK (DenoActor / PythonActor)](#sdk-denoactor--pythonactor)
- [Tailing from actor code](#tailing-from-actor-code)
- [Public REST API](#public-rest-api)
- [Tailing over Server-Sent Events](#tailing-over-server-sent-events)
- [Tailing from a React app](#tailing-from-a-react-app)
- [Error codes](#error-codes)
- [Limits](#limits)

## Surfaces

| Surface | Reaches streams through | Auth |
|---|---|---|
| StreamActor | YAML `action` ([stream-actor.md](stream-actor.md)) | Automatic |
| DenoActor, PythonActor | `POST /streams` on the runtime endpoint via `biqApi` / `biq_api` | Automatic, tenant-scoped |
| External systems, scripts, the CLI | `/v1/orgs/:org/workspaces/:workspace/streams` | Personal access token |
| A React app on a canvas | `/v1/app-streams/…`, through the SDK | The app-actor token |

Every surface goes through BorgIQ endpoints; no actor, app or client holds a storage credential.

## SDK (DenoActor / PythonActor)

From code, every action is one `POST /streams` whose body is the action's options, as for `POST /collections`. The
response is the envelope `{ ok: boolean, value: T, error?: { code, message } }`; `T` is the action's result in
[stream-actor.md → Actions](stream-actor.md#actions).

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

// createStream: persistent, so an app can depend on it
await streamsApi({ action: "createStream", slug: "order-events", persistent: true });

// appendData: the batch is stored in full or not at all
const ack = await streamsApi<{ tailCursor: string }>({
  action: "appendData",
  stream: "order-events",
  records: [{ payload: JSON.stringify({ orderId: "O-1", state: "paid" }) }],
});

// getStreamInfo first: an unchanged tail means nothing new
const info = await streamsApi<{ tailCursor: string }>({ action: "getStreamInfo", stream: "order-events" });
if (info.tailCursor === (await loadCursor())) return;

// readStream: walk forward from the persisted cursor, one page at a time
let from = (await loadCursor()) ?? "start";
while (true) {
  const page = await streamsApi<{
    records: { cursor: string; timestamp: string; payload: string }[];
    nextCursor: string; hasMore: boolean;
  }>({ action: "readStream", stream: "order-events", from, maxRecords: 500 });
  for (const record of page.records) await handle(JSON.parse(record.payload));
  await saveCursor(page.nextCursor);
  if (!page.hasMore) break;
  from = page.nextCursor;
}
```

`loadCursor` and `saveCursor` are yours: typically a collection item keyed `cursor:order-events`, saved with
`putItem` and `options.overwrite: true` ([collection-sdk.md](collection-sdk.md)).

Python sends the same bodies:

```python
from borgiq import Request, Response, biq_api

def receive(req: Request) -> Response:
    biq_api('/streams', method='POST', json={
        'action': 'appendData', 'stream': 'order-events',
        'records': [{'payload': '{"orderId": "O-1", "state": "paid"}'}],
    })
    page = biq_api('/streams', method='POST', json={
        'action': 'readStream', 'stream': 'order-events',
        'from': req.inputs.get('cursor') or 'start', 'maxRecords': 500,
    }).json()['value']
    info = biq_api('/streams', method='POST', json={
        'action': 'getStreamInfo', 'stream': 'order-events',
    }).json()['value']
    return Response(results={'records': page['records'], 'nextCursor': page['nextCursor'], 'tail': info['tailCursor']})
```

## Tailing from actor code

Actor code can hold a tail open for a bounded window instead of polling, to get records as they land:

```
GET /streams/:streamIdOrSlug/tail?from=<start|tail|cursor>&maxSeconds=<1..120>&maxRecords=<1..10000>
```

- `maxSeconds` defaults to **30** and is capped at **120**; `maxRecords` closes the tail after that many records. The
  tail also closes when half of `maxSeconds` passes with no record. The actor pays for the whole wait and has its own
  invocation timeout, so state the budget you mean.
- The wire format is the [public tail's](#tailing-over-server-sent-events): a record frame's `id:` line is the
  successor cursor, `data.cursor` the record's own position, and `event: end` carries `nextCursor` when a bound is
  reached.
- A tail holds one of the workspace's 20 tail slots for its whole duration. Do not tail from a scheduled loop when
  `getStreamInfo` + `readStream` would do.

```typescript
const res = await biqApi("/streams/order-events/tail", { queryParams: { from: cursor, maxSeconds: "60", maxRecords: "100" } });
const text = await res.text(); // the whole SSE transcript: the tail closes itself at the bound
for (const frame of text.split("\n\n")) {
  const lines = frame.split("\n");
  const data = lines.find((l) => l.startsWith("data: "))?.slice(6);
  const id = lines.find((l) => l.startsWith("id: "))?.slice(4); // the successor: where to resume
  if (frame.includes("event: record") && data) { handle(JSON.parse(data)); if (id) cursor = id; }
  if (frame.includes("event: end") && data) cursor = JSON.parse(data).nextCursor;
}
```

## Public REST API

External systems, scripts and the CLI use the workspace REST API with a personal access token
([api-tokens.md](api-tokens.md)), under `/v1/orgs/:orgSlugOrId/workspaces/:workspaceSlugOrId/streams`:

```http
POST /v1/orgs/my-org/workspaces/my-workspace/streams/order-events/records
Authorization: Bearer biq_abc123...
Content-Type: application/json

{ "records": [ { "payload": "{\"orderId\":\"O-1\",\"state\":\"paid\"}" } ] }
```

Scopes are per verb: a workspace viewer can read and tail, and cannot create, append, edit or delete.

| Method | Path | Body or query | Scope | Returns |
|---|---|---|---|---|
| `GET` | `/streams` | — | `stream:read` | Every stream summary |
| `POST` | `/streams` | `{ slug, name?, description?, idleTtlSeconds? \| persistent?, maxRecordSizeInKiloBytes? }` | `stream:write` | `201` + the stream summary |
| `PUT` | `/streams/:streamIdOrSlug` | `{ name?, description?, idleTtlSeconds? \| persistent?, maxRecordSizeInKiloBytes? }` | `stream:write` | The stream summary |
| `DELETE` | `/streams/:streamIdOrSlug` | — | `stream:delete` | `{ streamId, slug }` |
| `GET` | `/streams/:streamIdOrSlug/records` | `?from=&maxRecords=&maxBytes=` | `stream:read` | One `readStream` page |
| `POST` | `/streams/:streamIdOrSlug/records` | `{ records: [{ payload, kind? }] }` | `stream:write` | The `appendData` result |
| `GET` | `/streams/:streamIdOrSlug/tail` | `?from=` | `stream:read` | `text/event-stream` (below) |

Every JSON response is the `{ ok, value }` envelope, with the shapes in [stream-actor.md](stream-actor.md#actions);
errors are `{ ok: false, error: { code, message } }` with the status in [Error codes](#error-codes). A missing or invalid
token is `401`; a token without the scope, or for a workspace its user is not a member of, is `403`. There is no
`GET /streams/:id`: the list carries every summary field, and the live tail comes from `getStreamInfo` or a page's
`tailCursor`.

## Tailing over Server-Sent Events

`GET …/streams/:streamIdOrSlug/tail` holds the connection open and pushes records as they arrive. It is the only stream
surface that waits, which is why it is capped.

```http
GET /v1/orgs/my-org/workspaces/my-workspace/streams/order-events/tail?from=start
Authorization: Bearer biq_abc123...
Accept: text/event-stream
```

- `from` is `start`, `tail` or a cursor; **omitted, it is `tail`** (only records appended after the connection opens).
- A `Last-Event-ID` header **overrides `from`**. Browser `EventSource` sends the last `id` it received, the successor
  cursor, on reconnect, which is why resuming is free. A value this stream did not issue is rejected with
  `400 INVALID_CURSOR`, never ignored.

Each record is one event whose `id` is the position to **resume from**, the record's successor; `data.cursor` is the
record itself. Replay the `id` and the next session starts after the record you already have.

```
id: <opaque-cursor>
event: record
data: {"cursor":"<opaque-cursor>","timestamp":"2026-08-27T10:41:12.317Z","payload":"{\"orderId\":\"O-1\",\"state\":\"paid\"}"}

: heartbeat

event: end
data: {"nextCursor":"<opaque-cursor>","records":2,"reason":"idle"}

event: error
data: {"code":"BACKEND_UNAVAILABLE","message":"Stream storage is temporarily unavailable","retryable":true}
```

| Frame | When | What to do |
|---|---|---|
| `event: record` | A record landed | Handle `data`; keep the **`id:` line** as the resume point. Resuming from `data.cursor` re-delivers the record, because reads are inclusive |
| `: heartbeat` | Every 15 s while quiet | Nothing; it keeps proxies from dropping the connection. Treat 45 s of silence as a dead connection |
| `event: end` | The server closed the session cleanly | **Reconnect with `from = data.nextCursor`**, which is always present (the opening position if nothing was sent). `reason` is `idle`, `total` or `maxRecords`: after `idle` the stream was silent, so pause first; after the others more may be waiting |
| `event: error` | A failure after the headers were sent | `{ code, message, retryable }`: reconnect with backoff from your last `id:` only when `retryable` is true. A non-retryable code (a deleted stream, another stream's cursor) fails the same way forever, so stop |

**A clean `end` is the normal path.** The public tail closes after **60 s without a record** or **300 s in total**; a
consumer that stays subscribed reconnects from `nextCursor` and misses nothing. A live view that reconnects this way
keeps the records it already shows.

Failures before the stream starts arrive as real HTTP statuses in the `{ ok: false, error }` envelope, never as a `200`
whose first frame is an error:

| Status | Meaning |
|---|---|
| `400 INVALID_CURSOR` | `from` or `Last-Event-ID` is malformed or from another stream |
| `404 STREAM_NOT_FOUND` | The stream does not exist, or **idle-expired** while you tailed it. That is lifecycle, not a transient error: stop reconnecting |
| `429 TAIL_LIMIT_EXCEEDED` + `Retry-After: 30` | The workspace already has **20** open tails; retry after `Retry-After` |
| `503 BACKEND_UNAVAILABLE` | Storage could not be reached to open the session; retry with backoff |
| `401` / `403` | Token missing, invalid, or without `stream:read` |
| `403 STREAM_NOT_DECLARED` / `429 VIEWER_TAIL_LIMIT_EXCEEDED` | App surface only ([below](#tailing-from-a-react-app)) |

## Tailing from a React app

A React app served by a ReactAppTriggerActor reads streams through its own routes, authenticated by the app-actor token
the `@borgiq/actors` SDK holds:

```http
GET /v1/app-streams/:org/:workspace/:streamIdOrSlug/tail?from=<cursor|start|tail>
GET /v1/app-streams/:org/:workspace/:streamIdOrSlug/records?from=<cursor|start|tail>&maxRecords=&maxBytes=
X-App-Actor-Token: <app-actor JWT>
Accept: text/event-stream
```

- **Header only.** The token travels in `X-App-Actor-Token`, never in a query string. No PAT, no `stream:read` scope.
- **Authorized by declaration.** The app's build lists the streams it may read (`options.streams` on the actor: an exact
  `slug` or a `slugPrefix`, same workspace only, frozen at Build). Anything else, including a stream declared after the
  last Build, is `403 STREAM_NOT_DECLARED`: declare it and rebuild.
- **Same frames and pre-commit statuses** as the public tail, with the same 60 s idle and 300 s total budgets, but **no
  `Last-Event-ID`**: the client is `fetch`, and the SDK always sends `from`.
- **Its own caps:** a pool of **100 app tails per workspace** (`TAIL_LIMIT_EXCEEDED`), separate from the 20
  public and actor tails, plus **4 open tails per viewer per app** (`VIEWER_TAIL_LIMIT_EXCEEDED`) and **30 opens per
  minute** per viewer. All carry `Retry-After: 30`.
- **Read only.** There is no app-token append: an app writes to a stream by calling an endpoint whose flow appends.

Never call these routes by hand from app code. The SDK attaches the token, shares one connection per stream, resumes
from its cursor and falls back to polling `…/records` while capped; `useStreamTail`, `tailStream` and `readStream` are
documented in [react-app-sdk.md → Streams](react-app-sdk.md#streams).

## Error codes

| Code | HTTP | Meaning |
|---|---|---|
| `INVALID_ACTION` | 400 | Unknown `action` |
| `INVALID_STREAM_SLUG` | 400 | Slug does not match `^[a-z0-9][a-z0-9_-]{0,63}$` |
| `INVALID_IDLE_TTL` | 400 | `idleTtlSeconds` outside 60–2,592,000, or combined with `persistent` |
| `INVALID_RECORD_SIZE` | 400 | `maxRecordSizeInKiloBytes` below 1 or above the ceiling (just under 1 MiB) |
| `EMPTY_APPEND` | 400 | `records` is empty |
| `INVALID_RECORD_KIND` | 400 | A `kind` other than `text` |
| `INVALID_CURSOR` | 400 | Malformed cursor, or one from another stream |
| `RECORD_TOO_LARGE` | 400 | A payload over the stream's `maxRecordSizeInKiloBytes` |
| `BATCH_LIMIT_EXCEEDED` | 400 | More than 500 records in one append |
| `BATCH_BYTES_EXCEEDED` | 400 | One append over 1 MiB |
| `READ_LIMIT_EXCEEDED` | 400 | `maxRecords` above 1000 |
| `RECORD_EXCEEDS_MESSAGE_BUDGET` | 400 | A read from actor code met a record larger than the workspace message budget |
| `STREAM_NOT_DECLARED` | 403 | App surface: the React app's build does not declare the stream; declare it and rebuild |
| `STREAM_NOT_FOUND` | 404 | Never created, deleted, or **idle-expired** |
| `BACKEND_STREAM_MISSING` | 404 | The stream's storage is gone; the platform reconciles this shortly |
| `STREAM_ALREADY_EXISTS` | 409 | The slug is taken in this workspace |
| `STREAM_LIMIT_EXCEEDED` | 409 | The workspace already has 100 streams |
| `APPEND_RATE_EXCEEDED` | 429 | Over 50 appends/s on the stream or 200/s in the workspace; retry after a short delay |
| `TAIL_LIMIT_EXCEEDED` | 429 | 20 tails open in the workspace, or 100 in the app-tail pool; honour `Retry-After` |
| `VIEWER_TAIL_LIMIT_EXCEEDED` | 429 | App surface: this viewer has 4 app tails open on this app; close a tab, then honour `Retry-After` |
| `RECORD_DECRYPTION_FAILED`, `INTERNAL_ERROR` | 500 | Platform failure: retry, then report |
| `BACKEND_UNSUPPORTED` | 501 | The storage backend cannot perform this operation |
| `BACKEND_UNAVAILABLE`, `BACKEND_ERROR` | 503 | Storage temporarily unavailable; retry with backoff |

## Limits

| Limit | Value |
|---|---|
| Streams per workspace | 100 |
| Slug | `^[a-z0-9][a-z0-9_-]{0,63}$` |
| `name` / `description` | ≤ 120 / ≤ 500 characters |
| `idleTtlSeconds` | 60 – 2,592,000 (30 days); default 3,600 |
| Grace before the first append | 15 minutes, whatever the TTL |
| `maxRecordSizeInKiloBytes` | Default 256; ceiling just under 1 MiB |
| Records per append | 1 – 500 |
| Bytes per append | ≤ 1 MiB |
| Append rate | 50/s per stream, 200/s per workspace |
| `readStream` `maxRecords` / `maxBytes` | ≤ 1000 / ≤ 1 MiB; from actor code the workspace message budget caps it |
| Runtime tail `maxSeconds` / `maxRecords` | Default 30, ≤ 120 / ≤ 10,000 |
| Public tail | Closes at 60 s idle or 300 s total; 20 concurrent per workspace |
| App tails | 100 per workspace; 4 per viewer per app; 30 opens/min per viewer |
| Record `kind` | `text` only |
