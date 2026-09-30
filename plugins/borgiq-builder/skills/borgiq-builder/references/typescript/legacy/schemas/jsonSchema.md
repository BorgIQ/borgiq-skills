# schemas/jsonSchema

Generated from the platform's runtime types. Do not edit.

Legacy: the editor's option-form dialect. The `*JsonSchema` constants in other files are typed with it; actor YAML never needs it.

`BIQJsonSchema`, the dialect of the editor's option forms.

See also: [canvas](../../canvas.md).

## schemas/jsonSchema

**Source:** `schemas/jsonSchema.ts`

```typescript
/**
 * NOTE: This file is to ONLY be used for types that is used in the runtime.
 **/

import { z } from 'zod';

// canvas.js is itself import-free, so this file stays cycle-safe to import directly — which
// actorSchemas/trigger/reactApp.ts relies on (it imports this leaf rather than the schemas barrel to
// break a cycle). Keep any future import here to leaf modules only.
import { BIQActorType } from '../canvas.js';

/** The BIQ Json Schema Types for each component in the form rendered by the JSON schema */
export enum BIQJsonSchemaType {
  /** different string type schemas */
  String = 'string',
  
  /** different number type schemas */
  Number = 'number',
  Integer = 'integer',
  
  Boolean = 'boolean',

  /** different object type schemas */
  Object = 'object',
  Array = 'array',
  Any = 'any',
}


const BIQBaseJsonSchemaZodSchema = z.object({
  /** The title of the section */
  title: z.string().optional(),
  /** The description of the section */
  description: z.string().optional(),
  /** default value for the schema */
  default: z.any().optional(),
});

/** The base values available for all schema types */
interface BIQBaseJsonSchema {
  title?: string;
  description?: string;
  default?: unknown;
}

/** color values for the UI */
const BIQColorZodSchema = z.union([
  z.string().regex(/^#[0-9A-Fa-f]{6}$/, {
    error: 'Color must be a valid hex code (e.g., #FF0000)'
  }),
  z.enum(['red', 'pink', 'grape', 'violet', 'indigo', 'blue', 'cyan', 'teal', 'green', 'lime', 'yellow', 'orange', 'gray'], {
    error: 'Color must be one of: red, pink, grape, violet, indigo, blue, cyan, teal, green, lime, yellow, orange, gray',
  }),
], {
  error: 'If color is required, it must be a valid hex code or a valid color name',
});

// --------------------------------- String Input Schemas ---------------------------------
/** the basic string input schema that would return a string */
const BIQStringJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** if the value is a const */
  const: z.string().optional(),
  /** The minimum length of the string */
  minLength: z.number().optional(),
  /** The maximum length of the string */
  maxLength: z.number().optional(),
  /** The pattern of the string */
  pattern: z.string().optional(),
  /** The format of the string that will also verify the type */
  format: z.enum(['email', 'uri']).optional(),
  /** other options to format the ui for the component */
  ui: z.object({
    /** if the component is hidden */
    hidden: z.boolean().optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** The component of how to render the text input */
    component: z.enum(['input', 'textarea', 'password', 'markdown']).optional(),
    /** other options to format the ui for the component */
    options: z.object({
      /** if the component is disabled */
      disabled: z.boolean().optional(),
      /** allow to copy the value of the input */
      copyable: z.boolean().optional(),
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
      /** the minimum lines of the textarea and markdown defaults to 1 */
      minLines: z.number().optional(),
      /** the maximum lines of the textarea and markdown defaults to infinite */
      maxLines: z.number().optional(),
      /** allow to open the textarea/markdown input in a modal to edit the value */
      editInModal: z.boolean().optional(),
      /** the set height of the input for textarea and markdown */
      height: z.union([z.number(), z.string()]).optional(),
      /** the width of the input defaults to 100% */
      width: z.union([z.number(), z.string()]).optional(),
      /** if the component is a text area let it auto-resize to fit content */
      autoResize: z.boolean().optional(),
      /** if the component is a markdown input if the lines should be wrapped */
      wrapLines: z.boolean().optional(),
      /** for markdown input show a preview of markdown */
      preview: z.boolean().optional(),
    }).optional(),
  }).optional(),
});

export type BIQStringJsonSchema = z.infer<typeof BIQStringJsonSchemaZodSchema>;

/** the basic string input schema that would return a string */
const BIQCodeJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** if the value is a const */
  const: z.string().optional(),
  /** The minimum length of the string */
  minLength: z.number().optional(),
  /** The maximum length of the string */
  maxLength: z.number().optional(),
  /** other options to format the ui for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** The component of how to render the text input */
    component: z.literal('code'),
    /** other options to format the ui for the component */
    options: z.object({
      /** the language of the code */
      language: z.string().optional(),
      /** if the component is disabled */
      disabled: z.boolean().optional(),
      /** allow to copy the value of the input */
      copyable: z.boolean().optional(),
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
      /** the minimum lines of the input defaults to 1 */
      minLines: z.number().optional(),
      /** the maximum lines of the input defaults to infinite */
      maxLines: z.number().optional(),
      /** allow to open the code input in a modal to edit the value */
      editInModal: z.boolean().optional(),
      /** the set height of the input */
      height: z.union([z.number(), z.string()]).optional(),
      /** the width of the input defaults to 100% */
      width: z.union([z.number(), z.string()]).optional(),
      /** if the component is a text area let it auto-resize to fit content */
      autoResize: z.boolean().optional(),
      /** if the component is a codemirror input if the lines should be wrapped */
      wrapLines: z.boolean().optional(),
    }).optional(),
  }).optional(),
});

export type BIQCodeJsonSchema = z.infer<typeof BIQCodeJsonSchemaZodSchema>;

/** a date time input schema that would return a string of the date time */
const BIQDateTimeJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** The format of the date-time string that will also verify the type */
  format: z.enum(['date-time', 'date', 'time']),
  /** other options to format the ui for the component */
  ui: z.object({
    /** if the component is hidden */
    hidden: z.boolean().optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** The component of how to render the date input it is ignored for date-time and time inputs */
    component: z.enum(['input', 'calendar']).optional(),
    /** other options to format the ui for the component */
    options: z.object({
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
    }).optional(),
  }).optional(),
});

export type BIQDateTimeJsonSchema = z.infer<typeof BIQDateTimeJsonSchemaZodSchema>;

/** a suggestion input schema that would return a string but has a dropdown of suggestions */
const BIQSuggestionJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** The enum values of the string */
  /** other options to format the ui for the component */
  ui: z.object({
    /** if the component is hidden */
    hidden: z.boolean().optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** The component of how to render the select input  */
    component: z.literal('suggestion'),
    /** other options to format the ui for the component */
    options: z.object({
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
      /** the suggestions to display in the dropdown */
      suggestions: z.array(z.string()),
      /** labels for the select for suggestions inputs where the key is the suggestion value and the value is the label */
      suggestionLabels: z.record(z.string(), z.string()).optional(),
      /** the groups for suggestions labels where the key is the group name and the value is an array of the suggestion values */
      suggestionGroups: z.record(z.string(), z.array(z.string())).optional(),
    }),
  }),
});

export type BIQSuggestionJsonSchema = z.infer<typeof BIQSuggestionJsonSchemaZodSchema>;

/** a select input schema that would return a string of the selected value */
const BIQSelectJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** The enum values of the string */
  enum: z.array(z.string()),
  /** other options to format the ui for the component */
  ui: z.object({
    /** if the component is hidden */
    hidden: z.boolean().optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** The component of how to render the select input  */
    component: z.enum(['select', 'searchSelect', 'radio', 'radioVertical']).optional(),
    /** other options to format the ui for the component */
    options: z.object({
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
      /** labels for the select for enum inputs where the key is the enum value and the value is the label */
      enumLabels: z.record(z.string(), z.string()).optional(),
      /** the subtitles for the select for enum inputs where the key is the enum value and the value is the subtitle */
      enumSubtitles: z.record(z.string(), z.string()).optional(),
      /** the groups for enum labels where the key is the group name and the value is an array of the enum values */
      enumGroups: z.record(z.string(), z.array(z.string())).optional(),
      /** Name of a sibling field whose value filters this select's options (e.g. 'harness'). */
      optionsFilterField: z.string().optional(),
      /** Allowed enum values per sibling-field value, used with optionsFilterField.
       *  Key is the sibling value (e.g. 'codex'); value is the list of allowed enum values. */
      optionsByFieldValue: z.record(z.string(), z.array(z.string())).optional(),
    }).optional(),
  }).optional(),
});

export type BIQSelectJsonSchema = z.infer<typeof BIQSelectJsonSchemaZodSchema>;

/**
 * An actor picker: a compact control that opens a modal to browse workspace → canvas → actor,
 * filtered to the declared actor type(s).
 *
 * The value written into THIS property is the selected actor's id — so the property key is the
 * actor-id key, and needs no configuring (`callableTriggerActorId` and `actorId` both work). The
 * picker also writes the target coordinates into the SIBLING keys named by
 * `ui.options.workspaceKey` / `canvasKey` in the same object: flat siblings, not a nested value,
 * because that is the shape every consumer already persists.
 *
 * An absent workspace/canvas sibling means "the current canvas" — the picker never writes them
 * eagerly. Every coordinate, the actor id included, may hold a `${{ }}` expression; the picker
 * degrades to manual entry when it cannot query a list.
 */
const BIQActorSelectJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** validation pattern for the actor id (e.g. `ACTR[0-9a-z]{26}$`) */
  pattern: z.string().optional(),
  /** other options to format the ui for the component */
  ui: z.object({
    /** if the component is hidden */
    hidden: z.boolean().optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as an actor picker */
    component: z.literal('actorSelect'),
    /** other options to format the ui for the component */
    options: z.object({
      /** the actor types the picker offers. Omit or leave empty to offer every type. */
      actorTypes: z.array(z.enum(BIQActorType)).optional(),
      /**
       * An eligibility filter applied on top of `actorTypes`, for targets whose eligibility depends
       * on their configuration rather than their type — e.g. a UniversalTriggerActor only counts as
       * a webhook endpoint when its webhook source is enabled and it has a routing triggerKey.
       */
      capability: z.enum(['webhookEndpointTarget']).optional(),
      /** sibling key holding the target workspace slug. Omit to hide the workspace step. */
      workspaceKey: z.string().optional(),
      /** sibling key holding the target canvas slug. Omit to hide the canvas step. */
      canvasKey: z.string().optional(),
      /** the noun for the thing being picked — drives the modal title, primary action and empty state. Defaults to 'actor'. */
      entityLabel: z.string().optional(),
      /** the placeholder on the collapsed control when nothing is selected */
      placeholder: z.string().optional(),
    }).optional(),
  }),
});

export type BIQActorSelectJsonSchema = z.infer<typeof BIQActorSelectJsonSchemaZodSchema>;

/**
 * The sibling keys the actorSelect pickers in `properties` own.
 *
 * Renderers must skip these: the coordinates belong to the picker, which writes all three together
 * and clears the ones a change invalidates (a new workspace voids the canvas and the actor beneath
 * it). Rendering them as their own inputs as well would both duplicate the control and give the user
 * a way to change a workspace or canvas WITHOUT the dependent values being cleared — leaving an
 * actor id pointing into a canvas it doesn't live in, which CallFlow only discovers at run time.
 */
export function getActorSelectCoordinateKeys(properties?: Record<string, unknown>): Set<string> {
  const keys = new Set<string>();
  for (const schema of Object.values(properties ?? {})) {
    const ui = (schema as BIQActorSelectJsonSchema | undefined)?.ui;
    if (!ui || ui.component !== 'actorSelect') continue;
    if (ui.options?.workspaceKey) keys.add(ui.options.workspaceKey);
    if (ui.options?.canvasKey) keys.add(ui.options.canvasKey);
  }
  return keys;
}

/** a diff input schema that would return a string of the "new" code in the diff */
const BIQDiffJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as a diff */
    component: z.literal('diff'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The old value of the diff */
      oldValue: z.string(),
      /** the supported languages of the diff component */
      language: z.string().optional(),
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
      /** if the component is read only (value would be defined by default) */
      readOnly: z.boolean().optional(),
      /** minimum lines of the diff */
      minLines: z.number().optional(),
      /** maximum lines of the diff */
      maxLines: z.number().optional(),
      /** allow to open the diff input in a modal to edit the value */
      editInModal: z.boolean().optional(),
      /** The height of the diff */
      height: z.union([z.number(), z.string()]).optional(),
      /** The width of the diff */
      width: z.union([z.number(), z.string()]).optional(),
      /** if the diff should auto-resize to fit content */
      autoResize: z.boolean().optional(),
      /** if the component is a codemirror input if the lines should be wrapped */
      wrapLines: z.boolean().optional(),
      /** whether to render the revert controls (only would render is readOnly is undefined or false)  */
      revertControls: z.boolean().optional(),
    }),
  }),
});

export type BIQDiffJsonSchema = z.infer<typeof BIQDiffJsonSchemaZodSchema >;

// --------------------------------- Number Input Schemas ---------------------------------

/** a basic number input schema that would return a number */
const BIQNumberJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.enum([BIQJsonSchemaType.Number, BIQJsonSchemaType.Integer]),
  /** The minimum value of the number */
  minimum: z.number().optional(),
  /** The maximum value of the number */
  maximum: z.number().optional(),
  /** The exclusive minimum value of the number */
  exclusiveMinimum: z.number().optional(),
  /** The exclusive maximum value of the number */
  exclusiveMaximum: z.number().optional(),
  /** other options to format the ui for the component */
  ui: z.object({
    /** if the component is hidden */
    hidden: z.boolean().optional(),
    /** The component of how to render the number input  */
    component: z.enum(['number', 'currency', 'percent', 'phoneNumber', 'rating', 'slider']).optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** other options to format the ui for the component */
    options: z.object({
      /** if the component type  is currency, this would be the prefix for the number */
      currencyPrefix: z.string().optional(),
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
      /** whether to hide the number controls */
      hideControls: z.boolean().optional(),
      /** for a slider component, the step value */
      step: z.number().positive().optional(),
    }).optional(),
  }).optional(),
});

export type BIQNumberJsonSchema = z.infer<typeof BIQNumberJsonSchemaZodSchema>;

// --------------------------------- Boolean Input Schemas ---------------------------------

/** a basic boolean input schema that would return a boolean */
const BIQBooleanJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.Boolean),
  /** options to format the ui for the component */
  ui: z.object({
    /** if the component is hidden */
    hidden: z.boolean().optional(),
    /** The component of how to render the number input.  Defaults to switch */
    component: z.enum(['checkbox', 'switch']).optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
  }).optional(),
});

export type BIQBooleanJsonSchema = z.infer<typeof BIQBooleanJsonSchemaZodSchema>;

// --------------------------------- Any Input Schemas ---------------------------------

/** an any input schema that would return the yaml or json as an object */
const BIQAnyJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.enum([BIQJsonSchemaType.Any]),
  /** options to format the ui for the component */
  ui: z.object({
    component: z.enum(['input', 'modal']).optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** other options to format the ui for the component */
    options: z.object({
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
      /** the language of the any type (defaults to yaml) */
      language: z.enum(['yaml', 'json']).optional(),
      /** if the component is a codemirror input if the lines should be wrapped */
      wrapLines: z.boolean().optional(),
      /** let  the code editor component auto-resize to fit content */
      autoResize: z.boolean().optional(),
      /** the minimum lines of the textarea and codemirror defaults to 1 */
      minLines: z.number().optional(),
      /** the maximum lines of the textarea and codemirror defaults to infinite */
      maxLines: z.number().optional(),
      /** edit the value in a modal */
      editInModal: z.boolean().optional(),
    }).optional(),
  }).optional(),
});

export type BIQAnyJsonSchema = z.infer<typeof BIQAnyJsonSchemaZodSchema>;

// --------------------------------- Object Input Schemas (Files) ---------------------------------

/** a file input that would return an object with the structure of a BIQFile */
const BIQFileJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.Object),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure the component is rendered as a file input */
    component: z.literal('file'),
    /** other options to format the ui for the component */
    options: z.object({
      /** if multiple files can be uploaded at once */
      multiple: z.boolean().optional(),
      /** the allowed file types */
      accept: z.string().optional(),
      /** the type of file component */
      type: z.enum(['input', 'button']).optional(),
    }).optional(),
  })
});

export type BIQFileJsonSchema = z.infer<typeof BIQFileJsonSchemaZodSchema>;

/** an audio recording input that would return an object with the structure of a BIQAudioRecording */
const BIQAudioFileJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.Object),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure the component is rendered as a audio recording input */
    component: z.literal('audioRecording'),
    /** other options to format the ui for the component */
    options: z.object({
      /** the max duration the audio recording can be */
      maxDuration: z.number().optional(),
    }).optional(),
  })
});

export type BIQAudioRecordingFileJsonSchema = z.infer<typeof BIQAudioFileJsonSchemaZodSchema>;

// --------------------------------- String Display Schemas ---------------------------------

/** a display text input that would not return anything but would display a title and/or description in the form */
const BIQDisplayTextJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as a display text */
    component: z.literal('display'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The title color of the display text */
      titleColor: BIQColorZodSchema.optional(),
      /** The title order of the display text */
      titleOrder: z.union([z.literal(0), z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)]).optional(),
      /** The description color of the display text */
      descriptionColor: BIQColorZodSchema.optional(),
    }).optional(),
  }),
});

export type BIQDisplayTextJsonSchema = z.infer<typeof BIQDisplayTextJsonSchemaZodSchema>;

/** a divider input that would not return anything but would display a divider in the form */
const BIQDividerJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as a divider */
    component: z.literal('divider'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The color of the divider */
      color: BIQColorZodSchema.optional(),
      /** The weight of the divider */
      weight: z.number().optional(),
      /** The text alignment of the divider */
      textAlignment: z.enum(['left', 'center', 'right']).optional(),
    }).optional(),
  }),
});

export type BIQDividerJsonSchema = z.infer<typeof BIQDividerJsonSchemaZodSchema>;

/**
 * a button input that would not return anything but would complete the action of the button
 * this is the component that would be used to submit the form with the action type of submit
 **/
const BIQButtonJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as a button */
    component: z.literal('button'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The action type of the button */
      actionType: z.enum(['button', 'reset', 'submit']).optional(),
      /** The variant of the button */
      variant: z.enum(['default', 'filled', 'light', 'outline', 'subtle', 'transparent', 'white']).optional(),
      /** The color of the button */
      color: BIQColorZodSchema.optional(),
      /** The url of the button */
      url: z.string().optional(),
      /** The open url in current tab of the button */
      openUrlInCurrentTab: z.boolean().optional(),
    }).optional(),
  }),
});

export type BIQButtonJsonSchema = z.infer<typeof BIQButtonJsonSchemaZodSchema>;

/** a image input that would return nothing but would display an image */
const BIQImageJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as an image */
    component: z.literal('image'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The src of the image */
      src: z.string(),
      /** The width of the image */
      width: z.union([z.number(), z.string()]).optional(),
      /** The height of the image */
      height: z.union([z.number(), z.string()]).optional(),
    }).optional(),
  }),
});

export type BIQImageJsonSchema = z.infer<typeof BIQImageJsonSchemaZodSchema>;

/** a markdown viewer input that would return nothing but would display a markdown component */
const BIQMarkdownViewerJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the file name for the pdf */
  title: z.string().optional(),
  /** the markdown string to display */
  default: z.string(),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as an image */
    component: z.literal('markdownViewer'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The width of the markdown component */
      width: z.union([z.number(), z.string()]).optional(),
      /** The height of the markdown component */
      height: z.union([z.number(), z.string()]).optional(),
    }).optional(),
  }),
});

export type BIQMarkdownViewerJsonSchema = z.infer<typeof BIQMarkdownViewerJsonSchemaZodSchema>;

/** a code viewer input that would return nothing but would display a code markdown component */
const BIQCodeViewerJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the title of the code */
  title: z.string().optional(),
  /** the code string to display */
  default: z.string(),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as an image */
    component: z.literal('codeViewer'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The language of the code */
      language: z.string().optional(),
      /** The width of the markdown component */
      width: z.union([z.number(), z.string()]).optional(),
      /** The height of the markdown component */
      height: z.union([z.number(), z.string()]).optional(),
    }).optional(),
  }),
});

export type BIQCodeViewerJsonSchema = z.infer<typeof BIQCodeViewerJsonSchemaZodSchema>;

/** a pdf viewer input that would return nothing but would display a pdf */
const BIQPdfViewerJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the file name for the pdf */
  title: z.string().optional(),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as an image */
    component: z.literal('pdfViewer'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The src of the pdf */
      src: z.string(),
      /** The width of the pdf */
      width: z.union([z.number(), z.string()]).optional(),
      /** The height of the pdf */
      height: z.union([z.number(), z.string()]).optional(),
    }),
  }),
});

export type BIQPdfViewerJsonSchema = z.infer<typeof BIQPdfViewerJsonSchemaZodSchema>;

// --------------------------------- Object Input Schemas ---------------------------------

/** an object input that would return an object with the structure of the properties */
const BIQObjectJsonSchemaZodSchema: z.ZodObject<Record<string, z.ZodTypeAny>> = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.Object),
  /** The properties of the object */
  properties: z.record(z.string(), z.lazy(() => z.union(
    [
      BIQStringJsonSchemaZodSchema, BIQCodeJsonSchemaZodSchema, BIQDateTimeJsonSchemaZodSchema, BIQSuggestionJsonSchemaZodSchema, BIQSelectJsonSchemaZodSchema, BIQActorSelectJsonSchemaZodSchema, BIQDiffJsonSchemaZodSchema,
      BIQNumberJsonSchemaZodSchema,
      BIQBooleanJsonSchemaZodSchema,
      BIQAnyJsonSchemaZodSchema, BIQObjectJsonSchemaZodSchema, BIQArrayJsonSchemaZodSchema, BIQAnyOfJsonSchemaZodSchema,
      BIQFileJsonSchemaZodSchema, BIQAudioFileJsonSchemaZodSchema,
      BIQDisplayTextJsonSchemaZodSchema, BIQDividerJsonSchemaZodSchema, BIQButtonJsonSchemaZodSchema, BIQImageJsonSchemaZodSchema, BIQPdfViewerJsonSchemaZodSchema, BIQMarkdownViewerJsonSchemaZodSchema, BIQCodeViewerJsonSchemaZodSchema
    ]))).optional(),
  /** The required properties of the object */
  required: z.array(z.string()).optional(),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    options: z.object({
      /** if to render the object in a section, defaults to true */
      section: z.boolean().optional(),
    }).optional(),
  }).optional(),
});

/** the typing for the object input schema since the ZodSchema schema is created dynamically */
export interface BIQObjectJsonSchema extends BIQBaseJsonSchema {
  type: BIQJsonSchemaType.Object;
  properties?: Record<string, BIQPropertyJsonSchemas>;
  required?: string[];
  ui?: {
    order?: number;
    options?: {
      section?: boolean;
    };
  }
}

// --------------------------------- Array Input Schemas ---------------------------------
/** a form array input that would return an array with the structure of the items */
const BIQArrayJsonSchemaZodSchema: z.ZodObject<Record<string, z.ZodTypeAny>> = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.Array),
  /** The items of the array */
  items: z.lazy(() => z.union(
    [
      BIQStringJsonSchemaZodSchema, BIQCodeJsonSchemaZodSchema, BIQDateTimeJsonSchemaZodSchema, BIQSuggestionJsonSchemaZodSchema, BIQSelectJsonSchemaZodSchema, BIQActorSelectJsonSchemaZodSchema, BIQDiffJsonSchemaZodSchema,
      BIQNumberJsonSchemaZodSchema,
      BIQBooleanJsonSchemaZodSchema,
      BIQAnyJsonSchemaZodSchema, BIQObjectJsonSchemaZodSchema, BIQArrayJsonSchemaZodSchema, BIQAnyOfJsonSchemaZodSchema,
      BIQFileJsonSchemaZodSchema, BIQAudioFileJsonSchemaZodSchema,
      BIQDisplayTextJsonSchemaZodSchema, BIQDividerJsonSchemaZodSchema, BIQButtonJsonSchemaZodSchema, BIQImageJsonSchemaZodSchema, BIQPdfViewerJsonSchemaZodSchema, BIQMarkdownViewerJsonSchemaZodSchema, BIQCodeViewerJsonSchemaZodSchema
    ])),
  /** The min items of the array */
  minItems: z.number().optional(),
  /** The max items of the array */
  maxItems: z.number().optional(),
  /** if all the items must be unique */
  uniqueItems: z.boolean().optional(),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
  }).optional(),
});

/** the typing for the array input schema since the ZodSchema schema is created dynamically */
export interface BIQArrayJsonSchema extends BIQBaseJsonSchema {
  type: BIQJsonSchemaType.Array;
  items: BIQPropertyJsonSchemas;
  minItems?: number;
  maxItems?: number;
  uniqueItems?: boolean;
  ui?: {
    order?: number;
  }
}

export const BIQAnyOfJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The key of the value to discriminate by if it is a discriminated union, the key value must be of type string and contain a constant value */
  discriminatorKey: z.string().optional(),
  /** The array of the anyOf */
  anyOf: z.array(z.lazy(() => z.union(
    [
      BIQStringJsonSchemaZodSchema, BIQCodeJsonSchemaZodSchema, BIQDateTimeJsonSchemaZodSchema, BIQSuggestionJsonSchemaZodSchema, BIQSelectJsonSchemaZodSchema, BIQActorSelectJsonSchemaZodSchema, BIQDiffJsonSchemaZodSchema,
      BIQNumberJsonSchemaZodSchema,
      BIQBooleanJsonSchemaZodSchema,
      BIQAnyJsonSchemaZodSchema, BIQObjectJsonSchemaZodSchema, BIQArrayJsonSchemaZodSchema, BIQAnyJsonSchemaZodSchema,
      BIQFileJsonSchemaZodSchema, BIQAudioFileJsonSchemaZodSchema,
      BIQDisplayTextJsonSchemaZodSchema, BIQDividerJsonSchemaZodSchema, BIQButtonJsonSchemaZodSchema, BIQImageJsonSchemaZodSchema, BIQPdfViewerJsonSchemaZodSchema, BIQMarkdownViewerJsonSchemaZodSchema, BIQCodeViewerJsonSchemaZodSchema
    ]))),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
  }).optional(),
}).superRefine((data, ctx) => {
  if (!data.discriminatorKey) return;
  // Ensure all schemas in anyOf are properly formatted
  for (const schema of (data.anyOf as BIQPropertyJsonSchemas[])) {
    // check if the schema is an object and has properties (since there needs to be a key with the value of the discriminatorKey)
    if (!('type' in schema) || schema.type !== BIQJsonSchemaType.Object || !('properties' in schema)) {
      ctx.addIssue({
        code: 'custom',
        message: 'All schemas in anyOf must be of type object when using discriminatorKey',
        path: ['anyOf'],
      });
      return;
    }

    // check if the schema has the discriminatorKey in its properties
    if (!schema.properties || !(data.discriminatorKey in schema.properties)) {
      ctx.addIssue({
        code: 'custom',
        message: `All schemas in anyOf must have the discriminatorKey "${data.discriminatorKey}" in their properties`,
        path: ['anyOf'],
      });
    }

    // check if the discriminatorKey property is of type string and has a const value
    const discriminatorProperty = schema.properties?.[data.discriminatorKey];
    if (!discriminatorProperty || !('type' in discriminatorProperty) || discriminatorProperty.type !== BIQJsonSchemaType.String || !('const' in discriminatorProperty)) {
      ctx.addIssue({
        code: 'custom',
        message: 'The discriminatorKey property must be of type string and have a const value',
        path: ['anyOf'],
      });
    }
  }

  // Check for duplicate discriminator values
  const discriminatorValues = new Set();
  for (const schema of (data.anyOf as BIQPropertyJsonSchemas[])) {
    if (!('properties' in schema) || !schema.properties) continue;
    const discriminatorProperty = schema.properties[data.discriminatorKey];
    if (!('const' in discriminatorProperty) || discriminatorProperty.const === undefined) continue;
    const discriminatorValue = discriminatorProperty.const;
    if (discriminatorValues.has(discriminatorValue)) {
      ctx.addIssue({
        code: 'custom',
        message: `Duplicate discriminator value "${discriminatorValue}" found`,
        path: ['anyOf'],
      });
    }
    discriminatorValues.add(discriminatorValue);
  }
});

export interface BIQAnyOfJsonSchema extends BIQBaseJsonSchema {
  discriminatorKey?: string;
  anyOf: BIQPropertyJsonSchemas[];
  ui?: {
    order?: number;
  }
}

export const BIQPropertiesJsonSchemaZodSchema = z.union([
  BIQStringJsonSchemaZodSchema, BIQCodeJsonSchemaZodSchema, BIQDateTimeJsonSchemaZodSchema, BIQSuggestionJsonSchemaZodSchema, BIQSelectJsonSchemaZodSchema, BIQActorSelectJsonSchemaZodSchema, BIQDiffJsonSchemaZodSchema,
  BIQNumberJsonSchemaZodSchema,
  BIQBooleanJsonSchemaZodSchema,
  BIQAnyJsonSchemaZodSchema, BIQObjectJsonSchemaZodSchema, BIQArrayJsonSchemaZodSchema, BIQAnyOfJsonSchemaZodSchema,
  BIQFileJsonSchemaZodSchema, BIQAudioFileJsonSchemaZodSchema,
  BIQDisplayTextJsonSchemaZodSchema, BIQDividerJsonSchemaZodSchema, BIQButtonJsonSchemaZodSchema, BIQImageJsonSchemaZodSchema, BIQPdfViewerJsonSchemaZodSchema, BIQMarkdownViewerJsonSchemaZodSchema, BIQCodeViewerJsonSchemaZodSchema
]);

/** the BIQ schema across all the different types */
export type BIQPropertyJsonSchemas = BIQStringJsonSchema | BIQCodeJsonSchema | BIQDateTimeJsonSchema | BIQSuggestionJsonSchema | BIQSelectJsonSchema | BIQActorSelectJsonSchema | BIQNumberJsonSchema | BIQBooleanJsonSchema |
BIQAnyJsonSchema | BIQObjectJsonSchema | BIQArrayJsonSchema | BIQFileJsonSchema | BIQAudioRecordingFileJsonSchema | BIQDisplayTextJsonSchema | BIQDividerJsonSchema |
BIQButtonJsonSchema | BIQImageJsonSchema | BIQPdfViewerJsonSchema | BIQMarkdownViewerJsonSchema | BIQCodeViewerJsonSchema | BIQDiffJsonSchema | BIQAnyOfJsonSchema;

/** the ZodSchema schema for the custom BIQ json schema */
export const BIQJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The properties of the object */
  properties: z.record(z.string(), BIQPropertiesJsonSchemaZodSchema),
  /** The required properties of the object */
  required: z.array(z.string()).optional(),
  /** the ui options for the component */
  ui: z.object({
    /** an image to be displayed at the top of the form (above the title and description) */
    topImage: z.object({
      /** The src of the image */
      src: z.string(),
      /** The width of the image */
      width: z.union([z.number(), z.string()]).optional(),
      /** The height of the image */
      height: z.union([z.number(), z.string()]).optional(),
    }).optional(),
    options: z.object({
      /** The base theme color for the entire form */
      themeColor: BIQColorZodSchema.optional(),
      /** The background color of the form */
      backgroundColor: BIQColorZodSchema.optional(),
      /** The color of the title */
      titleColor: BIQColorZodSchema.optional(),
      /** The order of the title */
      titleOrder: z.union([z.literal(0), z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)]).optional(),
      /** The color of the description */
      descriptionColor: BIQColorZodSchema.optional(),
      /** the width of the form */
      width: z.enum(['full', 'half']).optional(),
    }).optional(),
  }).optional(),
});

/** the typing for the BIQ json schema since the ZodSchema schema is created dynamically */
export interface BIQJsonSchema extends BIQBaseJsonSchema {
  type?: BIQJsonSchemaType.Object;
  properties: Record<string, BIQPropertyJsonSchemas>;
  required?: string[];
  ui?: {
    topImage?: {
      src: string;
      width?: number | string;
      height?: number | string;
    }
    options?: {
      themeColor?: string;
      backgroundColor?: string;
      titleColor?: string;
      titleOrder?: 1 | 2 | 3 | 4 | 5 | 6;
      descriptionColor?: string;
      width?: 'full' | 'half';
    }
  }
}
```
