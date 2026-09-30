# formComponents/string/buttonGroup

Generated from the platform's runtime types. Do not edit.

The schema for a button group input and its options.

See also: [formComponents/base](../base.md).

## formComponents/string/buttonGroup

**Source:** `formComponents/string/buttonGroup.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema, BIQColorZodSchema, BIQButtonStyleZodSchema } from '../base.js';

/**
 * The format of the options for the button group
 *
 * 1. It can be an array of strings defining the values of the buttons
 * 2. It can be an array of objects to format the buttons
 *
 **/
const BIQButtonOptionZodSchema = z.string();
const BIQButtonOptionsObjectZodSchema = z.object({
  /** The the label to render on the button. If not set, the value will be used as the label */
  label: z.string().optional(),
  /** The value of the button. This is what will be submitted when the button is clicked */
  value: z.string(),
  /** The variant of the button. Defaults to `outline` */
  variant: BIQButtonStyleZodSchema.optional(),
  /** The color of the button. Defaults to the theme color */
  color: BIQColorZodSchema.optional(),
  /** The src of the icon to render on the button. If not set, no icon will be rendered */
  icon: z.string().optional(),
  /** If the option's button should be disabled. Defaults to false */
  disabled: z.boolean().optional(),
});
const BIQBaseButtonOptionsZodSchema = z.union([BIQButtonOptionZodSchema, BIQButtonOptionsObjectZodSchema]);

export type BIQButtonOptionSchema = z.infer<typeof BIQBaseButtonOptionsZodSchema>;

/** Allow for buttons to be grouped together */
const BIQGroupedButtonOptionsZodSchema = z.object({
  /** The label of the group */
  group: z.string(),
  /** The buttons to render in the group */
  items: BIQBaseButtonOptionsZodSchema.array(),
});

const BIQButtonOptionsSchema = z.union([BIQBaseButtonOptionsZodSchema, BIQGroupedButtonOptionsZodSchema]).array();

export const BIQButtonGroupZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `buttonGroup` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.ButtonGroup),

  /** the default value for the input */
  default: z.string().optional(),

  /** the options for the button group to render the set of buttons */
  options: BIQButtonOptionsSchema,

  /** the orientation of the button group. Defaults to `horizontal` */
  orientation: z.enum(['horizontal', 'vertical']).optional(),
});

export type BIQButtonGroupSchema = z.infer<typeof BIQButtonGroupZodSchema>;
```
