# actorSchemas/task/collection/deleteItem

Generated from the platform's runtime types. Do not edit.

The options schema for the deleteItem action for the CollectionActor.

See also: [actorSchemas/task/collection/actions](actions.md).

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
