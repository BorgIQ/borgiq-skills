# formComponents/date/time

Generated from the platform's runtime types. Do not edit.

The schema for a time input.

See also: [formComponents/base](../base.md).

## formComponents/date/time

**Source:** `formComponents/date/time.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a time input */
export const BIQTimeZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `time` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Time),

  /** the default value for the form input */
  default: z.iso.time().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** if to allow the user to select the time with seconds in the input. Defaults to false */
  withSeconds: z.boolean().optional(),

  /** the minimum time for the input in 24 hour format. If not set, there is no minimum time */
  minTime: z.iso.time().optional(),
  /** the maximum time for the input in 24 hour format. If not set, there is no maximum time */
  maxTime: z.iso.time().optional(),
});

export type BIQTimeSchema = z.infer<typeof BIQTimeZodSchema>;
```
