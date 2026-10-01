# actorSchemas/trigger/triggerConfig

Generated from the platform's runtime types. Do not edit.

Static trigger configuration shared by the webhook, scheduled and universal triggers: webhook authorization, schedule `cron` and `timezone`, lifecycle events.

See also: [canvas](../../canvas.md).

## actorSchemas/trigger/triggerConfig

**Source:** `actorSchemas/trigger/triggerConfig.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType, BIQObjectJsonSchema } from '../../schemas/jsonSchema.js';
import { BIQWebhookAuthorizationLevel } from '../../canvas.js';

/**
 * Shared building blocks for the unified trigger-actor config data model.
 *
 * The webhook/schedule configuration is split along the interpolation boundary that
 * already exists in the platform: `configuration.options` is the interpolated blob
 * (run through the `${{ }}` engine in the runtime, with the request in scope), while
 * structured config siblings (like `connection`) are never interpolated.
 *
 *  - STATIC, admission-consumed fields live in `configuration.webhook` / `configuration.schedule`
 *    (these schemas). They must be literals — expressions are rejected.
 *  - INTERPOLATABLE behavior fields live inside the interpolated `options` blob, under
 *    `options.webhook` ({@link WebhookBehaviorOptionsSchema}).
 */

// the regex of the cron schedule is from https://gist.github.com/Aterfax/401875eb3d45c9c114bbef69364dd045
export const cronPattern = /^((((\d+,)+\d+|(\d+(\/|-|#)\d+)|\d+L?|\*(\/\d+)?|L(-\d+)?|\?|[A-Z]{3}(-[A-Z]{3})?) ?){5})|(@(annually|yearly|monthly|weekly|daily|hourly|reboot))|(@every (\d+(m|h))+)$/;

// list of all the supported timezones
export const timezoneValues = Intl.supportedValuesOf('timeZone');

/** Matches a string that is a single `${{ ... }}` interpolation expression. */
export const EXPRESSION_REGEX = /^\$\{\{\s*((?:(?!\$\{\{)[\s\S])*?)\s*\}\}$/;

/** Adds a validation issue when a static (non-interpolatable) string field holds a `${{ }}` expression. */
const rejectExpression = (value: unknown, ctx: z.RefinementCtx, field: string): void => {
  if (typeof value === 'string' && EXPRESSION_REGEX.test(value)) {
    ctx.addIssue({
      code: 'custom',
      message: `${field} must be a literal value and cannot be an interpolated \${{ }} expression`,
      path: [field],
    });
  }
};

/**
 * STATIC webhook config — lives at `configuration.webhook` (sibling of `options`/`connection`).
 * Consumed by the orchestrator at admission (routing, auth, method gate, wait bound, source gate),
 * so every field must be a literal and is DB-queryable. `enabled` is only meaningful for the
 * UniversalTriggerActor; the standalone WebhookTriggerActor is always enabled when present.
 */
export const WebhookConfigSchema = z.object({
  triggerKey: z.string().optional()
    .describe('The unique key in the webhook URL used to route requests to this actor.'),
  authorizationLevel: z.enum(BIQWebhookAuthorizationLevel).optional()
    .describe('Who can call this webhook. \'public\' allows anyone, \'apps\' requires a valid app webhook token, \'apiKey\' requires a valid API key (a personal access token in Authorization: Bearer or X-Api-Key), \'appsAndApiKey\' accepts either.'),
  allowedMethods: z.array(z.enum(['get', 'post', 'put', 'delete'])).optional()
    .describe('HTTP methods accepted by the webhook URL.'),
  responseTimeout: z.number().gte(1).lte(60).optional()
    .describe('How long (seconds) the request is held open waiting for a WebhookResponse actor. Max 60s, defaults to 30s.'),
  enabled: z.boolean().optional()
    .describe('UniversalTriggerActor only: when false the webhook URL returns 404 and no flowruns are created.'),
}).superRefine((data, ctx) => {
  rejectExpression(data.triggerKey, ctx, 'triggerKey');
});

export type WebhookConfig = z.infer<typeof WebhookConfigSchema>;

/**
 * STATIC schedule config — lives at `configuration.schedule`. Schedule has no interpolatable
 * fields: `cron` is read at admission to register the cron job (and the engine cannot interpolate
 * it), `timezone`/`enabled` are admission-time too. So all of it is static — there is no
 * `options.schedule`.
 */
export const ScheduleConfigSchema = z.object({
  cron: z.string().regex(cronPattern).optional()
    .describe('The cron schedule. Cannot be an interpolated value.'),
  timezone: z.enum(timezoneValues).optional()
    .describe('The timezone used to evaluate the cron expression.'),
  enabled: z.boolean().optional()
    .describe('UniversalTriggerActor only: when false no cron job is registered.'),
  preventOverlappingFlowruns: z.boolean().optional()
    .describe('ScheduledTriggerActor only (ignored by UniversalTriggerActor): when true, a scheduled flowrun is skipped if the previous flowrun is still in progress.'),
}).superRefine((data, ctx) => {
  rejectExpression(data.cron, ctx, 'cron');
});

export type ScheduleConfig = z.infer<typeof ScheduleConfigSchema>;

/**
 * The lifecycle transitions deliverable on the `lifecycle` trigger event.
 *
 * Single source of truth: the TriggerEvent variant, the flowrun payload schema, the API input
 * schema, and the lambda runtime's `buildTrigger` check all derive from this const. The vocabulary
 * grows by extending this list, never by adding a TriggerEvent union member. Lives here (rather
 * than beside the TriggerEvent variant in `schemas/trigger.ts`) because both `schemas/trigger.ts`
 * and `schemas/runtime.ts` need it, and this module is downstream of neither — importing it from
 * `schemas/trigger.ts` would make those two modules circular and TDZ-crash at module init.
 */
export const LIFECYCLE_TRIGGER_EVENTS = ['canvas-enabled', 'canvas-disabled', 'on-delete'] as const;

export type LifecycleTriggerEvent = typeof LIFECYCLE_TRIGGER_EVENTS[number];

/**
 * Display copy for each lifecycle event, used by the editor's subscription checkboxes.
 *
 * Typed as an exhaustive `Record` on purpose: adding a value to {@link LIFECYCLE_TRIGGER_EVENTS}
 * without adding its metadata here is a compile error rather than an unlabelled checkbox.
 */
export const LIFECYCLE_TRIGGER_EVENT_META: Record<LifecycleTriggerEvent, { label: string; description: string }> = {
  'canvas-enabled': { label: 'Canvas enabled', description: 'Fired when the canvas is deployed.' },
  'canvas-disabled': { label: 'Canvas disabled', description: 'Fired when the canvas is undeployed.' },
  'on-delete': {
    label: 'On delete',
    description: 'For unregistering anything you registered externally when this actor goes away. Not delivered automatically yet: run it by hand from the editor in a development workspace to test your handler. Delivery when a deployed canvas, its workspace or its organization is deleted is coming. It can arrive more than once, so make the handler idempotent.',
  },
};

/**
 * Which level an `on-delete` lifecycle event is about: the actor itself, or the canvas / workspace / org
 * it lived in. One event with a scope, rather than an event per level, so an author subscribes once and
 * branches. The event's shape is `FlowrunLifecycleTriggerDataSchema` in `schemas/runtime.ts`.
 *
 * TODO: only `'actor'` is sent today, by a hand-run test fire (`manual: true`) in a
 * development workspace. `'canvas'`, `'workspace'` and `'org'` are reserved for automatic delivery on a
 * deployed workspace, which arrives with the deploy flow.
 */
export const LIFECYCLE_DELETE_SCOPES = ['actor', 'canvas', 'workspace', 'org'] as const;

export type LifecycleDeleteScope = typeof LIFECYCLE_DELETE_SCOPES[number];

/**
 * STATIC lifecycle config — lives at `configuration.lifecycle`. Like schedule, lifecycle
 * has no interpolatable fields: `events` is the subscription list read at fire time, so all of it
 * is static and there is no `options.lifecycle`.
 *
 * Subscription is PER EVENT, not a single on/off flag: {@link LIFECYCLE_TRIGGER_EVENTS} is the
 * growth axis for this feature, so a flag would silently opt every subscribed actor into events
 * added later. Absent block, absent `events`, and `events: []` all mean unsubscribed.
 */
export const LifecycleConfigSchema = z.object({
  events: z.array(z.enum(LIFECYCLE_TRIGGER_EVENTS)).optional()
    .describe('UniversalTriggerActor only: the lifecycle events this actor is subscribed to. Absent or empty means the actor receives none.'),
});

export type LifecycleConfig = z.infer<typeof LifecycleConfigSchema>;

/**
 * Whether an actor's static lifecycle config subscribes it to `event`. The single place the
 * subscription question is answered — the fire gate in `Trigger.lifecycle()` uses it, and the
 * canvas-deploy engine will use it to pick out subscribed actors before fanning out.
 */
export const isSubscribedToLifecycleEvent = (config: LifecycleConfig | undefined, event: LifecycleTriggerEvent): boolean =>
  config?.events?.includes(event) === true;

/**
 * INTERPOLATABLE webhook behavior — lives inside the interpolated `options` blob at
 * `options.webhook`. Reused by the standalone WebhookTriggerActor's options and by the
 * UniversalTriggerActor's options. Fields accept their literal type OR a `${{ }}` string so
 * an un-interpolated expression validates at save time; the runtime resolves it before reading.
 */
export const WebhookBehaviorOptionsSchema = z.object({
  respondImmediately: z.union([z.boolean(), z.string()]).nullish()
    .describe('If true, the configured response is returned immediately; otherwise a downstream WebhookResponse actor must respond.'),
  emitRawBody: z.union([z.boolean(), z.string()]).nullish()
    .describe('If true the raw request body is included on the emitted event.request.rawBody.'),
  response: z.object({
    statusCode: z.union([z.number(), z.string()]),
    headers: z.record(z.string(), z.unknown()).nullish(),
    body: z.unknown(),
  }).nullish()
    .describe('The response returned when respondImmediately is true.'),
});

export type WebhookBehaviorOptions = z.infer<typeof WebhookBehaviorOptionsSchema>;

/** JSON Schema for the static `configuration.webhook` editor (Settings sub-group — no `${{ }}` toggle). */
export const WebhookConfigJsonSchema: BIQJsonSchema = {
  properties: {
    triggerKey: {
      type: BIQJsonSchemaType.String,
      title: 'Trigger key',
      description: 'The unique key in the webhook URL used to route requests to this actor.',
    },
    authorizationLevel: {
      type: BIQJsonSchemaType.String,
      title: 'Authorization level',
      description: 'Control who can call this webhook.',
      enum: [BIQWebhookAuthorizationLevel.Public, BIQWebhookAuthorizationLevel.Apps, BIQWebhookAuthorizationLevel.ApiKey, BIQWebhookAuthorizationLevel.AppsAndApiKey],
    },
    allowedMethods: {
      type: BIQJsonSchemaType.Array,
      title: 'Allowed methods',
      description: 'HTTP methods accepted by the webhook URL.',
      items: { type: BIQJsonSchemaType.String, enum: ['get', 'post', 'put', 'delete'] },
      uniqueItems: true,
    },
    responseTimeout: {
      type: BIQJsonSchemaType.Number,
      title: 'Response timeout',
      description: 'How long (seconds) the request is held open waiting for a Webhook Response actor. Maximum 60s, defaults to 30s.',
      minimum: 1,
      maximum: 60,
      default: 30,
    },
  },
};

/** JSON Schema for the static `configuration.schedule` editor. */
export const ScheduleConfigJsonSchema: BIQJsonSchema = {
  properties: {
    cron: {
      type: BIQJsonSchemaType.String,
      title: 'Schedule',
      description: 'The cron schedule to use for the trigger. Warning: You cannot use interpolated values in the schedule.',
      pattern: cronPattern.source,
    },
    timezone: {
      type: BIQJsonSchemaType.String,
      title: 'Timezone',
      description: 'The timezone used to evaluate the cron expression.',
      enum: timezoneValues,
      default: 'America/New_York',
      ui: { component: 'searchSelect' },
    },
  },
};

/** JSON Schema for the interpolatable `options.webhook` behavior editor (Response sub-group — with `${{ }}` toggle). */
export const WebhookBehaviorOptionsJsonSchema: BIQObjectJsonSchema = {
  type: BIQJsonSchemaType.Object,
  title: 'Webhook',
  description: 'Behavior for forming the webhook response. These fields are interpolated at runtime with the request in scope.',
  properties: {
    respondImmediately: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Respond immediately',
      description: 'If true, the configured response is returned immediately. If false a downstream Webhook Response actor must respond.',
      ui: { component: 'switch' },
    },
    emitRawBody: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit raw body',
      description: 'Include the raw request body on the emitted event.request.rawBody.',
      ui: { component: 'switch' },
    },
    response: {
      type: BIQJsonSchemaType.Object,
      title: 'Response',
      description: 'Response returned when respondImmediately is true.',
      properties: {
        statusCode: {
          type: BIQJsonSchemaType.Number,
          title: 'Status code',
          description: 'HTTP status code.',
        },
        headers: {
          type: BIQJsonSchemaType.Any,
          title: 'Headers',
          description: 'Response headers.',
          ui: { options: { editInModal: true } },
        },
        body: {
          type: BIQJsonSchemaType.Any,
          title: 'Body',
          description: 'Response body.',
          ui: { options: { editInModal: true } },
        },
      },
      required: ['statusCode'],
    },
  },
};
```
