# actorSchemas/task/interfaceStatus

Generated from the platform's runtime types. Do not edit.

The options schema for the InterfaceStatusActor.

See also: [formComponents/form](../../formComponents/form.md).

## actorSchemas/task/interfaceStatus

**Source:** `actorSchemas/task/interfaceStatus.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchemaType, BIQJsonSchema } from '../../schemas/index.js';
import { BIQFormComponentZodSchema } from '../../formComponents/form.js';

/** The options schema for the InterfaceStatusActor */
export const InterfaceStatusActorOptionsSchema = z.object({
  component: BIQFormComponentZodSchema.optional()
    .describe('The component to add/update to the status area of a waiting for interface page'),
  emitComponents: z.boolean().optional()
    .describe('Whether to emit the components to the status area of a waiting for interface page'),
  order: z.enum(['append', 'prepend']).optional()
    .describe('The order to add the component if not already present to the status area of a waiting for interface page'),
});

export type InterfaceStatusActorOptions = z.infer<typeof InterfaceStatusActorOptionsSchema>;

export const InterfaceStatusActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    component: {
      type: BIQJsonSchemaType.Any,
      title: 'Component',
      description: 'The component to add/update to the status area of a waiting for interface page',
      ui: {
        component: 'modal',
        options: {
          language: 'yaml',
        },
      }
    },
    emitComponents: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit components',
      description: 'Whether to emit the components to the status area of a waiting for interface page',
    },
    order: {
      type: BIQJsonSchemaType.String,
      title: 'Order',
      description: 'The order to add the component if not already present to the status area of a waiting for interface page',
      enum: ['append', 'prepend'],
      default: 'prepend',
    },
  },
  required: [],
};

/** the message response schema for the InterfaceStatusActor */
export const InterfaceStatusActorResultSchema = z.object({
  status: z.string()
    .describe('The status of the interface'),
  statusComponents: z.array(BIQFormComponentZodSchema).optional()
    .describe('The components to add/update to the status area of a waiting for interface page'),
});

export type InterfaceStatusActorResult = z.infer<typeof InterfaceStatusActorResultSchema>;
```
