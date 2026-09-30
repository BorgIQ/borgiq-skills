# formComponents/form

Generated from the platform's runtime types. Do not edit.

Nested form components (array, object section, object collapse, union) and the union of every component schema.

See also: [formComponents/any/codeInput](any/codeInput.md), [formComponents/any/modal](any/modal.md), [formComponents/array/multiSelect](array/multiSelect.md), [formComponents/array/multiCheckbox](array/multiCheckbox.md), [formComponents/array/table](array/table.md), [formComponents/boolean/checkbox](boolean/checkbox.md), [formComponents/boolean/switch](boolean/switch.md), [formComponents/date/dateTime](date/dateTime.md), [formComponents/date/calendar](date/calendar.md), [formComponents/date/calendarRange](date/calendarRange.md), [formComponents/date/date](date/date.md), [formComponents/date/dateRange](date/dateRange.md), [formComponents/date/time](date/time.md), [formComponents/display/header](display/header.md), [formComponents/display/divider](display/divider.md), [formComponents/display/formButton](display/formButton.md), [formComponents/display/urlButton](display/urlButton.md), [formComponents/display/image](display/image.md), [formComponents/display/markdown](display/markdown.md), [formComponents/display/code](display/code.md), [formComponents/display/fileDownload](display/fileDownload.md), [formComponents/display/pdf](display/pdf.md), [formComponents/display/progress](display/progress.md), [formComponents/display/webViewer](display/webViewer.md), [formComponents/display/textDisplay](display/textDisplay.md), [formComponents/file/fileInput](file/fileInput.md), [formComponents/file/fileButton](file/fileButton.md), [formComponents/file/audioRecording](file/audioRecording.md), [formComponents/file/fileDropzone](file/fileDropzone.md), [formComponents/number/number](number/number.md), [formComponents/number/rating](number/rating.md), [formComponents/number/slider](number/slider.md), [formComponents/number/percentage](number/percentage.md), [formComponents/number/currency](number/currency.md), [formComponents/string/text](string/text.md), [formComponents/string/textArea](string/textArea.md), [formComponents/string/password](string/password.md), [formComponents/string/phoneNumber](string/phoneNumber.md), [formComponents/string/code](string/code.md), [formComponents/string/codeDiff](string/codeDiff.md), [formComponents/string/markdown](string/markdown.md), [formComponents/string/select](string/select.md), [formComponents/string/suggest](string/suggest.md), [formComponents/string/buttonGroup](string/buttonGroup.md), [formComponents/string/radio](string/radio.md), [formComponents/string/pin](string/pin.md), [formComponents/base](base.md).

## formComponents/form

**Source:** `formComponents/form.ts`

