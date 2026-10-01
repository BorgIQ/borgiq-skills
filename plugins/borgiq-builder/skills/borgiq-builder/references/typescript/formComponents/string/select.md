# formComponents/string/select

Generated from the platform's runtime types. Do not edit.

The schema for a select input.

See also: [formComponents/base](../base.md).

## formComponents/string/select

**Source:** `formComponents/string/select.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQOptionsZodSchema, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a select input */
export const BIQSelectZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `select` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Select),

  /** the default value for the input */
  default: z.string().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),
  /** the options to render the dropdown options with */
  options: BIQOptionsZodSchema,

  /** if the input is searchable. Defaults to false */
  searchable: z.boolean().optional(),
  /** the message to display when no options are found. Defaults to `No options found` */
  nothingFoundMessage: z.string().optional(),
});

export type BIQSelectSchema = z.infer<typeof BIQSelectZodSchema>;
```
