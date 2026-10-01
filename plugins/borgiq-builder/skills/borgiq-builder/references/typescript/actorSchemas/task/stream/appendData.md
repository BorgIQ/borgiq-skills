# actorSchemas/task/stream/appendData

Generated from the platform's runtime types. Do not edit.

The options schema for the appendData action for the StreamActor.

See also: [actorSchemas/task/stream/actions](actions.md), [actorSchemas/task/stream/limits](limits.md).

## actorSchemas/task/stream/appendData

**Source:** `actorSchemas/task/stream/appendData.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { StreamActorAction } from './actions.js';
import { STREAM_SCHEMA_LIMITS } from './limits.js';

/**
 * The options schema for the appendData action for the StreamActor.
 *
 * An append either stores every record or fails. It never reports success for a record that was
 * not durably written, which is why there is no partial-success shape in the result.
 */
export const StreamActorAppendDataOptionsSchema = z.object({
  /** Must be appendData to access this function */
  action: z.literal(StreamActorAction.AppendData)
    .describe('Must be appendData to access this function'),
  stream: z.string().min(1).max(STREAM_SCHEMA_LIMITS.streamRefMaxLength)
    .describe('The slug or id of the stream to append to'),
  records: z.array(z.object({
    kind: z.literal('text').optional()
      .describe('The payload type. Only text is supported in this version'),
    payload: z.string()
      .describe('The record payload'),
  })).min(1).max(STREAM_SCHEMA_LIMITS.appendBatchRecords)
    .describe(`The records to append, up to ${STREAM_SCHEMA_LIMITS.appendBatchRecords} per call`),
});

export type StreamActorAppendDataOptions = z.infer<typeof StreamActorAppendDataOptionsSchema>;

export const StreamActorAppendDataOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be appendData to access this function',
      const: StreamActorAction.AppendData,
    },
    stream: {
      type: BIQJsonSchemaType.String,
      title: 'Stream',
      description: 'The slug or id of the stream to append to',
    },
    records: {
      type: BIQJsonSchemaType.Array,
      title: 'Records',
      description: `The records to append, up to ${STREAM_SCHEMA_LIMITS.appendBatchRecords} per call`,
      items: {
        type: BIQJsonSchemaType.Object,
        title: 'Record',
        properties: {
          payload: {
            type: BIQJsonSchemaType.String,
            title: 'Payload',
            description: 'The record payload',
          },
        },
        required: ['payload'],
      },
      maxItems: STREAM_SCHEMA_LIMITS.appendBatchRecords,
    },
  },
  required: ['action', 'stream', 'records'],
};

/** The emitted message schema for the appendData action for the StreamActor */
export const StreamActorAppendDataResultSchema = z.object({
  streamId: z.string().describe('The id of the stream appended to'),
  recordsAccepted: z.number().describe('How many records were durably stored'),
  firstCursor: z.string().describe('The cursor of the first record in this append'),
  lastCursor: z.string().describe('The cursor of the last record in this append'),
  tailCursor: z.string().describe('The stream tail after this append'),
});

export type StreamActorAppendDataResult = z.infer<typeof StreamActorAppendDataResultSchema>;
```
