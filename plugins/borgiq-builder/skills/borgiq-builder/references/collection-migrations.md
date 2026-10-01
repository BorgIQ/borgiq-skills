# Collection Migrations & Provisioning

How to provision the collections and streams an app depends on: an idempotent migration runner, built as a
UniversalTriggerActor that only a manual invoke fires, which creates storage, seeds defaults, keeps a ledger and
publishes the `$meta` manifest. Read it whenever you build a collection- or stream-backed app, and ship the runner with
the app.

## Contents

- [Why provisioning is required](#why-provisioning-is-required)
- [The four things a migration run does](#the-four-things-a-migration-run-does)
- [Idempotency — the core requirement](#idempotency--the-core-requirement)
- [The migration manager pattern](#the-migration-manager-pattern)
- [Worked example: a migration manager UniversalTriggerActor (manual invoke)](#worked-example-a-migration-manager-universaltriggeractor-manual-invoke)
- [Provisioning streams](#provisioning-streams)
- [Wiring and running migrations](#wiring-and-running-migrations)
- [Splitting migrations](#splitting-migrations)

## Why provisioning is required

Collections are **not implicit**: an action on a slug that was never created fails with `COLLECTION_NOT_FOUND` (404).
Streams are not either ([below](#provisioning-streams)). An app shipped without a provisioning step works in the dev
workspace where someone hand-created its storage, then 404s in production. So every collection-backed app needs a
step that creates its storage and seeds defaults **before it serves traffic**, safe to re-run on every deploy and in
every workspace. If you generate a collection-backed app with no migration actor, flag the gap and add one.

Build a migration step whenever the app depends on its collection existing, needs **seed data** on first run (config
rows, lookup tables, an admin user, status enums, a counter), assumes a **label set** (declared at creation), or will
be deployed to **more than one workspace or environment**.

An app normally provisions exactly **one** collection: all its entity types live in it under key prefixes, with a
`$meta` manifest listing them ([collection-design.md](collection-design.md)). A runner creating a second collection for
the same app needs a security boundary or an explicit user request to justify it.

## The four things a migration run does

1. **Ensure the app's collection exists:** `createCollection` with its `name`, `description` and `labels`.
2. **Seed default data:** create-only `putItem`s of the rows the app cannot run without, under their entity prefixes
   (`config:settings`, `user:admin`).
3. **Record what ran:** a `$migration:<id>` ledger row in the app's own collection per applied migration.
4. **Publish the manifest:** rewrite `$meta` (`putItem` with `options.overwrite: true`) from the runner's `ENTITIES`
   constant with the applied `schemaVersion`, at the end of **every** invoke, so it always matches the deployed code.

## Idempotency — the core requirement

A migration **will** run more than once (re-deploys, retries, several environments). Every step must be safe to
repeat without erroring or clobbering live data:

- **Keep a ledger.** Before a migration, `getItem` its `$migration:<id>` key and skip it if present; after it
  succeeds, `putItem` the key with a timestamp. This skips a whole migration, not just each call, gives an applied
  history, and without it you cannot tell a first run from a re-run or add migrations safely. The ledger lives in the
  app's own collection, so ids cannot collide across apps, and its `$` prefix keeps it out of entity queries.
- **Swallow `COLLECTION_ALREADY_EXISTS` (409) on `createCollection`**, or `listCollections` first and create only the
  missing slugs. A bare `createCollection` aborts the whole run the second time. Do not swallow `COLLECTION_DELETING`:
  the collection is mid-deletion, so wait and re-run.
- **Swallow `ITEM_ALREADY_EXISTS` (409) on seed `putItem`s.** `putItem` is create-only, which is exactly what seed data
  wants: a re-run never clobbers a row a user has since edited. Never "fix" the error with `overwrite: true`; that
  resets live data on every deploy. The one exception is `$meta`, which is derived from code. A seed `putItem` that also
  passes `conditions` reports the same collision as `CONDITION_FAILED`.

## The migration manager pattern

Centralize provisioning in **one UniversalTriggerActor, the migration manager, invoked manually**, that:

- holds an ordered list of migrations, each with a stable `id` and a `run()` function;
- reads the ledger, skips applied migrations and runs the rest in order;
- records each success in the ledger;
- rewrites `$meta` from its `ENTITIES` constant;
- returns a report (`applied`, `skipped`, `schemaVersion`).

A new seed row or label is one more list entry; a new entity prefix is one more `ENTITIES` entry (plus a migration if it
needs seed rows). `$meta` publishes that truth into the collection.

## Worked example: a migration manager UniversalTriggerActor (manual invoke)

Webhook and schedule are disabled, so only a `manual` invoke (canvas Invoke) fires it. Static configuration follows
[universal-trigger-actor.md](universal-trigger-actor.md). Paste the `collectionsApi` helper from
[collection-sdk.md](collection-sdk.md#typed-helper-deno) where marked; it throws errors carrying their `code`.

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
      webhook:
        enabled: false   # no webhook URL
      schedule:
        enabled: false   # no cron
      options:
        allowNet: true
      codeDir:
        - path: main.ts
          content: |
            import { biqApi } from "@borgiq/actors";
            import type { TriggerRequest, Response } from "@borgiq/actors";

            const COLLECTION = "taskapp";          // one collection for the whole app
            const LEDGER_PREFIX = "$migration:";

            // Every key prefix the app writes; $meta publishes this.
            const ENTITIES = {
              task:   { prefix: "task:",   key: "task:<ulid>",   description: "Tasks" },
              user:   { prefix: "user:",   key: "user:<id>",     description: "Users" },
              config: { prefix: "config:", key: "config:<name>", description: "Settings and status lookup rows" },
            };
            const LABELS = { type: "entity name (task, user, config)", status: "task status", owner: "assignee user id" };

            // async function collectionsApi<T>(body) { ... }  <- paste the helper from collection-sdk.md here

            async function ensureCollection(spec: Record<string, unknown>): Promise<void> {
              try { await collectionsApi({ action: "createCollection", ...spec }); }
              catch (e) { if ((e as any).code !== "COLLECTION_ALREADY_EXISTS") throw e; }
            }

            // Create-only seed: "already exists" is success.
            async function seed(key: string, value: unknown): Promise<void> {
              try { await collectionsApi({ action: "putItem", collection: COLLECTION, key, value }); }
              catch (e) { if ((e as any).code !== "ITEM_ALREADY_EXISTS") throw e; }
            }

            // Append new entries; never reorder or rename shipped ids.
            const MIGRATIONS: { id: string; run: () => Promise<void> }[] = [
              {
                id: "0001_seed_defaults",
                run: async () => {
                  await seed("config:settings", { version: 1, theme: "system", createdAt: new Date().toISOString() });
                  for (const s of ["pending", "active", "done"]) await seed(`config:status:${s}`, { label: s });
                },
              },
              {
                id: "0002_seed_admin_user",
                run: async () => {
                  await seed("user:admin", { name: "Admin", role: "admin", createdAt: new Date().toISOString() });
                },
              },
            ];

            export default async function receive(req: TriggerRequest): Promise<Response> {
              if (req.trigger.type !== "manual") return { results: undefined };   // guard: manual invoke only

              // The collection first, ledger keys included. Declare only the labels the app filters on.
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
                await m.run();   // a throw fails the actor before the ledger row: safe to re-run
                await collectionsApi({
                  action: "putItem", collection: COLLECTION, key: LEDGER_PREFIX + m.id,
                  value: { appliedAt: new Date().toISOString() },
                });
                applied.push(m.id);
              }

              // Last, on every run: reaching here means every migration is applied.
              const schemaVersion = MIGRATIONS.length;
              await collectionsApi({
                action: "putItem", collection: COLLECTION, key: "$meta",
                value: {
                  app: "taskapp", schemaVersion, entities: ENTITIES,
                  system: { [LEDGER_PREFIX]: "Applied migration ledger" },
                  labels: LABELS, updatedAt: new Date().toISOString(),
                },
                options: { overwrite: true },
              });

              return { results: { ok: true, applied, skipped, schemaVersion } };
            }
    schemas: {}
    id: ACTR01migrationmgr0000000000
    position:
      x: 0
      'y': 0
    edges: {}
```

The ledger check is the primary guard; the per-call "already exists" handling covers a migration that failed midway
and re-runs. Because `$meta` is written last, a run that fails midway leaves the previous manifest and `schemaVersion`
in place, so app code checking for pending migrations keeps refusing until a re-run succeeds.

## Provisioning streams

`appendData` or `readStream` on a stream that was never created, or that expired, fails with `STREAM_NOT_FOUND` (404),
and a stream with neither `persistent: true` nor `idleTtlSeconds` is deleted an hour after its last append
([stream-actor.md → Rules](stream-actor.md#rules)). Create every stream the app or a scheduled consumer depends on with
**`persistent: true`** in the same runner.

Ensure streams on **every** invoke, next to `ensureCollection` and outside the ledger, so a stream deleted since the
last run is recreated (empty). `createStream` on a taken slug fails with `STREAM_ALREADY_EXISTS` (409) and leaves that
stream's lifecycle unchanged, so on that error call `editMetadata` with `persistent: true` in case it was created
without it. Add to the worked example, with the `streamsApi` helper from
[stream-api.md](stream-api.md#sdk-denoactor--pythonactor) pasted beside `collectionsApi`:

```typescript
// createStream that treats "already exists" as success and converges the lifecycle.
async function ensureStream(slug: string, name: string): Promise<void> {
  try {
    await streamsApi({ action: "createStream", slug, name, persistent: true });
  } catch (e) {
    if ((e as any).code !== "STREAM_ALREADY_EXISTS") throw e;
    await streamsApi({ action: "editMetadata", stream: slug, persistent: true });
  }
}

// In receive(), right after ensureCollection(...):
await ensureStream("task-activity", "Task activity");
```

- Slugs match `^[a-z0-9][a-z0-9_-]{0,63}$`; a workspace holds at most 100 streams (`STREAM_LIMIT_EXCEEDED`, 409).
- Provision only the fixed-slug streams the app always needs. Per-run or per-session streams (`run-<id>`) are created
  by the flow that uses them, with an `idleTtlSeconds`.

## Wiring and running migrations

The migration manager **is** the trigger, so nothing is wired to it. **Fire it with a manual invoke, never any other
way:** keep `webhook.enabled: false` and `schedule.enabled: false` so it has no webhook URL and no cron registration,
and never wire it to a WebhookTriggerActor, a ButtonTriggerActor, a ScheduledTriggerActor or a sub-flow call on a
request path. Provisioning is a deliberate operator action, not something that rides on user traffic or a timer (an
extra manual run is harmless: everything is idempotent).

- **In the UI:** canvas Invoke on the migration trigger.
- **From the CLI:** start it, wait for the run, then read the report the trigger emitted:

  ```bash
  borgiq triggers run --canvas <canvasId> --actor-id <runnerActorId> --json   # canvas by ULID, not slug; returns flowrun.id
  borgiq flowruns status <flowrunId> --json                                   # poll until state is "completed"
  borgiq flowruns summary <flowrunId> --json                                  # "errors" must be empty
  borgiq flowrun-messages list --canvas <canvasId> --flowrun-id <flowrunId> --actor-id <runnerActorId> --json
  borgiq flowrun-messages data <messageId> --json                             # msg.run_migrations: { applied, skipped, schemaVersion }
  ```

Run it after deploying the canvas to a new workspace and again after appending migrations.

## Splitting migrations

- **Small app** (one collection, a few seed rows): one manager like the example.
- **Evolving schema:** keep one manager and append to `MIGRATIONS`, one entry per change with a new id
  (`0003_add_index_labels`, `0004_backfill_owner`). The ledger keys on the id, so never edit, reorder or rename a
  shipped id: a renamed `0001_init` looks unapplied and runs again.
- **Heavy backfills:** page through with `query` + `batchWriteItem` inside that migration's `run()`. If it needs pandas
  or CLI tooling, have the (still manually invoked) trigger emit the work to a [PythonActor](python-actor.md).
