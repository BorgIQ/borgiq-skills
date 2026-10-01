# actorSchemas/task/stream/index

Generated from the platform's runtime types. Do not edit.

StreamActor options, a discriminated union on `action`, and its result types.

See also: [actorSchemas/task/stream/createStream](createStream.md), [actorSchemas/task/stream/editMetadata](editMetadata.md), [actorSchemas/task/stream/appendData](appendData.md), [actorSchemas/task/stream/readStream](readStream.md), [actorSchemas/task/stream/deleteStream](deleteStream.md), [actorSchemas/task/stream/listStreams](listStreams.md), [actorSchemas/task/stream/getStreamInfo](getStreamInfo.md), [actorSchemas/task/stream/actions](actions.md), [actorSchemas/task/stream/limits](limits.md), [actorSchemas/task/stream/summary](summary.md).

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
export * from './limits.js';
export * from './summary.js';

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
