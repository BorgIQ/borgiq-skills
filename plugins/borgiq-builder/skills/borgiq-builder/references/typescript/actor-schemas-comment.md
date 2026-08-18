# Actor Schemas: CommentActor

Zod schemas and TypeScript types for CommentActor (non-functional UI element for adding notes and documentation to workflows).

## Table of Contents

- [actorSchemas/other/comment.ts](#actorschemasothercomment)

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
