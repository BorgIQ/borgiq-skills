# actorSchemas/task/dataStore/get

Generated from the platform's runtime types. Do not edit.

Legacy: DataStoreActor is kept only so existing canvases load. Build new storage with CollectionActor.

The options schema for the get action for the DataStoreActor.

See also: [schemas/jsonSchema](../../../schemas/jsonSchema.md), [actorSchemas/task/dataStore/actions](actions.md).

## actorSchemas/task/dataStore/get

**Source:** `actorSchemas/task/dataStore/get.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the get action for the DataStoreActor */
export const DataStoreActorGetOptionsSchema = z.object({
  /** Must be get to access this function */
  action: z.literal(DataStoreActorAction.Get)
    .describe('Must be get to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe(
      'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'
    ),
  key: z.string().min(1)
    .describe('The key to get the value of'),
  defaultValue: z.unknown().nullish()
    .describe('The value to emit if the key does not exist, otherwise defaults to null'),
});

export type DataStoreActorGetOptions = z.infer<typeof DataStoreActorGetOptionsSchema>;

export const DataStoreActorGetOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be get to access this function',
      const: DataStoreActorAction.Get,
    },
    scope: {
      type: BIQJsonSchemaType.String,
      title: 'Scope',
      description: 'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope',
      enum: ['canvas', 'workspace'],
    },
    key: {
      type: BIQJsonSchemaType.String,
      title: 'Key',
      description: 'The key to get the value of',
      minLength: 1,
    },
    defaultValue: {
      type: BIQJsonSchemaType.Any,
      title: 'Default value',
      description: 'The value to emit if the key does not exist, otherwise defaults to null',
      ui: {
        options: {
          placeholder: 'null',
          editInModal: true,
        },
      },
    },
  },
  required: ['action', 'scope', 'key'],
};

/** The emitted message schema for the get action for the DataStoreActor */
export const DataStoreActorGetResultSchema = z.object({
  key: z.string()
    .describe('The key the value was retrieved from'),
  value: z.unknown()
    .describe('The value of the key'),
});

export type DataStoreActorGetResult = z.infer<typeof DataStoreActorGetResultSchema>;
```
