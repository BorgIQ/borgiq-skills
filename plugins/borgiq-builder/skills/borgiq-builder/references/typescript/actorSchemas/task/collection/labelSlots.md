# actorSchemas/task/collection/labelSlots

Generated from the platform's runtime types. Do not edit.

The number of named label slots a collection can define.

## actorSchemas/task/collection/labelSlots

**Source:** `actorSchemas/task/collection/labelSlots.ts`

```typescript
/**
 * The number of named label slots a collection can define.
 *
 * Each slot is backed by a physical Global Secondary Index on the collections
 * table — slot n is `GSI-L{n}`, keyed on `GSI{n}PK`/`GSI{n}SK` — so this is a
 * property of the table, not a per-tenant setting. Raising it means, in order:
 *
 *   1. adding the matching GSIs in internal infrastructure
 *      (`projects/dynamodb-setup/src/collectionsTable.ts`) and letting every
 *      index finish backfilling — they build one at a time, however many the
 *      apply adds;
 *   2. widening every existing collection's stored `labels` array with
 *      `scripts/data-migrations/20260821_widen_collection_label_slots.sh` — a
 *      collection created under the old limit keeps an array of that length,
 *      and `updateCollection` fills the first `null` slot it finds in it;
 *   3. deploying this constant;
 *   4. running that migration a second time, to widen the collections created
 *      between step 2 and step 3.
 *
 * DynamoDB's default quota is 20 GSIs per table, so 20 is the ceiling without a
 * service quota increase.
 */
export const MAX_LABEL_SLOTS = 15;
```
