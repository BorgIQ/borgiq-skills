---
name: new-actor
description: Scaffold a starter BorgIQ actor inside a canvas bundle or as standalone workflow YAML, with a generated ULID, msgVar, and minimum required schema fields.
disable-model-invocation: true
argument-hint: "<ActorType> [Name] [bundle-dir]"
allowed-tools: Bash(borgiq*) Bash(mkdir*) Bash(ls*) Bash(test*)
---

# /new-actor — scaffold a BorgIQ actor

Generate a minimal valid actor in the current canvas bundle when one is present; otherwise generate standalone workflow YAML. Use it as a starting point and fill in actor-specific options from the relevant reference.

## Inputs

`$ARGUMENTS[0]` — actor type (e.g. `HttpRequestActor`, `DenoActor`, `PythonActor`, `AiActor`, `AiAgentActor`, `AgentHarnessActor`, `CollectionActor`, `RouterActor`, `MessageProcessorActor`, `WebhookTriggerActor`, `InterfaceTriggerActor`, `AppTriggerActor`, etc.).

`$ARGUMENTS[1]` (optional) — human-readable actor name. If omitted, derive one from the type.

If the actor type is missing or unrecognized, list the supported types from `${CLAUDE_SKILL_DIR}/../borgiq-builder/SKILL.md` (Task Actor Types and Trigger Actor Types tables) and ask which to use.

## Prerequisite

ID and msgVar generation ship as the `borgiq generate` command in the `@borgiq/cli` (no dependency install needed):

!`if command -v borgiq >/dev/null 2>&1; then echo "borgiq CLI found: $(borgiq --version)"; else echo "borgiq CLI not found. Install it with: npm install -g @borgiq/cli"; fi`

## Generate IDs

```bash
ACTOR_ID=$(borgiq generate id actor)
MSG_VAR=$(borgiq generate msgvar "$ARGUMENTS[1]")
```

## Detect bundle context

If an explicit target directory contains `canvas.yaml`, or the current directory contains `canvas.yaml`, use the bundle branch below. Otherwise use the standalone YAML branch.

!`test -f canvas.yaml && echo "BUNDLE:."; ls -d *.borgiq-canvas 2>/dev/null`

If multiple bundles are present and no target was specified, ask which one. For a bundle, confirm `borgiq bundle --help` succeeds; if not, tell the user to upgrade `@borgiq/cli`.

## Inside a canvas bundle

1. Read the bundle's generated `AGENTS.md` for the installed CLI's layout contract, then read `${CLAUDE_SKILL_DIR}/../borgiq-builder/references/cli/canvas-bundles.md` and the actor-specific reference.
2. Resolve the actor's exact category and kebab-case type folder from the bundle path registry in the bundle reference. Do not guess an unknown type.
3. Create `actors/<category>/<type-folder>/<ACTOR_ID>/actor.yaml` in **ExportedCanvasActor object shape**. Do not wrap it in `metadata`/`actors`, and do not include `edges`, `position`, or inline code when using `codeDir`.
4. For `DenoActor`, `DenoTestActor`, or `UniversalTriggerActor`, set `configuration.codeDir: code` and create `code/main.ts`. For `PythonActor`, create `code/main.py`. The entrypoint is required and must sit at the root of `code/`; add helper files and folders beside it as the actor grows, importing them relatively (`./lib/format.ts` in Deno, `from lib.format import format` in Python, where a package folder needs `__init__.py`). Do not create a file whose name the runtime reserves — see the reserved table in the bundle reference. For `AppTriggerActor`, create only its canonical `code/index.html`, `styles.css`, and `script.js` files that are needed.
5. Complete the three-edit rule in `canvas.yaml`: add the actor's `actors[]` index entry and exactly one `graph.nodes` entry. Add `graph.edges` wiring when requested; each `sourcePortId` must exist in the source actor's `sourcePorts`. Mint every new edge ID with `borgiq generate id edge`.
6. Search the whole bundle for any expressions or tool lists that must reference the new actor, then run:

```bash
borgiq bundle validate <bundle-dir> --strict
```

7. Fill in the actor-specific `configuration.options` using the reference read in step 1 — a structurally valid but empty actor only fails at server validation or first flowrun. Then apply the spoke handoff from [After scaffolding](#after-scaffolding) and re-run `bundle validate` after the options are complete.

Do not write `outputs/<msgVar>.yaml` in bundle context. Do not add a separate CommentActor as part of a single-actor scaffold unless the user requests documentation; that would be another actor requiring its own folder, index entry, and graph node.

## Standalone YAML (no bundle)

### Build the starter YAML

1. Read the actor-specific reference at `${CLAUDE_SKILL_DIR}/../borgiq-builder/references/<lowercased-actor-type>.md` to find:
   - The `version` field value
   - The minimum `configuration.options` required for the actor to be valid
   - Whether the actor needs `connection`, `connections`, or `credentials`
2. Build a YAML following the structure in the hub SKILL.md's **Common Actor Structure** section. Required top-level keys: `metadata`, `actors`. Inside the actor entry: `type`, `version`, `name`, `msgVar`, `description`, `isActive: true`, `continueOnError: false`, `sourcePorts: [{id: SPRTdefault}]`, `configuration` (with `inputs`, `options`, and `outputs` as relevant), `schemas.inputs` (start with `type: any` per generation rule #12), `id`, `position: {x: 0, y: 0}`, `edges: {}`.

   For `DenoActor`, `DenoTestActor`, `UniversalTriggerActor`, and `PythonActor`, the source goes in `configuration.codeDir` — a list of `{path, content}` files, sibling of `options`, containing the required entrypoint `main.ts` (`main.py` for Python):

   ```yaml
   configuration:
     options: {}
     codeDir:
       - path: main.ts
         content: |
           import type { Request, Response } from "@borgiq/actors";

           export default async function receive(req: Request): Promise<Response> {
             return { results: req.inputs };
           }
   ```
3. Include a **CommentActor** at the top with setup notes, prerequisites, and a brief spec for what this actor does. Position it with negative `y` (`y: -300`) so it renders above the actor in the canvas (per hub generation rule #19).

### Write the file

Place the YAML under `outputs/` in the working directory:

```bash
mkdir -p outputs
# Write the YAML to outputs/<msg-var>.yaml
```

Filename = `outputs/<msgVar>.yaml` (the generator already gives you a unique, sluggable name).

### After scaffolding

Run `/borgiq-builder:validate` against the new YAML to confirm the scaffold is well-formed. Then fill in the actor-specific `configuration.options` using the reference file you read above.

If the actor type is part of a domain a spoke covers, also point the user at the spoke (applies to both the bundle and standalone branches):
- Interface / form actors → `borgiq-form-builder`
- ReactAppTriggerActor (and legacy raw-HTML AppTriggerActor) → `borgiq-react-app-builder`
- AiActor / AiAgentActor / AgentHarnessActor / McpServerActor → `borgiq-agent-builder`
- Anything with an output schema → `borgiq-json-schema-builder`