```typescript
/**
 * This file contains the schemas for the nested form components.
 * So there can be circular dependencies between the form components.
 */

import { z } from 'zod';
import {
  BIQAnyCodeInputZodSchema,
  BIQAnyModalZodSchema,
} from './any/index.js';
import {
  BIQMultiSelectZodSchema,
  BIQMultiCheckboxZodSchema,
  BIQTableZodSchema,
} from './array/index.js';
import {
  BIQCheckboxZodSchema,
  BIQSwitchZodSchema,
} from './boolean/index.js';
import {
  BIQDateTimeZodSchema,
  BIQCalendarZodSchema,
  BIQCalendarRangeZodSchema,
  BIQDateZodSchema,
  BIQDateRangeZodSchema,
  BIQTimeZodSchema,
} from './date/index.js';
import {
  BIQHeaderZodSchema,
  BIQDividerZodSchema,
  BIQFormButtonZodSchema,
  BIQUrlButtonZodSchema,
  BIQImageZodSchema,
  BIQMarkdownZodSchema,
  BIQCodeViewerZodSchema,
  BIQFileDownloadZodSchema,
  BIQPdfViewerZodSchema,
  BIQProgressZodSchema,
  BIQWebViewZodSchema,
  BIQTextDisplayZodSchema,
} from './display/index.js';
import {
  BIQFileInputZodSchema,
  BIQFileButtonZodSchema,
  BIQAudioRecordingZodSchema,
  BIQFileDropzoneZodSchema,
} from './file/index.js';
import {
  BIQNumberZodSchema,
  BIQRatingZodSchema,
  BIQSliderZodSchema,
  BIQPercentageZodSchema,
  BIQCurrencyZodSchema,
} from './number/index.js';
import {
  BIQTextZodSchema,
  BIQTextAreaZodSchema,
  BIQPasswordZodSchema,
  BIQPhoneNumberZodSchema,
  BIQCodeZodSchema,
  BIQCodeDiffZodSchema,
  BIQMarkdownInputZodSchema,
  BIQSelectZodSchema,
  BIQSuggestZodSchema,
  BIQButtonGroupZodSchema,
  BIQRadioZodSchema,
  BIQSelectSchema,
  BIQPinZodSchema,
} from './string/index.js';

import {
  BIQButtonStyleZodSchema,
  BIQColorZodSchema,
  BIQFormComponentType,
  BIQBaseFormComponentZodSchema,
  BIQBaseFormComponentSchema,
  BIQColor,
  BIQFormSchemaOptions,
  BIQOptionsZodSchema,
  BIQElementSizeZodSchema,
  BIQElementSize,
} from './base.js';

/** a helper function to extract the values form any type of options */
const extractEnumValuesFromOptions = (options: BIQFormSchemaOptions) => {
  const optionsValues: string[] = [];
  for (const option of options) {
    if (typeof option === 'string') {
      optionsValues.push(option);
    } else if (typeof option === 'object' && 'group' in option) {
      for (const item of option.items) {
        optionsValues.push(typeof item === 'string' ? item : item.value);
      }
    } else {
      optionsValues.push(option.value);
    }
  }
  return optionsValues;
};

/** The zod schema for all the components that do not have nested components so they can be used directly when building the nested zod schemas */
export const BaseFormComponentsZodSchemas = [
  /** any type components */
  BIQAnyCodeInputZodSchema,
  BIQAnyModalZodSchema,

  /** array type components */
  BIQMultiSelectZodSchema,
  BIQMultiCheckboxZodSchema,
  BIQTableZodSchema,
  
  /** boolean type components */
  BIQCheckboxZodSchema,
  BIQSwitchZodSchema,

  /** date type components */
  BIQDateTimeZodSchema,
  BIQCalendarZodSchema,
  BIQCalendarRangeZodSchema,
  BIQDateZodSchema,
  BIQDateRangeZodSchema,
  BIQTimeZodSchema,

  /** display type components */
  BIQHeaderZodSchema,
  BIQDividerZodSchema,
  BIQProgressZodSchema,
  BIQFormButtonZodSchema,
  BIQUrlButtonZodSchema,
  BIQImageZodSchema,
  BIQMarkdownZodSchema,
  BIQCodeViewerZodSchema,
  BIQPdfViewerZodSchema,
  BIQFileDownloadZodSchema,
  BIQWebViewZodSchema,
  BIQTextDisplayZodSchema,

  /** file type components */
  BIQFileInputZodSchema,
  BIQFileButtonZodSchema,
  BIQAudioRecordingZodSchema,
  BIQFileDropzoneZodSchema,

  /** number type components */
  BIQNumberZodSchema,
  BIQRatingZodSchema,
  BIQSliderZodSchema,
  BIQPercentageZodSchema,
  BIQCurrencyZodSchema,

  /** string type components */
  BIQTextZodSchema,
  BIQTextAreaZodSchema,
  BIQPasswordZodSchema,
  BIQPhoneNumberZodSchema,
  BIQPinZodSchema,
  BIQCodeZodSchema,
  BIQCodeDiffZodSchema,
  BIQMarkdownInputZodSchema,
  BIQSelectZodSchema,
  BIQSuggestZodSchema,
  BIQButtonGroupZodSchema,
  BIQRadioZodSchema,
] as const;


/** The zod schema for an array of form components. This will be used to build the zod schema for nested form components with multiple children. */
export const biqFormComponentArrayZodSchema: z.ZodType<BIQFormComponentSchema[]> = z.array(z.lazy(() => BIQFormComponentZodSchema)).superRefine((data, ctx) => {
  /** Make sure there are no duplicate keys in the array of components */
  const keys = data.map((child) => child.key);
  const keyToIndices = new Map<string, number[]>();
  
  // Find all indices for each key
  keys.forEach((key, index) => {
    const indices = keyToIndices.get(key) || [];
    indices.push(index);
    keyToIndices.set(key, indices);
  });

  // Check for duplicates
  for (const [key, indices] of Array.from(keyToIndices.entries())) {
    if (indices.length > 1) {
      for (const index of indices) {
        ctx.addIssue({
          code: 'custom',
          message: `Duplicate key '${key}' found`,
          path: [index],
        });
      }
    }
  }
});

// *********** The array parent component which is used to build an array out of any other component *********

/** The type of the schema for the array parent component */
export type BIQArrayParentSchema = {
  /** The type of the component is `arrayParent` for the form builder to know what component to render */
  type: BIQFormComponentType.ArrayParent;
  /**
   * The singular item input that will be rendered in the array.
   * This will be rendered as either a one line input or a card depending on the if the item is a nested component or not
   * For nested components, the items label will be used as the title of the card
   */
  item: BIQFormComponentSchema;

  /** The default value of the array. This will be an array of the item type */
  default?: any[]; // eslint-disable-line @typescript-eslint/no-explicit-any

  /** The minimum number of items in the array. Defaults to 0 */
  minItems?: number;
  /** The maximum number of items in the array. If not set, the array will have no limit */
  maxItems?: number;
  /** If all the items in the array have to be unique. Defaults to false */
  uniqueItems?: boolean;

  /** If to allow the user to reorder the items in the array. Defaults to true */
  allowReorder?: boolean;

  /** The gap between array items. Can be a Mantine size ('xs', 'sm', 'md', 'lg', 'xl') or a number. Defaults to 'xs' */
  gap?: BIQElementSize;

  // ********** The Props to edit the add button *********
  /** The color of the button to add a new item to the array. Defaults to the Theme Color */
  addButtonColor?: z.infer<typeof BIQColorZodSchema>;
  /** The text to display on the button to add a new item to the array. Defaults to `Add Item` */
  addButtonText?: string;
  /** The variant of the button to add a new item to the array. Defaults to Outline */
  addButtonVariant?: z.infer<typeof BIQButtonStyleZodSchema>;

} & BIQBaseFormComponentSchema;

/** The zod schema for the array parent component based on the array parent type schema */
export const BIQArrayParentZodSchema = BIQBaseFormComponentZodSchema.extend({
  type: z.literal(BIQFormComponentType.ArrayParent),
  item: z.lazy(() => BIQFormComponentZodSchema),

  default: z.array(z.any()).optional(),

  minItems: z.number().gt(0).optional(),
  maxItems: z.number().gt(0).optional(),
  uniqueItems: z.boolean().optional(),

  allowReorder: z.boolean().optional(),

  gap: BIQElementSizeZodSchema.optional(),

  addButtonColor: BIQColorZodSchema.optional(),
  addButtonText: z.string().optional(),
  addButtonVariant: BIQButtonStyleZodSchema.optional(),
});

// *********** The Object/Section component which is used to build an object out of a set of components *********

/** The type of the schema for the object section component */
export type BIQObjectSectionSchema = {
  /** The type of the component is `section` for the form builder to know what component to render */
  type: BIQFormComponentType.Section;
  /** The children of the section. This will be an array of form components to be rendered in the section */
  children: BIQFormComponentSchema[];

  /** The default value of the section. This will be an object based on the format of the components in the section and will be used to pre-populate the section */
  default?: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any

  /** The gap between child components. Can be a Mantine size ('xs', 'sm', 'md', 'lg', 'xl') or a number. Defaults to 'sm' */
  gap?: BIQElementSize;

  // ********** The Props to edit the section header *********
  /** The order of the section header. Defaults to 1 (biggest) */
  sectionLabelOrder?: 1 | 2 | 3 | 4 | 5 | 6;
  /** The color of the section header. Defaults to the default text color (black for light theme and white for dark theme) */
  sectionLabelColor?: BIQColor;

  /** The color of the section description. Defaults to the default text color (black for light theme and white for dark theme) */
  sectionDescriptionColor?: BIQColor;

  /** The color of the section divider between the section header and the section content. Defaults to the default text color (black for light theme and white for dark theme) */
  sectionDividerColor?: BIQColor;
  /** The weight of the section divider. Defaults to 1 */
  sectionDividerWeight?: number;

  /**
   * If the section should be returned as the parent object extended or as a nested object with the key as the parent
   * If true, the section values will be merged with this section's parent object values
   * eg of results in the parent object
   * ``` json
   * {
   *   "formKey1": "formValue1",
   *   ...,
   *   "formKeyN": "formValueN",
   *   // the current section children values
   *   "sectionChildKey1": "sectionChildValue1",
   *   "sectionChildKey2": "sectionChildValue2",
   *   ...
   *   "sectionChildKeyN": "sectionChildValueN",
   * }
   * ```
   * If false, the section values will be nested under the current sections key
   ** ``` json
   * {
   *   "formKey1": "formValue1",
   *   ...,
   *   "formKeyN": "formValueN",
   *   // the current section children values
   *   "sectionKey": {
   *     "sectionChildKey1": "sectionChildValue1",
   *     "sectionChildKey2": "sectionChildValue2",
   *     ...
   *     "sectionChildKeyN": "sectionChildValueN"
   *   }
   * }
   * ```
   * Defaults to false — values nest under the component key unless extendParentObject is explicitly true (matches the form builder and submission validator)
   */
  extendParentObject?: boolean;
} & BIQBaseFormComponentSchema;

/** The zod schema for the object section component based on the section type schema */
export const BIQObjectSectionZodSchema = BIQBaseFormComponentZodSchema.extend({
  type: z.literal(BIQFormComponentType.Section),
  children: biqFormComponentArrayZodSchema,

  default: z.record(z.string(), z.any()).optional(),

  gap: BIQElementSizeZodSchema.optional(),

  sectionLabelOrder: z.union([z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)]).optional(),
  sectionLabelColor: BIQColorZodSchema.optional(),

  sectionDescriptionColor: BIQColorZodSchema.optional(),

  sectionDividerColor: BIQColorZodSchema.optional(),
  sectionDividerWeight: z.number().min(0).optional(),

  extendParentObject: z.boolean().optional(),
});

// *********** The collapse component which is used to build a collapsible section out of a set of components *********

/** The type of the schema for the collapse component (similar to `section` but the children are rendered in a collapsible section) */
export type BIQObjectCollapseSchema = {
  /** The type of the component is `collapse` for the form builder to know what component to render */
  type: BIQFormComponentType.Collapse;
  /** The children of the collapse. This will be an array of form components to be rendered in the collapse */
  children: BIQFormComponentSchema[];

  /** The default value of the collapse. This will be an object based on the format of the components in the collapse and will be used to pre-populate the collapse */
  default?: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any

  /** The gap between child components. Can be a Mantine size ('xs', 'sm', 'md', 'lg', 'xl') or a number. Defaults to 'sm' */
  gap?: BIQElementSize;

  // ********** The Props to edit the collapse header *********
  /** the order of the labels */
  sectionLabelOrder?: 1 | 2 | 3 | 4 | 5 | 6;
  /** The color of the section label. Defaults to the default text color (black for light theme and white for dark theme) */
  sectionLabelColor?: BIQColor;

  /** The color of the section description. Defaults to the default text color (black for light theme and white for dark theme) */
  sectionDescriptionColor?: BIQColor;

  /** if the collapse should be open by default. Defaults to false */
  defaultOpen?: boolean;

  /**
   * If the section should be returned as the parent object extended or as a nested object with the key as the parent
   * If true, the section values will be merged with this section's parent object values
   * eg of results in the parent object
   * ``` json
   * {
   *   "formKey1": "formValue1",
   *   ...,
   *   "formKeyN": "formValueN",
   *   // the current collapse children values
   *   "collapseChildKey1": "collapseChildValue1",
   *   "collapseChildKey2": "collapseChildValue2",
   *   ...
   *   "collapseChildKeyN": "collapseChildValueN"
   * }
   * ```
   * If false, the section values will be nested under the current sections key
   ** ``` json
   * {
   *   "formKey1": "formValue1",
   *   ...,
   *   "formKeyN": "formValueN",
   *   // the current collapse children values
   *   "collapseKey": {
   *     "collapseChildKey1": "collapseChildValue1",
   *     "collapseChildKey2": "collapseChildValue2",
   *     ...
   *     "collapseChildKeyN": "collapseChildValueN"
   *   }
   * }
   * ```
   * Defaults to false — values nest under the component key unless extendParentObject is explicitly true (matches the form builder and submission validator)
   */
  extendParentObject?: boolean;
} & BIQBaseFormComponentSchema;

/** The zod schema for the collapse component based on the collapse type schema */
export const BIQObjectCollapseZodSchema = BIQBaseFormComponentZodSchema.extend({
  type: z.literal(BIQFormComponentType.Collapse),
  children: biqFormComponentArrayZodSchema,

  default: z.record(z.string(), z.any()).optional(),

  gap: BIQElementSizeZodSchema.optional(),

  sectionLabelOrder: z.union([z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)]).optional(),
  sectionLabelColor: BIQColorZodSchema.optional(),

  sectionDescriptionColor: BIQColorZodSchema.optional(),

  defaultOpen: z.boolean().optional(),

  extendParentObject: z.boolean().optional(),
});

// *********** The Union component which is used to allow a component to be one of multiple types where a select component is used to choose the type *********

/** The type of the schema for the union component */
export type BIQUnionSchema = {
  /** The type of the component is `union` for the form builder to know what component to render */
  type: BIQFormComponentType.Union;
  /**
   * the options to select which child component to render
   * the value needs to be the key of the child component
   * If provided, make sure all the children have a corresponding option and vice versa
   * Defaults to an array of the keys of the children
   */
  unionTypeOptions?: BIQFormSchemaOptions;
  /** the children for each of the union types. The key will be how to choose the child component to render */
  children: Record<string, BIQFormComponentSchema>;

  /** The default value of the union. can be any of the children type for any of the keys in the children object */
  default?: any; // eslint-disable-line @typescript-eslint/no-explicit-any
} & BIQBaseFormComponentSchema;

/** The base zod schema for the union component based on the union type schema */
const BIQBaseUnionZodSchema = BIQBaseFormComponentZodSchema.extend({
  type: z.literal(BIQFormComponentType.Union),
  unionTypeOptions: BIQOptionsZodSchema.optional(),
  children: z.record(z.string(), z.lazy(() => BIQFormComponentZodSchema)),

  default: z.any().optional(),
});

/** the function to super refine the union schema  and validate all union options have a corresponding children entry and vice versa */
const UnionSuperRefine = (data: BIQUnionSchema, ctx: z.RefinementCtx) => {
  // If no union type options are provided, no need to validate since the children keys will be used directly
  if (!data.unionTypeOptions) return;

  const selectKeys = extractEnumValuesFromOptions(data.unionTypeOptions);
  const childrenKeys = Object.keys(data.children);
  // Check if all selectKeys are in childrenKeys
  for (const key of selectKeys) {
    if (!childrenKeys.includes(key)) {
      // if there is an extra option, we need to add an issue that it doesn't have a corresponding children entry
      ctx.addIssue({
        code: 'custom',
        message: `Union type option '${key}' does not have a corresponding children entry`,
        path: ['unionTypeOptions'],
      });
    }
  }

  // Check if all childrenKeys are in selectKeys
  for (const key of childrenKeys) {
    if (!selectKeys.includes(key)) {
      // if there is an extra children entry, we need to add an issue that it doesn't have a corresponding union type option
      ctx.addIssue({
        code: 'custom',
        message: `Children entry '${key}' does not have a corresponding union type option`,
        path: ['children'],
      });
    }
  }
  return;
  
};

export const BIQUnionZodSchema = BIQBaseUnionZodSchema.superRefine(UnionSuperRefine);

// *********** The Conditional component which is used to allow an object to be conditional on one of the properties of the object (a discriminated union) *********

/** The type of the schema for the conditional component */
export type BIQConditionalSchema = {
  /** The type of the component is `conditional` for the form builder to know what component to render */
  type: BIQFormComponentType.Conditional;
  /**
   * The select component to choose the value of the conditional field.
   * The value for the conditional field options will be used to determine which children component to render where the key will be the value of the conditional field
   * The value for the conditional field will be merged into the values of the children components
   */
  conditionalField: BIQSelectSchema;
  /**
   * The children for each of the conditional fields. The key will be the value of the conditional field
   * The children under the key on the selected conditionalField option will be rendered
   * The value for the conditional field will be merged into the values of the children components
   */
  children: Record<string, BIQFormComponentSchema[]>;

  /** The default value of the conditional. can be any of the children type for any of the keys in the children object and the conditional field value will be merged into the values of the children components */
  default?: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any

  /** The gap between child components. Can be a Mantine size ('xs', 'sm', 'md', 'lg', 'xl') or a number. Defaults to 'sm' */
  gap?: BIQElementSize;

  /**
   * If the conditional should be returned as the parent object extended or as a nested object with the key as the parent
   * If true, the conditional values will be merged with this conditional's parent object values
   * eg of results in the parent object
   * ``` json
   * {
   *   "formKey1": "formValue1",
   *   ...,
   *   "formKeyN": "formValueN",
   *   // the current conditional children values
   *   "conditionalFieldKey": "conditionalFieldValue",
   *   "conditionalChildKey1": "conditionalChildValue1",
   *   "conditionalChildKey2": "conditionalChildValue2",
   *   ...
   *   "conditionalChildKeyN": "conditionalChildValueN"
   * }
   * ```
   * If false, the conditional values will be nested under the current conditional's key
   ** ``` json
   * {
   *   "formKey1": "formValue1",
   *   ...,
   *   "formKeyN": "formValueN",
   *   // the current conditional children values
   *   "conditionalKey": {
   *     "conditionalFieldKey": "conditionalFieldValue",
   *     "conditionalChildKey1": "conditionalChildValue1",
   *     "conditionalChildKey2": "conditionalChildValue2",
   *     ...
   *     "conditionalChildKeyN": "conditionalChildValueN"
   *   }
   * }
   * ```
   * Defaults to false — values nest under the component key unless extendParentObject is explicitly true (matches the form builder and submission validator)
   */
  extendParentObject?: boolean;
} & BIQBaseFormComponentSchema;

/** The zod schema for the conditional component based on the conditional type schema */
const BIQBaseConditionalZodSchema = BIQBaseFormComponentZodSchema.extend({
  type: z.literal(BIQFormComponentType.Conditional),
  conditionalField: BIQSelectZodSchema,
  children: z.record(z.string(), biqFormComponentArrayZodSchema),

  default: z.record(z.string(), z.any()).optional(),

  gap: BIQElementSizeZodSchema.optional(),

  extendParentObject: z.boolean().optional(),
});

/**
 * the function to super refine the conditional schema  and validate all conditional options have a corresponding children entry and vice versa
 * also checks to make sure the conditional key is not also a children key
 */
const ConditionalSuperRefine = (data: BIQConditionalSchema, ctx: z.RefinementCtx) => {
  if (!data.conditionalField) return;

  const selectKeys = extractEnumValuesFromOptions(data.conditionalField.options);
  const childrenKeys = Object.keys(data.children);
  // Check if all selectKeys are in childrenKeys
  for (const key of selectKeys) {
    if (!childrenKeys.includes(key)) {
      ctx.addIssue({
        code: 'custom',
        message: `Conditional key '${key}' does not have a corresponding children entry`,
        path: ['conditionalField'],
      });
    }
  }

  // Check if all childrenKeys are in selectKeys
  for (const key of childrenKeys) {
    if (!selectKeys.includes(key)) {
      ctx.addIssue({
        code: 'custom',
        message: `Children entry '${key}' does not have a corresponding conditional key`,
        path: ['children'],
      });
    }
  }

  // check to make sure the conditional key is not also a children key
  for (const key of selectKeys) {
    if (!data.children[key]) continue;
    for (const [childIndex, child] of Object.entries(data.children[key])) {
      if (child.key === data.conditionalField.key) {
        ctx.addIssue({
          code: 'custom',
          message: `Child component key '${child.key}' cannot be the same as the conditional field key '${data.conditionalField.key}'`,
          path: ['children', key, childIndex, 'key'],
        });
      }
    }
  }
  return;
};

export const BIQConditionalZodSchema = BIQBaseConditionalZodSchema.superRefine(ConditionalSuperRefine);

// *********** The zod schema for all the components a form can include. This is also used as the children or items schema for the nested form components *********

/** Forward type declaration to break circular reference */
export type BIQFormComponentSchema =
  | z.infer<typeof BaseFormComponentsZodSchemas[number]>
  | BIQArrayParentSchema
  | BIQObjectSectionSchema
  | BIQObjectCollapseSchema
  | BIQUnionSchema
  | BIQConditionalSchema;

/** The zod schema for all the components that a form can include. We can make it a discriminated union to make sure the schema is correct based on the type of the component */
export const BIQFormComponentZodSchema: z.ZodType<BIQFormComponentSchema> = z.discriminatedUnion('type', [
  ...BaseFormComponentsZodSchemas,
  BIQArrayParentZodSchema,
  BIQObjectSectionZodSchema,
  BIQObjectCollapseZodSchema,
  BIQBaseUnionZodSchema,
  BIQBaseConditionalZodSchema,
] as const).superRefine((data, ctx) => {
  switch (data.type) {
    case BIQFormComponentType.Union:
      // check to make sure the union type options are valid
      return UnionSuperRefine(data, ctx);
    case BIQFormComponentType.Conditional:
      // check to make sure the conditional field is valid and the children are valid
      return ConditionalSuperRefine(data, ctx);
    default:
      return;
  }
});
```
