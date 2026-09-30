# formComponents/date/date

Generated from the platform's runtime types. Do not edit.

The schema for a date input.

See also: [formComponents/base](../base.md), [formComponents/date/dateValue](dateValue.md).

## formComponents/date/date

**Source:** `formComponents/date/date.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';
import { BIQIsoDateValueZodSchema } from './dateValue.js';

/** The schema for a date input */
export const BIQDateZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `date` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Date),

  /** the default value for the form input */
  default: BIQIsoDateValueZodSchema.optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** the minimum date that can be selected. If not set, there is no minimum date */
  minDate: BIQIsoDateValueZodSchema.optional(),
  /** the maximum date that can be selected. If not set, there is no maximum date */
  maxDate: BIQIsoDateValueZodSchema.optional(),

  /** the first day of the week where 0 is sunday and 6 is saturday. Defaults to 1 (monday) */
  firstDayOfTheWeek: z.union([z.literal(0), z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)]).optional(),
  /** if to highlight the current date on the calendar. Defaults to true */
  highlightToday: z.boolean().optional(),
  /** if to hide the weekday names on the top of the calendar. Defaults to false */
  hideWeekdays: z.boolean().optional(),
  /** if to allow deselecting the date. Defaults to false */
  allowDeselect: z.boolean().optional(),
});

export type BIQDateSchema = z.infer<typeof BIQDateZodSchema>;
```
