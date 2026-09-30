# formComponents/number/percentage

Generated from the platform's runtime types. Do not edit.

The schema for a percentage input.

See also: [formComponents/base](../base.md).

## formComponents/number/percentage

**Source:** `formComponents/number/percentage.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a percentage input */
export const BIQPercentageZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `percentage` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Percentage),

  /** the default value for the input */
  default: z.number().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),
  /** The variant on if the return value should be the decimal or percentage, eg `0.5` or `50` for `50%`. Defaults to `decimal` */
  variant: z.enum(['decimal', 'percentage']).optional(),

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
});

export type BIQPercentageSchema = z.infer<typeof BIQPercentageZodSchema>;
```
