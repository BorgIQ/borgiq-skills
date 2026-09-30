# formComponents/string/codeDiff

Generated from the platform's runtime types. Do not edit.

The schema for a code diff (compare two code blocks) input.

See also: [formComponents/base](../base.md).

## formComponents/string/codeDiff

**Source:** `formComponents/string/codeDiff.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a code diff (compare two code blocks) input */
export const BIQCodeDiffZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `codeDiff` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.CodeDiff),

  /** The code block of the old value of the diff (this code will not be editable in the component) */
  oldValue: z.string(),
  /** The code block of the new value of the diff and the default value of the form component. This code will be editable in the component and can be reverted to the old value */
  default: z.string(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** the language of the code input to apply code highlighting. If not set, no code highlighting will be applied */
  language: z.string().optional(),

  /** the title to display above the old code block */
  oldCodeTitle: z.string().optional(),
  /** the title to display above the new code block */
  newCodeTitle: z.string().optional(),
  
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
  /** the set height of the input for input. If not set, the input will auto-resize to fit the content */
  height: z.union([z.number(), z.string()]).optional(),
  /** the width of the input. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** if the input should auto-resize to fit content. Defaults to true */
  autoResize: z.boolean().optional(),

  /** If the old code and new code should be rendered inline (in the same code area) or side by side. Defaults to false (side by side) */
  inline: z.boolean().optional(),
  /** whether to render the revert controls (only would render if readOnly is undefined or false) to revert the updated section of the new code back to the old code. Defaults to true */
  revertControls: z.boolean().optional(),
});

export type BIQCodeDiffSchema = z.infer<typeof BIQCodeDiffZodSchema>;
```
