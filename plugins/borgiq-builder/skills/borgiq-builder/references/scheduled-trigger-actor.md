# Scheduled Trigger Actor Reference

The ScheduledTriggerActor starts a flow on a cron schedule (syncs, reports, polling, batch jobs). Read this for its config, cron syntax, the emitted message and incremental processing with LTM. If the same flow must also fire on webhook requests, or code must run at trigger time, use [universal-trigger-actor.md](universal-trigger-actor.md).

## Configuration

```yaml
type: ScheduledTriggerActor
version: 1
name: Hourly Sync Trigger
msgVar: scheduled_trigger
isActive: true
enableLTM: true
sourcePorts:
  - id: SPRTdefault
configuration:
  schedule:
    cron: '0 * * * *'
    timezone: America/New_York
schemas: {}
```

The schedule is static: it lives at `configuration.schedule`, is never interpolated, and `options` stays empty.

| Field | Type | Default | Meaning |
|---|---|---|---|
| `cron` | string | — (required) | When to run (see below). A literal: `${{ }}` is rejected. |
| `timezone` | IANA zone name | none | Zone the cron is evaluated in, e.g. `America/Los_Angeles`, `Europe/London`, `Asia/Tokyo` ([full list](https://www.iana.org/time-zones)). Always set it: without it the job runs on the scheduler's server clock (the editor pre-fills `America/New_York`). |
| `preventOverlappingFlowruns` | boolean | `false` | When true, a tick emits nothing while the flowrun started by the previous tick is still running. The trigger tracks that flowrun in its LTM, so keep `enableLTM: true` (the default for this trigger). |

Exact schema: [typescript/actorSchemas/trigger/scheduled.md](typescript/actorSchemas/trigger/scheduled.md) and [typescript/actorSchemas/trigger/triggerConfig.md](typescript/actorSchemas/trigger/triggerConfig.md).

## Cron syntax

Five fields: minute (0–59), hour (0–23), day of month (1–31), month (1–12), day of week (0–6, 0 = Sunday). `*` is any value, `,` a list (`1,3,5`), `-` a range (`1-5`), `/` a step (`*/15`).

| Expression | Runs |
|---|---|
| `* * * * *` | every minute |
| `*/15 * * * *` | every 15 minutes |
| `@every 30m` | every 30 minutes |
| `0 * * * *`, `@hourly`, `@every 1h` | every hour at minute 0 |
| `0 */2 * * *` | every 2 hours |
| `0 0 * * *`, `@daily` | every day at midnight |
| `0 9 * * *` | every day at 09:00 |
| `0 9,12,17 * * *` | at 09:00, 12:00 and 17:00 |
| `0 8 * * 1-5` | weekdays at 08:00 |
| `0 9 * * 1` | Mondays at 09:00 |
| `0 0 * * 0`, `@weekly` | Sundays at midnight |
| `0 0 1 * *`, `@monthly` | the 1st at midnight |
| `@annually`, `@yearly` | `0 0 1 1 *` |

## Emitted message

`{ triggeredAt, lastTriggeredAt }`: ISO 8601 times of this tick and of the previous one (`null` on the first run). Downstream actors read `${{ msg.scheduled_trigger.triggeredAt }}`.

## Incremental processing with LTM

`lastTriggeredAt` already gives the previous run time; use LTM for custom state such as processed record ids or cursors. Run no more often than needed, make the job idempotent (a tick can fire twice), handle failures with `continueOnError` or an error block, and watch run outcomes ([flowrun-job-states.md](flowrun-job-states.md)). The DenoActor below needs `enableLTM: true` and `configuration.inputs: ${{ msg.scheduled_trigger }}`:

```typescript
import type { Request, Response } from "@borgiq/actors";
import _ from "npm:lodash@4.17.21";

export default async function receive(req: Request): Promise<Response> {
  // Use lastTriggeredAt from the trigger (or fall back to LTM for custom tracking)
  const lastRunAt = req.inputs.lastTriggeredAt || _.get(req.memory.ltm, "lastRunAt", null);

  const items = await fetchItemsSince(lastRunAt);

  for (const item of items) {
    await processItem(item);
  }

  return {
    results: {
      processedCount: items.length,
      lastRunAt: req.inputs.triggeredAt,
    },
    // Update last run timestamp in LTM (optional, since trigger provides lastTriggeredAt).
    // A returned top-level key replaces the stored one; other LTM keys are kept.
    memory: { ltm: { lastRunAt: req.inputs.triggeredAt } },
  };
}
```
