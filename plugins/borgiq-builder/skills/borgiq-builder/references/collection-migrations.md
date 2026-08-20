# Collection Migrations & Provisioning

Collections are **not implicit**. A `putItem`/`getItem`/`query` against a slug that was never created fails with `COLLECTION_NOT_FOUND` (404) — the collection must exist in the registry first (see [collection-api.md → Error Codes](collection-api.md#error-codes)). So any app backed by [CollectionActor](collection-actor.md) needs a **provisioning step** that creates its collection and seeds default data *before the app serves traffic* — and that step has to be safe to run again every deploy, in every workspace/environment.

Per [single-collection design](collection-api.md#single-collection-design), an app normally has exactly **one** collection to provision: all of its entity types live in that collection under key prefixes (`task:`, `user:`, `config:`). If your migration runner is creating a second collection for the same app, first check that a security boundary or an explicit user request actually justifies it.

Treat this exactly like database migrations in a normal app: an **idempotent migration runner** that brings a workspace's collections up to the shape the app expects. Build it as a **UniversalTriggerActor that you fire with the `manual` trigger type** (canvas Invoke) — *never* via a webhook, a schedule, a button, or any other invoke. Migrations are an explicit, operator-initiated action: a UniversalTriggerActor runs Deno code (with `biqApi`) directly in `receive`, and restricting it to manual invoke keeps it from ever running by accident on an HTTP request or cron tick. Reach for this pattern whenever you design a collection-backed app — it is not an afterthought.

## Table of Contents

- [When to build migrations](#when-to-build-migrations)
- [The three things a migration does](#the-three-things-a-migration-does)
- [Idempotency — the core requirement](#idempotency--the-core-requirement)
- [The migration manager pattern](#the-migration-manager-pattern)
- [Worked example: a migration manager UniversalTriggerActor (manual invoke)](#worked-example-a-migration-manager-universaltriggeractor-manual-invoke)
- [Wiring and running migrations](#wiring-and-running-migrations)
- [Splitting migrations](#splitting-migrations)
- [Common mistakes](#common-mistakes)

## When to build migrations

Build a migration step whenever the app:

- depends on its collection existing (every CRUD app, every collection-backed app),
- needs **default / seed data** present on first run (config rows, lookup tables, an admin user, status enums, a singleton counter),
- has a **key strategy or label set** the app assumes (so the collection must be created with the right `labels` declared up front),
- will be deployed to **more than one workspace or environment** (dev/stage/prod), where you can't hand-create collections in the UI each time.

If you are generating a collection-backed app and there is no migration actor, that is a gap — flag it and add one.

## The three things a migration does

1. **Ensure the app's collection exists** — `createCollection` for the app's **single** collection (with the right `name`, `description`, and `labels` — see [single-collection design](collection-api.md#single-collection-design)).
2. **Seed default data** — `putItem` the rows the app can't run without, each under its entity key prefix (`config:settings`, `user:admin`).
3. **Record what ran** — write a marker so the next run knows this migration is already applied (the "ledger"): `_migration:<id>` keys inside the app's own collection.

## Idempotency — the core requirement

A migration **will** be run more than once (re-deploys, retries, multiple environments). Every step must be safe to repeat without erroring or clobbering live data. Three techniques, in order of preference:

- **Keep a migration ledger.** Reserved `_migration:<id>` keys **inside the app's own collection**, keyed by a stable migration id. Before running a migration, `getItem` its `_migration:<id>` key; skip if present. After it succeeds, `putItem` the key with a timestamp. This makes the *whole* migration skippable, not just each call, and gives you an applied-history audit trail — without a second collection, and with each app's ledger scoped to its own collection so migration ids can't collide across apps. The `_` prefix keeps ledger rows out of entity prefix queries (`task:*`), which is why entity prefixes never start with `_`.
- **Catch `COLLECTION_ALREADY_EXISTS` (409) on `createCollection`.** Re-creating an existing collection is a no-op you simply swallow. (Or call `listCollections` first and create only the missing slugs.)
- **Catch `ITEM_ALREADY_EXISTS` (409) on seed `putItem`s.** `putItem` is **create-only by default** (`overwrite` defaults to `false`) — writing a key that already exists throws rather than replacing it. That default is exactly what seed data wants: a re-run can never clobber a row a user has since edited. So treat "already exists" as success and move on. Do **not** "fix" the error by passing `overwrite: true` — that turns every re-deploy into a reset of live data.

> Two related error-code details: if a seed `putItem` also passes `conditions`, the same collision surfaces as `CONDITION_FAILED` instead of `ITEM_ALREADY_EXISTS`; and `createCollection` against a collection that is mid-deletion returns `COLLECTION_DELETING` rather than `COLLECTION_ALREADY_EXISTS` — don't swallow that one; it means wait and re-run. See [collection-api.md → Error Codes](collection-api.md#error-codes).

## The migration manager pattern

Rather than scatter provisioning calls across the app, centralize them in **one UniversalTriggerActor — the migration manager, invoked manually** — that:

- holds an **ordered list** of migrations, each with a unique `id` and a `run()` function,
- reads the ledger, **skips already-applied** migrations, runs the rest **in order**,
- records each success in the ledger,
- returns a **report** (`applied`, `skipped`) for the operator to inspect.

Adding a new seed row, label, or key prefix later = appending one entry to the list. The manager stays the single source of truth for "what shape should this workspace's storage be in."

## Worked example: a migration manager UniversalTriggerActor (manual invoke)

A single UniversalTriggerActor that provisions an app's collection and seed data idempotently. The app follows [single-collection design](collection-api.md#single-collection-design): **one** collection holds every entity type under key prefixes, and the migration ledger lives in the same collection under `_migration:` keys. **Webhook and schedule are disabled — it only ever fires on the `manual` trigger type (canvas Invoke).** It uses the same `biqApi`/`collectionsApi` helper documented in [collection-api.md → SDK Interface](collection-api.md#sdk-interface-denoactor--pythonactor); static source config follows [universal-trigger-actor.md](universal-trigger-actor.md).

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01migrationmgr0000000000:
    type: UniversalTriggerActor
    version: 1
    name: Run Collection Migrations
    msgVar: run_migrations
    description: Idempotently create the app collection and seed default data — manual invoke only
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      # Manual invoke ONLY — no webhook URL, no cron. Migrations never run by accident.
      webhook:
        enabled: false
      schedule:
        enabled: false
      options:
        allowNet: true
        code: |
          import { biqApi } from "@borgiq/actors";
          import type { TriggerRequest, Response } from "@borgiq/actors";

          // ONE collection for the whole app — entity types are separated by key
          // prefix (task:, user:, config:), per single-collection design. The
          // migration ledger lives in the same collection under _migration: keys.
          const COLLECTION = "taskapp";
          const LEDGER_PREFIX = "_migration:";

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

          // createCollection that treats "already exists" as success (idempotent).
          async function ensureCollection(spec: Record<string, unknown>): Promise<void> {
            try {
              await collectionsApi({ action: "createCollection", ...spec });
            } catch (e) {
              if ((e as any).code !== "COLLECTION_ALREADY_EXISTS") throw e;
            }
          }

          // Seed putItem: create-only (the default), and "already exists" = success.
          async function seed(key: string, value: unknown): Promise<void> {
            try {
              await collectionsApi({ action: "putItem", collection: COLLECTION, key, value });
            } catch (e) {
              // putItem defaults to overwrite: false, so an existing key throws
              // ITEM_ALREADY_EXISTS — for seed data that is a no-op, not an error.
              if ((e as any).code !== "ITEM_ALREADY_EXISTS") throw e;
            }
          }

          // --- The ordered migration list. Append new entries; never reorder/rename ids. ---
          const MIGRATIONS: { id: string; run: () => Promise<void> }[] = [
            {
              id: "0001_seed_defaults",
              run: async () => {
                await seed("config:settings", {
                  version: 1, theme: "system", createdAt: new Date().toISOString(),
                });
                // Status lookup rows the UI depends on:
                for (const s of ["pending", "active", "done"]) {
                  await seed(`config:status:${s}`, { label: s });
                }
              },
            },
            {
              id: "0002_seed_admin_user",
              run: async () => {
                await seed("user:admin", {
                  name: "Admin", role: "admin", createdAt: new Date().toISOString(),
                });
              },
            },
          ];

          export default async function receive(req: TriggerRequest): Promise<Response> {
            // Manual invoke only. Webhook/schedule are disabled in config, but guard
            // anyway so migrations can never run off an HTTP request or cron tick.
            if (req.trigger.type !== "manual") return { results: undefined };

            // The app's single collection must exist before anything else — including
            // the ledger keys. Declare labels up front: the 5 label slots are shared
            // by every entity type in the collection, so keep the names generic.
            await ensureCollection({
              slug: COLLECTION, name: "Task App",
              description: "All Task App data — entities separated by key prefix (task:, user:, config:)",
              labels: ["type", "status", "owner"],
            });

            const applied: string[] = [];
            const skipped: string[] = [];

            for (const m of MIGRATIONS) {
              const existing = await collectionsApi<{ key: string; value: unknown } | null>({
                action: "getItem", collection: COLLECTION, key: LEDGER_PREFIX + m.id,
              });
              if (existing) { skipped.push(m.id); continue; }

              await m.run(); // throws -> actor fails -> nothing recorded -> safe re-run
              await collectionsApi({
                action: "putItem", collection: COLLECTION, key: LEDGER_PREFIX + m.id,
                value: { appliedAt: new Date().toISOString() },
              });
              applied.push(m.id);
            }

            return { results: { ok: true, applied, skipped } };
          }
    schemas: {}
    id: ACTR01migrationmgr0000000000
    position:
      x: 0
      'y': 0
    edges: {}
```

> The ledger check (`getItem` on the `_migration:<id>` key) is the primary idempotency guard; the per-call "already exists" handling is the belt-and-suspenders backup for a migration that failed midway and re-runs.

## Wiring and running migrations

The migration manager **is** the trigger (a UniversalTriggerActor), so you don't wire a separate trigger to it — you **fire it with the `manual` trigger type**:

- **In the UI:** canvas Invoke on the migration trigger.
- **From the CLI:** `borgiq triggers run --canvas <canvasId> --actor-id <migrationTriggerActorId> --json` (the manual invoke; the canvas must be given by ULID, not slug), then poll `borgiq flowruns status <flowrunId>` and read the `applied` / `skipped` report.

Run it once after deploying the canvas to a new workspace, and again after appending migrations.

**Always invoke migrations manually — never any other invoke type.** Keep `webhook.enabled: false` and `schedule.enabled: false` so the migration runner has no webhook URL and no cron registration; the only way it fires is an explicit operator Invoke. Do **not** wire it to a WebhookTriggerActor, a ButtonTriggerActor, a ScheduledTriggerActor, or call it as a sub-flow on a request path — provisioning is a deliberate operator action, not something that should ride on user traffic or a timer. (It's idempotent, so an accidental extra manual run is harmless; the point is to keep it off automatic invokes.)

Because every step is idempotent, re-running is always safe — that is the whole point.

## Splitting migrations

- **Small app (one collection, a few seed rows):** a single manual-invoke migration UniversalTriggerActor like the example is enough.
- **Larger app / evolving schema:** keep one **manager** but grow the `MIGRATIONS` list over time — each schema change is a new entry with a new id (`0003_add_index_labels`, `0004_backfill_owner`, …). Never edit or reorder a shipped migration's id; add a new one. This preserves the applied-history contract.
- **Heavy backfills:** if a migration must transform many existing items, page through with `query` + `batchWriteItem` inside that migration's `run()`. If the backfill needs pandas/CLI tooling, have the (still manually-invoked) migration trigger emit the work downstream to a [PythonActor](python-actor.md) instead of doing it inline.

## Common mistakes

1. **One collection per entity type.** Provisioning `app-users`, `app-orders`, `app-comments`, `app-meta`, … for a single app. Model every entity type in the app's **one** collection with key prefixes (`user:`, `order:`, `comment:`, `meta:`) — see [collection-api.md → Single-Collection Design](collection-api.md#single-collection-design). Extra collections are only justified by a security boundary or an explicit user request.
2. **Assuming `putItem` auto-creates the collection.** It does not — you get `COLLECTION_NOT_FOUND`. Always provision with `createCollection` first.
3. **Non-idempotent migrations.** A bare `createCollection` throws `COLLECTION_ALREADY_EXISTS` on the second run and aborts the whole flow. Swallow it (or check `listCollections` first).
4. **Mishandling seed re-runs.** `putItem` is create-only by default, so a re-run seed throws `ITEM_ALREADY_EXISTS` — and the wrong fix is passing `overwrite: true`, which makes every deploy reset user-edited rows. The right fix: keep the create-only default and treat `ITEM_ALREADY_EXISTS` as success.
5. **No ledger.** Without recording applied ids you can't tell first-run from re-run, can't add migrations safely, and have no audit trail. Keep `_migration:<id>` ledger keys in the app's collection.
6. **Reordering or renaming migration ids.** The ledger keys on the id; renaming `0001_init` makes it look unapplied and it re-runs. Treat shipped ids as immutable; only append.
7. **Forgetting migrations entirely.** A collection-backed app with no provisioning step works in the dev workspace where someone hand-created the collection, then 404s in prod. Always ship the migration actor with the app.
8. **Running migrations on an automatic invoke.** A webhook-, schedule-, button-, or sub-flow-triggered migration can fire on user traffic or a timer. Build the migration runner as a UniversalTriggerActor with `webhook.enabled: false` / `schedule.enabled: false` and fire it with the **manual** trigger type only.
