# Interface Actor Reference

The InterfaceActor is a task actor that renders a form page mid-workflow: its Meta port emits the page URL when the actor runs, and its Event port emits the submission. Use it for approvals, review steps and "send a form by email" patterns. The `page` schema is in [interface-pages.md](interface-pages.md); a complete approval page is in [interface-examples.md](interface-examples.md#approval-page).

## Contents

- [Rules](#rules)
- [Actor document](#actor-document)
- [Options](#options)
- [Meta port output](#meta-port-output)
- [Event port output](#event-port-output)
- [Using the ports downstream](#using-the-ports-downstream)
- [Waiting page status](#waiting-page-status)

## Rules

- Whoever opens `interfaceUrl` must be signed in to BorgIQ as a Viewer, Member or Admin of the canvas's workspace; App user grants do not cover InterfaceActors, and there is no anonymous access ([interface-pages.md](interface-pages.md#access)). Send the URL only to workspace members.
- Declare both source ports and wire them: Meta (`SPRTdefault`) to the actor that delivers the URL (email, Slack), Event (`SPRTevent00`) to the actor that processes the answer.
- The actor waits for a submission without limit unless `timeoutInMinutes` is set. On timeout it fails with a `TimeoutError`; downstream actors receive it as `err` only when `continueOnError: true`.
- Unlike an InterfaceTriggerActor, it can sit anywhere in a flow. Chain several for a wizard ([interface-examples.md](interface-examples.md#multi-step-form)).

## Actor document

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: InterfaceActor
    version: 1
    name: Approval Form
    msgVar: approval_form
    description: Display an approval form and capture user response
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTevent00
        name: Event
      - id: SPRTdefault
        name: Meta
    configuration:
      options:
        page:
          children:
            - key: decision
              type: select
              label: Decision
              options:
                - label: Approve
                  value: approved
                - label: Reject
                  value: rejected
            - key: submit
              type: formButton
              text: Submit Decision
        onSubmit:
          type: successMessage
          successMessage: Thank you for your response!
        timeoutInMinutes: 4320   # stop waiting after 3 days
    schemas: {}
    id: ACTR01xxxxx
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
| `timeoutInMinutes` | number | No | Minutes to wait for a submission. Default: no timeout. On timeout the actor fails with a `TimeoutError` |
| `defaultValues` | object | No | Prefill values keyed by component `key`, appended to `interfaceUrl` as query params (visible in the URL) |
| `autoSubmitAfterSeconds` | integer | No | Submit the form automatically this many seconds after it opens |
| `showProgressStatus` | boolean | No | Show the flow's progress on the waiting page after submission. Requires `onSubmit.type: nextInterface` |
| `emitPage` | boolean | No | Include the page config in the Meta port message |

Exact types: [typescript/actorSchemas/task/interface.md](typescript/actorSchemas/task/interface.md).

## Meta port output

The Meta port (`SPRTdefault`) emits immediately when the actor executes:

```json
{
  "interfaceId": "b1ec816b2e25b5a7b57600dda21e0bc8",
  "interfaceUrl": "https://app.borgiq.com/org/myorg/w/my-workspace/c/CANV01xxx/interfaces/ACTR01xxx/b1ec816b2e25b5a7b57600dda21e0bc8"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `interfaceId` | string | Unique identifier for this interface instance |
| `interfaceUrl` | string | Full URL to access the form page; `defaultValues` are appended as query params |
| `page` | object | The rendered page config; present only when `emitPage: true` |

## Event port output

The Event port (`SPRTevent00`) emits when a user submits the form:

```json
{
  "meta": {
    "interfaceId": "b1ec816b2e25b5a7b57600dda21e0bc8",
    "submissionInterfaceId": "5f0c2e9a7d4b41c8a3e6b2d19f7c0a54",
    "user": { "id": "USER01abc123def456ghi789jkl0mn", "name": "John Smith", "email": "john@example.com" },
    "ipAddress": "203.0.113.7"
  },
  "body": { "decision": "approved", "comments": "Looks good to me!" }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `meta.interfaceId` | string | Matches the `interfaceId` from the Meta port; use it to match a submission to the URL you sent |
| `meta.submissionInterfaceId` | string | A new id for the page shown after submission (used by `onSubmit: nextInterface`) |
| `meta.user` | object | The signed-in user who submitted: `id`, `name`, `email` |
| `meta.ipAddress` | string | IP address of the submitter |
| `body` | object | Form field values (keyed by component `key`) |

## Using the ports downstream

```yaml
# SendEmailActor on the Meta port edge: email the interface URL to the approver
configuration:
  inputs:
    interfaceUrl: ${{ msg.approval_form.interfaceUrl }}
    approverEmail: ${{ msg.request.approverEmail }}   # the approver must be a workspace member
  options:
    to: ${{ inputs.approverEmail }}
    subject: Approval Required
    textBody: |
      Please review and approve: ${{ inputs.interfaceUrl }}
```

```yaml
# The actor on the Event port edge: process the submission
configuration:
  inputs:
    decision: ${{ msg.approval_form.body.decision }}
    comments: ${{ msg.approval_form.body.comments }}
    submittedBy: ${{ msg.approval_form.meta.user.email }}
```

SendEmailActor options: [send-email-actor.md](send-email-actor.md).

## Waiting page status

While a submitter waits on a `nextInterface` waiting page, an InterfaceStatusActor in the same flow run adds a component to its status area, or replaces the one with the same `key`; the area keeps the five most recent. Options: `component` (any form component, such as a `textDisplay` or `progress`), `order` (`prepend`, the default, or `append`) and `emitComponents` (also return the status components in its output). Its output is `{ status, statusComponents? }`; `status` is `not-found` when no waiting page is open. Exact types: [typescript/actorSchemas/task/interfaceStatus.md](typescript/actorSchemas/task/interfaceStatus.md).
