# formComponents/string/markdown

Generated from the platform's runtime types. Do not edit.

The schema for a markdown input.

See also: [formComponents/base](../base.md).

## formComponents/string/markdown

**Source:** `formComponents/string/markdown.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a markdown input */
export const BIQMarkdownInputZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `markdownInput` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.MarkdownInput),

  /** The default value of the markdown input */
  default: z.string(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** the regex pattern to validate the input against. If not set, the input will not be validated */
  regex: z.string().optional(),
  /** error message to display if the input does not match the regex pattern. Defaults to `Invalid input` */
  regexErrorMessage: z.string().optional(),
  /** the minimum length of the input. Defaults to 0 for optional inputs and 1 for required inputs */
  minLength: z.number().optional(),
  /** the maximum length of the string input. If not set, the input does not have a maximum length */
  maxLength: z.number().optional(),

  /** If the lines of the markdown should be wrapped in the input component. If false, the markdown input will scroll horizontally. Defaults to true */
  wrapLines: z.boolean().optional(),
  /** the minimum number of lines the input component will render. If not set, the input does not have a minimum height */
  minLines: z.number().optional(),
  /** the maximum number of lines the input component will render. If not set, the input does not have a maximum height */
  maxLines: z.number().optional(),
  /** the set height of the input for input. If not set, the input will auto-resize to fit the content */
  height: z.union([z.number(), z.string()]).optional(),
  /** the width of the input. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** if the input should auto-resize to fit content. Defaults to true */
  autoResize: z.boolean().optional(),

  /** whether to show a preview of the markdown side by side with the raw markdown input. Defaults to true */
  preview: z.boolean().optional(),
  
  /** if the input should render a copy button on the top right corner. Defaults to false */
  copyable: z.boolean().optional(),
});

export type BIQMarkdownInputSchema = z.infer<typeof BIQMarkdownInputZodSchema>;
```
