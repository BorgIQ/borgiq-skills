# actorSchemas/task/aiRouter

Generated from the platform's runtime types. Do not edit.

AiRouterActor options, built from the actor's source ports, and its result.

See also: [schemas/runtime](../../schemas/runtime.md), [canvas](../../canvas.md), [ai/index](../../ai/index.md), [ai/modelRef](../../ai/modelRef.md).

## actorSchemas/task/aiRouter

**Source:** `actorSchemas/task/aiRouter.ts`

```typescript
import { ZodObject, z } from 'zod';

import { RuntimeActorSourcePort } from '../../schemas/runtime.js';
import { DEFAULT_SOURCE_PORT_ID } from '../../canvas.js';
import { BIQJsonSchemaType } from '../../schemas/index.js';
import { BIQJsonSchema } from '../../schemas/index.js';
import { AiModel, AiModelRef, AiModelRefSchema, BIQAiMessageSchema, buildAiModelSuggestionUiOptions } from '../../ai/index.js';
import { AiDefaultParameters } from '../../ai/index.js';

export enum AiRouterActorEmitType {
  SingleRoute = 'singleRoute',
  MultiRoute = 'multiRoute',
}

/** The options schema builder for the AiRouterActor since it changes for the sourcePorts configuration for the actor */
export const buildAiRouterActorOptionsSchema = (sourcePorts: RuntimeActorSourcePort[]): ZodObject<any> => z.object({ // eslint-disable-line @typescript-eslint/no-explicit-any
  model: AiModelRefSchema.nullish()
    .describe('The model to use: a known model id, "<provider>/<model-id>" for a built-in provider\'s unlisted model, or "<custom-provider-slug>/<model-id>" for a model served by one of the workspace\'s custom providers (e.g. "fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct"). Defaults to gpt-6-luna if not provided'),
  emitType: z.enum(AiRouterActorEmitType).nullish()
    .describe('How the AI router actor will function, either can be singleRoute or multiRoute where singleRoute emits only on one of the conditions being true and multiRoute emits on all of the conditions being true'),
  input: z.any().describe('The input to the AI router actor'),
  routeDescriptions: z.record(z.string(), z.string()).superRefine((value, ctx) => {
    const invalidRoutes: string[] = [];

    for (const routeName of Object.keys(value)) {
      const port = sourcePorts.find((port) => port.name === routeName);
      // if the port is not found, add it to the invalidRoutes list
      if (!port) {
        invalidRoutes.push(routeName);
      // if the route is the default port, add an issue
      } else if (port.id === DEFAULT_SOURCE_PORT_ID) {
        ctx.addIssue({
          code: 'invalid_value',
          path: [routeName],
          values: [routeName],
          message: `Route name '${routeName}' is reserved for the default route`,
        });
      }
    }
    // if there are no invalid ports, return the value
    if (invalidRoutes.length === 0) return;
    // if there are invalid ports, add an issue for all invalid routes
    ctx.addIssue({
      code: 'unrecognized_keys',
      keys: invalidRoutes,
      message: `Unrecognized Route name(s) in route definitions: ${invalidRoutes.join(', ')}`,
    });
  })
    .describe('The text definitions for the routes on if the input follows the route definition, the keys for the conditions are the route name provided in the routes section, the value is the text definition for the route'),
  emitInput: z.boolean().nullish()
    .describe('Whether to emit the input to the AI router actor'),
});

export type AiRouterActorOptions = {
  input: unknown,
  model?: AiModelRef,
  emitType?: AiRouterActorEmitType,
  routeDescriptions: { [portName: string]: string },
  emitInput?: boolean,
};

const modelSuggestionUi = buildAiModelSuggestionUiOptions(Object.values(AiModel));

/** this is a partial schema, since the emitType and routeDescriptions will be handled by the sourcePorts configuration */
export const AiRouterActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    model: {
      type: BIQJsonSchemaType.String,
      description: 'The model to use: a known model id, "<provider>/<model-id>" for a built-in provider\'s unlisted model, or "<custom-provider-slug>/<model-id>" for a model served by one of the workspace\'s custom providers (e.g. "fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct"). Defaults to gpt-6-luna if not provided',
      title: 'Model',
      default: AiDefaultParameters.model,
      ui: {
        component: 'suggestion',
        order: 0,
        options: {
          placeholder: 'Select or type a model',
          ...modelSuggestionUi,
        },
      },
    },
    input: {
      type: BIQJsonSchemaType.Any,
      description: 'The input to the AI router actor that would be passed to the AI model',
      title: 'Input',
    },
    emitInput: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Whether to emit the input to the AI router actor',
      title: 'Emit input',
      default: false,
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['input'],
};

/** The result schema for the AiRouterActor */
export const AiRouterResultSchema = z.object({
  route: z.string()
    .describe('The port name that the message was emitted from'),
  meta: z.object({
    input: z.array(z.union([BIQAiMessageSchema, z.object({
      role: z.literal('system'),
      content: z.string(),
    })])).nullish()
      .describe('The input messages to the AI router actor'),
    model: z.string()
      .describe('The model used to generate the response to determine the route'),
    usage: z.object({
      promptTokens: z.number().int()
        .describe('The number of tokens in the prompt'),
      completionTokens: z.number().int()
        .describe('The number of tokens in the completion'),
      totalTokens: z.number().int()
        .describe('The total number of tokens used'),
    }),
    fromCache: z.boolean()
      .describe('Whether the response, to determine the route, was fetched from the cache'),
  }),
});

export type AiRouterResult = z.infer<typeof AiRouterResultSchema>;
```
