# formComponents/display/urlButton

Generated from the platform's runtime types. Do not edit.

The schema for a url button component to navigate to a url.

See also: [formComponents/base](../base.md).

## formComponents/display/urlButton

**Source:** `formComponents/display/urlButton.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQColorZodSchema, BIQButtonStyleZodSchema, BIQButtonComponentSizeZodSchema, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a url button component to navigate to a url */
export const BIQUrlButtonZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `urlButton` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.UrlButton),

  /** the text to display in the button. Defaults to `Open URL` */
  text: z.string().optional(),
  /** the color of the button. Defaults to the primary color of the theme */
  color: BIQColorZodSchema.optional(),
  /** the variant of the button. Defaults to outlined */
  variant: BIQButtonStyleZodSchema.optional(),
  /** the size of the button. Defaults to medium */
  size: BIQButtonComponentSizeZodSchema.optional(),

  /** the url that the button will open when clicked */
  url: z.string(),
  /** if to open the url in the current tab, defaults to false (open in a new tab) */
  openUrlInCurrentPage: z.boolean().optional(),
});

export type BIQUrlButtonSchema = z.infer<typeof BIQUrlButtonZodSchema>;
```
