# Button Trigger Actor Reference

The ButtonTriggerActor starts a flow when someone clicks its button in the BorgIQ UI: manual runs, testing and debugging, ad-hoc jobs. It emits its `configuration.options` as the message.

```yaml
type: ButtonTriggerActor
version: 1
name: Process Data Button
msgVar: process_data_button
isActive: true
sourcePorts:
  - id: SPRTdefault
configuration:
  options:                    # any keys; emitted as msg.process_data_button
    action: processAll
    config:
      batchSize: 50
      dryRun: false
    startedAt: ${{ new Date().toISOString() }}
    literal: '\${{ Date.now() }}'
schemas: {}
```

- Options may hold any YAML (strings, numbers, lists, nested objects) and `${{ }}` expressions, evaluated when the run starts.
- Downstream actors read `${{ msg.<msgVar>.<key> }}`. A code actor maps the message through its `configuration.inputs`, e.g. `triggerData: ${{ msg.process_data_button }}`, then reads `req.inputs.triggerData.action`.
- To keep a `${{ }}` from being evaluated, put a backslash before it: `'\${{ ... }}'` in a plain or single-quoted YAML string, `"\\${{ ... }}"` in a double-quoted one. The backslash stays in the emitted value (`\${{ Date.now() }}`). Quoting alone does not escape: `'''${{ Date.now() }}'''` emits the evaluated timestamp wrapped in single quotes.

Schema: [typescript/actorSchemas/trigger/button.md](typescript/actorSchemas/trigger/button.md).
