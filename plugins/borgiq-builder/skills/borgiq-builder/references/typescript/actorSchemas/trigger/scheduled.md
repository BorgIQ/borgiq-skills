# actorSchemas/trigger/scheduled

Generated from the platform's runtime types. Do not edit.

The options schema for the ScheduledTriggerActor.

## actorSchemas/trigger/scheduled

**Source:** `actorSchemas/trigger/scheduled.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema } from '../../schemas/jsonSchema.js';

export const ScheduleTriggerActorMemory: { ltm?: boolean; stm?: boolean } = {
  ltm: true,
};

/**
 * The options schema for the ScheduledTriggerActor.
 *
 * Schedule has no interpolatable fields — `cron`/`timezone` are static and live in
 * `configuration.schedule` (see {@link ScheduleConfigSchema}). So options is empty.
 */
export const ScheduledTriggerActorOptionsSchema = z.object({});

export type ScheduledTriggerActorOptions = z.infer<typeof ScheduledTriggerActorOptionsSchema>;

export const ScheduledTriggerActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {},
};

export const ScheduledTriggerActorResultSchema = z.object({
  lastTriggeredAt: z.iso.datetime().nullable()
    .describe('The last time the trigger was triggered'),
  triggeredAt: z.iso.datetime()
    .describe('The time the trigger was triggered'),
});

export type ScheduledTriggerActorResult = z.infer<typeof ScheduledTriggerActorResultSchema>;
```
