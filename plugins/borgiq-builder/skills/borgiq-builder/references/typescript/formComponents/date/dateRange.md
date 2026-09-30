# formComponents/date/dateRange

Generated from the platform's runtime types. Do not edit.

The schema for a date range input.

See also: [formComponents/base](../base.md), [formComponents/date/dateValue](dateValue.md).

## formComponents/date/dateRange

**Source:** `formComponents/date/dateRange.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';
import { BIQIsoDateValueZodSchema } from './dateValue.js';

/** The schema for a date range input */
export const BIQDateRangeZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `dateRange` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.DateRange),

  /** the default value for the form input */
  default: z.object({
    startDate: BIQIsoDateValueZodSchema,
    endDate: BIQIsoDateValueZodSchema,
  }).optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  minDate: BIQIsoDateValueZodSchema.optional(),
  maxDate: BIQIsoDateValueZodSchema.optional(),

  /** the first day of the week where 0 is sunday and 6 is saturday */
  firstDayOfTheWeek: z.union([z.literal(0), z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)]).optional(),
  highlightToday: z.boolean().optional(),
  hideWeekdays: z.boolean().optional(),
});

export type BIQDateRangeSchema = z.infer<typeof BIQDateRangeZodSchema>;
```
