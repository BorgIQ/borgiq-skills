# actorSchemas/task/collection/deleteCollection

Generated from the platform's runtime types. Do not edit.

The options schema for the deleteCollection action for the CollectionActor.

See also: [actorSchemas/task/collection/actions](actions.md).

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
