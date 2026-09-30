# formComponents/display/markdown

Generated from the platform's runtime types. Do not edit.

The schema for a markdown component.

See also: [formComponents/base](../base.md).

## formComponents/display/markdown

**Source:** `formComponents/display/markdown.ts`

```typescript
import { z } from 'zod';
import { BIQColorZodSchema, BIQFormComponentType, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a markdown component */
export const BIQMarkdownZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `markdown` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Markdown),

  /** the markdown content to display */
  value: z.string(),
 
  /** the width of the markdown area. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** the height of the markdown area. Defaults to 100% */
  height: z.union([z.number(), z.string()]).optional(),

  /** the background color of the markdown area. Defaults to transparent */
  backgroundColor: BIQColorZodSchema.optional(),
});

export type BIQMarkdownSchema = z.infer<typeof BIQMarkdownZodSchema>;
```
