# schemas/error

Generated from the platform's runtime types. Do not edit.

Actor error configuration (`if`, `retryIf`, `message`, `includeResult`) and the runtime error names.

## schemas/error

**Source:** `schemas/error.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from './jsonSchema.js';

/**
 * Shared runtime error names. The orchestrator keys off `error.name` on a runtime error response, so
 * these strings are a wire contract between the lambda runtime and `packages/orchestrator` and
 * live here rather than in either side's own module.
 */

/**
 * The runtime could not start an actor from the prebuilt runtime cache it was handed — the artifact
 * failed to download, failed verification, or belongs to a different image.
 *
 * **Retryable, and the retry must differ**: the runtime deliberately does NOT fall back to resolving
 * dependencies itself, because a cached environment is shared by every actor of one canvas and the
 * legacy chain would resolve one actor's dependencies inside it. The orchestrator re-dispatches the
 * job exactly once with the cache block removed, which lands it in a fresh per-actor environment on
 * the legacy path.
 */
export const RUNTIME_CACHE_UNAVAILABLE_ERROR_NAME = 'RuntimeCacheUnavailable';

/**
 * An actor's code imports a module outside its own code directory. Never retryable — the same code
 * resolves the same way on a fresh container. Raised by the build-time module-graph lint (which can
 * name the offending specifier) and by the runtime when Deno's own permission check denies the read
 * at actor start (which deliberately cannot: an out-of-tree path is never echoed to the user).
 */
export const DISALLOWED_IMPORT_ERROR_NAME = 'DisallowedImport';


export const ActorErrorConfigurationSchema = z.object({
  if: z.boolean(),
  retryIf: z.boolean().nullish(),
  message: z.string().nullish(),
  includeResult: z.boolean().nullish(),
});

export type ActorErrorConfiguration = z.infer<typeof ActorErrorConfigurationSchema>;

export const ActorErrorConfigurationJsonSchema: BIQJsonSchema = {
  properties: {
    if: {
      type: BIQJsonSchemaType.Boolean,
      title: 'If',
      description: 'If the actor should throw an error',
      default: '${{}}',
    },
    retryIf: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Retry If',
      description: 'If the error should be retried',
      default: '${{}}',
    },
    message: {
      type: BIQJsonSchemaType.String,
      title: 'Message',
      description: 'The message to show to the user',
    },
    includeResult: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Include Result',
      description: 'If the error stack trace should include the result',
      default: false,
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['if'],
};
```
