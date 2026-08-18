# Actor Schemas: CollectionActor

Zod schemas and TypeScript types for CollectionActor actions: query, getItem, putItem, deleteItem, batchGet, batchWrite, batchDelete, createCollection, deleteCollection, listCollections, atomicAdd.

## Table of Contents

- [actorSchemas/task/collection/actions.ts](#actorschemastaskcollectionactions)
- [actorSchemas/task/collection/batchGetItem.ts](#actorschemastaskcollectionbatchgetitem)
- [actorSchemas/task/collection/batchWriteItem.ts](#actorschemastaskcollectionbatchwriteitem)
- [actorSchemas/task/collection/createCollection.ts](#actorschemastaskcollectioncreatecollection)
- [actorSchemas/task/collection/deleteCollection.ts](#actorschemastaskcollectiondeletecollection)
- [actorSchemas/task/collection/deleteItem.ts](#actorschemastaskcollectiondeleteitem)
- [actorSchemas/task/collection/getItem.ts](#actorschemastaskcollectiongetitem)
- [actorSchemas/task/collection/index.ts](#actorschemastaskcollectionindex)
- [actorSchemas/task/collection/listCollections.ts](#actorschemastaskcollectionlistcollections)
- [actorSchemas/task/collection/putItem.ts](#actorschemastaskcollectionputitem)
- [actorSchemas/task/collection/query.ts](#actorschemastaskcollectionquery)
- [actorSchemas/task/collection/transactGet.ts](#actorschemastaskcollectiontransactget)
- [actorSchemas/task/collection/transactWrite.ts](#actorschemastaskcollectiontransactwrite)
- [actorSchemas/task/collection/updateCollection.ts](#actorschemastaskcollectionupdatecollection)
- [actorSchemas/task/collection/updateItem.ts](#actorschemastaskcollectionupdateitem)

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

## actorSchemas/task/collection/batchGetItem

**Source:** `actorSchemas/task/collection/batchGetItem.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the batchGetItem action for the CollectionActor */
export const CollectionActorBatchGetItemOptionsSchema = z.object({
  /** Must be batchGetItem to access this function */
  action: z.literal(CollectionActorAction.BatchGetItem)
    .describe('Must be batchGetItem to access this function'),
  items: z.array(z.object({
    collection: z.string()
      .describe('The collection to get the item from'),
    key: z.string()
      .describe('The key of the item to get'),
  })).max(100)
    .describe('The items to get, up to 100'),
  options: z.object({
    meta: z.boolean().optional()
      .describe('Whether to include metadata in the results'),
  }).optional()
    .describe('Options for the batch get operation'),
});

export type CollectionActorBatchGetItemOptions = z.infer<typeof CollectionActorBatchGetItemOptionsSchema>;

export const CollectionActorBatchGetItemOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be batchGetItem to access this function',
      const: CollectionActorAction.BatchGetItem,
    },
    items: {
      type: BIQJsonSchemaType.Array,
      title: 'Items',
      description: 'The items to get, up to 100',
      maxItems: 100,
      items: {
        type: BIQJsonSchemaType.Object,
        title: 'Item',
        properties: {
          collection: {
            type: BIQJsonSchemaType.String,
            title: 'Collection',
            description: 'The collection to get the item from',
          },
          key: {
            type: BIQJsonSchemaType.String,
            title: 'Key',
            description: 'The key of the item to get',
          },
        },
        required: ['collection', 'key'],
      },
    },
    options: {
      type: BIQJsonSchemaType.Object,
      title: 'Options',
      description: 'Options for the batch get operation',
      properties: {
        meta: {
          type: BIQJsonSchemaType.Boolean,
          title: 'Include metadata',
          description: 'Whether to include metadata in the results',
          ui: { component: 'switch' },
        },
      },
    },
  },
  required: ['action', 'items'],
};

/** The emitted message schema for the batchGetItem action for the CollectionActor.
 * Each item always includes key and value. When meta: true, additionally
 * includes collection, timestamps, and labels. */
export const CollectionActorBatchGetItemResultSchema = z.object({
  items: z.array(z.object({
    key: z.string()
      .describe('The key of the item'),
    value: z.unknown()
      .describe('The item data'),
    collection: z.string().optional()
      .describe('The collection the item belongs to (included when meta: true)'),
    labels: z.record(z.string(), z.string().nullable()).optional()
      .describe('The labels of the item (included when meta: true)'),
    createdAt: z.string().optional()
      .describe('The creation timestamp (included when meta: true)'),
    updatedAt: z.string().optional()
      .describe('The last-updated timestamp (included when meta: true)'),
    ttl: z.string().optional()
      .describe('The time-to-live of the item as ISO-8601 (included when meta: true)'),
  }).nullable())
    .describe('The retrieved items, null for items not found'),
});

export type CollectionActorBatchGetItemResult = z.infer<typeof CollectionActorBatchGetItemResultSchema>;
```

## actorSchemas/task/collection/batchWriteItem

**Source:** `actorSchemas/task/collection/batchWriteItem.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the batchWriteItem action for the CollectionActor */
export const CollectionActorBatchWriteItemOptionsSchema = z.object({
  /** Must be batchWriteItem to access this function */
  action: z.literal(CollectionActorAction.BatchWriteItem)
    .describe('Must be batchWriteItem to access this function'),
  items: z.array(z.object({
    operation: z.enum(['put', 'delete'])
      .describe('The operation to perform'),
    collection: z.string()
      .describe('The collection for the operation'),
    key: z.string()
      .describe('The key for the operation'),
    value: z.unknown().optional()
      .describe('The value to store, required for put operations'),
    ttl: z.union([z.number(), z.string(), z.null()]).optional()
      .describe('Time-to-live for the item'),
    labels: z.record(z.string(), z.string().nullable()).optional()
      .describe('Labels for the item'),
  })).max(25)
    .describe('The items to write, up to 25'),
  options: z.object({
    meta: z.boolean().optional()
      .describe('Whether to include metadata in the results'),
  }).optional()
    .describe('Options for the batch write operation'),
});

export type CollectionActorBatchWriteItemOptions = z.infer<typeof CollectionActorBatchWriteItemOptionsSchema>;

export const CollectionActorBatchWriteItemOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be batchWriteItem to access this function',
      const: CollectionActorAction.BatchWriteItem,
    },
    items: {
      type: BIQJsonSchemaType.Array,
      title: 'Items',
      description: 'The items to write, up to 25',
      maxItems: 25,
      items: {
        type: BIQJsonSchemaType.Object,
        title: 'Item',
        properties: {
          operation: {
            type: BIQJsonSchemaType.String,
            title: 'Operation',
            description: 'The operation to perform',
            enum: ['put', 'delete'],
            ui: { component: 'select' },
          },
          collection: {
            type: BIQJsonSchemaType.String,
            title: 'Collection',
            description: 'The collection for the operation',
          },
          key: {
            type: BIQJsonSchemaType.String,
            title: 'Key',
            description: 'The key for the operation',
          },
          value: {
            type: BIQJsonSchemaType.Any,
            title: 'Value',
            description: 'The value to store, required for put operations',
            ui: { options: { editInModal: true } },
          },
          ttl: {
            title: 'TTL',
            description: 'Time-to-live for the item',
            anyOf: [
              { type: BIQJsonSchemaType.Number, title: 'TTL (seconds)' },
              { type: BIQJsonSchemaType.String, title: 'TTL (expression)' },
            ],
          },
          labels: {
            type: BIQJsonSchemaType.Any,
            title: 'Labels',
            description: 'Labels for the item',
          },
        },
        required: ['operation', 'collection', 'key'],
      },
    },
    options: {
      type: BIQJsonSchemaType.Object,
      title: 'Options',
      description: 'Options for the batch write operation',
      properties: {
        meta: {
          type: BIQJsonSchemaType.Boolean,
          title: 'Include metadata',
          description: 'Whether to include metadata in the results',
          ui: { component: 'switch' },
        },
      },
    },
  },
  required: ['action', 'items'],
};

/** The emitted message schema for the batchWriteItem action for the CollectionActor.
 * Each item always includes key and value. When meta: true, additionally
 * includes collection, timestamps, and labels. */
export const CollectionActorBatchWriteItemResultSchema = z.object({
  processed: z.number()
    .describe('The number of items processed'),
  items: z.array(z.object({
    key: z.string()
      .describe('The key of the item'),
    value: z.unknown()
      .describe('The item data'),
    collection: z.string().optional()
      .describe('The collection the item belongs to (included when meta: true)'),
    labels: z.record(z.string(), z.string().nullable()).optional()
      .describe('The labels of the item (included when meta: true)'),
    createdAt: z.string().optional()
      .describe('The creation timestamp (included when meta: true)'),
    updatedAt: z.string().optional()
      .describe('The last-updated timestamp (included when meta: true)'),
    ttl: z.string().optional()
      .describe('The time-to-live of the item as ISO-8601 (included when meta: true)'),
  })).optional()
    .describe('The items that were put'),
  deleted: z.array(z.object({
    collection: z.string()
      .describe('The collection the item was deleted from'),
    key: z.string()
      .describe('The key of the deleted item'),
  })).optional()
    .describe('The items that were deleted'),
});

export type CollectionActorBatchWriteItemResult = z.infer<typeof CollectionActorBatchWriteItemResultSchema>;
```

## actorSchemas/task/collection/createCollection

**Source:** `actorSchemas/task/collection/createCollection.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the createCollection action for the CollectionActor */
export const CollectionActorCreateCollectionOptionsSchema = z.object({
  /** Must be createCollection to access this function */
  action: z.literal(CollectionActorAction.CreateCollection)
    .describe('Must be createCollection to access this function'),
  slug: z.string().regex(/^[a-z0-9_-]+$/).refine((val) => !val.startsWith('__'), { message: 'Slug must not start with __' })
    .describe('The unique slug for the collection'),
  name: z.string()
    .describe('The display name for the collection'),
  description: z.string().optional()
    .describe('An optional description for the collection'),
  labels: z.array(z.string()).max(5).optional()
    .describe('Optional labels for the collection, up to 5'),
});

export type CollectionActorCreateCollectionOptions = z.infer<typeof CollectionActorCreateCollectionOptionsSchema>;

export const CollectionActorCreateCollectionOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be createCollection to access this function',
      const: CollectionActorAction.CreateCollection,
    },
    slug: {
      type: BIQJsonSchemaType.String,
      title: 'Slug',
      description: 'The unique slug for the collection',
    },
    name: {
      type: BIQJsonSchemaType.String,
      title: 'Name',
      description: 'The display name for the collection',
    },
    description: {
      type: BIQJsonSchemaType.String,
      title: 'Description',
      description: 'An optional description for the collection',
    },
    labels: {
      type: BIQJsonSchemaType.Array,
      title: 'Labels',
      description: 'Optional labels for the collection, up to 5',
      items: { type: BIQJsonSchemaType.String, title: 'Label' },
      maxItems: 5,
    },
  },
  required: ['action', 'slug', 'name'],
};

/** The emitted message schema for the createCollection action for the CollectionActor */
export const CollectionActorCreateCollectionResultSchema = z.object({
  slug: z.string()
    .describe('The slug of the created collection'),
  name: z.string()
    .describe('The name of the created collection'),
  description: z.string().optional()
    .describe('The description of the created collection'),
  labels: z.array(z.string())
    .describe('The labels of the created collection'),
  createdAt: z.string()
    .describe('The creation timestamp'),
});

export type CollectionActorCreateCollectionResult = z.infer<typeof CollectionActorCreateCollectionResultSchema>;
```

## actorSchemas/task/collection/deleteCollection

**Source:** `actorSchemas/task/collection/deleteCollection.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the deleteCollection action for the CollectionActor */
export const CollectionActorDeleteCollectionOptionsSchema = z.object({
  /** Must be deleteCollection to access this function */
  action: z.literal(CollectionActorAction.DeleteCollection)
    .describe('Must be deleteCollection to access this function'),
  slug: z.string()
    .describe('The slug of the collection to delete'),
});

export type CollectionActorDeleteCollectionOptions = z.infer<typeof CollectionActorDeleteCollectionOptionsSchema>;

export const CollectionActorDeleteCollectionOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be deleteCollection to access this function',
      const: CollectionActorAction.DeleteCollection,
    },
    slug: {
      type: BIQJsonSchemaType.String,
      title: 'Slug',
      description: 'The slug of the collection to delete',
    },
  },
  required: ['action', 'slug'],
};

/** The emitted message schema for the deleteCollection action for the CollectionActor */
export const CollectionActorDeleteCollectionResultSchema = z.object({
  slug: z.string()
    .describe('The slug of the deleted collection'),
  deletedAt: z.string()
    .describe('The deletion timestamp'),
});

export type CollectionActorDeleteCollectionResult = z.infer<typeof CollectionActorDeleteCollectionResultSchema>;
```

## actorSchemas/task/collection/deleteItem

**Source:** `actorSchemas/task/collection/deleteItem.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the deleteItem action for the CollectionActor */
export const CollectionActorDeleteItemOptionsSchema = z.object({
  /** Must be deleteItem to access this function */
  action: z.literal(CollectionActorAction.DeleteItem)
    .describe('Must be deleteItem to access this function'),
  collection: z.string()
    .describe('The collection to delete items from'),
  keys: z.union([z.string(), z.array(z.string()).min(1).max(25)])
    .describe('A single key or array of keys (up to 25) to delete'),
  conditions: z.record(z.string(), z.unknown()).optional()
    .describe('Conditional expressions for the delete operation. Applies to data fields only, not labels.'),
});

export type CollectionActorDeleteItemOptions = z.infer<typeof CollectionActorDeleteItemOptionsSchema>;

export const CollectionActorDeleteItemOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be deleteItem to access this function',
      const: CollectionActorAction.DeleteItem,
    },
    collection: {
      type: BIQJsonSchemaType.String,
      title: 'Collection',
      description: 'The collection to delete items from',
    },
    keys: {
      title: 'Keys',
      description: 'A single key or array of keys (up to 25) to delete',
      anyOf: [
        { type: BIQJsonSchemaType.String, title: 'Key', description: 'A single key to delete' },
        { type: BIQJsonSchemaType.Array, title: 'Keys', description: 'An array of keys to delete', items: { type: BIQJsonSchemaType.String, title: 'Key' } },
      ],
    },
    conditions: {
      type: BIQJsonSchemaType.Any,
      title: 'Conditions',
      description: 'Conditional expressions for the delete operation. Applies to data fields only, not labels.',
      ui: {
        options: {
          editInModal: true,
        },
      },
    },
  },
  required: ['action', 'collection', 'keys'],
};

/** The emitted message schema for the deleteItem action for the CollectionActor */
export const CollectionActorDeleteItemResultSchema = z.object({
  deleted: z.number()
    .describe('The number of items deleted'),
});

export type CollectionActorDeleteItemResult = z.infer<typeof CollectionActorDeleteItemResultSchema>;
```

## actorSchemas/task/collection/getItem

**Source:** `actorSchemas/task/collection/getItem.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the getItem action for the CollectionActor */
export const CollectionActorGetItemOptionsSchema = z.object({
  /** Must be getItem to access this function */
  action: z.literal(CollectionActorAction.GetItem)
    .describe('Must be getItem to access this function'),
  collection: z.string()
    .describe('The collection to get the item from'),
  key: z.string()
    .describe('The key of the item to get'),
  options: z.object({
    meta: z.boolean().optional()
      .describe('Whether to include metadata in the result'),
    label: z.string().optional()
      .describe('Filter by label'),
  }).optional()
    .describe('Options for the get operation'),
});

export type CollectionActorGetItemOptions = z.infer<typeof CollectionActorGetItemOptionsSchema>;

export const CollectionActorGetItemOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be getItem to access this function',
      const: CollectionActorAction.GetItem,
    },
    collection: {
      type: BIQJsonSchemaType.String,
      title: 'Collection',
      description: 'The collection to get the item from',
    },
    key: {
      type: BIQJsonSchemaType.String,
      title: 'Key',
      description: 'The key of the item to get',
    },
    options: {
      type: BIQJsonSchemaType.Object,
      title: 'Options',
      description: 'Options for the get operation',
      properties: {
        meta: {
          type: BIQJsonSchemaType.Boolean,
          title: 'Include metadata',
          description: 'Whether to include metadata in the result',
          ui: { component: 'switch' },
        },
        label: {
          type: BIQJsonSchemaType.String,
          title: 'Label',
          description: 'Filter by label',
        },
      },
    },
  },
  required: ['action', 'collection', 'key'],
};

/** The emitted message schema for the getItem action for the CollectionActor.
 * Always includes key and value. When meta: true, additionally includes
 * collection, timestamps, and labels. */
export const CollectionActorGetItemResultSchema = z.object({
  key: z.string()
    .describe('The key of the item'),
  value: z.unknown()
    .describe('The item data'),
  collection: z.string().optional()
    .describe('The collection the item belongs to (included when meta: true)'),
  labels: z.record(z.string(), z.string().nullable()).optional()
    .describe('The labels of the item (included when meta: true)'),
  createdAt: z.string().optional()
    .describe('The creation timestamp (included when meta: true)'),
  updatedAt: z.string().optional()
    .describe('The last-updated timestamp (included when meta: true)'),
  ttl: z.string().optional()
    .describe('The time-to-live of the item as ISO-8601 (included when meta: true)'),
}).nullable();

export type CollectionActorGetItemResult = z.infer<typeof CollectionActorGetItemResultSchema>;
```

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

## actorSchemas/task/collection/listCollections

**Source:** `actorSchemas/task/collection/listCollections.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the listCollections action for the CollectionActor */
export const CollectionActorListCollectionsOptionsSchema = z.object({
  /** Must be listCollections to access this function */
  action: z.literal(CollectionActorAction.ListCollections)
    .describe('Must be listCollections to access this function'),
  options: z.object({
    startKey: z.string().optional()
      .describe('Pagination start key from a previous query'),
    limit: z.number().int().min(1).max(100).default(100).optional()
      .describe('The number of collections to return, defaults to 100'),
  }).optional()
    .describe('Options for listing collections'),
});

export type CollectionActorListCollectionsOptions = z.infer<typeof CollectionActorListCollectionsOptionsSchema>;

export const CollectionActorListCollectionsOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be listCollections to access this function',
      const: CollectionActorAction.ListCollections,
    },
    options: {
      type: BIQJsonSchemaType.Object,
      title: 'Options',
      description: 'Options for listing collections',
      properties: {
        startKey: {
          type: BIQJsonSchemaType.String,
          title: 'Start key',
          description: 'Pagination start key from a previous query',
        },
        limit: {
          type: BIQJsonSchemaType.Integer,
          title: 'Limit',
          description: 'The number of collections to return, defaults to 100',
          default: 100,
          minimum: 1,
          maximum: 100,
        },
      },
    },
  },
  required: ['action'],
};

/** The emitted message schema for the listCollections action for the CollectionActor */
export const CollectionActorListCollectionsResultSchema = z.object({
  collections: z.array(z.object({
    slug: z.string()
      .describe('The slug of the collection'),
    name: z.string()
      .describe('The name of the collection'),
    description: z.string().optional()
      .describe('The description of the collection'),
    labels: z.array(z.string())
      .describe('The labels of the collection'),
    createdAt: z.string()
      .describe('The creation timestamp'),
  }))
    .describe('The list of collections'),
  lastKey: z.string().optional()
    .describe('Key for the next page'),
});

export type CollectionActorListCollectionsResult = z.infer<typeof CollectionActorListCollectionsResultSchema>;
```

## actorSchemas/task/collection/putItem

**Source:** `actorSchemas/task/collection/putItem.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the putItem action for the CollectionActor */
export const CollectionActorPutItemOptionsSchema = z.object({
  /** Must be putItem to access this function */
  action: z.literal(CollectionActorAction.PutItem)
    .describe('Must be putItem to access this function'),
  collection: z.string()
    .describe('The collection to put the item into'),
  key: z.string().max(256).refine((val) => !val.includes('#'), { message: 'Key must not contain #' })
    .describe('The key for the item, max 256 characters, must not contain #'),
  value: z.unknown()
    .describe('The value to store'),
  labels: z.record(z.string(), z.string().nullable()).optional()
    .describe('Optional labels for the item'),
  ttl: z.union([z.number(), z.string(), z.null()]).optional()
    .describe('Optional time-to-live for the item'),
  options: z.object({
    overwrite: z.boolean().default(false).optional()
      .describe('Whether to overwrite existing items, defaults to false'),
    meta: z.boolean().optional()
      .describe('Whether to include metadata in the result'),
  }).optional()
    .describe('Options for the put operation'),
  conditions: z.record(z.string(), z.unknown()).optional()
    .describe('Conditional expressions for the put operation. Applies to data fields only, not labels.'),
});

export type CollectionActorPutItemOptions = z.infer<typeof CollectionActorPutItemOptionsSchema>;

export const CollectionActorPutItemOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be putItem to access this function',
      const: CollectionActorAction.PutItem,
    },
    collection: {
      type: BIQJsonSchemaType.String,
      title: 'Collection',
      description: 'The collection to put the item into',
    },
    key: {
      type: BIQJsonSchemaType.String,
      title: 'Key',
      description: 'The key for the item, max 256 characters, must not contain #',
    },
    value: {
      type: BIQJsonSchemaType.Any,
      title: 'Value',
      description: 'The value to store',
      ui: {
        options: {
          editInModal: true,
        },
      },
    },
    labels: {
      type: BIQJsonSchemaType.Any,
      title: 'Labels',
      description: 'Optional labels for the item',
    },
    ttl: {
      title: 'TTL',
      description: 'Optional time-to-live for the item',
      anyOf: [
        { type: BIQJsonSchemaType.Number, title: 'TTL (seconds)' },
        { type: BIQJsonSchemaType.String, title: 'TTL (expression)' },
      ],
    },
    options: {
      type: BIQJsonSchemaType.Object,
      title: 'Options',
      description: 'Options for the put operation',
      properties: {
        overwrite: {
          type: BIQJsonSchemaType.Boolean,
          title: 'Overwrite',
          description: 'Whether to overwrite existing items, defaults to false',
          default: false,
          ui: { component: 'switch' },
        },
        meta: {
          type: BIQJsonSchemaType.Boolean,
          title: 'Include metadata',
          description: 'Whether to include metadata in the result',
          ui: { component: 'switch' },
        },
      },
    },
    conditions: {
      type: BIQJsonSchemaType.Any,
      title: 'Conditions',
      description: 'Conditional expressions for the put operation. Applies to data fields only, not labels.',
      ui: {
        options: {
          editInModal: true,
        },
      },
    },
  },
  required: ['action', 'collection', 'key', 'value'],
};

/** The emitted message schema for the putItem action for the CollectionActor.
 * Always includes key and value. When meta: true, additionally includes
 * collection, timestamps, and labels. */
export const CollectionActorPutItemResultSchema = z.object({
  key: z.string()
    .describe('The key of the item'),
  value: z.unknown()
    .describe('The stored data'),
  collection: z.string().optional()
    .describe('The collection the item was put into (included when meta: true)'),
  labels: z.record(z.string(), z.string().nullable()).optional()
    .describe('The labels of the item (included when meta: true)'),
  createdAt: z.string().optional()
    .describe('The creation timestamp (included when meta: true)'),
  updatedAt: z.string().optional()
    .describe('The last-updated timestamp (included when meta: true)'),
  ttl: z.string().optional()
    .describe('The time-to-live of the item as ISO-8601 (included when meta: true)'),
});

export type CollectionActorPutItemResult = z.infer<typeof CollectionActorPutItemResultSchema>;
```

## actorSchemas/task/collection/query

**Source:** `actorSchemas/task/collection/query.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the query action for the CollectionActor */
export const CollectionActorQueryOptionsSchema = z.object({
  /** Must be query to access this function */
  action: z.literal(CollectionActorAction.Query)
    .describe('Must be query to access this function'),
  collection: z.string()
    .describe('The collection to query'),
  expression: z.string()
    .describe('The query expression'),
  options: z.object({
    limit: z.number().int().min(1).max(1000).default(100).optional()
      .describe('The maximum number of items to return, defaults to 100'),
    startKey: z.record(z.string(), z.string()).optional()
      .describe('Pagination start key from a previous query (pass the lastKey from a previous result)'),
    meta: z.boolean().optional()
      .describe('Whether to include metadata in the results'),
    label: z.string().optional()
      .describe('Filter by label'),
    reverse: z.boolean().optional()
      .describe('Whether to reverse the sort order'),
  }).optional()
    .describe('Options for the query operation'),
});

export type CollectionActorQueryOptions = z.infer<typeof CollectionActorQueryOptionsSchema>;

export const CollectionActorQueryOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be query to access this function',
      const: CollectionActorAction.Query,
    },
    collection: {
      type: BIQJsonSchemaType.String,
      title: 'Collection',
      description: 'The collection to query',
    },
    expression: {
      type: BIQJsonSchemaType.String,
      title: 'Expression',
      description: 'The query expression',
    },
    options: {
      type: BIQJsonSchemaType.Object,
      title: 'Options',
      description: 'Options for the query operation',
      properties: {
        limit: {
          type: BIQJsonSchemaType.Integer,
          title: 'Limit',
          description: 'The maximum number of items to return, defaults to 100',
          default: 100,
          minimum: 1,
          maximum: 1000,
        },
        startKey: {
          type: BIQJsonSchemaType.Any,
          title: 'Start key',
          description: 'Pagination start key from a previous query (pass the lastKey from a previous result)',
        },
        meta: {
          type: BIQJsonSchemaType.Boolean,
          title: 'Include metadata',
          description: 'Whether to include metadata in the results',
          ui: { component: 'switch' },
        },
        label: {
          type: BIQJsonSchemaType.String,
          title: 'Label',
          description: 'Filter by label',
        },
        reverse: {
          type: BIQJsonSchemaType.Boolean,
          title: 'Reverse',
          description: 'Whether to reverse the sort order',
          ui: { component: 'switch' },
        },
      },
    },
  },
  required: ['action', 'collection', 'expression'],
};

/** The emitted message schema for the query action for the CollectionActor.
 * Each item always includes key and value. When meta: true, additionally
 * includes collection, timestamps, and labels. */
export const CollectionActorQueryResultSchema = z.object({
  items: z.array(z.object({
    key: z.string()
      .describe('The key of the item'),
    value: z.unknown()
      .describe('The item data'),
    collection: z.string().optional()
      .describe('The collection the item belongs to (included when meta: true)'),
    labels: z.record(z.string(), z.string().nullable()).optional()
      .describe('The labels of the item (included when meta: true)'),
    createdAt: z.string().optional()
      .describe('The creation timestamp (included when meta: true)'),
    updatedAt: z.string().optional()
      .describe('The last-updated timestamp (included when meta: true)'),
    ttl: z.string().optional()
      .describe('The time-to-live of the item as ISO-8601 (included when meta: true)'),
  }))
    .describe('The items matching the query'),
  lastKey: z.record(z.string(), z.string()).optional()
    .describe('Key for the next page of results. Pass this as startKey to get the next page.'),
  count: z.number()
    .describe('The number of items returned'),
});

export type CollectionActorQueryResult = z.infer<typeof CollectionActorQueryResultSchema>;
```

## actorSchemas/task/collection/transactGet

**Source:** `actorSchemas/task/collection/transactGet.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the transactGet action for the CollectionActor */
export const CollectionActorTransactGetOptionsSchema = z.object({
  /** Must be transactGet to access this function */
  action: z.literal(CollectionActorAction.TransactGet)
    .describe('Must be transactGet to access this function'),
  items: z.array(z.object({
    collection: z.string()
      .describe('The collection to get the item from'),
    key: z.string()
      .describe('The key of the item to get'),
  })).max(100)
    .describe('The items to get in the transaction, up to 100'),
  options: z.object({
    meta: z.boolean().optional()
      .describe('Whether to include metadata in the results'),
  }).optional()
    .describe('Options for the transact get operation'),
});

export type CollectionActorTransactGetOptions = z.infer<typeof CollectionActorTransactGetOptionsSchema>;

export const CollectionActorTransactGetOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be transactGet to access this function',
      const: CollectionActorAction.TransactGet,
    },
    items: {
      type: BIQJsonSchemaType.Array,
      title: 'Items',
      description: 'The items to get in the transaction, up to 100',
      maxItems: 100,
      items: {
        type: BIQJsonSchemaType.Object,
        title: 'Item',
        properties: {
          collection: {
            type: BIQJsonSchemaType.String,
            title: 'Collection',
            description: 'The collection to get the item from',
          },
          key: {
            type: BIQJsonSchemaType.String,
            title: 'Key',
            description: 'The key of the item to get',
          },
        },
        required: ['collection', 'key'],
      },
    },
    options: {
      type: BIQJsonSchemaType.Object,
      title: 'Options',
      description: 'Options for the transact get operation',
      properties: {
        meta: {
          type: BIQJsonSchemaType.Boolean,
          title: 'Include metadata',
          description: 'Whether to include metadata in the results',
          ui: { component: 'switch' },
        },
      },
    },
  },
  required: ['action', 'items'],
};

/** The emitted message schema for the transactGet action for the CollectionActor.
 * Each item always includes key and value. When meta: true, additionally
 * includes collection, timestamps, and labels. */
export const CollectionActorTransactGetResultSchema = z.object({
  items: z.array(z.object({
    key: z.string()
      .describe('The key of the item'),
    value: z.unknown()
      .describe('The item data'),
    collection: z.string().optional()
      .describe('The collection the item belongs to (included when meta: true)'),
    labels: z.record(z.string(), z.string().nullable()).optional()
      .describe('The labels of the item (included when meta: true)'),
    createdAt: z.string().optional()
      .describe('The creation timestamp (included when meta: true)'),
    updatedAt: z.string().optional()
      .describe('The last-updated timestamp (included when meta: true)'),
    ttl: z.string().optional()
      .describe('The time-to-live of the item as ISO-8601 (included when meta: true)'),
  }).nullable())
    .describe('The retrieved items, null for items not found'),
});

export type CollectionActorTransactGetResult = z.infer<typeof CollectionActorTransactGetResultSchema>;
```

## actorSchemas/task/collection/transactWrite

**Source:** `actorSchemas/task/collection/transactWrite.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the transactWrite action for the CollectionActor */
export const CollectionActorTransactWriteOptionsSchema = z.object({
  /** Must be transactWrite to access this function */
  action: z.literal(CollectionActorAction.TransactWrite)
    .describe('Must be transactWrite to access this function'),
  items: z.array(z.object({
    operation: z.enum(['put', 'update', 'delete', 'check'])
      .describe('The operation to perform'),
    collection: z.string()
      .describe('The collection for the operation'),
    key: z.string()
      .describe('The key for the operation'),
    value: z.unknown().optional()
      .describe('The value for put/update operations'),
    labels: z.record(z.string(), z.string().nullable()).optional()
      .describe('Labels for the item'),
    ttl: z.union([z.number(), z.string(), z.null()]).optional()
      .describe('Time-to-live for the item'),
    conditions: z.record(z.string(), z.unknown()).optional()
      .describe('Conditional expressions for the operation. Applies to data fields only, not labels.'),
    atomicCounters: z.record(z.string(), z.number()).optional()
      .describe('Atomic counter increments to apply'),
  })).max(100)
    .describe('The items to transact, up to 100'),
  options: z.object({
    idempotencyKey: z.string().optional()
      .describe('An idempotency key for the transaction'),
  }).optional()
    .describe('Options for the transact write operation'),
});

export type CollectionActorTransactWriteOptions = z.infer<typeof CollectionActorTransactWriteOptionsSchema>;

export const CollectionActorTransactWriteOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be transactWrite to access this function',
      const: CollectionActorAction.TransactWrite,
    },
    items: {
      type: BIQJsonSchemaType.Array,
      title: 'Items',
      description: 'The items to transact, up to 100',
      maxItems: 100,
      items: {
        type: BIQJsonSchemaType.Object,
        title: 'Item',
        properties: {
          operation: {
            type: BIQJsonSchemaType.String,
            title: 'Operation',
            description: 'The operation to perform',
            enum: ['put', 'update', 'delete', 'check'],
            ui: { component: 'select' },
          },
          collection: {
            type: BIQJsonSchemaType.String,
            title: 'Collection',
            description: 'The collection for the operation',
          },
          key: {
            type: BIQJsonSchemaType.String,
            title: 'Key',
            description: 'The key for the operation',
          },
          value: {
            type: BIQJsonSchemaType.Any,
            title: 'Value',
            description: 'The value for put/update operations',
            ui: { options: { editInModal: true } },
          },
          labels: {
            type: BIQJsonSchemaType.Any,
            title: 'Labels',
            description: 'Labels for the item',
          },
          ttl: {
            title: 'TTL',
            description: 'Time-to-live for the item',
            anyOf: [
              { type: BIQJsonSchemaType.Number, title: 'TTL (seconds)' },
              { type: BIQJsonSchemaType.String, title: 'TTL (expression)' },
            ],
          },
          conditions: {
            type: BIQJsonSchemaType.Any,
            title: 'Conditions',
            description: 'Conditional expressions for the operation. Applies to data fields only, not labels.',
            ui: { options: { editInModal: true } },
          },
          atomicCounters: {
            type: BIQJsonSchemaType.Any,
            title: 'Atomic counters',
            description: 'Atomic counter increments to apply',
            ui: { options: { editInModal: true } },
          },
        },
        required: ['operation', 'collection', 'key'],
      },
    },
    options: {
      type: BIQJsonSchemaType.Object,
      title: 'Options',
      description: 'Options for the transact write operation',
      properties: {
        idempotencyKey: {
          type: BIQJsonSchemaType.String,
          title: 'Idempotency key',
          description: 'An idempotency key for the transaction',
        },
      },
    },
  },
  required: ['action', 'items'],
};

/** The emitted message schema for the transactWrite action for the CollectionActor */
export const CollectionActorTransactWriteResultSchema = z.object({
  processed: z.number()
    .describe('The number of items processed'),
});

export type CollectionActorTransactWriteResult = z.infer<typeof CollectionActorTransactWriteResultSchema>;
```

## actorSchemas/task/collection/updateCollection

**Source:** `actorSchemas/task/collection/updateCollection.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the updateCollection action for the CollectionActor */
export const CollectionActorUpdateCollectionOptionsSchema = z.object({
  /** Must be updateCollection to access this function */
  action: z.literal(CollectionActorAction.UpdateCollection)
    .describe('Must be updateCollection to access this function'),
  slug: z.string()
    .describe('The slug of the collection to update'),
  name: z.string().optional()
    .describe('The new name for the collection'),
  description: z.string().nullable().optional()
    .describe('The new description for the collection, or null to remove'),
  addLabels: z.array(z.string()).optional()
    .describe('Labels to add to the collection'),
  removeLabels: z.array(z.string()).optional()
    .describe('Labels to remove from the collection'),
});

export type CollectionActorUpdateCollectionOptions = z.infer<typeof CollectionActorUpdateCollectionOptionsSchema>;

export const CollectionActorUpdateCollectionOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be updateCollection to access this function',
      const: CollectionActorAction.UpdateCollection,
    },
    slug: {
      type: BIQJsonSchemaType.String,
      title: 'Slug',
      description: 'The slug of the collection to update',
    },
    name: {
      type: BIQJsonSchemaType.String,
      title: 'Name',
      description: 'The new name for the collection',
    },
    description: {
      type: BIQJsonSchemaType.String,
      title: 'Description',
      description: 'The new description for the collection, or null to remove',
    },
    addLabels: {
      type: BIQJsonSchemaType.Array,
      title: 'Add labels',
      description: 'Labels to add to the collection',
      items: { type: BIQJsonSchemaType.String, title: 'Label' },
    },
    removeLabels: {
      type: BIQJsonSchemaType.Array,
      title: 'Remove labels',
      description: 'Labels to remove from the collection',
      items: { type: BIQJsonSchemaType.String, title: 'Label' },
    },
  },
  required: ['action', 'slug'],
};

/** The emitted message schema for the updateCollection action for the CollectionActor */
export const CollectionActorUpdateCollectionResultSchema = z.object({
  slug: z.string()
    .describe('The slug of the updated collection'),
  name: z.string()
    .describe('The name of the updated collection'),
  description: z.string().optional()
    .describe('The description of the updated collection'),
  labels: z.array(z.string())
    .describe('The labels of the updated collection'),
  updatedAt: z.string()
    .describe('The update timestamp'),
});

export type CollectionActorUpdateCollectionResult = z.infer<typeof CollectionActorUpdateCollectionResultSchema>;
```

## actorSchemas/task/collection/updateItem

**Source:** `actorSchemas/task/collection/updateItem.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the updateItem action for the CollectionActor */
export const CollectionActorUpdateItemOptionsSchema = z.object({
  /** Must be updateItem to access this function */
  action: z.literal(CollectionActorAction.UpdateItem)
    .describe('Must be updateItem to access this function'),
  collection: z.string()
    .describe('The collection containing the item'),
  key: z.string()
    .describe('The key of the item to update'),
  value: z.record(z.string(), z.unknown()).optional()
    .describe('The value fields to update'),
  labels: z.record(z.string(), z.string().nullable()).optional()
    .describe('Labels to update on the item'),
  ttl: z.union([z.number(), z.string(), z.null()]).optional()
    .describe('Time-to-live to set on the item'),
  options: z.object({
    meta: z.boolean().optional()
      .describe('Whether to include metadata in the result'),
  }).optional()
    .describe('Options for the update operation'),
  conditions: z.record(z.string(), z.unknown()).optional()
    .describe('Conditional expressions for the update operation. Applies to data fields only, not labels.'),
  atomicCounters: z.record(z.string(), z.number()).optional()
    .describe('Atomic counter increments to apply'),
});

export type CollectionActorUpdateItemOptions = z.infer<typeof CollectionActorUpdateItemOptionsSchema>;

export const CollectionActorUpdateItemOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be updateItem to access this function',
      const: CollectionActorAction.UpdateItem,
    },
    collection: {
      type: BIQJsonSchemaType.String,
      title: 'Collection',
      description: 'The collection containing the item',
    },
    key: {
      type: BIQJsonSchemaType.String,
      title: 'Key',
      description: 'The key of the item to update',
    },
    value: {
      type: BIQJsonSchemaType.Any,
      title: 'Value',
      description: 'The value fields to update',
      ui: {
        options: {
          editInModal: true,
        },
      },
    },
    labels: {
      type: BIQJsonSchemaType.Any,
      title: 'Labels',
      description: 'Labels to update on the item',
    },
    ttl: {
      title: 'TTL',
      description: 'Time-to-live to set on the item',
      anyOf: [
        { type: BIQJsonSchemaType.Number, title: 'TTL (seconds)' },
        { type: BIQJsonSchemaType.String, title: 'TTL (expression)' },
      ],
    },
    options: {
      type: BIQJsonSchemaType.Object,
      title: 'Options',
      description: 'Options for the update operation',
      properties: {
        meta: {
          type: BIQJsonSchemaType.Boolean,
          title: 'Include metadata',
          description: 'Whether to include metadata in the result',
          ui: { component: 'switch' },
        },
      },
    },
    conditions: {
      type: BIQJsonSchemaType.Any,
      title: 'Conditions',
      description: 'Conditional expressions for the update operation. Applies to data fields only, not labels.',
      ui: {
        options: {
          editInModal: true,
        },
      },
    },
    atomicCounters: {
      type: BIQJsonSchemaType.Any,
      title: 'Atomic counters',
      description: 'Atomic counter increments to apply',
      ui: {
        options: {
          editInModal: true,
        },
      },
    },
  },
  required: ['action', 'collection', 'key'],
};

/** The emitted message schema for the updateItem action for the CollectionActor.
 * Always includes key and value. When meta: true, additionally includes
 * collection, timestamps, and labels. */
export const CollectionActorUpdateItemResultSchema = z.object({
  key: z.string()
    .describe('The key of the item'),
  value: z.unknown()
    .describe('The updated data'),
  collection: z.string().optional()
    .describe('The collection the item belongs to (included when meta: true)'),
  labels: z.record(z.string(), z.string().nullable()).optional()
    .describe('The labels of the item (included when meta: true)'),
  createdAt: z.string().optional()
    .describe('The creation timestamp (included when meta: true)'),
  updatedAt: z.string().optional()
    .describe('The last-updated timestamp (included when meta: true)'),
  ttl: z.string().optional()
    .describe('The time-to-live of the item as ISO-8601 (included when meta: true)'),
});

export type CollectionActorUpdateItemResult = z.infer<typeof CollectionActorUpdateItemResultSchema>;
```
