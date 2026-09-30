# actorSchemas/task/stream/editMetadata

Generated from the platform's runtime types. Do not edit.

The options schema for the editMetadata action for the StreamActor.

See also: [actorSchemas/task/stream/actions](actions.md), [actorSchemas/task/stream/limits](limits.md), [actorSchemas/task/stream/summary](summary.md).

## actorSchemas/task/stream/editMetadata

**Source:** `actorSchemas/task/stream/editMetadata.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { StreamActorAction } from './actions.js';
import { STREAM_SCHEMA_LIMITS } from './limits.js';
import { StreamActorStreamSummarySchema } from './summary.js';

/**
 * The options schema for the editMetadata action for the StreamActor.
 *
 * Bounds come from `STREAM_SCHEMA_LIMITS`, shared with the API request schemas, so this schema and
 * the platform's cannot disagree about what a valid edit is. The numeric options accept a string
 * too, because options are validated before interpolation — see `createStream.ts` for why.
 */
export const StreamActorEditMetadataOptionsSchema = z.object({
  /** Must be editMetadata to access this function */
  action: z.literal(StreamActorAction.EditMetadata)
    .describe('Must be editMetadata to access this function'),
  stream: z.string().min(1).max(STREAM_SCHEMA_LIMITS.streamRefMaxLength)
    .describe('The slug or id of the stream to edit'),
  name: z.string().min(1).max(STREAM_SCHEMA_LIMITS.nameMaxLength).optional()
    .describe('A new display name for the stream'),
  description: z.string().max(STREAM_SCHEMA_LIMITS.descriptionMaxLength).nullable().optional()
    .describe('A new description for the stream. Null clears it; leaving it out keeps the current one'),
  idleTtlSeconds: z.number().int().min(STREAM_SCHEMA_LIMITS.minIdleTtlSeconds).max(STREAM_SCHEMA_LIMITS.maxIdleTtlSeconds).optional()
    .describe('A new idle TTL. Mutually exclusive with persistent'),
  persistent: z.boolean().optional()
    .describe('Convert the stream to persistent. Mutually exclusive with idleTtlSeconds. False converts a persistent stream back, applying idleTtlSeconds if given and the default TTL otherwise'),
  maxRecordSizeInKiloBytes: z.number().int().min(1).max(STREAM_SCHEMA_LIMITS.maxRecordSizeKiloBytes).optional()
    .describe('A new per-record payload ceiling for this stream. Lowering it affects future appends only; records already stored are unaffected'),
}).refine((value) => !(value.persistent === true && value.idleTtlSeconds !== undefined), {
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
      description: 'A new description for the stream. Null clears it; leaving it out keeps the current one',
    },
    idleTtlSeconds: {
      type: BIQJsonSchemaType.Number,
      title: 'Idle TTL (seconds)',
      description: 'A new idle TTL, from 60s to 30 days. Cannot be combined with Persistent',
    },
    persistent: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Persistent',
      description: 'Convert the stream to persistent. Cannot be combined with an idle TTL. Switching it off applies the idle TTL, or the 1 hour default when none is set',
    },
    maxRecordSizeInKiloBytes: {
      type: BIQJsonSchemaType.Number,
      title: 'Max Record Size (KB)',
      description: 'A new per-record payload ceiling for this stream. Lowering it affects future appends only; records already stored are unaffected',
    },
  },
  required: ['action', 'stream'],
};

/**
 * The emitted message schema for the editMetadata action for the StreamActor.
 *
 * The same summary a create returns — an edit re-reports the whole stream, not just what changed.
 */
export const StreamActorEditMetadataResultSchema = StreamActorStreamSummarySchema;

export type StreamActorEditMetadataResult = z.infer<typeof StreamActorEditMetadataResultSchema>;
```
