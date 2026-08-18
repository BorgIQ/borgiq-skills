# CommentActor

CommentActor is a non-functional actor used for adding visual annotations to workflows. It does not participate in message flow or execution—it's purely for documentation purposes.

## Required: Workflow Setup Comment

**Every workflow must include a CommentActor at the top** with setup instructions, prerequisites, and a brief spec. This is the first actor in the YAML and is positioned above all other actors (negative `y` value).

The setup comment should include:
- **Brief description** of what the workflow does
- **Setup instructions** (connections to configure, webhook URLs to register, etc.)
- **Prerequisites** (required workspace settings, external service configuration)
- **TODOs** for known limitations or future improvements

### Example - Setup Comment

```yaml
ACTR01jpskpc493pyaf8mmgby52sw5:
  version: 1
  type: CommentActor
  name: Comment
  msgVar: comment
  description: |
    # Email Reply Workflow
    Monitors inbox and auto-replies using AI.

    ## Setup
    1. Configure Gmail connection in workspace settings
    2. Set up webhook URL in external service
    3. Test with sample payload

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
  continueOnError: false
  enableLTM: false
  enableSTM: false
  id: ACTR01jpskpc493pyaf8mmgby52sw5
  position:
    x: 0
    'y': -300
  edges: {}
```

### Positioning

Position the CommentActor **above** all other actors by using a negative `y` value (e.g., `y: -300`). The first functional actor (trigger) should start at `y: 0`.

## Use Cases

- **Workflow setup comment** (required) — setup instructions and spec at the top of every workflow
- Document workflow sections with explanations
- Add TODO notes for future improvements
- Provide setup instructions or prerequisites
- Explain complex logic to other team members

## More Examples

### TODO Comment

```yaml
ACTR01jpskpc493pyaf8mmgby52sw5:
  version: 1
  type: CommentActor
  name: Comment
  msgVar: comment
  description: '# TODO: Support for Monitoring Multiple Inboxes (via Connection ID)'
  isActive: true
  sourcePorts: []
  configuration:
    options:
      width: 510px
      height: 115px
      bgColor: '#ffe066'
      textColor: black
  schemas: {}
  continueOnError: false
  enableLTM: false
  enableSTM: false
  id: ACTR01jpskpc493pyaf8mmgby52sw5
  position:
    x: 0
    'y': -300
  edges: {}
```

### Minimal Comment (no styling)

```yaml
ACTR01kk5b1et45zvmrkpt7qgsey1x:
  type: CommentActor
  version: 1
  name: Comment
  msgVar: comment
  description: The Comment actor allows for in-canvas descriptions.
  isActive: true
  continueOnError: false
  enableLTM: false
  enableSTM: false
  sourcePorts: []
  configuration:
    options: {}
  schemas: {}
  id: ACTR01kk5b1et45zvmrkpt7qgsey1x
  position:
    x: 0
    'y': -300
  edges: {}
```

## Options

| Option | Type | Description |
|--------|------|-------------|
| `width` | string | CSS width (e.g., `"510px"`, `"300px"`) |
| `height` | string | CSS height (e.g., `"115px"`, `"200px"`) |
| `bgColor` | string | Background color (hex or CSS color name) |
| `textColor` | string | Text color (hex or CSS color name) |

## Notes

- The `description` field supports **markdown** that is rendered in the UI
- For single-line descriptions, use a plain string or quoted string: `description: '# My Title'`
- For multi-line descriptions, use YAML `|` block scalar: `description: |`
- `sourcePorts` should be an empty array `[]`
- `edges` should be an empty object `{}`
- CommentActors are not connected to other actors
- When editing workflows, update the CommentActor if setup instructions or spec changed
