# actorSchemas/task/messageProcessor/forkJoin

Generated from the platform's runtime types. Do not edit.

The options schema for the forkJoin action in the MessageProcessorActor.

See also: [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/forkJoin

**Source:** `actorSchemas/task/messageProcessor/forkJoin.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options for the forkJoin actor in the MessageProcessorActor */
export const MessageProcessorActorForkJoinOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.ForkJoin)
    .describe('Must be forkJoin to access this function'),
  forkId: z.string()
    .describe('The forkId emitted by the upstream MessageProcessorActor with the fork action. Messages with the same forkId will be collected in the same message'),
  size: z.number().int().gt(0)
    .describe('The number of unique upstream actors whose messages it should collect before emitting. Defaults to ctx.actor.upstreamActorCount (the number of active actors with an edge into this one), which it CAN NOT exceed'),
});

export type MessageProcessorActorForkJoinOptions = z.infer<typeof MessageProcessorActorForkJoinOptionsSchema>;

export const MessageProcessorActorForkJoinOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.ForkJoin,
    },
    forkId: {
      type: BIQJsonSchemaType.String,
      title: 'Fork ID',
      description: 'The forkId emitted by the upstream MessageProcessorActor with the fork action. Messages with the same forkId will be collected in the same message',
      default: '${{msg.FORK_ACTOR.forkId}}',
    },
    size: {
      type: BIQJsonSchemaType.Integer,
      exclusiveMinimum: 0,
      title: 'Size',
      description: 'The number of unique upstream actors whose messages it should collect before emitting. Defaults to ctx.actor.upstreamActorCount (the number of active actors with an edge into this one), which it CAN NOT exceed',
      default: '${{ctx.actor.upstreamActorCount}}',
    },
  },
  required: ['action', 'forkId', 'size'],
};

/** The emitted message schema for the forkJoin action in the MessageProcessorActor */
/** Each key in the emitted message would be the actor that is the the source actor */
export const MessageProcessorActorForkJoinResultSchema = z.record(z.string(),
  z.array(z.record(z.string(), z.any())),
);

export type MessageProcessorActorForkJoinResult = z.infer<typeof MessageProcessorActorForkJoinResultSchema>;
```
