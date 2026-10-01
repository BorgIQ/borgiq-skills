# formComponents/number/rating

Generated from the platform's runtime types. Do not edit.

The schema for a rating input.

See also: [formComponents/base](../base.md).

## formComponents/number/rating

**Source:** `formComponents/number/rating.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a rating input */
export const BIQRatingZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `rating` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Rating),

  /** the default value for the input */
  default: z.number().optional(),

  /** the maximum value of the rating. Defaults to 5 */
  maximum: z.number().optional(),
  /** how many fractions each star can have. Defaults to 1 */
  fractions: z.number().optional(),
});

export type BIQRatingSchema = z.infer<typeof BIQRatingZodSchema>;
```
