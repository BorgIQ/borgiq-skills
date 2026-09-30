# actorSchemas/task/sendEmail

Generated from the platform's runtime types. Do not edit.

The options schema for the SendEmailActor.

See also: [schemas/file](../../schemas/file.md).

## actorSchemas/task/sendEmail

**Source:** `actorSchemas/task/sendEmail.ts`

```typescript
import { z } from 'zod';

import { BIQFileSchema, BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

const emailRegex = /^(?:"?([^"]*)"?\s)?(?:<)?([a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*)(>)?$/;

/** The options schema for the SendEmailActor */
export const SendEmailActorOptionsSchema = z.object({
  to: z.string().refine((value) => {
    const emails = value.split(',');
    return emails.every((email) => emailRegex.test(email.trim()));
  }, 'Invalid email address(es) provided')
    .describe('The email address(es) to send the email to, multiple emails should be a comma separated list of emails'),
  subject: z.string()
    .describe('The subject of the email to send'),
  cc: z.string().refine((value) => {
    const emails = value.split(',');
    return emails.every((email) => emailRegex.test(email.trim()));
  }, 'Invalid email address(es) provided').nullish()
    .describe('Any email address(es) to cc the email to, multiple emails should be a comma separated list of emails'),
  bcc: z.string().refine((value) => {
    const emails = value.split(',');
    return emails.every((email) => emailRegex.test(email.trim()));
  }, 'Invalid email address(es) provided').nullish()
    .describe('Any email address(es) to bcc the email to, multiple emails should be a comma separated list of emails'),
  textBody: z.string().nullish()
    .describe('The text body of the email to send (is required if html body is not defined)'),
  htmlBody: z.string().nullish()
    .describe('The html body of the email to send (is required if text body is not defined'),
  attachments: z.union([z.array(BIQFileSchema), BIQFileSchema]).nullish()
    .describe('The attachments included in the email sent'),
}).refine((data) => data.textBody || data.htmlBody, {
  error: 'Either textbody or htmlbody must be defined',
  path: ['textbody', 'htmlbody'] // specify the fields this refinement is about
});

export type SendEmailActorOptions = z.infer<typeof SendEmailActorOptionsSchema>;

export const SendEmailActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    to: {
      type: BIQJsonSchemaType.String,
      title: 'To',
      description: 'The email address(es) to send the email to, multiple emails should be a comma separated list of emails',
    },
    subject: {
      type: BIQJsonSchemaType.String,
      title: 'Subject',
      description: 'The subject of the email to send',
    },
    cc: {
      type: BIQJsonSchemaType.String,
      title: 'Cc',
      description: 'Any email address(es) to cc the email to, multiple emails should be a comma separated list of emails',
    },
    bcc: {
      type: BIQJsonSchemaType.String,
      title: 'Bcc',
      description: 'Any email address(es) to bcc the email to, multiple emails should be a comma separated list of emails',
    },
    textBody: {
      type: BIQJsonSchemaType.String,
      title: 'Text body',
      description: 'The text body of the email to send (is required if html body is not defined)',
      ui: {
        component: 'textarea',
      },
    },
    htmlBody: {
      type: BIQJsonSchemaType.String,
      title: 'HTML body',
      description: 'The html body of the email to send (is required if text body is not defined)',
      ui: {
        component: 'code',
        options: {
          language: 'html',
        },
      },
    },
    attachments: {
      type: BIQJsonSchemaType.Array,
      title: 'Attachments',
      description: 'The attachments included in the email sent',
      default: [
        '${{}}',
      ],
      items: {
        type: BIQJsonSchemaType.Object,
        default: '${{}}',
        ui: {
          component: 'file',
          options: {
            multiple: true,
          },
        },
      }
    },
  },
  required: ['to', 'subject'],
};

export const SendEmailActorResultSchema = z.object({
  meta: z.object({
    /** the borgiq email id of the email sent */
    emailId: z.string()
      .describe('The borgiq email id of the email sent'),
  }),
  to: z.string()
    .describe('The email address(es) the email was sent to'),
  cc: z.string().nullish()
    .describe('The email addresses(es) the email was cc\'d to'),
  bcc: z.string().nullish()
    .describe('The email addresses(es) the email was bcc\'d to'),
  subject: z.string()
    .describe('The subject of the email sent'),
  textBody: z.string().nullish()
    .describe('The text body of the email sent'),
  htmlBody: z.string().nullish()
    .describe('The html body of the email sent'),
  attachments: z.array(BIQFileSchema).nullish()
    .describe('The attachments included in the email sent'),
});

export type SendEmailActorResult = z.infer<typeof SendEmailActorResultSchema>;
```
