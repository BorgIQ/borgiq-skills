# actorSchemas/trigger/reactApp

Generated from the platform's runtime types. Do not edit.

ReactAppTriggerActor options and limits: source and overlay files, endpoints, stream grants, and the script, style, permission and WebAssembly allowances.

See also: [canvas](../../canvas.md), [schemas/file](../../schemas/file.md), [schemas/idSchema](../../schemas/idSchema.md), [actorSchemas/trigger/permissionsPolicy](permissionsPolicy.md), [actorSchemas/codeDir](../codeDir.md).

## actorSchemas/trigger/reactApp

**Source:** `actorSchemas/trigger/reactApp.ts`

```typescript
import { z } from 'zod';

// Import from the concrete leaf module, NOT the `../../schemas/index.js` barrel: the barrel pulls in
// `runtime.js`, which imports THIS file (for ReactAppCodeDirSchema, added in §4.1). Going through the
// barrel forms a cycle that leaves `BIQJsonSchemaType` undefined when the JSON-schema literal below
// evaluates at module load. jsonSchema.js is a dependency-free leaf, so importing it directly is cycle-safe.
import { BIQActorType } from '../../canvas.js';
import { BIQJsonSchemaType } from '../../schemas/jsonSchema.js';
import type { BIQJsonSchema } from '../../schemas/jsonSchema.js';
import { BIQFileSchema } from '../../schemas/file.js';
import { idSchema } from '../../schemas/idSchema.js';
import { PermissionsPolicyDirective, PermissionsPolicyDirectiveZodSchema } from './permissionsPolicy.js';
import { CodeDirSchema, CodeFileSchema, normalizeCodePath } from '../codeDir.js';
import type { CodeDir, CodeFile } from '../codeDir.js';

/** Maximum number of interpolatable overlay files in `configuration.options.files`. */
export const MAX_OPTIONS_FILES = 50;
/** Maximum number of endpoints declared on a ReactAppTriggerActor (Phase II). */
export const MAX_REACT_APP_ENDPOINTS = 50;
/** Maximum number of stream grants declared on a ReactAppTriggerActor. */
export const MAX_REACT_APP_STREAMS = 50;

/**
 * React-app back-compat aliases over the generic `codeDir` module (`../codeDir.ts`), which owns
 * the path normalizer, the file schema and the size caps for every actor type that carries a
 * `configuration.codeDir`. React-app keeps the plain schema — no entrypoint requirement and no
 * reserved paths: its tree never shares a directory with runtime files, it is materialized into
 * a per-build temp dir.
 */
export const ReactAppCodeFileSchema = CodeFileSchema;
export type ReactAppCodeFile = CodeFile;
export const ReactAppCodeDirSchema = CodeDirSchema;
export type ReactAppCodeDir = CodeDir;
export const normalizeReactAppPath = normalizeCodePath;

/** An interpolatable overlay file: inline text OR a BIQFile handle (typically `${{ assets.<key> }}`). */
export const ReactAppOptionsFileSchema = z.object({
  /** path relative to the project root; same path rules as codeDir */
  path: z.string().min(1).max(255),
  /** inline text OR a BIQFile handle (typically produced by `${{ assets.<key> }}`) */
  content: z.union([z.string(), BIQFileSchema]),
});

export type ReactAppOptionsFile = z.infer<typeof ReactAppOptionsFileSchema>;

/**
 * A named endpoint bound to a webhook-capable trigger — a WebhookTriggerActor, or a
 * UniversalTriggerActor with its webhook source enabled (Phase II — §5.1, §15.3.5, §18).
 * Coordinates are slugs (CallFlow parity — callFlow.ts stores slugs); absent workspace/canvas
 * default to the app actor's own. Same-org only. Because options are interpolatable, the string
 * fields may carry `${{ }}` expressions resolved at build time (§15.3.5).
 */
export const ReactAppEndpointSchema = z.object({
  /** unique within this actor's endpoint list; the hook lookup key */
  name: z.string().regex(/^[a-zA-Z_][a-zA-Z0-9_]*$/, 'endpoint name must be a valid identifier'),
  description: z.string().nullish(),
  /** the target trigger: a WebhookTriggerActor, or a UniversalTriggerActor with its webhook source enabled */
  actorId: idSchema.actorId,
  /** target workspace slug; absent = the app actor's own workspace. Same-org only. */
  workspaceSlug: z.string().nullish(),
  /** target canvas slug; absent = the app actor's own canvas. */
  canvasSlug: z.string().nullish(),
});

export type ReactAppEndpoint = z.infer<typeof ReactAppEndpointSchema>;

/**
 * A stream grant: a workspace stream (or a family of them) the app may read live through the
 * `@borgiq/actors` SDK's `useStreamTail`. Mirrors `ReactAppEndpointSchema` in shape, lifecycle and
 * posture — frozen into the build manifest at Build time, and the token is authorized against the
 * manifest, never against the viewer's workspace role.
 *
 * Exactly one of `slug` (one stream, by its workspace slug) or `slugPrefix` (every stream whose
 * slug starts with it — the shape for streams a flow creates per session, conversation or device,
 * whose slugs cannot be known when the app is authored). No globs, no regexes: a prefix is what a
 * customer can reason about and what the API can match in one string comparison. Same workspace
 * only in v1. The string fields may carry `${{ }}` expressions resolved at build time, like an
 * endpoint's.
 */
export const ReactAppStreamGrantSchema = z.object({
  /** unique within this actor's stream list; a valid identifier, like an endpoint name */
  name: z.string().regex(/^[a-zA-Z_][a-zA-Z0-9_]*$/, 'stream grant name must be a valid identifier'),
  description: z.string().nullish(),
  /** one stream, by its workspace slug (mutually exclusive with `slugPrefix`) */
  slug: z.string().min(1).max(64).optional(),
  /** every stream whose slug starts with this (mutually exclusive with `slug`) */
  slugPrefix: z.string().min(1).max(64).optional(),
}).refine(
  (grant) => (grant.slug !== undefined) !== (grant.slugPrefix !== undefined),
  { message: 'a stream grant must have exactly one of "slug" or "slugPrefix"' },
);

export type ReactAppStreamGrant = z.infer<typeof ReactAppStreamGrantSchema>;

/**
 * Whether a stream slug is covered by a grant.
 *
 * The one matching rule, shared by the API middleware that authorizes an app tail and the
 * browser SDK's fail-fast check (which ports it), so the two cannot disagree about a near miss:
 * a prefix of `chat-` covers `chat-42` and not `chats`.
 */
export function streamGrantMatches(grant: { slug?: string | null; slugPrefix?: string | null }, streamSlug: string): boolean {
  if (typeof grant.slug === 'string') {
    return grant.slug === streamSlug;
  }
  if (typeof grant.slugPrefix === 'string' && grant.slugPrefix.length > 0) {
    return streamSlug.startsWith(grant.slugPrefix);
  }
  return false;
}

/** The options schema for the ReactAppTriggerActor (interpolated at build time). */
export const ReactAppTriggerActorOptionsSchema = z.object({
  /** interpolatable file overlay: asset-backed or templated files (wins on path collision) */
  files: z.array(ReactAppOptionsFileSchema).max(MAX_OPTIONS_FILES).nullish(),
  /** Phase II — named webhook-trigger endpoints consumed via `useEndpoint` (§15.4) */
  endpoints: z.array(ReactAppEndpointSchema).max(MAX_REACT_APP_ENDPOINTS).nullish(),
  /** workspace streams the app may tail live via `useStreamTail`; frozen into the build like endpoints */
  streams: z.array(ReactAppStreamGrantSchema).max(MAX_REACT_APP_STREAMS).nullish(),
  /** allowed domains for external scripts */
  allowedScriptDomains: z.array(z.string()).nullish(),
  /** allowed domains for external stylesheets */
  allowedStyleDomains: z.array(z.string()).nullish(),
  /** Enable unsafe-inline for scripts, bypassing hash verification */
  allowInlineScripts: z.boolean().nullish(),
  /** Enable unsafe-inline for styles, bypassing hash verification */
  allowInlineStyling: z.boolean().nullish(),
  /** Permissions-Policy directives to enable */
  allowedPermissions: z.array(PermissionsPolicyDirectiveZodSchema).nullish(),
  /** Add 'wasm-unsafe-eval' to script-src so WebAssembly can compile (not general JS eval) */
  allowWebAssembly: z.boolean().nullish(),
  /** Add `worker-src 'self' blob:` so the app can start inline (blob:) workers */
  allowBlobWorkers: z.boolean().nullish(),
});

export type ReactAppTriggerActorOptions = z.infer<typeof ReactAppTriggerActorOptionsSchema>;

/**
 * Drives the options form in the right-hand configuration panel. `files` is editable here as a
 * structured path/content array (and also, more richly, via the file tree in the full-page React-app
 * editor — both write the same `options.files`). `endpoints` is editable here as a structured array
 * of slug-based coordinates via a workspace → canvas → webhook-trigger picker (§15.6.6); save-time
 * validation catches bad references, tolerating `${{ }}` expressions (resolved at build, §15.3.5).
 */
export const ReactAppTriggerActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    files: {
      type: BIQJsonSchemaType.Array,
      title: 'Files',
      description: 'Asset-backed or templated files overlaid onto the project at build time (they win over the source tree on a path collision). Manage them here or via the file tree in the full-page editor.',
      items: {
        type: BIQJsonSchemaType.Object,
        properties: {
          path: {
            type: BIQJsonSchemaType.String,
            title: 'Path',
            description: 'Project-relative path, e.g. src/assets/logo.png or src/assets/hero.jpg. Import it from your source (e.g. import logo from \'./assets/logo.png\'); avoid public/.',
          },
          content: {
            type: BIQJsonSchemaType.String,
            title: 'Content',
            description: 'Reference an uploaded asset with ${{ assets["<key>"] }} (injected at build), or provide inline text.',
            ui: {
              options: {
                placeholder: '${{ assets["my-asset"] }}',
              },
            },
          },
        },
        required: ['path'],
      },
    },
    endpoints: {
      type: BIQJsonSchemaType.Array,
      title: 'Endpoints',
      description: 'Named webhook-trigger endpoints the app calls via useEndpoint("<name>"). Target a webhook-capable trigger — a WebhookTrigger, or a UniversalTrigger with its webhook source enabled (use authorizationLevel: "apps", or "appsAndApiKey" when external API callers share the endpoint) — on this canvas, or another canvas/workspace in the same org — leave workspace/canvas blank for this canvas. Coordinates are slugs. Endpoint changes take effect after the next Build.',
      items: {
        type: BIQJsonSchemaType.Object,
        properties: {
          name: {
            type: BIQJsonSchemaType.String,
            title: 'Name',
            description: 'The lookup key passed to useEndpoint(). Must be a valid identifier (letters, digits, underscore; not starting with a digit).',
            pattern: '^[a-zA-Z_][a-zA-Z0-9_]*$',
          },
          actorId: {
            type: BIQJsonSchemaType.String,
            title: 'Trigger',
            description: 'The target trigger — a WebhookTriggerActor, or a UniversalTriggerActor with its webhook source enabled.',
            // the picker also writes workspaceSlug / canvasSlug below; blank coordinates target the
            // app actor's own canvas. `capability` is what narrows UniversalTriggers to the ones
            // whose webhook source is on and that carry a routing key — a configuration rule the
            // actorTypes list alone cannot express.
            ui: {
              component: 'actorSelect',
              options: {
                actorTypes: [BIQActorType.WebhookTriggerActor, BIQActorType.UniversalTriggerActor],
                capability: 'webhookEndpointTarget',
                workspaceKey: 'workspaceSlug',
                canvasKey: 'canvasSlug',
                entityLabel: 'trigger',
              },
            },
          },
          workspaceSlug: {
            type: BIQJsonSchemaType.String,
            title: 'Workspace',
            description: 'Optional. The target workspace slug; blank = this app\'s workspace. Same org only.',
            ui: { options: { placeholder: 'blank = this workspace' } },
          },
          canvasSlug: {
            type: BIQJsonSchemaType.String,
            title: 'Canvas',
            description: 'Optional. The target canvas slug; blank = this app\'s canvas.',
            ui: { options: { placeholder: 'blank = this canvas' } },
          },
          description: {
            type: BIQJsonSchemaType.String,
            title: 'Description',
            description: 'Optional note about what this endpoint does.',
          },
        },
        required: ['name', 'actorId'],
      },
    },
    streams: {
      type: BIQJsonSchemaType.Array,
      title: 'Streams',
      description: 'Workspace streams the app may follow live with useStreamTail("<slug>"). Grant one stream by its slug, or every stream whose slug starts with a prefix (for streams a flow creates per session). Same workspace only. An app can only read the streams declared here; stream changes take effect after the next Build.',
      items: {
        type: BIQJsonSchemaType.Object,
        properties: {
          name: {
            type: BIQJsonSchemaType.String,
            title: 'Name',
            description: 'A label for this grant. Must be a valid identifier (letters, digits, underscore; not starting with a digit).',
            pattern: '^[a-zA-Z_][a-zA-Z0-9_]*$',
          },
          slug: {
            type: BIQJsonSchemaType.String,
            title: 'Stream slug',
            description: 'Exactly one stream, by its workspace slug. Leave blank when granting by prefix.',
            ui: { options: { placeholder: 'e.g. agent-activity' } },
          },
          slugPrefix: {
            type: BIQJsonSchemaType.String,
            title: 'Slug prefix',
            description: 'Every stream whose slug starts with this — for streams a flow creates per session. Leave blank when granting one slug.',
            ui: { options: { placeholder: 'e.g. chat-' } },
          },
          description: {
            type: BIQJsonSchemaType.String,
            title: 'Description',
            description: 'Optional note about what the app shows from this stream.',
          },
        },
        required: ['name'],
      },
    },
    allowInlineScripts: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Allow inline scripts',
      description: 'Uses \'unsafe-inline\' in the CSP script-src directive instead of hashed values. This is less secure but may be needed for dynamically generated scripts.',
      ui: {
        component: 'switch',
      },
    },
    allowInlineStyling: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Allow inline styling',
      description: 'Uses \'unsafe-inline\' in the CSP style-src directive instead of hashed values. This is less secure but may be needed for dynamically generated styles.',
      ui: {
        component: 'switch',
      },
    },
    allowWebAssembly: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Allow WebAssembly',
      description: 'Adds \'wasm-unsafe-eval\' to the CSP script-src directive so the app can compile WebAssembly modules. This does not allow JavaScript eval() or inline scripts. Takes effect after the app is rebuilt.',
      ui: {
        component: 'switch',
      },
    },
    allowBlobWorkers: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Allow blob workers',
      description: 'Adds a CSP worker-src \'self\' blob: directive so the app can start Web Workers from blob: URLs (e.g. Vite `?worker&inline`). Workers inherit the app\'s CSP, so a worker that compiles WebAssembly also needs Allow WebAssembly. Takes effect after the app is rebuilt.',
      ui: {
        component: 'switch',
      },
    },
    allowedScriptDomains: {
      type: BIQJsonSchemaType.Array,
      title: 'Allowed script domains',
      description: 'Allowed domains for external scripts loaded via CSP.',
      items: {
        type: BIQJsonSchemaType.String,
      },
    },
    allowedStyleDomains: {
      type: BIQJsonSchemaType.Array,
      title: 'Allowed style domains',
      description: 'Allowed domains for external stylesheets loaded via CSP.',
      items: {
        type: BIQJsonSchemaType.String,
      },
    },
    allowedPermissions: {
      type: BIQJsonSchemaType.Array,
      title: 'Allowed permissions',
      description: 'Permissions-Policy directives to enable for the iframe.',
      items: {
        type: BIQJsonSchemaType.String,
        enum: Object.values(PermissionsPolicyDirective),
      },
      uniqueItems: true,
    },
  },
  required: [],
};

export const ReactAppTriggerActorResultSchema = z.object({});

export type ReactAppTriggerActorResult = z.infer<typeof ReactAppTriggerActorResultSchema>;
```
