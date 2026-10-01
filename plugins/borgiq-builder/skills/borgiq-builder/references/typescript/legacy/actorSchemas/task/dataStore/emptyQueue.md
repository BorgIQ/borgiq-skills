# actorSchemas/task/dataStore/emptyQueue

Generated from the platform's runtime types. Do not edit.

Legacy: DataStoreActor is kept only so existing canvases load. Build new storage with CollectionActor.

The options schema for the emptyQueue action for the DataStoreActor.

See also: [schemas/jsonSchema](../../../schemas/jsonSchema.md), [actorSchemas/task/dataStore/actions](actions.md).

## actorSchemas/task/dataStore/emptyQueue

**Source:** `actorSchemas/task/dataStore/emptyQueue.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the emptyQueue action for the DataStoreActor */
export const DataStoreActorEmptyQueueOptionsSchema = z.object({
  action: z.literal(DataStoreActorAction.EmptyQueue)
    .describe('Must be emptyQueue to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe(
      'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'
    ),
  queueName: z.string().min(1)
    .describe('The name of the queue to empty'),
});

export type DataStoreActorEmptyQueueOptions = z.infer<typeof DataStoreActorEmptyQueueOptionsSchema>;

export const DataStoreActorEmptyQueueOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be emptyQueue to access this function',
      const: DataStoreActorAction.EmptyQueue,
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
      description: 'The name of the queue to empty',
      minLength: 1,
    },
  },
  required: ['action', 'scope', 'queueName'],
};

/** The emitted message schema for the emptyQueue action for the DataStoreActor */
export const DataStoreActorEmptyQueueResultSchema = z.object({
  queueName: z.string()
    .describe('The name of the queue the item was dequeued from'),
  values: z.array(z.unknown())
    .describe('The values that were in the queue'),
});

export type DataStoreActorEmptyQueueResult = z.infer<typeof DataStoreActorEmptyQueueResultSchema>;
```
