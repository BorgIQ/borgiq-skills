# actorSchemas/trigger/universalTrigger

Generated from the platform's runtime types. Do not edit.

The UniversalTriggerActor's `configuration.codeDir`: a project tree whose handler lives in `main.ts`, minus the paths the Deno bootstrap owns.

See also: [actorSchemas/codeDir](../codeDir.md), [actorSchemas/task/deno](../task/deno.md), [actorSchemas/trigger/triggerConfig](triggerConfig.md), [schemas/trigger](../../schemas/trigger.md).

## actorSchemas/trigger/universalTrigger

**Source:** `actorSchemas/trigger/universalTrigger.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema } from '../../schemas/jsonSchema.js';
import { DENO_RESERVED_PATHS, makeCodeDirSchema, UNIVERSAL_TRIGGER_ACTOR_ENTRYPOINT } from '../codeDir.js';
import { DenoActorOptionsJsonSchema } from '../task/deno.js';

import { WebhookBehaviorOptionsSchema, WebhookBehaviorOptionsJsonSchema } from './triggerConfig.js';

export { TriggerEventSchema, type TriggerEvent } from '../../schemas/trigger.js';

/**
 * The UniversalTriggerActor's `configuration.codeDir`: a project tree whose handler lives in
 * `main.ts`, minus the paths the Deno bootstrap owns. This type has its own `universal-trigger`
 * bootstrap variant, but that variant is the `deno-actor` one plus a trigger-aware handler — same
 * entry chain, same shared kernel, and its own `main_test.ts` harness — so it reserves the same set.
 */
export const UniversalTriggerActorCodeDirSchema = makeCodeDirSchema({
  requiredEntrypoint: UNIVERSAL_TRIGGER_ACTOR_ENTRYPOINT,
  reservedPaths: DENO_RESERVED_PATHS,
});

/**
 * The options for the UniversalTriggerActor (the interpolated `options` blob).
 *
 * Deno runtime fields live at root; interpolatable webhook *behavior* is nested under `webhook`
 * (shared with the standalone WebhookTriggerActor). The STATIC, admission-consumed source config
 * (webhook triggerKey/authorizationLevel/allowedMethods/responseTimeout/enabled and schedule
 * cron/timezone/enabled) lives in `configuration.webhook` / `configuration.schedule`, not here.
 */
export const UniversalTriggerActorOptionsSchema = z.object({
  // --- deno runtime options (root) ---
  emitArrayAsSingleMessage: z.boolean().nullish()
    .describe('Emit the array as a single message instead of an array of messages, defaults to true').default(true),
  allowNet: z.boolean().nullish()
    .describe('Allow network access. By default when this is true, all network calls are allowed; allowNetList narrows the set.').default(false),
  allowNetList: z.array(z.string()).nullish()
    .describe('List of URLs that are allowed to be accessed when allowNet is true.').default([]),
  denyNetList: z.array(z.string()).nullish()
    .describe('List of URLs that are denied to be accessed when allowNet is true.').default([]),
  allowFs: z.boolean().nullish()
    .describe('Allow file system access to the temporary directory.').default(false),
  env: z.array(z.object({
    name: z.string()
      .regex(/^[A-Z0-9_]+$/, 'Environment variable name must contain only uppercase letters, numbers and underscores')
      .regex(/^(?!TMPDIR$)/, 'Environment variable name cannot be TMPDIR')
      .regex(/^(?!DENO_NO_UPDATE_CHECK$)/, 'Environment variable name cannot be DENO_NO_UPDATE_CHECK'),
    value: z.string().nullish(),
  })).nullish().default([])
    .describe('Environment variables exposed to the Deno runtime.'),
  // --- interpolatable webhook behavior (shared with WebhookTriggerActor) ---
  webhook: WebhookBehaviorOptionsSchema.nullish(),
});

export type UniversalTriggerActorOptions = z.infer<typeof UniversalTriggerActorOptionsSchema>;

// Memory is fully opt-in for UniversalTriggerActor — no infrastructure code reads or
// writes LTM/STM on the user's behalf. User code can persist anything (including a
// per-fire `lastTriggeredAt`) via `req.memory.ltm` (returned in `Response.memory`) if it enables LTM in advanced settings.
// Intentionally no `UniversalTriggerActorMemory` constant — the generic Actor.validate()
// in the lambda picks up `${type}Memory` by naming convention and would otherwise
// require LTM/STM on every event (including webhook-only).

/** JSON Schema for the editor's schema-driven configuration form (interpolatable options only). */
export const UniversalTriggerActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    ...DenoActorOptionsJsonSchema.properties,
    webhook: WebhookBehaviorOptionsJsonSchema,
  },
};

/** The response schema for the UniversalTriggerActor (user code can emit any JSON). */
export const UniversalTriggerActorResultSchema = z.any();

export type UniversalTriggerActorResult = z.infer<typeof UniversalTriggerActorResultSchema>;
```
