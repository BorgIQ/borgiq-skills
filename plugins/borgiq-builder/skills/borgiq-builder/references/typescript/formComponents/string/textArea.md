# formComponents/string/textArea

Generated from the platform's runtime types. Do not edit.

The schema for a text area input.

See also: [formComponents/base](../base.md).

## formComponents/string/textArea

**Source:** `formComponents/string/textArea.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a text area input */
export const BIQTextAreaZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `textArea` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.TextArea),

  /** the default value for the input */
  default: z.string().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** the regex pattern to validate the input against. If not set, the input will not be validated */
  regex: z.string().optional(),
  /** the regex error message to display if the input does not match the regex pattern. Defaults to `Invalid input` */
  regexErrorMessage: z.string().optional(),
  /** the minimum length of the input. Defaults to 0 for optional inputs and 1 for required inputs */
  minLength: z.number().optional(),
  /** the maximum length of the input. If not set, the input does not have a maximum length */
  maxLength: z.number().optional(),

  /** the minimum lines of the textarea. If not set, the textarea does not have a minimum height */
  minLines: z.number().optional(),
  /** the maximum lines of the textarea. If not set, the textarea does not have a maximum height */
  maxLines: z.number().optional(),
  /** the set height of the input component. If not set, the input will auto-resize to fit the content */
  height: z.union([z.number(), z.string()]).optional(),
  /** the width of the input component. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** if the input component should auto-resize to fit content. Defaults to true */
  autoResize: z.boolean().optional(),
  
  /** if the input should render a copy button on the top right corner. Defaults to false */
  copyable: z.boolean().optional(),
});

export type BIQTextAreaSchema = z.infer<typeof BIQTextAreaZodSchema>;
```
