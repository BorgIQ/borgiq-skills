# actorSchemas/task/stream/listStreams

Generated from the platform's runtime types. Do not edit.

The options schema for the listStreams action for the StreamActor.

See also: [actorSchemas/task/stream/actions](actions.md), [actorSchemas/task/stream/summary](summary.md).

## actorSchemas/task/stream/listStreams

**Source:** `actorSchemas/task/stream/listStreams.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { StreamActorAction } from './actions.js';
import { StreamActorStreamSummarySchema } from './summary.js';

/** The options schema for the listStreams action for the StreamActor */
export const StreamActorListStreamsOptionsSchema = z.object({
  /** Must be listStreams to access this function */
  action: z.literal(StreamActorAction.ListStreams)
    .describe('Must be listStreams to access this function'),
});

export type StreamActorListStreamsOptions = z.infer<typeof StreamActorListStreamsOptionsSchema>;

export const StreamActorListStreamsOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be listStreams to access this function',
      const: StreamActorAction.ListStreams,
    },
  },
  required: ['action'],
};

/** The emitted message schema for the listStreams action for the StreamActor */
export const StreamActorListStreamsResultSchema = z.array(StreamActorStreamSummarySchema);

export type StreamActorListStreamsResult = z.infer<typeof StreamActorListStreamsResultSchema>;
```
