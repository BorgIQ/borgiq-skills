# React app SDK (`@borgiq/actors`)

The browser SDK every ReactAppTriggerActor app ships with: named endpoints (`useEndpoint`, `callEndpoint`), the
viewer's session (`useGetSession`, `getSession`), the browser tab title (`useTitle`, `setTitle`) and live workspace
streams (`useStreamTail`, `tailStream`, `readStream`). Read it when you write the app code that talks to BorgIQ, or
when an SDK error needs explaining.

## Contents

- [Rules](#rules)
- [Endpoints](#endpoints)
- [Declaring endpoints](#declaring-endpoints)
- [Viewer session](#viewer-session)
- [Tab title](#tab-title)
- [Streams](#streams)
- [Declaring streams](#declaring-streams)
- [Stream recipes](#stream-recipes)
- [Errors](#errors)

## Rules

- Call backends only through the SDK. It attaches the `X-App-Actor-Token` to its own requests; there is no global
  `fetch` patch in a React app, so a raw `fetch()` to a `/msg/` or `/app-streams/` URL carries no token.
- Send files as `FormData` (multipart), never base64 in JSON; each file part reaches the trigger as a BIQFile.
- Treat `useGetSession` as display only: flows authorize with the server-attested `trigger.user`.

## Endpoints

```tsx
import { useEndpoint, callEndpoint, getBasename } from '@borgiq/actors'

// Hook: never fetches on its own; trigger() fires it.
const { data, loading, error, trigger } = useEndpoint('saveRecord', '?page=1', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Ada' }),
})
<button disabled={loading} onClick={() => trigger()}>Save</button>
const { data: saved, error: failed } = await trigger({ body: JSON.stringify({ name: 'Bob' }) }) // per-call override

// Non-hook: anywhere (handlers, effects, plain modules); resolves with the body, rejects on failure.
const result = await callEndpoint('saveRecord', undefined, { method: 'POST', body: new URLSearchParams({ name: 'Ada' }) })
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | string | A declared endpoint name |
| `search` | string, `URLSearchParams` or `Record<string, string>` | Appended to the endpoint URL's query |
| `init` | `{ method, headers, body, signal }` | Browser `fetch` semantics. `method` defaults to `GET`. `body` passes through untouched: `URLSearchParams` → form-encoded, `FormData` → multipart, string or `Blob` as is |

| Returned by `useEndpoint` | Meaning |
|---|---|
| `data` | The last response body: JSON when the response's content type says so, else text |
| `loading`, `error` | Request state; `error` is one of the [errors](#errors) |
| `trigger(overrides?)` | Fires the request. `overrides` merge onto `init` (headers merge, other fields replace). It **never rejects**: it resolves with `{ data, error }`, so `onClick={() => trigger()}` is safe. A newer `trigger()` aborts one still in flight, and only the newest result is kept |

`getBasename()` returns the router basename for the token path (from `document.baseURI`); pass it to a React Router
`basename`.

## Declaring endpoints

An endpoint is an entry under the actor's `options.endpoints`
([schema](typescript/actorSchemas/trigger/reactApp.md)):

| Field | Meaning |
|---|---|
| `name` | Identifier used by `useEndpoint('<name>')`: letters, digits, underscore, not starting with a digit |
| `actorId` | The target: a WebhookTriggerActor, or a UniversalTriggerActor with its webhook source enabled |
| `workspaceSlug`, `canvasSlug` | Optional **slugs**; blank targets this canvas. Another canvas or workspace must be in the same org |
| `description` | Optional |

- The list is the app's authorization grant: the API answers `401` for any webhook the build does not declare, even
  one on the same canvas, and for every endpoint until the app is built.
- It is resolved at Build and frozen into the build: endpoint edits, including a target's `triggerKey`, apply on the
  next Build. `${{ }}` is allowed in the string fields; a target that cannot be resolved makes `useEndpoint` throw
  `EndpointResolutionError`.
- Set the target trigger to `authorizationLevel: apps`, or `appsAndApiKey` when external API callers share it.
  `public` skips token checks and suits only genuinely public endpoints.
- At most 50 endpoints per actor.

## Viewer session

```tsx
import { useGetSession, getSession } from '@borgiq/actors'

const { data: session, loading, error } = useGetSession()   // passive: resolves on mount, no trigger()
if (session) return <p>Hello, {session.name || session.email}</p>

const viewer = await getSession()                            // non-hook; rejects instead of returning error state
```

| Field | Meaning |
|---|---|
| `id` | The signed-in viewer's user id |
| `userId` | Alias of `id`; prefer it, since it cannot be confused with `appSessionId` |
| `email` | The viewer's email |
| `name` | Display name; may be `''` |
| `appSessionId` | This visit: one id per BorgIQ login and app. May be absent (older tokens): treat absence as "no session information" and degrade, never crash |

- It is the identity flows see as `trigger.user`. `data` is `null` until it resolves and on error.
- `appSessionId` survives reloads and token refreshes; another app, or a new login (a session handoff included), gets
  a new one; tabs of one app share it (add a per-tab suffix for tab identity). Key per-visit state (a draft, a wizard
  step, a chat thread) on it, with `userId` beside it when the data belongs to the person.
- It is decoded from the token the SDK holds (no request) and cached per login: a profile rename shows the old `name`
  until reload; a re-login in the parent refreshes it on the next read.
- Outside the BorgIQ iframe (a local `npm run dev`) it settles at once with `SessionUnavailableError`: gate identity UI
  on `session`.
- It authorizes nothing. Enforce access with `apps` endpoints and per-app grants, and trust `trigger.user.appSessionId`,
  never a session id sent in a body or query.

## Tab title

The app runs in a cross-origin iframe and cannot write the tab's title itself, so the SDK asks the BorgIQ page that
hosts it.

```tsx
import { useTitle, setTitle } from '@borgiq/actors'

function OrderPage({ order }) {
  useTitle(order ? `Order ${order.number}` : null)   // held while mounted, given back on unmount
  …
}

setTitle('Saving…')   // non-hook: anywhere; setTitle(null) withdraws it
```

- **Precedence:** a title set in code, then the actor's `options.title`, then BorgIQ's default (`App | BorgIQ`).
  `options.title` is a static title that needs no code; it accepts `${{ }}` and is frozen at Build
  ([react-app-build.md](react-app-build.md#build-time-options)).
- The tab shows the text as written, with nothing appended. BorgIQ strips control and invisible characters, collapses
  whitespace and cuts it at 150 characters. A title that is nothing but such characters clears the runtime title.
- When several mounted components call `useTitle`, the most deeply nested, most recently mounted one wins: set a
  general title in a layout and a specific one in each route. `null`, `undefined` or a blank string claims nothing, so
  pass `null` while data loads. `setTitle` outranks the hooks mounted when it is called, until `setTitle(null)`; a
  hook that mounts afterwards takes over, so clear a transient `setTitle` rather than leaving it.
- Only the app's own page (`/org/{org}/w/{wsp}/c/{canvas}/apps/{actorId}`) honours it. A page that embeds the app
  some other way, such as an interface page's web viewer, keeps its own tab title.
- The `<title>` in `index.html`, and `document.title` written by the app, never reach the tab.
- Both calls return nothing and never throw. They need SDK 2.4.0 (`version` from `@borgiq/actors`); on a BorgIQ that
  predates them the tab keeps its default.
- Under a local `npm run dev` they set the local page's `document.title`, and clearing restores the original.

## Streams

Tail a [declared](#declaring-streams) stream by slug. The SDK opens a Server-Sent Events tail with the app token and
owns the connection, cursor, reconnection, buffer and polling fallback.

```tsx
import { useStreamTail, tailStream, readStream } from '@borgiq/actors'

const { records, status, dropped } = useStreamTail('agent-activity', { from: 'tail' })            // live from now
const { records: chat } = useStreamTail(chatSlug, { from: 'start', resumeKey: 'chat' })         // a slug an endpoint returned

for await (const record of tailStream('agent-activity', { from: 'tail', signal })) { /* … */ }     // ends on abort or a terminal condition
const { records, nextCursor, tailCursor, hasMore } = await readStream('agent-activity', { from: 'start', maxRecords: 200 })
```

| `useStreamTail` option | Default | Meaning |
|---|---|---|
| `from` | `'tail'` | Where the **first** session starts: `'start'`, `'tail'` or a cursor this stream issued. Later sessions resume from the SDK's cursor |
| `enabled` | `true` | `false` closes the tail and releases its connection |
| `resumeKey` | — | Keep the cursor in `sessionStorage` (`borgiq:stream:<appActorId>:<resumeKey>`), so the tail survives a reload in this tab |
| `maxBufferedRecords` / `maxBufferedChars` | `1000` / `1,000,000` | Drop-oldest buffer bounds; evictions count in `dropped` |
| `onRecord` | — | Called per record as it lands, for an app that processes records without keeping them |
| `pollFallbackMs` | `5000` | While capped (`429`), poll the paged read at this interval; `0` disables |

It returns `records` (newest last, each `{ cursor, timestamp, payload }`; `payload` is the string the flow appended),
`dropped`, `status`, `cursor` (where to resume), `error` and `retryNow()` (cut a backoff or `Retry-After` wait short).
`readStream` returns one page and never blocks; `tailStream` takes `from`, `signal` and `pollFallbackMs`.

| `status` | Show |
|---|---|
| `idle` | Nothing yet: `enabled: false`, or before the first connect |
| `connecting` | A "connecting…" affordance |
| `live` | The feed. A clean server end (60 s idle / 300 s total) reconnects silently and stays `live` |
| `reconnecting` | The feed and a quiet "reconnecting" hint (backing off after a network or retryable error) |
| `capped` | "The workspace is busy": a `429`; the SDK waits out `Retry-After` or drops to `polling` |
| `polling` | The feed, updated on a timer through the paged read until the tail can reopen |
| `gone` | "This stream has ended": deleted or idle-expired. Terminal; the buffer is kept; offer no retry |
| `error` | `error.message`. Terminal: undeclared stream, non-retryable error frame, repeated 5xx, or no session (local dev) |

Components tailing one slug share a connection, cursor and buffer. The SDK refuses a **fifth** distinct concurrent
tail on a page, so endpoint calls never stall behind open connections: tail a few streams, not one per row. Server
caps (per viewer and app: 4 open tails, 30 opens a minute; 100 app tails per workspace) are in
[stream-api.md](stream-api.md#tailing-from-a-react-app).

## Declaring streams

An app can tail only the streams its actor declares under `options.streams`:

```yaml
streams:
  - name: activity        # an identifier, like an endpoint name (the hook takes the slug, not this)
    slug: agent-activity  # one stream, exact slug
  - name: chats
    slugPrefix: chat-     # every stream whose slug starts with chat- (per-session streams a flow creates)
```

- Each entry has exactly one of `slug` or `slugPrefix` (1–64 characters). At most 50 entries.
- Declarations resolve in the app's **own workspace only**: a stream grant has no workspace or canvas coordinates.
- They are frozen at Build like endpoints: a stream declared later answers `403 STREAM_NOT_DECLARED` until you rebuild.
- Every viewer's token is authorized by the same declarations, so a `chat-` prefix lets viewer A read viewer B's
  `chat-<id>` if A learns the slug. Mint per-session slugs from an unguessable part (the stream's ULID, a random
  suffix), hand each to the app in an endpoint response, and never derive them from a user id or counter.
- Apps only read. To write, call an endpoint whose flow appends; the write is then validated, rate-limited and
  attributed to a flowrun.

## Stream recipes

- **History, then live.** There is no "last N records" position: `from: 'tail'` shows nothing until the next append;
  `from: 'start'` replays everything. Read history with `readStream(slug, { from: 'start' })` (page on `nextCursor`
  while `hasMore`), then mount `useStreamTail(slug, { from: 'tail' })`. That is a full replay on a long stream, so give
  long-lived streams an idle TTL or mint per-session ones.
- **Resume is per tab.** The cursor lives in memory, or in `sessionStorage` with `resumeKey` (never the token). To
  resume across devices, save `cursor` through an endpoint and pass it back as `from`.
- **A tail is not activity.** Only appends refresh a stream's idle TTL; an unwritten stream expires and the hook goes
  `gone`. Fix it in the flow that creates the stream (a longer `idleTtlSeconds`, or `persistent: true`).
- **Sensitive data.** Records reach the browser as plaintext and stay visible in devtools while the tail is open. The
  SDK stores only a cursor; do not write records to `localStorage`. The declaration is the control that matters:
  declare narrowly.

## Errors

| Error | Carries | When |
|---|---|---|
| `EndpointNotFoundError` | `endpoint` | The name is not declared in the build |
| `EndpointResolutionError` | `endpoint` | The endpoint's target could not be resolved at Build |
| `EndpointHttpError` | `endpoint`, `status`, `body` (parsed) | Any non-2xx response |
| `TokenTimeoutError` | — | No app token arrived from the BorgIQ page within 5 s |
| `SessionUnavailableError` | — | No viewer can exist here: not embedded in BorgIQ (local dev), or the token has no identity. Hooks settle at once in `error`: gate the UI on it (`session`, `status !== 'error'`) so the page renders locally |
| `StreamNotDeclaredError` | `stream` | The slug matches no declaration: thrown before any request, or the server's `403 STREAM_NOT_DECLARED` for a stream addressed by id. Declare it and rebuild |
| `StreamGoneError` | `stream` | `404` on a (re)connect or read: deleted or idle-expired. The hook reports `gone` |
| `StreamHttpError` | `stream`, `status`, `body` | Any other non-2xx, including `429 VIEWER_TAIL_LIMIT_EXCEEDED` (this viewer has 4 tails open on this app: close a tab) and the per-minute open limit |
