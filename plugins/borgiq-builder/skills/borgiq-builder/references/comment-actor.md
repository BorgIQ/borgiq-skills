# CommentActor

A CommentActor is a note on the canvas: its `description` renders as markdown; it has no ports or edges and never runs.

## When to add one

- It is optional. In a canvas bundle, the canvas's setup instructions, prerequisites and brief spec go in the bundle's `README.md` ([the canvas README](cli/canvas-bundles.md#the-canvas-readme)).
- Add a setup CommentActor only when the user wants the notes on the canvas itself, or when you return a YAML document without a bundle. Make it the first actor in the YAML and place it above the new workflow: negative `y` (e.g. `y: -300`), with the trigger at `y: 0`. In a bundle the position goes in `canvas.yaml` like any other actor's.
- Never add one as part of a single-actor addition.
- Update a comment when what it describes changes.

A setup comment gives what the workflow does, setup steps (connections, webhook URLs to register), prerequisites (workspace settings, external services) and known TODOs.

## Example

```yaml
ACTR01jpskpc493pyaf8mmgby52sw5:
  type: CommentActor
  version: 1
  name: Comment
  msgVar: comment
  description: |
    # Email Reply Workflow
    Monitors inbox and auto-replies using AI.

    ## Setup
    1. Configure Gmail connection in workspace settings
    2. Set up webhook URL in external service

    ## TODO
    - Support monitoring multiple inboxes via Connection ID
  isActive: true
  sourcePorts: []
  configuration:
    options:
      width: 510px
      height: 200px
      bgColor: '#ffe066'
      textColor: black
  schemas: {}
  id: ACTR01jpskpc493pyaf8mmgby52sw5
  position:
    x: 0
    'y': -300
  edges: {}
```

## Options

All optional; `options: {}` gives an unstyled note. Schema: [typescript/actorSchemas/other/comment.md](typescript/actorSchemas/other/comment.md).

| Option | Type | Meaning |
|---|---|---|
| `width`, `height` | string | CSS size, e.g. `510px` |
| `bgColor`, `textColor` | string | Hex or CSS color name |

For a one-line note, `description` can be a quoted string (`'# My Title'`); use a `|` block for several lines.
