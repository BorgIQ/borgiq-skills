# actorSchemas/task/collection/actions

Generated from the platform's runtime types. Do not edit.

The actions available for the CollectionActor.

## actorSchemas/task/collection/actions

**Source:** `actorSchemas/task/collection/actions.ts`

```typescript
import { BIQJsonSchemaType, BIQSelectJsonSchema } from '../../../schemas/index.js';

/** The actions available for the CollectionActor */
export enum CollectionActorAction {
  CreateCollection = 'createCollection',
  ListCollections = 'listCollections',
  UpdateCollection = 'updateCollection',
  DeleteCollection = 'deleteCollection',
  PutItem = 'putItem',
  UpdateItem = 'updateItem',
  GetItem = 'getItem',
  DeleteItem = 'deleteItem',
  Query = 'query',
  BatchGetItem = 'batchGetItem',
  BatchWriteItem = 'batchWriteItem',
  TransactWrite = 'transactWrite',
  TransactGet = 'transactGet',
}

// This identifies which actions have LTM and/or STM enabled
export const CollectionActorActionMemory: Partial<Record<CollectionActorAction, { ltm?: boolean; stm?: boolean }>> = {};

export const CollectionActorActionsJsonSchema: BIQSelectJsonSchema = {
  type: BIQJsonSchemaType.String,
  title: 'Action',
  description: 'The action to perform on the CollectionActor',
  enum: Object.values(CollectionActorAction),
  ui: {
    component: 'searchSelect',
    options: {
      enumLabels: {
        [CollectionActorAction.CreateCollection]: 'Create Collection',
        [CollectionActorAction.ListCollections]: 'List Collections',
        [CollectionActorAction.UpdateCollection]: 'Update Collection',
        [CollectionActorAction.DeleteCollection]: 'Delete Collection',
        [CollectionActorAction.PutItem]: 'Put Item',
        [CollectionActorAction.UpdateItem]: 'Update Item',
        [CollectionActorAction.GetItem]: 'Get Item',
        [CollectionActorAction.DeleteItem]: 'Delete Item',
        [CollectionActorAction.Query]: 'Query',
        [CollectionActorAction.BatchGetItem]: 'Batch Get Item',
        [CollectionActorAction.BatchWriteItem]: 'Batch Write Item',
        [CollectionActorAction.TransactWrite]: 'Transact Write',
        [CollectionActorAction.TransactGet]: 'Transact Get',
      },
      enumGroups: {
        'Collection Management': [CollectionActorAction.CreateCollection, CollectionActorAction.ListCollections, CollectionActorAction.UpdateCollection, CollectionActorAction.DeleteCollection],
        'Item Operations': [CollectionActorAction.PutItem, CollectionActorAction.UpdateItem, CollectionActorAction.GetItem, CollectionActorAction.DeleteItem, CollectionActorAction.Query],
        'Batch Operations': [CollectionActorAction.BatchGetItem, CollectionActorAction.BatchWriteItem],
        'Transactions': [CollectionActorAction.TransactWrite, CollectionActorAction.TransactGet],
      }
    },
  },
};
```
