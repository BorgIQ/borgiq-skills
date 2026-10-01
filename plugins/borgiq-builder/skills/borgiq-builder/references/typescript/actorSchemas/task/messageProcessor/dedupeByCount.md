# actorSchemas/task/messageProcessor/dedupeByCount

Generated from the platform's runtime types. Do not edit.

The options schema for the dedupeByCount action in the MessageProcessorActor.

See also: [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/dedupeByCount

**Source:** `actorSchemas/task/messageProcessor/dedupeByCount.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options action for the dedupeByCount action in the MessageProcessActor */
export const MessageProcessorActorDedupeByCountOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.DedupeByCount)
    .describe('Must be dedupeByCount to access this function'),
  dedupeKey: z.any()
    .describe('The key to perform the deduplicate action by'),
  lookbackAsCount: z.number().int().gt(0)
    .describe('The number of messages to look back to to check if a message has been emitted with key'),
  emitAlways: z.boolean()
    .describe('If true, the actor would emit the message even if it has been emitted before'),
});

export type MessageProcessorActorDedupeByCountOptions = z.infer<typeof MessageProcessorActorDedupeByCountOptionsSchema>;

export const MessageProcessorActorDedupeByCountOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.DedupeByCount,
    },
    dedupeKey: {
      type: BIQJsonSchemaType.Any,
      title: 'Dedupe key',
      description: 'The key to perform the deduplicate action by',
      default: '${{ }}',
    },
    lookbackAsCount: {
      type: BIQJsonSchemaType.Integer,
      title: 'Lookback as count',
      description: 'The number of messages to look back to to check if a message has been emitted with key',
      exclusiveMinimum: 0,
    },
    emitAlways: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit always',
      description: 'If true, the actor would emit the message even if it has been emitted before',
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['action', 'dedupeKey', 'lookbackAsCount', 'emitAlways'],
};

/** The emitted message schema for the dedupeByCount for the MessageProcessorActor */
export const MessageProcessorActorDedupeByCountResultSchema = z.object({
  dedupeKey: z.any()
    .describe('The key that the message was deduplicated by'),
  unique: z.boolean()
    .describe('If the message key is unique across the count, will only be false if emitAlways in the options is set to true'),
});

export type MessageProcessorActorDedupeByCountResult = z.infer<typeof MessageProcessorActorDedupeByCountResultSchema>;
```
