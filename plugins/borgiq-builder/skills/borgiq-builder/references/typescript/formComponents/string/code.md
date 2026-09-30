# formComponents/string/code

Generated from the platform's runtime types. Do not edit.

The schema for a code input.

See also: [formComponents/base](../base.md).

## formComponents/string/code

**Source:** `formComponents/string/code.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a code input */
export const BIQCodeZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `code` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Code),

  /** The default value for the input */
  default: z.string().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** the language of the code input to apply code highlighting. If not set, no code highlighting will be applied */
  language: z.string().optional(),
  

  /** the regex pattern to validate the input against. If not set, the input will not be validated */
  regex: z.string().optional(),
  /** error message to display if the input does not match the regex pattern. Defaults to `Invalid input` */
  regexErrorMessage: z.string().optional(),
  /** the minimum length of the input. Defaults to 0 for optional inputs and 1 for required inputs */
  minLength: z.number().optional(),
  /** the maximum length of the string input. If not set, the input does not have a maximum length */
  maxLength: z.number().optional(),

  /** If wrap the lines of the code in the input component. If false, the code input will scroll horizontally. Defaults to true */
  wrapLines: z.boolean().optional(),
  /** the minimum number of lines the input component will render. If not set, the input does not have a minimum height */
  minLines: z.number().optional(),
  /** the maximum number of lines the input component will render. If not set, the input does not have a maximum height */
  maxLines: z.number().optional(),
  /** the set height of the input component. If not set, the input will auto-resize to fit the content */
  height: z.union([z.number(), z.string()]).optional(),
  /** if the input should auto-resize to fit content. Defaults to true */
  autoResize: z.boolean().optional(),
  
  /** if the input should render a copy button on the top right corner. Defaults to false */
  copyable: z.boolean().optional(),
});

export type BIQCodeSchema = z.infer<typeof BIQCodeZodSchema>;
```
