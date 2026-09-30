# formComponents/file/fileInput

Generated from the platform's runtime types. Do not edit.

The schema for a file input.

See also: [formComponents/base](../base.md).

## formComponents/file/fileInput

**Source:** `formComponents/file/fileInput.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a file input */
export const BIQFileInputZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `fileInput` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.FileInput),

  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  // the accept file types formatted as a comma separated list of mime types. Defaults to `*/*` which means any file type is acceptable.
  // see https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept
  accept: z.string().optional(),

  // ********* Multiple Files Properties *********
  /** if the input can accept multiple files */
  multiple: z.boolean().optional(),
  /** If `multiple` is true, the max number of files that can be uploaded */
  maxLength: z.number().optional(),
  /** If `multiple` is true, the min number of files that can be uploaded */
  minLength: z.number().optional(),

  /** the max file size in bytes. If no max file size is set, the file size will not be checked */
  maxFileSize: z.number().optional(),
});

export type BIQFileInputSchema = z.infer<typeof BIQFileInputZodSchema>;
```
