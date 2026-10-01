# actorSchemas/codeDir

Generated from the platform's runtime types. Do not edit.

The generic, actor-type-independent `configuration.codeDir` model: an array of `{ path, content }` source files forming a project tree, never interpolated.

## actorSchemas/codeDir

**Source:** `actorSchemas/codeDir.ts`

```typescript
import { z } from 'zod';

/**
 * The generic, actor-type-independent `configuration.codeDir` model: an array of
 * `{ path, content }` source files forming a project tree, never interpolated.
 *
 * IMPORTANT — this module must stay a dependency-free LEAF. `schemas/runtime.ts` imports the
 * generic schema from here, and `actorSchemas/trigger/reactApp.ts` re-exports it; importing
 * anything but `zod` risks the same load-order cycle documented at the top of `reactApp.ts`.
 */

/** Maximum number of files allowed in `configuration.codeDir`. */
export const MAX_CODE_DIR_FILES = 200;
/** Maximum total UTF-8 byte size of all `configuration.codeDir` file contents (1 MiB). */
export const MAX_CODE_DIR_TOTAL_BYTES = 1024 * 1024;

/**
 * Normalize a project-relative path to '/'-separated form and validate it is safe.
 * Returns the normalized path, or an error string describing the first violation.
 * Rules: reject absolute paths, '..' segments, backslashes, empty segments, and a trailing slash.
 *
 * Performs no trimming and no separator rewriting, so `segments.join('/')` is an identity
 * transform for any accepted input — a valid `rawPath` is returned verbatim.
 */
export function normalizeCodePath(rawPath: string): { path: string } | { error: string } {
  if (rawPath.includes('\\')) {
    return { error: `path '${rawPath}' must use '/' separators, not backslashes` };
  }
  if (rawPath.startsWith('/')) {
    return { error: `path '${rawPath}' must be relative to the project root (no leading '/')` };
  }
  // Guard against Windows drive-letter absolute paths (e.g. C:/...).
  if (/^[a-zA-Z]:/.test(rawPath)) {
    return { error: `path '${rawPath}' must be relative to the project root` };
  }
  const segments = rawPath.split('/');
  for (const segment of segments) {
    if (segment === '') {
      return { error: `path '${rawPath}' contains an empty segment (leading, trailing, or doubled '/')` };
    }
    if (segment === '.' || segment === '..') {
      return { error: `path '${rawPath}' contains a '.' or '..' segment` };
    }
  }
  return { path: segments.join('/') };
}

/** A single source file in the never-interpolated project tree. */
export const CodeFileSchema = z.object({
  /** path relative to the project root; '/' separates nested folders, e.g. 'lib/util.ts' */
  path: z.string().min(1).max(255),
  /** raw file content, UTF-8 text */
  content: z.string(),
});

export type CodeFile = z.infer<typeof CodeFileSchema>;

/**
 * The entrypoint each code actor type's runtime executes: the one path in `configuration.codeDir`
 * that must exist, and that exports the handler (`main.ts`) or defines `receive` (`main.py`).
 *
 * **This is the single source of truth for those filenames.** The per-type `codeDir` schemas below,
 * the actor-schema metadata the API serves to the web editor and the CLI, and the lambda runtime's
 * per-type validation all resolve the name from here — so renaming an entrypoint is a one-line edit
 * in this module rather than a sweep across the platform and the lambda runtime. Kept as
 * four separate constants rather than one shared value because the name is a property of each
 * type's runtime: they coincide today, and nothing should assume they always will.
 *
 * A rename is NOT just this edit. It is a breaking change that also needs: a data migration (every
 * migrated `codeDir` row names the old path), the `actors/*.yaml` seed templates, the placeholder
 * file the Deno bootstrap ships under this name, and the static `import` specifiers in the
 * bootstrap's `handler.ts` / `handler.py`. Test fixtures deliberately keep the literal so a rename
 * fails loudly and surfaces that list, rather than going green while running actors break.
 */
export const DENO_ACTOR_ENTRYPOINT = 'main.ts';
export const DENO_TEST_ACTOR_ENTRYPOINT = 'main.ts';
export const UNIVERSAL_TRIGGER_ACTOR_ENTRYPOINT = 'main.ts';
export const PYTHON_ACTOR_ENTRYPOINT = 'main.py';

/**
 * Paths a user's `codeDir` may not claim, because the runtime owns them.
 *
 * Write ordering (user files first, borgiq files last) already makes borgiq files win any
 * *overwrite* collision. These lists close the two cases ordering cannot fix: config
 * **discovery precedence** (Deno prefers a user `deno.json` over the bootstrap's `deno.jsonc`)
 * and Python **module shadowing** (the work-dir root wins on `sys.path` over `.borgiq/`).
 */
export interface ReservedPathSet {
  /** whole paths that are reserved, compared case-insensitively */
  exact: readonly string[];
  /** directory prefixes, each written WITH its trailing '/', matched against `path + '/'` */
  prefixes: readonly string[];
}

/**
 * Return the reserved entry a normalized path collides with, or `null` when it is free.
 *
 * Comparison is case-insensitive, matching the bundle compiler's case-fold collision rule:
 * on a case-insensitive filesystem `Server.ts` and `server.ts` are the same file. Prefixes are
 * tested against `path + '/'`, so a prefix of `shared/` rejects both `shared/api.ts` and a file
 * literally named `shared`.
 */
