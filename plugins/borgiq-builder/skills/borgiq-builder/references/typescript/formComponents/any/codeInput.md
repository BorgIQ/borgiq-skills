# formComponents/any/codeInput

Generated from the platform's runtime types. Do not edit.

The schema for an object or other native javascript types input using a code editor (codemirror editor) using yaml or json parsing.

See also: [formComponents/base](../base.md).

## formComponents/any/codeInput

**Source:** `formComponents/any/codeInput.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for an object or other native javascript types input using a code editor (codemirror editor) using yaml or json parsing */
export const BIQAnyCodeInputZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `anyCodeInput` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.AnyCodeInput),

  /** The default value for the form input. The object will be be converted to the correct format based on the language selected */
  default: z.any().optional(),
  /** The placeholder to render in the input section */
  placeholder: z.any().optional(),

  /** the language the input will be formatted in, the stringified input will be converted to a javascript object (yaml.load or JSON.parse) */
  language: z.enum(['yaml', 'json']).optional(),
  

  /** wrap the lines of the input in the code editor */
  wrapLines: z.boolean().optional(),
  /** the minimum lines of the code editor. Defaults to 10 */
  minLines: z.number().optional(),
  /** the maximum lines of the code editor. If not set, the code editor will auto-resize to fit the content */
  maxLines: z.number().optional(),
  /** to set a specific height of the code editor (this will override the minLines and maxLines) */
  height: z.union([z.number(), z.string()]).optional(),
  /** the width of the code editor defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** if the component is a code editor let it auto-resize to fit content, defaults to true */
  autoResize: z.boolean().optional(),
});

export type BIQAnyCodeInputSchema = z.infer<typeof BIQAnyCodeInputZodSchema>;
```
