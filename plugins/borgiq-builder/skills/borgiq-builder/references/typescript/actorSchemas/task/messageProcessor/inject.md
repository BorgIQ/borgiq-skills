# actorSchemas/task/messageProcessor/inject

Generated from the platform's runtime types. Do not edit.

The options schema for the inject action in the MessageProcessorActor.

See also: [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/inject

**Source:** `actorSchemas/task/messageProcessor/inject.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the inject action in the MessageProcessorActor */
export const MessageProcessorActorInjectOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.Inject)
    .describe('Must be inject to access this function'),
  payload: z.any()
    .describe('The value to be the actors emit message'),
});

export type MessageProcessorActorInjectOptions = z.infer<typeof MessageProcessorActorInjectOptionsSchema>;

export const MessageProcessorActorInjectOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.Inject,
    },
    payload: {
      type: BIQJsonSchemaType.Any,
      title: 'Payload',
      description: 'The value to be the actors emit message',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
  },
  required: ['action', 'payload'],
};

/** The emitted message schema for the inject action in the MessageProcessorActor */
export const MessageProcessorActorInjectResultSchema = z.any().describe('The payload of the inject action');

export type MessageProcessorActorInjectResult = z.infer<typeof MessageProcessorActorInjectResultSchema>;
```
