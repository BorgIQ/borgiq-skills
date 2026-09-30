# actorSchemas/task/denoTest

Generated from the platform's runtime types. Do not edit.

The DenoTestActor's `configuration.codeDir`: a project tree whose handler lives in `main.ts`, minus the paths the Deno bootstrap owns.

See also: [actorSchemas/codeDir](../codeDir.md).

## actorSchemas/task/denoTest

**Source:** `actorSchemas/task/denoTest.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';
import { DENO_RESERVED_PATHS, DENO_TEST_ACTOR_ENTRYPOINT, makeCodeDirSchema } from '../codeDir.js';

/**
 * The DenoTestActor's `configuration.codeDir`: a project tree whose handler lives in `main.ts`, minus
 * the paths the Deno bootstrap owns. This type shares the `deno-actor` bootstrap variant with the
 * DenoActor, so it shares that variant's reserved set too.
 */
export const DenoTestActorCodeDirSchema = makeCodeDirSchema({
  requiredEntrypoint: DENO_TEST_ACTOR_ENTRYPOINT,
  reservedPaths: DENO_RESERVED_PATHS,
});

/** The options for the DenoTestActor */
export const DenoTestActorOptionsSchema = z.object({
  emitArrayAsSingleMessage: z.boolean().nullish()
    .describe('Emit the array as a single message instead of an array of messages').default(false),
  argList: z.array(z.string()).nullish()
    .describe('List of command line arguments to pass to deno.').default([]),
  env: z.array(z.object({
    name: z.string()
      .regex(/^[A-Z0-9_]+$/)
      .describe('Environment variable name (must contain only uppercase letters, numbers and underscores)'),
    value: z.string().describe('Environment variable value')
  })).nullish().default([])
    .describe('List of environment variables to pass to the Deno runtime'),
});

export type DenoTestActorOptions = z.infer<typeof DenoTestActorOptionsSchema>;

export const DenoTestActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    emitArrayAsSingleMessage: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit array as single message',
      description: 'Emit the array as a single message instead of an array of messages',
      ui: {
        component: 'switch',
      },
    },
    argList: {
      type: BIQJsonSchemaType.Array,
      title: 'Argument list',
      description: 'List of command line arguments to pass to deno.',
      items: {
        type: BIQJsonSchemaType.String,
      },
    },
    env: {
      type: BIQJsonSchemaType.Array,
      title: 'Environment variables',
      description: 'List of environment variables to pass to the Deno runtime',
      items: {
        type: BIQJsonSchemaType.Object,
        properties: {
          name: {
            type: BIQJsonSchemaType.String,
            title: 'Name',
            description: 'Environment variable name (must contain only uppercase letters, numbers and underscores)',
            pattern: '^[A-Z0-9_]+$'
          },
          value: {
            type: BIQJsonSchemaType.String,
            title: 'Value',
            description: 'Environment variable value'
          }
        }
      }
    }
  },
};

/** The response schema for the DenoTestActor */
export const DenoTestActorResultSchema = z.any();

export type DenoTestActorResult = z.infer<typeof DenoTestActorResultSchema>;
```
