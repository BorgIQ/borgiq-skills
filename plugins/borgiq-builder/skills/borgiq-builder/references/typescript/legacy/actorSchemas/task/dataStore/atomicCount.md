# actorSchemas/task/dataStore/atomicCount

Generated from the platform's runtime types. Do not edit.

Legacy: DataStoreActor is kept only so existing canvases load. Build new storage with CollectionActor.

The options schema for the atomicCount action for the DataStoreActor.

See also: [schemas/jsonSchema](../../../schemas/jsonSchema.md), [actorSchemas/task/dataStore/actions](actions.md).

## actorSchemas/task/dataStore/atomicCount

**Source:** `actorSchemas/task/dataStore/atomicCount.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the atomicCount action for the DataStoreActor */
export const DataStoreActorAtomicCountOptionsSchema = z.object({
  action: z.literal(DataStoreActorAction.AtomicCount)
    .describe('Must be atomicCount to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe('The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'),
  key: z.string().min(1)
    .describe('The key to increment or decrement'),
  valueToAdd: z.number().int().nullish()
    .describe('The value to add to the value stored under key, defaults to 1. Values can be positive or negative'),
});

export type DataStoreActorAtomicCountOptions = z.infer<typeof DataStoreActorAtomicCountOptionsSchema>;

export const DataStoreActorAtomicCountOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: DataStoreActorAction.AtomicCount
    },
    scope: {
      type: BIQJsonSchemaType.String,
      title: 'Scope',
      description: 'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope',
      enum: ['canvas', 'workspace'],
      default: 'canvas',
    },
    key: {
      type: BIQJsonSchemaType.String,
      title: 'Key',
      description: 'The key to increment or decrement',
      minLength: 1,
    },
    valueToAdd: {
      type: BIQJsonSchemaType.Integer,
      title: 'Value to add',
      description: 'The value to add to the value stored under key, defaults to 1. Values can be positive or negative',
      ui: {
        options: {
          placeholder: '1',
        }
      }
    }
  },
  required: ['action', 'scope', 'key'],
};

/** The emitted message schema for the atomicCount action for the DataStoreActor */
export const DataStoreActorAtomicCountResultSchema = z.object({
  key: z.string()
    .describe('The key the atomic count action was completed on'),
  value: z.number().int()
    .describe('The updated value of the atomic count'),
});

export type DataStoreActorAtomicCountResult = z.infer<typeof DataStoreActorAtomicCountResultSchema>;
```
