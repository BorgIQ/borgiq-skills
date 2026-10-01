# actorSchemas/task/collection/createCollection

Generated from the platform's runtime types. Do not edit.

The options schema for the createCollection action for the CollectionActor.

See also: [actorSchemas/task/collection/actions](actions.md), [actorSchemas/task/collection/labelSlots](labelSlots.md).

## actorSchemas/task/collection/createCollection

**Source:** `actorSchemas/task/collection/createCollection.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';
import { MAX_LABEL_SLOTS } from './labelSlots.js';

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
  labels: z.array(z.string()).max(MAX_LABEL_SLOTS).optional()
    .describe(`Optional labels for the collection, up to ${MAX_LABEL_SLOTS}`),
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
      description: `Optional labels for the collection, up to ${MAX_LABEL_SLOTS}`,
      items: { type: BIQJsonSchemaType.String, title: 'Label' },
      maxItems: MAX_LABEL_SLOTS,
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
