# actorSchemas/task/messageProcessor/collect

Generated from the platform's runtime types. Do not edit.

The options schema for the collect action in the MessageProcessorActor.

See also: [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/collect

**Source:** `actorSchemas/task/messageProcessor/collect.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the collect action in the MessageProcessorActor */
export const MessageProcessorActorCollectOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.Collect)
    .describe('Must be collect to access this function'),
  splitId: z.string()
    .describe('The split ID from the upstream Message Processor Actor with the split action that the values should be collected from'),
  size: z.number().int().gt(0)
    .describe('The total size of the array being collected, can be the size from the upstream split action'),
  captureValue: z.any()
    .describe('The value to collect and insert into the array'),
  emitKey: z.string().nullish()
    .describe('The key to emit the collected array under, defaults to message'),
  if: z.boolean().nullish()
    .describe('If provided the condition must evaluate to true for the value to be collected.'),
});

export type MessageProcessorActorCollectOptions = z.infer<typeof MessageProcessorActorCollectOptionsSchema>;

export const MessageProcessorActorCollectOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.Collect,
    },
    splitId: {
      type: BIQJsonSchemaType.String,
      title: 'Split ID',
      description: 'The split ID from the upstream Message Processor Actor with the split action that the values should be collected from',
      minLength: 1,
      default: '${{msg.SPLIT_ACTOR.splitId}}',
    },
    size: {
      type: BIQJsonSchemaType.Integer,
      title: 'Size',
      description: 'The total size of the array being collected, can be the size from the upstream split action',
      exclusiveMinimum: 0,
      default: '${{msg.SPLIT_ACTOR.size}}',
    },
    captureValue: {
      type: BIQJsonSchemaType.Any,
      title: 'Capture value',
      description: 'The value to collect and insert into the array',
      default: '${{msg}}',
    },
    emitKey: {
      type: BIQJsonSchemaType.String,
      title: 'Emit key',
      description: 'The key to emit the collected array under, defaults to message',
      default: 'items',
    },
    if: {
      type: BIQJsonSchemaType.Boolean,
      title: 'If',
      description: 'If provided the condition must evaluate to true for the value to be collected.',
      default: '${{true}}',
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['action', 'splitId', 'size', 'captureValue'],
};

/** The emitted message schema for the collect action in the MessageProcessActor */
export const MessageProcessorActorCollectResultSchema = z.record(z.string(),
  z.array(z.record(z.string(), z.any())),
);

export type MessageProcessorActorCollectResult = z.infer<typeof MessageProcessorActorCollectResultSchema>;
```
