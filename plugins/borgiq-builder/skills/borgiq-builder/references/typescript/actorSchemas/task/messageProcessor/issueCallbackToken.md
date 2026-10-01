# actorSchemas/task/messageProcessor/issueCallbackToken

Generated from the platform's runtime types. Do not edit.

The options schema for the issueCallbackToken action in the MessageProcessorActor.

See also: [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/issueCallbackToken

**Source:** `actorSchemas/task/messageProcessor/issueCallbackToken.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the issueCallbackToken action in the MessageProcessorActor */
export const MessageProcessorActorIssueCallbackTokenOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.IssueCallbackToken)
    .describe('Must be issueCallbackToken to access this function'),
  expiresAfterInSeconds: z.number().gt(0).nullish()
    .describe('How long the callback token should be valid for'),
  multipleResponse: z.boolean().nullish()
    .describe('If true, the callback token can be used to continue multiple Message Processor Actor with waitForCallbackToken action'),
});

export type MessageProcessorActorIssueCallbackTokenOptions = z.infer<typeof MessageProcessorActorIssueCallbackTokenOptionsSchema>;

export const MessageProcessorActorIssueCallbackTokenOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.IssueCallbackToken,
    },
    expiresAfterInSeconds: {
      type: BIQJsonSchemaType.Number,
      exclusiveMinimum: 0,
      title: 'Expires after in seconds',
      description: 'How long the callback token should be valid for',
    },
    multipleResponse: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Multiple response',
      description: 'If true, the callback token can be used to continue multiple Message Processor Actor with waitForCallbackToken action',
      default: false,
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['action'],
};

/** The emitted message schema for the issueCallbackToken action in the MessageProcessorActor */
export const MessageProcessorActorIssueCallbackTokenResultSchema = z.object({
  token: z.string()
    .describe('The generated callback token'),
  url: z.string()
    .describe('The URL to resolve the callback token'),
  expiresAt: z.string()
    .describe('The time the token would expire'),
  multipleResponse: z.boolean()
    .describe('If the token can be used to continue multiple Message Processor Actor with waitForCallbackToken action'),
});

export type MessageProcessorActorIssueCallbackTokenResult = z.infer<typeof MessageProcessorActorIssueCallbackTokenResultSchema>;
```
