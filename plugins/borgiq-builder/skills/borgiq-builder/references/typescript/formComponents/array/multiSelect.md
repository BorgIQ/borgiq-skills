# formComponents/array/multiSelect

Generated from the platform's runtime types. Do not edit.

The schema for a multi select input.

See also: [formComponents/base](../base.md).

## formComponents/array/multiSelect

**Source:** `formComponents/array/multiSelect.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQOptionsZodSchema, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a multi select input */
export const BIQMultiSelectZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `multiSelect` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.MultiSelect),

  /** The default value for the form input */
  default: z.array(z.string()).optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),
  /** The options that will define the values and labels for the select options */
  options: BIQOptionsZodSchema,
  /** The min number of options that can be selected */
  minLength: z.number().optional(),
  /** The max number of options that can be selected */
  maxLength: z.number().optional(),

  /** If the input element can allow the user to search for options */
  searchable: z.boolean().optional(),
  /** The message to display when no options are found */
  nothingFoundMessage: z.string().optional(),

  /** The position of the check icon to the left or right of the option label in the dropdown menu in the select element */
  checkIconPosition: z.enum(['left', 'right']).optional(),
});

export type BIQMultiSelectSchema = z.infer<typeof BIQMultiSelectZodSchema>;
```
