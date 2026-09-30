# formComponents/date/dateTime

Generated from the platform's runtime types. Do not edit.

The schema for a date time input.

See also: [formComponents/base](../base.md), [formComponents/date/dateValue](dateValue.md).

## formComponents/date/dateTime

**Source:** `formComponents/date/dateTime.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';
import { BIQIsoDateValueZodSchema } from './dateValue.js';

/** The schema for a date time input */
export const BIQDateTimeZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `dateTime` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.DateTime),

  /** the default value for the form input */
  default: BIQIsoDateValueZodSchema.optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** if to allow the user to select the time with seconds in the input. Defaults to false */
  withSeconds: z.boolean().optional(),

  /** the minimum date time that can be selected. If not set, there is no minimum date time */
  minDate: BIQIsoDateValueZodSchema.optional(),
  /** the maximum date time that can be selected. If not set, there is no maximum date time */
  maxDate: BIQIsoDateValueZodSchema.optional(),

  /** the first day of the week where 0 is sunday and 6 is saturday. Defaults to 1 (monday) */
  firstDayOfTheWeek: z.union([z.literal(0), z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)]).optional(),
  /** if to highlight the current date on the calendar. Defaults to true */
  highlightToday: z.boolean().optional(),
  /** if to hide the weekday names on the top of the calendar. Defaults to false */
  hideWeekdays: z.boolean().optional(),
});

export type BIQDateTimeSchema = z.infer<typeof BIQDateTimeZodSchema>;
```
