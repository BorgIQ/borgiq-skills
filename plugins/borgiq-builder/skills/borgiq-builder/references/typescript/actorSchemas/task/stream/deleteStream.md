# actorSchemas/task/stream/deleteStream

Generated from the platform's runtime types. Do not edit.

The options schema for the deleteStream action for the StreamActor.

See also: [actorSchemas/task/stream/actions](actions.md), [actorSchemas/task/stream/limits](limits.md).

## actorSchemas/task/stream/deleteStream

**Source:** `actorSchemas/task/stream/deleteStream.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { StreamActorAction } from './actions.js';
import { STREAM_SCHEMA_LIMITS } from './limits.js';

/**
 * The options schema for the deleteStream action for the StreamActor.
 *
 * Deletion is hard: the records are destroyed in the backend and the row is removed. There is no
 * tombstone and no undo, and this action does not confirm — exactly like deleteCollection.
 */
export const StreamActorDeleteStreamOptionsSchema = z.object({
  /** Must be deleteStream to access this function */
  action: z.literal(StreamActorAction.DeleteStream)
    .describe('Must be deleteStream to access this function'),
  stream: z.string().min(1).max(STREAM_SCHEMA_LIMITS.streamRefMaxLength)
    .describe('The slug or id of the stream to delete'),
});

export type StreamActorDeleteStreamOptions = z.infer<typeof StreamActorDeleteStreamOptionsSchema>;

export const StreamActorDeleteStreamOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be deleteStream to access this function',
      const: StreamActorAction.DeleteStream,
    },
    stream: {
      type: BIQJsonSchemaType.String,
      title: 'Stream',
      description: 'The slug or id of the stream to delete. This destroys every record in it',
    },
  },
  required: ['action', 'stream'],
};

/** The emitted message schema for the deleteStream action for the StreamActor */
export const StreamActorDeleteStreamResultSchema = z.object({
  streamId: z.string().describe('The id of the deleted stream'),
  slug: z.string().describe('The slug of the deleted stream'),
});

export type StreamActorDeleteStreamResult = z.infer<typeof StreamActorDeleteStreamResultSchema>;
```
