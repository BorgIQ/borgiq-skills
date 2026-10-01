# actorSchemas/task/messageProcessor/delayBySeconds

Generated from the platform's runtime types. Do not edit.

The options schema for the delayBySeconds action in the MessageProcessorActor.

See also: [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/delayBySeconds

**Source:** `actorSchemas/task/messageProcessor/delayBySeconds.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the delayBySeconds action in the MessageProcessorSchema */
export const MessageProcessorActorDelayBySecondsOptionsSchema = z.object({
  /** Must be delayBySeconds to access this function */
  action: z.literal(MessageProcessorAction.DelayBySeconds)
    .describe('Must be delayBySeconds to access this function'),
  /** The number of seconds to delay emitting the message */
  seconds: z.number().gte(0)
    .describe('The number of seconds to delay emitting the message'),
});

export type MessageProcessorActorDelayBySecondsOptions = z.infer<typeof MessageProcessorActorDelayBySecondsOptionsSchema>;

export const MessageProcessorActorDelayBySecondsOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.DelayBySeconds,
    },
    seconds: {
      type: BIQJsonSchemaType.Number,
      title: 'Seconds',
      description: 'The number of seconds to delay emitting the message',
      minimum: 0,
    },
  },
  required: ['action', 'seconds'],
};

/** The emitted message schema for the delayBySeconds action in the MessageProcessorSchema */
export const MessageProcessorActorDelayResultSchema = z.object({
  /** the date the messaged emitted at as ISO formatted date time string */
  delayUntil: z.string(),
});

export type MessageProcessorActorDelayResult = z.infer<typeof MessageProcessorActorDelayResultSchema>;
```
