# schemas/interface

Generated from the platform's runtime types. Do not edit.

Interface page data and the `onSubmit` variants.

See also: [formComponents/form](../formComponents/form.md).

## schemas/interface

**Source:** `schemas/interface.ts`

```typescript
import { z } from 'zod';
import { biqFormComponentArrayZodSchema } from '../formComponents/index.js';

export const BIQInterfacePageDataSchema = z.object({
  formWidth: z.enum(['full', 'half', 'adjustable']).optional(),
  children: biqFormComponentArrayZodSchema,
  pageTitle: z.string().optional(),
  themeColor: z.string().optional(),
  backgroundColor: z.string().optional(),
});

export type BIQInterfacePageData = z.infer<typeof BIQInterfacePageDataSchema>;

export const InterfaceOnSubmitWaitForInterfaceSchema = z.object({
  type: z.literal('nextInterface'),
  loadingMessage: z.string().optional(),
});

export type InterfaceOnSubmitWaitForInterface = z.infer<typeof InterfaceOnSubmitWaitForInterfaceSchema>;

export const InterfaceOnSubmitSuccessMessageSchema = z.object({
  type: z.literal('successMessage'),
  successMessage: z.string().optional(),
});

export type InterfaceOnSubmitSuccessMessage = z.infer<typeof InterfaceOnSubmitSuccessMessageSchema>;

export const InterfaceOnSubmitUrlRedirectSchema = z.object({
  type: z.literal('urlRedirect'),
  url: z.string(),
});

export type InterfaceOnSubmitUrlRedirect = z.infer<typeof InterfaceOnSubmitUrlRedirectSchema>;

export const InterfaceOnSubmitSchema = z.discriminatedUnion('type', [
  InterfaceOnSubmitWaitForInterfaceSchema,
  InterfaceOnSubmitSuccessMessageSchema,
  InterfaceOnSubmitUrlRedirectSchema,
]);

export type InterfaceOnSubmit = z.infer<typeof InterfaceOnSubmitSchema>;
```
