# formComponents/display/webViewer

Generated from the platform's runtime types. Do not edit.

The schema for a web viewer component.

See also: [formComponents/base](../base.md), [actorSchemas/trigger/permissionsPolicy](../../actorSchemas/trigger/permissionsPolicy.md).

## formComponents/display/webViewer

**Source:** `formComponents/display/webViewer.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseComponentZodSchema } from '../base.js';
import { ZodIssueCode } from 'zod/v3';
import { PermissionsPolicyDirectiveZodSchema } from '../../actorSchemas/trigger/permissionsPolicy.js';

/** The schema for a web viewer component */
export const BIQWebViewZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `webViewer` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.WebViewer),

  /** the src url of the web viewer. This can be a url to the web viewer */
  src: z.string().optional().refine((val) => {
    if (!val) return true;
    try {
      new URL(val);
      return true;
    } catch {
      return false;
    }
  }, {
    message: 'Invalid src URL',
  }),
  /** the html content of the web viewer. This can be a html string */
  html: z.string().optional(),
  /** the width of the web viewer. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** the height of the web viewer. Defaults to 500px */
  height: z.union([z.number(), z.string()]).optional(),
  /** if the web viewer should be full screen, this would override the height and width and hide any other components. Defaults to false */
  fullScreen: z.boolean().optional(),
  /** allowed domains for external scripts (e.g., ['https://cdn.example.com', 'https://api.example.com']). Used for CSP script-src directive */
  allowedScriptDomains: z.array(z.url()).optional(),
  /** allowed domains for external stylesheets (e.g., ['https://fonts.googleapis.com', 'https://cdn.example.com']). Used for CSP style-src directive */
  allowedStyleDomains: z.array(z.url()).optional(),
  /** Permissions-Policy directives to enable for the webviewer (e.g., [PermissionsPolicyDirective.ClipboardWrite, PermissionsPolicyDirective.Fullscreen]). Controls access to browser APIs. */
  allowedPermissions: z.array(PermissionsPolicyDirectiveZodSchema).optional(),
  /** Enable unsafe-inline for styles, without hash verification (adds 'unsafe-inline' to style-src CSP). Use with caution as this reduces security. */
  allowInlineStyling: z.boolean().optional(),
  /** Enable unsafe-inline for scripts, without hash verification (adds 'unsafe-inline' to script-src CSP). Use with caution as this significantly reduces security. */
  allowInlineScripts: z.boolean().optional(),
}).superRefine((val, ctx) => {
  if (val.src && val.html) {
    ctx.addIssue({
      code: ZodIssueCode.custom,
      message: 'Only one of src or html must be provided',
      path: ['src'],
    });
    ctx.addIssue({
      code: ZodIssueCode.custom,
      message: 'Only one of src or html must be provided, but not both',
      path: ['html'],
    });
  } else if (!val.src && !val.html) {
    ctx.addIssue({
      code: ZodIssueCode.custom,
      message: 'Either src or html must be provided',
      path: ['src'],
    });
    ctx.addIssue({
      code: ZodIssueCode.custom,
      message: 'Either src or html must be provided',
      path: ['html'],
    });
  }
});

export type BIQWebViewSchema = z.infer<typeof BIQWebViewZodSchema>;
```
