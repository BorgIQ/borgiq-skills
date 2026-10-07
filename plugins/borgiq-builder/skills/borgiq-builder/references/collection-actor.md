# CollectionActor Reference

The CollectionActor is the YAML surface of Collections, the recommended persistent storage for new workflows. This file
holds every action's options and results, query and condition syntax, write semantics, concurrency and queue patterns,
errors and limits. Read [collection-design.md](collection-design.md) before choosing keys,
[collection-migrations.md](collection-migrations.md) to provision, and [collection-sdk.md](collection-sdk.md) to call
the same actions from code.

## Contents

- [Rules](#rules)
- [Configuration](#configuration)
- [Collection actions](#collection-actions)
- [Item actions](#item-actions)
- [Query](#query)
- [Batch and transaction actions](#batch-and-transaction-actions)
- [Conditions](#conditions)
- [Semantics](#semantics)
- [Reading results downstream](#reading-results-downstream)
- [Concurrent updates](#concurrent-updates)
- [Queue pattern](#queue-pattern)
- [Workflow patterns](#workflow-patterns)
- [Errors](#errors)
- [Limits](#limits)

## Rules

- **One collection per app**, entity key prefixes, a `$meta` manifest ([collection-design.md](collection-design.md)).
- **Create collections before use.** Any action on a slug that was never created fails with `COLLECTION_NOT_FOUND`.
  Ship an idempotent migration runner that creates the collection and seeds defaults
  ([collection-migrations.md](collection-migrations.md)).
- **`putItem` is create-only.** An existing key fails with `ITEM_ALREADY_EXISTS` (409) unless `options.overwrite: true`,
  which replaces the whole item.
- **`updateItem` never creates an item.** Setting `value` fields or counters on a missing key fails with
  `ITEM_DOES_NOT_EXIST` (404); `putItem` first.
- **TTL goes in `options.ttl`** on `putItem` and `transactWrite` puts, and top-level `ttl` on `batchWriteItem` items.
  A top-level `ttl` on `putItem` is moved into `options.ttl`, which wins when both are set. On a `transactWrite` item it
  is dropped and the item never expires. `updateItem` cannot set a TTL.
- **`query` needs a non-empty `expression`.** In a shared collection query by entity prefix, never `*`.
- **Condition values are strings** and test `value` fields only, never labels.
- **Use what a write emits** instead of re-reading it: reads are eventually consistent.
- Events in order ("what happened") go to a [StreamActor](stream-actor.md), not `event:<timestamp>` items.

## Configuration

Options live under `configuration.options`; `action` selects the action. The actor has one source port, `SPRTdefault`,
and emits the action's result as `msg.<msgVar>`. Exact schemas:
[typescript/actorSchemas/task/collection/index.md](typescript/actorSchemas/task/collection/index.md) (one module per
action alongside it).

```yaml
type: CollectionActor
version: 1
name: Store Token
msgVar: store_token
sourcePorts:
  - id: SPRTdefault
configuration:
  options:
    action: putItem
    collection: callback-tokens
    key: gmail-${{ msg.send_email.body.threadId }}
    value:
      token: ${{ msg.issue_token.token }}
      createdAt: ${{ Q.now() }}
```

## Collection actions

| Action | Options | Emits |
|---|---|---|
| `createCollection` | `slug` (required; `^[a-z0-9_-]+$`, 1–128 bytes, not starting `__`), `name` (required), `description`, `labels` (label names, ≤ 15) | `{ slug, name, description?, labels, createdAt, updatedAt }` |
| `listCollections` | `options.limit` (1–100, default 100), `options.startKey` (the previous `lastKey`, a slug) | `{ items: [collection], lastKey?, count }`. Collections being deleted are skipped, so a page can hold fewer |
| `updateCollection` | `slug` (required), `name`, `description` (an empty string clears it; `null` is rejected), `addLabels`, `removeLabels` | the collection |
| `deleteCollection` | `slug` (required) | `{ slug, status: "deleting" }` |

- A result's `labels` is the 15 slots in order: `null` is unused, `{ name, deletedAt }` is a label still being removed.
  A removed label's slot stays reserved until its cleanup finishes; an added label takes the first free slot.
- `deleteCollection` marks the collection and a background job deletes its items. Item actions on the slug then fail
  with `COLLECTION_NOT_FOUND`, and re-creating it fails with `COLLECTION_DELETING` until cleanup finishes.

```yaml
configuration:
  options:
    action: createCollection
    slug: ticketing
    name: Ticketing
    labels: [type, status, owner]
```

## Item actions

Every item action takes `collection`, the slug. `putItem`, `getItem`, `updateItem` and `query` also take `options.meta`
(boolean): each item in the result then carries `collection`, `labels`, `createdAt`, `updatedAt` and `ttl` too.

| Action | Option | Type | Default | Meaning |
|---|---|---|---|---|
| `putItem` | `key` | string | required | The item key: 1–256 characters, no `#` |
| | `value` | any | required | Stored as given |
| | `labels` | record of string \| null | — | Label values; each label must be declared on the collection |
| | `options.overwrite` | boolean | `false` | `true` replaces an existing item whole: value, labels, TTL, and `createdAt` unless `options.created` matches |
| | `options.ttl` | number \| string | — | Seconds from now (a number at or above the current epoch time is an absolute epoch timestamp), or an ISO-8601 string |
| | `options.created` | string \| integer | — | With `overwrite: true`, write only if the stored `createdAt` still equals this: the `createdAt` a `meta: true` read returned, unchanged, or the same instant in epoch **milliseconds** (`Date.parse(createdAt)`), never seconds. A match keeps `createdAt`; otherwise `CREATED_MISMATCH`. Ignored without `overwrite` |
| | `conditions` | object | — | [Conditions](#conditions) on the stored item |
| `getItem` | `key` | string | required | Key to read |
| | `options.label` | string | — | Look up by label instead: one item whose value for this label equals `key` |
| `updateItem` | `key` | string | required | An existing item's key |
| | `value` | record | — | Top-level fields to merge. `{ $add: <n> }` increments a number atomically; `null` removes a field |
| | `labels` | record of string \| null | — | Labels to set; `null` removes one |
| | `atomicCounters` | record of number | — | Atomic increments to `value` fields; negative decrements |
| | `options.removeNulls` | boolean | `true` | Remove fields set to `null` |
| | `conditions` | object | — | [Conditions](#conditions) |
| `deleteItem` | `keys` | string \| string[] | required | One key or up to 25 |
| | `conditions` | object | — | Applied only when deleting one key; ignored for several |

| Action | Emits |
|---|---|
| `putItem`, `updateItem` | `{ key, value }` (the whole stored value) |
| `getItem` | `{ key, value }`, or **`null`** when the item does not exist |
| `deleteItem` | `{ deleted: [{ collection, key }] }` for every requested key, including keys that did not exist |

```yaml
configuration:
  options:
    action: putItem
    collection: session-data
    key: session:${{ msg.trigger.body.sessionId }}
    value:
      userId: ${{ msg.trigger.body.userId }}
    labels:
      type: user-session
    options:
      ttl: 86400        # here, not top-level
      meta: true
```

Increment counters with `atomicCounters` or with `$add` inside `value` (the item must exist):

```yaml
configuration:
  options:
    action: updateItem
    collection: stats
    key: page:${{ msg.trigger.body.pageId }}
    value:
      pageViews:
        $add: 1
      lastVisitor: ${{ msg.trigger.body.userId }}
```

## Query

| Option | Type | Default | Meaning |
|---|---|---|---|
| `expression` | string | required | Matches item keys (or the label value with `options.label`); must be non-empty |
| `options.limit` | 1–1000 | 100 | Items per page |
| `options.startKey` | record of string | — | The previous result's `lastKey` |
| `options.label` | string | — | Query this label's index instead of the key |
| `options.reverse` | boolean | `false` | Descending key order |

Emits `{ items: [{ key, value }], count, lastKey? }`; `lastKey` is present when more items remain.

### Query expressions

| Pattern | Example | Matches |
|---|---|---|
| Wildcard | `*` | Every item in the collection |
| Prefix | `users:*` | Keys starting with `users:` |
| Greater / greater or equal | `>users:j`, `>=orders:2024-01-01` | Keys after (or from) the value |
| Less / less or equal | `<users:n`, `<=orders:2024-06-30` | Keys before (or up to) the value |
| Between | `orders:2024-01\|orders:2024-12` | Keys between two values, inclusive |
| Exact | `users:jane@doe.com` | The one item with that key |
| Escaped wildcard | `users:admin\*` | Exact key ending in a literal `*` |

### Query by label

With `options.label`, the query reads the index of that label and `expression` matches the label's **value**. A query
reads one access pattern, the key or one label; key and label conditions cannot be combined.

```yaml
configuration:
  options:
    action: query
    collection: products
    expression: electronics*   # the label value
    options:
      label: category          # the label name
      limit: 50
```

### Pagination

Pass `lastKey` back as `options.startKey: ${{ msg.page1.lastKey }}`. It holds only sort-key attributes: `{ SK }` for a
key query, plus the label index's `GSI<n>SK` for a label query.

## Batch and transaction actions

| Action | Options | Emits |
|---|---|---|
| `batchGetItem` | `items`: up to 100 `{ collection, key }`, across collections; `options.meta` | `{ items }`, in request order, `null` for a missing item |
| `batchWriteItem` | `items`: up to 25 `{ operation: put \| delete, collection, key, value (put), labels, ttl }`; `options.meta` | `{ processed, items?, deleted? }` |
| `transactGet` | `items`: up to 100 `{ collection, key }`; `options.meta` | `{ items, count }`, `null` for a missing item; one consistent snapshot |
| `transactWrite` | `items`: up to 100 `{ operation: put \| update \| delete \| check, collection, key, value, labels, conditions, atomicCounters, options: { ttl, overwrite, created } }`; `options.idempotencyKey` | `{ processed }` |

- A `batchWriteItem` put always replaces an existing item: no create-only check, no `overwrite`, no conditions, no
  atomic counters. Its `ttl` is top-level on each item, in the forms `options.ttl` takes.
- `transactWrite` is all-or-nothing, across collections if needed. A `put` is create-only unless it has
  `options.overwrite: true` or `conditions`; an `update` that sets `value` fields or counters needs an existing item;
  `check` asserts `conditions` without writing. A failure is `TRANSACTION_FAILED` with per-item
  `error.cancellationReasons`. `options.created` on a put works as on `putItem`; its failure is that item's
  `CREATED_MISMATCH`.

```yaml
configuration:
  options:
    action: transactWrite
    items:
      - operation: update
        collection: accounts
        key: account:sender
        atomicCounters:
          balance: -100
        conditions:
          balance: ">= 100"
      - operation: update
        collection: accounts
        key: account:receiver
        atomicCounters:
          balance: 100
      - operation: put
        collection: accounts
        key: transfer:${{ Q.ulid() }}
        value:
          from: account:sender
          to: account:receiver
          amount: 100
    options:
      idempotencyKey: ${{ msg.trigger.body.requestId }}
```

## Conditions

`conditions` on `putItem`, `updateItem`, a single-key `deleteItem` and `transactWrite` items are preconditions on the
**existing item**. If any is false the whole operation fails with `CONDITION_FAILED` (409). On a key with no item every
comparison is false. Conditions test `value` fields only: labels cannot be used.

```yaml
conditions:
  AND:                          # AND and OR take a list, NOT one condition object; they nest to any depth
    - price:                    # several conditions on one field, and several fields, are ANDed
        - "> 0"
        - "< 50"
      address.country: "= US"   # dot paths reach nested fields
    - OR:
        - status: active
        - category: featured
```

A condition object is either several fields (implicitly ANDed) or exactly one `AND`, `OR` or `NOT` key; never mix
the two at one level.

| Expression | Example | True when |
|---|---|---|
| Value, or `= value` | `"active"`, `"= active"` | Field equals the value |
| `!=` | `"!= discontinued"` | Field differs |
| `>`, `>=`, `<`, `<=` | `">= 100"` | Numeric or string comparison |
| `between a\|b` | `"between 1\|100"` | Between the bounds, inclusive |
| `in a\|b\|c` | `"in active\|pending\|review"` | Field equals one of the values |
| `exists`, `not_exists` | `"not_exists"` | Attribute present / absent (a stored `null` counts as present) |
| `begins_with p` | `"begins_with prod-"` | String starts with `p` |
| `contains v` | `"contains electronics"` | String contains `v`, or set contains `v` |
| `size <op> n` | `"size > 5"` | String length or list/set count compares |

Values are strings: `"true"`/`"false"` become booleans, `"null"` null, numeric strings numbers, anything else a string.
An operator needs a space after it (`">= 5"`; `">=5"` fails `INVALID_CONDITION`). Use `=` to disambiguate a value that
starts with an operator word (`"= in progress"`, `"= size large"`).

## Semantics

| | `putItem` | `updateItem` |
|---|---|---|
| Missing item | Creates it | Fails `ITEM_DOES_NOT_EXIST` |
| Existing item | Fails `ITEM_ALREADY_EXISTS`; `overwrite: true` replaces it, deleting unmentioned fields | Changes only the listed top-level fields |
| Nested objects | Stored as given | A nested object replaces the whole top-level field |
| `null` values | Stored | Remove the field (`removeNulls` defaults to `true`) |
| Counters, TTL | TTL via `options.ttl`; no counters | Counters via `atomicCounters` / `$add`; no TTL |

- **`updateItem` merges shallowly.** Stored `{ address: { city: "Boston", zip: "02101" } }` updated with
  `{ address: { city: "NYC" } }` becomes `{ address: { city: "NYC" } }`: `zip` is gone. Flatten fields that change
  independently (`address_city`, `address_zip`), or read, change and write back the whole field under an optimistic
  lock. Data always written whole (a config object) can stay nested.
- **Counters are atomic.** `atomicCounters` and `$add` start a missing field at 0 on an existing item, and every
  concurrent increment applies.
- **Reads are eventually consistent** (`getItem`, `query`, `batchGetItem`): a `getItem` right after a write can return
  the previous version. Use the `{ key, value }` the write emits; use `transactGet` for a consistent multi-item snapshot.
- A multi-key `deleteItem` is a batch: no conditions.
- Each action is one DynamoDB call: `putItem` a Put, `updateItem` an Update (SET/REMOVE on top-level fields), a
  single-key `deleteItem` a Delete, `getItem` a Get (a Query with `options.label`), `query` a Query, `batchGetItem` a
  BatchGet, `batchWriteItem` and a multi-key `deleteItem` a BatchWrite, and the transactions a TransactWrite or
  TransactGet.

## Reading results downstream

A CollectionActor with `msgVar: result` is read as `msg.result.<field>`:

| Result | Expression |
|---|---|
| Stored or read value | `${{ msg.result.value.token }}`, `${{ msg.result.key }}` |
| With `meta: true` | `${{ msg.result.createdAt }}`, `${{ msg.result.updatedAt }}` |
| `getItem` found? (a RouterActor condition) | `${{ !Q.isNil(msg.result) }}`; safe access `${{ msg.result?.value?.token }}` |
| `query` page | `${{ msg.result.items[0].value }}`, `${{ msg.result.count }}`, more: `${{ !Q.isNil(msg.result.lastKey) }}` |
| `listCollections` | `${{ msg.result.items[0].slug }}` |
| `deleteItem` | `${{ msg.result.deleted.length }}` |
| `batchGetItem` / `transactGet` | `${{ msg.result.items[0]?.value }}`, missing: `${{ Q.isNil(msg.result.items[1]) }}` |
| `batchWriteItem` | `${{ msg.result.processed }}`, `${{ msg.result.items }}`, `${{ msg.result.deleted }}` |
| `transactWrite` | `${{ msg.result.processed }}` |

## Concurrent updates

Downstream actors run concurrently. Never `getItem` → modify → `putItem` with `overwrite: true` in parallel branches:
two runs read `{ count: 5 }`, both write `{ count: 6 }`, and one update is lost.

| Scenario | Pattern |
|---|---|
| Parallel writes to **different fields** of one item | `updateItem` of each branch's own fields; create the item before the branches start |
| Parallel counts, totals, balances | `atomicCounters` / `$add` |
| Read-modify-write (append to an array, merge objects) | A `version` field in `conditions`, retried on conflict. YAML has no retry loop: use code ([collection-sdk.md → Optimistic lock](collection-sdk.md#optimistic-lock-with-retry)) |
| Several items all-or-nothing | `transactWrite` with conditions |
| Last write wins (losing data is acceptable) | `putItem` with `options.overwrite: true`, no conditions |

A counter keyed per hour or day does not exist on the period's first write, which fails `ITEM_DOES_NOT_EXIST`. Put a
create-only `putItem` of zeroed fields (`value: { count: 0 }`, `continueOnError: true`) before the increment: once
the item exists it fails harmlessly with `ITEM_ALREADY_EXISTS`.

```yaml
configuration:
  options:
    action: updateItem
    collection: metrics
    key: daily:${{ Q.dateFns.format(Q.now(), 'yyyy-MM-dd') }}
    atomicCounters:
      totalProcessed: 1
      errors: '${{ inputs.hasError ? 1 : 0 }}'
```

## Queue pattern

A job queue for moderate throughput (email sending, webhook delivery, report generation); use a message broker for
millions of messages per second or sub-millisecond dequeues.

- **Collection** `queue-<name>`; **key** `<priority>:<timestamp>:<ulid>` (`0` high, `1` normal, `2` low; timestamp
  gives FIFO within a priority, the ULID uniqueness).
- **Labels:** `status` (`pending`, `processing`, `completed`, `failed`, `dead`), `consumer`, `type`.
- **Value at enqueue:** `payload`, `enqueuedAt`, `attempts: 0`, `maxAttempts`. Never store `claimedAt`, `timeoutAt`,
  `completedAt` or `error` as `null`: `claimedAt: not_exists` treats a stored `null` as existing, so every claim fails.

Each step is a CollectionActor's `configuration.options`; the claim and the releases set `continueOnError: true`, so a
lost race (`CONDITION_FAILED`) does not fail the run.

```yaml
# Enqueue (msgVar: enqueue_job): create-only; the ULID keeps keys unique
action: putItem
collection: queue-emails
key: "1:${{ new Date().toISOString() }}:${{ Q.ulid() }}"
value: { payload: "${{ msg }}", enqueuedAt: "${{ new Date().toISOString() }}", attempts: 0, maxAttempts: 3 }
labels: { status: pending, type: welcome-email }
---
# Claim, step 1 (msgVar: next_job): route on count > 0 before step 2
action: query
collection: queue-emails
expression: pending
options: { label: status, limit: 1 }
---
# Claim, step 2 (msgVar: claim_job): the condition makes exactly one worker win
action: updateItem
collection: queue-emails
key: ${{ msg.next_job.items[0].key }}
value:
  claimedAt: ${{ new Date().toISOString() }}
  timeoutAt: ${{ new Date(Date.now() + 300000).toISOString() }}
  attempts: { $add: 1 }
labels: { status: processing, consumer: "${{ ctx.flowrun.id }}" }
conditions: { claimedAt: not_exists }
---
# Complete
action: updateItem
collection: queue-emails
key: ${{ msg.claim_job.key }}
value: { completedAt: "${{ new Date().toISOString() }}" }
labels: { status: completed }
conditions: { claimedAt: exists }
---
# Retry when attempts < maxAttempts (err.send_email: the failed step, continueOnError: true); null removes a field or label
action: updateItem
collection: queue-emails
key: ${{ msg.claim_job.key }}
value: { claimedAt: null, timeoutAt: null, error: "${{ err.send_email.message }}" }
labels: { status: pending, consumer: null }
conditions: { claimedAt: exists }
# Dead-letter when attempts >= maxAttempts: the same with value { error } and labels { status: dead }
---
# Reaper, on a 5-minute ScheduledTrigger: query label status = processing (limit 50, msgVar in_flight), split
# msg.in_flight.items (msgVar stale, emitKey item), then release each expired claim:
action: updateItem
collection: queue-emails
key: ${{ msg.stale.item.key }}
value: { claimedAt: null, timeoutAt: null }
labels: { status: pending, consumer: null }
conditions: { timeoutAt: "< ${{ new Date().toISOString() }}" }
```

| Concern | Impact | Mitigation |
|---|---|---|
| Index lag | A new message can miss a label query for a few hundred ms | Fine for most work; not for sub-100 ms latency |
| No atomic pop | Two workers can pick the same message; the conditional claim picks one | The retry is cheap |
| Hot partition | One busy queue concentrates writes on one partition key | Shard across `queue-emails-0` … `-3`, round-robin consumers |
| Cleanup | Completed messages accumulate | `updateItem` cannot set a TTL: set `options.ttl` at enqueue that outlasts processing, or delete completed messages on a schedule |
| Ordering | FIFO per priority, but not strict under concurrent claims | One consumer, or sequence numbers with conditional checks |

## Workflow patterns

- **Async email reply:** `SendEmail → IssueCallbackToken → CollectionActor putItem` (token keyed `gmail-<threadId>` in
  `callback-tokens`); on the reply, `EmailTrigger → CollectionActor getItem → RouterActor → NotifyCallbackToken`.
- **Rate limit:** `putItem { count: 0 }` (continueOnError) `→ updateItem atomicCounters → RouterActor` (count over the
  limit?).
- **CRUD API:** a route that only reads or writes a collection and returns JSON fits one webhook-enabled
  UniversalTriggerActor ([Universal vs Webhook Trigger](../SKILL.md#universal-trigger-vs-webhook-trigger-http-endpoints)).
  In a flow, map `POST → putItem`, `GET → getItem`/`query`, `PUT → putItem` with `overwrite: true` or `updateItem`,
  `DELETE → deleteItem`. A WebhookTriggerActor emits `body` and `queryParams` (no path params), so ids for GET and
  DELETE come from `msg.<trigger>.queryParams`.
- **Job queue** ([above](#queue-pattern)) and **atomic transfer** (one `transactWrite` that debits, credits and logs).

## Errors

A request that breaks the request schema (unknown `action`, a key with `#` or over 256 characters, a bad slug, an empty
`expression`, a non-string condition value, a limit or item count over its maximum) fails with HTTP 400 and **no
code**. Every other failure has a code:

| Code | HTTP | Meaning |
|---|---|---|
| `INVALID_EXPRESSION` | 400 | Malformed query expression |
| `INVALID_CONDITION` | 400 | Malformed condition: empty, no space after the operator, bad `between`/`in`/`size` syntax |
| `INVALID_LABEL` | 400 | The label is not declared on the collection, or is being removed |
| `LABEL_LIMIT_EXCEEDED` | 400 | More than 15 active labels. A collection created when the limit was 5 keeps 5 slots until an operator widens it |
| `LABEL_NOT_FOUND` | 400 | The label does not exist on the collection |
| `LABEL_DELETING` | 409 | The label is already being deleted |
| `COLLECTION_NOT_FOUND` | 404 | The collection was never created, or is being deleted |
| `COLLECTION_ALREADY_EXISTS` | 409 | The slug is taken |
| `COLLECTION_DELETING` | 409 | Re-created while its deletion is still running |
| `CONDITION_FAILED` | 409 | A condition was false. A create-only put that collides reports this instead of `ITEM_ALREADY_EXISTS` when it has conditions |
| `ITEM_ALREADY_EXISTS` | 409 | `putItem` without `overwrite` on an existing key |
| `ITEM_DOES_NOT_EXIST` | 404 | `updateItem` set `value` fields or counters on a missing key |
| `CREATED_MISMATCH` | 409 | `overwrite` with `options.created`: the stored `createdAt` differs, or the item is gone. A failed condition on the same put reports this too |
| `TRANSACTION_FAILED` | 409 | A transaction item failed (a condition, a create-only put on an existing key); `error.cancellationReasons` has per-item codes |
| `TRANSACTION_CONFLICT` | 409 | A concurrent transaction conflicted |
| `TRANSACTION_DUPLICATE_ITEM` | 400 | The same collection and key twice in one transaction |
| `TRANSACTION_IN_PROGRESS` | 409 | A transaction with this `idempotencyKey` is still running |
| `IDEMPOTENCY_MISMATCH` | 400 | An `idempotencyKey` reused with different items |
| `ITEM_TOO_LARGE` | 400 | Item over 400 KB |
| `EXPRESSION_TOO_LONG`, `EXPRESSION_LIMIT` | 400 | Conditions or updates too large, or too many attribute names or values |
| `VALIDATION_ERROR` | 400 | Storage rejected the write (e.g. an empty-string label value), or `options.created` is in epoch seconds |
| `SERIALIZATION_ERROR` | 400 | The value cannot be stored |
| `THROUGHPUT_EXCEEDED` | 429 | The partition was throttled ([capacity model](collection-design.md#capacity-model)); retry after a short delay |
| `CONCURRENT_LIMIT` | 429 | Too many concurrent operations; retry after a short delay |
| (none) | 500 | Unexpected server error |
| `STORAGE_UNAVAILABLE`, `STORAGE_ERROR` | 503 | Storage temporarily unavailable; retry with backoff |

## Limits

| Limit | Value |
|---|---|
| Collection slug | 1–128 bytes, `^[a-z0-9_-]+$`, not starting `__` |
| Item key | 1–256 characters, any except `#` |
| Label name | 1–64 characters, `^[a-zA-Z0-9_-]+$` |
| Label value | Non-empty string, or `null` to remove the label (an empty string fails `VALIDATION_ERROR`) |
| Labels per collection | 15 (one index per slot) |
| Item size | 400 KB |
| `query` limit | 1–1000, default 100 |
| `listCollections` limit | 1–100, default 100 |
| `batchGetItem` / `batchWriteItem` | 100 / 25 items |
| `deleteItem` keys | 25 |
| `transactGet` / `transactWrite` | 100 items; 4 MB of data per transaction |
| `idempotencyKey` | ≤ 36 characters, a 10-minute window |
