# actorSchemas/task/messageProcessor/fork

Generated from the platform's runtime types. Do not edit.

The options schema for the fork action in the MessageProcessorActor.

See also: [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/fork

**Source:** `actorSchemas/task/messageProcessor/fork.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the fork action in the MessageProcessorActor */
export const MessageProcessorActorForkOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.Fork)
    .describe('Must be fork to access this function'),
});

export type MessageProcessorActorForkOptions = z.infer<typeof MessageProcessorActorForkOptionsSchema>;

export const MessageProcessorActorForkOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.Fork,
    },
  },
  required: ['action'],
};

/** The emitted message schema for the fork action in the MessageProcessorActor */
export const MessageProcessorActorForkResultSchema = z.object({
  forkId: z.string()
    .describe('The unique ID to be used by the downstream Message Processor Actor with the forkJoin action'),
});

export type MessageProcessorActorForkResult = z.infer<typeof MessageProcessorActorForkResultSchema>;
```
