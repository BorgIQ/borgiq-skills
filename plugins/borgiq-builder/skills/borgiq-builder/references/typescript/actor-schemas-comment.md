# Actor Schemas: CommentActor and EchoActor

Zod schemas and TypeScript types for CommentActor (non-functional UI element for adding notes and documentation to workflows) and EchoActor (a debugging actor that emits the message, error, inputs, locals and options it received).

## Table of Contents

- [actorSchemas/other/comment.ts](#actorschemasothercomment)
- [actorSchemas/other/echo.ts](#actorschemasotherecho)

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

## actorSchemas/other/echo

**Source:** `actorSchemas/other/echo.ts`

```typescript
import { z } from 'zod';

export const EchoActorOptionsSchema = z.unknown().describe('Options for the Echo actor to emit in the options field');

export const EchoActorResultSchema = z.object({
  msg: z.record(z.string(), z.any())
    .describe('The received message'),
  err: z.record(z.string(), z.any())
    .describe('The received error'),
  inputs: z.record(z.string(), z.any())
    .describe('The actors inputs'),
  locals: z.record(z.string(), z.any())
    .describe('The actors locals'),
  options: z.unknown()
    .describe('The actors options'),
});

export type EchoActorResult = z.infer<typeof EchoActorResultSchema>;
```
