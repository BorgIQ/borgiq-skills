# Interface Actor Reference

The InterfaceActor renders a web form/page mid-workflow and provides two output ports: one for page metadata (including URL) and one for form submission events.

## Table of Contents

- [Overview](#overview)
- [Key Differences from InterfaceTriggerActor](#key-differences-from-interfacetriggeractor)
- [Configuration Structure](#configuration-structure)
- [Source Ports](#source-ports)
- [Options Reference](#options-reference)
- [Page Configuration](#page-configuration)
- [Workflow Patterns](#workflow-patterns)
- [Complete Example: Approval Form](#complete-example-approval-form)
- [Accessing Interface Data in Downstream Actors](#accessing-interface-data-in-downstream-actors)
- [Use Cases](#use-cases)
- [TypeScript Schema Hint](#typescript-schema-hint)

## Overview

Unlike InterfaceTriggerActor which starts a workflow, InterfaceActor is a **Task Actor** that can be placed anywhere in a workflow. It generates a unique URL for a form page and emits messages on two separate ports:

- **Meta port** (`SPRTdefault`): Emits when the actor executes, providing the interface URL
- **Event port** (`SPRTevent00`): Emits when a user submits the form

Whoever opens `interfaceUrl` must be signed in to BorgIQ as a Viewer, Member or Admin of the canvas's workspace (the workspace settings offer App user grants only for App, React App and InterfaceTrigger actors); there is no anonymous access. Send the URL only to workspace members. The actor waits for a submission without limit unless `timeoutInMinutes` is set.

Use InterfaceActor for:

- Displaying forms mid-workflow without requiring an interface trigger
- Sending form URLs via email, Slack, or other channels for async user input
- Building approval workflows where the form URL is distributed programmatically
- Creating multi-step workflows with user interaction points

## Key Differences from InterfaceTriggerActor

| Aspect | InterfaceTriggerActor | InterfaceActor |
|--------|----------------------|----------------|
| Category | Trigger Actor | Task Actor |
| Starts workflow | Yes | No |
| Position in flow | Must be first | Anywhere |
| Output ports | 1 (default) | 2 (Meta + Event) |
| URL distribution | Manual sharing | Programmatic (via Meta port) |

## Configuration Structure

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
            - key: header
              type: header
              value: Approval Required
            - key: decision
              type: select
              label: Decision
              options:
                - label: Approve
                  value: approved
                - label: Reject
                  value: rejected
            - key: comments
              type: textarea
              label: Comments
              placeholder: Add any comments...
            - key: submit
              type: formButton
              text: Submit Decision
        onSubmit:
          type: successMessage
          successMessage: Thank you for your response!
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Source Ports

InterfaceActor has two required source ports:

| Port ID | Name | Description |
|---------|------|-------------|
| `SPRTevent00` | Event | Emits form submission data when user submits the form |
| `SPRTdefault` | Meta | Emits interface metadata (URL, ID) when the actor executes |

### Meta Port Output

The Meta port emits immediately when the actor executes:

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

### Event Port Output

The Event port emits when a user submits the form:

```json
{
  "meta": {
    "interfaceId": "b1ec816b2e25b5a7b57600dda21e0bc8",
    "submissionInterfaceId": "5f0c2e9a7d4b41c8a3e6b2d19f7c0a54",
    "user": {
      "id": "USER01abc123def456ghi789jkl0mn",
      "name": "John Smith",
      "email": "john@example.com"
    },
    "ipAddress": "203.0.113.7"
  },
  "body": {
    "decision": "approved",
    "comments": "Looks good to me!"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `meta.interfaceId` | string | Matches the `interfaceId` from the Meta port; use it to match a submission to the URL you sent |
| `meta.submissionInterfaceId` | string | A new id for the page shown after submission (used by `onSubmit: nextInterface`) |
| `meta.user` | object | The signed-in user who submitted: `id`, `name`, `email` |
| `meta.ipAddress` | string | IP address of the submitter |
| `body` | object | Form field values (keyed by component `key`) |

## Options Reference

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `page` | object | Yes | Page layout configuration. See [interface-pages.md](interface-pages.md) for complete reference. |
| `page.children` | array | Yes | Array of UI components to render |
| `page.pageTitle` | string | No | Browser tab title |
| `page.formWidth` | string | No | `full`, `half` (default) or `adjustable` |
| `page.themeColor` | string | No | Primary color: hex `#RRGGBB` or a Mantine color name |
| `page.backgroundColor` | string | No | Page background: a CSS color or a Mantine color name |
| `onSubmit` | object | Yes | Action to perform after form submission |
| `timeoutInMinutes` | number | No | Minutes to wait for a submission. Default: no timeout. On timeout the actor fails with a `TimeoutError`; downstream actors receive it as `err` only when `continueOnError: true` |
| `defaultValues` | object | No | Prefill values keyed by component `key`, appended to `interfaceUrl` as query params (visible in the URL) |
| `autoSubmitAfterSeconds` | integer | No | Submit the form automatically this many seconds after it opens |
| `showProgressStatus` | boolean | No | Show the flow's progress on the waiting page after submission. Requires `onSubmit.type: nextInterface` |
| `emitPage` | boolean | No | Include the page config in the Meta port message |

### onSubmit Types

| Type | Description |
|------|-------------|
| `successMessage` | Display a success message after submission |
| `urlRedirect` | Redirect to an external URL |
| `nextInterface` | Redirect to the next interface rendered in the workflow |

## Page Configuration

The `page` configuration defines the form layout and components. For the complete reference including all component types, properties, dynamic default values, read-only fields, and examples, see **[interface-pages.md](interface-pages.md)**.

## Workflow Patterns

### Pattern 1: Send Form URL via Email

```
ButtonTrigger -> InterfaceActor -> SendEmail (Meta port)
                      |
                      +-> ProcessApproval (Event port)
```

The Meta port provides the URL immediately, which can be sent via email. When the user clicks the link and submits, the Event port fires.

### Pattern 2: Approval Workflow

```yaml
# InterfaceActor edges configuration
edges:
  EDGE01metaedge:
    id: EDGE01metaedge
    sourceActorId: ACTR01interface
    sourcePortId: SPRTdefault  # Meta port
    targetActorId: ACTR01sendemail
    targetPortId: TPRTdefault
    label: Meta
    type: borgiqEdge
  EDGE01eventedge:
    id: EDGE01eventedge
    sourceActorId: ACTR01interface
    sourcePortId: SPRTevent00  # Event port
    targetActorId: ACTR01processapproval
    targetPortId: TPRTdefault
    label: Event
    type: borgiqEdge
```

### Pattern 3: Display Data with Action Buttons

Use read-only fields to display data and capture user actions:

```yaml
page:
  children:
    - type: header
      key: orderHeader
      value: Order Review
    - type: section
      key: orderDetails
      label: Order Details
      extendParentObject: true
      children:
        - type: text
          key: orderId
          label: Order ID
          readOnly: true
          default: ${{ msg.order.id }}
        - type: number
          key: total
          label: Total Amount
          readOnly: true
          default: ${{ msg.order.total }}
    - type: divider
      key: actionDivider
    - type: buttonGroup
      key: action
      label: Action
      options:
        - label: Approve
          value: approve
        - label: Reject
          value: reject
        - label: Request More Info
          value: more_info
    - type: textarea
      key: notes
      label: Notes
      placeholder: Add any notes...
    - type: formButton
      key: submit
      text: Submit
```

## Complete Example: Approval Form

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01k7hkjx0te3zgybq95rwbcbjz:
    type: InterfaceActor
    version: 1
    name: Approval Form
    msgVar: approval_form
    description: Display approval form and capture decision
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
          pageTitle: Approval Required
          formWidth: half
          children:
            - type: header
              key: title
              value: Request Approval
            - type: text
              key: requestId
              label: Request ID
              readOnly: true
              default: ${{ msg.request.id }}
            - type: divider
              key: separator
            - type: buttonGroup
              key: decision
              label: Decision
              required: true
              options:
                - label: Approve
                  value: approved
                - label: Reject
                  value: rejected
            - type: textarea
              key: comments
              label: Comments
              placeholder: Add any comments...
            - type: formButton
              key: submit
              text: Submit Decision
        onSubmit:
          type: successMessage
          successMessage: Thank you for your response!
        timeoutInMinutes: 4320   # stop waiting after 3 days
    schemas: {}
    id: ACTR01k7hkjx0te3zgybq95rwbcbjz
    position:
      x: 0
      'y': 0
    edges: {}
```

For more page configuration examples, see **[interface-pages.md](interface-pages.md)**.

## Accessing Interface Data in Downstream Actors

### From Meta Port (interface URL)

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

See [send-email-actor.md](send-email-actor.md) for the full SendEmailActor configuration.

### From Event Port (form submission)

```yaml
# Process form submission
configuration:
  inputs:
    decision: ${{ msg.approval_form.body.decision }}
    comments: ${{ msg.approval_form.body.comments }}
    submittedBy: ${{ msg.approval_form.meta.user.email }}
```

## Use Cases

### Approval Workflows

Create approval forms that can be sent via any channel (email, Slack, SMS) and process the response when submitted.

### Data Review Interfaces

Display data from upstream actors for user review before proceeding with the workflow.

### Multi-Step Forms

Chain multiple InterfaceActors to create wizard-like multi-step form experiences.

### Async User Input

Collect user input at any point in a workflow without requiring the workflow to start from an interface.

## TypeScript Schema Hint

The InterfaceActor shares the same page configuration schema as InterfaceTriggerActor. Exact definitions: InterfaceActor options in [typescript/actorSchemas/task/interface.md](typescript/actorSchemas/task/interface.md), the page schema in [typescript/schemas/interface.md](typescript/schemas/interface.md), and the components in [typescript/index.md](typescript/index.md).
