# schemas/file

Generated from the platform's runtime types. Do not edit.

`BIQFile`, the file reference actors pass around, and the file upload inputs.

See also: [schemas/idSchema](idSchema.md).

## schemas/file

**Source:** `schemas/file.ts`

```typescript
/** NOTE: This file is to ONLY be used for types that is used in the runtime. */
import { z } from 'zod';

import { idSchema } from './idSchema.js';

import { BIQFileStatus, BIQFileStorageEngine, BIQFileUsageType } from '../common.js';

const status = z.enum(BIQFileStatus);
const usageType = z.enum(BIQFileUsageType);

export const FileInputSchema = z.object({
  id: idSchema.fileId,
  key: z.string(),
  fileName: z.string().min(1, 'must be 1 or more characters long').max(255, 'must be 255 or fewer characters long'),
  mimeType: z.string().min(1, 'must be 1 or more characters long').max(255, 'must be 255 or fewer characters long'),
  sizeInBytes: z.number().int(),
  storageEngine: z.enum(BIQFileStorageEngine).optional(),
  status: z.optional(status),
  usageType: z.optional(usageType),
  md5: z.optional(z.string()),
  sha256: z.optional(z.string()),
});

export type FileInput = z.infer<typeof FileInputSchema>;

export const BIQFileSchema = z.object({
  id: idSchema.fileId,
  fileName: z.string(),
  md5: z.string(),
  sha256: z.string(),
  mimeType: z.string(),
  sizeInBytes: z.number(),
  createdAt: z.string(),
});

export type BIQFile = z.infer<typeof BIQFileSchema>;

/** this is the input the api receives for uploading multiple files, if this updates, make sure to update the FilesRuntimeUploadedSchemaFromRuntime */
export const FilesRuntimeUploadInputSchema = z.object({
  body: z.object({
    files: z.array(FileInputSchema.extend({ uploadIndex: z.number() })),
    // Validate the flowrun id shape (FLRN-prefixed, 30 chars) rather than accepting any string —
    // this endpoint writes it straight into files.flowrun_id, so a session/sandbox id or malformed
    // value must be rejected at the boundary instead of silently persisted.
    flowrunId: idSchema.flowrunId,
  }),
});

export type FilesRuntimeUploadInput = z.infer<typeof FilesRuntimeUploadInputSchema>;

/** since the api middleware adds the id and key to each file, this is the input required to be sent from the runtime */
export const RuntimeBodyFilesUploadedInputsSchema = z.object({
  files: z.array(FileInputSchema.omit({ id: true, key: true }).extend({ uploadIndex: z.number() })),
  // Same flowrun-id shape validation as FilesRuntimeUploadInputSchema (this is the runtime-side
  // body before the API middleware adds id/key) — keep the two in sync.
  flowrunId: idSchema.flowrunId,
});

export type RuntimeBodyFilesUploaded = z.infer<typeof RuntimeBodyFilesUploadedInputsSchema>;

export const FilesRuntimeUpdateUploadsBodySchema = z.object({
  files: z.array(
    z.object({
      id: idSchema.fileId,
      status,
      md5: z.optional(z.string()),
      sha256: z.optional(z.string()),
    }).refine((data) => {
      // if the file is uploaded successfully, then the md5 and sha256 are required
      if (data.status === BIQFileStatus.UploadSuccess) {
        return data.md5 !== undefined && data.sha256 !== undefined;
      }
      return true;
    }, {
      error: 'MD5 and SHA256 are required for successful file upload.',
    }),
  ),
});

export type FilesRuntimeUpdateUploadsBody = z.infer<typeof FilesRuntimeUpdateUploadsBodySchema>;

/** this is the output the api returns for uploading multiple files, if this updates, make sure to update the FilesRuntimeUploadedSchemaFromRuntime */
export const FilesRuntimeUpdateUploadsInputsSchema = z.object({
  body: FilesRuntimeUpdateUploadsBodySchema,
});

export type FilesRuntimeUpdateUploadsInputs = z.infer<typeof FilesRuntimeUpdateUploadsInputsSchema>;
```
