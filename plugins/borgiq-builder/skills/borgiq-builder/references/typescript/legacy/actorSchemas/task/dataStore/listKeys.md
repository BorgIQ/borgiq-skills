# actorSchemas/task/dataStore/listKeys

Generated from the platform's runtime types. Do not edit.

Legacy: DataStoreActor is kept only so existing canvases load. Build new storage with CollectionActor.

The options schema for the listKeys action for the DataStoreActor.

See also: [schemas/jsonSchema](../../../schemas/jsonSchema.md), [actorSchemas/task/dataStore/actions](actions.md).

## actorSchemas/task/dataStore/listKeys

**Source:** `actorSchemas/task/dataStore/listKeys.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the listKeys action for the DataStoreActor */
export const DataStoreActorListKeysOptionsSchema = z.object({
  action: z.literal(DataStoreActorAction.ListKeys)
    .describe('Must be listKeys to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe(
      'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'
    ),
  page: z.number().int().min(1).nullish()
    .describe('The page number to retrieve, defaults to 1'),
  pageSize: z.number().int().min(1).nullish()
    .describe('The amount of keys to retrieve per page, defaults to 10'),
  sortBy: z.enum(['key', 'createdAt', 'updatedAt']).nullish()
    .describe('The field to sort by, defaults to key'),
  sortOrder: z.enum(['asc', 'desc']).nullish()
    .describe('The order to sort by, defaults to asc'),
  search: z.string().nullish()
    .describe('Filter returned keys with a search value, an empty string indicated no filtering. Defaults to \'\''),
});

export type DataStoreActorListKeysOptions = z.infer<typeof DataStoreActorListKeysOptionsSchema>;

export const DataStoreActorListKeysOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be listKeys to access this function',
      const: DataStoreActorAction.ListKeys,
    },
    scope: {
      type: BIQJsonSchemaType.String,
      title: 'Scope',
      description: 'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope',
      enum: ['canvas', 'workspace'],
      default: 'canvas',
    },
    page: {
      type: BIQJsonSchemaType.Integer,
      title: 'Page',
      description: 'The page number to retrieve, defaults to 1',
      default: 1,
      ui: {
        options: {
          placeholder: '1',
        },
      },
    },
    pageSize: {
      type: BIQJsonSchemaType.Integer,
      title: 'Page size',
      description: 'The amount of keys to retrieve per page, defaults to 10',
      default: 10,
      ui: {
        options: {
          placeholder: '10',
        },
      },
    },
    sortBy: {
      type: BIQJsonSchemaType.String,
      title: 'Sort by',
      description: 'The field to sort by, defaults to key',
      enum: ['key', 'createdAt', 'updatedAt'],
      default: 'key',
    },
    sortOrder: {
      type: BIQJsonSchemaType.String,
      title: 'Sort order',
      description: 'The order to sort by, defaults to asc',
      enum: ['asc', 'desc'],
      default: 'asc',
    },
    search: {
      type: BIQJsonSchemaType.String,
      title: 'Search',
      description: 'Filter returned keys with a search value, an empty string indicated no filtering. Defaults to \'\'',
      default: '',
    },
  },
  required: ['action', 'scope'],
};

/** The emitted message schema for the listKeys action for the DataStoreActor */
export const DataStoreActorListKeysResultSchema = z.object({
  keys: z.array(z.string())
    .describe('The keys retrieved'),
  total: z.number().int()
    .describe('The total number of keys'),
  page: z.number().int()
    .describe('The page number retrieved'),
  pageSize: z.number().int()
    .describe('The amount of keys retrieved per page'),
});

export type DataStoreActorListKeysResult = z.infer<typeof DataStoreActorListKeysResultSchema>;
```
