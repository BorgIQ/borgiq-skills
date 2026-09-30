# formComponents/string/phoneNumber

Generated from the platform's runtime types. Do not edit.

The schema for a phone number input.

See also: [formComponents/base](../base.md).

## formComponents/string/phoneNumber

**Source:** `formComponents/string/phoneNumber.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a phone number input */
export const BIQPhoneNumberZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `phoneNumber` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.PhoneNumber),

  /** the default value for the input */
  default: z.string().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /**
   * Format and validation
   * E.164: The full international phone number eg `+1234567890`
   * national: The phone number without the country code eg `(234) 567-890`
   * international: The phone number without the national prefix eg `+1 234 567 890`
   * defaults to `E.164`
   **/
  format: z.enum(['E.164', 'national', 'international']).optional(),

  /** The default country in ISO 3166 two-letter region code only valid for E.164 or international format, eg `US` for USA. Defaults to the user's locale. */
  defaultCountry: z.string().optional(),
  /**
   * If true, the country code will be fixed and not allow the user to update it. This is only valid for E.164 or international format.
   * This requires a defaultCountry to be set.
   * Defaults to true.
   **/
  fixedCountryCode: z.boolean().optional(),
});

export type BIQPhoneNumberSchema = z.infer<typeof BIQPhoneNumberZodSchema>;
```
