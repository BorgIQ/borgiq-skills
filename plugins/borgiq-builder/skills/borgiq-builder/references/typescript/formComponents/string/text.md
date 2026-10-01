# formComponents/string/text

Generated from the platform's runtime types. Do not edit.

The schema for a text input.

See also: [formComponents/base](../base.md).

## formComponents/string/text

**Source:** `formComponents/string/text.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a text input */
export const BIQTextZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `text` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Text),

  /** the default value for the input */
  default: z.string().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),
  /** to specify a variant of the input that will add an icon to the input and complete validation. This will override the regex validation. When not specified, a generic input is rendered */
  variant: z.enum(['email', 'uri']).optional(),


  /** the regex pattern to validate the input against. If not set, the input will not be validated */
  regex: z.string().optional(),
  /** the regex error message to display if the input does not match the regex pattern. Defaults to `Invalid input` */
  regexErrorMessage: z.string().optional(),
  /** the minimum length of the input. Defaults to 0 for optional inputs and 1 for required inputs */
  minLength: z.number().optional(),
  /** the maximum length of the input. If not set, the input does not have a maximum length */
  maxLength: z.number().optional(),

  /** if the input should render a copy button on the top right corner. Defaults to false */
  copyable: z.boolean().optional(),
});

export type BIQTextSchema = z.infer<typeof BIQTextZodSchema>;
```
