# actorSchemas/task/stream/limits

Generated from the platform's runtime types. Do not edit.

The stream limits the option schemas enforce, in one place.

## actorSchemas/task/stream/limits

**Source:** `actorSchemas/task/stream/limits.ts`

```typescript
/**
 * The stream limits that a SCHEMA can enforce, in one place.
 *
 * Streams are validated three times over — the actor option schemas here, the API request schemas
 * in `@borgiq/types`, and the service layer in `@borgiq/core` — and each of those copies used to
 * carry its own literals. That is how the `persistent` mismatch got in: three declarations of one
 * contract drift silently, and the drift only surfaces as a platform 400 against an input the
 * actor's own `validate()` accepted.
 *
 * So the numbers live here, in the package the runtime mirrors, and the other two import them. This
 * is the same reason `collection/labelSlots.ts` exists.
 *
 * What is NOT here: anything that is a platform *policy* rather than a schema *constraint* — the
 * default idle TTL, the default record size, the per-workspace stream cap, the rate limits. Those
 * stay in `STREAM_LIMITS` (`packages/core/src/lib/streams/limits.ts`), because no schema rejects an
 * input for violating them; the service decides. The one number that spans both worlds is the
 * record-size ceiling, and core derives its byte form from the envelope overhead — a unit test
 * asserts the two agree rather than a comment asking you to keep them in step.
 */

/**
 * Slugs are the renameable, human-facing handle for a stream.
 *
 * Deliberately narrower than the column: no uppercase (a slug is compared literally, and two
 * spellings of one name resolving to two streams is a support ticket), no leading separator, and no
 * `/` — the locator that addresses a stream inside its backend uses `/` as its separator, so a slug
 * carrying one could collide across workspaces.
 *
 * The `{0,63}` bound is the 64-character maximum expressed inside the pattern, so a schema that
 * applies this regex is correct even without a separate `.max()`.
 */
const SLUG_PATTERN = /^[a-z0-9][a-z0-9_-]{0,63}$/;

export const STREAM_SCHEMA_LIMITS = {

  /** The slug pattern. Enforced identically by the actor schemas, the API schemas and `assertValidSlug`. */
  slugPattern: SLUG_PATTERN,

  /** Longest slug. Matches the `{0,63}` repeat in the pattern above. */
  slugMaxLength: 64,

  /**
   * Longest stream reference.
   *
   * A reference is a slug OR an external stream id, so it is bounded by the longer of the two —
   * which is the slug, ids being 30 characters.
   */
  streamRefMaxLength: 64,

  /** Longest display name. */
  nameMaxLength: 120,

  /** Longest description. */
  descriptionMaxLength: 500,

  /** Shortest idle TTL a stream may set. */
  minIdleTtlSeconds: 60,

  /** Longest idle TTL a stream may set. Beyond this, a stream should be explicitly persistent. */
  maxIdleTtlSeconds: 30 * 24 * 60 * 60,

  /** Records per append batch. Below the backend's own 1000 so the vendor limit is never the one that bites. */
  appendBatchRecords: 500,

  /** Records per read page. */
  readPageRecords: 1000,

  /** Bytes per read page. */
  readPageBytes: 1024 * 1024,

  /**
   * Largest per-record ceiling a stream may configure, in kilobytes.
   *
   * The backend meters a record at 1 MiB *including* the encryption envelope, so the configurable
   * payload ceiling is that minus the envelope overhead, floored to whole kilobytes. Core computes
   * the byte form from the overhead constant; `streams-limits.test.ts` asserts it lands here.
   */
  maxRecordSizeKiloBytes: 1023,

} as const;

export default STREAM_SCHEMA_LIMITS;
```
