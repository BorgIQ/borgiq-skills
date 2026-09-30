# actorSchemas/task/python

Generated from the platform's runtime types. Do not edit.

The PythonActor's `configuration.codeDir`: a project tree whose handler lives in `main.py`, minus the paths the Python runtime owns.

See also: [actorSchemas/codeDir](../codeDir.md).

## actorSchemas/task/python

**Source:** `actorSchemas/task/python.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';
import { PYTHON_ACTOR_ENTRYPOINT, PYTHON_RESERVED_PATHS, makeCodeDirSchema } from '../codeDir.js';

/**
 * The PythonActor's `configuration.codeDir`: a project tree whose handler lives in `main.py`, minus
 * the paths the Python runtime owns. Unlike the Deno family, most of those are reserved against
 * `sys.path` SHADOWING rather than overwriting — the actor's work dir sits ahead of `.borgiq/` on
 * the search path, so a root `handler.py` would win over the runtime's without touching it.
 */
export const PythonActorCodeDirSchema = makeCodeDirSchema({
  requiredEntrypoint: PYTHON_ACTOR_ENTRYPOINT,
  reservedPaths: PYTHON_RESERVED_PATHS,
});

/** The options for the PythonActor */
export const PythonActorOptionsSchema = z.object({
  emitArrayAsSingleMessage: z.boolean().nullish()
    .describe('Emit the array as a single message instead of an array of messages, defaults to true').default(true),
  dependencies: z.array(z.string()).nullish()
    .describe('List of Python package dependencies (e.g., ["pandas>=2.0.0", "numpy>=1.24.0"]). These will be installed using UV').default([]),
  env: z.array(z.object({
    name: z.string()
      .regex(/^[A-Z0-9_]+$/, 'Environment variable name must contain only uppercase letters, numbers and underscores')
      .regex(/^(?!TMPDIR$)/, 'Environment variable name cannot be TMPDIR')
      .regex(/^(?!HOME$)/, 'Environment variable name cannot be HOME')
      .regex(/^(?!PYTHONUNBUFFERED$)/, 'Environment variable name cannot be PYTHONUNBUFFERED')
      .regex(/^(?!UV_CACHE_DIR$)/, 'Environment variable name cannot be UV_CACHE_DIR')
      .regex(/^(?!UV_PROJECT_ENVIRONMENT$)/, 'Environment variable name cannot be UV_PROJECT_ENVIRONMENT')
      .regex(/^(?!PYTHONUSERBASE$)/, 'Environment variable name cannot be PYTHONUSERBASE')
      .describe('Environment variable name (must contain only uppercase letters, numbers and underscores)'),
    value: z.string().nullish()
      .describe('Environment variable value')
  })).nullish().default([])
    .describe('List of environment variables to pass to the Python runtime'),
});

export type PythonActorOptions = z.infer<typeof PythonActorOptionsSchema>;

export const PythonActorOptionsJsonSchema: BIQJsonSchema = {
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
    dependencies: {
      type: BIQJsonSchemaType.Array,
      title: 'Python dependencies',
      description: 'List of Python package dependencies (e.g., "pandas>=2.0.0", "numpy>=1.24.0"). These will be installed using UV',
      items: {
        type: BIQJsonSchemaType.String,
      },
    },
    env: {
      type: BIQJsonSchemaType.Array,
      title: 'Environment variables',
      description: 'List of environment variables to pass to the Python runtime',
      items: {
        type: BIQJsonSchemaType.Object,
        properties: {
          name: {
            type: BIQJsonSchemaType.String,
            title: 'Name',
            description: 'Environment variable name (must contain only uppercase letters, numbers and underscores)',
            pattern: '^(?!TMPDIR$)(?!HOME$)(?!PYTHONUNBUFFERED$)(?!UV_CACHE_DIR$)(?!UV_PROJECT_ENVIRONMENT$)(?!PYTHONUSERBASE$)[A-Z0-9_]+$'
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

/** The response schema for the PythonActor */
export const PythonActorResultSchema = z.any();

export type PythonActorResult = z.infer<typeof PythonActorResultSchema>;
```
