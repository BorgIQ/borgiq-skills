# actorSchemas/task/interface

Generated from the platform's runtime types. Do not edit.

InterfaceActor options and result, and its event port id.

See also: [schemas/interface](../../schemas/interface.md).

## actorSchemas/task/interface

**Source:** `actorSchemas/task/interface.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchemaType, BIQJsonSchema, BIQInterfacePageDataSchema } from '../../schemas/index.js';

/** the interface event source port id */
export const INTERFACE_EVENT_SOURCE_PORT_ID = 'SPRTevent00';

/** The options schema for the InterfaceActor */
export const InterfaceActorOptionsSchema = z.object({
  page: BIQInterfacePageDataSchema
    .describe('The page data to build the components for the interface actor'),
  defaultValues: z.record(z.string(), z.any()).nullish()
    .describe('The default values to inject into the url as query params'),
  autoSubmitAfterSeconds: z.number().int().min(0).nullish()
    .describe('Auto submit the form after it has been opened after a certain number of seconds'),
  timeoutInMinutes: z.number().min(0).nullish()
    .describe('How long to wait for the interface actor to submit the form before timing out. Default to no timeout.'),
  onSubmit: z.discriminatedUnion('type', [
    z.object({
      type: z.literal('nextInterface')
        .describe('when the interface form is successfully submitted, redirect to the next interface rendered in the flow'),
      loadingMessage: z.string().nullish()
        .describe('The message to show while the next interface is loading'),
    }),
    z.object({
      type: z.literal('successMessage'),
      successMessage: z.string().nullish()
        .describe('The message to show when the interface form is successfully submitted'),
    }),
    z.object({
      type: z.literal('urlRedirect'),
      url: z.url()
        .describe('The url to redirect to when the interface form is successfully submitted'),
    })
  ])
    .describe('What page to redirect to when the interface form is submitted'),
  showProgressStatus: z.boolean().nullish()
    .describe('Show real-time flow progress and actor status on the waiting page. Requires onSubmit type to be nextInterface.'),
  emitPage: z.boolean().nullish()
    .describe('Whether to emit the page data on the meta port'),
});

export type InterfaceActorOptions = z.infer<typeof InterfaceActorOptionsSchema>;

export const InterfaceActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    page: {
      type: BIQJsonSchemaType.Any,
      title: 'Page',
      description: 'The page data to render for the interface trigger',
      ui: {
        component: 'modal',
        options: {
          language: 'yaml',
        },
      }
    },
    defaultValues: {
      type: BIQJsonSchemaType.Any,
      title: 'Default values',
      description: 'The default values to inject into the url as query params',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
    autoSubmitAfterSeconds: {
      type: BIQJsonSchemaType.Integer,
      title: 'Auto submit after seconds',
      description: 'Auto submit the form after it has been opened after a certain number of seconds',
    },
    timeoutInMinutes: {
      type: BIQJsonSchemaType.Number,
      title: 'Timeout in minutes',
      description: 'How long to wait for the interface actor to submit the form before timing out. Default to infinite timeout.',
    },
    onSubmit: {
      discriminatorKey: 'type',
      anyOf: [
        {
          type: BIQJsonSchemaType.Object,
          title: 'On submit',
          description: 'The action to perform when the interface form is successfully submitted',
          properties: {
            type: {
              type: BIQJsonSchemaType.String,
              title: 'On submit type',
              description: 'The type of on submit action',
              const: 'nextInterface',
              default: 'Next Interface',
            },
            loadingMessage: {
              type: BIQJsonSchemaType.String,
              title: 'Loading message',
              description: 'The message to show while the next interface is loading',
              ui: {
                options: {
                  placeholder: 'Loading...',
                },
              },
            },
          },
          required: ['type'],
        },
        {
          type: BIQJsonSchemaType.Object,
          title: 'On submit',
          description: 'The action to perform when the interface form is successfully submitted',
          properties: {
            type: {
              type: BIQJsonSchemaType.String,
              title: 'Type',
              description: 'The type of on submit action',
              const: 'successMessage',
              default: 'Success Message',
            },
            successMessage: {
              type: BIQJsonSchemaType.String,
              title: 'Success message',
              description: 'The message to show when the interface form is successfully submitted',
              ui: {
                options: {
                  placeholder: 'Success!',
                },
              },
            },
          },
          required: ['type'],
        },
        {
          type: BIQJsonSchemaType.Object,
          title: 'On submit',
          description: 'The action to perform when the interface form is successfully submitted',
          properties: {
            type: {
              type: BIQJsonSchemaType.String,
              title: 'On submit type',
              description: 'The type of on submit action',
              const: 'urlRedirect',
              default: 'URL Redirect',
            },
            url: {
              type: BIQJsonSchemaType.String,
              title: 'URL',
              description: 'The url to redirect to when the interface form is successfully submitted',
              format: 'uri',
            },
          },
          required: ['type', 'url'],
        },
      ],
    },
    showProgressStatus: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Show progress status',
      description: 'Show real-time flow progress and actor status on the waiting page. Requires onSubmit type to be nextInterface.',
      ui: {
        component: 'switch',
      },
    },
    emitPage: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit page',
      description: 'Whether to emit the page data on the meta port',
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['page', 'onSubmit'],
};

/** the message response schema for the InterfaceActor */
export const InterfaceActorMetadataReceiveResponseSchema = z.object({
  interfaceId: z.string()
    .describe('The interface id to use for the interface session'),
  interfaceUrl: z.string()
    .describe('The url the interface page lives under'),
  page: BIQInterfacePageDataSchema.optional()
    .describe('The page data to render for the interface actor'),
});

export type InterfaceActorMetadataReceiveResponse = z.infer<typeof InterfaceActorMetadataReceiveResponseSchema>;

export const InterfaceActorResultSchema = z.object({
  meta: z.object({
    interfaceId: z.string()
      .describe('The interface id that was used to submit the form'),
    submissionInterfaceId: z.string()
      .describe('The interface id that was used to submit the form and will be used to render the next page'),
    ipAddress: z.string().optional()
      .describe('The IP address of the user who submitted the form'),
  }),
  body: z.record(z.string(), z.any())
    .describe('The body of the interface submission'),
});

export type InterfaceActorResult = z.infer<typeof InterfaceActorResultSchema>;
```
