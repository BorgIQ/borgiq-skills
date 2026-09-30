# formComponents/display/progress

Generated from the platform's runtime types. Do not edit.

The schema for a progress component.

See also: [formComponents/base](../base.md).

## formComponents/display/progress

**Source:** `formComponents/display/progress.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQColorZodSchema, BIQBaseComponentZodSchema, BIQElementSizeZodSchema } from '../base.js';

/** The schema for a progress component */
export const BIQProgressZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `progress` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Progress),

  /** the color of the divider. Defaults to a dimmed gray color */
  color: BIQColorZodSchema.optional(),
  /** the value of the progress from 0 to 100, if steps is set, the value is the floor of the value divided by the steps */
  value: z.number().min(0).max(100),
  /** the number of steps in the progress. Defaults to 1 */
  steps: z.number().min(1).optional(),
  
  /** if the progress bar should be striped. Defaults to false */
  striped: z.boolean().optional(),
  /** if the progress bar should be animated. Defaults to false */
  animated: z.boolean().optional(),
  
  /** the label to display in the progress bar. Defaults to empty */
  label: z.string().optional(),
  /** the label color of the progress bar. Defaults to the color of the progress bar */
  labelColor: BIQColorZodSchema.optional(),
  /** the label font size of the progress bar. Defaults to md */
  labelSize: BIQElementSizeZodSchema.optional(),
  /** the label font weight of the progress bar. Defaults to 400 */
  labelWeight: z.number().optional(),
  /** the label font size of the progress bar. Defaults to 14 */
  labelPosition: z.enum(['top', 'bottom']).optional(),
  /** the label alignment of the progress bar. Defaults to `left` */
  labelAlignment: z.enum(['left', 'center', 'right']).optional(),
});

export type BIQProgressSchema = z.infer<typeof BIQProgressZodSchema>;
```
