# actorSchemas/task/deno

Generated from the platform's runtime types. Do not edit.

The DenoActor's `configuration.codeDir`: a project tree whose handler lives in `main.ts`, minus the paths the Deno bootstrap owns.

See also: [actorSchemas/codeDir](../codeDir.md).

## actorSchemas/task/deno

**Source:** `actorSchemas/task/deno.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';
import { DENO_ACTOR_ENTRYPOINT, DENO_RESERVED_PATHS, makeCodeDirSchema } from '../codeDir.js';

/**
 * The DenoActor's `configuration.codeDir`: a project tree whose handler lives in `main.ts`, minus the
 * paths the Deno bootstrap owns. Both rules are actor-type knowledge, so they live here rather than on
 * the wire-level `CodeDirSchema`.
 */
export const DenoActorCodeDirSchema = makeCodeDirSchema({
  requiredEntrypoint: DENO_ACTOR_ENTRYPOINT,
  reservedPaths: DENO_RESERVED_PATHS,
});

/** The options for the DenoActor */
export const DenoActorOptionsSchema = z.object({
  emitArrayAsSingleMessage: z.boolean().nullish()
    .describe('Emit the array as a single message instead of an array of messages, defaults to true').default(true),
  allowNet: z.boolean().nullish()
    .describe('Allow network access. By default when this is true, all network call is allowed but if allowNetList is provided then only that subset of URLs are allowed').default(false),
  allowNetList: z.array(z.string()).nullish()
    .describe('List of URLs that are allowed to be accessed when allowNet is true. This is ignored if allowNet is false').default([]),
  denyNetList: z.array(z.string()).nullish()
    .describe('List of URLs that are denied to be accessed when allowNet is true. This is ignored if allowNet is false').default([]),
  allowFs: z.boolean().nullish()
    .describe('Allow file system access to the temporary directory. By default when this is true, all file system access is allowed within the temporary directory').default(false),
  env: z.array(z.object({
    name: z.string()
      .regex(/^[A-Z0-9_]+$/, 'Environment variable name must contain only uppercase letters, numbers and underscores')
      .regex(/^(?!TMPDIR$)/, 'Environment variable name cannot be TMPDIR')
      .regex(/^(?!DENO_NO_UPDATE_CHECK$)/, 'Environment variable name cannot be DENO_NO_UPDATE_CHECK')
      .describe('Environment variable name (must contain only uppercase letters, numbers and underscores). If allowEnv is false, this will be ignored'),
    value: z.string().nullish()
      .describe('Environment variable value. If allowEnv is false, this will be ignored')
  })).nullish().default([])
    .describe('List of environment variables to pass to the Deno runtime'),
});

export type DenoActorOptions = z.infer<typeof DenoActorOptionsSchema>;

export const DenoActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    emitArrayAsSingleMessage: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit array as single message',
      description: 'Emit the array as a single message instead of an array of messages',
      default: true,
      ui: {
        component: 'switch',
      },
    },
    allowNet: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Allow net',
      description: 'Allow network access. By default when this is true, all network call is allowed but if allowNetList is provided then only that subset of URLs are allowed',
      ui: {
        component: 'switch',
      },
    },
    allowNetList: {
      type: BIQJsonSchemaType.Array,
      title: 'Allow net list',
      description: 'List of URLs that are allowed to be accessed when allowNet is true. This is ignored if allowNet is false',
      items: {
        type: BIQJsonSchemaType.String,
      },
    },
    denyNetList: {
      type: BIQJsonSchemaType.Array,
      title: 'Deny net list',
      description: 'List of URLs that are denied to be accessed when allowNet is true. This is ignored if allowNet is false',
      items: {
        type: BIQJsonSchemaType.String,
      },
    },
    allowFs: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Allow file system',
      description: 'Allow file system access to the temporary directory. By default when this is true, all file system access is allowed within the temporary directory',
      ui: {
        component: 'switch',
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
            pattern: '^(?!TMPDIR$)(?!DENO_NO_UPDATE_CHECK$)[A-Z0-9_]+$'
          },
          value: {
            type: BIQJsonSchemaType.String,
            title: 'Value',
            description: 'Environment variable value'
          }
        },
        required: ['name']
      }
    }
  },
};

/** The response schema for the DenoActor */
export const DenoActorResultSchema = z.any();

export type DenoActorResult = z.infer<typeof DenoActorResultSchema>;
```
