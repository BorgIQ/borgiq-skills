# formComponents/string/radio

Generated from the platform's runtime types. Do not edit.

The schema for a radio input.

See also: [formComponents/base](../base.md).

## formComponents/string/radio

**Source:** `formComponents/string/radio.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQOptionsZodSchema, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a radio input */
export const BIQRadioZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `radio` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Radio),

  /** the default value for the input */
  default: z.string().optional(),
  /** the options to render the radio buttons with */
  options: BIQOptionsZodSchema,

  /** the orientation of the radio input. Defaults to `horizontal` */
  orientation: z.enum(['horizontal', 'vertical']).optional(),
});

export type BIQRadioSchema = z.infer<typeof BIQRadioZodSchema>;
```
