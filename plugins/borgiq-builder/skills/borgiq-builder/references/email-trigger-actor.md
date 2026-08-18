# Email Trigger Actor Reference

The EmailTriggerActor starts a workflow when it receives an email at its unique email address.

## Table of Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [Email Address](#email-address)
- [Emitted Message](#emitted-message)
- [Common Patterns](#common-patterns)
- [Accessing in Downstream Actors](#accessing-in-downstream-actors)
- [Use Cases](#use-cases)
- [Quick Example](#quick-example)

## Overview

Email triggers allow workflows to be initiated by sending emails. Each email trigger has a unique email address that accepts incoming messages. Use email triggers for:

- Processing incoming emails automatically
- Building email-based workflows (support tickets, form submissions)
- Forwarding and processing emails from other accounts
- Email-to-workflow automation

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: EmailTriggerActor
    version: 1
    name: Email Trigger
    msgVar: email_trigger
    description: Receive emails to trigger the workflow
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options: {}
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Options Reference

The EmailTriggerActor currently has no configurable options. The email address is automatically generated and assigned to the actor.

| Option | Type | Description |
|--------|------|-------------|
| (none) | - | No options currently available |

## TypeScript Schema Definition

The complete TypeScript schema for EmailTriggerActor results:

```typescript
import { z } from 'zod';

/** Schema for BorgIQ file objects (e.g., FILExxxx) */
export const BIQFileSchema = z.object({
  id: z.string().regex(/^FILE[a-z0-9]+$/),
  fileName: z.string(),
  md5: z.string(),
  sha256: z.string(),
  mimeType: z.string(),
  sizeInBytes: z.number(),
  createdAt: z.string(),
});

/** The result schema for the EmailTriggerActor */
export const EmailTriggerActorResultSchema = z.object({
  messageId: z.string()
    .describe('Unique message identifier'),
  from: z.string()
    .describe('Sender email address'),
  to: z.string()
    .describe('Recipient email address'),
  cc: z.string().nullish()
    .describe('CC recipients (comma-separated)'),
  subject: z.string()
    .describe('Email subject line'),
  date: z.string()
    .describe('Email date (ISO 8601)'),
  hasAttachments: z.boolean()
    .describe('Whether the email has attachments'),
  htmlBody: z.string().nullish()
    .describe('HTML body of the email'),
  textBody: z.string().nullish()
    .describe('Plain text body of the email'),
  attachments: z.array(BIQFileSchema).nullish()
    .describe('Array of file attachments'),
  headers: z.record(z.string(), z.string()).nullish()
    .describe('All email headers as key-value pairs'),
});

export type EmailTriggerActorResult = z.infer<typeof EmailTriggerActorResultSchema>;
```

## Email Address

Each EmailTriggerActor is assigned a unique email address in the format:

```
<unique-id>@<borgiq-email-domain>
```

This email address is displayed in the BorgIQ UI when you select the trigger actor. Send emails to this address to trigger the workflow.

## Emitted Message

The email trigger emits a message containing the parsed email data:

```json
{
  "messageId": "<unique-message-id@example.com>",
  "from": "sender@example.com",
  "to": "trigger-address@borgiq.email",
  "cc": "cc@example.com",
  "subject": "Email Subject Line",
  "date": "2024-01-15T10:30:00Z",
  "hasAttachments": true,
  "textBody": "Plain text body of the email",
  "htmlBody": "<html>HTML body of the email</html>",
  "attachments": [
    {
      "id": "FILE01abc123def456",
      "fileName": "document.pdf",
      "md5": "d41d8cd98f00b204e9800998ecf8427e",
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "mimeType": "application/pdf",
      "sizeInBytes": 12345,
      "createdAt": "2024-01-15T10:30:00Z"
    }
  ],
  "headers": {
    "...all email headers..."
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `messageId` | string | Unique message identifier |
| `from` | string | Sender's email address |
| `to` | string | Recipient email address |
| `cc` | string \| null | CC recipients (comma-separated) |
| `subject` | string | Email subject line |
| `date` | string | Email date (ISO 8601) |
| `hasAttachments` | boolean | Whether the email has attachments |
| `textBody` | string \| null | Plain text body of the email |
| `htmlBody` | string \| null | HTML body of the email |
| `attachments` | array \| null | Array of file attachments (BIQFile format) |
| `headers` | object \| null | All email headers as key-value pairs |

### Attachment Object (BIQFile)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | File ID (e.g., `FILExxxx`) |
| `fileName` | string | Attachment filename |
| `md5` | string | MD5 hash of the file |
| `sha256` | string | SHA256 hash of the file |
| `mimeType` | string | MIME type |
| `sizeInBytes` | number | Size in bytes |
| `createdAt` | string | Creation timestamp |

## Common Patterns

### Process Email Subject and Body

```yaml
# In downstream actor
configuration:
  inputs:
    subject: ${{ msg.email_trigger.subject }}
    body: ${{ msg.email_trigger.textBody }}
    sender: ${{ msg.email_trigger.from }}
```

### Extract Data from Email

```typescript
// In DenoActor
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const email = req.inputs;

  // Extract information from email
  const ticketId = extractTicketId(email.subject);
  const priority = determinePriority(email.subject, email.textBody);

  return {
    results: {
      ticketId,
      priority,
      from: email.from,
      receivedAt: email.date,
      hasAttachments: email.hasAttachments,
    },
  };
}

function extractTicketId(subject: string): string | null {
  const match = subject.match(/\[TICKET-(\d+)\]/);
  return match ? match[1] : null;
}

function determinePriority(subject: string, body: string): string {
  const text = `${subject} ${body}`.toLowerCase();
  if (text.includes('urgent') || text.includes('critical')) return 'high';
  if (text.includes('low priority')) return 'low';
  return 'normal';
}
```

### Process Attachments

```typescript
// In DenoActor
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const email = req.inputs;
  const processedAttachments = [];

  for (const attachment of email.attachments || []) {
    // Decode base64 content
    const content = atob(attachment.content);

    // Process based on content type
    if (attachment.contentType === 'application/json') {
      const data = JSON.parse(content);
      processedAttachments.push({
        filename: attachment.filename,
        data,
      });
    }
  }

  return {
    results: {
      subject: email.subject,
      attachments: processedAttachments,
    },
  };
}
```

### Forward to AI for Processing

Chain with AiActor to analyze email content:

```yaml
# AiActor configuration
configuration:
  inputs:
    emailSubject: ${{ msg.email_trigger.subject }}
    emailBody: ${{ msg.email_trigger.textBody }}
  options:
    systemPrompt: |
      You are an email classifier. Analyze the email and categorize it.
    userPrompt: |
      Subject: ${{ inputs.emailSubject }}

      Body: ${{ inputs.emailBody }}

      Classify this email into one of: support, sales, spam, other.
      Extract any action items mentioned.
```

## Accessing in Downstream Actors

```yaml
# In HttpRequestActor - create ticket from email
configuration:
  inputs:
    subject: ${{ msg.email_trigger.subject }}
    body: ${{ msg.email_trigger.textBody }}
    from: ${{ msg.email_trigger.from }}
  options:
    url: https://api.ticketsystem.com/tickets
    method: POST
    body:
      title: ${{ inputs.subject }}
      description: ${{ inputs.body }}
      reporterEmail: ${{ inputs.from }}
```

## Use Cases

### Support Ticket Creation

Forward support emails to create tickets automatically:

1. EmailTriggerActor receives email
2. AiActor classifies and extracts information
3. HttpRequestActor creates ticket in support system
4. HttpRequestActor sends confirmation email

### Invoice Processing

Receive invoices via email and process them:

1. EmailTriggerActor receives invoice email
2. DenoActor extracts PDF attachment
3. AiActor extracts invoice data from PDF
4. HttpRequestActor updates accounting system

### Email-Based Commands

Execute commands via email:

1. EmailTriggerActor receives command email
2. RouterActor routes based on subject line
3. Different branches handle different commands

## Quick Example

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kd298jgr5ah2ctkngrkdkfn0:
    type: EmailTriggerActor
    version: 1
    name: Support Email Trigger
    msgVar: support_email_trigger
    description: Receive support emails to create tickets automatically
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options: {}
    schemas: {}
    id: ACTR01kd298jgr5ah2ctkngrkdkfn0
    position:
      x: 0
      'y': 0
    edges: {}
```
