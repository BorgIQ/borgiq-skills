# SendEmailActor Reference

The SendEmailActor sends emails with text and/or HTML content, with optional attachments.

## Table of Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [Email Address Format](#email-address-format)
- [Output Schema](#output-schema)
- [Examples](#examples)
- [Use Cases](#use-cases)
- [Workflow Patterns](#workflow-patterns)
- [TypeScript Schema Hint](#typescript-schema-hint)

## Overview

SendEmailActor is a **Task Actor** that sends emails through BorgIQ's email service. It supports:

- Single or multiple recipients (to, cc, bcc)
- Text and/or HTML email bodies
- File attachments from upstream actors

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: SendEmailActor
    version: 1
    name: Send Email
    msgVar: send_email
    description: Sends an email notification
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        to: recipient@example.com
        subject: Email Subject
        textBody: Plain text content of the email
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
| `to` | string | Yes | Recipient email address(es). Multiple emails as comma-separated list. |
| `subject` | string | Yes | Email subject line |
| `cc` | string | No | CC email address(es). Multiple emails as comma-separated list. |
| `bcc` | string | No | BCC email address(es). Multiple emails as comma-separated list. |
| `textBody` | string | Conditional | Plain text email body. Required if `htmlBody` is not provided. |
| `htmlBody` | string | Conditional | HTML email body. Required if `textBody` is not provided. |
| `attachments` | array/BIQFile | No | File attachments. Can be a single BIQFile or array of BIQFiles. |

**Note:** At least one of `textBody` or `htmlBody` must be provided.

## Email Address Format

Email addresses can be in these formats:
- Simple: `user@example.com`
- With name: `"John Doe" <john@example.com>`
- Multiple: `user1@example.com, user2@example.com`

## Output Schema

When the email is sent successfully, SendEmailActor emits:

```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "textBody": "Plain text content...",
  "htmlBody": "<html>...</html>",
  "cc": "cc@example.com",
  "bcc": "bcc@example.com",
  "attachments": [...],
  "meta": {
    "emailId": "EMAL01kd83rj222vhmsengk043dp35"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `to` | string | Recipient email address(es) |
| `subject` | string | Email subject |
| `textBody` | string | Plain text body (if provided) |
| `htmlBody` | string | HTML body (if provided) |
| `cc` | string | CC recipients (if provided) |
| `bcc` | string | BCC recipients (if provided) |
| `attachments` | array | Attached files (if provided) |
| `meta.emailId` | string | BorgIQ email ID for tracking |

## Examples

### Simple Text Email

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kd9q4t718h204fqx82s0hprq:
    type: SendEmailActor
    version: 1
    name: Send Notification
    msgVar: send_notification
    description: Sends a simple text notification email
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        to: admin@example.com
        subject: Workflow Completed
        textBody: |
          The workflow has completed successfully.

          Processed items: 42
          Duration: 5 minutes
    schemas: {}
    id: ACTR01kd9q4t718h204fqx82s0hprq
    position:
      x: 0
      'y': 0
    edges: {}
```

### HTML Email with Dynamic Content

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kd9q5abc123def456gh78ij:
    type: SendEmailActor
    version: 1
    name: Send Report Email
    msgVar: send_report_email
    description: Sends an HTML formatted report email
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        recipientEmail: ${{ msg.trigger.body.email }}
        reportData: ${{ msg.generate_report.data }}
      options:
        to: ${{ inputs.recipientEmail }}
        subject: Daily Report - ${{ Q.dateFns.format(Q.now(), 'yyyy-MM-dd') }}
        htmlBody: |
          <html>
          <body>
            <h1>Daily Report</h1>
            <p>Here is your daily summary:</p>
            <table>
              <tr>
                <td>Total Orders:</td>
                <td>${{ inputs.reportData.totalOrders }}</td>
              </tr>
              <tr>
                <td>Revenue:</td>
                <td>${{ inputs.reportData.revenue }}</td>
              </tr>
            </table>
          </body>
          </html>
        textBody: |
          Daily Report

          Total Orders: ${{ inputs.reportData.totalOrders }}
          Revenue: ${{ inputs.reportData.revenue }}
    schemas:
      inputs:
        type: object
        properties:
          recipientEmail:
            type: string
            title: Recipient Email
          reportData:
            type: any
            title: Report Data
    id: ACTR01kd9q5abc123def456gh78ij
    position:
      x: 0
      'y': 0
    edges: {}
```

### Email with Multiple Recipients

```yaml
configuration:
  options:
    to: team-lead@example.com, manager@example.com
    cc: team@example.com
    bcc: archive@example.com
    subject: Weekly Team Update
    textBody: |
      Weekly team status update attached.
```

### Email with Attachments

```yaml
configuration:
  inputs:
    reportFile: ${{ msg.generate_pdf.file }}
  options:
    to: stakeholders@example.com
    subject: Monthly Report
    textBody: Please find the monthly report attached.
    attachments:
      - ${{ inputs.reportFile }}
```

### Email with Dynamic Attachment from Upstream Actor

```yaml
configuration:
  inputs:
    csvFile: ${{ msg.export_data.csvFile }}
    pdfReport: ${{ msg.generate_report.pdfFile }}
  options:
    to: ${{ msg.trigger.body.recipientEmail }}
    subject: Data Export Complete
    htmlBody: |
      <h1>Export Complete</h1>
      <p>Your data export is ready. Please find the files attached.</p>
    textBody: Your data export is ready. Please find the files attached.
    attachments:
      - ${{ inputs.csvFile }}
      - ${{ inputs.pdfReport }}
```

## Use Cases

### Notification Emails

Send automated notifications when workflows complete, errors occur, or specific conditions are met.

### Report Distribution

Distribute generated reports (PDFs, CSVs, Excel files) to stakeholders via email.

### Approval Requests

Send approval request emails with links to InterfaceActor forms (combine with InterfaceActor's Meta port output).

### Alert Emails

Send alerts when monitoring detects issues or thresholds are exceeded.

## Workflow Patterns

### Pattern 1: Notification After Processing

```
Trigger -> ProcessData -> SendEmailActor
```

### Pattern 2: Send Report with Attachment

```
Trigger -> GenerateReport -> SendEmailActor (with attachment)
```

### Pattern 3: Approval Workflow with Email

```
Trigger -> InterfaceActor -> SendEmail (Meta port for URL)
                    |
                    +-> ProcessApproval (Event port)
```

Example of sending an approval form URL via email:

```yaml
# SendEmailActor configuration after InterfaceActor
configuration:
  inputs:
    approvalUrl: ${{ msg.approval_form.interfaceUrl }}
    approverEmail: ${{ msg.trigger.body.approverEmail }}
  options:
    to: ${{ inputs.approverEmail }}
    subject: Approval Required - Request #${{ msg.trigger.body.requestId }}
    htmlBody: |
      <h1>Approval Required</h1>
      <p>Please review and approve the request:</p>
      <p><a href="${{ inputs.approvalUrl }}">Click here to review</a></p>
    textBody: |
      Approval Required

      Please review and approve the request:
      ${{ inputs.approvalUrl }}
```

## TypeScript Schema Hint

See [typescript/actor-schemas-task-core.md](typescript/actor-schemas-task-core.md) for complete TypeScript definitions including:
- `SendEmailActorOptionsSchema` - Configuration options
- `SendEmailActorResultSchema` - Output message structure
