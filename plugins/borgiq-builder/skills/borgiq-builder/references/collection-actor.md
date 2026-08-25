# CollectionActor Reference

CollectionActor is a **Task Actor** that provides YAML-based access to the [Collection API](collection-api.md). It is the recommended storage actor for all new workflows.

For full API documentation including actions, parameters, DynamoDB behavior, conditions, concurrent update patterns, transactions, batch operations, error codes, and code examples (Deno/Python), see [collection-api.md](collection-api.md).

> **One collection per app** — model all of an app's entity types in a **single collection** with key prefixes (`ticket:*`, `user:*`), never one collection per entity type. This is DynamoDB single-table design; split into multiple collections only for a security boundary or when the user explicitly asks. Every app collection also carries a **`$meta` manifest** row (the `$` prefix sorts first in the UI) listing its entity prefixes, so the collection can be navigated without scanning it. See [collection-api.md → Single-Collection Design](collection-api.md#single-collection-design).

> **Collections must be created before use** — a `putItem`/`query` against a slug that was never created returns `COLLECTION_NOT_FOUND`. Any app backed by collections needs an idempotent **provisioning/migration** step (create the app's collection + seed defaults, safe to re-run per deploy and per workspace). See [collection-migrations.md](collection-migrations.md) for the migration-manager pattern.

## Table of Contents

- [Configuration Structure](#configuration-structure)
- [Actions Summary](#actions-summary)
- [Event System](#event-system)
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
    type: CollectionActor
    version: 1
    name: Store Item
    msgVar: store_item
    description: Store an item in a collection
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: putItem
        collection: my-collection
        key: my-key
        value: ${{ msg.upstream_actor.value }}
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

---

## Actions Summary

All actions are configured via the `action` field in `configuration.options`. For full parameter documentation, see [collection-api.md](collection-api.md).

| Action | Description | API Reference |
|--------|-------------|---------------|
| `createCollection` | Create a new collection | [Details](collection-api.md#createcollection) |
| `listCollections` | List all collections | [Details](collection-api.md#listcollections) |
| `updateCollection` | Update collection metadata/labels | [Details](collection-api.md#updatecollection) |
| `deleteCollection` | Delete a collection | [Details](collection-api.md#deletecollection) |
| `putItem` | Store or replace an item (full replace) | [Details](collection-api.md#putitem) |
| `getItem` | Retrieve an item by key | [Details](collection-api.md#getitem) |
| `updateItem` | Partially update an item (shallow field merge) | [Details](collection-api.md#updateitem) |
| `deleteItem` | Delete one or more items | [Details](collection-api.md#deleteitem) |
| `query` | Query items by key/label with pagination | [Details](collection-api.md#query) |
| `batchGetItem` | Read up to 100 items | [Details](collection-api.md#batchgetitem) |
| `batchWriteItem` | Write up to 25 items (put/delete) | [Details](collection-api.md#batchwriteitem) |
| `transactGet` | Consistent read up to 100 items | [Details](collection-api.md#transactget) |
| `transactWrite` | Atomic write up to 100 items with conditions | [Details](collection-api.md#transactwrite) |

**Key concepts** (see [collection-api.md](collection-api.md)):
- [Condition Expressions](collection-api.md#condition-expressions) — preconditions for writes (optimistic locking, existence checks)
- [Concurrent Update Patterns](collection-api.md#concurrent-update-patterns) — safe patterns for parallel workflows
- [DynamoDB Mapping Reference](collection-api.md#dynamodb-mapping-reference) — how each action maps to DynamoDB, nested object behavior
- [Error Codes](collection-api.md#error-codes) — API error codes and meanings

## Event System

Item changes emit events that can be consumed by BorgIQ workflow triggers (via DynamoDB Streams).

### Event Types

| Event | Trigger |
|-------|---------|
| `created` | New item inserted (first `putItem`) |
| `updated` | Existing item modified |
| `deleted` | Item removed via `deleteItem` or TTL |

### Event Payload

```json
{
  "name": "updated",
  "collection": "products",
  "key": "productId-12345",
  "item": {
    "collection": "products",
    "key": "productId-12345",
    "value": { "name": "Widget Pro", "price": 34.99 },
    "createdAt": "2025-01-15T10:30:00.000Z",
    "updatedAt": "2025-01-15T12:00:00.000Z",
    "labels": { "category": "electronics", "status": "active" }
  },
  "previous": {
    "value": { "name": "Widget Pro", "price": 29.99 },
    "updatedAt": "2025-01-15T10:30:00.000Z"
  }
}
```

### Event Filtering

```
*                         → all events on all items
created                   → all created events
*:users                   → all events in "users" collection
created:users:jane*       → created events in "users" where key starts with "jane"
```

### Event Ordering

- Events are processed in order within a collection (same partition)
- Handlers across different partitions may execute in parallel
- On handler failure: exponential backoff retry for up to 24 hours, then dropped

---

## Complete Examples

### Store Callback Token for Email Thread

Store a callback token associated with an email thread ID for later retrieval when a reply arrives:

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01jn59bxebpqetm28j8ev936r1:
    type: CollectionActor
    version: 1
    name: Store Token with Thread ID
    msgVar: store_token
    description: Store callback token keyed by Gmail thread ID
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
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
    schemas: {}
    id: ACTR01jn59bxebpqetm28j8ev936r1
    position:
      x: 0
      'y': 0
    edges: {}
```

### Retrieve Token on Email Reply

When an email reply arrives, look up the associated callback token:

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kd9r2abc123def456gh78ij:
    type: CollectionActor
    version: 1
    name: Get Token by Thread ID
    msgVar: get_token
    description: Retrieve callback token for email thread
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: getItem
        collection: callback-tokens
        key: gmail-${{ msg.email_trigger.threadId }}
    schemas: {}
    id: ACTR01kd9r2abc123def456gh78ij
    position:
      x: 0
      'y': 0
    edges: {}
```

### Rate Limiting with Atomic Counter

Track API call count per hour using atomic counters:

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kd9r3xyz789abc012def345:
    type: CollectionActor
    version: 1
    name: Increment API Counter
    msgVar: api_counter
    description: Track API calls for rate limiting
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: updateItem
        collection: rate-limits
        key: api-calls-${{ Q.dateFns.format(Q.now(), 'yyyy-MM-dd-HH') }}
        atomicCounters:
          count: 1
    schemas: {}
    id: ACTR01kd9r3xyz789abc012def345
    position:
      x: 0
      'y': 0
    edges: {}
```

### CRUD Operations for Web App

**Create / Update an item:**
```yaml
configuration:
  options:
    action: putItem
    collection: products
    key: ${{ msg.webhook.body.productId }}
    value:
      name: ${{ msg.webhook.body.name }}
      price: ${{ msg.webhook.body.price }}
      updatedAt: ${{ Q.now() }}
    labels:
      category: ${{ msg.webhook.body.category }}
    options:
      meta: true
```

**Read a single item:**
```yaml
configuration:
  options:
    action: getItem
    collection: products
    key: ${{ msg.webhook.params.productId }}
    options:
      meta: true
```

**Delete an item:**
```yaml
configuration:
  options:
    action: deleteItem
    collection: products
    keys: ${{ msg.webhook.params.productId }}
```

**List items (query):**
```yaml
configuration:
  options:
    action: query
    collection: products
    expression: ""
    options:
      limit: 25
      meta: true
      label: ${{ msg.webhook.query.category }}
```

---

## Use Cases

| Scenario | Action |
|----------|--------|
| Store callback tokens for async workflows | `putItem` |
| Retrieve data by key | `getItem` |
| Track state across workflow runs | `putItem` / `getItem` |
| Rate limiting / counting | `updateItem` with `atomicCounters` |
| List or search stored items | `query` |
| Clean up old data | `deleteItem` |
| Temporary data with auto-expiry | `putItem` with `ttl` |
| Bulk import data | `batchWriteItem` |
| Fetch multiple items at once | `batchGetItem` |
| Atomic multi-item updates (e.g., transfers) | `transactWrite` |
| Consistent multi-item reads | `transactGet` |
| CRUD API backend | `putItem` / `getItem` / `deleteItem` / `query` |
| Organize data by category | `putItem` with `labels` + `query` with label filter |
| Store multiple entity types for one app | One collection + key prefixes (`user:*`, `order:*`) — see [single-collection design](collection-api.md#single-collection-design) |
| Provision the app's collection (migrations) | `createCollection` / `listCollections` / `deleteCollection` |
| Background job queue | `putItem` (enqueue) + `query` + `updateItem` (dequeue) — see [Queue Pattern](collection-api.md#queue-pattern-using-collections) |

---

## Workflow Patterns

### Pattern 1: Async Email Response Handling (using Collections)

```
EmailTrigger -> SendEmail -> IssueCallbackToken -> CollectionActor (putItem)
                                                         |
                                         [Store token in callback-tokens collection]

EmailReplyTrigger -> CollectionActor (getItem) -> RouterActor -> NotifyCallbackToken
                            |
              [Lookup token from callback-tokens collection]
```

### Pattern 2: Rate Limiting

```
Trigger -> CollectionActor (updateItem + atomicCounters) -> RouterActor -> [Continue or Block]
                                                                |
                                                    [Check if count > limit]
```

### Pattern 3: CRUD Web Application

```
WebhookTrigger -> RouterActor -> CollectionActor (per action) -> WebhookResponseActor
                     |
          [Route by HTTP method:
           POST   -> putItem (create)
           GET    -> getItem or query (read/list)
           PUT    -> putItem (update)
           DELETE -> deleteItem (delete)]
```

### Pattern 4: Background Job Queue

```
Trigger -> CollectionActor (putItem) -> [enqueue message with status=pending]

ScheduledTrigger -> CollectionActor (query label=pending) -> CollectionActor (updateItem + condition) -> [process] -> CollectionActor (updateItem status=completed)
                                                                       |
                                                          [Claim with condition to prevent double-processing]
```

### Pattern 5: Atomic Transfer

```
Trigger -> CollectionActor (transactWrite) -> [Continue on success]
                  |
     [Debit sender + credit receiver + log transfer atomically]
```

---

## TypeScript Schema Hint

See [typescript/actor-schemas-task-collection.md](typescript/actor-schemas-task-collection.md) for complete TypeScript definitions including:
- `CollectionActorAction` - Enum of all available actions
- `CollectionActorOptionsSchema` - Configuration options (discriminated union by action)
- `CollectionActorCreateCollectionOptionsSchema` / `CollectionActorCreateCollectionResult` - Create collection
- `CollectionActorListCollectionsOptionsSchema` / `CollectionActorListCollectionsResult` - List collections
- `CollectionActorUpdateCollectionOptionsSchema` / `CollectionActorUpdateCollectionResult` - Update collection
- `CollectionActorDeleteCollectionOptionsSchema` / `CollectionActorDeleteCollectionResult` - Delete collection
- `CollectionActorPutItemOptionsSchema` / `CollectionActorPutItemResult` - Put item
- `CollectionActorUpdateItemOptionsSchema` / `CollectionActorUpdateItemResult` - Update item
- `CollectionActorGetItemOptionsSchema` / `CollectionActorGetItemResult` - Get item
- `CollectionActorDeleteItemOptionsSchema` / `CollectionActorDeleteItemResult` - Delete item
- `CollectionActorQueryOptionsSchema` / `CollectionActorQueryResult` - Query items
- `CollectionActorBatchGetItemOptionsSchema` / `CollectionActorBatchGetItemResult` - Batch get
- `CollectionActorBatchWriteItemOptionsSchema` / `CollectionActorBatchWriteItemResult` - Batch write
- `CollectionActorTransactGetOptionsSchema` / `CollectionActorTransactGetResult` - Transact get
- `CollectionActorTransactWriteOptionsSchema` / `CollectionActorTransactWriteResult` - Transact write

---

