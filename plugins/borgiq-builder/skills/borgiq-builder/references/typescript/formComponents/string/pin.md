# formComponents/string/pin

Generated from the platform's runtime types. Do not edit.

The schema for a pin input.

See also: [formComponents/base](../base.md).

## formComponents/string/pin

**Source:** `formComponents/string/pin.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a pin input */
export const BIQPinZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `pin` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Pin),

  /** the default value for the input */
  default: z.string().optional(),

  /** the regex pattern to validate the input against. If not set, the input will not be validated */
  regex: z.string().optional(),
  /** error message to display if the input does not match the regex pattern. Defaults to `Invalid input` */
  regexErrorMessage: z.string().optional(),

  /** the allowed characters of the pin input, if regex is used then this will be ignored. If not set and regex is not used, defaults to `alphanumeric` */
  valueType: z.enum(['number', 'alphanumeric']).optional(),
  /** if its a OTP input, this will update the keyboard modes to allow using the last SMS with a code to be used as the pin. Defaults to false */
  isOTP: z.boolean().optional(),
  /** the length of the pin input. Defaults to 4 */
  length: z.number().optional(),

  /** if the pin input should be masked. Defaults to true */
  masked: z.boolean().optional(),
  /** the keyboard mode of input for the pin input. Defaults to to `numeric` if valueType is `number` or `text` if valueType is not set. */
  inputMode: z.enum(['search', 'text', 'none', 'tel', 'url', 'email', 'numeric', 'decimal']).optional(),

  /** if the form should be submitted when the pin input is completed. Defaults to false */
  submitOnComplete: z.boolean().optional(),
});

export type BIQPinSchema = z.infer<typeof BIQPinZodSchema>;
```
