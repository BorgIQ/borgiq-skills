# actorSchemas/task/stream/getStreamInfo

Generated from the platform's runtime types. Do not edit.

The options schema for the getStreamInfo action for the StreamActor.

See also: [actorSchemas/task/stream/actions](actions.md), [actorSchemas/task/stream/limits](limits.md).

## actorSchemas/task/stream/getStreamInfo

**Source:** `actorSchemas/task/stream/getStreamInfo.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { StreamActorAction } from './actions.js';
import { STREAM_SCHEMA_LIMITS } from './limits.js';

/**
 * The options schema for the getStreamInfo action for the StreamActor.
 *
 * The cheap "is there anything new?" probe. It reads the tail LIVE from the backend rather than
 * from a denormalized column, which is what makes the polling pattern viable: a ScheduledTrigger
 * compares this tail cursor against one persisted in a DataStore, and only reads records when it
 * has moved. That is the v1 substitute for a stream-arrival trigger.
 */
export const StreamActorGetStreamInfoOptionsSchema = z.object({
  /** Must be getStreamInfo to access this function */
  action: z.literal(StreamActorAction.GetStreamInfo)
    .describe('Must be getStreamInfo to access this function'),
  stream: z.string().min(1).max(STREAM_SCHEMA_LIMITS.streamRefMaxLength)
    .describe('The slug or id of the stream to describe'),
});

export type StreamActorGetStreamInfoOptions = z.infer<typeof StreamActorGetStreamInfoOptionsSchema>;

export const StreamActorGetStreamInfoOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be getStreamInfo to access this function',
      const: StreamActorAction.GetStreamInfo,
    },
    stream: {
      type: BIQJsonSchemaType.String,
      title: 'Stream',
      description: 'The slug or id of the stream to describe',
    },
  },
  required: ['action', 'stream'],
};

/** The emitted message schema for the getStreamInfo action for the StreamActor */
export const StreamActorGetStreamInfoResultSchema = z.object({
  streamId: z.string().describe('The stream id'),
  slug: z.string().describe('The stream slug'),
  name: z.string().describe('The stream name'),
  description: z.string().nullable().describe('The stream description'),
  tailCursor: z.string().describe('The current end of the stream, read live from the backend'),
  lastRecordAt: z.string().nullable().describe('When the last record arrived, or null if the stream is empty'),
  storedBytes: z.number().describe('Approximate bytes stored'),
  persistent: z.boolean().describe('Whether the stream lives until explicitly deleted'),
  idleTtlSeconds: z.number().nullable().describe('The idle TTL, or null when persistent'),
  expiresAt: z.string().nullable().describe('When the stream becomes eligible for deletion'),
  createdAt: z.string().describe('The creation timestamp'),
});

export type StreamActorGetStreamInfoResult = z.infer<typeof StreamActorGetStreamInfoResultSchema>;
```
