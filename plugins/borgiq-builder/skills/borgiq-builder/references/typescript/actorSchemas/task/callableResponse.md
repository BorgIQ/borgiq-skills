# actorSchemas/task/callableResponse

Generated from the platform's runtime types. Do not edit.

The options schema for the CallableResponseActor.

## actorSchemas/task/callableResponse

**Source:** `actorSchemas/task/callableResponse.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

/** The options schema for the CallableResponseActor */
export const CallableResponseActorOptionsSchema = z.object({
  payload: z.any().describe('The payload to emit on the Call flow actor that trigged the flow'),
  throwError: z.boolean().nullish()
    .describe('If the callable response actor should throw an error to the call flow actor'),
});

export type CallableResponseActorOptions = z.infer<typeof CallableResponseActorOptionsSchema>;

export const CallableResponseActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    payload: {
      type: BIQJsonSchemaType.Any,
      title: 'Payload',
      description: 'The payload to emit on the Call flow actor that trigged the flow',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
    throwError: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Throw error',
      description: 'If the callable response actor should throw an error to the call flow actor',
      default: false,
      ui: {
        component: 'switch',
      },
    },
  },
};

/** The response schema for the CallableResponseActor */
export const CallableResponseActorResultSchema = z.any().describe('The payload provided from the options of the CallableResponseActor');

export type CallableResponseActorResult = z.infer<typeof CallableResponseActorResultSchema>;
```
