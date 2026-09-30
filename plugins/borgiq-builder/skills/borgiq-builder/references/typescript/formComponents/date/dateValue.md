# formComponents/date/dateValue

Generated from the platform's runtime types. Do not edit.

A date-or-datetime value as an ISO string.

## formComponents/date/dateValue

**Source:** `formComponents/date/dateValue.ts`

```typescript
import { z } from 'zod';

/**
 * A date-or-datetime value as an ISO string.
 *
 * YAML parsers (js-yaml's default schema) turn unquoted values like
 * `default: 2026-07-24` or `default: 2026-07-24T10:00:00Z` into JS `Date`
 * objects before the schema ever sees them, so a plain string check would
 * reject YAML the author reasonably wrote. Coerce `Date` instances back to
 * their ISO string before validating.
 */
export const BIQIsoDateValueZodSchema = z.preprocess(
  (value) => value instanceof Date ? value.toISOString() : value,
  z.union([z.iso.datetime(), z.iso.date()]),
);
```
