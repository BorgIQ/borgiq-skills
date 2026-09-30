# actorSchemas/task/webhookResponse

Generated from the platform's runtime types. Do not edit.

The options schema for the WebhookResponseActor.

## actorSchemas/task/webhookResponse

**Source:** `actorSchemas/task/webhookResponse.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

/** The options schema for the WebhookResponseActor */
export const WebhookResponseActorOptionsSchema = z.object({
  statusCode: z.number().nullish()
    .describe('The status code of the response to return to the webhook request, defaults to 200'),
  body: z.unknown().nullish()
    .describe('The body of the response to return to the webhook request'),
  headers: z.record(z.string(), z.unknown()).nullish()
    .describe('The headers of the response to return to the webhook request'),
});

export type WebhookResponseActorOptions = z.infer<typeof WebhookResponseActorOptionsSchema>;

export const WebhookResponseActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    statusCode: {
      type: BIQJsonSchemaType.Number,
      title: 'Status code',
      description: 'The status code of the response to return to the webhook request, defaults to 200',
      default: 200,
    },
    body: {
      type: BIQJsonSchemaType.Any,
      title: 'Body',
      description: 'The body of the response to return to the webhook request',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
    headers: {
      type: BIQJsonSchemaType.Any,
      title: 'Headers',
      description: 'The headers of the response to return to the webhook request',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
  },
};

/** The result schema for the WebhookResponseActor */
export const WebhookResponseActorResultSchema = z.object({
  statusCode: z.number()
    .describe('The status code of the response to return to the webhook request'),
  body: z.unknown()
    .describe('The body of the response to return to the webhook request'),
  headers: z.record(z.string(), z.unknown()).nullable()
    .describe('The headers of the response to return to the webhook request'),
});

export type WebhookResponseActorResult = z.infer<typeof WebhookResponseActorResultSchema>;
```
