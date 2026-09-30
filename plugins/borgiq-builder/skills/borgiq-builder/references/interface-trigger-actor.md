# Interface Trigger Actor Reference

The InterfaceTriggerActor starts a workflow when a user submits the form on its hosted web page. Use it for forms that start a flow: internal requests, intake, feedback, surveys and data entry. For web applications (SPAs, dashboards, interactive tools) use a ReactAppTriggerActor (the `borgiq-react-app-builder` skill) instead. The `page` schema is in [interface-pages.md](interface-pages.md).

## Rules

- The page is open only to people signed in to BorgIQ with a workspace role, or App users granted this actor; there is no anonymous or public access ([interface-pages.md](interface-pages.md#access)). For public sign-ups, post from a page hosted outside BorgIQ to a public WebhookTriggerActor.
- The trigger has no upstream `msg`, so a `default` cannot read one: prefill with `default`, `defaultValues` or URL query params ([interface-pages.md](interface-pages.md#prefill)).
- To show a result the flow computes, set `onSubmit.type: nextInterface` and render an InterfaceActor downstream. Code actors cannot render a page: the Deno and Python SDKs build only the `webhookRespond`, `callableResponse` and `delayUntil` signals ([interface-examples.md](interface-examples.md#multi-step-form)).

## Actor document

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kd298z8kq4yd67m5pddd9cyp:
    type: InterfaceTriggerActor
    version: 1
    name: Feedback Form
    msgVar: feedback_form
    description: Collect user feedback through a web form
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        page:
          children:
            - key: header
              type: header
              value: Share Your Feedback
            - key: rating
              type: select
              label: How would you rate your experience?
              options:             # option values are strings
                - label: Excellent
                  value: '5'
                - label: Good
                  value: '4'
                - label: Poor
                  value: '2'
            - key: comments
              type: textarea
              label: Additional Comments
              placeholder: Tell us more...
            - key: submit
              type: formButton
              text: Submit Feedback
        onSubmit:
          type: successMessage
          successMessage: Thank you for your feedback!
    schemas: {}
    id: ACTR01kd298z8kq4yd67m5pddd9cyp
    position:
      x: 0
      'y': 0
    edges: {}
```

## Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `page` | object | Yes | Page options and components ([interface-pages.md](interface-pages.md#page-options)) |
| `onSubmit` | object | Yes | `successMessage`, `urlRedirect` or `nextInterface` ([interface-pages.md](interface-pages.md#onsubmit)) |
| `defaultValues` | object | No | Initial form values keyed by component `key`. Query params in the page URL (`?<key>=<value>`) also prefill fields and take precedence |
| `autoSubmitAfterSeconds` | integer | No | Auto-submit the form after specified seconds |
| `showProgressStatus` | boolean | No | Show the flow's progress on the waiting page after submission. Requires `onSubmit.type: nextInterface` |

Exact types: [typescript/actorSchemas/trigger/interface.md](typescript/actorSchemas/trigger/interface.md).

## Emitted message

```json
{
  "meta": {
    "submissionInterfaceId": "d85670632dd795c2d6dd02a500a61943",
    "user": { "id": "USER01abc123def456ghi789jkl0mn", "name": "John Smith", "email": "john@example.com" },
    "ipAddress": "203.0.113.7"
  },
  "body": { "rating": "5", "comments": "Great service" }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `meta.submissionInterfaceId` | string | The interface ID used for rendering the next page |
| `meta.user.id` | string | The user ID of the submitter |
| `meta.user.name` | string | The display name of the submitter; may be absent |
| `meta.user.email` | string | The email address of the submitter |
| `meta.ipAddress` | string | IP address of the submitter |
| `body` | object | Object containing all form field values (keyed by component `key`) |

The emitted shape is `FlowrunInterfaceTriggerDataSchema` in [typescript/schemas/runtime.md](typescript/schemas/runtime.md); the result schema in the options module lists `meta.interfaceId` and no `user`, which the runtime does not emit.

## Using the submission downstream

```yaml
# HttpRequestActor: map form fields into the request
configuration:
  inputs:
    name: ${{ msg.feedback_form.body.name }}
    email: ${{ msg.feedback_form.body.email }}
    submittedBy: ${{ msg.feedback_form.meta.user.email }}
  options:
    url: https://api.example.com/contacts
    method: POST
    body:
      name: ${{ inputs.name }}
      email: ${{ inputs.email }}
      submittedBy: ${{ inputs.submittedBy }}
```

To hand the whole submission to a code actor, set `inputs: ${{ msg.feedback_form }}`; the code reads `req.inputs.body` and `req.inputs.meta`.

## Interface URL

Each InterfaceTriggerActor is served at:

```
https://<borgiq-app-host>/org/<org-slug>/w/<workspace-slug>/c/<canvas-slug-or-id>/interfaces/<actor-id>
```

Share this URL only with people who can open it ([Access](interface-pages.md#access)).
