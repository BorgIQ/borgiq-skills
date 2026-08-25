# Editing Existing Workflows

A deployed canvas is edited through its bundle: pull it once, edit the files, and push. Use the direct document workflow only when a bundle is not possible — no shell/filesystem access, a CLI without `borgiq bundle`, or a one-off patch to a canvas nobody maintains locally.

## Preferred: editing a deployed canvas via bundle

Pull once, keep the bundle in git, and synchronize from the files:

```bash
borgiq bundle --help >/dev/null 2>&1 || echo "upgrade: npm install -g @borgiq/cli"
borgiq bundle pull <canvasSlugOrId> ./my-flow.borgiq-canvas
git init ./my-flow.borgiq-canvas
git -C ./my-flow.borgiq-canvas add .
git -C ./my-flow.borgiq-canvas commit -m "chore: pull BorgIQ canvas baseline"

# Edit actor.yaml, code/*, and canvas.yaml.
borgiq bundle validate ./my-flow.borgiq-canvas --strict
borgiq bundle push ./my-flow.borgiq-canvas --dry-run
git -C ./my-flow.borgiq-canvas add .
git -C ./my-flow.borgiq-canvas commit -m "fix: update BorgIQ workflow"
borgiq bundle push ./my-flow.borgiq-canvas   # add --auto-layout when actors were added, removed, or rewired
```

Commit after init/pull and before each push. After push, review and commit any refreshed actor/version metadata from the implicit pull. `pull` applies server-only changes, preserves pure local edits, and **aborts, writing nothing**, when an actor has both local and server changes; resolve those deliberately with `pull --replace` (server wins) or `push --force-local` (local wins), and use git to recover local versions after a `--replace`. Do not patch the same canvas out of band with `canvas-actors batch`; edit and push the bundle so the local copy stays authoritative.

Read [Canvas Bundles](cli/canvas-bundles.md) for the complete layout, sync, and conflict contract.

### Rename an actor in a bundle

When changing an actor's `name`, also regenerate its `msgVar`:

```bash
borgiq generate msgvar "New Actor Name Here"
```

Then:

1. Update `name` and `msgVar` in the actor's `actor.yaml`.
2. Update the corresponding `name` in `canvas.yaml` `actors[]`.
3. Search the **whole bundle**, because references can live in other actors' `actor.yaml` files and in native `code/*` files:

   ```bash
   rg -n 'msg\.old_msg_var|old_msg_var' ./my-flow.borgiq-canvas
   ```

4. Update every `msg.<old_msgVar>` expression, downstream input, tool reference, and interface display label.
5. Validate the bundle, review the git diff, and push.

### Add or remove an actor in a bundle

Adding an actor follows the three-edit rule:

