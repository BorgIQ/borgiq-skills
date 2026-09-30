# formComponents/string/password

Generated from the platform's runtime types. Do not edit.

The schema for a password input.

See also: [formComponents/base](../base.md).

## formComponents/string/password

**Source:** `formComponents/string/password.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a password input */
export const BIQPasswordZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `password` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Password),

  /** the default value for the input */
  default: z.string().optional(),
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
  
  /** if the input should allow unmasking the password (show the password in plain text). Defaults to true */
  allowUnmasking: z.boolean().optional(),
});

export type BIQPasswordSchema = z.infer<typeof BIQPasswordZodSchema>;
```
