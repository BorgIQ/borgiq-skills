# Actor Schemas: HttpRequestActor

Zod schemas and TypeScript types for HttpRequestActor options, authentication types, and results.

## Table of Contents

- [actorSchemas/task/httpRequest/index.ts](#actorschemastaskhttprequestindex)

## actorSchemas/task/httpRequest/index

**Source:** `actorSchemas/task/httpRequest/index.ts`

```typescript
import { z } from 'zod';

import { BIQFileSchema, BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { AuthDataSchema } from '../../../schemas/connection.js';

export const IRequestOptionsSchema = z.object({
  
  basicAuth: z.object({
    username: z.string(),
    password: z.string(),
  }).nullish()
    .describe('The basic auth to access the proxy'),
  maxContentLength: z.number().nullish()
    .describe('The maximum content length of the response'),
  maxBodyLength: z.number().nullish()
    .describe('The maximum body length of the request'),
}).describe('The request options, only needed for advanced use cases');

export type IRequestOptions = z.infer<typeof IRequestOptionsSchema>;

/** The options for the HttpRequestActor */
export const HttpRequestActorOptionsSchema = z.object({
  auth: AuthDataSchema.nullish()
    .describe('The authentication data for the request. This can be provided as a `${{secret.[key]}}` or a `${{connection.auth}}` if they are properly set'),
  method: z.enum([
    'get', 'GET',
    'delete', 'DELETE',
    'head', 'HEAD',
    'options', 'OPTIONS',
    'post', 'POST',
    'put', 'PUT',
    'patch', 'PATCH',
    'purge', 'PURGE',
    'link', 'LINK',
    'unlink', 'UNLINK'
  ])
    .describe('The method of the http request case in-sensitive.'),
  url: z.url()
    .describe('The url to send the request to'),
  headers: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])).nullish()
    .describe('The headers to send with the request'),
  queryParams: z.record(z.string(), z.unknown()).nullish()
    .describe('The query parameters to send with the request'),
  body: z.any().nullish()
    .describe('The body to send with the request'),
  multiPartFormFiles: z.record(z.string(), z.union([BIQFileSchema, z.array(BIQFileSchema)])).nullish()
    .describe('The form file upload as a multipart form'),
  contentType: z.string().nullish()
    .describe('The content type of the body. Valid types json, xml, text, buffer, or valid HTTP Content-Type https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type'),
  responseType: z.enum(['arraybuffer', 'blob', 'document', 'json', 'text', 'stream']).nullish()
    .describe('The expected type of the response. Valid types arraybuffer, blob, document, json, text, or stream'),
  options: IRequestOptionsSchema.nullish()
    .describe('The request options, only needed for advanced use cases'),
  emitRequest: z.boolean().nullish()
    .describe('If the actor should emit the request object in the emitted message.'),
  emitBodyAsFile: z.boolean().nullish()
    .describe('If the actor should return the response as a file.'),
});

export type HttpRequestActorOptions = z.infer<typeof HttpRequestActorOptionsSchema>;

export const HttpRequestActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    url: {
      type: BIQJsonSchemaType.String,
      title: 'URL',
      description: 'The url to send the request to',
    },
    method: {
      type: BIQJsonSchemaType.String,
      title: 'Method',
      description: 'The method of the http request case in-sensitive.',
      enum: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD', 'PURGE', 'LINK', 'UNLINK'],
      default: 'GET',
      ui: {
        component: 'searchSelect',
      },
    },
    auth: {
      type: BIQJsonSchemaType.Any,
      title: 'Auth',
      description: 'The authentication data for the request. It is recommended to pass in the auth data as a secret.',
      default: '${{connection.auth}}',
    },
    headers: {
      type: BIQJsonSchemaType.Any,
      title: 'Headers',
      description: 'The headers to send with the request',
      ui: {
        options: {
          minLines: 3,
          editInModal: true,
        },
      },
    },
    queryParams: {
      type: BIQJsonSchemaType.Any,
      title: 'Query params',
      description: 'The query parameters to send with the request',
      ui: {
        options: {
          minLines: 3,
          editInModal: true,
        },
      },
    },
    body: {
      type: BIQJsonSchemaType.Any,
      title: 'Body',
      description: 'The body to send with the request',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
    multiPartFormFiles: {
      type: BIQJsonSchemaType.Any,
      title: 'Multi part form files',
      description: 'The form file upload as a multipart form',
      ui: {
        options: {
          placeholder: 'file: ${{ assets.file }}\nfiles:\n  - ${{ assets.file1 }}\n  - ${{ assets.file2 }}',
        },
      },
    },
    contentType: {
      type: BIQJsonSchemaType.String,
      title: 'Content type',
      description: 'The content type of the body. Valid types json, xml, text, buffer, or valid HTTP Content-Type https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type',
      default: 'json',
      ui: {
        component: 'suggestion',
        options: {
          suggestions: [
            'json',
            'xml',
            'text',
            'buffer',
            'text/html',
            'text/css',
            'text/javascript',
            'application/javascript',
            'application/pdf',
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/svg+xml',
            'audio/mpeg',
            'video/mp4',
          ],
          suggestionLabels: {
            'json': 'JSON',
            'xml': 'XML',
            'text': 'Text',
            'buffer': 'Raw File',
          },
          suggestionGroups: {
            'Text': ['text', 'text/html', 'text/css', 'text/javascript', 'text/plain'],
            'Application': ['json', 'xml', 'buffer', 'application/javascript', 'application/pdf'],
            'Image': ['image/jpeg', 'image/png', 'image/gif', 'image/svg+xml'],
            'Audio': ['audio/mpeg'],
            'Video': ['video/mp4'],
          },
        },
      },
    },
    responseType: {
      type: BIQJsonSchemaType.String,
      title: 'Response type',
      description: 'The expected type of the response.',
      enum: ['arraybuffer', 'document', 'json', 'text', 'stream'],
      default: 'json',
      ui: {
        component: 'searchSelect',
        options: {
          enumLabels: {
            arraybuffer: 'File',
            document: 'HTML/XML',
            json: 'JSON',
            text: 'Text',
            stream: 'Stream',
          },
        },
      },
    },
    options: {
      type: BIQJsonSchemaType.Object,
      title: 'Options',
      description: 'The request options, only needed for advanced use cases',
      properties: {
        basicAuth: {
          type: BIQJsonSchemaType.Object,
          title: 'Basic auth',
          description: 'The basic auth to access the proxy',
          properties: {
            username: {
              type: BIQJsonSchemaType.String,
              title: 'Username',
              description: 'The username to access the proxy',
            },
            password: {
              type: BIQJsonSchemaType.String,
              title: 'Password',
              description: 'The password to access the proxy',
            },
          },
          required: ['username', 'password'],
        },
        maxContentLength: {
          type: BIQJsonSchemaType.Number,
          title: 'Max content length',
          description: 'The maximum content length of the response',
        },
        maxBodyLength: {
          type: BIQJsonSchemaType.Number,
          title: 'Max body length',
          description: 'The maximum body length of the request',
        },
      },
    },
    emitRequest: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit request',
      description: 'If the actor should emit the request object in the emitted message.',
      default: false,
      ui: {
        component: 'switch',
      },
    },
    emitBodyAsFile: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Return response as file',
      description: 'If the actor should return the raw response body as a file regardless of the content type. Buffer responses will always be returned as a file',
      default: false,
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['method', 'url'],
};

/** The emitted message schema for the HttpRequestActor */
export const HttpRequestActorResultSchema = z.object({
  /** The body of the response */
  body: z.any(),
  /** The status code of the response */
  statusCode: z.number(),
  /** The headers of the response */
  headers: z.unknown(),
  /**  The HTTP request object sent. Only defined if emitRequest on the HttpRequestActor was set to true */
  request: z.object({
    url: z.string(),
    method: z.string(),
    headers: z.record(z.string(), z.unknown()),
    body: z.union([z.string(), z.record(z.string(), z.unknown())]).nullish(),
    queryParams: z.record(z.string(), z.unknown()).nullish(),
  }).nullish(),
});

export type HttpRequestActorResult = z.infer<typeof HttpRequestActorResultSchema>;
```
