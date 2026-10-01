# actorSchemas/task/messageProcessor/renderTemplate

Generated from the platform's runtime types. Do not edit.

The options schema for the renderTemplate action in the MessageProcessorActor.

See also: [actorSchemas/task/messageProcessor/actions](actions.md).

## actorSchemas/task/messageProcessor/renderTemplate

**Source:** `actorSchemas/task/messageProcessor/renderTemplate.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the renderTemplate action in the MessageProcessorActor */
export const MessageProcessorActorRenderTemplateOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.RenderTemplate)
    .describe('Must be renderTemplate to access this function'),
  template: z.string().min(1)
    .describe('The template to render using LiquidJs, it will use the actors inputs for the args'),
});

export type MessageProcessorActorRenderTemplateOptions = z.infer<typeof MessageProcessorActorRenderTemplateOptionsSchema>;

export const MessageProcessorActorRenderTemplateOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.RenderTemplate,
    },
    template: {
      type: BIQJsonSchemaType.String,
      minLength: 1,
      title: 'Template',
      description: 'The template to render using LiquidJs, it will use the actors inputs for the args',
      ui: {
        component: 'code',
        options: {
          editInModal: true,
          minLines: 3,
          maxLines: 10,
          autoResize: true,
          placeholder: 'Hello {{ inputs.name }}',
        }
      }

    },
  },
  required: ['action', 'template'],
};

/** The result schema for the renderTemplate action in the MessageProcessorActor */
export const MessageProcessorActorRenderTemplateResultSchema = z.string().describe('The rendered template');

export type MessageProcessorActorRenderTemplateResult = z.infer<typeof MessageProcessorActorRenderTemplateResultSchema>;
```
