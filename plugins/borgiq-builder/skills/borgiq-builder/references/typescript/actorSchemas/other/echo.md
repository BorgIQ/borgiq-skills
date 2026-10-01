# actorSchemas/other/echo

Generated from the platform's runtime types. Do not edit.

EchoActor options and result: a debugging actor that emits the message, error, inputs, locals and options it received.

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
