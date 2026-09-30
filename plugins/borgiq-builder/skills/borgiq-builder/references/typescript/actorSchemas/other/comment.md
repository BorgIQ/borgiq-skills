# actorSchemas/other/comment

Generated from the platform's runtime types. Do not edit.

The options of the CommentActor, a note on the canvas.

## actorSchemas/other/comment

**Source:** `actorSchemas/other/comment.ts`

```typescript
import { z } from 'zod';

export const CommentActorOptionsSchema = z.object({
  width: z.string().nullish(),
  height: z.string().nullish(),
  bgColor: z.string().nullish(),
  textColor: z.string().nullish(),
});

export type CommentActorOptions = z.infer<typeof CommentActorOptionsSchema>;
```