1. Mint an ID with `borgiq generate id actor` and create `actors/<category>/<type>/<id>/actor.yaml` plus its `code/` entrypoint (`main.ts` / `main.py`, or App's three fixed files) when the type carries code.
2. Add its `actors[]` index entry in `canvas.yaml`.
3. Add exactly one `graph.nodes` position entry in `canvas.yaml`.
4. Wire it in `graph.edges`; mint edge IDs with `borgiq generate id edge` and use a `sourcePortId` declared by the source actor.

Removing an actor is the inverse: delete its folder, index entry, node, and all inbound/outbound edges. Search the bundle for its actor ID, msgVar, and `msg.<msgVar>` before validating.

### Edit code in a bundle

Edit the files under the actor's `code/` directory, never inline in `actor.yaml`; keep the marker `configuration.codeDir: code`. Update `configuration.inputs`, schemas, and downstream expressions if the code contract changes.

Deno, Deno Test, Universal Trigger, and Python actors hold a project tree there — the required entrypoint (`main.ts`, or `main.py` for Python) at the root of `code/`, plus whatever helper files and folders you add:

- **Split a growing entrypoint** by adding files beside it and importing them relatively: `import { format } from './lib/format.ts'` in Deno (extension included), `from lib.format import format` in Python (a package folder needs `__init__.py`). Imports may not leave `code/`.
- **Deleting a file from the tree removes it from the actor** on the next push — that is how you retire a helper. Nothing stale is left behind to be imported.
- **Do not rename or delete the entrypoint.** `bundle validate` rejects a tree without it; if the bundle predates multi-file support it has `code/mod.ts` (or `mod.py`), which you rename to `main.ts` (`main.py`) once.
- **Reserved filenames** (`server.ts`, `handler.ts`, `actor.ts`, `deno.json`, `shared/…`, and the Python equivalents) are rejected — see [Canvas Bundles → Code actor project trees](cli/canvas-bundles.md#code-actor-project-trees) for the full lists, size caps, and version requirements.

App actors keep their three fixed files (`index.html`, `styles.css`, `script.js`); a React App actor's `code/` is a whole Vite project.

## Semantic rules for any edit (bundle or direct)

These are platform semantics that no offline validator catches — apply them whether you are editing bundle files or a direct document:

1. **CommentActor** — if the workflow has a CommentActor documenting setup or behavior, update it to match the change.
2. **Model changes** — for AiActor, changing `model` also requires updating `maxTokens`; AiAgentActor has **no** `maxTokens` field — do not add one. Update the actor name/description if they mention the model.
3. **Changed inputs propagate** — update code access/destructuring, `schemas`, and every downstream consumer.
4. **Changed outputs propagate** — update return/output configuration, `schemas`, and all downstream `msg.<msgVar>.*` references.

## Direct document workflow

Use this subsection only when no local bundle is the source of truth.

### Editing checklist

1. Read the existing workflow document and understand actor relationships.
2. Make the required configuration, model, expression, code, or graph changes.
3. Apply the semantic rules above (CommentActor, model coupling, input/output propagation). Add a CommentActor above the workflow if appropriate and absent.
4. Run `borgiq validate <file>`.
5. Run `borgiq validate <file> --post-process -i` after fixing validation errors.
6. Review the resulting diff before deployment.

### Rename an actor in a direct document

When changing an actor's `name`, regenerate its `msgVar` and update all references:

1. Update the actor's `name`.
2. Generate and set the new `msgVar` with `borgiq generate msgvar "New Actor Name"`.
3. Replace every `msg.<old_msgVar>` expression.
4. Update downstream inputs and InterfaceActor display labels.
5. Validate and post-process the document.

Example:

```yaml
# Before
name: GPT-4o Response
msgVar: gpt4o_response
# Reference: ${{ msg.gpt4o_response.body }}

# After `borgiq generate msgvar "GPT-5.2 Response"`
name: GPT-5.2 Response
msgVar: gpt52_response
# Reference: ${{ msg.gpt52_response.body }}
```

### Update DenoActor/PythonActor code in a document

1. Update `configuration.inputs` when input names change.
2. Edit the entry in `configuration.codeDir` whose `path` is the file you mean — the entrypoint is `main.ts` (`main.py` for Python). Add an entry to introduce a helper file; drop an entry to retire one.
3. Ensure variable access/destructuring matches the inputs.
4. Update schemas, returned output, and downstream consumers when the result shape changes.
5. Validate. `borgiq validate` checks that `codeDir` is a list of `{path, content}` files containing the entrypoint; the BorgIQ API is the authority on the rest.

A document written before multi-file support carries a single `configuration.code` string instead. It still runs, and the platform converts it; to edit it as a file list, replace the field:

```yaml
# Before
configuration:
  options: {}
  code: |
    import type { Request, Response } from "@borgiq/actors";
    export default async function receive(req: Request): Promise<Response> { … }

# After
configuration:
  options: {}
  codeDir:
    - path: main.ts
      content: |
        import type { Request, Response } from "@borgiq/actors";
        export default async function receive(req: Request): Promise<Response> { … }
```

Never send both fields for the same actor.

### Common direct-document changes

The semantic rules above cover model, input, and output changes. Document-specific mechanics:

| Change | Actions required |
|---|---|
| Rename actor | Change `name`, regenerate `msgVar`, update every `msg.<msgVar>` reference. |
| Add actor | Generate actor/msgVar/edge IDs, add the actor, source-owned edges, and position. |
| Remove actor | Delete the actor and its inbound/outbound edges; update downstream references. |

### Validate after direct edits

```bash
borgiq validate workflow.yaml
borgiq validate workflow.yaml --post-process -i
```
