# formComponents/display/header

Generated from the platform's runtime types. Do not edit.

The schema for a header component.

See also: [formComponents/base](../base.md).

## formComponents/display/header

**Source:** `formComponents/display/header.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQColorZodSchema, BIQBaseComponentZodSchema, BIQTextSizeZodSchema } from '../base.js';

/** The schema for a header component */
export const BIQHeaderZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `header` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Header),

  /** the text to display in the main header */
  value: z.string(),
  /** the order of the header (it needs to be literals to match mantine's order type), can a number from 1 to 6. Defaults to 1 */
  order: z.union([
    z.literal(1),
    z.literal(2),
    z.literal(3),
    z.literal(4),
    z.literal(5),
    z.literal(6),
  ]).optional(),
  /** the color of the header. Defaults to the default text color based on the theme (black for light theme and white for dark theme) */
  color: BIQColorZodSchema.optional(),

  /** the subtitle text to display under the header. If no subtitle is provided, the header will not have a subtitle */
  subtitle: z.string().optional(),
  /** the color of the subtitle. Defaults to dimmed color */
  subtitleColor: BIQColorZodSchema.optional(),
  /** the size of the subtitle as a mantine size or a css string. Defaults to xs */
  subtitleSize: BIQTextSizeZodSchema.optional(),
});

export type BIQHeaderSchema = z.infer<typeof BIQHeaderZodSchema>;
```
