# actorSchemas/task/dataStore/dequeue

Generated from the platform's runtime types. Do not edit.

Legacy: DataStoreActor is kept only so existing canvases load. Build new storage with CollectionActor.

The options schema for the dequeue action for the DataStoreActor.

See also: [schemas/jsonSchema](../../../schemas/jsonSchema.md), [actorSchemas/task/dataStore/actions](actions.md).

## actorSchemas/task/dataStore/dequeue

**Source:** `actorSchemas/task/dataStore/dequeue.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the dequeue action for the DataStoreActor */
export const DataStoreActorDequeueOptionsSchema = z.object({
  action: z.literal(DataStoreActorAction.Dequeue)
    .describe('Must be dequeue to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe('The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'),
  queueName: z.string().min(1)
    .describe('The name of the queue to dequeue from'),
  amount: z.number().int().nullish()
    .describe('The amount of items to dequeue from the queue, defaults to 1'),
});

export type DataStoreActorDequeueOptions = z.infer<typeof DataStoreActorDequeueOptionsSchema>;

export const DataStoreActorDequeueOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be dequeue to access this function',
      const: DataStoreActorAction.Dequeue,
    },
    scope: {
      type: BIQJsonSchemaType.String,
      title: 'Scope',
      description: 'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope',
      enum: ['canvas', 'workspace'],
      default: 'canvas',
    },
    queueName: {
      type: BIQJsonSchemaType.String,
      title: 'Queue name',
      description: 'The name of the queue to dequeue from',
      minLength: 1,
    },
    amount: {
      type: BIQJsonSchemaType.Integer,
      title: 'Amount',
      description: 'The amount of items to dequeue from the queue, defaults to 1',
      minimum: 1,
      ui: {
        options: {
          placeholder: '1',
        },
      },
    },
  },
  required: ['action', 'scope', 'queueName'],
};

/** The emitted message schema for the dequeue action for the DataStoreActor */
export const DataStoreActorDequeueResultSchema = z.object({
  data: z.object({
    queueName: z.string()
      .describe('The name of the queue the item was dequeued from'),
    value: z.array(z.unknown())
      .describe('The values that were dequeued from the queue'),
  })
    .describe('The data returned from the dequeue'),
  size: z.number().int()
    .describe('The size of the queue after the dequeue'),
});

export type DataStoreActorDequeueResult = z.infer<typeof DataStoreActorDequeueResultSchema>;
```
