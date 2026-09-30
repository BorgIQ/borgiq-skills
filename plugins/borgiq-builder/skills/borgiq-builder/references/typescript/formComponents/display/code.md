# formComponents/display/code

Generated from the platform's runtime types. Do not edit.

The schema for a code viewer component.

See also: [formComponents/base](../base.md).

## formComponents/display/code

**Source:** `formComponents/display/code.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a code viewer component */
export const BIQCodeViewerZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `codeViewer` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.CodeViewer),

  /** the code string to display in the code block */
  value: z.string(),

  /** the language of the code to apply syntax highlighting. If no language is provided, no syntax highlighting will be applied */
  language: z.string().optional(),

  /** the width of the code block. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** the height of the code block. Defaults to fitting the content height */
  height: z.union([z.number(), z.string()]).optional(),
});

export type BIQCodeViewerSchema = z.infer<typeof BIQCodeViewerZodSchema>;
```
