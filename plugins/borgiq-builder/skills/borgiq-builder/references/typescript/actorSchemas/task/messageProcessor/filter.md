# actorSchemas/task/messageProcessor/filter

Generated from the platform's runtime types. Do not edit.

The options schema for the filter action in the MessageProcessorActor.

See also: [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/filter

**Source:** `actorSchemas/task/messageProcessor/filter.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the filter action in the MessageProcessorActor */
export const MessageProcessorActorFilterOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.Filter)
    .describe('Must be filter to access this function'),
  filter: z.boolean(),
});

export type MessageProcessorActorFilterOptions = z.infer<typeof MessageProcessorActorFilterOptionsSchema>;

export const MessageProcessorActorFilterOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.Filter,
    },
    filter: {
      type: BIQJsonSchemaType.Boolean,
      default: '${{}}',
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['action', 'filter'],
};

/** The emitted message schema for the filter action in the MessageProcessorActor */
export const MessageProcessorActorFilterResultSchema = z.boolean();

export type MessageProcessorActorFilterResult = z.infer<typeof MessageProcessorActorFilterResultSchema>;
```
