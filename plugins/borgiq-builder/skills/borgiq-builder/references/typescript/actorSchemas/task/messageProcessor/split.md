# actorSchemas/task/messageProcessor/split

Generated from the platform's runtime types. Do not edit.

The options schema for the split action in the MessageProcessorActor.

See also: [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/split

**Source:** `actorSchemas/task/messageProcessor/split.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the split action in the MessageProcessorActor */
export const MessageProcessorActorSplitOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.Split)
    .describe('Must be split to access this function'),
  valueToSplit: z.array(z.unknown())
    .describe('The value to split'),
  emitKey: z.string().nullish()
    .describe('the key for the split values to be send under in the emitted message'),
  limit: z.number().nullish()
    .describe('The limit for the maximum number of messages that will be emitted, defaults to 1000'),
});

export type MessageProcessorActorSplitOptions = z.infer<typeof MessageProcessorActorSplitOptionsSchema>;

export const MessageProcessorActorSplitOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.Split,
    },
    valueToSplit: {
      type: BIQJsonSchemaType.Array,
      title: 'Value to split',
      description: 'The value to split',
      default: '${{}}',
      items: {
        type: BIQJsonSchemaType.Any,
      },
    },
    emitKey: {
      type: BIQJsonSchemaType.String,
      title: 'Emit key',
      description: 'The key for the split values to be send under in the emitted message',
      default: 'item',
    },
    limit: {
      type: BIQJsonSchemaType.Number,
      title: 'Limit',
      description: 'The limit for the maximum number of messages that will be emitted, defaults to 1000',
    },
  },
  required: ['action', 'valueToSplit'],
};

/** The emitted message schema for the split action in the MessageProcessorActor */
export const MessageProcessorActorSplitResultSchema = z.object({
  splitId: z.string()
    .describe('the id of the split action to be used in future Message Processor Actor with collect action, will be the same for all the emitted messages from the same array'),
  index: z.number()
    .describe('The index of the split value from the original array'),
  size: z.number()
    .describe('the total size of the array'),
});

export type MessageProcessorActorSplitResult = z.infer<typeof MessageProcessorActorSplitResultSchema> & { [key: string]: unknown };
```
