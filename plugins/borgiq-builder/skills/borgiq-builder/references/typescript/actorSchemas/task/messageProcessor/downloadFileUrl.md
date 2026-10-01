# actorSchemas/task/messageProcessor/downloadFileUrl

Generated from the platform's runtime types. Do not edit.

The options schema for the download file url action in the MessageProcessorActor.

See also: [schemas/file](../../../schemas/file.md), [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/downloadFileUrl

**Source:** `actorSchemas/task/messageProcessor/downloadFileUrl.ts`

```typescript
import { z } from 'zod';

import { BIQFileSchema, BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the download file url action in the MessageProcessorActor */
export const MessageProcessorActorDownloadFileUrlOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.DownloadFileUrl)
    .describe('Must be downloadFileUrl to access this function'),
  file: BIQFileSchema,
  expiresInMinutes: z.number().min(1).nullish().describe('The number of minutes download URL will be valid for'),
  downloadAsAttachment: z.boolean().nullish().describe('Whether to download the file as an attachment or inline. Defaults to false.'),
});

export type MessageProcessorActorDownloadFileUrlOptions = z.infer<typeof MessageProcessorActorDownloadFileUrlOptionsSchema>;

export const MessageProcessorActorDownloadFileUrlOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.DownloadFileUrl,
    },
    file: {
      type: BIQJsonSchemaType.Any,
      title: 'File',
      description: 'The BorgIQ file to download',
    },
    expiresInMinutes: {
      type: BIQJsonSchemaType.Number,
      title: 'Expires URL after minutes',
      description: 'The number of minutes download URL will be valid for. Defaults to 1 minute.',
      default: 1,
    },
    downloadAsAttachment: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Download as attachment',
      description: 'Whether the file should be downloaded as an attachment to the user\'s computer or opened in the browser. Defaults to false, open the file in the browser.',
      default: false,
    },
  },
  required: ['action', 'file'],
};

/** The emitted message schema for the downloadFileAsBase64 action in the MessageProcessorActor */
export const MessageProcessorActorDownloadFileUrlResultSchema = z.object({
  file: BIQFileSchema,
  url: z.string().describe('The download URL of the file'),
});

export type MessageProcessorActorDownloadFileUrlResult = z.infer<typeof MessageProcessorActorDownloadFileUrlResultSchema>;
```
