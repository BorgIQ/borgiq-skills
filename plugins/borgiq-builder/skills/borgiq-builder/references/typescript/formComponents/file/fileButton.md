# formComponents/file/fileButton

Generated from the platform's runtime types. Do not edit.

The schema for a file button input.

See also: [formComponents/base](../base.md).

## formComponents/file/fileButton

**Source:** `formComponents/file/fileButton.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema, BIQColorZodSchema, BIQButtonStyleZodSchema } from '../base.js';

/** The schema for a file button input */
export const BIQFileButtonZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `fileButton` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.FileButton),

  // the accept file types formatted as a comma separated list of mime types. Defaults to `*/*` which means any file type is acceptable.
  // see https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept
  accept: z.string().optional(),

  /** the button text. Defaults to `Upload file` */
  buttonText: z.string().optional(),
  /** the button color. Defaults to the primary color of the theme */
  buttonColor: BIQColorZodSchema.optional(),
  /** the button variant. Defaults to `outline` */
  buttonVariant: BIQButtonStyleZodSchema.optional(),

  // ********** Multiple Files Properties *********
  /** if the input can accept multiple files */
  multiple: z.boolean().optional(),
  /** only if `multiple` is true, the max number of files that can be uploaded */
  maxLength: z.number().optional(),
  /** only if `multiple` is true, the min number of files that can be uploaded */
  minLength: z.number().optional(),

  /** the max file size in bytes. If no max file size is set, the file size will not be checked */
  maxFileSize: z.number().optional(),

  /** show the uploaded file */
  showUploadedFile: z.boolean().optional(),
});

export type BIQFileButtonSchema = z.infer<typeof BIQFileButtonZodSchema>;
```
