# actorSchemas/task/messageProcessor/dedupeByTime

Generated from the platform's runtime types. Do not edit.

The options schema for the dedupeByTime action in the MessageProcessorActor.

See also: [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/dedupeByTime

**Source:** `actorSchemas/task/messageProcessor/dedupeByTime.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the dedupeByTime action in the MessageProcessorActor */
export const MessageProcessorActorDedupeByTimeOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.DedupeByTime)
    .describe('Must be dedupeByTime to access this function'),
  dedupeKey: z.any()
    .describe('The key to perform the deduplicate action by'),
  lookbackInSeconds: z.number().gt(0)
    .describe('The number of seconds to look back to to check if a message has been emitted with key'),
  emitAlways: z.boolean()
    .describe('If true, the actor would emit the message even if it has been emitted before'),
});

export type MessageProcessorActorDedupeByTimeOptions = z.infer<typeof MessageProcessorActorDedupeByTimeOptionsSchema>;

export const MessageProcessorActorDedupeByTimeOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.DedupeByTime,
    },
    dedupeKey: {
      type: BIQJsonSchemaType.Any,
      title: 'Dedupe key',
      description: 'The key to perform the deduplicate action by',
    },
    lookbackInSeconds: {
      type: BIQJsonSchemaType.Number,
      title: 'Lookback in seconds',
      description: 'The number of seconds to look back to to check if a message has been emitted with key',
      exclusiveMinimum: 0,
    },
    emitAlways: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit always',
      description: 'If true, the actor would emit the message even if it has been emitted before',
      default: false,
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['action', 'dedupeKey', 'lookbackInSeconds', 'emitAlways'],
};

/** The emitted message schema for the dedupeByTime action in the MessageProcessorActor */
export const MessageProcessorActorDedupeByTimeResultSchema = z.object({
  dedupeKey: z.any()
    .describe('The key that the message was deduplicated by'),
  unique: z.boolean()
    .describe('If the message key is unique across the time, will only be false if emitAlways in the options is set to true'),
});

export type MessageProcessorActorDedupeByTimeResult = z.infer<typeof MessageProcessorActorDedupeByTimeResultSchema>;
```
