---
name: validate
description: Validate a BorgIQ canvas bundle directory or workflow YAML against bundle structure, actor schemas, IDs, and edges. Run before deploy to catch local violations with artifact-specific diagnostics.
compatibility: Requires the borgiq-builder skill, a shell and the borgiq CLI (npm install -g @borgiq/cli). Offline; no login needed.
disable-model-invocation: true
argument-hint: "[path/to/bundle-or-workflow.yaml] [--strict]"
allowed-tools: Bash(borgiq*) Bash(ls*) Bash(test*)
---

# Validate a BorgIQ bundle or workflow

Requires the `borgiq-builder` skill: the links below go into its `references/` folder.

CLI version (Claude Code fills this in; otherwise run it yourself): !`borgiq --version 2>&1 || echo "CLI_MISSING"`

If it printed `CLI_MISSING` or no version, ask the user to install it: `npm install -g @borgiq/cli`.

## Pick the artifact

Use the path the user gave, if any: a directory containing `canvas.yaml` is a bundle; a `.yaml`/`.yml` file is a
direct document. Otherwise look for candidates (Claude Code fills this in; otherwise run it yourself):

!`find . -maxdepth 2 \( -name canvas.yaml -o -name '*.borgiq-canvas' -o -name '*.yaml' -o -name '*.yml' \) -not -path '*/.*' | head -20`

If there are several, ask which. Prefer a bundle that is the canvas's maintained local copy.

## Validate

**Bundle.** `borgiq help bundle` must succeed (otherwise upgrade the CLI), then:

```bash
borgiq bundle validate <dir> --strict   # --strict makes warnings fatal: use it before deploying
```

Each finding names a bundle file (`canvas.yaml`, an `actor.yaml`, a `code/` file): fix it and rerun. Fixes, `code/`
errors included: [canvas-bundles.md → Troubleshooting](../borgiq-builder/references/cli/canvas-bundles.md#troubleshooting).

**Direct document** (`metadata` + `actors`): `borgiq validate <file>`. Errors name an actor ID, field path or line.
Schema errors: the actor type's reference, `<kebab-case-actor-type>.md` (`HttpRequestActor` →
[http-request-actor.md](../borgiq-builder/references/http-request-actor.md)); ID and edge errors:
[edges-and-positioning.md](../borgiq-builder/references/edges-and-positioning.md). Fix the YAML and rerun.
`borgiq validate <file> --post-process --in-place` is optional cleanup after a pass: it validates nothing and renames
no msgVar or ID ([what it changes](../borgiq-builder/references/validation.md#validators-per-mode)).

## After validation passes

Neither validator checks workspace connections, assets or cross-canvas references: use the `deploy` skill
(`/borgiq-builder:deploy` in Claude Code), which validates on the server after pushing, or run
`borgiq canvases validate <canvas> --json` on an existing canvas.
