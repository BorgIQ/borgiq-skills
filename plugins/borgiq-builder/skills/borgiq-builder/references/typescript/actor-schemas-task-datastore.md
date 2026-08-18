# Actor Schemas: DataStoreActor

Zod schemas and TypeScript types for DataStoreActor actions: get, set, delete, listKeys, atomicCount, enqueue, dequeue, emptyQueue, deleteQueue.

## Table of Contents

- [actorSchemas/task/dataStore/actions.ts](#actorschemastaskdatastoreactions)
- [actorSchemas/task/dataStore/atomicCount.ts](#actorschemastaskdatastoreatomiccount)
- [actorSchemas/task/dataStore/delete.ts](#actorschemastaskdatastoredelete)
- [actorSchemas/task/dataStore/deleteQueue.ts](#actorschemastaskdatastoredeletequeue)
- [actorSchemas/task/dataStore/dequeue.ts](#actorschemastaskdatastoredequeue)
- [actorSchemas/task/dataStore/emptyQueue.ts](#actorschemastaskdatastoreemptyqueue)
- [actorSchemas/task/dataStore/enqueue.ts](#actorschemastaskdatastoreenqueue)
- [actorSchemas/task/dataStore/get.ts](#actorschemastaskdatastoreget)
- [actorSchemas/task/dataStore/index.ts](#actorschemastaskdatastoreindex)
- [actorSchemas/task/dataStore/listKeys.ts](#actorschemastaskdatastorelistkeys)
- [actorSchemas/task/dataStore/set.ts](#actorschemastaskdatastoreset)

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

## actorSchemas/task/dataStore/atomicCount

**Source:** `actorSchemas/task/dataStore/atomicCount.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the atomicCount action for the DataStoreActor */
export const DataStoreActorAtomicCountOptionsSchema = z.object({
  action: z.literal(DataStoreActorAction.AtomicCount)
    .describe('Must be atomicCount to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe('The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'),
  key: z.string().min(1)
    .describe('The key to increment or decrement'),
  valueToAdd: z.number().int().nullish()
    .describe('The value to add to the value stored under key, defaults to 1. Values can be positive or negative'),
});

export type DataStoreActorAtomicCountOptions = z.infer<typeof DataStoreActorAtomicCountOptionsSchema>;

export const DataStoreActorAtomicCountOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: DataStoreActorAction.AtomicCount
    },
    scope: {
      type: BIQJsonSchemaType.String,
      title: 'Scope',
      description: 'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope',
      enum: ['canvas', 'workspace'],
      default: 'canvas',
    },
    key: {
      type: BIQJsonSchemaType.String,
      title: 'Key',
      description: 'The key to increment or decrement',
      minLength: 1,
    },
    valueToAdd: {
      type: BIQJsonSchemaType.Integer,
      title: 'Value to add',
      description: 'The value to add to the value stored under key, defaults to 1. Values can be positive or negative',
      ui: {
        options: {
          placeholder: '1',
        }
      }
    }
  },
  required: ['action', 'scope', 'key'],
};

/** The emitted message schema for the atomicCount action for the DataStoreActor */
export const DataStoreActorAtomicCountResultSchema = z.object({
  key: z.string()
    .describe('The key the atomic count action was completed on'),
  value: z.number().int()
    .describe('The updated value of the atomic count'),
});

export type DataStoreActorAtomicCountResult = z.infer<typeof DataStoreActorAtomicCountResultSchema>;
```

## actorSchemas/task/dataStore/delete

**Source:** `actorSchemas/task/dataStore/delete.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the delete action for the DataStoreActor */
export const DataStoreActorDeleteOptionsSchema = z.object({
  /** Must be delete to access this function */
  action: z.literal(DataStoreActorAction.Delete)
    .describe('Must be delete to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe(
      'The scope of the key you want to delete, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'
    ),
  key: z.string().min(1)
    .describe('The key to delete'),
});

export type DataStoreActorDeleteOptions = z.infer<typeof DataStoreActorDeleteOptionsSchema>;

export const DataStoreActorDeleteOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be delete to access this function',
      const: DataStoreActorAction.Delete,
    },
    scope: {
      type: BIQJsonSchemaType.String,
      title: 'Scope',
      description: 'The scope of the key you want to delete, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope',
      enum: ['canvas', 'workspace'],
    },
    key: {
      type: BIQJsonSchemaType.String,
      title: 'Key',
      description: 'The key to delete',
      minLength: 1,
    },
  },
  required: ['action', 'scope', 'key'],
};

/** The emitted message schema for the delete action for the DataStoreActor */
export const DataStoreActorDeleteResultSchema = z.literal('deleted');

export type DataStoreActorDeleteResult = z.infer<typeof DataStoreActorDeleteResultSchema>;
```

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

## actorSchemas/task/dataStore/enqueue

**Source:** `actorSchemas/task/dataStore/enqueue.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the enqueue action for the DataStoreActor */
export const DataStoreActorEnqueueOptionsSchema = z.object({
  action: z.literal(DataStoreActorAction.Enqueue)
    .describe('Must be enqueue to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe(
      'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'
    ),
  queueName: z.string().min(1)
    .describe('The name of the queue to enqueue to'),
  value: z.unknown()
    .refine((value) => value !== undefined, { message: 'Required' })
    .describe('The value(s) to enqueue'),
  enqueueAsASingleValue: z.boolean().nullish()
    .describe('If to enqueue array values as one value, if its false each item in the array will be enqueued as a separate value. Default value is false'),
});

export type DataStoreActorEnqueueOptions = z.infer<typeof DataStoreActorEnqueueOptionsSchema>;

export const DataStoreActorEnqueueOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be enqueue to access this function',
      const: DataStoreActorAction.Enqueue,
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
      description: 'The name of the queue to enqueue to',
      minLength: 1,
    },
    value: {
      type: BIQJsonSchemaType.Any,
      title: 'Value',
      description: 'The value(s) to enqueue',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
    enqueueAsASingleValue: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Enqueue as a single value',
      description: 'If to enqueue array values as one value, if its false each item in the array will be enqueued as a separate value. Default value is false',
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['action', 'scope', 'queueName', 'value'],
};

/** The emitted message schema for the enqueue action for the DataStoreActor */
export const DataStoreActorEnqueueResultSchema = z.object({
  data: z.object({
    queueName: z.string()
      .describe('The name of the queue the item was enqueued to'),
    value: z.unknown()
      .describe('The value(s) enqueued to the queue'),
  }),
  size: z.number().int()
    .describe('The size of the queue after the enqueue'),
});

export type DataStoreActorEnqueueResult = z.infer<typeof DataStoreActorEnqueueResultSchema>;
```

## actorSchemas/task/dataStore/get

**Source:** `actorSchemas/task/dataStore/get.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the get action for the DataStoreActor */
export const DataStoreActorGetOptionsSchema = z.object({
  /** Must be get to access this function */
  action: z.literal(DataStoreActorAction.Get)
    .describe('Must be get to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe(
      'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'
    ),
  key: z.string().min(1)
    .describe('The key to get the value of'),
  defaultValue: z.unknown().nullish()
    .describe('The value to emit if the key does not exist, otherwise defaults to null'),
});

export type DataStoreActorGetOptions = z.infer<typeof DataStoreActorGetOptionsSchema>;

export const DataStoreActorGetOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be get to access this function',
      const: DataStoreActorAction.Get,
    },
    scope: {
      type: BIQJsonSchemaType.String,
      title: 'Scope',
      description: 'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope',
      enum: ['canvas', 'workspace'],
    },
    key: {
      type: BIQJsonSchemaType.String,
      title: 'Key',
      description: 'The key to get the value of',
      minLength: 1,
    },
    defaultValue: {
      type: BIQJsonSchemaType.Any,
      title: 'Default value',
      description: 'The value to emit if the key does not exist, otherwise defaults to null',
      ui: {
        options: {
          placeholder: 'null',
          editInModal: true,
        },
      },
    },
  },
  required: ['action', 'scope', 'key'],
};

/** The emitted message schema for the get action for the DataStoreActor */
export const DataStoreActorGetResultSchema = z.object({
  key: z.string()
    .describe('The key the value was retrieved from'),
  value: z.unknown()
    .describe('The value of the key'),
});

export type DataStoreActorGetResult = z.infer<typeof DataStoreActorGetResultSchema>;
```

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

## actorSchemas/task/dataStore/listKeys

**Source:** `actorSchemas/task/dataStore/listKeys.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the listKeys action for the DataStoreActor */
export const DataStoreActorListKeysOptionsSchema = z.object({
  action: z.literal(DataStoreActorAction.ListKeys)
    .describe('Must be listKeys to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe(
      'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'
    ),
  page: z.number().int().min(1).nullish()
    .describe('The page number to retrieve, defaults to 1'),
  pageSize: z.number().int().min(1).nullish()
    .describe('The amount of keys to retrieve per page, defaults to 10'),
  sortBy: z.enum(['key', 'createdAt', 'updatedAt']).nullish()
    .describe('The field to sort by, defaults to key'),
  sortOrder: z.enum(['asc', 'desc']).nullish()
    .describe('The order to sort by, defaults to asc'),
  search: z.string().nullish()
    .describe('Filter returned keys with a search value, an empty string indicated no filtering. Defaults to \'\''),
});

export type DataStoreActorListKeysOptions = z.infer<typeof DataStoreActorListKeysOptionsSchema>;

export const DataStoreActorListKeysOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be listKeys to access this function',
      const: DataStoreActorAction.ListKeys,
    },
    scope: {
      type: BIQJsonSchemaType.String,
      title: 'Scope',
      description: 'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope',
      enum: ['canvas', 'workspace'],
      default: 'canvas',
    },
    page: {
      type: BIQJsonSchemaType.Integer,
      title: 'Page',
      description: 'The page number to retrieve, defaults to 1',
      default: 1,
      ui: {
        options: {
          placeholder: '1',
        },
      },
    },
    pageSize: {
      type: BIQJsonSchemaType.Integer,
      title: 'Page size',
      description: 'The amount of keys to retrieve per page, defaults to 10',
      default: 10,
      ui: {
        options: {
          placeholder: '10',
        },
      },
    },
    sortBy: {
      type: BIQJsonSchemaType.String,
      title: 'Sort by',
      description: 'The field to sort by, defaults to key',
      enum: ['key', 'createdAt', 'updatedAt'],
      default: 'key',
    },
    sortOrder: {
      type: BIQJsonSchemaType.String,
      title: 'Sort order',
      description: 'The order to sort by, defaults to asc',
      enum: ['asc', 'desc'],
      default: 'asc',
    },
    search: {
      type: BIQJsonSchemaType.String,
      title: 'Search',
      description: 'Filter returned keys with a search value, an empty string indicated no filtering. Defaults to \'\'',
      default: '',
    },
  },
  required: ['action', 'scope'],
};

/** The emitted message schema for the listKeys action for the DataStoreActor */
export const DataStoreActorListKeysResultSchema = z.object({
  keys: z.array(z.string())
    .describe('The keys retrieved'),
  total: z.number().int()
    .describe('The total number of keys'),
  page: z.number().int()
    .describe('The page number retrieved'),
  pageSize: z.number().int()
    .describe('The amount of keys retrieved per page'),
});

export type DataStoreActorListKeysResult = z.infer<typeof DataStoreActorListKeysResultSchema>;
```

## actorSchemas/task/dataStore/set

**Source:** `actorSchemas/task/dataStore/set.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the set action for the DataStoreActor  */
export const DataStoreActorSetOptionsSchema = z.object({
  action: z.literal(DataStoreActorAction.Set)
    .describe('Must be set to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe(
      'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'
    ),
  key: z.string().min(1)
    .describe('The key to set the value of'),
  value: z.unknown()
    .refine((value) => value !== undefined, { message: 'Required' })
    .describe('The value to set'),
});

export type DataStoreActorSetOptions = z.infer<typeof DataStoreActorSetOptionsSchema>;

export const DataStoreActorSetOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be set to access this function',
      const: DataStoreActorAction.Set,
    },
    scope: {
      type: BIQJsonSchemaType.String,
      title: 'Scope',
      description: 'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope',
      enum: ['canvas', 'workspace'],
      default: 'canvas',
    },
    key: {
      type: BIQJsonSchemaType.String,
      title: 'Key',
      description: 'The key to set the value of',
    },
    value: {
      type: BIQJsonSchemaType.Any,
      title: 'Value',
      description: 'The value to set',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
  },
  required: ['action', 'scope', 'key', 'value'],
};


/** The emitted message schema for the set action for the DataStoreActor */
export const DataStoreActorSetResultSchema = z.object({
  key: z.string()
    .describe('The key the value was set to'),
  value: z.unknown()
    .describe('The value set'),
});

export type DataStoreActorSetResult = z.infer<typeof DataStoreActorSetResultSchema>;
```
