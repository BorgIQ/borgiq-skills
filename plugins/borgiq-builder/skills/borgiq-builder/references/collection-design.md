# Collection Design

How to lay out an app's data in collections: one collection per app, entity key prefixes, the `$meta` manifest,
labels, and what one collection can carry. Read it before creating a collection or choosing keys. Action options are in
[collection-actor.md](collection-actor.md); provisioning is in [collection-migrations.md](collection-migrations.md).

## Contents

- [How collections are stored](#how-collections-are-stored)
- [One collection per app](#one-collection-per-app)
- [Key-prefix modeling](#key-prefix-modeling)
- [The `$` system namespace and the `$meta` manifest](#the--system-namespace-and-the-meta-manifest)
- [Labels](#labels)
- [Capacity model](#capacity-model)
- [When multiple collections are justified](#when-multiple-collections-are-justified)
- [Collections vs streams](#collections-vs-streams)

## How collections are stored

Every collection of every workspace lives in one shared DynamoDB table. A collection is one **partition key**
(`<org>#<workspace>#<slug>`), built by the platform; an item's `key` is the **sort key**, stored verbatim.

- Keys sort in UTF-8 byte order, so prefix (`user:*`) and range (`>=user:U003`) queries are fast. Design keys
  hierarchically with delimiters (`app:R001:C004`).
- Every query reads one collection. There are no full-table scans.
- An item is `key`, `value` and an optional `labels` map. Nothing validates `value`: a collection has no schema.
- Writes are durable at once; reads are eventually consistent ([semantics](collection-actor.md#semantics)).

## One collection per app

Model **all** of an app's entity types in one collection, separated by key prefixes; never one collection per entity
type. `query { collection: "ticketing", expression: "ticket:*" }` is exactly as fast and as isolated as
`expression: "*"` on a `tt-tickets` collection: both are a single-partition prefix read.

```text
Wrong:  tt-tickets  tt-users  tt-labels  tt-comments  tt-activity  tt-meta

Right:  Collection ticketing (rows in the order the UI lists them)
          $meta                            manifest: lists every entity prefix; always the first row
          $migration:<id>                  migration ledger
          $counter:ticketNumber            atomic counters
          activity:<ticketId>:<at>         activity, sorted under its ticket
          comment:<ticketId>:<createdAt>   comments, sorted under their ticket
          label:<id>                       label records
          ticket:<id>                      ticket records
          user:<id>                        user records
```

A collection per entity buys no schema, index or isolation benefit, since a collection is already one partition key in a
shared table. One collection keeps `transactWrite` and `batchGetItem` across entities natural (a ticket and its
activity row), makes provisioning one `createCollection`, and lets `$meta` say in one place what the app stores.

## Key-prefix modeling

- `<entity>:<id>` for top-level entities: `ticket:01HQX...`, `user:demo-maya`, `label:bug`.
- Hierarchical keys for children: `comment:<ticketId>:<createdAt>` sorts a ticket's comments together in time order,
  so one prefix query (`comment:ticket-42:*`) fetches them with no index.
- `config:` for app-level lookup rows (settings, status enums).
- **Query by entity prefix, never `*`.** In a shared collection `*` returns every entity type; `ticket:*` is
  `SELECT * FROM tickets`.
- Entity prefixes are lowercase words and never start with `$`.

## The `$` system namespace and the `$meta` manifest

The Collections UI, like a `query` with `expression: "*"`, lists items in key byte order one page at a time, so page
one of a ticketing collection is all `activity:*` rows. **Every app collection therefore has a `$meta` manifest row,
and every system row uses the `$` prefix.** `$` sorts before digits and letters, so these rows always come first; it
is safe in YAML plain scalars, JS template literals, Python and query expressions (`$*` lists the system rows). `#` is
not allowed in keys, `_` sorts after digits and uppercase, and most other symbols are YAML-special or query operators.
(DynamoDB's advice against `$` concerns attribute names; an item key is an attribute value.)

| Key | Purpose | Written by |
|---|---|---|
| `$meta` | **Required.** App name, applied `schemaVersion`, and the `entities` index of every key prefix | The migration runner, at the end of **every** invoke, with `options.overwrite: true` |
| `$migration:<id>` | Migration ledger, one row per applied migration | The migration runner |
| `$counter:<name>` | Atomic counters (`updateItem` + `atomicCounters`) | Seeded at 0 by the migration runner (`updateItem` cannot create it); incremented by app code |
| `$<anything-else>` | Operational singletons (locks, cursors, cached config) | App code |

`$` rows never match an entity prefix query, so they cost nothing at read time.

```json
{
  "app": "ticketing",
  "schemaVersion": 3,
  "entities": {
    "ticket":  { "prefix": "ticket:",  "key": "ticket:<ulid>", "description": "Tickets" },
    "user":    { "prefix": "user:",    "key": "user:<id>",     "description": "Users and demo users" },
    "comment": { "prefix": "comment:", "key": "comment:<ticketId>:<createdAt>", "description": "Comments, sorted under their ticket", "parent": "ticket" }
  },
  "system": { "$migration:": "Applied migration ledger", "$counter:": "Atomic counters (ticketNumber)" },
  "labels": { "type": "entity name (ticket, user, …)", "status": "ticket status", "owner": "assignee id" },
  "updatedAt": "2026-08-20T10:00:00.000Z"
}
```

- **Derive `$meta` from code; users never edit it.** The runner rewrites it from an `ENTITIES` constant on every invoke.
  It is the one seed-style write where `overwrite: true` is right; seed data rows stay create-only.
- **A new key prefix means updating `ENTITIES` and re-invoking the runner.** A prefix missing from `$meta` is invisible
  to anyone who opens the collection: treat it as a bug.
- **`schemaVersion` is the applied version.** Code that must refuse traffic until migrations run (`MIGRATIONS_PENDING`)
  compares it with the version it was built for; a missing `$meta` means version 0.
- **Keep it small:** prefixes, key patterns, one-line descriptions, label meanings. No counts, no data.

Read any collection the same way: `getItem` `$meta` (the first row in the UI), pick a prefix from `entities`, then
prefix-query it (`ticket:*` in the UI's expression box). In code:
[collection-sdk.md → Enumerate a collection](collection-sdk.md#enumerate-a-collection-from-meta).

## Labels

Labels are a separate `labels` map on an item (`labels: { status: open }`), not fields of `value`. Only labels are
indexed, so a `value` field cannot be queried; conditions test `value` fields, never labels.

- A collection has at most **15 label slots**, shared by all its entity types. Each slot is a Global Secondary Index on
  the shared table, so the cap is fixed.
- Write cost binds before the slot count: every label on an item is an extra index write ([capacity](#capacity-model)).
- Declare labels on the collection (`createCollection` `labels`, `updateCollection` `addLabels`) before items use them.
- Use generic names that work across entities (`type`, `status`, `owner`) and declare only the two or three the app
  filters on. A `type` label holding the entity name gives a per-type listing when key order is not enough.
- Querying: [collection-actor.md → Query by label](collection-actor.md#query-by-label).

## Capacity model

A collection is one partition key and inherits DynamoDB's per-partition limits. Design against these, not user counts:

| Fact | Number | Consequence |
|---|---|---|
| Partition throughput | ~3,000 RCU / 1,000 WCU per second | A burst ceiling: adaptive capacity splits a hot key range over time (the table has no LSIs), but a sudden spike throttles first |
| Write cost | 1 WCU per KB written, rounded up, per item | Item size, not write count, burns the budget |
| Read cost | 0.5 RCU per 4 KB (eventually consistent) | A 25-item page of 2 KB items is ~7 RCU; reads rarely bind |
| Labels | One extra index write per label on the item | 5 labels cost ~6× the writes of none; 15 cost ~16× |
| One item | ~1,000 writes/s; never split | Counters and "last updated" singletons are hotspots |
| Item size | 400 KB max | An embedded growing array hits it and pays full-size WCU per append |
| Collection size | No cap | Size is never a reason to split |

An internal app of 100,000 users (5% active, each writing a 2 KB item with 2 labels per minute, refreshing a 25-item
list every 30 s) needs ~510 WCU and ~1,150 RCU: one collection carries it. Design breaks it, not user count:

1. **Keep items small; never embed growing arrays.** Store children as rows under a hierarchical key. Embedding
   rewrites the parent on every append, and `updateItem` replaces nested objects whole.
2. **Label only what you query by.** Use key prefixes and ranges for everything else.
3. **Don't funnel every action into one item.** A `$counter:ticketNumber` hit per create is fine (hundreds/s); a
   per-request `updateItem` on a shared singleton (a global "last activity" row, or `$meta` from app code) is not.
   Keep per-user state in `user:<id>` rows.

A collection is outgrown only by sustained writes near ~1,000 KB/s for minutes, seen as `THROUGHPUT_EXCEEDED` (429).
Then shard by collection (`ticketing-0` … `ticketing-3` by a hash of the entity id) or move the hottest entity type
into its own collection, each shard with its own `$meta`.

## When multiple collections are justified

- A security or access boundary the rest of the app must not share.
- The user explicitly asks for separate collections.
- Sustained writes near the partition limit, after fixing item size, labels and hot singletons.
- A high-churn queue: the [queue pattern](collection-actor.md#queue-pattern) keeps its own shardable `queue-<name>`
  collection. State for one workflow (a `callback-tokens` collection) is already single-collection design.

Otherwise, before calling `createCollection` a second time for the same app, redesign the keys.

## Collections vs streams

A collection holds the current value of things. "What happened, in order" (webhook deliveries, audit trails, activity
feeds) and consumers that resume from a cursor belong in a stream, not in `event:<timestamp>` items:
[stream-actor.md → Collections vs streams](stream-actor.md#collections-vs-streams).