export function matchReservedPath(normalizedPath: string, reserved: ReservedPathSet): string | null {
  const lowered = normalizedPath.toLowerCase();
  for (const exact of reserved.exact) {
    if (lowered === exact.toLowerCase()) return exact;
  }
  const loweredAsDir = `${lowered}/`;
  for (const prefix of reserved.prefixes) {
    if (loweredAsDir.startsWith(prefix.toLowerCase())) return prefix;
  }
  return null;
}

/** Reserved by the Deno bootstrap variant — shared by DenoActor, DenoTestActor and UniversalTriggerActor. */
export const DENO_RESERVED_PATHS: ReservedPathSet = {
  exact: [
    // bootstrap entry chain; `actor.ts` is the @borgiq/actors SDK barrel mapped in deno.jsonc
    'server.ts',
    'handler.ts',
    'actor.ts',
    // bootstrap-owned test harness (universal-trigger variant)
    'main_test.ts',
    // bootstrap config + lockfile
    'deno.jsonc',
    'deno.lock',
    // reserved even though the bootstrap ships neither: Deno config discovery would prefer a user
    // `deno.json` over the bootstrap's `deno.jsonc`, and a `package.json` changes resolution.
    'deno.json',
    'package.json',
  ],
  prefixes: [
    // the materialized shared kernel (dereferenced symlink)
    'shared/',
    // resolution surface
    'node_modules/',
    // a Deno Test actor's own dependency cache, embedded in its work dir by the runtime build (the
    // parallel of Python's `.venv/`); reserved for the whole family so the name cannot be claimed
    '.borgiq-deno-dir/',
  ],
};

/** Reserved by the Python runtime. Most of these are sys.path shadowing risks, not overwrites. */
export const PYTHON_RESERVED_PATHS: ReservedPathSet = {
  exact: [
    // runtime-generated (dependencies come from configuration.options.dependencies)
    'pyproject.toml',
    '.python-version',
    'uv.lock',
    // the work-dir root wins on sys.path over `.borgiq/`, so a root file with a runtime module's
    // name shadows it without overwriting anything
    'server.py',
    'handler.py',
    'borgiq.py',
  ],
  prefixes: [
    // the copied runtime (server.py, handler.py, borgiq/)
    '.borgiq/',
    // uv-managed environment
    '.venv/',
    // shadows the borgiq SDK package
    'borgiq/',
  ],
};

export interface CodeDirSchemaOptions {
  /** exactly one entry must carry this path, e.g. 'main.ts' / 'main.py'. Omitted ⇒ no entrypoint rule. */
  requiredEntrypoint?: string;
  /** paths the runtime owns; rejected case-insensitively. Omitted ⇒ no reserved-path rule. */
  reservedPaths?: ReservedPathSet;
}

/**
 * Build a `codeDir` array schema. The shape rules (safe paths, no duplicates, file-count and
 * total-byte caps) always apply; the entrypoint and reserved-path rules are opt-in because they
 * are properties of a specific actor type's runtime, not of the wire format.
 */
export function makeCodeDirSchema(opts: CodeDirSchemaOptions = {}): z.ZodType<CodeFile[]> {
  const { requiredEntrypoint, reservedPaths } = opts;
  return z.array(CodeFileSchema)
    .max(MAX_CODE_DIR_FILES, `codeDir may contain at most ${MAX_CODE_DIR_FILES} files`)
    .superRefine((files, ctx) => {
      const seen = new Set<string>();
      const entrypointIndexes: number[] = [];
      let totalBytes = 0;
      // TextEncoder (not Buffer) so this schema stays portable between Node and the Deno runtime mirror.
      const encoder = new TextEncoder();
      files.forEach((file, index) => {
        const result = normalizeCodePath(file.path);
        if ('error' in result) {
          ctx.addIssue({ code: z.ZodIssueCode.custom, message: result.error, path: [index, 'path'] });
          return;
        }
        if (seen.has(result.path)) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: `duplicate path '${result.path}' in codeDir`,
            path: [index, 'path'],
          });
        }
        seen.add(result.path);
        if (requiredEntrypoint !== undefined && result.path === requiredEntrypoint) {
          entrypointIndexes.push(index);
        }
        if (reservedPaths) {
          const reserved = matchReservedPath(result.path, reservedPaths);
          if (reserved !== null) {
            ctx.addIssue({
              code: z.ZodIssueCode.custom,
              message: `path '${result.path}' is reserved by the runtime ('${reserved}') and cannot be used`,
              path: [index, 'path'],
            });
          }
        }
        totalBytes += encoder.encode(file.content).length;
      });
      if (totalBytes > MAX_CODE_DIR_TOTAL_BYTES) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: `codeDir total content size ${totalBytes} exceeds the ${MAX_CODE_DIR_TOTAL_BYTES}-byte limit`,
          path: [],
        });
      }
      if (requiredEntrypoint !== undefined) {
        if (entrypointIndexes.length === 0) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: `codeDir must contain an entrypoint file named '${requiredEntrypoint}'`,
            path: [],
          });
        }
        // A duplicate entrypoint is already flagged by the duplicate-path check, but flag the
        // extra entries too so the error points at the offending file, not just the array.
        entrypointIndexes.slice(1).forEach((index) => {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: `codeDir must contain exactly one entrypoint file named '${requiredEntrypoint}'`,
            path: [index, 'path'],
          });
        });
      }
    });
}

/**
 * The generic, type-independent `codeDir` shape used by the shared transport schemas. Per-type
 * entrypoint and reserved-path rules are deliberately NOT wire-level — they run where actor-type
 * context exists (save-time warnings, canvas validation, and the runtime).
 */
export const CodeDirSchema = makeCodeDirSchema();

export type CodeDir = z.infer<typeof CodeDirSchema>;
```
