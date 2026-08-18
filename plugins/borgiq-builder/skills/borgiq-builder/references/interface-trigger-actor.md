# Interface Trigger Actor Reference

The InterfaceTriggerActor starts a workflow when a user submits a form on its hosted web page.

## Table of Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [Page Configuration](#page-configuration)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [Emitted Message](#emitted-message)
- [UI Component Examples](#ui-component-examples)
- [Accessing Form Data in Downstream Actors](#accessing-form-data-in-downstream-actors)
- [Dynamic Interface Response](#dynamic-interface-response)
- [Interface URL](#interface-url)
- [Use Cases](#use-cases)
- [Quick Example](#quick-example)

## Overview

Interface triggers provide a hosted web page with customizable form elements. When users submit the form, the workflow is triggered with the form data. Use interface triggers for:

- Building user-facing forms and interfaces
- Collecting structured input from users
- Internal tools requiring form-based data entry

**Note:** For web applications (SPAs, dashboards, interactive tools), use [AppTriggerActor](app-trigger-actor.md) instead. InterfaceTriggerActor is designed for form-based workflows where user submission triggers downstream processing.

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: InterfaceTriggerActor
    version: 1
    name: Interface Trigger
    msgVar: interface_trigger
    description: Display a form and trigger workflow on submission
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
              value: Form Title
            - key: submit
              type: formButton
        onSubmit:
          type: successMessage
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Options Reference

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `page` | object | Yes | Page layout configuration. See [interface-pages.md](interface-pages.md) for complete reference. |
| `page.children` | array | Yes | Array of UI components to render |
| `onSubmit` | object | Yes | Action to perform after form submission |
| `defaultValues` | object | No | Default values to inject into the form via URL query params |
| `autoSubmitAfterSeconds` | integer | No | Auto-submit the form after specified seconds |

## Page Configuration

The `page` configuration defines the form layout and components. For the complete reference including all component types, properties, and examples, see **[interface-pages.md](interface-pages.md)**.

## TypeScript Schema Definition

The complete TypeScript schema for InterfaceTriggerActor options and results:

```typescript
import { z } from 'zod';

/** The options schema for the InterfaceTriggerActor */
export const InterfaceTriggerActorOptionsSchema = z.object({
  /** The page to render for the interface trigger */
  page: BIQInterfacePageDataSchema
    .describe('The page data to render for the interface trigger'),
  /** The default values to inject into the url as query params */
  defaultValues: z.record(z.string(), z.any()).nullish()
    .describe('The default values to pass to the interface trigger form to build the form'),
  /** Auto submit the form after it has been opened after a certain number of seconds */
  autoSubmitAfterSeconds: z.number().int().min(0).nullish()
    .describe('Auto submit the form after it has been opened after a certain number of seconds'),
  /** What page to redirect to when the interface trigger form is submitted */
  onSubmit: z.discriminatedUnion('type', [
    z.object({
      /** When submitted, redirect to the next interface rendered in the flow */
      type: z.literal('nextInterface')
        .describe('When submitted, redirect to the next interface rendered in the flow'),
      /** The message to show while the next interface is loading */
      loadingMessage: z.string().nullish()
        .describe('The message to show while the next interface is loading'),
    }),
    z.object({
      /** When submitted, show a success message */
      type: z.literal('successMessage')
        .describe('When submitted, show a success message'),
      /** The message to show when successfully submitted */
      successMessage: z.string().nullish()
        .describe('The message to show when successfully submitted'),
    }),
    z.object({
      /** When submitted, redirect to a URL */
      type: z.literal('urlRedirect')
        .describe('When submitted, redirect to a URL'),
      /** The URL to redirect to */
      url: z.url()
        .describe('The URL to redirect to when successfully submitted'),
    })
  ]),
});

export type InterfaceTriggerActorOptions = z.infer<typeof InterfaceTriggerActorOptionsSchema>;

/** The result schema for the InterfaceTriggerActor */
export const InterfaceTriggerActorResultSchema = z.object({
  meta: z.object({
    submissionInterfaceId: z.string()
      .describe('The interface id used for rendering the next page'),
    user: z.object({
      id: z.string()
        .describe('The user ID of the submitter'),
      name: z.string()
        .describe('The display name of the submitter'),
      email: z.string()
        .describe('The email address of the submitter'),
    }).describe('Information about the user who submitted the form'),
  }),
  body: z.record(z.string(), z.any())
    .describe('The body of the interface submission'),
});

export type InterfaceTriggerActorResult = z.infer<typeof InterfaceTriggerActorResultSchema>;
```

### onSubmit Types

| Type | Description |
|------|-------------|
| `nextInterface` | Redirect to the next interface rendered in the workflow |
| `successMessage` | Display a success message after submission |
| `urlRedirect` | Redirect to an external URL |

### Page Children (UI Components)

For the complete list of component types and their properties, see **[interface-pages.md](interface-pages.md)**.

Common component types include:

| Type | Description |
|------|-------------|
| `header` | Header/title text |
| `text` | Single-line text input |
| `textarea` | Multi-line text input |
| `number` | Numeric input |
| `select` | Dropdown selection |
| `checkbox` | Boolean checkbox |
| `radio` | Radio button group |
| `formButton` | Form submit button |

## Emitted Message

The interface trigger emits a message containing the form submission data:

```json
{
  "meta": {
    "submissionInterfaceId": "d85670632dd795c2d6dd02a500a61943",
    "user": {
      "id": "USER01abc123def456ghi789jkl0mn",
      "name": "John Smith",
      "email": "john@example.com"
    }
  },
  "body": {
    "fieldKey1": "user input value",
    "fieldKey2": 42,
    "fieldKey3": true
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `meta.submissionInterfaceId` | string | The interface ID used for rendering the next page |
| `meta.user.id` | string | The user ID of the submitter |
| `meta.user.name` | string | The display name of the submitter |
| `meta.user.email` | string | The email address of the submitter |
| `body` | object | Object containing all form field values (keyed by component `key`) |

## UI Component Examples

For detailed component examples and all available component types, see **[interface-pages.md](interface-pages.md)**.

## Accessing Form Data in Downstream Actors

```yaml
# HttpRequestActor configuration - mapping individual fields
configuration:
  inputs:
    name: ${{ msg.interface_trigger.body.name }}
    email: ${{ msg.interface_trigger.body.email }}
    message: ${{ msg.interface_trigger.body.message }}
  options:
    url: https://api.example.com/contacts
    method: POST
    body:
      name: ${{ inputs.name }}
      email: ${{ inputs.email }}
      message: ${{ inputs.message }}
```

```yaml
# HttpRequestActor configuration - mapping the entire trigger output
configuration:
  inputs: ${{ msg.interface_trigger }}
  options:
    url: https://api.example.com/contacts
    method: POST
    body:
      name: ${{ inputs.body.name }}
      email: ${{ inputs.body.email }}
      message: ${{ inputs.body.message }}
      submittedBy: ${{ inputs.meta.user.email }}
```

```yaml
# DenoActor configuration
configuration:
  inputs: ${{ msg.interface_trigger }}
  options:
    allowNet: true
  code: |
    // code goes here...
```

```typescript
// In DenoActor
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const formData = req.inputs.body;

  // Access form fields
  const name = formData.name;
  const email = formData.email;
  const category = formData.category;

  // Access metadata
  const submissionInterfaceId = req.inputs.meta.submissionInterfaceId;
  const submittedBy = req.inputs.meta.user;

  // Process form data
  return {
    results: {
      processed: true,
      submissionInterfaceId,
      submittedBy: submittedBy.email,
      contact: { name, email, category },
    },
  };
}
```

## Dynamic Interface Response

Use DenoActor with `InterfaceRender` signal to dynamically render interface content:

```typescript
import type { Request, Response } from "@borgiq/actors";
import { Signal } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const formData = req.inputs.body;

  // Process data
  const result = await processSubmission(formData);

  // Render custom response via the returned signal
  return {
    results: result,
    signal: Signal.interfaceRender({
      page: {
        children: [
          { key: 'header', type: 'header', value: 'Submission Received!' },
          { key: 'result', type: 'text', value: `Your reference number: ${result.id}` },
        ],
      },
    }),
  };
}
```

## Interface URL

Each InterfaceTriggerActor is assigned a unique URL:

```
https://<borgiq-domain>/interface/<actor-id>
```

Share this URL with users to access the form.

## Use Cases

### Feedback Form

Collect user feedback with ratings and comments.

### Internal Request Form

Allow employees to submit requests (IT tickets, time off, expenses).

### Simple Survey

Create multi-question surveys with various input types.

### Data Entry Interface

Build interfaces for manual data entry into automated workflows.

## Quick Example

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
              options:
                - label: Excellent
                  value: 5
                - label: Good
                  value: 4
                - label: Average
                  value: 3
                - label: Poor
                  value: 2
                - label: Very Poor
                  value: 1
            - key: comments
              type: textArea
              label: Additional Comments
              placeholder: Tell us more...
            - key: submit
              type: formButton
              value: Submit Feedback
        onSubmit:
          type: successMessage
          message: Thank you for your feedback!
    schemas: {}
    id: ACTR01kd298z8kq4yd67m5pddd9cyp
    position:
      x: 0
      'y': 0
    edges: {}
```
