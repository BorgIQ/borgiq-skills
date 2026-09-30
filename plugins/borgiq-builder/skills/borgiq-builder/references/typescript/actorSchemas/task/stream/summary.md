# actorSchemas/task/stream/summary

Generated from the platform's runtime types. Do not edit.

A stream as every management action reports it.

## actorSchemas/task/stream/summary

**Source:** `actorSchemas/task/stream/summary.ts`

```typescript
import { z } from 'zod';

/**
 * A stream as every management action reports it.
 *
 * `createStream`, `editMetadata` and `listStreams` all return exactly this — the service builds one
 * `toSummary(row)` and the API returns it verbatim — so they declare it once rather than three
 * times. They used to declare three different subsets of it, each understating what the actor
 * actually emits: a canvas author reading the schema saw no `maxRecordSizeInKiloBytes` on a create
 * and no `updatedAt` on a list, both of which were in the message all along.
 *
 * This is the wire form of `BIQStreamSummary` in `@borgiq/types`. Cursor-typed fields are plain
 * strings here because the brand is a platform-internal guard and does not survive JSON;
 * `streamResultContracts.test.ts` asserts the two shapes stay equal.
 */
export const StreamActorStreamSummarySchema = z.object({
  streamId: z.string().describe('The stream id'),
  slug: z.string().describe('The stream slug'),
  name: z.string().describe('The stream name'),
  description: z.string().nullable().describe('The stream description'),
  idleTtlSeconds: z.number().nullable().describe('The idle TTL, or null when persistent'),
  persistent: z.boolean().describe('Whether the stream lives until explicitly deleted'),
  maxRecordSizeInKiloBytes: z.number().describe('The largest single record payload this stream accepts'),
  storedBytes: z.number().describe('Approximate bytes stored, refreshed periodically'),
  lastActivityAt: z.string().nullable().describe('When the stream was last appended to, as last observed'),
  expiresAt: z.string().nullable().describe('When the stream becomes eligible for deletion'),
  createdAt: z.string().describe('The creation timestamp'),
  updatedAt: z.string().nullable().describe('When the stream metadata was last edited. Not activity'),
});

export type StreamActorStreamSummary = z.infer<typeof StreamActorStreamSummarySchema>;
```
