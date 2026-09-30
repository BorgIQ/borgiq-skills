# actorSchemas/task/callFlow

Generated from the platform's runtime types. Do not edit.

The options schema for the CallFlowActor.

See also: [canvas](../../canvas.md).

## actorSchemas/task/callFlow

**Source:** `actorSchemas/task/callFlow.ts`

```typescript
import { z } from 'zod';

import { BIQActorType } from '../../canvas.js';
import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

/** The options schema for the CallFlowActor */
export const CallFlowActorOptionsSchema = z.object({
  workspaceSlug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'need a valid borgIQ workspace slug')
    .min(5, 'must be 5 or more characters long').max(10, 'must be 10 or fewer characters long').nullish()
    .describe('The workspace the Callable Trigger Actor is in, defaults to the current workspace'),
  canvasSlug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'need a valid borgIQ canvas slug')
    .min(2, 'must be 2 or more characters long').max(255, 'must be 255 or fewer characters long').nullish()
    .describe('The canvas the Callable Trigger Actor is in, defaults to the current canvas'),
  callableTriggerActorId: z.string().regex(new RegExp('ACTR[0123456789abcdefghjkmnpqrstvwxyz]{26}$'), 'need a valid borgIQ callable trigger actor id')
    .describe('The actor id of the Callable Trigger Actor that wants to be triggered'),
  waitForResponse: z.boolean().nullish()
    .describe('If this actor should wait for a response from the Callable Response Actor from the called flow or emit a message immediately'),
  timeoutInSeconds: z.number().positive().nullish()
    .describe('The timeout in seconds for the sub-flow to return a response, defaults to no timeout'),
  payload: z.any()
    .describe('The payload to send to the Callable Trigger Actor, the parameters of the callable trigger flow'),
});

export type CallFlowActorOptions = z.infer<typeof CallFlowActorOptionsSchema>;

export const CallFlowActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    workspaceSlug: {
      type: BIQJsonSchemaType.String,
      title: 'Workspace slug',
      description: 'The workspace the Callable Trigger Actor is in, defaults to the current workspace',
    },
    canvasSlug: {
      type: BIQJsonSchemaType.String,
      title: 'Canvas slug',
      description: 'The canvas the Callable Trigger Actor is in, defaults to the current canvas',
    },
    callableTriggerActorId: {
      type: BIQJsonSchemaType.String,
      title: 'Callable trigger',
      description: 'The Callable Trigger Actor this flow calls.',
      pattern: 'ACTR[0123456789abcdefghjkmnpqrstvwxyz]{26}$',
      // the picker also writes workspaceSlug / canvasSlug above; blank coordinates mean the current
      // workspace and canvas, which is what create-call-flow-flowrun-data resolves to
      ui: {
        component: 'actorSelect',
        options: {
          actorTypes: [BIQActorType.CallableTriggerActor],
          workspaceKey: 'workspaceSlug',
          canvasKey: 'canvasSlug',
          entityLabel: 'callable trigger',
        },
      },
    },
    payload: {
      type: BIQJsonSchemaType.Any,
      title: 'Payload',
      description: 'The payload to send to the Callable Trigger Actor, the parameters of the callable trigger flow',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
    waitForResponse: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Wait for response',
      description: 'If this actor should wait for a response from the Callable Response Actor from the called flow or emit a message immediately',
      default: false,
      ui: {
        component: 'switch',
      },
    },
    timeoutInSeconds: {
      type: BIQJsonSchemaType.Number,
      title: 'Timeout in seconds',
      description: 'The timeout in seconds for the sub-flow to return a response, defaults to no timeout',
      default: 900, // 15 minutes
    },
  },
  required: ['callableTriggerActorId'],
};

export const CallFlowActorReceiveResultSchema = z.any();

export type CallFlowActorResult = z.infer<typeof CallFlowActorReceiveResultSchema>;
```
