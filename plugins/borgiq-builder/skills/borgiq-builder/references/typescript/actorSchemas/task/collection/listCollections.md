# actorSchemas/task/collection/listCollections

Generated from the platform's runtime types. Do not edit.

The options schema for the listCollections action for the CollectionActor.

See also: [actorSchemas/task/collection/actions](actions.md).

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
