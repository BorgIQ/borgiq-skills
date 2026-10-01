---
name: new-actor
description: Scaffold a starter BorgIQ actor inside a canvas bundle or as standalone workflow YAML, with a generated ULID, msgVar, and minimum required schema fields.
compatibility: Requires the borgiq-builder skill, a shell and the borgiq CLI (@borgiq/cli), logged in to read a type's defaults.
disable-model-invocation: true
argument-hint: "<ActorType> [Name] [bundle-dir]"
allowed-tools: Bash(borgiq*) Bash(mkdir*) Bash(ls*) Bash(test*)
---

# Scaffold a BorgIQ actor

Requires the `borgiq-builder` skill: the links below go into its `references/` folder.

The user names the actor type (`HttpRequestActor`, `DenoActor`, `WebhookTriggerActor`, …), and optionally an actor
name (else derive one from the type) and a bundle directory. For a missing or unknown type, list the types
(`borgiq actors list`, or the hub's [Task](../borgiq-builder/SKILL.md#task-actor-types) and
[Trigger Actor Types](../borgiq-builder/SKILL.md#trigger-actor-types)) and ask.

CLI version (Claude Code fills this in; otherwise run it yourself): !`borgiq --version 2>&1 || echo "CLI_MISSING"`

If it printed `CLI_MISSING` or no version, ask the user to install it: `npm install -g @borgiq/cli`.

## IDs and the type's schema

```bash
borgiq generate id actor
borgiq generate msgvar "<actor name>"
borgiq actors schema <ActorType> --json   # needs a login; an unknown type is a 404
```

In the schema, `defaultOptions` is the starting `configuration.options`; `sourcePorts.fixedPorts`, `code.entrypoint`,
`supportsConnection` and `optionsSchema` give the ports, entrypoint, connection support and every option.
The actor's reference is `../borgiq-builder/references/<kebab-case-actor-type>.md` (`HttpRequestActor` →
[http-request-actor.md](../borgiq-builder/references/http-request-actor.md)).

## Bundle or standalone

Use the bundle branch when the target or current directory contains `canvas.yaml`; if several, ask.
Candidates (Claude Code fills this in; otherwise run it yourself):

!`find . -maxdepth 2 \( -name canvas.yaml -o -name '*.borgiq-canvas' \) -not -path '*/.*' | head -20`

A bundle needs `borgiq help bundle` to succeed; otherwise the user upgrades `@borgiq/cli`.

## Inside a canvas bundle

1. Read the bundle's `README.md` (its conventions; add the new actor if it lists them), its `AGENTS.md`
   (the CLI's layout contract), [canvas-bundles.md](../borgiq-builder/references/cli/canvas-bundles.md) and the
   actor's reference.
2. Create `actors/<category>/<type-folder>/<ACTOR_ID>/actor.yaml`, folders from the
   [registry](../borgiq-builder/references/cli/canvas-bundles.md#folder-layout-and-ownership) (never guess one), in the
   object shape: no `metadata`/`actors` wrapper, no `edges`, `position` or inline code.
3. DenoActor, DenoTestActor, UniversalTriggerActor: `configuration.codeDir: code` and `code/main.ts`; PythonActor:
   `code/main.py`; AppTriggerActor: only the `code/index.html`, `styles.css`, `script.js` it needs. Helpers sit beside
   the entrypoint, imported relatively, never under a
   [reserved name](../borgiq-builder/references/cli/canvas-bundles.md#code-actor-project-trees).
4. In `canvas.yaml`, apply the
   [three-edit rule](../borgiq-builder/references/cli/canvas-bundles.md#add-and-remove-actors-the-three-edit-rule): an
   `actors[]` entry, exactly one `graph.nodes` entry, and `graph.edges` if requested (each `sourcePortId` declared by
   its source actor, each ID from `borgiq generate id edge`).
5. Update any expression or tool list that must name the new actor; run `borgiq bundle validate <bundle-dir> --strict`.
6. Fill in `configuration.options` from the reference and schema (an empty actor fails on the server or at its first
   run), apply [After scaffolding](#after-scaffolding), and validate again.

No `outputs/` file in a bundle, and no CommentActor unless the user asks.

## Standalone YAML (no bundle)

1. From the schema and the reference, take the `version`, the required options, and whether it needs a `connection`
   or `credentials`.
2. Write one `metadata` + `actors` document shaped like the hub's
   [Common Actor Structure](../borgiq-builder/SKILL.md#common-actor-structure), with `isActive: true`,
   `continueOnError: false`, `sourcePorts: [{id: SPRTdefault}]`, `schemas.inputs` starting as `type: any` (the
   object-schema rule in [Generation Instructions](../borgiq-builder/SKILL.md#generation-instructions)),
   `position: {x: 0, y: 0}` and `edges: {}`. Deno-family and Python actors carry their source in
   `configuration.codeDir`, beside `options`, a list of `{path, content}` files including the entrypoint:

   ```yaml
   configuration:
     options: {}
     codeDir:
       - path: main.ts   # main.py for Python
         content: |
           import type { Request, Response } from "@borgiq/actors";

           export default async function receive(req: Request): Promise<Response> {
             return { results: req.inputs };
           }
   ```
3. Add a CommentActor only if the user asks; it belongs above a new multi-actor workflow (`y: -300`).
4. Save it as `outputs/<msgVar>.yaml` (`mkdir -p outputs`).

## After scaffolding

Validate with the `validate` skill (`/borgiq-builder:validate` in Claude Code) and fill in the options. Point the
user at the domain's skill: `borgiq-form-builder` (interface and form actors), `borgiq-react-app-builder`
(ReactAppTriggerActor, legacy AppTriggerActor), `borgiq-agent-builder` (AI actors, McpServerActor),
`borgiq-json-schema-builder` (any output schema).
