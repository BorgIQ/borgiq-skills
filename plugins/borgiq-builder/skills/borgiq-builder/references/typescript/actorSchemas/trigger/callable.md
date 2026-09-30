# actorSchemas/trigger/callable

Generated from the platform's runtime types. Do not edit.

The emitted message schema for the CallableTriggerActor.

## actorSchemas/trigger/callable

**Source:** `actorSchemas/trigger/callable.ts`

```typescript
import { z } from 'zod';

/** The emitted message schema for the CallableTriggerActor */
export const CallableTriggerActorResultSchema = z.any();

export type CallableTriggerActorResult = z.infer<typeof CallableTriggerActorResultSchema>;
```
