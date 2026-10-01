# formComponents/number/slider

Generated from the platform's runtime types. Do not edit.

The schema for a slider input.

See also: [formComponents/base](../base.md).

## formComponents/number/slider

**Source:** `formComponents/number/slider.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a slider input */
export const BIQSliderZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `slider` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Slider),

  /** the default value for the input */
  default: z.number().optional(),

  /** the minimum value of the slider */
  minimum: z.number().optional(),
  /** the maximum value of the slider */
  maximum: z.number().optional(),
  /** the marks of the slider. If not set, the slider will not have marks */
  marks: z.array(z.object({
    value: z.number(),
    label: z.string().optional(),
  })).optional(),

  /** the step value of the slider. Defaults to 1 */
  step: z.number().optional(),
  /** if the slider should be restricted to the marks. Defaults to false */
  restrictToMarks: z.boolean().optional(),
});

export type BIQSliderSchema = z.infer<typeof BIQSliderZodSchema>;
```
