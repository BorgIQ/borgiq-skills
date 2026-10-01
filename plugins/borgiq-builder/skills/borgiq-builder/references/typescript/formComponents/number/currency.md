# formComponents/number/currency

Generated from the platform's runtime types. Do not edit.

The schema for a currency input.

See also: [formComponents/base](../base.md).

## formComponents/number/currency

**Source:** `formComponents/number/currency.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a currency input */
export const BIQCurrencyZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `currency` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Currency),

  /** the default value for the input */
  default: z.number().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),
  /** The variant on how to render the input. This will only . Defaults to `decimal` */
  variant: z.enum(['decimal', 'integer']).optional(),

  /** the minimum value of the number. If not provided, there is no minimum value */
  minimum: z.number().optional(),
  /** the maximum value of the number. If not provided, there is no maximum value */
  maximum: z.number().optional(),
  /** if the minimum value is exclusive. Defaults to false */
  isExclusiveMinimum: z.boolean().optional(),
  /** if the maximum value is exclusive. Defaults to false */
  isExclusiveMaximum: z.boolean().optional(),

  /** hide controls for the input */
  hideControls: z.boolean().optional(),

  /** the currency to display in the input. Defaults to `$` */
  currencyPrefix: z.string().optional(),
});

export type BIQCurrencySchema = z.infer<typeof BIQCurrencyZodSchema>;
```
