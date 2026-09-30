# formComponents/display/fileDownload

Generated from the platform's runtime types. Do not edit.

The schema for a file download component.

See also: [schemas/file](../../schemas/file.md), [formComponents/base](../base.md).

## formComponents/display/fileDownload

**Source:** `formComponents/display/fileDownload.ts`

```typescript
import { z } from 'zod';

import { BIQFileSchema } from '../../schemas/file.js';
import { BIQFormComponentType, BIQColorZodSchema, BIQButtonStyleZodSchema, BIQButtonComponentSizeZodSchema, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a file download component */
export const BIQFileDownloadZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `fileDownload` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.FileDownload),

  /** the file to download. This can be a BIQFile, a file object, or a url to a file */
  file: z.union([
    // the BIQFile will use the metadata to fetch the file from the server and download it
    BIQFileSchema,
    // the file object will be downloaded directly building the file object in the browser
    z.object({
      name: z.string(),
      mimeType: z.string(),
      base64content: z.string(),
    }),
    // the url will be downloaded directly by opening the url in a new tab
    z.string(),
  ]),

  /** the button text. Defaults to `Download` */
  buttonText: z.string().optional(),
  /** the button color. Defaults to the primary color of the theme */
  buttonColor: BIQColorZodSchema.optional(),
  /** the button variant. Defaults to outlined */
  buttonVariant: BIQButtonStyleZodSchema.optional(),
  /** the button size. Defaults to medium */
  buttonSize: BIQButtonComponentSizeZodSchema.optional(),
});

export type BIQFileDownloadSchema = z.infer<typeof BIQFileDownloadZodSchema>;
```
