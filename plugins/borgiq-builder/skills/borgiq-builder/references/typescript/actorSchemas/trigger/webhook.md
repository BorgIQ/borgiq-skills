# actorSchemas/trigger/webhook

Generated from the platform's runtime types. Do not edit.

The options schema for the WebhookTriggerActor.

See also: [schemas/runtime](../../schemas/runtime.md), [actorSchemas/trigger/triggerConfig](triggerConfig.md).

## actorSchemas/trigger/webhook

**Source:** `actorSchemas/trigger/webhook.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema } from '../../schemas/jsonSchema.js';
import { WebhookTriggerAuthSchema, WebhookTriggerRequestUserSchema } from '../../schemas/runtime.js';

import { WebhookBehaviorOptionsSchema, WebhookBehaviorOptionsJsonSchema } from './triggerConfig.js';

/**
 * The options schema for the WebhookTriggerActor.
 *
 * Only interpolatable webhook *behavior* lives here, nested under `webhook` (the same shape the
 * UniversalTriggerActor uses). Static, admission-consumed fields (triggerKey, authorizationLevel,
 * allowedMethods, responseTimeout) live in `configuration.webhook` — see {@link WebhookConfigSchema}.
 */
export const WebhookTriggerActorOptionsSchema = z.object({
  webhook: WebhookBehaviorOptionsSchema.nullish(),
});

export type WebhookTriggerActorOptions = z.infer<typeof WebhookTriggerActorOptionsSchema>;

export const WebhookTriggerActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    webhook: WebhookBehaviorOptionsJsonSchema,
  },
};

/** The response schema for the WebhookTriggerActor */
export const WebhookTriggerActorResultSchema = z.object({
  meta: z.object({
    requestId: z.string()
      .describe('The request id of the webhook request'),
    ipAddress: z.string().optional()
      .describe('The IP address of the webhook request'),
    user: WebhookTriggerRequestUserSchema.optional()
      .describe('The authenticated caller when the request carried an app actor webhook token or an API key; absent on public calls'),
    auth: WebhookTriggerAuthSchema.optional()
      .describe('Which API key authenticated the request (id and name, never the secret); present only on API-key-authenticated calls'),
  }),
  method: z.string().nullish()
    .describe('The method of the request. Valid methods are GET, POST, PUT, DELETE'),
  headers: z.record(z.string(), z.any()).nullish()
    .describe('The headers sent with the request'),
  body: z.any().nullish()
    .describe('The body sent with the request'),
  queryParams: z.any().nullish()
    .describe('The query parameters sent with the request'),
  rawBody: z.string().nullish()
    .describe('The raw body of the request if emitRawBody was set to true in the options'),
  response: z.object({
    statusCode: z.number(),
    headers: z.record(z.string(), z.unknown()).nullish(),
    body: z.any().nullish(),
  }).nullish()
    .describe('The response to the webhook request if respondImmediately was set to true'),
});

export type WebhookTriggerActorResult = z.infer<typeof WebhookTriggerActorResultSchema>;
```
