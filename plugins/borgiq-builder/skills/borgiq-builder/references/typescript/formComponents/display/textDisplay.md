# formComponents/display/textDisplay

Generated from the platform's runtime types. Do not edit.

The schema for a text display component that shows text with optional copy functionality.

See also: [formComponents/base](../base.md).

## formComponents/display/textDisplay

**Source:** `formComponents/display/textDisplay.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseComponentZodSchema, BIQColorZodSchema, BIQTextSizeZodSchema } from '../base.js';

/** The schema for a text display component that shows text with optional copy functionality */
export const BIQTextDisplayZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `textDisplay` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.TextDisplay),

  /** The text value to display */
  value: z.string(),

  /** The color of the text. Defaults to the default text color based on the theme */
  color: BIQColorZodSchema.optional(),

  /** The size of the text. Defaults to 'sm' */
  size: BIQTextSizeZodSchema.optional(),

  /** The font weight of the text (e.g., 'normal', 'bold', or a number like 500) */
  weight: z.union([z.string(), z.number()]).optional(),

  /** If true, the text will be displayed in italic style */
  italic: z.boolean().optional(),

  /** If true, the text will be underlined */
  underline: z.boolean().optional(),

  /** If true, the text will have a strikethrough */
  strikethrough: z.boolean().optional(),

  /** Text transform style: uppercase, lowercase, capitalize, or none */
  transform: z.enum(['uppercase', 'lowercase', 'capitalize', 'none']).optional(),

  /** If true, the text will be displayed in a monospace font */
  monospace: z.boolean().optional(),

  /** If true, shows a copy button to copy the text to clipboard */
  copyable: z.boolean().optional(),
});

export type BIQTextDisplaySchema = z.infer<typeof BIQTextDisplayZodSchema>;
```
