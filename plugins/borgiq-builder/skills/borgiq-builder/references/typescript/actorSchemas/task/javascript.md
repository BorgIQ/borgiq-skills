# actorSchemas/task/javascript

Generated from the platform's runtime types. Do not edit.

JavaScriptActor options and `configuration.codeDir`, including the `main.ts` entrypoint and reserved paths.

See also: [actorSchemas/codeDir](../codeDir.md), [actorSchemas/task/deno](deno.md).

## actorSchemas/task/javascript

**Source:** `actorSchemas/task/javascript.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema } from '../../schemas/index.js';
import { JS_ACTOR_ENTRYPOINT, JS_ACTOR_RESERVED_PATHS, makeCodeDirSchema } from '../codeDir.js';
import { DenoActorOptionsJsonSchema } from './deno.js';

/**
 * The JavaScriptActor runs the DenoActor's code — the same `main.ts` default-exporting `receive(req)`,
 * the same `@borgiq/actors` SDK, the same results — on workerd (the workerd sandbox) instead of Deno.
 */

/** The JavaScriptActor's `configuration.codeDir`: a project tree whose handler lives in `main.ts`. */
export const JavaScriptActorCodeDirSchema = makeCodeDirSchema({
  requiredEntrypoint: JS_ACTOR_ENTRYPOINT,
  reservedPaths: JS_ACTOR_RESERVED_PATHS,
});

const ALLOW_NET_DESCRIPTION = 'Allow network access. When this is true every host may be reached, unless allowNetList is provided: then only the hosts it lists may be reached';

const ENV_DESCRIPTION = 'List of environment variables the actor reads from process.env. They are set afresh for every invocation, so changing a value never rebuilds the actor';

/**
 * A network-list entry the egress forwarder can match: a host name, an IP address, `host:port`, or a
 * URL (only its host counts). A wildcard or anything without a host fails this schema, because the
 * forwarder would silently never match it: the editor's save shows it as an options warning, a strict
 * batch save rejects it, and a run fails when the runtime parses the options.
 */
const NetListEntrySchema = z.string().refine((entry) => {
  try {
    const { hostname } = new URL(entry.includes('://') ? entry : `https://${entry}`);
    return hostname.length > 0 && !hostname.includes('*');
  } catch {
    return false;
  }
}, { message: 'Each entry must be a host name, an IP address or a URL, such as api.example.com or https://api.example.com:8443. Wildcards are not supported.' });

/**
 * The options for the JavaScriptActor: the DenoActor's, without `allowFs` (a test holds the two to
 * the same fields and defaults). workerd gives user code no host filesystem to grant; `node:fs` is an
 * in-memory `/tmp` that lasts one invocation. A DenoActor configuration switched to this type keeps
 * working: the unknown `allowFs` key is stripped, and the DenoActor's env-name rules (no `TMPDIR`, no
 * `DENO_NO_UPDATE_CHECK`) are kept for the same reason, although workerd reads neither.
 */
export const JavaScriptActorOptionsSchema = z.object({
  emitArrayAsSingleMessage: z.boolean().nullish()
    .describe('Emit the array as a single message instead of an array of messages, defaults to true').default(true),
  allowNet: z.boolean().nullish()
    .describe(ALLOW_NET_DESCRIPTION).default(false),
  allowNetList: z.array(NetListEntrySchema).nullish()
    .describe('List of host names, IP addresses or URLs that are allowed to be accessed when allowNet is true. This is ignored if allowNet is false').default([]),
  denyNetList: z.array(NetListEntrySchema).nullish()
    .describe('List of host names, IP addresses or URLs that are denied to be accessed when allowNet is true. This is ignored if allowNet is false').default([]),
  env: z.array(z.object({
    name: z.string()
      .regex(/^[A-Z0-9_]+$/, 'Environment variable name must contain only uppercase letters, numbers and underscores')
      .regex(/^(?!TMPDIR$)/, 'Environment variable name cannot be TMPDIR')
      .regex(/^(?!DENO_NO_UPDATE_CHECK$)/, 'Environment variable name cannot be DENO_NO_UPDATE_CHECK')
      .describe('Environment variable name (must contain only uppercase letters, numbers and underscores)'),
    value: z.string().nullish()
      .describe('Environment variable value'),
  })).nullish().default([])
    .describe(ENV_DESCRIPTION),
});

export type JavaScriptActorOptions = z.infer<typeof JavaScriptActorOptionsSchema>;

const { allowFs: _allowFs, env: denoEnv, ...sharedOptionProperties } = DenoActorOptionsJsonSchema.properties ?? {};

export const JavaScriptActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    ...sharedOptionProperties,
    // overriding in place keeps the DenoActor's field order
    allowNet: { ...sharedOptionProperties.allowNet, description: ALLOW_NET_DESCRIPTION },
    env: { ...denoEnv, description: ENV_DESCRIPTION },
  },
};

/** The response schema for the JavaScriptActor */
export const JavaScriptActorResultSchema = z.any();

export type JavaScriptActorResult = z.infer<typeof JavaScriptActorResultSchema>;
```
