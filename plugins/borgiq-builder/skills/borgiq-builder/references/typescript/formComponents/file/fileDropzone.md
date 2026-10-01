# formComponents/file/fileDropzone

Generated from the platform's runtime types. Do not edit.

The schema for a file dropzone input.

See also: [formComponents/base](../base.md).

## formComponents/file/fileDropzone

**Source:** `formComponents/file/fileDropzone.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema, BIQColorZodSchema } from '../base.js';

/** The schema for a file dropzone input */
export const BIQFileDropzoneZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `fileButton` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.FileDropzone),

  // the accept file types formatted as a comma separated list of mime types. Defaults to `*/*` which means any file type is acceptable.
  // see https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept
  accept: z.string().optional(),

  /** The text to display in the dropzone. Defaults to `Drag files here or click to select files` */
  dropzoneText: z.string().optional(),
  /** The color of the dropzone text. Defaults to the primary color of the theme */
  dropzoneTextColor: BIQColorZodSchema.optional(),
  /** The description to display in the dropzone. If not set, the description will not be displayed */
  dropzoneDescription: z.string().optional(),
  /** The color of the dropzone description. Defaults to `dimmed` a light gray color */
  dropzoneDescriptionColor: BIQColorZodSchema.optional(),

  // ********* Multiple Files Properties *********
  /** if the input can accept multiple files */
  multiple: z.boolean().optional(),
  /** If `multiple` is true, the max number of files that can be uploaded */
  maxLength: z.number().optional(),
  /** If `multiple` is true, the min number of files that can be uploaded */
  minLength: z.number().optional(),

  /** the max file size in bytes. If no max file size is set, the file size will not be checked */
  maxFileSize: z.number().optional(),

  /** If to render the list of uploaded files below the dropzone. Defaults to true */
  showUploadedFile: z.boolean().optional(),
});

export type BIQFileDropzoneSchema = z.infer<typeof BIQFileDropzoneZodSchema>;
```
