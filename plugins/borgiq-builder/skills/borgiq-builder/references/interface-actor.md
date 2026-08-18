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
              value: Submit Decision
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
| `interfaceUrl` | string | Full URL to access the form page |

### Event Port Output

The Event port emits when a user submits the form:

```json
{
  "meta": {
    "submissionInterfaceId": "b1ec816b2e25b5a7b57600dda21e0bc8",
    "user": {
      "id": "USER01abc123def456ghi789jkl0mn",
      "name": "John Smith",
      "email": "john@example.com"
    }
  },
  "body": {
    "decision": "approved",
    "comments": "Looks good to me!"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `meta.submissionInterfaceId` | string | Matches the `interfaceId` from Meta port |
| `meta.user` | object | Information about the user who submitted |
| `body` | object | Form field values (keyed by component `key`) |

## Options Reference

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `page` | object | Yes | Page layout configuration. See [interface-pages.md](interface-pages.md) for complete reference. |
| `page.children` | array | Yes | Array of UI components to render |
| `page.pageTitle` | string | No | Browser tab title |
| `page.formWidth` | string | No | Form width: `full`, `half`, `third` |
| `page.themeColor` | string | No | Theme color for the form |
| `onSubmit` | object | Yes | Action to perform after form submission |

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
          defaultValue: ${{ msg.order.id }}
        - type: number
          key: total
          label: Total Amount
          readOnly: true
          defaultValue: ${{ msg.order.total }}
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
      value: Submit
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
              defaultValue: ${{ msg.request.id }}
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
              value: Submit Decision
        onSubmit:
          type: successMessage
          successMessage: Thank you for your response!
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
# Send interface URL via email
configuration:
  inputs:
    interfaceUrl: ${{ msg.approval_form.interfaceUrl }}
  options:
    url: https://api.sendgrid.com/v3/mail/send
    method: POST
    body:
      personalizations:
        - to:
            - email: ${{ inputs.approverEmail }}
      subject: Approval Required
      content:
        - type: text/html
          value: |
            Please review and approve: ${{ inputs.interfaceUrl }}
```

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

The InterfaceActor shares the same page configuration schema as InterfaceTriggerActor. See [typescript/actor-schemas-triggers.md](typescript/actor-schemas-triggers.md) for the complete TypeScript definitions of page components and options.
