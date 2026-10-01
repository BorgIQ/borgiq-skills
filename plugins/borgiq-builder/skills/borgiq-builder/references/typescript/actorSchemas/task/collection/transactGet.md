# actorSchemas/task/collection/transactGet

Generated from the platform's runtime types. Do not edit.

The options schema for the transactGet action for the CollectionActor.

See also: [actorSchemas/task/collection/actions](actions.md).

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
