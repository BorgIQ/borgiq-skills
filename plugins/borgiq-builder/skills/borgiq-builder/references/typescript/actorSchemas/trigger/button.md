# actorSchemas/trigger/button

Generated from the platform's runtime types. Do not edit.

ButtonTriggerActor options and result: it emits its configured options.

## actorSchemas/trigger/button

**Source:** `actorSchemas/trigger/button.ts`

```typescript
import { z } from 'zod';

export const ButtonTriggerActorOptionsSchema = z.unknown().describe('What the message should be');

export type ButtonTriggerActorOptions = z.infer<typeof ButtonTriggerActorOptionsSchema>;

export const ButtonTriggerActorResultSchema = z.unknown().describe('The options of the button trigger');

export type ButtonTriggerActorResult = z.infer<typeof ButtonTriggerActorResultSchema>;
```
