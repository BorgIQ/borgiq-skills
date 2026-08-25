# Actor Schemas: Trigger Actors

Zod schemas and TypeScript types for all trigger actor options and results (Button, Webhook, Email, Interface, App, Scheduled, Callable).

## Table of Contents

- [actorSchemas/trigger/app.ts](#actorschemastriggerapp)
- [actorSchemas/trigger/button.ts](#actorschemastriggerbutton)
- [actorSchemas/trigger/callable.ts](#actorschemastriggercallable)
- [actorSchemas/trigger/email.ts](#actorschemastriggeremail)
- [actorSchemas/trigger/interface.ts](#actorschemastriggerinterface)
- [actorSchemas/trigger/permissionsPolicy.ts](#actorschemastriggerpermissionspolicy)
- [actorSchemas/trigger/reactApp.ts](#actorschemastriggerreactapp)
- [actorSchemas/trigger/scheduled.ts](#actorschemastriggerscheduled)
- [actorSchemas/trigger/triggerConfig.ts](#actorschemastriggertriggerconfig)
- [actorSchemas/trigger/universalTrigger.ts](#actorschemastriggeruniversaltrigger)
- [actorSchemas/trigger/webhook.ts](#actorschemastriggerwebhook)

## actorSchemas/trigger/app

**Source:** `actorSchemas/trigger/app.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchemaType, BIQJsonSchema } from '../../schemas/index.js';
import { BIQFileSchema } from '../../schemas/file.js';
import { PermissionsPolicyDirective, PermissionsPolicyDirectiveZodSchema } from './permissionsPolicy.js';

/** Content field that can be either an inline string or a BIQFile reference */
const AppContentFieldSchema = z.union([z.string(), BIQFileSchema]);

/** The options schema for the AppTriggerActor */
export const AppTriggerActorOptionsSchema = z.object({
  /** HTML content or file */
  html: AppContentFieldSchema
    .describe('The HTML content for the app. Can be an inline string or a BIQFile reference.'),
  /** CSS content or file */
  css: AppContentFieldSchema.nullish()
    .describe('CSS styles for the app. Can be an inline string or a BIQFile reference.'),
  /** JavaScript content or file */
  script: AppContentFieldSchema.nullish()
    .describe('JavaScript code for the app. Can be an inline string or a BIQFile reference.'),
  /** allowed domains for external scripts */
  allowedScriptDomains: z.array(z.string()).nullish(),
  /** allowed domains for external stylesheets */
  allowedStyleDomains: z.array(z.string()).nullish(),
  /** Enable unsafe-inline for scripts, bypassing hash verification */
  allowInlineScripts: z.boolean().nullish(),
  /** Enable unsafe-inline for styles, bypassing hash verification */
  allowInlineStyling: z.boolean().nullish(),
  /** Permissions-Policy directives to enable */
  allowedPermissions: z.array(PermissionsPolicyDirectiveZodSchema).nullish(),
});

export type AppTriggerActorOptions = z.infer<typeof AppTriggerActorOptionsSchema>;

export const AppTriggerActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    html: {
      type: BIQJsonSchemaType.Any,
      title: 'HTML',
      description: 'The HTML content for the app. Can be an inline string or a BIQFile.',
      ui: {
        component: 'modal',
      },
    },
    css: {
      type: BIQJsonSchemaType.Any,
      title: 'CSS',
      description: 'CSS styles for the app. Can be an inline string or a BIQFile.',
      ui: {
        component: 'modal',
      },
    },
    script: {
      type: BIQJsonSchemaType.Any,
      title: 'Script',
      description: 'JavaScript code for the app. Can be an inline string or a BIQFile.',
      ui: {
        component: 'modal',
      },
    },
    allowInlineScripts: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Allow inline scripts',
      description: 'Uses \'unsafe-inline\' in the CSP script-src directive instead of hashed values. This is less secure but may be needed for dynamically generated scripts.',
      ui: {
        component: 'switch',
      },
    },
    allowInlineStyling: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Allow inline styling',
      description: 'Uses \'unsafe-inline\' in the CSP style-src directive instead of hashed values. This is less secure but may be needed for dynamically generated styles.',
      ui: {
        component: 'switch',
      },
    },
    allowedScriptDomains: {
      type: BIQJsonSchemaType.Array,
      title: 'Allowed script domains',
      description: 'Allowed domains for external scripts loaded via CSP.',
      items: {
        type: BIQJsonSchemaType.String,
      },
    },
    allowedStyleDomains: {
      type: BIQJsonSchemaType.Array,
      title: 'Allowed style domains',
      description: 'Allowed domains for external stylesheets loaded via CSP.',
      items: {
        type: BIQJsonSchemaType.String,
      },
    },
    allowedPermissions: {
      type: BIQJsonSchemaType.Array,
      title: 'Allowed permissions',
      description: 'Permissions-Policy directives to enable for the iframe.',
      items: {
        type: BIQJsonSchemaType.String,
        enum: Object.values(PermissionsPolicyDirective),
      },
      uniqueItems: true,
    },
  },
  required: ['html'],
};

export const AppTriggerActorResultSchema = z.object({});

export type AppTriggerActorResult = z.infer<typeof AppTriggerActorResultSchema>;
```

## actorSchemas/trigger/button

**Source:** `actorSchemas/trigger/button.ts`

```typescript
import { z } from 'zod';

export const ButtonTriggerActorOptionsSchema = z.unknown().describe('What the message should be');

export type ButtonTriggerActorOptions = z.infer<typeof ButtonTriggerActorOptionsSchema>;

export const ButtonTriggerActorResultSchema = z.unknown().describe('The options of the button trigger');

export type ButtonTriggerActorResult = z.infer<typeof ButtonTriggerActorResultSchema>;
```

## actorSchemas/trigger/callable

**Source:** `actorSchemas/trigger/callable.ts`

```typescript
import { z } from 'zod';

/** The emitted message schema for the CallableTriggerActor */
export const CallableTriggerActorResultSchema = z.any();

export type CallableTriggerActorResult = z.infer<typeof CallableTriggerActorResultSchema>;
```

## actorSchemas/trigger/email

**Source:** `actorSchemas/trigger/email.ts`

```typescript
import { z } from 'zod';
import { BIQFileSchema } from '../../schemas/index.js';

export const EmailTriggerActorResultSchema = z.object({
  messageId: z.string(),
  from: z.string(),
  to: z.string(),
  cc: z.string().nullish(),
  subject: z.string(),
  date: z.string(),
  hasAttachments: z.boolean(),
  htmlBody: z.string().nullish(),
  textBody: z.string().nullish(),
  attachments: z.array(BIQFileSchema).nullish(),
  headers: z.record(z.string(), z.string()).nullish(),
});

export type EmailTriggerActorResult = z.infer<typeof EmailTriggerActorResultSchema>;
```

## actorSchemas/trigger/interface

**Source:** `actorSchemas/trigger/interface.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchemaType, BIQJsonSchema, BIQInterfacePageDataSchema } from '../../schemas/index.js';

/** The options schema for the WebhookTriggerActor */
export const InterfaceTriggerActorOptionsSchema = z.object({
  /** The page to render for the interface trigger */
  page: BIQInterfacePageDataSchema
    .describe('The page data to render for the interface trigger'),
  /** The default values to inject into the url as query params */
  defaultValues: z.record(z.string(), z.any()).nullish()
    .describe('The default values to pass to the interface trigger form to build the form'),
  /** auto submit the form after it has been opened after a certain number of seconds */
  autoSubmitAfterSeconds: z.number().int().min(0).nullish()
    .describe('auto submit the form after it has been opened after a certain number of seconds'),
  /** What page to redirect to when the interface trigger form is submitted */
  onSubmit: z.discriminatedUnion('type', [
    z.object({
      /** when the interface trigger form is successfully submitted, redirect to the next interface rendered in the flow  */
      type: z.literal('nextInterface')
        .describe('when the interface trigger form is successfully submitted, redirect to the next interface rendered in the flow'),
      /** The message to show while the next interface is loading */
      loadingMessage: z.string().nullish()
        .describe('The message to show while the next interface is loading'),
    }),
    z.object({
      /** when the interface trigger form is successfully submitted, show a success message */
      type: z.literal('successMessage')
        .describe('when the interface trigger form is successfully submitted, show a success message'),
      /** The message to show when the interface trigger form is successfully submitted */
      successMessage: z.string().nullish()
        .describe('The message to show when the interface trigger form is successfully submitted'),
    }),
    z.object({
      /** when the interface trigger form is successfully submitted, redirect to a url */
      type: z.literal('urlRedirect')
        .describe('when the interface trigger form is successfully submitted, redirect to a url'),
      /** The url to redirect to when the interface trigger form is successfully submitted */
      url: z.url()
        .describe('The url to redirect to when the interface trigger form is successfully submitted'),
    })
  ]),
  /** Whether to show real-time flow progress and actor status on the waiting page. Requires onSubmit type to be nextInterface. */
  showProgressStatus: z.boolean().nullish()
    .describe('Show real-time flow progress and actor status on the waiting page. Requires onSubmit type to be nextInterface.'),
});

export type InterfaceTriggerActorOptions = z.infer<typeof InterfaceTriggerActorOptionsSchema>;

export const InterfaceTriggerActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    page: {
      type: BIQJsonSchemaType.Any,
      title: 'Page',
      description: 'The page data to render for the interface trigger',
      ui: {
        component: 'modal',
        options: {
          language: 'yaml',
        },
      }
    },
    autoSubmitAfterSeconds: {
      type: BIQJsonSchemaType.Integer,
      title: 'Auto submit after seconds',
      description: 'auto submit the form after it has been opened after a certain number of seconds'
    },
    onSubmit: {
      discriminatorKey: 'type',
      anyOf: [
        {
          title: 'On submit',
          description: 'What to do when the interface form is submitted',
          type: BIQJsonSchemaType.Object,
          properties: {
            type: {
              type: BIQJsonSchemaType.String,
              title: 'Type',
              description: 'The type of on submit action',
              const: 'nextInterface',
              default: 'Next Interface',
            },
            loadingMessage: {
              type: BIQJsonSchemaType.String,
              title: 'Loading message',
              description: 'The message to show while the next interface is loading',
              ui: {
                options: {
                  placeholder: 'Loading...',
                },
              },
            },
          },
          required: ['type'],
        },
        {
          type: BIQJsonSchemaType.Object,
          properties: {
            type: {
              type: BIQJsonSchemaType.String,
              title: 'Type',
              description: 'The type of on submit action',
              const: 'successMessage',
              default: 'Success Message',
            },
            successMessage: {
              type: BIQJsonSchemaType.String,
              title: 'Success message',
              description: 'The message to show when the interface form is successfully submitted',
              ui: {
                options: {
                  placeholder: 'Success!',
                },
              },
            },
          },
          required: ['type'],
        },
        {
          type: BIQJsonSchemaType.Object,
          properties: {
            type: {
              type: BIQJsonSchemaType.String,
              title: 'Type',
              description: 'The type of on submit action',
              const: 'urlRedirect',
              default: 'URL Redirect',
            },
            url: {
              type: BIQJsonSchemaType.String,
              title: 'URL',
              description: 'The url to redirect to when the interface form is successfully submitted',
              format: 'uri',
            },
          },
          required: ['type', 'url'],
        },
      ],
    },
    showProgressStatus: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Show progress status',
      description: 'Show real-time flow progress and actor status on the waiting page. Requires onSubmit type to be nextInterface.',
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['page', 'onSubmit']
};

export const InterfaceTriggerActorResultSchema = z.object({
  meta: z.object({
    interfaceId: z.string()
      .describe('The interface id that was used to submit the form'),
    submissionInterfaceId: z.string()
      .describe('The interface id that was used to submit the form and will be used to render the next page'),
    ipAddress: z.string().optional()
      .describe('The IP address of the user who submitted the form'),
  }),
  body: z.record(z.string(), z.any())
    .describe('The body of the interface submission'),
});

export type InterfaceTriggerActorResult = z.infer<typeof InterfaceTriggerActorResultSchema>;
```

## actorSchemas/trigger/permissionsPolicy

**Source:** `actorSchemas/trigger/permissionsPolicy.ts`

```typescript
import { z } from 'zod';

/**
 * Valid Permissions-Policy directives that can be enabled for iframes.
 * These control access to browser APIs and features.
 * @see https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy
 */
export enum PermissionsPolicyDirective {
  /** Access to the Accelerometer interface */
  Accelerometer = 'accelerometer',
  /** Access to the AmbientLightSensor interface */
  AmbientLightSensor = 'ambient-light-sensor',
  /** Autoplay of media requested through HTMLMediaElement */
  Autoplay = 'autoplay',
  /** Access to the BatteryManager interface */
  Battery = 'battery',
  /** Access to video input devices */
  Camera = 'camera',
  /** Access to read clipboard contents via Clipboard API */
  ClipboardRead = 'clipboard-read',
  /** Access to write to clipboard via Clipboard API */
  ClipboardWrite = 'clipboard-write',
  /** Access to use the Screen Capture API (getDisplayMedia) */
  DisplayCapture = 'display-capture',
  /** Access to the Encrypted Media Extensions API */
  EncryptedMedia = 'encrypted-media',
  /** Access to the Fullscreen API */
  Fullscreen = 'fullscreen',
  /** Access to the Geolocation API */
  Geolocation = 'geolocation',
  /** Access to the Gyroscope interface */
  Gyroscope = 'gyroscope',
  /** Access to the Magnetometer interface */
  Magnetometer = 'magnetometer',
  /** Access to audio input devices */
  Microphone = 'microphone',
  /** Access to the Web MIDI API */
  Midi = 'midi',
  /** Access to the Payment Request API */
  Payment = 'payment',
  /** Access to the Picture-in-Picture API */
  PictureInPicture = 'picture-in-picture',
  /** Access to the Web Authentication API */
  PublicKeyCredentialsGet = 'publickey-credentials-get',
  /** Access to the Screen Wake Lock API */
  ScreenWakeLock = 'screen-wake-lock',
  /** Access to the WebUSB API */
  Usb = 'usb',
  /** Access to the Web Share API */
  WebShare = 'web-share',
  /** Access to WebXR Device API */
  XrSpatialTracking = 'xr-spatial-tracking',
}

/** Zod schema for PermissionsPolicyDirective enum */
export const PermissionsPolicyDirectiveZodSchema = z.nativeEnum(PermissionsPolicyDirective);
```

## actorSchemas/trigger/reactApp

**Source:** `actorSchemas/trigger/reactApp.ts`

```typescript
import { z } from 'zod';

// Import from the concrete leaf module, NOT the `../../schemas/index.js` barrel: the barrel pulls in
// `runtime.js`, which imports THIS file (for ReactAppCodeDirSchema, added in §4.1). Going through the
// barrel forms a cycle that leaves `BIQJsonSchemaType` undefined when the JSON-schema literal below
// evaluates at module load. jsonSchema.js is a dependency-free leaf, so importing it directly is cycle-safe.
import { BIQActorType } from '../../canvas.js';
import { BIQJsonSchemaType } from '../../schemas/jsonSchema.js';
import type { BIQJsonSchema } from '../../schemas/jsonSchema.js';
import { BIQFileSchema } from '../../schemas/file.js';
import { idSchema } from '../../schemas/idSchema.js';
import { PermissionsPolicyDirective, PermissionsPolicyDirectiveZodSchema } from './permissionsPolicy.js';
import { CodeDirSchema, CodeFileSchema, normalizeCodePath } from '../codeDir.js';
import type { CodeDir, CodeFile } from '../codeDir.js';

/** Maximum number of interpolatable overlay files in `configuration.options.files`. */
export const MAX_OPTIONS_FILES = 50;
/** Maximum number of endpoints declared on a ReactAppTriggerActor (Phase II). */
export const MAX_REACT_APP_ENDPOINTS = 50;

/**
 * React-app back-compat aliases over the generic `codeDir` module (`../codeDir.ts`), which owns
 * the path normalizer, the file schema and the size caps for every actor type that carries a
 * `configuration.codeDir`. React-app keeps the plain schema — no entrypoint requirement and no
 * reserved paths: its tree never shares a directory with runtime files, it is materialized into
 * a per-build temp dir.
 */
export const ReactAppCodeFileSchema = CodeFileSchema;
export type ReactAppCodeFile = CodeFile;
export const ReactAppCodeDirSchema = CodeDirSchema;
export type ReactAppCodeDir = CodeDir;
export const normalizeReactAppPath = normalizeCodePath;

/** An interpolatable overlay file: inline text OR a BIQFile handle (typically `${{ assets.<key> }}`). */
export const ReactAppOptionsFileSchema = z.object({
  /** path relative to the project root; same path rules as codeDir */
  path: z.string().min(1).max(255),
  /** inline text OR a BIQFile handle (typically produced by `${{ assets.<key> }}`) */
  content: z.union([z.string(), BIQFileSchema]),
});

export type ReactAppOptionsFile = z.infer<typeof ReactAppOptionsFileSchema>;

/**
 * A named endpoint bound to a webhook-capable trigger — a WebhookTriggerActor, or a
 * UniversalTriggerActor with its webhook source enabled (Phase II — §5.1, §15.3.5, §18).
 * Coordinates are slugs (CallFlow parity — callFlow.ts stores slugs); absent workspace/canvas
 * default to the app actor's own. Same-org only. Because options are interpolatable, the string
 * fields may carry `${{ }}` expressions resolved at build time (§15.3.5).
 */
export const ReactAppEndpointSchema = z.object({
  /** unique within this actor's endpoint list; the hook lookup key */
  name: z.string().regex(/^[a-zA-Z_][a-zA-Z0-9_]*$/, 'endpoint name must be a valid identifier'),
  description: z.string().nullish(),
  /** the target trigger: a WebhookTriggerActor, or a UniversalTriggerActor with its webhook source enabled */
  actorId: idSchema.actorId,
  /** target workspace slug; absent = the app actor's own workspace. Same-org only. */
  workspaceSlug: z.string().nullish(),
  /** target canvas slug; absent = the app actor's own canvas. */
  canvasSlug: z.string().nullish(),
});

export type ReactAppEndpoint = z.infer<typeof ReactAppEndpointSchema>;

/** The options schema for the ReactAppTriggerActor (interpolated at build time). */
export const ReactAppTriggerActorOptionsSchema = z.object({
  /** interpolatable file overlay: asset-backed or templated files (wins on path collision) */
  files: z.array(ReactAppOptionsFileSchema).max(MAX_OPTIONS_FILES).nullish(),
  /** Phase II — named webhook-trigger endpoints consumed via `useEndpoint` (§15.4) */
  endpoints: z.array(ReactAppEndpointSchema).max(MAX_REACT_APP_ENDPOINTS).nullish(),
  /** allowed domains for external scripts */
  allowedScriptDomains: z.array(z.string()).nullish(),
  /** allowed domains for external stylesheets */
  allowedStyleDomains: z.array(z.string()).nullish(),
  /** Enable unsafe-inline for scripts, bypassing hash verification */
  allowInlineScripts: z.boolean().nullish(),
  /** Enable unsafe-inline for styles, bypassing hash verification */
  allowInlineStyling: z.boolean().nullish(),
  /** Permissions-Policy directives to enable */
  allowedPermissions: z.array(PermissionsPolicyDirectiveZodSchema).nullish(),
});

export type ReactAppTriggerActorOptions = z.infer<typeof ReactAppTriggerActorOptionsSchema>;

/**
 * Drives the options form in the right-hand configuration panel. `files` is editable here as a
 * structured path/content array (and also, more richly, via the file tree in the full-page React-app
 * editor — both write the same `options.files`). `endpoints` is editable here as a structured array
 * of slug-based coordinates via a workspace → canvas → webhook-trigger picker (§15.6.6); save-time
 * validation catches bad references, tolerating `${{ }}` expressions (resolved at build, §15.3.5).
 */
export const ReactAppTriggerActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    files: {
      type: BIQJsonSchemaType.Array,
      title: 'Files',
      description: 'Asset-backed or templated files overlaid onto the project at build time (they win over the source tree on a path collision). Manage them here or via the file tree in the full-page editor.',
      items: {
        type: BIQJsonSchemaType.Object,
        properties: {
          path: {
            type: BIQJsonSchemaType.String,
            title: 'Path',
            description: 'Project-relative path, e.g. src/assets/logo.png or src/assets/hero.jpg. Import it from your source (e.g. import logo from \'./assets/logo.png\'); avoid public/.',
          },
          content: {
            type: BIQJsonSchemaType.String,
            title: 'Content',
            description: 'Reference an uploaded asset with ${{ assets["<key>"] }} (injected at build), or provide inline text.',
            ui: {
              options: {
                placeholder: '${{ assets["my-asset"] }}',
              },
            },
          },
        },
        required: ['path'],
      },
    },
    endpoints: {
      type: BIQJsonSchemaType.Array,
      title: 'Endpoints',
      description: 'Named webhook-trigger endpoints the app calls via useEndpoint("<name>"). Target a webhook-capable trigger — a WebhookTrigger, or a UniversalTrigger with its webhook source enabled (use authorizationLevel: "apps") — on this canvas, or another canvas/workspace in the same org — leave workspace/canvas blank for this canvas. Coordinates are slugs. Endpoint changes take effect after the next Build.',
      items: {
        type: BIQJsonSchemaType.Object,
        properties: {
          name: {
            type: BIQJsonSchemaType.String,
            title: 'Name',
            description: 'The lookup key passed to useEndpoint(). Must be a valid identifier (letters, digits, underscore; not starting with a digit).',
            pattern: '^[a-zA-Z_][a-zA-Z0-9_]*$',
          },
          actorId: {
            type: BIQJsonSchemaType.String,
            title: 'Trigger',
            description: 'The target trigger — a WebhookTriggerActor, or a UniversalTriggerActor with its webhook source enabled.',
            // the picker also writes workspaceSlug / canvasSlug below; blank coordinates target the
            // app actor's own canvas. `capability` is what narrows UniversalTriggers to the ones
            // whose webhook source is on and that carry a routing key — a configuration rule the
            // actorTypes list alone cannot express.
            ui: {
              component: 'actorSelect',
              options: {
                actorTypes: [BIQActorType.WebhookTriggerActor, BIQActorType.UniversalTriggerActor],
                capability: 'webhookEndpointTarget',
                workspaceKey: 'workspaceSlug',
                canvasKey: 'canvasSlug',
                entityLabel: 'trigger',
              },
            },
          },
          workspaceSlug: {
            type: BIQJsonSchemaType.String,
            title: 'Workspace',
            description: 'Optional. The target workspace slug; blank = this app\'s workspace. Same org only.',
            ui: { options: { placeholder: 'blank = this workspace' } },
          },
          canvasSlug: {
            type: BIQJsonSchemaType.String,
            title: 'Canvas',
            description: 'Optional. The target canvas slug; blank = this app\'s canvas.',
            ui: { options: { placeholder: 'blank = this canvas' } },
          },
          description: {
            type: BIQJsonSchemaType.String,
            title: 'Description',
            description: 'Optional note about what this endpoint does.',
          },
        },
        required: ['name', 'actorId'],
      },
    },
    allowInlineScripts: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Allow inline scripts',
      description: 'Uses \'unsafe-inline\' in the CSP script-src directive instead of hashed values. This is less secure but may be needed for dynamically generated scripts.',
      ui: {
        component: 'switch',
      },
    },
    allowInlineStyling: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Allow inline styling',
      description: 'Uses \'unsafe-inline\' in the CSP style-src directive instead of hashed values. This is less secure but may be needed for dynamically generated styles.',
      ui: {
        component: 'switch',
      },
    },
    allowedScriptDomains: {
      type: BIQJsonSchemaType.Array,
      title: 'Allowed script domains',
      description: 'Allowed domains for external scripts loaded via CSP.',
      items: {
        type: BIQJsonSchemaType.String,
      },
    },
    allowedStyleDomains: {
      type: BIQJsonSchemaType.Array,
      title: 'Allowed style domains',
      description: 'Allowed domains for external stylesheets loaded via CSP.',
      items: {
        type: BIQJsonSchemaType.String,
      },
    },
    allowedPermissions: {
      type: BIQJsonSchemaType.Array,
      title: 'Allowed permissions',
      description: 'Permissions-Policy directives to enable for the iframe.',
      items: {
        type: BIQJsonSchemaType.String,
        enum: Object.values(PermissionsPolicyDirective),
      },
      uniqueItems: true,
    },
  },
  required: [],
};

export const ReactAppTriggerActorResultSchema = z.object({});

export type ReactAppTriggerActorResult = z.infer<typeof ReactAppTriggerActorResultSchema>;
```

## actorSchemas/trigger/scheduled

**Source:** `actorSchemas/trigger/scheduled.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema } from '../../schemas/jsonSchema.js';

export const ScheduleTriggerActorMemory: { ltm?: boolean; stm?: boolean } = {
  ltm: true,
};

/**
 * The options schema for the ScheduledTriggerActor.
 *
 * Schedule has no interpolatable fields — `cron`/`timezone` are static and live in
 * `configuration.schedule` (see {@link ScheduleConfigSchema}). So options is empty.
 */
export const ScheduledTriggerActorOptionsSchema = z.object({});

export type ScheduledTriggerActorOptions = z.infer<typeof ScheduledTriggerActorOptionsSchema>;

export const ScheduledTriggerActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {},
};

export const ScheduledTriggerActorResultSchema = z.object({
  lastTriggeredAt: z.iso.datetime().nullable()
    .describe('The last time the trigger was triggered'),
  triggeredAt: z.iso.datetime()
    .describe('The time the trigger was triggered'),
});

export type ScheduledTriggerActorResult = z.infer<typeof ScheduledTriggerActorResultSchema>;
```

## actorSchemas/trigger/triggerConfig

**Source:** `actorSchemas/trigger/triggerConfig.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType, BIQObjectJsonSchema } from '../../schemas/jsonSchema.js';
import { BIQWebhookAuthorizationLevel } from '../../canvas.js';

/**
 * Shared building blocks for the unified trigger-actor config data model.
 *
 * The webhook/schedule configuration is split along the interpolation boundary that
 * already exists in the platform: `configuration.options` is the interpolated blob
 * (run through the `${{ }}` engine in the runtime, with the request in scope), while
 * structured config siblings (like `connection`) are never interpolated.
 *
 *  - STATIC, admission-consumed fields live in `configuration.webhook` / `configuration.schedule`
 *    (these schemas). They must be literals — expressions are rejected.
 *  - INTERPOLATABLE behavior fields live inside the interpolated `options` blob, under
 *    `options.webhook` ({@link WebhookBehaviorOptionsSchema}).
 */

// the regex of the cron schedule is from https://gist.github.com/Aterfax/401875eb3d45c9c114bbef69364dd045
export const cronPattern = /^((((\d+,)+\d+|(\d+(\/|-|#)\d+)|\d+L?|\*(\/\d+)?|L(-\d+)?|\?|[A-Z]{3}(-[A-Z]{3})?) ?){5})|(@(annually|yearly|monthly|weekly|daily|hourly|reboot))|(@every (\d+(m|h))+)$/;

// list of all the supported timezones
export const timezoneValues = Intl.supportedValuesOf('timeZone');

/** Matches a string that is a single `${{ ... }}` interpolation expression. */
export const EXPRESSION_REGEX = /^\$\{\{\s*((?:(?!\$\{\{)[\s\S])*?)\s*\}\}$/;

/** Adds a validation issue when a static (non-interpolatable) string field holds a `${{ }}` expression. */
const rejectExpression = (value: unknown, ctx: z.RefinementCtx, field: string): void => {
  if (typeof value === 'string' && EXPRESSION_REGEX.test(value)) {
    ctx.addIssue({
      code: 'custom',
      message: `${field} must be a literal value and cannot be an interpolated \${{ }} expression`,
      path: [field],
    });
  }
};

/**
 * STATIC webhook config — lives at `configuration.webhook` (sibling of `options`/`connection`).
 * Consumed by the orchestrator at admission (routing, auth, method gate, wait bound, source gate),
 * so every field must be a literal and is DB-queryable. `enabled` is only meaningful for the
 * UniversalTriggerActor; the standalone WebhookTriggerActor is always enabled when present.
 */
export const WebhookConfigSchema = z.object({
  triggerKey: z.string().optional()
    .describe('The unique key in the webhook URL used to route requests to this actor.'),
  authorizationLevel: z.enum(BIQWebhookAuthorizationLevel).optional()
    .describe('Who can call this webhook. \'public\' allows anyone, \'apps\' requires a valid app webhook token.'),
  allowedMethods: z.array(z.enum(['get', 'post', 'put', 'delete'])).optional()
    .describe('HTTP methods accepted by the webhook URL.'),
  responseTimeout: z.number().gte(1).lte(60).optional()
    .describe('How long (seconds) the request is held open waiting for a WebhookResponse actor. Max 60s, defaults to 30s.'),
  enabled: z.boolean().optional()
    .describe('UniversalTriggerActor only: when false the webhook URL returns 404 and no flowruns are created.'),
}).superRefine((data, ctx) => {
  rejectExpression(data.triggerKey, ctx, 'triggerKey');
});

export type WebhookConfig = z.infer<typeof WebhookConfigSchema>;

/**
 * STATIC schedule config — lives at `configuration.schedule`. Schedule has no interpolatable
 * fields: `cron` is read at admission to register the cron job (and the engine cannot interpolate
 * it), `timezone`/`enabled` are admission-time too. So all of it is static — there is no
 * `options.schedule`.
 */
export const ScheduleConfigSchema = z.object({
  cron: z.string().regex(cronPattern).optional()
    .describe('The cron schedule. Cannot be an interpolated value.'),
  timezone: z.enum(timezoneValues).optional()
    .describe('The timezone used to evaluate the cron expression.'),
  enabled: z.boolean().optional()
    .describe('UniversalTriggerActor only: when false no cron job is registered.'),
  preventOverlappingFlowruns: z.boolean().optional()
    .describe('ScheduledTriggerActor only (ignored by UniversalTriggerActor): when true, a scheduled flowrun is skipped if the previous flowrun is still in progress.'),
}).superRefine((data, ctx) => {
  rejectExpression(data.cron, ctx, 'cron');
});

export type ScheduleConfig = z.infer<typeof ScheduleConfigSchema>;

/**
 * The lifecycle transitions deliverable on the `lifecycle` trigger event.
 *
 * Single source of truth: the TriggerEvent variant, the flowrun payload schema, the API input
 * schema, and the lambda runtime's `buildTrigger` check all derive from this const. The vocabulary
 * grows by extending this list, never by adding a TriggerEvent union member. Lives here (rather
 * than beside the TriggerEvent variant in `schemas/trigger.ts`) because both `schemas/trigger.ts`
 * and `schemas/runtime.ts` need it, and this module is downstream of neither — importing it from
 * `schemas/trigger.ts` would make those two modules circular and TDZ-crash at module init.
 */
export const LIFECYCLE_TRIGGER_EVENTS = ['canvas-enabled', 'canvas-disabled'] as const;

export type LifecycleTriggerEvent = typeof LIFECYCLE_TRIGGER_EVENTS[number];

/**
 * Display copy for each lifecycle event, used by the editor's subscription checkboxes.
 *
 * Typed as an exhaustive `Record` on purpose: adding a value to {@link LIFECYCLE_TRIGGER_EVENTS}
 * without adding its metadata here is a compile error rather than an unlabelled checkbox.
 */
export const LIFECYCLE_TRIGGER_EVENT_META: Record<LifecycleTriggerEvent, { label: string; description: string }> = {
  'canvas-enabled': { label: 'Canvas enabled', description: 'Fired when the canvas is deployed.' },
  'canvas-disabled': { label: 'Canvas disabled', description: 'Fired when the canvas is undeployed.' },
};

/**
 * STATIC lifecycle config — lives at `configuration.lifecycle`. Like schedule, lifecycle
 * has no interpolatable fields: `events` is the subscription list read at fire time, so all of it
 * is static and there is no `options.lifecycle`.
 *
 * Subscription is PER EVENT, not a single on/off flag: {@link LIFECYCLE_TRIGGER_EVENTS} is the
 * growth axis for this feature, so a flag would silently opt every subscribed actor into events
 * added later. Absent block, absent `events`, and `events: []` all mean unsubscribed.
 */
export const LifecycleConfigSchema = z.object({
  events: z.array(z.enum(LIFECYCLE_TRIGGER_EVENTS)).optional()
    .describe('UniversalTriggerActor only: the lifecycle events this actor is subscribed to. Absent or empty means the actor receives none.'),
});

export type LifecycleConfig = z.infer<typeof LifecycleConfigSchema>;

/**
 * Whether an actor's static lifecycle config subscribes it to `event`. The single place the
 * subscription question is answered — the fire gate in `Trigger.lifecycle()` uses it, and the
 * canvas-deploy engine will use it to pick out subscribed actors before fanning out.
 */
export const isSubscribedToLifecycleEvent = (config: LifecycleConfig | undefined, event: LifecycleTriggerEvent): boolean =>
  config?.events?.includes(event) === true;

/**
 * INTERPOLATABLE webhook behavior — lives inside the interpolated `options` blob at
 * `options.webhook`. Reused by the standalone WebhookTriggerActor's options and by the
 * UniversalTriggerActor's options. Fields accept their literal type OR a `${{ }}` string so
 * an un-interpolated expression validates at save time; the runtime resolves it before reading.
 */
export const WebhookBehaviorOptionsSchema = z.object({
  respondImmediately: z.union([z.boolean(), z.string()]).nullish()
    .describe('If true, the configured response is returned immediately; otherwise a downstream WebhookResponse actor must respond.'),
  emitRawBody: z.union([z.boolean(), z.string()]).nullish()
    .describe('If true the raw request body is included on the emitted event.request.rawBody.'),
  response: z.object({
    statusCode: z.union([z.number(), z.string()]),
    headers: z.record(z.string(), z.unknown()).nullish(),
    body: z.unknown(),
  }).nullish()
    .describe('The response returned when respondImmediately is true.'),
});

export type WebhookBehaviorOptions = z.infer<typeof WebhookBehaviorOptionsSchema>;

/** JSON Schema for the static `configuration.webhook` editor (Settings sub-group — no `${{ }}` toggle). */
export const WebhookConfigJsonSchema: BIQJsonSchema = {
  properties: {
    triggerKey: {
      type: BIQJsonSchemaType.String,
      title: 'Trigger key',
      description: 'The unique key in the webhook URL used to route requests to this actor.',
    },
    authorizationLevel: {
      type: BIQJsonSchemaType.String,
      title: 'Authorization level',
      description: 'Control who can call this webhook.',
      enum: [BIQWebhookAuthorizationLevel.Public, BIQWebhookAuthorizationLevel.Apps],
    },
    allowedMethods: {
      type: BIQJsonSchemaType.Array,
      title: 'Allowed methods',
      description: 'HTTP methods accepted by the webhook URL.',
      items: { type: BIQJsonSchemaType.String, enum: ['get', 'post', 'put', 'delete'] },
      uniqueItems: true,
    },
    responseTimeout: {
      type: BIQJsonSchemaType.Number,
      title: 'Response timeout',
      description: 'How long (seconds) the request is held open waiting for a Webhook Response actor. Maximum 60s, defaults to 30s.',
      minimum: 1,
      maximum: 60,
      default: 30,
    },
  },
};

/** JSON Schema for the static `configuration.schedule` editor. */
export const ScheduleConfigJsonSchema: BIQJsonSchema = {
  properties: {
    cron: {
      type: BIQJsonSchemaType.String,
      title: 'Schedule',
      description: 'The cron schedule to use for the trigger. Warning: You cannot use interpolated values in the schedule.',
      pattern: cronPattern.source,
    },
    timezone: {
      type: BIQJsonSchemaType.String,
      title: 'Timezone',
      description: 'The timezone used to evaluate the cron expression.',
      enum: timezoneValues,
      default: 'America/New_York',
      ui: { component: 'searchSelect' },
    },
  },
};

/** JSON Schema for the interpolatable `options.webhook` behavior editor (Response sub-group — with `${{ }}` toggle). */
export const WebhookBehaviorOptionsJsonSchema: BIQObjectJsonSchema = {
  type: BIQJsonSchemaType.Object,
  title: 'Webhook',
  description: 'Behavior for forming the webhook response. These fields are interpolated at runtime with the request in scope.',
  properties: {
    respondImmediately: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Respond immediately',
      description: 'If true, the configured response is returned immediately. If false a downstream Webhook Response actor must respond.',
      ui: { component: 'switch' },
    },
    emitRawBody: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit raw body',
      description: 'Include the raw request body on the emitted event.request.rawBody.',
      ui: { component: 'switch' },
    },
    response: {
      type: BIQJsonSchemaType.Object,
      title: 'Response',
      description: 'Response returned when respondImmediately is true.',
      properties: {
        statusCode: {
          type: BIQJsonSchemaType.Number,
          title: 'Status code',
          description: 'HTTP status code.',
        },
        headers: {
          type: BIQJsonSchemaType.Any,
          title: 'Headers',
          description: 'Response headers.',
          ui: { options: { editInModal: true } },
        },
        body: {
          type: BIQJsonSchemaType.Any,
          title: 'Body',
          description: 'Response body.',
          ui: { options: { editInModal: true } },
        },
      },
      required: ['statusCode'],
    },
  },
};
```

## actorSchemas/trigger/universalTrigger

**Source:** `actorSchemas/trigger/universalTrigger.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema } from '../../schemas/jsonSchema.js';
import { DENO_RESERVED_PATHS, makeCodeDirSchema } from '../codeDir.js';
import { DenoActorOptionsJsonSchema } from '../task/deno.js';

import { WebhookBehaviorOptionsSchema, WebhookBehaviorOptionsJsonSchema } from './triggerConfig.js';

export { TriggerEventSchema, type TriggerEvent } from '../../schemas/trigger.js';

/**
 * Legacy single-string source. Kept for the transition window only — the runtime normalizes it into
 * a one-entry `codeDir` before validating, and it is deleted at shim-drop.
 */
export const UniversalTriggerActorCodeSchema = z.string().min(1);

/**
 * The UniversalTriggerActor's `configuration.codeDir`: a project tree whose handler lives in
 * `main.ts`, minus the paths the Deno bootstrap owns. This type has its own `universal-trigger`
 * bootstrap variant, but that variant is the `deno-actor` one plus a trigger-aware handler — same
 * entry chain, same shared kernel, and its own `main_test.ts` harness — so it reserves the same set.
 */
export const UniversalTriggerActorCodeDirSchema = makeCodeDirSchema({
  requiredEntrypoint: 'main.ts',
  reservedPaths: DENO_RESERVED_PATHS,
});

/**
 * The options for the UniversalTriggerActor (the interpolated `options` blob).
 *
 * Deno runtime fields live at root; interpolatable webhook *behavior* is nested under `webhook`
 * (shared with the standalone WebhookTriggerActor). The STATIC, admission-consumed source config
 * (webhook triggerKey/authorizationLevel/allowedMethods/responseTimeout/enabled and schedule
 * cron/timezone/enabled) lives in `configuration.webhook` / `configuration.schedule`, not here.
 */
export const UniversalTriggerActorOptionsSchema = z.object({
  // --- deno runtime options (root) ---
  emitArrayAsSingleMessage: z.boolean().nullish()
    .describe('Emit the array as a single message instead of an array of messages, defaults to true').default(true),
  allowNet: z.boolean().nullish()
    .describe('Allow network access. By default when this is true, all network calls are allowed; allowNetList narrows the set.').default(false),
  allowNetList: z.array(z.string()).nullish()
    .describe('List of URLs that are allowed to be accessed when allowNet is true.').default([]),
  denyNetList: z.array(z.string()).nullish()
    .describe('List of URLs that are denied to be accessed when allowNet is true.').default([]),
  allowFs: z.boolean().nullish()
    .describe('Allow file system access to the temporary directory.').default(false),
  env: z.array(z.object({
    name: z.string()
      .regex(/^[A-Z0-9_]+$/, 'Environment variable name must contain only uppercase letters, numbers and underscores')
      .regex(/^(?!TMPDIR$)/, 'Environment variable name cannot be TMPDIR')
      .regex(/^(?!DENO_NO_UPDATE_CHECK$)/, 'Environment variable name cannot be DENO_NO_UPDATE_CHECK'),
    value: z.string().nullish(),
  })).nullish().default([])
    .describe('Environment variables exposed to the Deno runtime.'),
  // --- interpolatable webhook behavior (shared with WebhookTriggerActor) ---
  webhook: WebhookBehaviorOptionsSchema.nullish(),
});

export type UniversalTriggerActorOptions = z.infer<typeof UniversalTriggerActorOptionsSchema>;

// Memory is fully opt-in for UniversalTriggerActor — no infrastructure code reads or
// writes LTM/STM on the user's behalf. User code can persist anything (including a
// per-fire `lastTriggeredAt`) via `req.memory.ltm` (returned in `Response.memory`) if it enables LTM in advanced settings.
// Intentionally no `UniversalTriggerActorMemory` constant — the generic Actor.validate()
// in the lambda picks up `${type}Memory` by naming convention and would otherwise
// require LTM/STM on every event (including webhook-only).

/** JSON Schema for the editor's schema-driven configuration form (interpolatable options only). */
export const UniversalTriggerActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    ...DenoActorOptionsJsonSchema.properties,
    webhook: WebhookBehaviorOptionsJsonSchema,
  },
};

/** The response schema for the UniversalTriggerActor (user code can emit any JSON). */
export const UniversalTriggerActorResultSchema = z.any();

export type UniversalTriggerActorResult = z.infer<typeof UniversalTriggerActorResultSchema>;
```

## actorSchemas/trigger/webhook

**Source:** `actorSchemas/trigger/webhook.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema } from '../../schemas/jsonSchema.js';

import { WebhookBehaviorOptionsSchema, WebhookBehaviorOptionsJsonSchema } from './triggerConfig.js';

/**
 * The options schema for the WebhookTriggerActor.
 *
 * Only interpolatable webhook *behavior* lives here, nested under `webhook` (the same shape the
 * UniversalTriggerActor uses). Static, admission-consumed fields (triggerKey, authorizationLevel,
 * allowedMethods, responseTimeout) live in `configuration.webhook` — see {@link WebhookConfigSchema}.
 */
export const WebhookTriggerActorOptionsSchema = z.object({
  webhook: WebhookBehaviorOptionsSchema.nullish(),
});

export type WebhookTriggerActorOptions = z.infer<typeof WebhookTriggerActorOptionsSchema>;

export const WebhookTriggerActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    webhook: WebhookBehaviorOptionsJsonSchema,
  },
};

/** The response schema for the WebhookTriggerActor */
export const WebhookTriggerActorResultSchema = z.object({
  meta: z.object({
    requestId: z.string()
      .describe('The request id of the webhook request'),
    ipAddress: z.string().optional()
      .describe('The IP address of the webhook request'),
  }),
  method: z.string().nullish()
    .describe('The method of the request. Valid methods are GET, POST, PUT, DELETE'),
  headers: z.record(z.string(), z.any()).nullish()
    .describe('The headers sent with the request'),
  body: z.any().nullish()
    .describe('The body sent with the request'),
  queryParams: z.any().nullish()
    .describe('The query parameters sent with the request'),
  rawBody: z.string().nullish()
    .describe('The raw body of the request if emitRawBody was set to true in the options'),
  response: z.object({
    statusCode: z.number(),
    headers: z.record(z.string(), z.unknown()).nullish(),
    body: z.any().nullish(),
  }).nullish()
    .describe('The response to the webhook request if respondImmediately was set to true'),
});

export type WebhookTriggerActorResult = z.infer<typeof WebhookTriggerActorResultSchema>;
```
