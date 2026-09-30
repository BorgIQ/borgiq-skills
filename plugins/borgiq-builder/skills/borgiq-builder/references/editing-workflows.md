# Editing Existing Workflows

How to change a canvas that already exists: in its bundle (the default), or in a direct document when a bundle is not
possible. It covers renaming actors, the platform rules no validator catches, and code edits. Bundle mechanics
(pull, push, conflicts, the three-edit rule, code trees) are in [canvas-bundles.md](cli/canvas-bundles.md).

## Preferred: editing a deployed canvas via bundle

Pull the canvas once (`borgiq bundle pull <canvas> <dir>`), commit the baseline, edit the files, validate, and push:
the [lifecycle](cli/canvas-bundles.md#lifecycle-commands) and the
[conflict rules](cli/canvas-bundles.md#incremental-sync-and-conflicts) are in canvas-bundles.md. Read the bundle's
`README.md` first and update it when you change what it describes. Never patch the same canvas out of band with
`canvas-actors batch`: the bundle stays the source of truth.

### Rename an actor in a bundle

1. `borgiq generate msgvar "New Actor Name"`; set `name` and `msgVar` in the actor's `actor.yaml`.
2. Update its `name` in `canvas.yaml` `actors[]`.
3. Search the **whole bundle**: references live in other actors' `actor.yaml` files and in native `code/*` files.

   ```bash
   rg -n 'msg\.old_msg_var|old_msg_var' ./my-flow.borgiq-canvas
   ```

4. Update every `msg.<old_msgVar>` expression, downstream input, tool reference and interface display label.
5. Validate the bundle, review the git diff, and push.

### Add or remove an actor in a bundle

Follow the [three-edit rule](cli/canvas-bundles.md#add-and-remove-actors-the-three-edit-rule): an actor folder, an
`actors[]` entry and one `graph.nodes` entry, then `graph.edges`. Removing is the inverse, plus every inbound and
outbound edge; search the bundle for the actor's ID, msgVar and `msg.<msgVar>` before validating.

### Edit code in a bundle

Edit the files under the actor's `code/`, never inline in `actor.yaml`, and keep the marker
`configuration.codeDir: code`. When the code's contract changes, update `configuration.inputs`, the schemas and the
downstream expressions too.

- **Split a growing entrypoint** into files beside it, imported relatively (rules:
  [code actor project trees](cli/canvas-bundles.md#code-actor-project-trees)).
- **Deleting a file removes it from the actor** on the next push; that is how you retire a helper.
- **Never rename or delete the entrypoint** (`main.ts`, or `main.py`). A bundle that predates multi-file support has
  `code/mod.ts` (`mod.py`): rename it once.

App actors keep their three fixed files (`index.html`, `styles.css`, `script.js`); a React App actor's `code/` is a
whole Vite project.

## Semantic rules for any edit (bundle or direct)

No offline validator catches these platform rules; apply them in bundle files and direct documents alike:

1. **CommentActor**: if the workflow has one documenting its setup or behavior, update it to match the change.
2. **Model changes**: changing an AiActor's `model` also means updating `maxTokens`. AiAgentActor has **no**
   `maxTokens` field; do not add one. Update the actor's name and description if they mention the model.
3. **Changed inputs propagate** to the code's access and destructuring, the `schemas`, and every downstream consumer.
4. **Changed outputs propagate** to the returned or `outputs` configuration, the `schemas`, and every downstream
   `msg.<msgVar>.*` reference.

## Direct document workflow

Only when no local bundle is the source of truth.

### Editing checklist

1. Read the existing workflow document and the actors' relationships.
2. Make the configuration, model, expression, code or graph change.
3. Apply the semantic rules above. Add a CommentActor above the workflow if it fits and none exists.
4. `borgiq validate <file>`; fix the errors.
5. Optionally `borgiq validate <file> --post-process -i` ([validation.md](validation.md#validators-per-mode)).
6. Review the diff before deploying.

### Rename an actor in a direct document

Update `name`, set the new `msgVar` from `borgiq generate msgvar "<new name>"`, then replace every
`msg.<old_msgVar>` expression, downstream input and InterfaceActor display label, and validate:

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

Adding an actor means generating its actor ID, msgVar and edge IDs, then adding the actor, its source-owned `edges`
and its `position`. Removing one means deleting it and its inbound and outbound edges, then fixing downstream
references.

### Update DenoActor/PythonActor code in a document

1. Update `configuration.inputs` when input names change.
2. Edit the `configuration.codeDir` entry whose `path` is the file you mean; the entrypoint is `main.ts` (`main.py` for
   Python). Add an entry to introduce a helper file; drop one to retire it.
3. Keep variable access and destructuring in step with the inputs.
4. Update the schemas, the returned output and downstream consumers when the result shape changes.
5. Validate. `borgiq validate` checks that `codeDir` is a list of `{path, content}` files containing the entrypoint;
   the BorgIQ API is the authority on the rest.

A document written before multi-file support may carry a single `configuration.code` string. The runtime reads only
`codeDir`, so that actor cannot run (`canvases validate` reports the missing entrypoint) until you replace the field.
Never send both for one actor:

```yaml
# Before
configuration:
  code: |
    import type { Request, Response } from "@borgiq/actors";
    export default async function receive(req: Request): Promise<Response> { … }

# After
configuration:
  codeDir:
    - path: main.ts
      content: |
        import type { Request, Response } from "@borgiq/actors";
        export default async function receive(req: Request): Promise<Response> { … }
```
