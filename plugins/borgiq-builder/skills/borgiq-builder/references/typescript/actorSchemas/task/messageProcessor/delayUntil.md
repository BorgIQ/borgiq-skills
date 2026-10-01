# actorSchemas/task/messageProcessor/delayUntil

Generated from the platform's runtime types. Do not edit.

The options schema for the delayUntil action in the MessageProcessorActor.

See also: [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/delayUntil

**Source:** `actorSchemas/task/messageProcessor/delayUntil.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the delayUntil action in the MessageProcessorSchema */
export const MessageProcessorActorDelayUntilOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.DelayUntil)
    .describe('Must be delayUntil to access this function'),
  until: z.iso.datetime()
    .describe('The time to delay emitting the message at'),
});

export type MessageProcessorActorDelayUntilOptions = z.infer<typeof MessageProcessorActorDelayUntilOptionsSchema>;

export const MessageProcessorActorDelayUntilOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.DelayUntil,
    },
    until: {
      type: BIQJsonSchemaType.String,
      format: 'date-time',
      title: 'Until',
      description: 'The time to delay emitting the message at',
    },
  },
  required: ['action', 'until'],
};
```
