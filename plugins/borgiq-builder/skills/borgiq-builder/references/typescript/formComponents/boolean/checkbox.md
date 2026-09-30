# formComponents/boolean/checkbox

Generated from the platform's runtime types. Do not edit.

The schema for a checkbox input.

See also: [formComponents/base](../base.md).

## formComponents/boolean/checkbox

**Source:** `formComponents/boolean/checkbox.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema, BIQColorZodSchema } from '../base.js';

/** The schema for a checkbox input */
export const BIQCheckboxZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `checkbox` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Checkbox),

  /** the default value for the form input */
  default: z.boolean().optional(),
  /** the variant of the checkbox. Defaults to filled */
  variant: z.enum(['filled', 'outlined']).optional(),
  /** the color of the checkbox. Defaults to the Theme Color */
  color: BIQColorZodSchema.optional(),

  /** if the label is inline with the checkbox. Defaults to false */
  inlineLabel: z.boolean().optional(),
  /** the position of the label when inlineLabel is true. Defaults to right */
  labelPosition: z.enum(['left', 'right']).optional(),
});

export type BIQCheckboxSchema = z.infer<typeof BIQCheckboxZodSchema>;
```
