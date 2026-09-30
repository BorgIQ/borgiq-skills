# actorSchemas/trigger/app

Generated from the platform's runtime types. Do not edit.

AppTriggerActor options (legacy raw-HTML apps) and result.

See also: [schemas/file](../../schemas/file.md), [actorSchemas/trigger/permissionsPolicy](permissionsPolicy.md).

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
