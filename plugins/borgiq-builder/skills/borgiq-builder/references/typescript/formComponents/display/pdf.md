# formComponents/display/pdf

Generated from the platform's runtime types. Do not edit.

The schema for a pdf viewer component.

See also: [formComponents/base](../base.md).

## formComponents/display/pdf

**Source:** `formComponents/display/pdf.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a pdf viewer component */
export const BIQPdfViewerZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `pdfViewer` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.PdfViewer),

  /** the src of the pdf. This can be the full base64 content of the pdf or a url to the pdf */
  src: z.string().refine((val) => {
    try {
      new URL(val);
      return true;
    } catch {
      return false;
    }
  }, {
    message: 'Invalid src URL',
  }),
  /** the width of the pdf. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** the height of the pdf. Defaults to 500px */
  height: z.union([z.number(), z.string()]).optional(),
});

export type BIQPdfViewerSchema = z.infer<typeof BIQPdfViewerZodSchema>;
```
