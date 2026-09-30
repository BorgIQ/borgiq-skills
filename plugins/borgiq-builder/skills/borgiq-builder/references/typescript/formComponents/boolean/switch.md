# formComponents/boolean/switch

Generated from the platform's runtime types. Do not edit.

The schema for a switch input.

See also: [formComponents/base](../base.md).

## formComponents/boolean/switch

**Source:** `formComponents/boolean/switch.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema, BIQColorZodSchema } from '../base.js';

/** The schema for a switch input */
export const BIQSwitchZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `switch` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Switch),

  /** the default value for the form input. */
  default: z.boolean().optional(),
  /** the color of the switch. Defaults to the Theme Color */
  color: BIQColorZodSchema.optional(),

  /** if the label is inline with the switch. Defaults to false */
  inlineLabel: z.boolean().optional(),
  /** the position of the label when inlineLabel is true. Defaults to right */
  labelPosition: z.enum(['left', 'right']).optional(),
});

export type BIQSwitchSchema = z.infer<typeof BIQSwitchZodSchema>;
```
