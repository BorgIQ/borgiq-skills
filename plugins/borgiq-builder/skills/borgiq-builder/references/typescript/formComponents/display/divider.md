# formComponents/display/divider

Generated from the platform's runtime types. Do not edit.

The schema for a divider component.

See also: [formComponents/base](../base.md).

## formComponents/display/divider

**Source:** `formComponents/display/divider.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQColorZodSchema, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a divider component */
export const BIQDividerZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `divider` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Divider),

  /** the color of the divider. Defaults to a dimmed gray color */
  color: BIQColorZodSchema.optional(),
  /** the weight of the divider. Defaults to 1 */
  weight: z.number().min(0).optional(),
  
  /** the text to display in the divider. If no text is provided, the divider will be displayed as just a line */
  text: z.string().optional(),
  /** the text alignment of the divider. Defaults to `center` and only applies if text is provided */
  textAlignment: z.enum(['left', 'center', 'right']).optional(),
});

export type BIQDividerSchema = z.infer<typeof BIQDividerZodSchema>;
```
