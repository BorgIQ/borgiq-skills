# actorSchemas/task/messageProcessor/downloadFileAsBase64

Generated from the platform's runtime types. Do not edit.

The options schema for the download file as base64 action in the MessageProcessorActor.

See also: [schemas/file](../../../schemas/file.md), [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/downloadFileAsBase64

**Source:** `actorSchemas/task/messageProcessor/downloadFileAsBase64.ts`

```typescript
import { z } from 'zod';

import { BIQFileSchema, BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the download file as base64 action in the MessageProcessorActor */
export const MessageProcessorActorDownloadFileAsBase64OptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.DownloadFileAsBase64)
    .describe('Must be downloadFileAsBase64 to access this function'),
  file: BIQFileSchema,
});

export type MessageProcessorActorDownloadFileAsBase64Options = z.infer<typeof MessageProcessorActorDownloadFileAsBase64OptionsSchema>;

export const MessageProcessorActorDownloadFileAsBase64OptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.DownloadFileAsBase64,
    },
    file: {
      type: BIQJsonSchemaType.Any,
      title: 'File',
      description: 'The BorgIQ file to download',
    },
  },
  required: ['action', 'file'],
};

/** The emitted message schema for the downloadFileAsBase64 action in the MessageProcessorActor */
export const MessageProcessorActorDownloadFileAsBase64ResultSchema = z.object({
  file: BIQFileSchema,
  base64: z.string().describe('The base64 encoded string of the file'),
});

export type MessageProcessorActorDownloadFileAsBase64Result = z.infer<typeof MessageProcessorActorDownloadFileAsBase64ResultSchema>;
```
