# actorSchemas/task/messageProcessor/regexExtract

Generated from the platform's runtime types. Do not edit.

The options and result schemas for the regexExtract action in the MessageProcessorActor.

See also: [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/regexExtract

**Source:** `actorSchemas/task/messageProcessor/regexExtract.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The output schema of the regexExtract action in the MessageProcessorActor */
export const MessageProcessorActorRegexExtractOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.RegexExtract)
    .describe('Must be regexExtract to access this function'),
  rules: z.array(
    z.object({
      regex: z.string().refine((value) => {
        // make sure the regex is valid
        try {
          new RegExp(value);
          return true;
        } catch (_e) { // eslint-disable-line @typescript-eslint/no-unused-vars
          return false;
        }
      }, 'Invalid regex expression')
        .describe('The regex to run the value to extract, must be valid regex'),
      regexOptions: z.string().nullish()
        .describe('The optional flag for search options'),
      extractFrom: z.any()
        .describe('the value to run the regex against'),
      extractTo: z.string()
        .describe('The key to store the extracted value in the emitted message'),
    }),
  )
    .describe('The rules to extract data from the message'),
});

export type MessageProcessorActorRegexExtractOptions = z.infer<typeof MessageProcessorActorRegexExtractOptionsSchema>;

export const MessageProcessorActorRegexExtractOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.RegexExtract,
    },
    rules: {
      type: BIQJsonSchemaType.Array,
      title: 'Rules',
      description: 'The rules to extract data from the message',
      items: {
        type: BIQJsonSchemaType.Object,
        properties: {
          regex: {
            type: BIQJsonSchemaType.String,
            title: 'Regex',
            description: 'The regex to run the value to extract, must be valid regex',
            ui: {
              options: {
                placeholder: '/[A-Z]+/',
              },
            },
          },
          regexOptions: {
            type: BIQJsonSchemaType.String,
            title: 'Regex options',
            description: 'The optional flag for search options',
            ui: {
              options: {
                placeholder: 'g',
              },
            },
          },
          extractFrom: {
            type: BIQJsonSchemaType.Any,
            title: 'Extract from',
            description: 'the value to run the regex against',
          },
          extractTo: {
            type: BIQJsonSchemaType.String,
            title: 'Extract to',
            description: 'The key to store the extracted value in the emitted message',
          },
        },
        required: ['regex', 'extractFrom', 'extractTo'],
      },
    },
  },
  required: ['action', 'rules'],
};

/** The message schema for the regexExtract action in the MessageProcessorActor */
/** is the keys of the message is the `extractTo` keys provided by the rules */
export const MessageProcessorActorRegexExtractResultSchema = z.record(z.string(),
  z.array(z.string())
    .describe('The array of strings extracted when running the rule'),
);

export type MessageProcessorActorRegexExtractResult = z.infer<typeof MessageProcessorActorRegexExtractResultSchema>;
```
