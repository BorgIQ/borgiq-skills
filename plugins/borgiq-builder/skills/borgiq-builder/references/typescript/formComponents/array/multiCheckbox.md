# formComponents/array/multiCheckbox

Generated from the platform's runtime types. Do not edit.

The schema for a multi checkbox input.

See also: [formComponents/base](../base.md).

## formComponents/array/multiCheckbox

**Source:** `formComponents/array/multiCheckbox.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQOptionsZodSchema, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a multi checkbox input */
export const BIQMultiCheckboxZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `multiCheckbox` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.MultiCheckbox),

  /** The default value for the form input */
  default: z.array(z.string()).optional(),
  /** The options that will define the values and labels for the checkboxes */
  options: BIQOptionsZodSchema,
  /** The min number of checkboxes that can be selected */
  minLength: z.number().optional(),
  /** The max number of checkboxes that can be selected */
  maxLength: z.number().optional(),

  // ********** The Props to edit the select all option, this is a checkbox at the top of the checkboxes to allow the user to select all the checkboxes at once *********
  /** If to render the select all option to allow the user to select all the checkboxes */
  selectAllOption: z.boolean().optional(),
  /** The label for the select all option */
  selectAllOptionLabel: z.string().optional(),

  /** The orientation of the group of checkboxes. Defaults to horizontal */
  orientation: z.enum(['vertical', 'horizontal']).optional(),
});

export type BIQMultiCheckboxSchema = z.infer<typeof BIQMultiCheckboxZodSchema>;
```
