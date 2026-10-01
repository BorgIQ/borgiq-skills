# actorSchemas/task/dataStore/enqueue

Generated from the platform's runtime types. Do not edit.

Legacy: DataStoreActor is kept only so existing canvases load. Build new storage with CollectionActor.

The options schema for the enqueue action for the DataStoreActor.

See also: [schemas/jsonSchema](../../../schemas/jsonSchema.md), [actorSchemas/task/dataStore/actions](actions.md).

## actorSchemas/task/dataStore/enqueue

**Source:** `actorSchemas/task/dataStore/enqueue.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { DataStoreActorAction } from './actions.js';

/** The options schema for the enqueue action for the DataStoreActor */
export const DataStoreActorEnqueueOptionsSchema = z.object({
  action: z.literal(DataStoreActorAction.Enqueue)
    .describe('Must be enqueue to access this function'),
  scope: z.enum(['canvas', 'workspace'])
    .describe(
      'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope'
    ),
  queueName: z.string().min(1)
    .describe('The name of the queue to enqueue to'),
  value: z.unknown()
    .refine((value) => value !== undefined, { message: 'Required' })
    .describe('The value(s) to enqueue'),
  enqueueAsASingleValue: z.boolean().nullish()
    .describe('If to enqueue array values as one value, if its false each item in the array will be enqueued as a separate value. Default value is false'),
});

export type DataStoreActorEnqueueOptions = z.infer<typeof DataStoreActorEnqueueOptionsSchema>;

export const DataStoreActorEnqueueOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be enqueue to access this function',
      const: DataStoreActorAction.Enqueue,
    },
    scope: {
      type: BIQJsonSchemaType.String,
      title: 'Scope',
      description: 'The scope of the key you want to set, is its accessible to only to this canvas or across this workspace. Keys under the canvas scope are not accessible with workspace scope',
      enum: ['canvas', 'workspace'],
      default: 'canvas',
    },
    queueName: {
      type: BIQJsonSchemaType.String,
      title: 'Queue name',
      description: 'The name of the queue to enqueue to',
      minLength: 1,
    },
    value: {
      type: BIQJsonSchemaType.Any,
      title: 'Value',
      description: 'The value(s) to enqueue',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
    enqueueAsASingleValue: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Enqueue as a single value',
      description: 'If to enqueue array values as one value, if its false each item in the array will be enqueued as a separate value. Default value is false',
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['action', 'scope', 'queueName', 'value'],
};

/** The emitted message schema for the enqueue action for the DataStoreActor */
export const DataStoreActorEnqueueResultSchema = z.object({
  data: z.object({
    queueName: z.string()
      .describe('The name of the queue the item was enqueued to'),
    value: z.unknown()
      .describe('The value(s) enqueued to the queue'),
  }),
  size: z.number().int()
    .describe('The size of the queue after the enqueue'),
});

export type DataStoreActorEnqueueResult = z.infer<typeof DataStoreActorEnqueueResultSchema>;
```
