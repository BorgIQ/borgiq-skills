# actorSchemas/task/dataStore/actions

Generated from the platform's runtime types. Do not edit.

Legacy: DataStoreActor is kept only so existing canvases load. Build new storage with CollectionActor.

The actions available for the DataStoreActor.

See also: [schemas/jsonSchema](../../../schemas/jsonSchema.md).

## actorSchemas/task/dataStore/actions

**Source:** `actorSchemas/task/dataStore/actions.ts`

```typescript
import { BIQJsonSchemaType, BIQSelectJsonSchema } from '../../../schemas/index.js';

/** The actions available for the DataStoreActor */
export enum DataStoreActorAction {
  Get = 'get',
  Set = 'set',
  Delete = 'delete',
  ListKeys = 'listKeys',
  Enqueue = 'enqueue',
  Dequeue = 'dequeue',
  EmptyQueue = 'emptyQueue',
  DeleteQueue = 'deleteQueue',
  AtomicCount = 'atomicCount',
}

// This identifies which actions have LTM and/or STM enabled
export const DataStoreActorActionMemory: Partial<Record<DataStoreActorAction, { ltm?: boolean; stm?: boolean }>> = {};

export const DataStoreActorActionsJsonSchema: BIQSelectJsonSchema = {
  type: BIQJsonSchemaType.String,
  title: 'Action',
  description: 'The action to perform on the DataStoreActor',
  enum: Object.values(DataStoreActorAction),
  ui: {
    component: 'searchSelect',
    options: {
      enumLabels: {
        [DataStoreActorAction.Get]: 'Get',
        [DataStoreActorAction.Set]: 'Set',
        [DataStoreActorAction.ListKeys]: 'List Keys',
        [DataStoreActorAction.Enqueue]: 'Enqueue',
        [DataStoreActorAction.Dequeue]: 'Dequeue',
        [DataStoreActorAction.EmptyQueue]: 'Empty Queue',
        [DataStoreActorAction.AtomicCount]: 'Atomic Count',
        [DataStoreActorAction.Delete]: 'Delete',
        [DataStoreActorAction.DeleteQueue]: 'Delete Queue',
      },
      enumGroups: {
        'Key-Value': [DataStoreActorAction.Get, DataStoreActorAction.Set, DataStoreActorAction.ListKeys, DataStoreActorAction.AtomicCount, DataStoreActorAction.Delete],
        'Queue': [DataStoreActorAction.Enqueue, DataStoreActorAction.Dequeue, DataStoreActorAction.EmptyQueue, DataStoreActorAction.DeleteQueue],
      }
    },
  },
};
```
