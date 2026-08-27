# Actor Schemas: StreamActor

Zod schemas and TypeScript types for StreamActor actions: createStream, editMetadata, appendData, readStream, deleteStream, listStreams, getStreamInfo.

## Table of Contents

- [actorSchemas/task/stream/actions.ts](#actorschemastaskstreamactions)
- [actorSchemas/task/stream/appendData.ts](#actorschemastaskstreamappenddata)
- [actorSchemas/task/stream/createStream.ts](#actorschemastaskstreamcreatestream)
- [actorSchemas/task/stream/deleteStream.ts](#actorschemastaskstreamdeletestream)
- [actorSchemas/task/stream/editMetadata.ts](#actorschemastaskstreameditmetadata)
- [actorSchemas/task/stream/getStreamInfo.ts](#actorschemastaskstreamgetstreaminfo)
- [actorSchemas/task/stream/index.ts](#actorschemastaskstreamindex)
- [actorSchemas/task/stream/listStreams.ts](#actorschemastaskstreamliststreams)
- [actorSchemas/task/stream/readStream.ts](#actorschemastaskstreamreadstream)

## actorSchemas/task/stream/actions

**Source:** `actorSchemas/task/stream/actions.ts`

```typescript
import { BIQJsonSchemaType, BIQSelectJsonSchema } from '../../../schemas/index.js';

/** The actions available for the StreamActor */
export enum StreamActorAction {
  CreateStream = 'createStream',
  EditMetadata = 'editMetadata',
  AppendData = 'appendData',
  ReadStream = 'readStream',
  DeleteStream = 'deleteStream',
  ListStreams = 'listStreams',
  GetStreamInfo = 'getStreamInfo',
}

// This identifies which actions have LTM and/or STM enabled
export const StreamActorActionMemory: Partial<Record<StreamActorAction, { ltm?: boolean; stm?: boolean }>> = {};

export const StreamActorActionsJsonSchema: BIQSelectJsonSchema = {
  type: BIQJsonSchemaType.String,
  title: 'Action',
  description: 'The action to perform on the StreamActor',
  enum: Object.values(StreamActorAction),
  ui: {
    component: 'searchSelect',
    options: {
      enumLabels: {
        [StreamActorAction.CreateStream]: 'Create Stream',
        [StreamActorAction.EditMetadata]: 'Edit Metadata',
        [StreamActorAction.AppendData]: 'Append Data',
        [StreamActorAction.ReadStream]: 'Read Stream',
        [StreamActorAction.DeleteStream]: 'Delete Stream',
        [StreamActorAction.ListStreams]: 'List Streams',
        [StreamActorAction.GetStreamInfo]: 'Get Stream Info',
      },
      enumGroups: {
        'Stream Management': [StreamActorAction.CreateStream, StreamActorAction.EditMetadata, StreamActorAction.ListStreams, StreamActorAction.DeleteStream],
        'Records': [StreamActorAction.AppendData, StreamActorAction.ReadStream],
        'Inspection': [StreamActorAction.GetStreamInfo],
      }
    },
  },
};
```

## actorSchemas/task/stream/appendData

**Source:** `actorSchemas/task/stream/appendData.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { StreamActorAction } from './actions.js';

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
  stream: z.string()
    .describe('The slug or id of the stream to append to'),
  records: z.array(z.object({
    kind: z.literal('text').optional()
      .describe('The payload type. Only text is supported in this version'),
    payload: z.string()
      .describe('The record payload'),
  })).min(1).max(500)
    .describe('The records to append, up to 500 per call'),
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
      description: 'The records to append, up to 500 per call',
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
      maxItems: 500,
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

## actorSchemas/task/stream/createStream

**Source:** `actorSchemas/task/stream/createStream.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { StreamActorAction } from './actions.js';

/**
 * The options schema for the createStream action for the StreamActor.
 *
 * `idleTtlSeconds` and `persistent` are mutually exclusive, and supplying neither means the default
 * one-hour idle TTL. Persistence has to be asked for: the expensive failure mode for a resource
 * this cheap to create is abandoned streams accumulating silently.
 */
export const StreamActorCreateStreamOptionsSchema = z.object({
  /** Must be createStream to access this function */
  action: z.literal(StreamActorAction.CreateStream)
    .describe('Must be createStream to access this function'),
  slug: z.string().regex(/^[a-z0-9][a-z0-9_-]{0,63}$/)
    .describe('The unique slug for the stream within the workspace'),
  name: z.string().optional()
    .describe('The display name for the stream. Defaults to the slug'),
  description: z.string().optional()
    .describe('An optional description for the stream'),
  idleTtlSeconds: z.number().int().min(60).max(2592000).optional()
    .describe('Delete the stream once it has gone this long without an append. 60s to 30 days. Mutually exclusive with persistent'),
  persistent: z.literal(true).optional()
    .describe('Keep the stream until it is explicitly deleted. Mutually exclusive with idleTtlSeconds'),
  maxRecordSizeInKiloBytes: z.number().int().min(1).optional()
    .describe('The largest single record payload this stream accepts. Defaults to 256KB'),
}).refine((value) => !(value.persistent && value.idleTtlSeconds !== undefined), {
  message: 'A stream is either persistent or has an idle TTL, not both',
  path: ['persistent'],
});

export type StreamActorCreateStreamOptions = z.infer<typeof StreamActorCreateStreamOptionsSchema>;

export const StreamActorCreateStreamOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be createStream to access this function',
      const: StreamActorAction.CreateStream,
    },
    slug: {
      type: BIQJsonSchemaType.String,
      title: 'Slug',
      description: 'The unique slug for the stream within the workspace',
    },
    name: {
      type: BIQJsonSchemaType.String,
      title: 'Name',
      description: 'The display name for the stream. Defaults to the slug',
    },
    description: {
      type: BIQJsonSchemaType.String,
      title: 'Description',
      description: 'An optional description for the stream',
    },
    idleTtlSeconds: {
      type: BIQJsonSchemaType.Number,
      title: 'Idle TTL (seconds)',
      description: 'Delete the stream once it has gone this long without an append. 60s to 30 days. Leave both this and Persistent unset for the 1 hour default',
    },
    persistent: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Persistent',
      description: 'Keep the stream until it is explicitly deleted. Cannot be combined with an idle TTL',
    },
    maxRecordSizeInKiloBytes: {
      type: BIQJsonSchemaType.Number,
      title: 'Max Record Size (KB)',
      description: 'The largest single record payload this stream accepts. Defaults to 256KB',
    },
  },
  required: ['action', 'slug'],
};

/** The emitted message schema for the createStream action for the StreamActor */
export const StreamActorCreateStreamResultSchema = z.object({
  streamId: z.string().describe('The id of the created stream'),
  slug: z.string().describe('The slug of the created stream'),
  name: z.string().describe('The name of the created stream'),
  persistent: z.boolean().describe('Whether the stream lives until explicitly deleted'),
  idleTtlSeconds: z.number().nullable().describe('The idle TTL, or null when persistent'),
  expiresAt: z.string().nullable().describe('When the stream currently becomes eligible for deletion'),
  createdAt: z.string().describe('The creation timestamp'),
});

export type StreamActorCreateStreamResult = z.infer<typeof StreamActorCreateStreamResultSchema>;
```

## actorSchemas/task/stream/deleteStream

**Source:** `actorSchemas/task/stream/deleteStream.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { StreamActorAction } from './actions.js';

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
  stream: z.string()
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

## actorSchemas/task/stream/editMetadata

**Source:** `actorSchemas/task/stream/editMetadata.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { StreamActorAction } from './actions.js';

/** The options schema for the editMetadata action for the StreamActor */
export const StreamActorEditMetadataOptionsSchema = z.object({
  /** Must be editMetadata to access this function */
  action: z.literal(StreamActorAction.EditMetadata)
    .describe('Must be editMetadata to access this function'),
  stream: z.string()
    .describe('The slug or id of the stream to edit'),
  name: z.string().optional()
    .describe('A new display name for the stream'),
  description: z.string().optional()
    .describe('A new description for the stream'),
  idleTtlSeconds: z.number().int().min(60).max(2592000).optional()
    .describe('A new idle TTL. Mutually exclusive with persistent'),
  persistent: z.literal(true).optional()
    .describe('Convert the stream to persistent. Mutually exclusive with idleTtlSeconds'),
  maxRecordSizeInKiloBytes: z.number().int().min(1).optional()
    .describe('A new per-record payload ceiling for this stream'),
}).refine((value) => !(value.persistent && value.idleTtlSeconds !== undefined), {
  message: 'A stream is either persistent or has an idle TTL, not both',
  path: ['persistent'],
});

export type StreamActorEditMetadataOptions = z.infer<typeof StreamActorEditMetadataOptionsSchema>;

export const StreamActorEditMetadataOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be editMetadata to access this function',
      const: StreamActorAction.EditMetadata,
    },
    stream: {
      type: BIQJsonSchemaType.String,
      title: 'Stream',
      description: 'The slug or id of the stream to edit',
    },
    name: {
      type: BIQJsonSchemaType.String,
      title: 'Name',
      description: 'A new display name for the stream',
    },
    description: {
      type: BIQJsonSchemaType.String,
      title: 'Description',
      description: 'A new description for the stream',
    },
    idleTtlSeconds: {
      type: BIQJsonSchemaType.Number,
      title: 'Idle TTL (seconds)',
      description: 'A new idle TTL, from 60s to 30 days. Cannot be combined with Persistent',
    },
    persistent: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Persistent',
      description: 'Convert the stream to persistent. Cannot be combined with an idle TTL',
    },
    maxRecordSizeInKiloBytes: {
      type: BIQJsonSchemaType.Number,
      title: 'Max Record Size (KB)',
      description: 'A new per-record payload ceiling for this stream',
    },
  },
  required: ['action', 'stream'],
};

/** The emitted message schema for the editMetadata action for the StreamActor */
export const StreamActorEditMetadataResultSchema = z.object({
  streamId: z.string().describe('The id of the stream'),
  slug: z.string().describe('The slug of the stream'),
  name: z.string().describe('The updated name'),
  persistent: z.boolean().describe('Whether the stream lives until explicitly deleted'),
  idleTtlSeconds: z.number().nullable().describe('The idle TTL, or null when persistent'),
  expiresAt: z.string().nullable().describe('When the stream currently becomes eligible for deletion'),
});

export type StreamActorEditMetadataResult = z.infer<typeof StreamActorEditMetadataResultSchema>;
```

## actorSchemas/task/stream/getStreamInfo

**Source:** `actorSchemas/task/stream/getStreamInfo.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { StreamActorAction } from './actions.js';

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
  stream: z.string()
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

## actorSchemas/task/stream/index

**Source:** `actorSchemas/task/stream/index.ts`

```typescript
import { z } from 'zod';

import { StreamActorCreateStreamOptionsSchema, StreamActorCreateStreamResult } from './createStream.js';
import { StreamActorEditMetadataOptionsSchema, StreamActorEditMetadataResult } from './editMetadata.js';
import { StreamActorAppendDataOptionsSchema, StreamActorAppendDataResult } from './appendData.js';
import { StreamActorReadStreamOptionsSchema, StreamActorReadStreamResult } from './readStream.js';
import { StreamActorDeleteStreamOptionsSchema, StreamActorDeleteStreamResult } from './deleteStream.js';
import { StreamActorListStreamsOptionsSchema, StreamActorListStreamsResult } from './listStreams.js';
import { StreamActorGetStreamInfoOptionsSchema, StreamActorGetStreamInfoResult } from './getStreamInfo.js';

export * from './createStream.js';
export * from './editMetadata.js';
export * from './appendData.js';
export * from './readStream.js';
export * from './deleteStream.js';
export * from './listStreams.js';
export * from './getStreamInfo.js';
export * from './actions.js';

/** The options schema for the StreamActor with separated by actions */
export const StreamActorOptionsSchema = z.discriminatedUnion('action', [
  StreamActorCreateStreamOptionsSchema,
  StreamActorEditMetadataOptionsSchema,
  StreamActorAppendDataOptionsSchema,
  StreamActorReadStreamOptionsSchema,
  StreamActorDeleteStreamOptionsSchema,
  StreamActorListStreamsOptionsSchema,
  StreamActorGetStreamInfoOptionsSchema,
]);

export type StreamActorOptions = z.infer<typeof StreamActorOptionsSchema>;

/** The emitted message schema for the StreamActor with separated by actions */
export type StreamActorResult =
  StreamActorCreateStreamResult | StreamActorEditMetadataResult | StreamActorAppendDataResult |
  StreamActorReadStreamResult | StreamActorDeleteStreamResult | StreamActorListStreamsResult |
  StreamActorGetStreamInfoResult;
```

## actorSchemas/task/stream/listStreams

**Source:** `actorSchemas/task/stream/listStreams.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { StreamActorAction } from './actions.js';

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
export const StreamActorListStreamsResultSchema = z.array(z.object({
  streamId: z.string().describe('The stream id'),
  slug: z.string().describe('The stream slug'),
  name: z.string().describe('The stream name'),
  description: z.string().nullable().describe('The stream description'),
  persistent: z.boolean().describe('Whether the stream lives until explicitly deleted'),
  idleTtlSeconds: z.number().nullable().describe('The idle TTL, or null when persistent'),
  storedBytes: z.number().describe('Approximate bytes stored, refreshed periodically'),
  lastActivityAt: z.string().nullable().describe('When the stream was last appended to, as last observed'),
  expiresAt: z.string().nullable().describe('When the stream becomes eligible for deletion'),
  createdAt: z.string().describe('The creation timestamp'),
}));

export type StreamActorListStreamsResult = z.infer<typeof StreamActorListStreamsResultSchema>;
```

## actorSchemas/task/stream/readStream

**Source:** `actorSchemas/task/stream/readStream.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { StreamActorAction } from './actions.js';

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
  stream: z.string()
    .describe('The slug or id of the stream to read'),
  from: z.string().optional()
    .describe('Where to start: "start", "tail", or a cursor from a previous read. Defaults to start'),
  maxRecords: z.number().int().min(1).max(1000).optional()
    .describe('Maximum records to return in this page'),
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
