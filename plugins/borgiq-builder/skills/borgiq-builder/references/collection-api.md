# Collection API Reference

The Collection API provides persistent, structured storage organized into named collections, backed by AWS DynamoDB. It is accessed via:

- **CollectionActor** — YAML configuration with `action` field. See [collection-actor.md](collection-actor.md).
- **DenoActor** — `biqApi('/collections')` from `@borgiq/actors`. See [deno-actor.md](deno-actor.md).
- **PythonActor** — `biq_api('/collections')` from `borgiq`. See [python-actor.md](python-actor.md).

All operations go through a single `POST /collections` runtime endpoint with an `action` field in the request body. Authentication and tenant scoping are handled automatically.

## Table of Contents

- [Overview](#overview)
- [Single-Collection Design](#single-collection-design)
- [Collection Management Actions](#collection-management-actions)
- [Item Operations](#item-operations)
- [Query Expression Syntax](#query-expression-syntax)
- [Condition Expressions](#condition-expressions)
- [Concurrent Update Patterns](#concurrent-update-patterns)
- [Batch Operations](#batch-operations)
- [Transactions](#transactions)
- [SDK Interface (DenoActor / PythonActor)](#sdk-interface-denoactor--pythonactor)
- [Response Format Reference](#response-format-reference)
- [Error Codes](#error-codes)
- [Input Validation Constraints](#input-validation-constraints)
- [Queue Pattern (using Collections)](#queue-pattern-using-collections)
- [DynamoDB Mapping Reference](#dynamodb-mapping-reference)

## Overview

The Collection API provides persistent, structured storage organized into named collections. It is the recommended storage solution for all new workflows, including queue semantics via key ordering and conditional writes.

**Built on DynamoDB:** Collections are backed by AWS DynamoDB. All collections of all workspaces live in **one shared table**: a collection is one **partition key** (`<org>#<workspace>#<slug>`, built by the API layer) and each item's `key` is the **sort key**, stored verbatim. This means:
- **Keys are sorted lexicographically** (UTF-8 byte order) — prefix queries like `user:*` and range queries like `>=user:U003` are efficient and fast
- **Design keys hierarchically** using delimiters (e.g., `app:R001:C004`) to enable efficient prefix-based access patterns
- **One app = one collection** — model all of an app's entity types in a single collection with key prefixes, not one collection per entity type. See [Single-Collection Design](#single-collection-design) and its [capacity model](#capacity-model-what-one-collection-carries)
- **Writes are durable immediately; reads are eventually consistent.** The platform does not request strongly consistent reads, so `getItem`, `query`, and `batchGetItem` use DynamoDB's default — usually current within milliseconds, but a `getItem` issued right after a `putItem`/`updateItem` *can* return the previous version. Use the value a write returns instead of re-reading it; use `transactGet` when you need a consistent snapshot
- **Transactions are ACID** — `transactWrite` is all-or-nothing across up to 100 items, even across collections
- **No full-table scans** — queries always operate on a single collection (partition key), keeping them fast regardless of total data size
- **Not for event logs** — data that is "what happened, in order" (events, audit trails, feeds) and consumers that resume from a cursor belong in a [Stream](stream-api.md), not in `event:<timestamp>` items. See [Collections vs Streams](stream-api.md#collections-vs-streams)

**Collection Management:** Create, list, update, delete collections

**Item Operations:** Put, get, update, delete items with optional labels and TTL

**Query:** Query items with expressions, pagination, and label filtering

**Batch Operations:** Batch get (up to 100) and batch write (up to 25) items

**Transactions:** Transactional reads (up to 100) and writes (up to 100) with conditions

## Single-Collection Design

**Default rule: one app, one collection.** Model *all* of an app's entity types in a single collection and separate them with key prefixes — do **not** create one collection per entity type. BorgIQ is itself single-table: every collection in every workspace lives in one DynamoDB table, keyed `PK = <org>#<workspace>#<collection>`, `SK = <item key>`. A collection is therefore **one partition key**, and "one app = one collection" means the whole app lives under one partition key. That is the right default for what BorgIQ apps are — internal tools, up to ~100,000 users — and the [capacity model](#capacity-model-what-one-collection-carries) below gives the numbers and the three design rules that keep it true. Only split an app across multiple collections when a **security/access boundary** requires it, the **user explicitly asks** for separate collections, or sustained write throughput genuinely approaches the partition limit (see [When multiple collections are justified](#when-multiple-collections-are-justified)).

**Wrong — one collection per entity type:**

```
tt-tickets     ticket records
tt-users       user records
tt-labels      label records
tt-comments    comment records
tt-activity    activity records
tt-meta        schema version + counters
```

**Right — one collection, one key prefix per entity type, a `$meta` manifest on top** (shown in the order the UI lists them):

```
Collection: ticketing
  $meta                            manifest: lists every entity prefix below — always the first row
  $migration:<id>                  migration ledger
  $counter:ticketNumber            atomic counters
  activity:<ticketId>:<at>         activity, sorted under its ticket
  comment:<ticketId>:<createdAt>   comments, sorted under their ticket
  label:<id>                       label records
  ticket:<id>                      ticket records
  user:<id>                        user records
```

Everything a separate collection gives you, a key prefix gives you too: `query { collection: "ticketing", expression: "ticket:*" }` is exactly as fast and exactly as isolated as `query { collection: "tt-tickets", expression: "*" }` — both are a single-partition prefix read.

### Key-prefix modeling rules

- **`<entity>:<id>`** for top-level entities: `ticket:01HQX...`, `user:demo-maya`, `label:bug`.
- **Hierarchical keys for child entities:** `comment:<ticketId>:<createdAt>` sorts a ticket's comments together in time order — one prefix query (`comment:ticket-42:*`) fetches them, no index needed.
- **`config:` prefix for app-level lookup rows** (settings, status enums). Schema version, counters, and the migration ledger are *system* rows and live under `$` (below), not under an entity prefix.
- **Always query by entity prefix, never `*`.** In a shared collection a bare `*` returns every entity type. `expression: "ticket:*"` is the equivalent of `SELECT * FROM tickets`.
- **Reserve the `$` prefix for system rows** (`$meta`, `$migration:<id>`, `$counter:<name>` — see [The `$` system namespace and the `$meta` manifest](#the--system-namespace-and-the-meta-manifest)); entity prefixes are lowercase words and never start with `$`.

### The `$` system namespace and the `$meta` manifest

A shared collection has a discoverability problem that a one-entity collection doesn't: the Collections UI (and a bare `query` with `expression: "*"`) lists items in **UTF-8 byte order of the key, one page at a time**. In a ticketing collection the first page is all `activity:*` rows, and nothing tells you that `comment:`, `label:`, `ticket:`, and `user:` rows exist further down — a full listing of a large collection is exactly the scan you don't want to run. The fix is a standard, always-present **manifest item that sorts before every entity row**, so it is the first thing anyone sees and tells them which prefixes to search.

**Rule: every app collection has a `$meta` item, and all system rows use the `$` prefix.**

`$` is chosen deliberately. Keys sort by UTF-8 bytes, and `$` (0x24) sorts before digits (`0` = 0x30), uppercase (`A` = 0x41), underscore (`_` = 0x5F), and lowercase (`a` = 0x61) — so `$`-rows are always the first rows on page one, no matter how entities are keyed. The alternatives all fail somewhere: `_` sorts *after* digits and uppercase (so a ULID-keyed or uppercase row beats it); `!`, `-`, `&`, `%`, and `*` are YAML-special at the start of a plain scalar and break CollectionActor configs; `>`, `<`, `|`, and a trailing `*` are query-expression operators; `#` is not allowed in keys. `$` is safe in YAML plain scalars, JS template literals (only `${` is special), Python, and query expressions (`$*` lists the whole system namespace).

> **"But AWS says avoid `$` in DynamoDB."** That guidance is about attribute *names* (column names), which need `ExpressionAttributeNames` aliases when they contain special characters. An item key is an attribute *value* — the `SK` value in the platform's table — and is never used as a name or parsed anywhere: it only ever appears as `SK: "$meta"` in a put or as the `:sk` value of `begins_with(#sk, :sk)` in a query. A leading `#`, `$`, or `%` in a sort-key *value* is the standard DynamoDB technique for pinning rows to the top of a partition; `#` is reserved by the platform as its partition-key delimiter, which leaves `$`.

| Key | Purpose | Written by |
|-----|---------|-----------|
| `$meta` | **Required.** The collection manifest: app name, applied `schemaVersion`, and the `entities` index of every key prefix in the collection | Migration runner, at the end of **every** invoke, with `overwrite: true` |
| `$migration:<id>` | Migration ledger — one row per applied migration | Migration runner |
| `$counter:<name>` | Atomic counters (`updateItem` + `atomicCounters`), e.g. `$counter:ticketNumber` | App code |
| `$<anything-else>` | Other operational singletons (locks, cursors, cached config) | App code |

`$` rows are **never entity data** and never appear in entity prefix queries (`ticket:*`), so they cost nothing at read time.

**`$meta` shape:**

```json
{
  "app": "ticketing",
  "schemaVersion": 3,
  "entities": {
    "ticket":   { "prefix": "ticket:",   "key": "ticket:<ulid>",                  "description": "Tickets" },
    "user":     { "prefix": "user:",     "key": "user:<id>",                      "description": "Users and demo users" },
    "label":    { "prefix": "label:",    "key": "label:<slug>",                   "description": "Ticket labels" },
    "comment":  { "prefix": "comment:",  "key": "comment:<ticketId>:<createdAt>", "description": "Comments, sorted under their ticket", "parent": "ticket" },
    "activity": { "prefix": "activity:", "key": "activity:<ticketId>:<at>",       "description": "Activity log, sorted under its ticket", "parent": "ticket" }
  },
  "system": {
    "$migration:": "Applied migration ledger",
    "$counter:":   "Atomic counters (ticketNumber)"
  },
  "labels": { "type": "entity name (ticket, user, …)", "status": "ticket status", "owner": "assignee id" },
  "updatedAt": "2026-08-20T10:00:00.000Z"
}
```

Rules for the manifest:

- **It is derived from code, not edited by users.** The migration runner holds an `ENTITIES` constant and rewrites `$meta` with `putItem` + `options.overwrite: true` at the end of every invoke — applied migrations or not. This is the one seed-style write where `overwrite: true` is correct: clobbering a manifest with a fresher copy of itself is the point. (Seed *data* rows keep the create-only default — see [collection-migrations.md](collection-migrations.md).)
- **Adding an entity prefix means updating `ENTITIES` and re-invoking the runner.** A prefix that isn't in `$meta` is invisible to everyone who opens the collection. Treat "new key prefix, manifest not updated" as a bug.
- **`schemaVersion` is the *applied* version**, written after migrations succeed. App code that needs to refuse traffic until migrations run (`MIGRATIONS_PENDING`) reads `$meta` and compares `schemaVersion` to the version it was built against; a missing `$meta` means version 0.
- **Keep the manifest small** — prefixes, key patterns, one-line descriptions, label meanings. No counts (they go stale), no data.

**Access pattern — the same three steps everywhere:**

1. **Read `$meta`.** In the UI it is the first row of the collection. In code: `getItem { collection, key: "$meta" }`.
2. **Pick a prefix from `entities`.** Every entity the app stores is listed; nothing else needs to be discovered by scanning.
3. **Prefix-query it.** UI: type `ticket:*` in the expression box. Code: `query { collection, expression: "ticket:*" }`.

```typescript
// Enumerate a collection without scanning it: manifest first, then one prefix query per entity.
const manifest = await collectionsApi<GetItemResult<{ entities: Record<string, { prefix: string }> }>>({
  action: "getItem", collection: "ticketing", key: "$meta",
});
for (const [name, entity] of Object.entries(manifest?.value.entities ?? {})) {
  const page = await collectionsApi<QueryResult>({
    action: "query", collection: "ticketing", expression: `${entity.prefix}*`, options: { limit: 25 },
  });
  console.log(name, page.count, page.lastKey ? "(more)" : "");
}
```

### Labels in a shared collection

A collection has at most **15 label slots** (`MAX_LABEL_SLOTS`), shared by every entity type in it. Each slot is a physical Global Secondary Index on the shared table, so the cap is a property of the table, not a per-tenant setting. Fifteen is enough that slot *count* is rarely the constraint in single-collection design; write cost is (every label is an extra GSI write per item — see the [capacity model](#capacity-model-what-one-collection-carries)). Choose generic label names that work across entities (`type`, `status`, `owner`) rather than entity-specific ones, and declare only the ones the app actually filters on. A `type` label whose value is the entity name (`ticket`, `user`, …) gives you a GSI listing per entity type as an alternative access path when you need something other than key order.

### Why one collection

- **It matches how the platform is built.** Single-table design keeps related data co-located and readable in one round trip. A collection is one partition key in a table that is already shared by every workspace, so "one collection per entity" buys no schema, index, or isolation benefit — it only fragments the data across partition keys you then have to provision and discover separately.
- **Transactions and batch operations stay natural.** `transactWrite` across a ticket and its activity row, or `batchGetItem` for a ticket plus its assignee, address one collection with different key prefixes.
- **Provisioning collapses to one `createCollection`.** The migration runner creates one collection instead of N, and there is no "which of the six collections is missing in this workspace" drift (see [collection-migrations.md](collection-migrations.md)). The `$meta` manifest it writes is the single place that says what the collection contains.
- **Collection budget.** The API reference lists a per-workspace collection limit (100, plan-configurable). Even where it is not binding, an app that burns six slots for one logical database is waste.

### Capacity model — what one collection carries

A collection is one DynamoDB partition key, so it inherits DynamoDB's per-partition physics. Design against these numbers, not against user counts:

| Fact | Number | Design consequence |
|------|--------|--------------------|
| Partition throughput ceiling | ~**3,000 RCU / 1,000 WCU per second** per partition key | This is a *burst* ceiling. DynamoDB adaptive capacity splits a hot item collection across partitions by key range over time (the table has no LSIs, so splitting is allowed), but it is reactive — a sudden spike still throttles first. |
| Write cost | **1 WCU per KB written**, rounded up, per item | A 4 KB item costs 4 WCU per `putItem`/`updateItem`. Item size, not write count, is usually what burns the budget. |
| Read cost | **0.5 RCU per 4 KB** (eventually consistent, the platform default) | A 25-item page of 2 KB items is ~7 RCU. Reads almost never bind first. |
| Labels | Each label on an item is an extra GSI write, on a GSI partition that is also per-collection (up to 15 slots) | An item with 5 labels costs ~6× the write capacity of the same item with none; all 15 would be ~16×. The cap is not the budget — the per-write cost is. |
| Single hot item | One item cannot be split — it has its own ~1,000 writes/s ceiling | Counters and "last updated" singletons are per-item hotspots. |
| Item size | **400 KB** max | An entity that embeds a growing array (a ticket holding its comments) will hit this *and* pay full-size WCU on every append. |
| Collection size | No cap (no LSIs) | Size is never a reason to split. |

**Back-of-envelope for the target profile** — an internal app, 100,000 users. Assume a generous 5% concurrently active (5,000), each writing once a minute, 2 KB items with 2 labels: ~85 writes/s × 2 KB × 3 (base + 2 GSIs) ≈ **510 WCU** — half the ceiling, before adaptive capacity does anything. Reads: the same 5,000 users each refreshing a 25-item list every 30 s ≈ 165 queries/s × ~7 RCU ≈ **1,150 RCU**, well under 3,000. One collection carries this with room to spare. What breaks it is design, not user count:

1. **Keep items small; never embed growing arrays.** Children are rows under a hierarchical key (`comment:<ticketId>:<createdAt>`), each written once at its own size. Embedding them in the parent rewrites the whole parent on every append, and `updateItem` replaces nested objects wholesale (see [Nested Object Behavior](#nested-object-behavior)).
2. **Label only what you query by.** Every label is a GSI write. The slot cap is 15, but declare only the two or three labels the UI actually filters on; use key prefixes and ranges for everything else.
3. **Don't funnel every action into one hot item.** A `$counter:ticketNumber` hit per *create* is fine (hundreds/s). A per-request `updateItem` on one shared singleton (a global "last activity" row, a `$meta` you touch from app code) is not — keep per-user state in `user:<id>` rows, and leave `$meta` to the migration runner.

**When you actually outgrow it:** sustained writes approaching ~1,000 KB/s on one collection for minutes at a time (observed as `THROUGHPUT_EXCEEDED` (429) on writes — distinct from `RATE_LIMITED`, which is the platform's per-org request cap). Then shard **by collection** — `ticketing-0` … `ticketing-3` chosen by a hash of the entity id, or move the single hottest entity type into its own collection — and give each shard its own `$meta`. That is the only throughput reason to have more than one collection per app, and the [Queue Pattern](#queue-pattern-using-collections) is the documented instance of it.

**Read-after-write:** because reads are eventually consistent, don't write and immediately `getItem` the same key to "confirm" — use the `{ key, value }` the write returns. Use `conditions` for correctness under concurrency and `transactGet` when a consistent multi-item snapshot matters.

### When multiple collections are justified

- **Security / access isolation** — data that must sit behind a different exposure or permission boundary than the rest of the app.
- **The user explicitly asks** for separate collections.
- **Sustained write throughput near the partition limit** (~1,000 WCU/s on one collection, see the [capacity model](#capacity-model-what-one-collection-carries)) — shard by collection, one `$meta` per shard. Internal apps at ~100k users do not reach this without a design mistake; fix the design (item size, labels, hot singletons) before sharding.
- **Documented infrastructure patterns** — the [Queue Pattern](#queue-pattern-using-collections) keeps a `queue-<name>` collection because a high-churn queue benefits from its own lifecycle and can be sharded across collections for throughput. Standalone workflow state (e.g. a `callback-tokens` collection for one workflow) is already single-collection design.

If none of these apply and you are about to call `createCollection` a second time for the same app, redesign the keys instead.

## Collection Management Actions

### createCollection

Creates a new named collection.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"createCollection"` | Yes | Must be `createCollection` |
| `slug` | string | Yes | Unique slug for the collection. Must match `^[a-z0-9_-]+$` and cannot start with `__` |
| `name` | string | Yes | Display name for the collection |
| `description` | string | No | Optional description |
| `labels` | array of strings | No | Optional labels, up to 15 (`MAX_LABEL_SLOTS`) |

**Example:**
```yaml
configuration:
  options:
    action: createCollection
    slug: callback-tokens
    name: Callback Tokens
    description: Stores callback tokens keyed by thread ID
    labels:
      - email
      - async
```

**Emitted Message:**
```json
{
  "slug": "callback-tokens",
  "name": "Callback Tokens",
  "description": "Stores callback tokens keyed by thread ID",
  "labels": ["email", "async"],
  "createdAt": "2026-03-19T10:00:00.000Z"
}
```

---

### listCollections

Lists all collections with pagination.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"listCollections"` | Yes | Must be `listCollections` |
| `options.startKey` | string | No | Pagination start key from a previous result |
| `options.limit` | number (1-100) | No | Number of collections to return (default: 50) |

**Example:**
```yaml
configuration:
  options:
    action: listCollections
    options:
      limit: 20
```

**Emitted Message:**
```json
{
  "collections": [
    {
      "slug": "callback-tokens",
      "name": "Callback Tokens",
      "description": "Stores callback tokens keyed by thread ID",
      "labels": ["email", "async"],
      "createdAt": "2026-03-19T10:00:00.000Z"
    },
    {
      "slug": "user-preferences",
      "name": "User Preferences",
      "labels": [],
      "createdAt": "2026-03-18T08:30:00.000Z"
    }
  ],
  "lastKey": "user-preferences"
}
```

---

### updateCollection

Updates a collection's name, description, or labels.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"updateCollection"` | Yes | Must be `updateCollection` |
| `slug` | string | Yes | Slug of the collection to update |
| `name` | string | No | New display name |
| `description` | string \| null | No | New description, or `null` to remove |
| `addLabels` | array of strings | No | Labels to add |
| `removeLabels` | array of strings | No | Labels to remove |

**Example:**
```yaml
configuration:
  options:
    action: updateCollection
    slug: callback-tokens
    description: Stores callback tokens for async email workflows
    addLabels:
      - production
    removeLabels:
      - async
```

**Emitted Message:**
```json
{
  "slug": "callback-tokens",
  "name": "Callback Tokens",
  "description": "Stores callback tokens for async email workflows",
  "labels": ["email", "production"],
  "updatedAt": "2026-03-19T12:00:00.000Z"
}
```

---

### deleteCollection

Deletes a collection and all its items.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"deleteCollection"` | Yes | Must be `deleteCollection` |
| `slug` | string | Yes | Slug of the collection to delete |

**Example:**
```yaml
configuration:
  options:
    action: deleteCollection
    slug: old-tokens
```

**Emitted Message:**
```json
{
  "slug": "old-tokens",
  "deletedAt": "2026-03-19T14:00:00.000Z"
}
```

---

## Item Operations

### putItem

Stores a value under a key in a collection. **Create-only by default**: `overwrite` defaults to `false`, so writing a key that already exists fails with `ITEM_ALREADY_EXISTS` (409) — pass `options.overwrite: true` to allow replacement.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"putItem"` | Yes | Must be `putItem` |
| `collection` | string | Yes | The collection to put the item into |
| `key` | string | Yes | The key for the item (max 256 chars, must not contain `#`) |
| `value` | any | Yes | The value to store |
| `labels` | record\<string, string \| null\> | No | Optional labels for the item |
| `ttl` | number \| string \| null | No | Optional time-to-live (seconds as number, ISO-8601 string, or null to remove) |
| `options.overwrite` | boolean | No | Whether to overwrite existing items (default: `false` — an existing key fails with `ITEM_ALREADY_EXISTS`) |
| `options.created` | integer | No | Epoch seconds for created-timestamp integrity check (use with `overwrite: true`) |
| `options.meta` | boolean | No | Whether to include metadata in the result |
| `conditions` | record\<string, unknown\> | No | Conditional expressions for the put operation (applies to data fields only, not labels) |

**Example (simple put):**
```yaml
configuration:
  options:
    action: putItem
    collection: callback-tokens
    key: gmail-${{ msg.send_email.body.threadId }}
    value:
      token: ${{ msg.issue_token.token }}
      createdAt: ${{ Q.now() }}
```

**Example (with labels and TTL):**
```yaml
configuration:
  options:
    action: putItem
    collection: session-data
    key: session-${{ msg.trigger.body.sessionId }}
    value:
      userId: ${{ msg.trigger.body.userId }}
      loginAt: ${{ Q.now() }}
    labels:
      type: user-session
      region: us-east-1
    ttl: 86400
    options:
      meta: true
```

**Emitted Message (without meta):**
```json
{
  "key": "gmail-thread123",
  "value": {
    "token": "cbt_01HQXYZ...",
    "createdAt": "2026-03-19T10:00:00.000Z"
  }
}
```

**Emitted Message (with meta: true):**
```json
{
  "key": "session-abc123",
  "value": {
    "userId": "user_01",
    "loginAt": "2026-03-19T10:00:00.000Z"
  },
  "collection": "session-data",
  "labels": {
    "type": "user-session",
    "region": "us-east-1"
  },
  "createdAt": "2026-03-19T10:00:00.000Z",
  "updatedAt": "2026-03-19T10:00:00.000Z",
  "ttl": "2026-03-20T10:00:00.000Z"
}
```

---

### getItem

Retrieves a single item by key. Returns `null` if the item does not exist.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"getItem"` | Yes | Must be `getItem` |
| `collection` | string | Yes | The collection to get the item from |
| `key` | string | Yes | The key of the item to get |
| `options.meta` | boolean | No | Whether to include metadata in the result |
| `options.label` | string | No | Filter by label |

**Example:**
```yaml
configuration:
  options:
    action: getItem
    collection: callback-tokens
    key: gmail-${{ msg.email_trigger.threadId }}
```

**Emitted Message (item found):**
```json
{
  "key": "gmail-thread123",
  "value": {
    "token": "cbt_01HQXYZ...",
    "createdAt": "2026-03-19T10:00:00.000Z"
  }
}
```

**Emitted Message (item not found):**
```json
null
```

---

### updateItem

Partially updates an existing item's value, labels, TTL, or atomically increments counters.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"updateItem"` | Yes | Must be `updateItem` |
| `collection` | string | Yes | The collection containing the item |
| `key` | string | Yes | The key of the item to update |
| `value` | record\<string, any\> | No | Partial value fields to merge into the existing value |
| `labels` | record\<string, string \| null\> | No | Labels to update (null to remove a label) |
| `ttl` | number \| string \| null | No | Time-to-live to set (null to remove) |
| `options.meta` | boolean | No | Whether to include metadata in the result |
| `options.removeNulls` | boolean | No | Remove fields set to `null` (default: `true`) |
| `conditions` | record\<string, unknown\> | No | Conditional expressions (applies to data fields only, not labels). See [Condition Expressions](#condition-expressions) |
| `atomicCounters` | record\<string, number\> | No | Atomic counter increments to apply to value fields |

**Example (partial update):**
```yaml
configuration:
  options:
    action: updateItem
    collection: user-profiles
    key: user-${{ msg.trigger.body.userId }}
    value:
      lastLogin: ${{ Q.now() }}
      displayName: ${{ msg.trigger.body.newName }}
```

**Example (atomic counter via `atomicCounters`):**
```yaml
configuration:
  options:
    action: updateItem
    collection: rate-limits
    key: api-calls-${{ Q.dateFns.format(Q.now(), 'yyyy-MM-dd-HH') }}
    atomicCounters:
      count: 1
    options:
      meta: true
```

**Example (atomic counter via `$add` shorthand in value):**

You can also use `{ "$add": <number> }` directly in the `value` object for inline atomic increments:

```yaml
configuration:
  options:
    action: updateItem
    collection: stats
    key: page-${{ msg.trigger.body.pageId }}
    value:
      pageViews:
        $add: 1
      dailyCounter:
        $add: -5
      lastVisitor: ${{ msg.trigger.body.userId }}
```

**Emitted Message:**
```json
{
  "key": "api-calls-2026-03-19-14",
  "value": {
    "count": 42
  }
}
```

---

### deleteItem

Deletes one or more items by key.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"deleteItem"` | Yes | Must be `deleteItem` |
| `collection` | string | Yes | The collection to delete items from |
| `keys` | string \| array of strings | Yes | A single key or array of keys to delete (max 25) |
| `conditions` | record\<string, unknown\> | No | Conditional expressions (applies to data fields only, not labels) |

**Example (single key):**
```yaml
configuration:
  options:
    action: deleteItem
    collection: callback-tokens
    keys: gmail-${{ msg.webhook.body.threadId }}
```

**Example (multiple keys):**
```yaml
configuration:
  options:
    action: deleteItem
    collection: temp-data
    keys:
      - key-1
      - key-2
      - key-3
```

**Emitted Message:**
```json
{
  "deleted": 3
}
```

---

### query

Queries items in a collection using an expression with support for pagination, label filtering, and reverse ordering.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"query"` | Yes | Must be `query` |
| `collection` | string | Yes | The collection to query |
| `expression` | string | Yes | The query expression |
| `options.limit` | number (1-1000) | No | Maximum number of items to return (default: 100) |
| `options.startKey` | record\<string, string\> | No | Pagination start key from a previous result's `lastKey` |
| `options.meta` | boolean | No | Whether to include metadata in results |
| `options.label` | string | No | Filter by label |
| `options.reverse` | boolean | No | Whether to reverse the sort order |

**Example:**
```yaml
configuration:
  options:
    action: query
    collection: callback-tokens
    expression: gmail-
    options:
      limit: 50
      meta: true
```

**Emitted Message:**
```json
{
  "items": [
    {
      "key": "gmail-thread123",
      "value": {
        "token": "cbt_01HQXYZ...",
        "createdAt": "2026-03-19T10:00:00.000Z"
      },
      "collection": "callback-tokens",
      "labels": {},
      "createdAt": "2026-03-19T10:00:00.000Z",
      "updatedAt": "2026-03-19T10:00:00.000Z"
    },
    {
      "key": "gmail-thread456",
      "value": {
        "token": "cbt_01HQABC...",
        "createdAt": "2026-03-19T09:30:00.000Z"
      },
      "collection": "callback-tokens",
      "labels": {},
      "createdAt": "2026-03-19T09:30:00.000Z",
      "updatedAt": "2026-03-19T09:30:00.000Z"
    }
  ],
  "lastKey": {
    "pk": "...",
    "sk": "..."
  },
  "count": 2
}
```

---

## Query Expression Syntax

Expressions operate on the **sort key** (item key) within a collection. The collection is always a separate field.

| Pattern | Example | Description |
|---------|---------|-------------|
| Wildcard (all) | `*` | All items in the collection |
| Prefix wildcard | `users:*` | Items whose key starts with `users:` |
| Greater than | `>users:j` | Keys lexicographically greater than `users:j` |
| Greater or equal | `>=orders:2024-01-01` | Keys >= `orders:2024-01-01` |
| Less than | `<users:n` | Keys less than `users:n` |
| Less or equal | `<=orders:2024-06-30` | Keys <= `orders:2024-06-30` |
| Between | `orders:2024-01\|orders:2024-12` | Keys between two values (inclusive) |
| Exact match | `users:jane@doe.com` | Single item with exact key |
| Escaped wildcard | `users:admin\*` | Exact match for key literally ending in `*` |

### Query by Label (GSI)

When `options.label` is specified, the query uses the GSI mapped to that label name. The `expression` then applies to the label value instead of the item key:

```yaml
configuration:
  options:
    action: query
    collection: products
    expression: "electronics*"
    options:
      label: category      # uses the GSI slot mapped to "category"
      limit: 50
```

**Important:** Each query operates on a **single access pattern** — either the primary key or one label. Combining key and label conditions in a single query is not supported (DynamoDB constraint: each `Query` targets one index).

### Pagination

Query results include a `lastKey` object when more items are available. Pass it as `startKey` in the next request:

```yaml
# Page 1
configuration:
  options:
    action: query
    collection: products
    expression: "*"
    options:
      limit: 25

# Page 2 — use lastKey from page 1
configuration:
  options:
    action: query
    collection: products
    expression: "*"
    options:
      limit: 25
      startKey: ${{ msg.page1.lastKey }}
```

`lastKey` is a `Record<string, string>` containing only SK attributes (PK attributes are filtered out for security). For table queries: `{ SK: "item-5" }`. For label (GSI) queries: `{ SK: "item-5", GSI1SK: "groupA" }`.

---

## Condition Expressions

Condition expressions allow write operations (`putItem`, `updateItem`, `deleteItem`) and transaction items to specify preconditions that must be true against the **existing item** before the write proceeds. If any condition evaluates to false, the entire operation fails atomically with `CONDITION_FAILED` (HTTP 409).

**Important:** Conditions apply only to **data fields** (fields in the item's `value` object). Label fields cannot be used in conditions — use label-based queries instead.

### Simple Conditions (Implicit AND)

```yaml
conditions:
  price: "<= 50"
  status: "!= discontinued"
```

### Multiple Conditions on the Same Field

```yaml
conditions:
  price:
    - "> 0"
    - "< 50"
  status: "active"
```

### Compound Logic with AND, OR, NOT

```yaml
conditions:
  AND:
    - price:
        - "> 0"
        - "< 50"
    - OR:
        - status: "active"
        - status: "pending"
```

`NOT` wraps a single condition object. Nesting is supported to arbitrary depth.

### Condition Operators

| Expression | Example | Description |
|-----------|---------|-------------|
| Exact match | `"active"` | Field equals value (implicit `=`) |
| Equality | `"= active"` | Field equals value |
| Not equal | `"!= discontinued"` | Field does not equal value |
| Greater than | `"> 0"` | Numeric/string comparison |
| Greater or equal | `">= 100"` | Numeric/string comparison |
| Less than | `"< 1000"` | Numeric/string comparison |
| Less or equal | `"<= 50.00"` | Numeric/string comparison |
| Between | `"between 1\|100"` | Value is between two bounds (inclusive) |
| In set | `"in active\|pending\|review"` | Value matches one of the listed values |
| Exists | `"exists"` | Attribute exists on the item |
| Not exists | `"not_exists"` | Attribute does not exist on the item |
| Begins with | `"begins_with prod-"` | String attribute starts with prefix |
| Contains | `"contains electronics"` | String contains substring, or set contains value |
| Size comparison | `"size > 5"` | Size of attribute (string length, list/set count) |

### Type Handling

- `"true"` / `"false"` → Booleans
- `"null"` → Null
- Numeric strings → numbers
- All other values → strings
- Reserved keyword collisions: use explicit equality operator to disambiguate (e.g., `"= in progress"`, `"= size large"`)

### Nested Fields

Use dot notation for nested field paths:

```yaml
conditions:
  address.country: "= US"
  metadata.tags: "contains priority"
  settings.notifications: "exists"
```

### Condition Examples in YAML

**Optimistic locking:**
```yaml
configuration:
  options:
    action: updateItem
    collection: products
    key: widget-1
    value:
      price: 34.99
      version: 4
    conditions:
      version: "= 3"
```

**Range check before update:**
```yaml
configuration:
  options:
    action: updateItem
    collection: accounts
    key: account-sender
    atomicCounters:
      balance: -100
    conditions:
      balance: ">= 100"
```

**Complex condition with OR:**
```yaml
configuration:
  options:
    action: putItem
    collection: orders
    key: order-${{ Q.ulid() }}
    value:
      status: processing
    conditions:
      AND:
        - price:
            - ">= 10"
            - "<= 100"
        - OR:
            - status: "active"
            - category: "featured"
    options:
      overwrite: true
```

---

## Concurrent Update Patterns

> **Warning: Do NOT use `getItem` → modify → `putItem` in parallel workflows.** BorgIQ runs downstream actors concurrently. If two actors read the same item, modify it, and write it back, one update will silently overwrite the other.

```
Actor A: getItem → reads { count: 5 }
Actor B: getItem → reads { count: 5 }
Actor A: putItem → writes { count: 6 }     ← A's update succeeds
Actor B: putItem → writes { count: 6 }     ← B overwrites A's update (expected: 7)
```

Use the patterns below instead.

### Pattern 1: Partial Updates with `updateItem`

When parallel actors update **different fields** of the same item, `updateItem` merges safely — each write only touches its own fields.

```yaml
# Actor A: updates field "serviceA_status"
configuration:
  options:
    action: updateItem
    collection: ecs-tasks
    key: task-${{ inputs.taskId }}
    value:
      serviceA_status: ${{ inputs.status }}
      serviceA_updatedAt: ${{ Q.dateFns.formatISO(new Date()) }}
```

```yaml
# Actor B: updates field "serviceB_status" — runs in parallel, no conflict
configuration:
  options:
    action: updateItem
    collection: ecs-tasks
    key: task-${{ inputs.taskId }}
    value:
      serviceB_status: ${{ inputs.status }}
      serviceB_updatedAt: ${{ Q.dateFns.formatISO(new Date()) }}
```

Both writes succeed because they modify different fields. The resulting item contains all fields from both updates.

### Pattern 2: Atomic Counters

For numeric aggregation (counts, totals, balances), use `atomicCounters` or `$add`. DynamoDB guarantees atomic increment even under concurrent writes.

```yaml
# Multiple actors can increment the same counter in parallel — all increments are applied
configuration:
  options:
    action: updateItem
    collection: metrics
    key: daily-${{ Q.dateFns.format(new Date(), 'yyyy-MM-dd') }}
    atomicCounters:
      totalProcessed: 1
      errors: ${{ inputs.hasError ? 1 : 0 }}
```

Equivalent inline syntax using `$add`:

```yaml
configuration:
  options:
    action: updateItem
    collection: metrics
    key: daily-${{ Q.dateFns.format(new Date(), 'yyyy-MM-dd') }}
    value:
      totalProcessed:
        $add: 1
      errors:
        $add: ${{ inputs.hasError ? 1 : 0 }}
```

### Pattern 3: Optimistic Locking with Conditions + Retry

When the full value must be read-modify-written atomically (e.g., appending to an array, merging complex objects), use a `version` field with conditions. On conflict (409), re-read and retry.

**Important:** CollectionActor YAML does not support retry loops. Use DenoActor or PythonActor with `biqApi` for this pattern.

```typescript
// DenoActor: optimistic locking with retry
import type { Request, Response } from "@borgiq/actors";
import { biqApi } from "@borgiq/actors";

// Raw envelope helper — returns { ok, value, error } without unwrapping,
// so the retry loop can inspect ok/error directly.
async function collectionsApi(body: Record<string, unknown>) {
  const res = await biqApi("/collections", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return (await res.json()) as { ok: boolean; value: any; error?: { code: string; message: string } };
}

export default async function receive(req: Request): Promise<Response> {
  const maxRetries = 5;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    // 1. Read current state
    const { value: item } = await collectionsApi({ action: "getItem", collection: "aggregated-status", key: req.inputs.taskId });
    const current = item?.value ?? { statuses: [], version: 0 };

    // 2. Compute update
    const updated = {
      statuses: [...current.statuses, req.inputs.newStatus],
      version: current.version + 1,
    };

    // 3. Write with version condition
    const result = await collectionsApi({
      action: "updateItem",
      collection: "aggregated-status",
      key: req.inputs.taskId,
      value: updated,
      conditions: current.version === 0
        ? { version: "not_exists" }  // First write
        : { version: `= ${current.version}` },
    });

    if (result.ok) return { results: updated };

    // 4. Conflict — retry with fresh data
    if (result.error?.code === "CONDITION_FAILED") continue;
    throw new Error(`Collection API error: ${JSON.stringify(result.error)}`);
  }

  throw new Error(`Failed after ${maxRetries} retries — concurrent contention too high`);
}
```

### Pattern 4: Transactions for Multi-Item Atomics

When multiple items must be updated together atomically (e.g., transfer balance, update parent + children), use `transactWrite` with conditions on each item. See the [Transactions](#transactions) section for full documentation.

```yaml
configuration:
  options:
    action: transactWrite
    items:
      - operation: update
        collection: accounts
        key: account-sender
        atomicCounters:
          balance: -100
        conditions:
          balance: ">= 100"
      - operation: update
        collection: accounts
        key: account-receiver
        atomicCounters:
          balance: 100
```

### Choosing a Pattern

| Scenario | Pattern | Actor |
|----------|---------|-------|
| Parallel updates to **different fields** of the same item | `updateItem` (partial merge) | CollectionActor |
| Parallel numeric aggregation (counts, totals) | `atomicCounters` / `$add` | CollectionActor |
| Read-modify-write with conflict detection + retry | `conditions` + retry loop | DenoActor/PythonActor via `biqApi` |
| Multi-item atomic update (all-or-nothing) | `transactWrite` with conditions | CollectionActor |
| Last-write-wins (data loss acceptable) | `putItem` without conditions | CollectionActor |

---

## Batch Operations

### batchGetItem

Retrieves multiple items across one or more collections in a single operation.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"batchGetItem"` | Yes | Must be `batchGetItem` |
| `items` | array of `{collection, key}` | Yes | Items to get, up to 100 |
| `options.meta` | boolean | No | Whether to include metadata in results |

**Example:**
```yaml
configuration:
  options:
    action: batchGetItem
    items:
      - collection: crm
        key: user:001
      - collection: crm
        key: user:002
      - collection: crm
        key: pref:001
    options:
      meta: true
```

**Emitted Message:**
```json
{
  "items": [
    {
      "key": "user:001",
      "value": { "name": "Alice", "email": "alice@example.com" },
      "collection": "crm",
      "labels": {},
      "createdAt": "2026-03-18T08:00:00.000Z",
      "updatedAt": "2026-03-19T10:00:00.000Z"
    },
    null,
    {
      "key": "pref:001",
      "value": { "theme": "dark", "language": "en" },
      "collection": "crm",
      "labels": {},
      "createdAt": "2026-03-18T08:00:00.000Z",
      "updatedAt": "2026-03-18T08:00:00.000Z"
    }
  ]
}
```

Items that are not found are returned as `null` in the corresponding array position.

---

### batchWriteItem

Writes and/or deletes multiple items across one or more collections in a single operation.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"batchWriteItem"` | Yes | Must be `batchWriteItem` |
| `items` | array | Yes | Items to write, up to 25. Each item has: `operation` (`"put"` or `"delete"`), `collection`, `key`, and optionally `value` (required for put), `ttl`, `labels` |
| `options.meta` | boolean | No | Whether to include metadata in results |

**Example:**
```yaml
configuration:
  options:
    action: batchWriteItem
    items:
      - operation: put
        collection: user-profiles
        key: user-001
        value:
          name: Alice
          email: alice@example.com
        labels:
          role: admin
      - operation: put
        collection: user-profiles
        key: user-002
        value:
          name: Bob
          email: bob@example.com
      - operation: delete
        collection: user-profiles
        key: user-old-999
```

**Emitted Message:**
```json
{
  "processed": 3,
  "items": [
    {
      "key": "user-001",
      "value": { "name": "Alice", "email": "alice@example.com" }
    },
    {
      "key": "user-002",
      "value": { "name": "Bob", "email": "bob@example.com" }
    }
  ],
  "deleted": [
    {
      "collection": "user-profiles",
      "key": "user-old-999"
    }
  ]
}
```

---

## Transactions

### transactGet

Retrieves multiple items in a single atomic transaction. All reads are consistent with each other.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"transactGet"` | Yes | Must be `transactGet` |
| `items` | array of `{collection, key}` | Yes | Items to get, up to 100 |
| `options.meta` | boolean | No | Whether to include metadata in results |

**Example:**
```yaml
configuration:
  options:
    action: transactGet
    items:
      - collection: accounts
        key: account-sender
      - collection: accounts
        key: account-receiver
```

**Emitted Message:**
```json
{
  "items": [
    {
      "key": "account-sender",
      "value": { "balance": 500, "name": "Alice" }
    },
    {
      "key": "account-receiver",
      "value": { "balance": 200, "name": "Bob" }
    }
  ]
}
```

Items that are not found are returned as `null` in the corresponding array position.

---

### transactWrite

Writes, updates, deletes, or checks multiple items atomically. The entire transaction succeeds or fails as a unit.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"transactWrite"` | Yes | Must be `transactWrite` |
| `items` | array | Yes | Items to transact, up to 100. Each item has: `operation` (`"put"`, `"update"`, `"delete"`, `"check"`), `collection`, `key`, and optionally `value`, `labels`, `ttl`, `conditions`, `atomicCounters` |
| `options.idempotencyKey` | string | No | Idempotency key to prevent duplicate transactions |

**Example:**
```yaml
configuration:
  options:
    action: transactWrite
    items:
      - operation: update
        collection: accounts
        key: account-sender
        atomicCounters:
          balance: -100
        conditions:
          balance:
            $gte: 100
      - operation: update
        collection: accounts
        key: account-receiver
        atomicCounters:
          balance: 100
      - operation: put
        collection: accounts
        key: transfer:${{ Q.ulid() }}
        value:
          from: account-sender
          to: account-receiver
          amount: 100
          timestamp: ${{ Q.now() }}
    options:
      idempotencyKey: ${{ msg.trigger.body.requestId }}
```

**Emitted Message:**
```json
{
  "processed": 3
}
```

---

## SDK Interface (DenoActor / PythonActor)

Collections can be accessed programmatically from DenoActor code via `biqApi`. There is no dedicated `collections` SDK yet — use the REST API directly through the `biqApi` helper:

### API Helper Pattern

All collection operations go through `POST /collections` with an `action` field in the request body. The HTTP response is always `{ ok: boolean, value: T, error?: { code, message } }`, but `T` varies per action:

| Action | Return type (`T`) |
|--------|------------------|
| `createCollection` | `{ slug, name, description?, labels, createdAt }` |
| `listCollections` | `{ collections: [{ slug, name, description?, labels, createdAt }], lastKey? }` |
| `updateCollection` | `{ slug, name, description?, labels, updatedAt }` |
| `deleteCollection` | `{ slug, deletedAt }` |
| `putItem` | `{ key, value }` (+ `collection, labels, createdAt, updatedAt, ttl` when `meta: true`) |
| `getItem` | `{ key, value }` (+ meta fields) **or `null` if not found** |
| `updateItem` | `{ key, value }` (+ meta fields) |
| `deleteItem` | `{ deleted: number }` |
| `query` | `{ items: [{ key, value, ...meta? }], count, lastKey? }` |
| `batchGetItem` | `{ items: [{ key, value, ...meta? } \| null] }` |
| `batchWriteItem` | `{ processed, items?, deleted? }` |
| `transactGet` | `{ items: [{ key, value, ...meta? } \| null] }` |
| `transactWrite` | `{ processed }` |

```typescript
import { biqApi } from "@borgiq/actors";

// ---- Shared result types ----

/** Metadata for a collection (returned by create/update/list). */
type CollectionMeta = {
  slug: string;
  name: string;
  description?: string;
  labels: string[];
  createdAt: string;
  updatedAt?: string;
};

/** An item envelope. `V` is the item's `value` shape. Meta fields present only with `options.meta: true`. */
type CollectionItem<V = unknown> = {
  key: string;
  value: V;
  collection?: string;
  labels?: Record<string, string | null>;
  createdAt?: string;
  updatedAt?: string;
  ttl?: string;
};

// ---- Per-action result types ----

type CreateCollectionResult = CollectionMeta;
type ListCollectionsResult  = { collections: CollectionMeta[]; lastKey?: string };
type UpdateCollectionResult = CollectionMeta;
type DeleteCollectionResult = { slug: string; deletedAt: string };

type PutItemResult<V = unknown>    = CollectionItem<V>;
type GetItemResult<V = unknown>    = CollectionItem<V> | null;
type UpdateItemResult<V = unknown> = CollectionItem<V>;
type DeleteItemResult              = { deleted: number };

type QueryResult<V = unknown> = {
  items: CollectionItem<V>[];
  count: number;
  lastKey?: Record<string, string>;
};

type BatchGetItemResult<V = unknown> = { items: (CollectionItem<V> | null)[] };
type BatchWriteItemResult<V = unknown> = {
  processed: number;
  items?: CollectionItem<V>[];
  deleted?: Array<{ collection: string; key: string }>;
};
type TransactGetResult<V = unknown> = { items: (CollectionItem<V> | null)[] };
type TransactWriteResult            = { processed: number };

// ---- Helper ----

async function collectionsApi<T = unknown>(body: Record<string, unknown>): Promise<T> {
  const res = await biqApi("/collections", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const json = (await res.json()) as { ok: boolean; value: T; error?: { code: string; message: string } };
  if (!json.ok) {
    const err = new Error(json.error?.message || "Collection action failed");
    (err as any).code = json.error?.code;
    throw err;
  }
  return json.value;
}
```

The `biqApi` helper automatically handles authentication and tenant scoping. The `collectionsApi` wrapper unwraps `json.value` so you get the action-specific type directly. **Pass the matching result type on each call** so callers get proper typing:

```typescript
// Generic (untyped) — returns `unknown`
await collectionsApi({ action: "deleteItem", collection: "products", keys: "k1" });

// Typed — returns the action-specific shape
const list    = await collectionsApi<ListCollectionsResult>({ action: "listCollections" });
const product = await collectionsApi<GetItemResult<{ name: string; price: number }>>({
  action: "getItem", collection: "products", key: "widget-1",
});
const page    = await collectionsApi<QueryResult<{ name: string; price: number }>>({
  action: "query", collection: "products", expression: "widget:*", options: { limit: 25 },
});
const del     = await collectionsApi<DeleteItemResult>({
  action: "deleteItem", collection: "products", keys: "widget-1",
});

// `product` is typed as { key; value: { name; price } } | null
// `page.items[0].value.name` is a string, `page.count` is a number, etc.
```

### Collection Management

```typescript
// Create a collection with named labels
await collectionsApi({
  action: "createCollection",
  slug: "products",
  name: "Products",
  description: "Product catalog",
  labels: ["category", "status", "brand"],
});

// List all collections
const list = await collectionsApi({ action: "listCollections", options: { limit: 50 } });

// Update collection — add and remove labels
await collectionsApi({
  action: "updateCollection",
  slug: "products",
  name: "Product Catalog",
  addLabels: ["priceRange"],
  removeLabels: ["brand"],
});

// Delete a collection (multi-phase: mark → background cleanup → registry removal)
await collectionsApi({ action: "deleteCollection", slug: "products" });
```

### Item Operations

```typescript
// putItem — create-only by default (overwrite defaults to false; an existing key throws ITEM_ALREADY_EXISTS)
await collectionsApi({
  action: "putItem",
  collection: "products",
  key: "widget-1",
  value: { name: "Widget Pro", price: 29.99 },
  labels: { category: "electronics", status: "active" },
  options: { meta: true },
});

// putItem — overwrite existing
await collectionsApi({
  action: "putItem",
  collection: "products",
  key: "widget-1",
  value: { name: "Widget Pro v2", price: 34.99 },
  labels: { category: "electronics", status: "active" },
  options: { overwrite: true, meta: true, ttl: 86400 },
});

// getItem
const item = await collectionsApi({ action: "getItem", collection: "products", key: "widget-1", options: { meta: true } });

// updateItem — partial update
await collectionsApi({
  action: "updateItem",
  collection: "products",
  key: "widget-1",
  value: { price: 39.99, updatedBy: "alice@acme.com" },
  labels: { status: "sale" },
});

// updateItem — atomic counter via $add shorthand
await collectionsApi({
  action: "updateItem",
  collection: "metrics",
  key: "metric:views:R001",
  value: { count: { $add: 1 } },
});

// deleteItem — single key
await collectionsApi({ action: "deleteItem", collection: "products", keys: "widget-1" });

// deleteItem — multiple keys
await collectionsApi({ action: "deleteItem", collection: "products", keys: ["widget-1", "widget-2", "widget-3"] });
```

### Query

```typescript
// All items in a collection
const result = await collectionsApi({ action: "query", collection: "products", expression: "*" });

// Prefix match
const widgets = await collectionsApi({
  action: "query",
  collection: "products",
  expression: "widget*",
  options: { limit: 10, reverse: true },
});

// Range query
const recent = await collectionsApi({
  action: "query",
  collection: "orders",
  expression: ">=2024-01-01",
  options: { limit: 50 },
});

// Query by label (uses GSI)
const electronics = await collectionsApi({
  action: "query",
  collection: "products",
  expression: "electronics*",
  options: { label: "category", limit: 50 },
});

// Pagination
const page1 = await collectionsApi({ action: "query", collection: "products", expression: "*", options: { limit: 25 } });
const page2 = await collectionsApi({ action: "query", collection: "products", expression: "*", options: { limit: 25, startKey: page1.lastKey } });
```

### Batch Operations

```typescript
// batchWriteItem — put and delete up to 25 items
await collectionsApi({
  action: "batchWriteItem",
  items: [
    { operation: "put", collection: "products", key: "widget-1", value: { name: "Widget" }, labels: { category: "electronics" } },
    { operation: "put", collection: "products", key: "widget-2", value: { name: "Gadget" } },
    { operation: "delete", collection: "products", key: "old-item" },
  ],
});

// batchGetItem — get up to 100 items (mixed entity types via key prefixes)
const results = await collectionsApi({
  action: "batchGetItem",
  items: [
    { collection: "shop", key: "product:widget-1" },
    { collection: "shop", key: "user:alice" },
  ],
  options: { meta: true },
});
```

### Transactions

```typescript
// Atomic transfer with condition check
await collectionsApi({
  action: "transactWrite",
  items: [
    {
      operation: "update",
      collection: "accounts",
      key: "account:alice",
      value: { balance: { $add: -50 } },
      conditions: { balance: ">= 50" },
    },
    {
      operation: "update",
      collection: "accounts",
      key: "account:bob",
      value: { balance: { $add: 50 } },
    },
    {
      operation: "put",
      collection: "accounts",
      key: "txn:2025-01-15_001",
      value: { from: "alice", to: "bob", amount: 50 },
    },
  ],
  options: { idempotencyKey: "txn-abc-123" },
});

// Condition check (assert without modifying) — "check" operation only in transactWrite
await collectionsApi({
  action: "transactWrite",
  items: [
    {
      operation: "check",
      collection: "orders",
      key: "order-9321",
      conditions: { status: "in pending|processing" },
    },
    {
      operation: "update",
      collection: "orders",
      key: "order-9321",
      value: { status: "shipped", shippedAt: new Date().toISOString() },
    },
  ],
});

// Atomic read — up to 100 items with serializable isolation
const result = await collectionsApi({
  action: "transactGet",
  items: [
    { collection: "accounts", key: "account:alice" },
    { collection: "accounts", key: "account:bob" },
  ],
  options: { meta: true },
});
```

---

## Response Format Reference

Different collection operations return different response shapes. This is critical when accessing results in downstream actors via `msg.<msgVar>`.

### Response Shape Summary

| Action | Response Shape | Top-level Fields |
|--------|---------------|-----------------|
| `createCollection` | Object | `slug`, `name`, `description?`, `labels`, `createdAt` |
| `listCollections` | Object with array | `collections[]`, `lastKey?` |
| `updateCollection` | Object | `slug`, `name`, `description?`, `labels`, `updatedAt` |
| `deleteCollection` | Object | `slug`, `deletedAt` |
| `putItem` | Object | `key`, `value`, + meta fields when `meta: true` |
| `getItem` | Object **or `null`** | `key`, `value`, + meta fields when `meta: true`; **entire response is `null` if not found** |
| `updateItem` | Object | `key`, `value`, + meta fields when `meta: true` |
| `deleteItem` | Object | `deleted` (count) |
| `query` | Object with array | `items[]`, `count`, `lastKey?` |
| `batchGetItem` | Object with array | `items[]` (nulls for missing items) |
| `batchWriteItem` | Object with arrays | `processed`, `items[]?`, `deleted[]?` |
| `transactGet` | Object with array | `items[]` (nulls for missing items) |
| `transactWrite` | Object | `processed` |

### Downstream Access Patterns

When a CollectionActor has `msgVar: store_item`, access its result as `msg.store_item.<field>`:

**Single item operations** (`putItem`, `getItem`, `updateItem`):
```yaml
# Access the stored/retrieved value
token: ${{ msg.store_item.value.token }}
itemKey: ${{ msg.store_item.key }}

# With meta: true, also available:
created: ${{ msg.store_item.createdAt }}
updated: ${{ msg.store_item.updatedAt }}
```

**getItem null check** (returns `null` when item not found):
```yaml
# In a RouterActor, check if the item exists
Found: ${{ !Q.isNil(msg.get_item) }}
Not Found: ${{ Q.isNil(msg.get_item) }}

# Safe access with optional chaining
token: ${{ msg.get_item?.value?.token }}
```

**query** (returns `items` array):
```yaml
# Access query results
firstItem: ${{ msg.query_results.items[0].value }}
totalCount: ${{ msg.query_results.count }}
hasMore: ${{ !Q.isNil(msg.query_results.lastKey) }}

# Pagination — pass lastKey to next query
startKey: ${{ msg.query_results.lastKey }}
```

**listCollections** (returns `collections` array):
```yaml
# Access collection list
firstSlug: ${{ msg.list_result.collections[0].slug }}
hasMore: ${{ !Q.isNil(msg.list_result.lastKey) }}
```

**deleteItem** (returns count only):
```yaml
deletedCount: ${{ msg.delete_result.deleted }}
```

**batchGetItem / transactGet** (returns `items` array, `null` for missing):
```yaml
firstItem: ${{ msg.batch_result.items[0]?.value }}
secondMissing: ${{ Q.isNil(msg.batch_result.items[1]) }}
```

**batchWriteItem** (separate arrays for puts and deletes):
```yaml
totalProcessed: ${{ msg.batch_write.processed }}
putResults: ${{ msg.batch_write.items }}
deleteResults: ${{ msg.batch_write.deleted }}
```

**transactWrite** (count only):
```yaml
processed: ${{ msg.transfer.processed }}
```

### SDK Response Wrapper

When using the REST API from DenoActor/PythonActor, the raw HTTP response wraps the result in `{ ok, value, error? }`. The `value` field contains the shapes described above:

```typescript
const result = await collectionsApi({ action: "getItem", collection: "products", key: "widget-1" });
// result is the unwrapped value: { key: "widget-1", value: { name: "Widget Pro", price: 29.99 } }
// or null if not found

const queryResult = await collectionsApi({ action: "query", collection: "products", expression: "*" });
// queryResult is: { items: [...], count: 5, lastKey?: {...} }

const listResult = await collectionsApi({ action: "listCollections" });
// listResult is: { collections: [...], lastKey?: "..." }
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_KEY` | 400 | Key format is invalid or contains `#` |
| `INVALID_ACTION` | 400 | Unknown action |
| `INVALID_EXPRESSION` | 400 | Malformed query expression |
| `INVALID_LABEL` | 400 | Label name not defined in collection schema |
| `INVALID_COLLECTION_SLUG` | 400 | Collection slug format is invalid |
| `BATCH_LIMIT_EXCEEDED` | 400 | More than 25 items in batch write or 100 in batch get |
| `QUERY_LIMIT_EXCEEDED` | 400 | Limit exceeds 1000 |
| `LABEL_LIMIT_EXCEEDED` | 400 | Adding labels would exceed 15 active labels (`MAX_LABEL_SLOTS`). A collection created before the limit was raised from 5 keeps its original slot count until an operator runs the widen migration — hitting this at 5 on an older collection means that migration has not run yet |
| `LABEL_NOT_FOUND` | 400 | Label name does not exist in collection |
| `LABEL_DELETING` | 409 | Label is already being deleted |
| `COLLECTION_NOT_FOUND` | 404 | Collection does not exist in the registry |
| `COLLECTION_ALREADY_EXISTS` | 409 | Collection slug already registered |
| `COLLECTION_DELETING` | 409 | Collection is being deleted |
| `CONDITION_FAILED` | 409 | Conditional write check failed |
| `ITEM_ALREADY_EXISTS` | 409 | `putItem` with `overwrite: false` (the default) and item exists |
| `ITEM_DOES_NOT_EXIST` | 404 | Item referenced does not exist |
| `CREATED_MISMATCH` | 409 | Created timestamp integrity check failed |
| `TRANSACTION_FAILED` | 409 | One or more transaction items failed |
| `TRANSACTION_CONFLICT` | 409 | Concurrent transaction conflict |
| `TRANSACTION_LIMIT_EXCEEDED` | 400 | More than 100 items in a transaction |
| `TRANSACTION_DUPLICATE_ITEM` | 400 | Same collection+key appears more than once in a transaction |
| `RATE_LIMITED` | 429 | Too many requests for this org/workspace |
| `THROUGHPUT_EXCEEDED` | 429 | DynamoDB throttled the partition (a collection's per-partition capacity, see the [capacity model](#capacity-model-what-one-collection-carries)); retry after a brief delay |
| `RESULT_TOO_LARGE` | 413 | Query result exceeds 1MB |

---

## Input Validation Constraints

| Field | Constraint |
|-------|-----------|
| Collection slug | 1-128 bytes, regex `/^[a-z0-9_-]+$/`, must not start with `__` |
| Item key | 1-256 bytes (UTF-8), any characters except `#` |
| Label name | 1-64 chars, regex `/^[a-zA-Z0-9_-]+$/` |
| Label value | Any string or `null` |
| Labels per collection | Max 15 (`MAX_LABEL_SLOTS`; one GSI per slot, `GSI-L1`…`GSI-L15`) |
| Query limit | 1-1000 (default 100) |
| Batch get size | Max 100 items |
| Batch write size | Max 25 items |
| Transaction size | Max 100 items |
| Transaction data | Max 4 MB aggregate |
| Max conditions per operation | 20 |
| Max item size | 400 KB (DynamoDB limit) |
| Idempotency key | Max 36 chars, 10-minute window |
| Max collections per workspace | 100 (configurable per plan) |

---

## Queue Pattern (using Collections)

CollectionActor supports queue semantics by leveraging DynamoDB's lexicographic key ordering, conditional writes, and labels for status tracking.

### Collection Design

- **Collection name:** `queue-{name}` (e.g., `queue-email-notifications`)
- **Key format:** `{priority}:{timestamp}:{ulid}` — priority prefix enables priority queues (`0` = high, `1` = normal, `2` = low), timestamp ensures FIFO within priority, ULID guarantees uniqueness
  - Example: `1:2025-03-20T10:30:00.000Z:01HQXYZ`
- **Labels:** `status` (pending/processing/completed/failed/dead), `consumer` (which worker claimed it), `type` (message type for routing)
- **Value structure:**

```json
{
  "payload": { "..." },
  "enqueuedAt": "2025-03-20T10:30:00.000Z",
  "attempts": 0,
  "maxAttempts": 3,
  "claimedAt": null,
  "timeoutAt": null,
  "completedAt": null,
  "error": null
}
```

### Enqueue

Use `putItem` with `overwrite: false` — the ULID in the key guarantees uniqueness:

```yaml
actor:
  type: CollectionActor
  options:
    action: putItem
    collection: queue-emails
    key: "1:${{ new Date().toISOString() }}:${{ crypto.randomUUID().replace(/-/g, '').substring(0, 26) }}"
    value:
      payload: ${{ msg }}
      enqueuedAt: ${{ new Date().toISOString() }}
      attempts: 0
      maxAttempts: 3
      claimedAt: null
      timeoutAt: null
      completedAt: null
      error: null
    labels:
      status: pending
      type: welcome-email
    options:
      overwrite: false
```

### Dequeue (Claim)

No atomic "pop" — use a two-step **query + conditional update**:

1. **Query** by label `status=pending` (with `limit: 1`) to find the next message
2. **updateItem** with condition to atomically claim it — if another worker already claimed it, the condition fails (`CONDITION_FAILED`) and you retry with the next message

```yaml
# Step 1: Query for pending messages
actor:
  type: CollectionActor
  options:
    action: query
    collection: queue-emails
    expression: "*"
    label: status=pending
    limit: 1

# Step 2: Claim the message with conditional update
actor:
  type: CollectionActor
  options:
    action: updateItem
    collection: queue-emails
    key: ${{ msg.items[0].key }}
    value:
      claimedAt: ${{ new Date().toISOString() }}
      timeoutAt: ${{ new Date(Date.now() + 300000).toISOString() }}
      attempts:
        "$add": 1
    labels:
      status: processing
      consumer: ${{ actor.id }}
    condition:
      claimedAt: not_exists
```

### Complete

```yaml
actor:
  type: CollectionActor
  options:
    action: updateItem
    collection: queue-emails
    key: ${{ msg.key }}
    value:
      completedAt: ${{ new Date().toISOString() }}
    labels:
      status: completed
    condition:
      claimedAt: exists
```

### Fail + Retry / Dead Letter

Check the attempt count — either re-enqueue (reset to pending) or dead-letter:

```yaml
# Retry (attempts < maxAttempts) — release claim, reset to pending
actor:
  type: CollectionActor
  options:
    action: updateItem
    collection: queue-emails
    key: ${{ msg.key }}
    value:
      claimedAt: null
      timeoutAt: null
      error: ${{ msg.errorMessage }}
    labels:
      status: pending
      consumer: ""
    condition:
      status: processing

# Dead-letter (attempts >= maxAttempts)
actor:
  type: CollectionActor
  options:
    action: updateItem
    collection: queue-emails
    key: ${{ msg.key }}
    value:
      error: ${{ msg.errorMessage }}
    labels:
      status: dead
    condition:
      status: processing
```

### Visibility Timeout Reaper

A scheduled workflow that reclaims stale `processing` messages whose timeout has expired:

```yaml
# ScheduledTrigger runs every 5 minutes
# Step 1: Query processing messages
actor:
  type: CollectionActor
  options:
    action: query
    collection: queue-emails
    expression: "*"
    label: status=processing
    limit: 50

# Step 2: For each stale message (timeoutAt < now), reset to pending
# Use a DenoActor to check timeoutAt and conditionally update
actor:
  type: CollectionActor
  options:
    action: updateItem
    collection: queue-emails
    key: ${{ msg.key }}
    value:
      claimedAt: null
      timeoutAt: null
    labels:
      status: pending
      consumer: ""
    condition:
      claimedAt: exists
```

### When This Works Well

This pattern fits moderate-throughput background job queues — email sending, webhook delivery, report generation, or async pipeline stages. For millions of messages per second or sub-millisecond dequeue latency, use a dedicated message broker instead.

### Queue Tradeoffs

| Concern | Impact | Mitigation |
|---|---|---|
| **GSI eventual consistency** | A just-enqueued message might not appear in a label query for a few hundred milliseconds | Acceptable for most workloads; not suitable for sub-100ms latency requirements |
| **No atomic pop** | Two workers can query the same message; one will win the conditional update, the other retries | The retry loop is cheap — conditional writes are fast |
| **Hot partition** | A single high-volume queue concentrates writes on one PK | Shard across multiple collections (`queue-emails-0` through `queue-emails-3`) and round-robin consumers |
| **Completed message cleanup** | Completed messages accumulate | Use TTL on completion (`ttl: 86400`) or a periodic cleanup job |
| **Ordering guarantees** | FIFO within a priority tier, but the claim pattern means strict ordering isn't guaranteed under concurrency | If strict ordering matters, use a single consumer or add sequence numbers with conditional checks |

---

## DynamoDB Mapping Reference

Each CollectionActor action maps to a specific DynamoDB operation. Understanding these mappings is critical for predicting behavior, especially around nested objects and concurrent updates.

### Action → DynamoDB Operation

| Action | DynamoDB Command | Behavior |
|--------|------------------|----------|
| `putItem` | `PutCommand` | **Full item replacement.** Overwrites the entire item including all fields. |
| `getItem` | `GetCommand` (or `QueryCommand` if label specified) | **Eventually consistent read** (DynamoDB default; the platform does not set `ConsistentRead`). Returns the full item or null. |
| `updateItem` | `UpdateCommand` with `UpdateExpression` | **Shallow field-level merge.** Only specified top-level fields are updated; unmentioned fields are preserved. |
| `deleteItem` (single key) | `DeleteCommand` | Deletes one item. Supports conditions. |
| `deleteItem` (multiple keys) | `BatchWriteCommand` | Deletes up to 25 items per batch. **No conditions support.** |
| `query` | `QueryCommand` | Reads items by key prefix, range, or exact match. Supports pagination. |
| `batchGetItem` | `BatchGetCommand` | Reads up to 100 items in one call. Auto-chunks at 100. |
| `batchWriteItem` | `BatchWriteCommand` | Writes up to 25 items per batch (put or delete). **No conditions, no atomic counters.** |
| `transactWrite` | `TransactWriteCommand` | Up to 100 items in one atomic transaction. Supports put, update, delete, and condition checks. |
| `transactGet` | `TransactGetCommand` | Up to 100 items in one consistent read. |

### Nested Object Behavior

> **Critical: `updateItem` does NOT deep-merge nested objects.** It performs a **shallow merge at the top-level fields** of the value. Passing a nested object replaces the entire top-level field.

**Example — nested object is replaced, not merged:**

```
# Stored item value: { address: { city: "Boston", zip: "02101" }, name: "Alice" }

# updateItem with: { value: { address: { city: "NYC" } } }
# Result:          { address: { city: "NYC" }, name: "Alice" }
#                    ↑ zip is GONE — the entire 'address' field was replaced
```

**Example — top-level fields are safely merged:**

```
# Stored item value: { name: "Alice", email: "alice@example.com", score: 10 }

# updateItem with: { value: { name: "Bob" } }
# Result:          { name: "Bob", email: "alice@example.com", score: 10 }
#                    ↑ only 'name' changed, email and score preserved
```

**To update a nested field without losing siblings**, you must either:
1. Read the full object, modify the nested field, and write the entire top-level field back (use optimistic locking — see [Concurrent Update Patterns](#concurrent-update-patterns))
2. Flatten your data structure so each field is top-level (recommended for data that is updated independently)

### `putItem` vs `updateItem`

| Behavior | `putItem` | `updateItem` |
|----------|-----------|--------------|
| DynamoDB operation | `PutCommand` (full replace) | `UpdateCommand` (field-level SET/REMOVE) |
| Unmentioned fields | **Deleted** (full replace) | **Preserved** (only listed fields change) |
| Nested objects | Stored as-is | Replaces entire top-level field |
| Atomic counters | Not supported | Supported (`atomicCounters` and `$add`) |
| Null values | Stored as null | Removed from item (when `removeNulls: true`, which is the default) |
| Default behavior | Fails if item exists (use `overwrite: true` to allow) | Creates item if it doesn't exist |
| Conditions | Supported | Supported |

### Atomic Counter Implementation

Both `atomicCounters` and `$add` translate to DynamoDB's `if_not_exists()` + addition:

```
SET #_data.#d_count = if_not_exists(#_data.#d_count, :zero) + :increment
```

This means:
- If the field doesn't exist, it's initialized to 0 then incremented
- The increment is atomic — concurrent increments from parallel actors all apply correctly
- Negative values work for decrements: `atomicCounters: { balance: -100 }`

### Conditions and Nested Field Access

Conditions **DO support nested field access** via dot notation (unlike `updateItem` which only operates on top-level fields):

```yaml
# This works — checks a nested field
conditions:
  address.city: "= Boston"
  metadata.tags: "contains priority"
  settings.notifications.email: "= true"
```

Each dot-separated segment maps to a DynamoDB expression attribute name:
```
#_data.#f0.#f1 = :v0
# where #f0 = 'address', #f1 = 'city', :v0 = 'Boston'
```

### Batch and Transaction Limits

| Operation | Max items per call | Conditions | Atomic counters |
|-----------|--------------------|------------|-----------------|
| `batchGetItem` | 100 | N/A (read) | N/A |
| `batchWriteItem` | 25 | No | No |
| `transactWrite` | 100 | Yes (per item) | Yes (in update ops) |
| `transactGet` | 100 | N/A (read) | N/A |
| `deleteItem` (batch) | 25 per batch | No | N/A |

### Data Structure Recommendations

To avoid the nested-object replacement problem, design your data with **flat top-level fields** when different parts are updated independently:

```yaml
# BAD — nested object, can't update 'city' without losing 'zip'
value:
  address:
    city: NYC
    zip: "10001"
    state: NY

# GOOD — flat fields, each can be updated independently
value:
  address_city: NYC
  address_zip: "10001"
  address_state: NY
```

For data that is always read and written as a whole (e.g., a config object), nesting is fine since it's always replaced entirely.
