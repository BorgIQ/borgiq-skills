# actorSchemas/task/collection/query

Generated from the platform's runtime types. Do not edit.

The options schema for the query action for the CollectionActor.

See also: [actorSchemas/task/collection/actions](actions.md).

## actorSchemas/task/collection/query

**Source:** `actorSchemas/task/collection/query.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the query action for the CollectionActor */
export const CollectionActorQueryOptionsSchema = z.object({
  /** Must be query to access this function */
  action: z.literal(CollectionActorAction.Query)
    .describe('Must be query to access this function'),
  collection: z.string()
    .describe('The collection to query'),
  expression: z.string()
    .describe('The query expression'),
  options: z.object({
    limit: z.number().int().min(1).max(1000).default(100).optional()
      .describe('The maximum number of items to return, defaults to 100'),
    startKey: z.record(z.string(), z.string()).optional()
      .describe('Pagination start key from a previous query (pass the lastKey from a previous result)'),
    meta: z.boolean().optional()
      .describe('Whether to include metadata in the results'),
    label: z.string().optional()
      .describe('Filter by label'),
    reverse: z.boolean().optional()
      .describe('Whether to reverse the sort order'),
  }).optional()
    .describe('Options for the query operation'),
});

export type CollectionActorQueryOptions = z.infer<typeof CollectionActorQueryOptionsSchema>;

export const CollectionActorQueryOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be query to access this function',
      const: CollectionActorAction.Query,
    },
    collection: {
      type: BIQJsonSchemaType.String,
      title: 'Collection',
      description: 'The collection to query',
    },
    expression: {
      type: BIQJsonSchemaType.String,
      title: 'Expression',
      description: 'The query expression',
    },
    options: {
      type: BIQJsonSchemaType.Object,
      title: 'Options',
      description: 'Options for the query operation',
      properties: {
        limit: {
          type: BIQJsonSchemaType.Integer,
          title: 'Limit',
          description: 'The maximum number of items to return, defaults to 100',
          default: 100,
          minimum: 1,
          maximum: 1000,
        },
        startKey: {
          type: BIQJsonSchemaType.Any,
          title: 'Start key',
          description: 'Pagination start key from a previous query (pass the lastKey from a previous result)',
        },
        meta: {
          type: BIQJsonSchemaType.Boolean,
          title: 'Include metadata',
          description: 'Whether to include metadata in the results',
          ui: { component: 'switch' },
        },
        label: {
          type: BIQJsonSchemaType.String,
          title: 'Label',
          description: 'Filter by label',
        },
        reverse: {
          type: BIQJsonSchemaType.Boolean,
          title: 'Reverse',
          description: 'Whether to reverse the sort order',
          ui: { component: 'switch' },
        },
      },
    },
  },
  required: ['action', 'collection', 'expression'],
};

/** The emitted message schema for the query action for the CollectionActor.
 * Each item always includes key and value. When meta: true, additionally
 * includes collection, timestamps, and labels. */
export const CollectionActorQueryResultSchema = z.object({
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
  }))
    .describe('The items matching the query'),
  lastKey: z.record(z.string(), z.string()).optional()
    .describe('Key for the next page of results. Pass this as startKey to get the next page.'),
  count: z.number()
    .describe('The number of items returned'),
});

export type CollectionActorQueryResult = z.infer<typeof CollectionActorQueryResultSchema>;
```
