# actorSchemas/task/collection/updateItem

Generated from the platform's runtime types. Do not edit.

The options schema for the updateItem action for the CollectionActor.

See also: [actorSchemas/task/collection/actions](actions.md).

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
