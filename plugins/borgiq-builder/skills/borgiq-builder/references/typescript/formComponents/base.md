# formComponents/base

Generated from the platform's runtime types. Do not edit.

Types every form component shares: the component `type` and return-type enums, the base props, and colors.

## formComponents/base

**Source:** `formComponents/base.ts`

```typescript
import { z } from 'zod';

/** The BIQ Form Component Return Types for each component in the form rendered by the JSON schema */
export enum BIQFormComponentReturnType {
  /** different string type schemas */
  String = 'string',
  Enum = 'enum',
  
  /** different number type schemas */
  Number = 'number',
  Integer = 'integer',
  
  Boolean = 'boolean',

  /** different object type schemas */
  Object = 'object',
  File = 'file',
  Array = 'array',
  Any = 'any',
}

/** The type of the component */
export enum BIQFormComponentType {
  /** string type inputs */
  Text = 'text', // a basic text input
  TextArea = 'textarea', // a text input that allows for multiple lines
  Password = 'password', // an input for passwords that allows for masking the input
  Pin = 'pin', // an input for pins that can be used for 2FA or OTPs

  Code = 'code', // an input for code as a string that allows for syntax highlighting and basic code formatting
  CodeDiff = 'codeDiff', // an input that allows for comparing two code blocks and highlighting the differences
  MarkdownInput = 'markdownInput', // an input for raw markdown input that allows for formatting and possibly previewing the rendered markdown

  /** select type inputs */
  Select = 'select', // a dropdown select input
  Suggest = 'suggest', // a dropdown input that allows for any text input
  Radio = 'radio', // a radio button input that allows for a single choice from a list
  ButtonGroup = 'buttonGroup', // a group of radio buttons that allows for a single choice from a list
  
  /** date inputs */
  DateTime = 'dateTime', // a date and time input that has a dropdown that allows for selecting a date and time
  Date = 'date', // a date input that has a dropdown that allows for selecting a date
  Time = 'time', // a time input that allows for selecting a time
  Calendar = 'calendar', // a calendar input that allows for selecting a date
  DateRange = 'dateRange', // a date range input that has a dropdown that allows for selecting a start and end date
  CalendarRange = 'calendarRange', // a calendar range input that allows for selecting a start and end date

  /** number type inputs */
  Number = 'number', // a basic number input that
  Currency = 'currency', // a number input that is formatted as a currency
  PhoneNumber = 'phoneNumber', // a number input that is formatted as a phone number
  Percentage = 'percentage', // a number input that is formatted as a percentage
  Rating = 'rating', // a rating input that allows for selecting a star rating
  Slider = 'slider', // a slider input to select a number between a min and max

  /** boolean type inputs */
  Checkbox = 'checkbox', // a checkbox input that allows for a boolean value
  Switch = 'switch', // a switch input that allows for a boolean value
  
  /** any type inputs */
  AnyCodeInput = 'anyCodeInput', // an input that allows for yaml or json input that would be parsed
  AnyModal = 'anyModal', // a modal that allows for yaml or json input that would be parsed

  /** file input */
  FileInput = 'fileInput', // an input component that accepts file(s)
  FileButton = 'fileButton', // a button component that accepts file(s)
  AudioRecordingInput = 'audioRecordingInput', // an input component that allows for an audio recording
  FileDropzone = 'fileDropzone', // a dropzone that allows for a file input
  
  /** object input */
  Section = 'section', // allows for a section of a form that can be saved in the parent or in its own child object
  Collapse = 'collapse', // allows for a section of a form that can be collapsed or expanded and saved in the parent or in its own child object
  Union = 'union', // allows for a section of a form that can be a union of two or more types
  Conditional = 'conditional', // allows for a section of a form that can be conditional on the value of another field and saved in the parent or in its own child object
  
  /** array input */
  ArrayParent = 'arrayParent', // allows for an array of any type of component where the user can add and remove items from the array
  MultiSelect = 'multiSelect', // a select component that allows for multiple selections
  MultiCheckbox = 'multiCheckbox', // a set of checkbox components that allows for multiple selections
  Table = 'table', // a table component that allows for a table of data to be displayed. The table rows can be editable, deletable, and/or selectable

  /** display components */
  Header = 'header', // a header component for titles and subtitles
  Divider = 'divider', // a divider component for separating sections of a form
  Progress = 'progress', // a progress component for displaying a progress bar
  FormButton = 'formButton', // a button component that can be used to submit or reset a form
  UrlButton = 'urlButton', // a button component that can be used to navigate to a url
  Image = 'image', // an image component that can be used to display an image
  Markdown = 'markdown', // a markdown component that can be used to display markdown
  CodeViewer = 'codeViewer', // a code viewer component that can be used to display code
  PdfViewer = 'pdfViewer', // a pdf viewer component that can be used to display a pdf
  FileDownload = 'fileDownload', // a file download component that can be used to download a file
  WebViewer = 'webViewer', // a web view component that can be used to display a web page in an iframe
  TextDisplay = 'textDisplay', // a text display component that can be used to display text with optional copy functionality
}

/**
 * A form can specify that all undefined optional properties should be hidden
 * If this is the case, on the top there will be a button to allow the user to inject the optional properties into the form so they can be edited
 * This helper data is used to render the menu item to inject the optional properties into the form
 */
export type BIQFormComponentHelperData = {
  returnType: (BIQFormComponentReturnType | string)[];
  title: string;
  description?: string;
  key?: string;
  defaultValue: unknown;
  required?: boolean;
};

/** The components that have children components that are nested in the parent component */
export const NestedFormComponentTypes: readonly BIQFormComponentType[] = [
  BIQFormComponentType.Section,
  BIQFormComponentType.Collapse,
  BIQFormComponentType.Conditional,
  BIQFormComponentType.Union,
  BIQFormComponentType.ArrayParent,
] as const;

/** The components that are display components and do not provide any input or output to the form data */
export const BIQDisplayComponentsTypes = [
  BIQFormComponentType.Header,
  BIQFormComponentType.Divider,
  BIQFormComponentType.Progress,
  BIQFormComponentType.FormButton,
  BIQFormComponentType.UrlButton,
  BIQFormComponentType.Image,
  BIQFormComponentType.Markdown,
  BIQFormComponentType.CodeViewer,
  BIQFormComponentType.PdfViewer,
  BIQFormComponentType.FileDownload,
  BIQFormComponentType.WebViewer,
  BIQFormComponentType.TextDisplay,
] as BIQFormComponentType[];

/** The base schema for any form component, both for inputs and display components */
export const BIQBaseComponentZodSchema = z.object({
  /** The key for the component and for form components, the key is the field name. */
  key: z.string(),
});

/** The base schema for any input form components (these are components that contain values from the form data) */
export const BIQBaseFormComponentZodSchema = BIQBaseComponentZodSchema.extend({
  
  /** The label to display above the input. If not set, the key (including parent keys) will be used as the label */
  label: z.string().optional(),
  /** The description to display below the label */
  description: z.string().optional(),
  /** any help text for the input that would be displayed in an info tooltip (additional information) */
  infoText: z.string().optional(),
  
  /** if the input is required */
  required: z.boolean().optional(),
  /** if the input is disabled */
  disabled: z.boolean().optional(),
  /** if the input is read only */
  readOnly: z.boolean().optional(),
  /** if the input is hidden */
  hidden: z.boolean().optional(),
});

export type BIQBaseFormComponentSchema = z.infer<typeof BIQBaseFormComponentZodSchema>;

/** The valid color values */
export const BIQColorZodSchema = z.union([
  z.string().regex(/^#[0-9A-Fa-f]{6}$/, {
    error: 'Color must be a valid hex code (e.g., #FF0000)'
  }),
  z.enum(['red', 'pink', 'grape', 'violet', 'indigo', 'blue', 'cyan', 'teal', 'green', 'lime', 'yellow', 'orange', 'gray', 'black', 'white'], {
    error: 'Color must be one of: red, pink, grape, violet, indigo, blue, cyan, teal, green, lime, yellow, orange, gray, black, white',
  }),
], {
  error: 'The color must be a valid hex code or color name',
});

export type BIQColor = z.infer<typeof BIQColorZodSchema>;

// ********* The following are the types for any list of options, for select, suggest, radio, etc. *********
/** a basic array of strings where the values will be used as the label and value */
const BIQOptionsArrayZodSchema = z.array(z.string());
/** an array of objects where each object has a custom label and value */
const BIQOptionsObjectZodSchema = z.array(z.object({
  label: z.string(),
  value: z.string(),
}));

const BIQBaseOptionsZodSchema = z.union([BIQOptionsArrayZodSchema, BIQOptionsObjectZodSchema]);

/** To allow grouping of options with a header defined by `group` */
const BIQGroupedOptionsZodSchema = z.array(z.object({
  group: z.string(),
  items: BIQBaseOptionsZodSchema,
}));

export const BIQOptionsZodSchema = z.union([BIQBaseOptionsZodSchema, BIQGroupedOptionsZodSchema]);

export type BIQFormSchemaOptions = z.infer<typeof BIQOptionsZodSchema>;

// ********* The following are the types for the table component column types *********

/** The schema for the editing properties of a table column */
const tableColumnEditVariantZodSchema = z.discriminatedUnion('editVariant', [
  // a simple text input
  z.object({
    editVariant: z.literal('text'),
  }).partial(),
  // a select input with the valid options for the column
  z.object({
    editVariant: z.enum(['select', 'multi-select']),
    editSelectOptions: BIQOptionsZodSchema,
  }),
]);

/** The schema for the filtering properties of a table column */
const tableColumnFilterVariantZodSchema = z.discriminatedUnion('filterVariant', [
  // a simple text search or a checkbox if the column is a boolean or if its defined or not
  z.object({
    filterVariant: z.enum(['text', 'checkbox']),
  }).partial(),
  // a select input with the valid options for the column to filter by
  z.object({
    filterVariant: z.enum(['autocomplete', 'select', 'multi-select']),
    filterSelectOptions: BIQOptionsZodSchema,
  }),
  // a date input with the range of dates for the column to filter by
  z.object({
    filterVariant: z.enum(['date', 'date-range']),
    minDate: z.iso.datetime().optional(),
    maxDate: z.iso.datetime().optional(),
  }),
  // a number range input with the min and max values for the column to filter by
  z.object({
    filterVariant: z.enum(['range', 'range-slider']),
    min: z.number().optional(),
    max: z.number().optional(),
  }),
]);

/** The custom schema to define a table column */
export const BIQTableColumnZodSchema =  z.object({
  /** The header to display at the top of the column */
  header: z.string(),
  /** The key that will be used to access the data for the column */
  key: z.string(),
  /** The width of the column in pixels if the table and/or the column is resizable */
  size: z.number().optional(),
  /** The minimum width of the column in pixels if the table and/or the column is resizable */
  minSize: z.number().optional(),
  /** The maximum width of the column in pixels if the table and/or the column is resizable */
  maxSize: z.number().optional(),

  /** If the value in the column for each row should be clickable and copyable to the clipboard */
  enableClickToCopy: z.boolean().optional(),
  /** If to render the menu of actions for the column, this is rendered as 3 dots beside the column header. Defaults to table setting */
  enableColumnActions: z.boolean().optional(),
  /** If to allow the user to filter the rows based on the values of the column. Defaults to table setting */
  enableColumnFilter: z.boolean().optional(),
  /** If to allow the user to reorder the column by dragging and dropping it. Defaults to table setting */
  enableColumnOrdering: z.boolean().optional(),
  /** If to allow the user to edit the type of filter that is applied to the column, eg contains, equals, not equals, between, greater than, less than, etc. Defaults to table setting */
  enableColumnFilterModes: z.boolean().optional(),
  /** If to allow the user to edit the values of the column. Defaults to true if the table is editable. */
  enableEditing: z.boolean().optional(),
  /** If to include the column in the global search. Defaults to true if the table has a global search. */
  enableGlobalFilter: z.boolean().optional(),
  /** If to allow the user to group the rows based on the values of the column. Defaults to table setting */
  enableGrouping: z.boolean().optional(),
  /** If to allow the user to hide the column. Defaults to table setting */
  enableHiding: z.boolean().optional(),
  /** If to allow the user to resize the column. Defaults to table setting */
  enableResizing: z.boolean().optional(),
  /** If to allow the user to sort the rows based on the values of the column. Defaults to table setting */
  enableSorting: z.boolean().optional(),
  /** If to allow the user to remove the sorting of the rows based on the values of the column. Defaults to table setting */
  enableSortingRemoval: z.boolean().optional(),
  /** If to allow the user to sort the rows based on multiple columns (allowed by shift + click on the column header). Defaults to table setting */
  enableMultiSort: z.boolean().optional(),
  /** If to allow the user to remove the sorting of the rows based on multiple columns after it has been applied. Defaults to table setting */
  enableMultiRemove: z.boolean().optional(),

  /** If to sort the undefined values of the column or if to prioritize them (1 = top, -1 = bottom). Defaults to false */
  sortUndefined: z.union([z.literal(false), z.literal(1), z.literal(-1)]).optional(),
}).and(tableColumnEditVariantZodSchema)
  .and(tableColumnFilterVariantZodSchema);

/** The schema for a buttons variant styles based on Mantine Button variants */
export const BIQButtonStyleZodSchema = z.enum(['filled', 'outline', 'light', 'subtle', 'transparent', 'white']);

export type BIQButtonStyle = z.infer<typeof BIQButtonStyleZodSchema>;

/** The schema for the size of components or any values, based on Mantine Sizes */
const BIQMantineSizeZodSchema = z.enum(['xs', 'sm', 'md', 'lg', 'xl']);

const BIQCompactButtonSizeZodSchema = z.enum(['compact-xs', 'compact-sm', 'compact-md', 'compact-lg', 'compact-xl',]);

/** The schema for the size of button components or any values, based on Mantine Sizes */
export const BIQButtonComponentSizeZodSchema = z.union([BIQMantineSizeZodSchema, BIQCompactButtonSizeZodSchema]);

export type BIQButtonComponentSize = z.infer<typeof BIQButtonComponentSizeZodSchema>;

/** The schema for the size of text that can be either a Mantine size or the raw css size string (eg. '12px' or '1rem') */
export const BIQTextSizeZodSchema = z.union([BIQMantineSizeZodSchema, z.string()]);

export type BIQTextSize = z.infer<typeof BIQTextSizeZodSchema>;

/** The schema for a flexible size that can be either a Mantine size, a number (pixels), or the raw css size string (eg. '12px' or '1rem') */
export const BIQElementSizeZodSchema = z.union([BIQMantineSizeZodSchema, z.number(), z.string()]);

export type BIQElementSize = z.infer<typeof BIQElementSizeZodSchema>;
```
