# SendEmailActor Reference

The SendEmailActor sends an email through BorgIQ's email service: text and/or HTML body, several recipients, optional attachments from upstream actors. Read this for its options, address formats, output, and the attachment and approval-link patterns.

## Options

| Option | Type | Required | Meaning |
|---|---|---|---|
| `to` | string | yes | Recipients, comma-separated |
| `subject` | string | yes | Subject line |
| `cc` | string | no | CC recipients, comma-separated |
| `bcc` | string | no | BCC recipients, comma-separated |
| `textBody` | string | one body is required | Plain-text body |
| `htmlBody` | string | one body is required | HTML body |
| `attachments` | BIQFile or BIQFile[] | no | Files from upstream actors |

- Give at least one of `textBody` and `htmlBody`.
- An address is `user@example.com` or `"John Doe" <john@example.com>`; separate several with commas.
- It emits the options it sent (a single attachment as a one-item array) plus `meta.emailId` (`EMAL…`), BorgIQ's id for the email.

Exact schema: [typescript/actorSchemas/task/sendEmail.md](typescript/actorSchemas/task/sendEmail.md).

## Example

```yaml
type: SendEmailActor
version: 1
name: Send Report Email
msgVar: send_report_email
isActive: true
sourcePorts:
  - id: SPRTdefault
configuration:
  inputs:
    recipientEmail: ${{ msg.trigger.body.email }}
    reportData: ${{ msg.generate_report.data }}
  options:
    to: ${{ inputs.recipientEmail }}
    cc: team@example.com, manager@example.com
    subject: Daily Report - ${{ Q.dateFns.format(Q.now(), 'yyyy-MM-dd') }}
    htmlBody: |
      <h1>Daily Report</h1>
      <p>Total orders: ${{ inputs.reportData.totalOrders }}</p>
      <p>Revenue: ${{ inputs.reportData.revenue }}</p>
    textBody: |
      Daily Report
      Total orders: ${{ inputs.reportData.totalOrders }}
      Revenue: ${{ inputs.reportData.revenue }}
    attachments:
      - ${{ msg.generate_pdf.file }}
      - ${{ msg.export_data.csvFile }}
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
```

## Emailing an approval link

An [InterfaceActor](interface-actor.md) emits its page URL on its Meta port (`SPRTdefault`) as soon as it runs, and the submission later on its Event port (`SPRTevent00`). Wire the Meta port to a SendEmailActor and the Event port to the approval logic:

```
Trigger -> InterfaceActor -> SendEmailActor      (Meta port: interfaceUrl)
                  |
                  +-> ProcessApproval            (Event port: submission)
```

```yaml
configuration:
  inputs:
    approvalUrl: ${{ msg.approval_form.interfaceUrl }}
    approverEmail: ${{ msg.trigger.body.approverEmail }}
  options:
    to: ${{ inputs.approverEmail }}
    subject: "Approval required: request #${{ msg.trigger.body.requestId }}"   # quoted: ' #' starts a YAML comment
    htmlBody: |
      <p>Please review the request: <a href="${{ inputs.approvalUrl }}">open it</a></p>
    textBody: |
      Please review the request: ${{ inputs.approvalUrl }}
```

Send the link only to people who can sign in as a Viewer, Member or Admin of the canvas's workspace; see [interface-actor.md](interface-actor.md).
