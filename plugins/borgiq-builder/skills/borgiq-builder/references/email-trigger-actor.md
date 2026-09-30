# Email Trigger Actor Reference

The EmailTriggerActor starts a flow when an email arrives at its own address, `<unique-id>@<borgiq-email-domain>` (forward mail from another account to it). The address is generated for the actor and shown in the BorgIQ UI when the actor is selected. The actor has no options. Read this for the message fields and for reading attachments.

```yaml
type: EmailTriggerActor
version: 1
name: Support Email Trigger
msgVar: email_trigger
isActive: true
sourcePorts:
  - id: SPRTdefault
configuration:
  options: {}
schemas: {}
```

## Emitted message

| Field | Type | Meaning |
|---|---|---|
| `messageId` | string | Message identifier |
| `from` | string | Sender address |
| `to` | string | Recipient address |
| `cc` | string \| null | CC recipients, comma-separated |
| `subject` | string | Subject line |
| `date` | string | ISO 8601 date |
| `textBody` | string \| null | Plain-text body |
| `htmlBody` | string \| null | HTML body |
| `hasAttachments` | boolean | Whether files are attached |
| `attachments` | BIQFile[] \| null | File references, not content: `id` (`FILE…`), `fileName`, `mimeType`, `sizeInBytes`, `md5`, `sha256`, `createdAt` |
| `headers` | object \| null | All email headers as key-value pairs |

Schemas: [typescript/actorSchemas/trigger/email.md](typescript/actorSchemas/trigger/email.md) and [typescript/schemas/file.md](typescript/schemas/file.md).

Downstream actors map the fields they need into their inputs (a code actor takes the whole message, e.g. `inputs: ${{ msg.email_trigger }}`). To classify the email with an AiActor:

```yaml
configuration:
  inputs:
    emailSubject: ${{ msg.email_trigger.subject }}
    emailBody: ${{ msg.email_trigger.textBody }}
  options:
    systemPrompt: You are an email classifier.
    prompt: |
      Subject: ${{ inputs.emailSubject }}

      Body: ${{ inputs.emailBody }}

      Classify this email as support, sales, spam or other, and list any action items.
```

## Reading attachments

`attachments` holds references. Split them and fetch each file's content with a MessageProcessorActor `downloadFileAsBase64` (or a short-lived URL with `downloadFileUrl`):

```yaml
# 1. One message per attachment
ACTR01splitAttachments:
  type: MessageProcessorActor
  msgVar: split_attachments
  configuration:
    options:
      action: split
      valueToSplit: ${{ msg.email_trigger.attachments ?? [] }}
      emitKey: attachment

# 2. Content of each file: emits { file, base64 }
ACTR01downloadAttachment:
  type: MessageProcessorActor
  msgVar: download_attachment
  configuration:
    options:
      action: downloadFileAsBase64
      file: ${{ msg.split_attachments.attachment }}

# 3. Downstream: ${{ msg.download_attachment.file.fileName }}, ${{ msg.download_attachment.file.mimeType }},
#    and Q.fromBase64AsText(msg.download_attachment.base64) for a text file
```
