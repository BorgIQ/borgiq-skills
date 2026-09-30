# Collection SDK and REST API

Calling collections from code (DenoActor, PythonActor, and the code of a UniversalTriggerActor) and over the workspace
REST API: the request envelope, a typed Deno helper with result types, the optimistic-lock retry, enumerating a
collection from `$meta`, and the REST routes and scopes. Code sends the same options the YAML actor takes: see
[collection-actor.md](collection-actor.md) for every action's options, semantics and error codes.

## Contents

- [The runtime endpoint](#the-runtime-endpoint)
- [Typed helper (Deno)](#typed-helper-deno)
- [Python](#python)
- [Optimistic lock with retry](#optimistic-lock-with-retry)
- [Enumerate a collection from `$meta`](#enumerate-a-collection-from-meta)
- [REST API](#rest-api)

## The runtime endpoint

Every action is one `POST /collections` whose JSON body is the action's options: `action` plus the fields the actor
takes under `configuration.options`. `biqApi` (Deno, from `@borgiq/actors`) and `biq_api` (Python, from `borgiq`) add
authentication and tenant scoping.

The response is `{ ok: boolean, value: T, error?: { code, message } }`, with two exceptions: a body that fails the
request schema gets HTTP 400 `{ status, message: "Input validation error!", details }` with no `code`, and an
unexpected server error is HTTP 500 with a plain message string. `T` is the action's result
([collection-actor.md](collection-actor.md#item-actions)).

## Typed helper (Deno)

One helper that unwraps `value` and throws with the error `code`, plus the result types to pass per call:

```typescript
import { biqApi } from "@borgiq/actors";

/** A collection (createCollection, updateCollection, listCollections items). */
type CollectionMeta = {
  slug: string;
  name: string;
  description?: string;
  /** 15 label slots in order: null = unused; { name, deletedAt } = being removed. */
  labels: (string | null | { name: string; deletedAt: string })[];
  createdAt: string;
  updatedAt: string;
};

/** An item. `V` is the value's shape. The optional fields are present only with `options.meta: true`. */
type CollectionItem<V = unknown> = {
  key: string;
  value: V;
  collection?: string;
  labels?: Record<string, string | null>;
  createdAt?: string;
  updatedAt?: string;
  ttl?: string;
};

type CreateCollectionResult = CollectionMeta;
type ListCollectionsResult  = { items: CollectionMeta[]; lastKey?: string; count: number };
type UpdateCollectionResult = CollectionMeta;
type DeleteCollectionResult = { slug: string; status: "deleting" };

type PutItemResult<V = unknown>    = CollectionItem<V>;
type GetItemResult<V = unknown>    = CollectionItem<V> | null;
type UpdateItemResult<V = unknown> = CollectionItem<V>;
type DeleteItemResult              = { deleted: Array<{ collection: string; key: string }> };
type QueryResult<V = unknown>      = { items: CollectionItem<V>[]; count: number; lastKey?: Record<string, string> };

type BatchGetItemResult<V = unknown>   = { items: (CollectionItem<V> | null)[] };
type BatchWriteItemResult<V = unknown> = { processed: number; items?: CollectionItem<V>[]; deleted?: Array<{ collection: string; key: string }> };
type TransactGetResult<V = unknown>    = { items: (CollectionItem<V> | null)[]; count: number };
type TransactWriteResult               = { processed: number };

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

Pass the result type on each call; untyped calls return `unknown`:

```typescript
type Product = { name: string; price: number };

// Create-only; an existing key throws with code ITEM_ALREADY_EXISTS. Replace with options.overwrite.
await collectionsApi<PutItemResult<Product>>({
  action: "putItem", collection: "shop", key: "product:widget-1",
  value: { name: "Widget Pro", price: 29.99 }, labels: { status: "active" },
  options: { overwrite: true, ttl: 86400 },
});

const product = await collectionsApi<GetItemResult<Product>>({ action: "getItem", collection: "shop", key: "product:widget-1" });
// product is { key, value: Product } | null

const page1 = await collectionsApi<QueryResult<Product>>({
  action: "query", collection: "shop", expression: "product:*", options: { limit: 25 },
});
const page2 = await collectionsApi<QueryResult<Product>>({
  action: "query", collection: "shop", expression: "product:*", options: { limit: 25, startKey: page1.lastKey },
});

await collectionsApi<DeleteItemResult>({ action: "deleteItem", collection: "shop", keys: ["product:widget-1", "product:widget-2"] });
```

A migration runner that swallows `COLLECTION_ALREADY_EXISTS` and `ITEM_ALREADY_EXISTS` by `code` is in
[collection-migrations.md](collection-migrations.md#worked-example-a-migration-manager-universaltriggeractor-manual-invoke).

## Python

Send the same bodies with `biq_api('/collections', method='POST', json=body)`; `.json()` is the envelope, so check
`['ok']` and read `['value']`. A quick reference is in [python-actor.md](python-actor.md).

## Optimistic lock with retry

For a read-modify-write of a whole value (appending to an array, merging objects) under concurrency, keep a `version`
field, write with a condition on it, and retry on conflict. The YAML actor has no retry loop, so this lives in code.
This helper returns the raw envelope so the loop can inspect `ok` and `error`:

```typescript
import type { Request, Response } from "@borgiq/actors";
import { biqApi } from "@borgiq/actors";

async function collectionsRaw(body: Record<string, unknown>) {
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
    const { value: item } = await collectionsRaw({ action: "getItem", collection: "aggregated-status", key: req.inputs.taskId });
    const current = item?.value ?? { statuses: [], version: 0 };
    const updated = { statuses: [...current.statuses, req.inputs.newStatus], version: current.version + 1 };

    // The first write is a create-only putItem: updateItem cannot create the item.
    const result = current.version === 0
      ? await collectionsRaw({ action: "putItem", collection: "aggregated-status", key: req.inputs.taskId, value: updated })
      : await collectionsRaw({
          action: "updateItem", collection: "aggregated-status", key: req.inputs.taskId,
          value: updated, conditions: { version: `= ${current.version}` },
        });
    if (result.ok) return { results: updated };

    // Conflict: another run wrote first (CONDITION_FAILED) or created the item first (ITEM_ALREADY_EXISTS). Retry.
    if (result.error?.code === "CONDITION_FAILED" || result.error?.code === "ITEM_ALREADY_EXISTS") continue;
    throw new Error(`Collection API error: ${JSON.stringify(result.error)}`);
  }
  throw new Error(`Failed after ${maxRetries} retries: contention too high`);
}
```

## Enumerate a collection from `$meta`

List a collection without scanning it: read the manifest, then one prefix query per entity
([collection-design.md](collection-design.md#the--system-namespace-and-the-meta-manifest)).

```typescript
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

## REST API

External systems and scripts reach collections over the workspace REST API with a personal access token
([api-tokens.md](api-tokens.md)), under `/v1/orgs/:orgSlugOrId/workspaces/:workspaceSlugOrId/collections`. Every route
checks only the `collection:read` scope, the write and delete routes included: treat a token with `collection:read` as
able to change collections.

| Method | Path | Body or query | Returns |
|---|---|---|---|
| `GET` | `/collections` | `?page=&pageSize=&search=` (page size ≤ 100, default 25) | `{ total, items }`; each item's `labels` lists active label names only |
| `POST` | `/collections` | `{ slug, name, description?, labels? }` | `201 { ok, value }` |
| `PUT` | `/collections/:slug` | `{ name?, description?, addLabels?, removeLabels? }` | `{ ok, value }` |
| `DELETE` | `/collections/:slug` | — | `{ ok, value: { slug, status: "deleting" } }` |
| `GET` | `/collections/:slug/items` | `?expression=` (default `*`) `&label=&pageSize=&startKey=` (the previous `lastKey`, JSON-encoded) | `{ items, lastKey?, labels }`; items carry the meta fields |
| `PUT` | `/collections/:slug/items` | `{ key, value, labels?, options?: { overwrite, ttl, meta, created }, conditions? }` | `{ ok, value }`; create-only unless `options.overwrite: true` |
| `DELETE` | `/collections/:slug/items` | `{ keys, conditions? }` (one key or up to 25) | `{ ok, value: { deleted } }` |

Errors: the `POST`, `PUT` and `DELETE` routes answer `{ ok: false, error: { code, message } }` with the code's HTTP
status; the two `GET` routes answer a collection error as a bare JSON string with that status. An unexpected error is a
500 with a plain message string on every route.
