# actorSchemas/task/dataStore/index

Generated from the platform's runtime types. Do not edit.

Legacy: DataStoreActor is kept only so existing canvases load. Build new storage with CollectionActor.

DataStoreActor options, a discriminated union on `action`.

See also: [actorSchemas/task/dataStore/atomicCount](atomicCount.md), [actorSchemas/task/dataStore/dequeue](dequeue.md), [actorSchemas/task/dataStore/emptyQueue](emptyQueue.md), [actorSchemas/task/dataStore/enqueue](enqueue.md), [actorSchemas/task/dataStore/get](get.md), [actorSchemas/task/dataStore/listKeys](listKeys.md), [actorSchemas/task/dataStore/set](set.md), [actorSchemas/task/dataStore/delete](delete.md), [actorSchemas/task/dataStore/deleteQueue](deleteQueue.md), [actorSchemas/task/dataStore/actions](actions.md).

## actorSchemas/task/dataStore/index

**Source:** `actorSchemas/task/dataStore/index.ts`

```typescript
import { z } from 'zod';

import { DataStoreActorAtomicCountOptionsSchema, DataStoreActorAtomicCountResult } from './atomicCount.js';
import { DataStoreActorDequeueOptionsSchema, DataStoreActorDequeueResult } from './dequeue.js';
import { DataStoreActorEmptyQueueOptionsSchema, DataStoreActorEmptyQueueResult } from './emptyQueue.js';
import { DataStoreActorEnqueueOptionsSchema, DataStoreActorEnqueueResult } from './enqueue.js';
import { DataStoreActorGetOptionsSchema, DataStoreActorGetResult } from './get.js';
import { DataStoreActorListKeysOptionsSchema, DataStoreActorListKeysResult } from './listKeys.js';
import { DataStoreActorSetOptionsSchema, DataStoreActorSetResult } from './set.js';
import { DataStoreActorDeleteOptionsSchema, DataStoreActorDeleteResult } from './delete.js';
import { DataStoreActorDeleteQueueOptionsSchema, DataStoreActorDeleteQueueResult } from './deleteQueue.js';

export * from './atomicCount.js';
export * from './dequeue.js';
export * from './emptyQueue.js';
export * from './enqueue.js';
export * from './get.js';
export * from './listKeys.js';
export * from './set.js';
export * from './delete.js';
export * from './deleteQueue.js';
export * from './actions.js';

/** The options schema for the DataStoreActor with separated by actions */
export const DataStoreActorOptionsSchema = z.discriminatedUnion('action', [
  DataStoreActorGetOptionsSchema,
  DataStoreActorSetOptionsSchema,
  DataStoreActorDeleteOptionsSchema,
  DataStoreActorEnqueueOptionsSchema,
  DataStoreActorDequeueOptionsSchema,
  DataStoreActorEmptyQueueOptionsSchema,
  DataStoreActorDeleteQueueOptionsSchema,
  DataStoreActorAtomicCountOptionsSchema,
  DataStoreActorListKeysOptionsSchema,
]);

export type DataStoreActorOptions = z.infer<typeof DataStoreActorOptionsSchema>;

/** The emitted message schema for the DataStoreActor with separated by actions */
export type DataStoreActorResult =
  DataStoreActorGetResult | DataStoreActorSetResult | DataStoreActorDeleteResult | DataStoreActorAtomicCountResult | DataStoreActorListKeysResult |
  DataStoreActorEnqueueResult | DataStoreActorDequeueResult | DataStoreActorEmptyQueueResult | DataStoreActorDeleteQueueResult;
```
