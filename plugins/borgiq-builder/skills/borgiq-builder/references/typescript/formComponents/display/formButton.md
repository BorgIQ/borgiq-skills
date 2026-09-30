# formComponents/display/formButton

Generated from the platform's runtime types. Do not edit.

The schema for a form button component.

See also: [formComponents/base](../base.md).

## formComponents/display/formButton

**Source:** `formComponents/display/formButton.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQColorZodSchema, BIQButtonStyleZodSchema, BIQButtonComponentSizeZodSchema, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a form button component */
export const BIQFormButtonZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `formButton` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.FormButton),

  /** the text to display in the button. Defaults to `Submit` for a submit button and `Reset` for a reset button */
  text: z.string().optional(),
  /** the color of the button. Defaults to the primary color of the theme */
  color: BIQColorZodSchema.optional(),
  /** the variant of the button. Defaults to filled */
  variant: BIQButtonStyleZodSchema.optional(),
  /** the size of the button. Defaults to medium */
  size: BIQButtonComponentSizeZodSchema.optional(),

  /** the action type of the button to take on the form, submit submits the form, reset resets the form to default values. Defaults to submit */
  actionType: z.enum(['submit', 'reset']).optional(),
});

export type BIQFormButtonSchema = z.infer<typeof BIQFormButtonZodSchema>;
```
