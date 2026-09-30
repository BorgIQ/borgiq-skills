# actorSchemas/trigger/email

Generated from the platform's runtime types. Do not edit.

The message an EmailTriggerActor emits.

See also: [schemas/file](../../schemas/file.md).

## actorSchemas/trigger/email

**Source:** `actorSchemas/trigger/email.ts`

```typescript
import { z } from 'zod';
import { BIQFileSchema } from '../../schemas/index.js';

export const EmailTriggerActorResultSchema = z.object({
  messageId: z.string(),
  from: z.string(),
  to: z.string(),
  cc: z.string().nullish(),
  subject: z.string(),
  date: z.string(),
  hasAttachments: z.boolean(),
  htmlBody: z.string().nullish(),
  textBody: z.string().nullish(),
  attachments: z.array(BIQFileSchema).nullish(),
  headers: z.record(z.string(), z.string()).nullish(),
});

export type EmailTriggerActorResult = z.infer<typeof EmailTriggerActorResultSchema>;
```
