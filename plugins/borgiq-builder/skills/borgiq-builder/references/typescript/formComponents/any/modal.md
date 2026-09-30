# formComponents/any/modal

Generated from the platform's runtime types. Do not edit.

The schema for an object input edited as YAML or JSON in a modal code editor.

See also: [formComponents/base](../base.md).

## formComponents/any/modal

**Source:** `formComponents/any/modal.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema, BIQColorZodSchema, BIQButtonStyleZodSchema, BIQButtonComponentSizeZodSchema } from '../base.js';

/**
 *  The schema for an object or other native javascript types input using a code editor (codemirror editor) using yaml or json parsing.
 *  The codemirror editor will be rendered in a modal for a larger input area.
 **/
export const BIQAnyModalZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `anyModal` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.AnyModal),

  /** The default value for the form input. The object will be be converted to the correct format based on the language selected */
  default: z.any().optional(),
  /** The placeholder to render in the input section */
  placeholder: z.any().optional(),

  /** the language the input will be formatted in, the stringified input will be converted to a javascript object (yaml.load or JSON.parse) */
  language: z.enum(['yaml', 'json']).optional(),
  

  // ********** The Props to edit the codemirror editor *********
  /** wrap the lines of the code editor */
  wrapLines: z.boolean().optional(),
  /** the minimum lines of the code editor */
  minLines: z.number().optional(),
  /** the maximum lines of the code editor */
  maxLines: z.number().optional(),
  /** the set height of the code editor */
  height: z.union([z.number(), z.string()]).optional(),
  /** the width of the code editor defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** if the component is a code editor let it auto-resize to fit content, defaults to true */
  autoResize: z.boolean().optional(),

  // ********** The Props to edit the button to open the modal that is rendered in the form *********
  /** the text to display on the button to open the modal. Defaults to Edit */
  openButtonText: z.string().optional(),
  /** the color of the button to open the modal. Defaults to the Theme Color */
  openButtonColor: BIQColorZodSchema.optional(),
  /** the variant of the button to open the modal. Defaults to Outline */
  openButtonVariant: BIQButtonStyleZodSchema.optional(),
  /** the size of the button to open the modal. Defaults to md */
  openButtonSize: BIQButtonComponentSizeZodSchema.optional(),

  // ********** The Props to edit the button to close the modal that is rendered on the bottom of the modal *********
  /** the text to display on the button to close the modal. Defaults to Close */
  closeButtonText: z.string().optional(),
  /** the color of the button to close the modal. Defaults to the Theme Color */
  closeButtonColor: BIQColorZodSchema.optional(),
  /** the variant of the button to close the modal. Defaults to Filled */
  closeButtonVariant: BIQButtonStyleZodSchema.optional(),
  /** the size of the button to close the modal. Defaults to md */
  closeButtonSize: BIQButtonComponentSizeZodSchema.optional(),
});

export type BIQAnyModalSchema = z.infer<typeof BIQAnyModalZodSchema>;
```
