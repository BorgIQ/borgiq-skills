# actorSchemas/task/stream/readStream

Generated from the platform's runtime types. Do not edit.

The options schema for the readStream action for the StreamActor.

See also: [actorSchemas/task/stream/actions](actions.md), [actorSchemas/task/stream/limits](limits.md).

## actorSchemas/task/stream/readStream

**Source:** `actorSchemas/task/stream/readStream.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { StreamActorAction } from './actions.js';
import { STREAM_SCHEMA_LIMITS } from './limits.js';

/**
 * The options schema for the readStream action for the StreamActor.
 *
 * This emits ONE BOUNDED PAGE, never a whole stream. The page is budgeted against the workspace's
 * message-size limit, so a 10,000-record stream does not become a 10,000-record flowrun message.
 * The cursor is the handle: loop `nextCursor` back into this actor on a canvas edge for chunked
 * processing, or park it in a DataStore to resume across flowruns.
 */
export const StreamActorReadStreamOptionsSchema = z.object({
  /** Must be readStream to access this function */
  action: z.literal(StreamActorAction.ReadStream)
    .describe('Must be readStream to access this function'),
  stream: z.string().min(1).max(STREAM_SCHEMA_LIMITS.streamRefMaxLength)
    .describe('The slug or id of the stream to read'),
  from: z.string().optional()
    .describe('Where to start: "start", "tail", or a cursor from a previous read. Defaults to start'),
  maxRecords: z.number().int().min(1).max(STREAM_SCHEMA_LIMITS.readPageRecords).optional()
    .describe('Maximum records to return in this page'),
  maxBytes: z.number().int().min(1).max(STREAM_SCHEMA_LIMITS.readPageBytes).optional()
    .describe('Maximum bytes to return in this page, up to the 1 MiB page ceiling'),
});

export type StreamActorReadStreamOptions = z.infer<typeof StreamActorReadStreamOptionsSchema>;

export const StreamActorReadStreamOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be readStream to access this function',
      const: StreamActorAction.ReadStream,
    },
    stream: {
      type: BIQJsonSchemaType.String,
      title: 'Stream',
      description: 'The slug or id of the stream to read',
    },
    from: {
      type: BIQJsonSchemaType.String,
      title: 'From',
      description: 'Where to start: "start", "tail", or a cursor from a previous read. Defaults to start',
    },
    maxRecords: {
      type: BIQJsonSchemaType.Number,
      title: 'Max Records',
      description: 'Maximum records to return in this page',
    },
    maxBytes: {
      type: BIQJsonSchemaType.Number,
      title: 'Max Bytes',
      description: 'Maximum bytes to return in this page, up to the 1 MiB page ceiling',
    },
  },
  required: ['action', 'stream'],
};

/** The emitted message schema for the readStream action for the StreamActor */
export const StreamActorReadStreamResultSchema = z.object({
  streamId: z.string().describe('The id of the stream read'),
  records: z.array(z.object({
    cursor: z.string().describe('This record\'s cursor'),
    timestamp: z.string().describe('When the record arrived, ISO 8601'),
    payload: z.string().describe('The record payload'),
  })).describe('The records in this page'),
  count: z.number().describe('How many records this page carries'),
  hasMore: z.boolean().describe('Whether more records remain after this page'),
  cursor: z.string().describe('Where this page started'),
  nextCursor: z.string().describe('Where to resume. Usable even when the page is empty'),
  tailCursor: z.string().describe('The current end of the stream'),
  skippedRecords: z.number().describe('Records skipped because this version could not interpret them'),
  truncatedByByteBudget: z.boolean().optional().describe('Set when the page stopped short because the message budget ran out'),
});

export type StreamActorReadStreamResult = z.infer<typeof StreamActorReadStreamResultSchema>;
```
