# actorSchemas/task/collection/index

Generated from the platform's runtime types. Do not edit.

CollectionActor options, a discriminated union on `action`, and its result types.

See also: [actorSchemas/task/collection/createCollection](createCollection.md), [actorSchemas/task/collection/listCollections](listCollections.md), [actorSchemas/task/collection/updateCollection](updateCollection.md), [actorSchemas/task/collection/deleteCollection](deleteCollection.md), [actorSchemas/task/collection/putItem](putItem.md), [actorSchemas/task/collection/updateItem](updateItem.md), [actorSchemas/task/collection/getItem](getItem.md), [actorSchemas/task/collection/deleteItem](deleteItem.md), [actorSchemas/task/collection/query](query.md), [actorSchemas/task/collection/batchGetItem](batchGetItem.md), [actorSchemas/task/collection/batchWriteItem](batchWriteItem.md), [actorSchemas/task/collection/transactWrite](transactWrite.md), [actorSchemas/task/collection/transactGet](transactGet.md), [actorSchemas/task/collection/actions](actions.md), [actorSchemas/task/collection/labelSlots](labelSlots.md).

## actorSchemas/task/collection/index

**Source:** `actorSchemas/task/collection/index.ts`

```typescript
import { z } from 'zod';

import { CollectionActorCreateCollectionOptionsSchema, CollectionActorCreateCollectionResult } from './createCollection.js';
import { CollectionActorListCollectionsOptionsSchema, CollectionActorListCollectionsResult } from './listCollections.js';
import { CollectionActorUpdateCollectionOptionsSchema, CollectionActorUpdateCollectionResult } from './updateCollection.js';
import { CollectionActorDeleteCollectionOptionsSchema, CollectionActorDeleteCollectionResult } from './deleteCollection.js';
import { CollectionActorPutItemOptionsSchema, CollectionActorPutItemResult } from './putItem.js';
import { CollectionActorUpdateItemOptionsSchema, CollectionActorUpdateItemResult } from './updateItem.js';
import { CollectionActorGetItemOptionsSchema, CollectionActorGetItemResult } from './getItem.js';
import { CollectionActorDeleteItemOptionsSchema, CollectionActorDeleteItemResult } from './deleteItem.js';
import { CollectionActorQueryOptionsSchema, CollectionActorQueryResult } from './query.js';
import { CollectionActorBatchGetItemOptionsSchema, CollectionActorBatchGetItemResult } from './batchGetItem.js';
import { CollectionActorBatchWriteItemOptionsSchema, CollectionActorBatchWriteItemResult } from './batchWriteItem.js';
import { CollectionActorTransactWriteOptionsSchema, CollectionActorTransactWriteResult } from './transactWrite.js';
import { CollectionActorTransactGetOptionsSchema, CollectionActorTransactGetResult } from './transactGet.js';

export * from './createCollection.js';
export * from './listCollections.js';
export * from './updateCollection.js';
export * from './deleteCollection.js';
export * from './putItem.js';
export * from './updateItem.js';
export * from './getItem.js';
export * from './deleteItem.js';
export * from './query.js';
export * from './batchGetItem.js';
export * from './batchWriteItem.js';
export * from './transactWrite.js';
export * from './transactGet.js';
export * from './actions.js';
export * from './labelSlots.js';

/** The options schema for the CollectionActor with separated by actions */
export const CollectionActorOptionsSchema = z.discriminatedUnion('action', [
  CollectionActorCreateCollectionOptionsSchema,
  CollectionActorListCollectionsOptionsSchema,
  CollectionActorUpdateCollectionOptionsSchema,
  CollectionActorDeleteCollectionOptionsSchema,
  CollectionActorPutItemOptionsSchema,
  CollectionActorUpdateItemOptionsSchema,
  CollectionActorGetItemOptionsSchema,
  CollectionActorDeleteItemOptionsSchema,
  CollectionActorQueryOptionsSchema,
  CollectionActorBatchGetItemOptionsSchema,
  CollectionActorBatchWriteItemOptionsSchema,
  CollectionActorTransactWriteOptionsSchema,
  CollectionActorTransactGetOptionsSchema,
]);

export type CollectionActorOptions = z.infer<typeof CollectionActorOptionsSchema>;

/** The emitted message schema for the CollectionActor with separated by actions */
export type CollectionActorResult =
  CollectionActorCreateCollectionResult | CollectionActorListCollectionsResult | CollectionActorUpdateCollectionResult | CollectionActorDeleteCollectionResult |
  CollectionActorPutItemResult | CollectionActorUpdateItemResult | CollectionActorGetItemResult | CollectionActorDeleteItemResult | CollectionActorQueryResult |
  CollectionActorBatchGetItemResult | CollectionActorBatchWriteItemResult | CollectionActorTransactWriteResult | CollectionActorTransactGetResult;
```
