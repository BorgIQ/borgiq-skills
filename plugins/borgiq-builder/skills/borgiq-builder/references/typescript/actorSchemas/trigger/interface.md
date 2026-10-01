# actorSchemas/trigger/interface

Generated from the platform's runtime types. Do not edit.

InterfaceTriggerActor options and result.

See also: [schemas/interface](../../schemas/interface.md).

## actorSchemas/trigger/interface

**Source:** `actorSchemas/trigger/interface.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchemaType, BIQJsonSchema, BIQInterfacePageDataSchema } from '../../schemas/index.js';

/** The options schema for the WebhookTriggerActor */
export const InterfaceTriggerActorOptionsSchema = z.object({
  /** The page to render for the interface trigger */
  page: BIQInterfacePageDataSchema
    .describe('The page data to render for the interface trigger'),
  /** The default values to inject into the url as query params */
  defaultValues: z.record(z.string(), z.any()).nullish()
    .describe('The default values to pass to the interface trigger form to build the form'),
  /** auto submit the form after it has been opened after a certain number of seconds */
  autoSubmitAfterSeconds: z.number().int().min(0).nullish()
    .describe('auto submit the form after it has been opened after a certain number of seconds'),
  /** What page to redirect to when the interface trigger form is submitted */
  onSubmit: z.discriminatedUnion('type', [
    z.object({
      /** when the interface trigger form is successfully submitted, redirect to the next interface rendered in the flow  */
      type: z.literal('nextInterface')
        .describe('when the interface trigger form is successfully submitted, redirect to the next interface rendered in the flow'),
      /** The message to show while the next interface is loading */
      loadingMessage: z.string().nullish()
        .describe('The message to show while the next interface is loading'),
    }),
    z.object({
      /** when the interface trigger form is successfully submitted, show a success message */
      type: z.literal('successMessage')
        .describe('when the interface trigger form is successfully submitted, show a success message'),
      /** The message to show when the interface trigger form is successfully submitted */
      successMessage: z.string().nullish()
        .describe('The message to show when the interface trigger form is successfully submitted'),
    }),
    z.object({
      /** when the interface trigger form is successfully submitted, redirect to a url */
      type: z.literal('urlRedirect')
        .describe('when the interface trigger form is successfully submitted, redirect to a url'),
      /** The url to redirect to when the interface trigger form is successfully submitted */
      url: z.url()
        .describe('The url to redirect to when the interface trigger form is successfully submitted'),
    })
  ]),
  /** Whether to show real-time flow progress and actor status on the waiting page. Requires onSubmit type to be nextInterface. */
  showProgressStatus: z.boolean().nullish()
    .describe('Show real-time flow progress and actor status on the waiting page. Requires onSubmit type to be nextInterface.'),
});

export type InterfaceTriggerActorOptions = z.infer<typeof InterfaceTriggerActorOptionsSchema>;

export const InterfaceTriggerActorOptionsJsonSchema: BIQJsonSchema = {
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
    autoSubmitAfterSeconds: {
      type: BIQJsonSchemaType.Integer,
      title: 'Auto submit after seconds',
      description: 'auto submit the form after it has been opened after a certain number of seconds'
    },
    onSubmit: {
      discriminatorKey: 'type',
      anyOf: [
        {
          title: 'On submit',
          description: 'What to do when the interface form is submitted',
          type: BIQJsonSchemaType.Object,
          properties: {
            type: {
              type: BIQJsonSchemaType.String,
              title: 'Type',
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
          properties: {
            type: {
              type: BIQJsonSchemaType.String,
              title: 'Type',
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
  },
  required: ['page', 'onSubmit']
};

export const InterfaceTriggerActorResultSchema = z.object({
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

export type InterfaceTriggerActorResult = z.infer<typeof InterfaceTriggerActorResultSchema>;
```
