# Scheduled Trigger Actor Reference

The ScheduledTriggerActor starts a workflow at specified times based on a cron schedule.

## Table of Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [Emitted Message](#emitted-message)
- [Common Patterns](#common-patterns)
- [Accessing in Downstream Actors](#accessing-in-downstream-actors)
- [Using LTM for Incremental Processing](#using-ltm-for-incremental-processing)
- [Use Cases](#use-cases)
- [Best Practices](#best-practices)
- [Quick Example](#quick-example)

## Overview

Scheduled triggers allow workflows to run automatically at defined intervals. They use cron expressions to specify when the workflow should execute. Use scheduled triggers for:

- Periodic data synchronization
- Scheduled reports and notifications
- Regular maintenance tasks
- Time-based polling of external services
- Batch processing jobs

If the same workflow must also fire on webhook requests, or you need code to run at trigger time, see [universal-trigger-actor.md](universal-trigger-actor.md).

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: ScheduledTriggerActor
    version: 1
    name: Scheduled Trigger
    msgVar: scheduled_trigger
    description: Trigger the workflow on a schedule
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      schedule:
        cron: '0 * * * *'
        timezone: America/New_York
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Config shape

Schedule config is fully **static** — it has no interpolatable fields. It lives at `configuration.schedule` (a sibling of `options`, never interpolated), and `options` is empty for the standalone ScheduledTriggerActor.

| Field | Location | Type | Required | Description |
|-------|----------|------|----------|-------------|
| `cron` | `configuration.schedule` | string | Yes | Cron expression defining when to run (renamed from `schedule`) |
| `timezone` | `configuration.schedule` | string | No | Timezone for the schedule (default: America/New_York) |
| `enabled` | `configuration.schedule` | boolean | No | UniversalTriggerActor only — when false no cron job is registered |

## TypeScript Schema Definition

Schedule config is the static `ScheduleConfigSchema` at `configuration.schedule`:

```typescript
import { z } from 'zod';

// Cron pattern regex for validation
const cronPattern = /^((((\d+,)+\d+|(\d+(\/|-|#)\d+)|\d+L?|\*(\/\d+)?|L(-\d+)?|\?|[A-Z]{3}(-[A-Z]{3})?) ?){5})|(@(annually|yearly|monthly|weekly|daily|hourly|reboot))|(@every (\d+(m|h))+)$/;

// List of all supported timezones
const timezoneValues = Intl.supportedValuesOf('timeZone');

/** STATIC schedule config — lives at configuration.schedule (never interpolated). */
export const ScheduleConfigSchema = z.object({
  cron: z.string().regex(cronPattern).optional()
    .describe('The cron schedule. Cannot be an interpolated value.'),
  timezone: z.enum(timezoneValues).optional()
    .describe('The timezone used to evaluate the cron expression.'),
  enabled: z.boolean().optional()
    .describe('UniversalTriggerActor only: when false no cron job is registered.'),
});

/** The ScheduledTriggerActor options are empty — all schedule config is static. */
export const ScheduledTriggerActorOptionsSchema = z.object({});

export type ScheduledTriggerActorOptions = z.infer<typeof ScheduledTriggerActorOptionsSchema>;

/** The result schema for the ScheduledTriggerActor */
export const ScheduledTriggerActorResultSchema = z.object({
  lastTriggeredAt: z.iso.datetime().nullable()
    .describe('The last time the trigger was triggered'),
  triggeredAt: z.iso.datetime()
    .describe('The time the trigger was triggered'),
});

export type ScheduledTriggerActorResult = z.infer<typeof ScheduledTriggerActorResultSchema>;
```

### Validation Rules

- `schedule` must be a valid cron expression matching the pattern
- `timezone` must be a valid IANA timezone (from `Intl.supportedValuesOf('timeZone')`)
- `schedule` does **not** support interpolated values (`${{ }}` expressions)

### Special Cron Shortcuts

The cron pattern also supports these shortcuts:

| Shortcut | Equivalent |
|----------|------------|
| `@annually` / `@yearly` | `0 0 1 1 *` |
| `@monthly` | `0 0 1 * *` |
| `@weekly` | `0 0 * * 0` |
| `@daily` | `0 0 * * *` |
| `@hourly` | `0 * * * *` |
| `@every 1h` | Every hour |
| `@every 30m` | Every 30 minutes |

### Schedule (Cron Expression)

The `schedule` option uses standard cron syntax:

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, 0=Sunday)
│ │ │ │ │
* * * * *
```

### Cron Expression Examples

| Expression | Description |
|------------|-------------|
| `* * * * *` | Every minute |
| `0 * * * *` | Every hour (at minute 0) |
| `0 0 * * *` | Every day at midnight |
| `0 9 * * *` | Every day at 9:00 AM |
| `0 9 * * 1-5` | Every weekday at 9:00 AM |
| `0 0 1 * *` | First day of every month at midnight |
| `0 */2 * * *` | Every 2 hours |
| `*/15 * * * *` | Every 15 minutes |
| `0 9,17 * * *` | At 9:00 AM and 5:00 PM daily |
| `0 0 * * 0` | Every Sunday at midnight |

### Special Characters

| Character | Description |
|-----------|-------------|
| `*` | Any value |
| `,` | Value list separator (e.g., `1,3,5`) |
| `-` | Range of values (e.g., `1-5`) |
| `/` | Step values (e.g., `*/15` = every 15) |

### Timezone

Specify the timezone using IANA timezone names:

| Timezone | Description |
|----------|-------------|
| `America/New_York` | Eastern Time (US) |
| `America/Los_Angeles` | Pacific Time (US) |
| `Europe/London` | British Time |
| `Europe/Paris` | Central European Time |
| `Asia/Tokyo` | Japan Standard Time |
| `Australia/Sydney` | Australian Eastern Time |

See [IANA Time Zone Database](https://www.iana.org/time-zones) for complete list.

## Emitted Message

The scheduled trigger emits a message containing schedule execution details:

```json
{
  "triggeredAt": "2024-01-15T09:00:00Z",
  "lastTriggeredAt": "2024-01-15T08:00:00Z"
}
```

| Field | Description |
|-------|-------------|
| `triggeredAt` | ISO 8601 timestamp when the trigger fired |
| `lastTriggeredAt` | ISO 8601 timestamp of the previous trigger (null if first run) |

## Common Patterns

### Every Hour

```yaml
configuration:
  schedule:
    cron: '0 * * * *'
    timezone: America/New_York
```

### Daily at Specific Time

```yaml
configuration:
  schedule:
    cron: '0 9 * * *'  # 9:00 AM
    timezone: America/New_York
```

### Weekdays Only

```yaml
configuration:
  schedule:
    cron: '0 8 * * 1-5'  # 8:00 AM, Monday-Friday
    timezone: Europe/London
```

### Multiple Times Per Day

```yaml
configuration:
  schedule:
    cron: '0 9,12,17 * * *'  # 9 AM, 12 PM, 5 PM
    timezone: America/Los_Angeles
```

### Weekly Report

```yaml
configuration:
  schedule:
    cron: '0 9 * * 1'  # Every Monday at 9:00 AM
    timezone: America/New_York
```

### Monthly Task

```yaml
configuration:
  schedule:
    cron: '0 0 1 * *'  # First day of each month at midnight
    timezone: America/New_York
```

## Accessing in Downstream Actors

```yaml
# In HttpRequestActor
configuration:
  inputs:
    triggeredAt: ${{ msg.scheduled_trigger.triggeredAt }}
    lastTriggeredAt: ${{ msg.scheduled_trigger.lastTriggeredAt }}
  options:
    url: https://api.example.com/sync
    method: POST
    body:
      triggeredAt: ${{ inputs.triggeredAt }}
      lastTriggeredAt: ${{ inputs.lastTriggeredAt }}
      type: scheduled
```

```typescript
// In DenoActor
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const trigger = req.inputs;

  console.log(`Scheduled execution at: ${trigger.triggeredAt}`);
  console.log(`Last triggered at: ${trigger.lastTriggeredAt}`);

  // Perform scheduled task
  const syncResults = await performScheduledSync();

  return {
    results: {
      executedAt: trigger.triggeredAt,
      results: syncResults,
    },
  };
}
```

## Using LTM for Incremental Processing

Combine scheduled triggers with LTM to track state between runs:

```typescript
import type { Request, Response } from "@borgiq/actors";
import _ from "npm:lodash@4.17.21";

export default async function receive(req: Request): Promise<Response> {
  // Use lastTriggeredAt from the trigger (or fall back to LTM for custom tracking)
  const lastRunAt = req.inputs.lastTriggeredAt || _.get(req.memory.ltm, "lastRunAt", null);

  // Fetch only new items since last run
  const items = await fetchItemsSince(lastRunAt);

  // Process items
  for (const item of items) {
    await processItem(item);
  }

  // Update last run timestamp in LTM (optional, since trigger provides lastTriggeredAt)
  _.set(req.memory.ltm, "lastRunAt", req.inputs.triggeredAt);

  return {
    results: {
      processedCount: items.length,
      lastRunAt: req.inputs.triggeredAt,
    },
    memory: req.memory,
  };
}
```

**Note:** The `lastTriggeredAt` field from the trigger provides the previous execution time, so you may not need to track this in LTM. However, LTM is still useful for tracking custom state like processed record IDs or cursors.

## Use Cases

### Data Synchronization

Sync data between systems at regular intervals:

1. ScheduledTriggerActor runs hourly
2. DenoActor fetches new records from source
3. HttpRequestActor updates destination system

### Scheduled Reports

Generate and send reports on schedule:

1. ScheduledTriggerActor runs weekly
2. HttpRequestActor fetches report data
3. AiActor summarizes data
4. HttpRequestActor sends email with report

### Health Checks

Monitor system health periodically:

1. ScheduledTriggerActor runs every 5 minutes
2. HttpRequestActors check various endpoints
3. RouterActor routes based on status
4. Notification sent if issues detected

### Cleanup Jobs

Run maintenance tasks regularly:

1. ScheduledTriggerActor runs daily at 2 AM
2. DenoActor identifies old records
3. HttpRequestActor archives or deletes records

## Best Practices

1. **Use appropriate intervals** - Don't run more frequently than necessary
2. **Consider timezone** - Set timezone to match your business hours
3. **Implement idempotency** - Handle cases where trigger might fire twice
4. **Use LTM for state** - Track last run time for incremental processing
5. **Handle failures gracefully** - Use `continueOnError` or error handling
6. **Monitor execution** - Track execution times and success rates

## Quick Example

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kd2993qzx0a9q8btbmcf3fda:
    type: ScheduledTriggerActor
    version: 1
    name: Hourly Sync Trigger
    msgVar: hourly_sync_trigger
    description: Trigger data synchronization every hour
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      schedule:
        cron: '0 * * * *'
        timezone: America/New_York
    schemas: {}
    id: ACTR01kd2993qzx0a9q8btbmcf3fda
    position:
      x: 0
      'y': 0
    edges: {}
```
