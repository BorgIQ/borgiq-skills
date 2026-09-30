# actorSchemas/task/collection/putItem

Generated from the platform's runtime types. Do not edit.

The options schema for the putItem action for the CollectionActor.

See also: [actorSchemas/task/collection/actions](actions.md).

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
