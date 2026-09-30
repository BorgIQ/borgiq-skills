# actorSchemas/task/dataStore/deleteQueue

Generated from the platform's runtime types. Do not edit.

Legacy: DataStoreActor is kept only so existing canvases load. Build new storage with CollectionActor.

The options schema for the deleteQueue action for the DataStoreActor.

See also: [schemas/jsonSchema](../../../schemas/jsonSchema.md), [actorSchemas/task/dataStore/actions](actions.md).

## actorSchemas/task/dataStore/deleteQueue

**Source:** `actorSchemas/task/dataStore/deleteQueue.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the deleteQueue action for the DataStoreActor */
export const DataStoreActorDeleteQueueOptionsSchema = z.object({
  /** Must be deleteQueue to access this function */
  action: z.literal(DataStoreActorAction.DeleteQueue)
    .describe('Must be deleteQueue to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe(
      'The scope of the key you want to delete, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'
    ),
  queueName: z.string().min(1)
    .describe('The name of the queue to delete'),
});

export type DataStoreActorDeleteQueueOptions = z.infer<typeof DataStoreActorDeleteQueueOptionsSchema>;

export const DataStoreActorDeleteQueueOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be deleteQueue to access this function',
      const: DataStoreActorAction.DeleteQueue,
    },
    scope: {
      type: BIQJsonSchemaType.String,
      title: 'Scope',
      description: 'The scope of the key you want to delete, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope',
      enum: ['canvas', 'workspace'],
    },
    queueName: {
      type: BIQJsonSchemaType.String,
      title: 'Queue name',
      description: 'The name of the queue to delete',
      minLength: 1,
    },
  },
  required: ['action', 'scope', 'queueName'],
};

/** The emitted message schema for the deleteQueue action for the DataStoreActor */
export const DataStoreActorDeleteQueueResultSchema = z.literal('deleted');

export type DataStoreActorDeleteQueueResult = z.infer<typeof DataStoreActorDeleteQueueResultSchema>;
```
