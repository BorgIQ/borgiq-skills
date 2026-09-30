# actorSchemas/task/dataStore/delete

Generated from the platform's runtime types. Do not edit.

Legacy: DataStoreActor is kept only so existing canvases load. Build new storage with CollectionActor.

The options schema for the delete action for the DataStoreActor.

See also: [schemas/jsonSchema](../../../schemas/jsonSchema.md), [actorSchemas/task/dataStore/actions](actions.md).

## actorSchemas/task/dataStore/delete

**Source:** `actorSchemas/task/dataStore/delete.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the delete action for the DataStoreActor */
export const DataStoreActorDeleteOptionsSchema = z.object({
  /** Must be delete to access this function */
  action: z.literal(DataStoreActorAction.Delete)
    .describe('Must be delete to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe(
      'The scope of the key you want to delete, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'
    ),
  key: z.string().min(1)
    .describe('The key to delete'),
});

export type DataStoreActorDeleteOptions = z.infer<typeof DataStoreActorDeleteOptionsSchema>;

export const DataStoreActorDeleteOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be delete to access this function',
      const: DataStoreActorAction.Delete,
    },
    scope: {
      type: BIQJsonSchemaType.String,
      title: 'Scope',
      description: 'The scope of the key you want to delete, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope',
      enum: ['canvas', 'workspace'],
    },
    key: {
      type: BIQJsonSchemaType.String,
      title: 'Key',
      description: 'The key to delete',
      minLength: 1,
    },
  },
  required: ['action', 'scope', 'key'],
};

/** The emitted message schema for the delete action for the DataStoreActor */
export const DataStoreActorDeleteResultSchema = z.literal('deleted');

export type DataStoreActorDeleteResult = z.infer<typeof DataStoreActorDeleteResultSchema>;
```
