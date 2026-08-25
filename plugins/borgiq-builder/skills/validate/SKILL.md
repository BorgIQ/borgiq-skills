---
name: validate
description: Validate a BorgIQ canvas bundle directory or workflow YAML against bundle structure, actor schemas, IDs, and edges. Run before deploy to catch local violations with artifact-specific diagnostics.
disable-model-invocation: true
argument-hint: "[path/to/bundle-or-workflow.yaml] [--strict]"
allowed-tools: Bash(borgiq*) Bash(ls*) Bash(test*)
---

# /validate — BorgIQ workflow validator

Run the correct offline validator for a canvas bundle or direct workflow document. Report structure/schema errors, missing IDs, and dangling edges *before* deployment.

## Prerequisite

Both validators ship in `@borgiq/cli`. Confirm the CLI is installed (no dependency install needed):

!`if command -v borgiq >/dev/null 2>&1; then echo "borgiq CLI found: $(borgiq --version)"; else echo "borgiq CLI not found. Install it with: npm install -g @borgiq/cli"; fi`

## Pick the artifact

Classify the explicit path first: a directory containing `canvas.yaml` is a bundle; a `.yaml`/`.yml` path is a direct document. Otherwise look for a bare `./canvas.yaml`, `*.borgiq-canvas/` directories, and workflow YAMLs in the current directory and `./outputs/`.

!`test -f canvas.yaml && echo "BUNDLE:."; ls -d *.borgiq-canvas 2>/dev/null; ls outputs/*.yaml outputs/*.yml *.yaml *.yml 2>/dev/null | head -20`

If several candidates exist, ask which one to validate. Prefer the bundle when it is the maintained local copy of the canvas.

## Validate

For a bundle directory, verify the capability and run bundle validation:

```bash
borgiq bundle --help >/dev/null 2>&1 || echo "upgrade: npm install -g @borgiq/cli"
borgiq bundle validate <dir>
# Add --strict when requested or before deployment to make warnings fatal.
```

Bundle validation is offline and reports errors/warnings against bundle-relative paths such as `canvas.yaml`, `actors/.../actor.yaml`, or `actors/.../code/main.ts`. Fix the named file and rerun. Consult `${CLAUDE_SKILL_DIR}/../borgiq-builder/references/cli/canvas-bundles.md` for the three-edit and `codeDir` contracts.

Code actors (Deno, Deno Test, Universal Trigger, Python) hold a project tree under `code/`, so validation additionally reports a missing entrypoint (`code/main.ts`, or `code/main.py` for Python), a filename reserved by the BorgIQ runtime, and an actor that carries both inline `configuration.code` and `code/` files. [Canvas Bundles → Code actor `code/` errors](../borgiq-builder/references/cli/canvas-bundles.md#code-actor-code-errors) lists each message with its fix; a bundle pulled before multi-file support needs its `code/mod.ts` renamed to `code/main.ts`.

For a direct YAML/YML document:

```bash
borgiq validate <file>
```

If direct validation emits errors:

1. Read each error literally — they reference actor IDs, field paths, and line numbers.
2. For schema errors, cross-reference the relevant actor doc in `${CLAUDE_SKILL_DIR}/../borgiq-builder/references/<actor-type>.md`.
3. For ID/edge errors, see `${CLAUDE_SKILL_DIR}/../borgiq-builder/references/edges-and-positioning.md`.
4. Fix the YAML directly. Re-run validate.

If direct validation emits a post-process suggestion (renamed msgVar, regenerated ID), apply it:

```bash
borgiq validate <file> --post-process --in-place
```

## After validation passes

Neither offline validator catches missing workspace connections/assets or invalid cross-canvas references. For those, use `/borgiq-builder:deploy` (which runs `borgiq canvases validate` server-side after deployment) or run `borgiq canvases validate <canvasSlugOrId> --json` against an existing canvas.
