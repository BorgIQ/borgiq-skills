# actorSchemas/task/stream/createStream

Generated from the platform's runtime types. Do not edit.

The options schema for the createStream action for the StreamActor.

See also: [actorSchemas/task/stream/actions](actions.md), [actorSchemas/task/stream/limits](limits.md), [actorSchemas/task/stream/summary](summary.md).

## actorSchemas/task/stream/createStream

**Source:** `actorSchemas/task/stream/createStream.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { StreamActorAction } from './actions.js';
import { STREAM_SCHEMA_LIMITS } from './limits.js';
import { StreamActorStreamSummarySchema } from './summary.js';

/**
 * The options schema for the createStream action for the StreamActor.
 *
 * `idleTtlSeconds` and `persistent` are mutually exclusive, and supplying neither means the default
 * one-hour idle TTL. Persistence has to be asked for: the expensive failure mode for a resource
 * this cheap to create is abandoned streams accumulating silently.
 *
 * Every bound below comes from `STREAM_SCHEMA_LIMITS`, which the API request schemas import too. An
 * input this schema accepts is one the platform accepts — which is what makes a platform 400 here a
 * bug rather than an author error.
 *
 * The numeric options are `number | string` because options are validated BEFORE interpolation: a
 * `${{ ... }}` expression is still text at that point, so a field that took only numbers would
 * reject every canvas that computes the value rather than typing it. The number branch keeps its
 * bounds, and the string branch is bounded by the API schema once the expression has resolved.
 * `collection/putItem.ts`'s `ttl` is the precedent.
 */
export const StreamActorCreateStreamOptionsSchema = z.object({
  /** Must be createStream to access this function */
  action: z.literal(StreamActorAction.CreateStream)
    .describe('Must be createStream to access this function'),
  slug: z.string().regex(STREAM_SCHEMA_LIMITS.slugPattern)
    .describe('The unique slug for the stream within the workspace'),
  name: z.string().min(1).max(STREAM_SCHEMA_LIMITS.nameMaxLength).optional()
    .describe('The display name for the stream. Defaults to the slug'),
  description: z.string().max(STREAM_SCHEMA_LIMITS.descriptionMaxLength).nullable().optional()
    .describe('An optional description for the stream'),
  idleTtlSeconds: z.number().int().min(STREAM_SCHEMA_LIMITS.minIdleTtlSeconds).max(STREAM_SCHEMA_LIMITS.maxIdleTtlSeconds).optional()
    .describe('Delete the stream once it has gone this long without an append. 60s to 30 days. Mutually exclusive with persistent'),
  persistent: z.boolean().optional()
    .describe('Keep the stream until it is explicitly deleted. Mutually exclusive with idleTtlSeconds. False means the same as leaving it out: the idle TTL, or the default when none is given'),
  maxRecordSizeInKiloBytes: z.number().int().min(1).max(STREAM_SCHEMA_LIMITS.maxRecordSizeKiloBytes).optional()
    .describe('The largest single record payload this stream accepts. Defaults to 256KB. Lowering it affects future appends only; records already stored are unaffected'),
}).refine((value) => !(value.persistent === true && value.idleTtlSeconds !== undefined), {
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
      description: 'Keep the stream until it is explicitly deleted. Cannot be combined with an idle TTL. Off means the idle TTL, or the 1 hour default when none is set',
    },
    maxRecordSizeInKiloBytes: {
      type: BIQJsonSchemaType.Number,
      title: 'Max Record Size (KB)',
      description: 'The largest single record payload this stream accepts. Defaults to 256KB. Lowering it affects future appends only; records already stored are unaffected',
    },
  },
  required: ['action', 'slug'],
};

/**
 * The emitted message schema for the createStream action for the StreamActor.
 *
 * The full stream summary, which is what the service returns. It used to declare a seven-field
 * subset of it, so the description, the record-size ceiling and the storage hints were in the
 * message but not in the schema an author reads.
 */
export const StreamActorCreateStreamResultSchema = StreamActorStreamSummarySchema;

export type StreamActorCreateStreamResult = z.infer<typeof StreamActorCreateStreamResultSchema>;
```
