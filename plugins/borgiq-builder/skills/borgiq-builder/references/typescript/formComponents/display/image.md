# formComponents/display/image

Generated from the platform's runtime types. Do not edit.

The schema for a image component.

See also: [formComponents/base](../base.md).

## formComponents/display/image

**Source:** `formComponents/display/image.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQColorZodSchema, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a image component */
export const BIQImageZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `image` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Image),

  /** the src of the image. This can be the full base64 content of the image or a url to the image */
  src: z.string(),
  /** the width of the image. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** the height of the image. Defaults to 100% */
  height: z.union([z.number(), z.string()]).optional(),

  // ********* The props to add a border to the image. If borderColor and borderWidth are not provided, the image will not have a border *********
  /** the border color of the image. Defaults to black */
  borderColor: BIQColorZodSchema.optional(),
  /** the border width of the image. Defaults to 1px */
  borderWidth: z.union([z.number(), z.string()]).optional(),
  /** the border radius of the image. Defaults to no border radius */
  borderRadius: z.union([z.number(), z.string()]).optional(),
});

export type BIQImageSchema = z.infer<typeof BIQImageZodSchema>;
```
