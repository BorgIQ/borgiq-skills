# actorSchemas/task/collection/getItem

Generated from the platform's runtime types. Do not edit.

The options schema for the getItem action for the CollectionActor.

See also: [actorSchemas/task/collection/actions](actions.md).

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
