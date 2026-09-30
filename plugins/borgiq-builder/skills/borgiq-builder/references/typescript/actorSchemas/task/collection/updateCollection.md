# actorSchemas/task/collection/updateCollection

Generated from the platform's runtime types. Do not edit.

The options schema for the updateCollection action for the CollectionActor.

See also: [actorSchemas/task/collection/actions](actions.md).

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
