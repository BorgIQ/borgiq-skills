# actorSchemas/task/collection/batchWriteItem

Generated from the platform's runtime types. Do not edit.

The options schema for the batchWriteItem action for the CollectionActor.

See also: [actorSchemas/task/collection/actions](actions.md).

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
