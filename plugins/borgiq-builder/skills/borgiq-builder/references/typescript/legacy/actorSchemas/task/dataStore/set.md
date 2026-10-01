# actorSchemas/task/dataStore/set

Generated from the platform's runtime types. Do not edit.

Legacy: DataStoreActor is kept only so existing canvases load. Build new storage with CollectionActor.

The options schema for the set action for the DataStoreActor.

See also: [schemas/jsonSchema](../../../schemas/jsonSchema.md), [actorSchemas/task/dataStore/actions](actions.md).

## actorSchemas/task/dataStore/set

**Source:** `actorSchemas/task/dataStore/set.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the set action for the DataStoreActor  */
export const DataStoreActorSetOptionsSchema = z.object({
  action: z.literal(DataStoreActorAction.Set)
    .describe('Must be set to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe(
      'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'
    ),
  key: z.string().min(1)
    .describe('The key to set the value of'),
  value: z.unknown()
    .refine((value) => value !== undefined, { message: 'Required' })
    .describe('The value to set'),
});

export type DataStoreActorSetOptions = z.infer<typeof DataStoreActorSetOptionsSchema>;

export const DataStoreActorSetOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be set to access this function',
      const: DataStoreActorAction.Set,
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
      description: 'The key to set the value of',
    },
    value: {
      type: BIQJsonSchemaType.Any,
      title: 'Value',
      description: 'The value to set',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
  },
  required: ['action', 'scope', 'key', 'value'],
};


/** The emitted message schema for the set action for the DataStoreActor */
export const DataStoreActorSetResultSchema = z.object({
  key: z.string()
    .describe('The key the value was set to'),
  value: z.unknown()
    .describe('The value set'),
});

export type DataStoreActorSetResult = z.infer<typeof DataStoreActorSetResultSchema>;
```
