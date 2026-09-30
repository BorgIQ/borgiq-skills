# formComponents/number/number

Generated from the platform's runtime types. Do not edit.

The schema for a number input.

See also: [formComponents/base](../base.md).

## formComponents/number/number

**Source:** `formComponents/number/number.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a number input */
export const BIQNumberZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `number` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Number),

  /** the default value for the input */
  default: z.number().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),
  /** The variant on if the input can have decimals or must be an integer. Defaults to `decimal` */
  variant: z.enum(['decimal', 'integer']).optional(),

  /** the minimum value of the number */
  minimum: z.number().optional(),
  /** the maximum value of the number */
  maximum: z.number().optional(),
  /** if the minimum value is exclusive */
  isExclusiveMinimum: z.boolean().optional(),
  /** if the maximum value is exclusive */
  isExclusiveMaximum: z.boolean().optional(),

  /** hide controls for the input */
  hideControls: z.boolean().optional(),
});

export type BIQNumberSchema = z.infer<typeof BIQNumberZodSchema>;
```
