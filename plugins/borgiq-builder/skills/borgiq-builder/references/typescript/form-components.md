# Form Components

Zod schemas and TypeScript types for InterfaceTriggerActor and InterfaceActor form components. Covers string inputs (text, select, radio, etc.), number inputs, boolean inputs, date inputs, file inputs, array inputs, display components, and any-type components.

## Table of Contents

- [formComponents/any/codeInput.ts](#formcomponentsanycodeinput)
- [formComponents/any/modal.ts](#formcomponentsanymodal)
- [formComponents/array/multiCheckbox.ts](#formcomponentsarraymulticheckbox)
- [formComponents/array/multiSelect.ts](#formcomponentsarraymultiselect)
- [formComponents/array/table.ts](#formcomponentsarraytable)
- [formComponents/base.ts](#formcomponentsbase)
- [formComponents/boolean/checkbox.ts](#formcomponentsbooleancheckbox)
- [formComponents/boolean/switch.ts](#formcomponentsbooleanswitch)
- [formComponents/date/calendar.ts](#formcomponentsdatecalendar)
- [formComponents/date/calendarRange.ts](#formcomponentsdatecalendarrange)
- [formComponents/date/date.ts](#formcomponentsdatedate)
- [formComponents/date/dateRange.ts](#formcomponentsdatedaterange)
- [formComponents/date/dateTime.ts](#formcomponentsdatedatetime)
- [formComponents/date/dateValue.ts](#formcomponentsdatedatevalue)
- [formComponents/date/time.ts](#formcomponentsdatetime)
- [formComponents/display/code.ts](#formcomponentsdisplaycode)
- [formComponents/display/divider.ts](#formcomponentsdisplaydivider)
- [formComponents/display/fileDownload.ts](#formcomponentsdisplayfiledownload)
- [formComponents/display/formButton.ts](#formcomponentsdisplayformbutton)
- [formComponents/display/header.ts](#formcomponentsdisplayheader)
- [formComponents/display/image.ts](#formcomponentsdisplayimage)
- [formComponents/display/markdown.ts](#formcomponentsdisplaymarkdown)
- [formComponents/display/pdf.ts](#formcomponentsdisplaypdf)
- [formComponents/display/progress.ts](#formcomponentsdisplayprogress)
- [formComponents/display/textDisplay.ts](#formcomponentsdisplaytextdisplay)
- [formComponents/display/urlButton.ts](#formcomponentsdisplayurlbutton)
- [formComponents/display/webViewer.ts](#formcomponentsdisplaywebviewer)
- [formComponents/file/audioRecording.ts](#formcomponentsfileaudiorecording)
- [formComponents/file/fileButton.ts](#formcomponentsfilefilebutton)
- [formComponents/file/fileDropzone.ts](#formcomponentsfilefiledropzone)
- [formComponents/file/fileInput.ts](#formcomponentsfilefileinput)
- [formComponents/form.ts](#formcomponentsform)
- [formComponents/index.ts](#formcomponentsindex)
- [formComponents/number/currency.ts](#formcomponentsnumbercurrency)
- [formComponents/number/number.ts](#formcomponentsnumbernumber)
- [formComponents/number/percentage.ts](#formcomponentsnumberpercentage)
- [formComponents/number/rating.ts](#formcomponentsnumberrating)
- [formComponents/number/slider.ts](#formcomponentsnumberslider)
- [formComponents/string/buttonGroup.ts](#formcomponentsstringbuttongroup)
- [formComponents/string/code.ts](#formcomponentsstringcode)
- [formComponents/string/codeDiff.ts](#formcomponentsstringcodediff)
- [formComponents/string/markdown.ts](#formcomponentsstringmarkdown)
- [formComponents/string/password.ts](#formcomponentsstringpassword)
- [formComponents/string/phoneNumber.ts](#formcomponentsstringphonenumber)
- [formComponents/string/pin.ts](#formcomponentsstringpin)
- [formComponents/string/radio.ts](#formcomponentsstringradio)
- [formComponents/string/select.ts](#formcomponentsstringselect)
- [formComponents/string/suggest.ts](#formcomponentsstringsuggest)
- [formComponents/string/text.ts](#formcomponentsstringtext)
- [formComponents/string/textArea.ts](#formcomponentsstringtextarea)

## formComponents/any/codeInput

**Source:** `formComponents/any/codeInput.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for an object or other native javascript types input using a code editor (codemirror editor) using yaml or json parsing */
export const BIQAnyCodeInputZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `anyCodeInput` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.AnyCodeInput),

  /** The default value for the form input. The object will be be converted to the correct format based on the language selected */
  default: z.any().optional(),
  /** The placeholder to render in the input section */
  placeholder: z.any().optional(),

  /** the language the input will be formatted in, the stringified input will be converted to a javascript object (yaml.load or JSON.parse) */
  language: z.enum(['yaml', 'json']).optional(),
  

  /** wrap the lines of the input in the code editor */
  wrapLines: z.boolean().optional(),
  /** the minimum lines of the code editor. Defaults to 10 */
  minLines: z.number().optional(),
  /** the maximum lines of the code editor. If not set, the code editor will auto-resize to fit the content */
  maxLines: z.number().optional(),
  /** to set a specific height of the code editor (this will override the minLines and maxLines) */
  height: z.union([z.number(), z.string()]).optional(),
  /** the width of the code editor defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** if the component is a code editor let it auto-resize to fit content, defaults to true */
  autoResize: z.boolean().optional(),
});

export type BIQAnyCodeInputSchema = z.infer<typeof BIQAnyCodeInputZodSchema>;
```

## formComponents/any/modal

**Source:** `formComponents/any/modal.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema, BIQColorZodSchema, BIQButtonStyleZodSchema, BIQButtonComponentSizeZodSchema } from '../base.js';

/**
 *  The schema for an object or other native javascript types input using a code editor (codemirror editor) using yaml or json parsing.
 *  The codemirror editor will be rendered in a modal for a larger input area.
 **/
export const BIQAnyModalZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `anyModal` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.AnyModal),

  /** The default value for the form input. The object will be be converted to the correct format based on the language selected */
  default: z.any().optional(),
  /** The placeholder to render in the input section */
  placeholder: z.any().optional(),

  /** the language the input will be formatted in, the stringified input will be converted to a javascript object (yaml.load or JSON.parse) */
  language: z.enum(['yaml', 'json']).optional(),
  

  // ********** The Props to edit the codemirror editor *********
  /** wrap the lines of the code editor */
  wrapLines: z.boolean().optional(),
  /** the minimum lines of the code editor */
  minLines: z.number().optional(),
  /** the maximum lines of the code editor */
  maxLines: z.number().optional(),
  /** the set height of the code editor */
  height: z.union([z.number(), z.string()]).optional(),
  /** the width of the code editor defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** if the component is a code editor let it auto-resize to fit content, defaults to true */
  autoResize: z.boolean().optional(),

  // ********** The Props to edit the button to open the modal that is rendered in the form *********
  /** the text to display on the button to open the modal. Defaults to Edit */
  openButtonText: z.string().optional(),
  /** the color of the button to open the modal. Defaults to the Theme Color */
  openButtonColor: BIQColorZodSchema.optional(),
  /** the variant of the button to open the modal. Defaults to Outline */
  openButtonVariant: BIQButtonStyleZodSchema.optional(),
  /** the size of the button to open the modal. Defaults to md */
  openButtonSize: BIQButtonComponentSizeZodSchema.optional(),

  // ********** The Props to edit the button to close the modal that is rendered on the bottom of the modal *********
  /** the text to display on the button to close the modal. Defaults to Close */
  closeButtonText: z.string().optional(),
  /** the color of the button to close the modal. Defaults to the Theme Color */
  closeButtonColor: BIQColorZodSchema.optional(),
  /** the variant of the button to close the modal. Defaults to Filled */
  closeButtonVariant: BIQButtonStyleZodSchema.optional(),
  /** the size of the button to close the modal. Defaults to md */
  closeButtonSize: BIQButtonComponentSizeZodSchema.optional(),
});

export type BIQAnyModalSchema = z.infer<typeof BIQAnyModalZodSchema>;
```

## formComponents/array/multiCheckbox

**Source:** `formComponents/array/multiCheckbox.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQOptionsZodSchema, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a multi checkbox input */
export const BIQMultiCheckboxZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `multiCheckbox` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.MultiCheckbox),

  /** The default value for the form input */
  default: z.array(z.string()).optional(),
  /** The options that will define the values and labels for the checkboxes */
  options: BIQOptionsZodSchema,
  /** The min number of checkboxes that can be selected */
  minLength: z.number().optional(),
  /** The max number of checkboxes that can be selected */
  maxLength: z.number().optional(),

  // ********** The Props to edit the select all option, this is a checkbox at the top of the checkboxes to allow the user to select all the checkboxes at once *********
  /** If to render the select all option to allow the user to select all the checkboxes */
  selectAllOption: z.boolean().optional(),
  /** The label for the select all option */
  selectAllOptionLabel: z.string().optional(),

  /** The orientation of the group of checkboxes. Defaults to horizontal */
  orientation: z.enum(['vertical', 'horizontal']).optional(),
});

export type BIQMultiCheckboxSchema = z.infer<typeof BIQMultiCheckboxZodSchema>;
```

## formComponents/array/multiSelect

**Source:** `formComponents/array/multiSelect.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQOptionsZodSchema, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a multi select input */
export const BIQMultiSelectZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `multiSelect` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.MultiSelect),

  /** The default value for the form input */
  default: z.array(z.string()).optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),
  /** The options that will define the values and labels for the select options */
  options: BIQOptionsZodSchema,
  /** The min number of options that can be selected */
  minLength: z.number().optional(),
  /** The max number of options that can be selected */
  maxLength: z.number().optional(),

  /** If the input element can allow the user to search for options */
  searchable: z.boolean().optional(),
  /** The message to display when no options are found */
  nothingFoundMessage: z.string().optional(),

  /** The position of the check icon to the left or right of the option label in the dropdown menu in the select element */
  checkIconPosition: z.enum(['left', 'right']).optional(),
});

export type BIQMultiSelectSchema = z.infer<typeof BIQMultiSelectZodSchema>;
```

## formComponents/array/table

**Source:** `formComponents/array/table.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQTableColumnZodSchema, BIQBaseFormComponentZodSchema, BIQButtonStyleZodSchema, BIQColorZodSchema } from '../base.js';

/** The different types of columns that can be used in the table */
export enum BIQColumnTypes {
  /** different string type schemas */
  String = 'string',
  Enum = 'enum',
  
  /** different number type schemas */
  Number = 'number',
  Integer = 'integer',
  
  Boolean = 'boolean',
}

/** The schema for a table input using the React Mantine Table library */
export const BIQTableZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `table` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Table),
 
  /** The data that will be used to populate the table */
  data: z.array(z.any()),
  /** The default value for the form input. For a selectable table, the default value would be the selected rows from data. Defaults to an empty array for a selectable table. This will be ignored if selectable is false */
  default: z.array(z.any()).optional(),
  /** The min number of rows that can be in the table */
  minLength: z.number().optional(),
  /** The max number of rows that can be in the table */
  maxLength: z.number().optional(),

  /** The configuration of the columns and headers for the table based on the React Mantine Table library column configuration */
  columns: z.array(BIQTableColumnZodSchema),

  /** The schema for the columns types that will be used to build the zod schema for the table columns */
  columnSchema: z.record(z.string(), z.enum(BIQColumnTypes)).optional(),

  // ******************** The React Mantine Table library props ********************

  // ********** The Props to edit the rows of the table (editing, creating, submitting, etc) *********
  /** If to allow the individual rows to be edited */
  enableEditing: z.boolean().optional(),
  /** The display mode for the editing of the rows */
  editDisplayMode: z.enum(['modal', 'row', 'cell', 'table']).optional(),
  /** If to allow the user to create new rows */
  enableCreate: z.boolean().optional(),
  /** The display mode for the creation of the rows. Defaults to modal */
  createDisplayMode: z.enum(['modal', 'row']).optional(),
  /** The text to display on the button to create a new row. Button will be only a + icon if not set */
  createButtonText: z.string().optional(),
  /** The color of the button to create a new row. Defaults to the Theme Color */
  createButtonColor: BIQColorZodSchema.optional(),
  /** The variant of the button to create a new row. Defaults to Outline */
  createButtonVariant: BIQButtonStyleZodSchema.optional(),
  /** The position of the actions column for the rows (the column with edit, delete, etc actions). Defaults to last */
  positionActionsColumn: z.enum(['first', 'last']).optional(),
  /** If to allow the user to submit the row. Defaults to true */
  enableSubmitRow: z.boolean().optional(),

  // ********** The Props to edit the sorting of the rows *********
  /** If to allow the user to sort the rows based on any of the columns. Defaults to true */
  enableSorting: z.boolean().optional(),
  /** If to allow the user to remove the sorting of the rows after it has been applied. Defaults to true */
  enableSortingRemoval: z.boolean().optional(),
  /** If to allow the user to sort the rows based on multiple columns (allowed by shift + click on the column header). Defaults to true */
  enableMultiSort: z.boolean().optional(),
  /** If to allow the user to remove the sorting of the rows based on multiple columns after it has been applied. Defaults to true */
  enableMultiRemove: z.boolean().optional(),

  // ********** The Props to edit the column features *********
  /** If to allow the user to filter the rows based on the values of the columns. Defaults to true */
  enableColumnFilter: z.boolean().optional(),
  /** If to allow the user to edit the type of filter that is applied to the columns, eg contains, equals, not equals, between, greater than, less than, etc. Defaults to false */
  enableColumnFilterModes: z.boolean().optional(),
  /** If to allow the user to reorder the columns by dragging and dropping them. Defaults to false (unless enableGrouping is true) */
  enableColumnOrdering: z.boolean().optional(),
  /** If to allow the user to pin the columns to the left or right. Defaults to false */
  enableColumnPinning: z.boolean().optional(),
  /** If to allow the user to resize the columns. Defaults to false */
  enableColumnResizing: z.boolean().optional(),
  /** If to render the menu of actions for all the columns, this is rendered as 3 dots beside the column header. Defaults to true */
  enableColumnActions: z.boolean().optional(),
  /** If to allow the user to hide the columns. Defaults to true */
  enableHiding: z.boolean().optional(),
  /** If to allow the user to group the rows based on the values of the columns. Defaults to false */
  enableGrouping: z.boolean().optional(),

  // ********** The Props to edit the filtering of the rows *********
  /** If to allow the user to filter the rows based on the values of the columns. Defaults to true */
  enableFilter: z.boolean().optional(),
  /** If to highlight the matches of the filter on the resulting rows. Defaults to true */
  enableFilterMatchHighlighting: z.boolean().optional(),
  /** If to allow the user to filter the rows based on a search across all columns. The global search is the search bar at the top of the table. Defaults to true */
  enableGlobalFilter: z.boolean().optional(),
  /** The position of the global filter. Defaults to left */
  positionGlobalFilter: z.enum(['left', 'right', 'none']).optional(),

  // ********** The Props to edit the selection of the rows *********
  /** If to allow the user to select rows. Defaults to false */
  enableRowSelection: z.boolean().optional(),
  /** If to allow the user to select all rows. Defaults to true */
  enableSelectAll: z.boolean().optional(),
  /** The display mode for the selection of the rows. Defaults to checkbox if enableMultiRowSelection is true/undefined or radio when enableMultiRowSelection is false */
  selectDisplayMode: z.enum(['checkbox', 'radio', 'switch']).optional(),
  /** If to allow the user to select multiple rows. Defaults to true */
  enableMultiRowSelection: z.boolean().optional(),

  // ********** The Props to edit the pagination of the rows *********
  /** If to allow the user to paginate the rows. Defaults to true */
  enablePagination: z.boolean().optional(),
  /** The position of the pagination. Defaults to bottom */
  positionPagination: z.enum(['bottom', 'top', 'both']).optional(),

  // ********** The Props to edit the toolbar of the table *********
  /** If render the top toolbar (global search, filter, table actions, add row, etc). Defaults to true */
  enableTopToolbar: z.boolean().optional(),
  /** If render the bottom toolbar (pagination, page size, etc). Defaults to true */
  enableBottomToolbar: z.boolean().optional(),

  // ********** The Props to edit the initial state of the table *********
  /** The initial state of the table */
  initialState: z.object({
    /** The initial state of the column filters. Defaults to an empty array (no initial filters) */
    columnFilters: z.array(z.object({
      /** The id of the column to filter */
      id: z.string(),
      /** The value of the column to filter by */
      value: z.union([z.string(), z.number(), z.boolean()]),
    })).optional(),

    /** The initial state of the column order where the value is the id of the column. Defaults to the order of the columns in the columns prop */
    columnOrder: z.array(z.string()).optional(),

    /** The initial state of the column sizing where the key is the id of the column and the value is the width of the column. Defaults to an empty object auto-sizing the columns */
    columnSizing: z.record(z.string(), z.number()).optional(),
    
    /** The initial state of the column visibility where the key is the id of the column and the value is a boolean to determine if the column is visible. Defaults to all columns being visible initially */
    columnVisibility: z.record(z.string(), z.boolean()).optional(),
        
    /** The initial state of the columns that are sorted. Defaults to an empty array (no initial sorting) */
    sorting: z.array(z.object({
      /** The id of the column to sort */
      id: z.string(),
      /** If the column is sorted in descending order */
      desc: z.boolean(),
    })).optional(),
    
    /** The initial state of the pagination. Defaults to { pageIndex: 0, pageSize: 10 } */
    pagination: z.object({
      /** The index of the page to display */
      pageIndex: z.number(),
      /** The number of rows to display per page */
      pageSize: z.number(),
    }).optional(),
  }).optional(),
});

export type BIQTableSchema = z.infer<typeof BIQTableZodSchema>;
```

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

## formComponents/boolean/checkbox

**Source:** `formComponents/boolean/checkbox.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema, BIQColorZodSchema } from '../base.js';

/** The schema for a checkbox input */
export const BIQCheckboxZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `checkbox` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Checkbox),

  /** the default value for the form input */
  default: z.boolean().optional(),
  /** the variant of the checkbox. Defaults to filled */
  variant: z.enum(['filled', 'outlined']).optional(),
  /** the color of the checkbox. Defaults to the Theme Color */
  color: BIQColorZodSchema.optional(),

  /** if the label is inline with the checkbox. Defaults to false */
  inlineLabel: z.boolean().optional(),
  /** the position of the label when inlineLabel is true. Defaults to right */
  labelPosition: z.enum(['left', 'right']).optional(),
});

export type BIQCheckboxSchema = z.infer<typeof BIQCheckboxZodSchema>;
```

## formComponents/boolean/switch

**Source:** `formComponents/boolean/switch.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema, BIQColorZodSchema } from '../base.js';

/** The schema for a switch input */
export const BIQSwitchZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `switch` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Switch),

  /** the default value for the form input. */
  default: z.boolean().optional(),
  /** the color of the switch. Defaults to the Theme Color */
  color: BIQColorZodSchema.optional(),

  /** if the label is inline with the switch. Defaults to false */
  inlineLabel: z.boolean().optional(),
  /** the position of the label when inlineLabel is true. Defaults to right */
  labelPosition: z.enum(['left', 'right']).optional(),
});

export type BIQSwitchSchema = z.infer<typeof BIQSwitchZodSchema>;
```

## formComponents/date/calendar

**Source:** `formComponents/date/calendar.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';
import { BIQIsoDateValueZodSchema } from './dateValue.js';

/** The schema for a calendar input */
export const BIQCalendarZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `calendar` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Calendar),

  /** the default value for the form input */
  default: BIQIsoDateValueZodSchema.optional(),

  /** the minimum date that can be selected. If not set, there is no minimum date */
  minDate: BIQIsoDateValueZodSchema.optional(),
  /** the maximum date that can be selected. If not set, there is no maximum date */
  maxDate: BIQIsoDateValueZodSchema.optional(),

  /** the first day of the week where 0 is sunday and 6 is saturday. Defaults to 1 (monday) */
  firstDayOfTheWeek: z.union([z.literal(0), z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)]).optional(),
  /** if to highlight the current date on the calendar. Defaults to true */
  highlightToday: z.boolean().optional(),
  /** if to hide the weekday names on the top of the calendar. Defaults to false */
  hideWeekdays: z.boolean().optional(),
  /** if to allow deselecting the date. Defaults to false */
  allowDeselect: z.boolean().optional(),
});

export type BIQCalendarSchema = z.infer<typeof BIQCalendarZodSchema>;
```

## formComponents/date/calendarRange

**Source:** `formComponents/date/calendarRange.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';
import { BIQIsoDateValueZodSchema } from './dateValue.js';

/** The schema for a calendar range input */
export const BIQCalendarRangeZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `calendarRange` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.CalendarRange),

  /** the default value for the form input */
  default: z.object({
    startDate: BIQIsoDateValueZodSchema,
    endDate: BIQIsoDateValueZodSchema,
  }).optional(),

  /** the minimum date that can be selected. If not set, there is no minimum date */
  minDate: BIQIsoDateValueZodSchema.optional(),
  /** the maximum date that can be selected. If not set, there is no maximum date */
  maxDate: BIQIsoDateValueZodSchema.optional(),

  /** the first day of the week where 0 is sunday and 6 is saturday. Defaults to 1 (monday) */
  firstDayOfTheWeek: z.union([z.literal(0), z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)]).optional(),
  /** if to highlight the current date on the calendar. Defaults to true */
  highlightToday: z.boolean().optional(),
  /** if to hide the weekday names on the top of the calendar. Defaults to false */
  hideWeekdays: z.boolean().optional(),
});

export type BIQCalendarRangeSchema = z.infer<typeof BIQCalendarRangeZodSchema>;
```

## formComponents/date/date

**Source:** `formComponents/date/date.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';
import { BIQIsoDateValueZodSchema } from './dateValue.js';

/** The schema for a date input */
export const BIQDateZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `date` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Date),

  /** the default value for the form input */
  default: BIQIsoDateValueZodSchema.optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** the minimum date that can be selected. If not set, there is no minimum date */
  minDate: BIQIsoDateValueZodSchema.optional(),
  /** the maximum date that can be selected. If not set, there is no maximum date */
  maxDate: BIQIsoDateValueZodSchema.optional(),

  /** the first day of the week where 0 is sunday and 6 is saturday. Defaults to 1 (monday) */
  firstDayOfTheWeek: z.union([z.literal(0), z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)]).optional(),
  /** if to highlight the current date on the calendar. Defaults to true */
  highlightToday: z.boolean().optional(),
  /** if to hide the weekday names on the top of the calendar. Defaults to false */
  hideWeekdays: z.boolean().optional(),
  /** if to allow deselecting the date. Defaults to false */
  allowDeselect: z.boolean().optional(),
});

export type BIQDateSchema = z.infer<typeof BIQDateZodSchema>;
```

## formComponents/date/dateRange

**Source:** `formComponents/date/dateRange.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';
import { BIQIsoDateValueZodSchema } from './dateValue.js';

/** The schema for a date range input */
export const BIQDateRangeZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `dateRange` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.DateRange),

  /** the default value for the form input */
  default: z.object({
    startDate: BIQIsoDateValueZodSchema,
    endDate: BIQIsoDateValueZodSchema,
  }).optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  minDate: BIQIsoDateValueZodSchema.optional(),
  maxDate: BIQIsoDateValueZodSchema.optional(),

  /** the first day of the week where 0 is sunday and 6 is saturday */
  firstDayOfTheWeek: z.union([z.literal(0), z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)]).optional(),
  highlightToday: z.boolean().optional(),
  hideWeekdays: z.boolean().optional(),
});

export type BIQDateRangeSchema = z.infer<typeof BIQDateRangeZodSchema>;
```

## formComponents/date/dateTime

**Source:** `formComponents/date/dateTime.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';
import { BIQIsoDateValueZodSchema } from './dateValue.js';

/** The schema for a date time input */
export const BIQDateTimeZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `dateTime` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.DateTime),

  /** the default value for the form input */
  default: BIQIsoDateValueZodSchema.optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** if to allow the user to select the time with seconds in the input. Defaults to false */
  withSeconds: z.boolean().optional(),

  /** the minimum date time that can be selected. If not set, there is no minimum date time */
  minDate: BIQIsoDateValueZodSchema.optional(),
  /** the maximum date time that can be selected. If not set, there is no maximum date time */
  maxDate: BIQIsoDateValueZodSchema.optional(),

  /** the first day of the week where 0 is sunday and 6 is saturday. Defaults to 1 (monday) */
  firstDayOfTheWeek: z.union([z.literal(0), z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)]).optional(),
  /** if to highlight the current date on the calendar. Defaults to true */
  highlightToday: z.boolean().optional(),
  /** if to hide the weekday names on the top of the calendar. Defaults to false */
  hideWeekdays: z.boolean().optional(),
});

export type BIQDateTimeSchema = z.infer<typeof BIQDateTimeZodSchema>;
```

## formComponents/date/dateValue

**Source:** `formComponents/date/dateValue.ts`

```typescript
import { z } from 'zod';

/**
 * A date-or-datetime value as an ISO string.
 *
 * YAML parsers (js-yaml's default schema) turn unquoted values like
 * `default: 2026-07-24` or `default: 2026-07-24T10:00:00Z` into JS `Date`
 * objects before the schema ever sees them, so a plain string check would
 * reject YAML the author reasonably wrote. Coerce `Date` instances back to
 * their ISO string before validating.
 */
export const BIQIsoDateValueZodSchema = z.preprocess(
  (value) => value instanceof Date ? value.toISOString() : value,
  z.union([z.iso.datetime(), z.iso.date()]),
);
```

## formComponents/date/time

**Source:** `formComponents/date/time.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a time input */
export const BIQTimeZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `time` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Time),

  /** the default value for the form input */
  default: z.iso.time().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** if to allow the user to select the time with seconds in the input. Defaults to false */
  withSeconds: z.boolean().optional(),

  /** the minimum time for the input in 24 hour format. If not set, there is no minimum time */
  minTime: z.iso.time().optional(),
  /** the maximum time for the input in 24 hour format. If not set, there is no maximum time */
  maxTime: z.iso.time().optional(),
});

export type BIQTimeSchema = z.infer<typeof BIQTimeZodSchema>;
```

## formComponents/display/code

**Source:** `formComponents/display/code.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a code viewer component */
export const BIQCodeViewerZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `codeViewer` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.CodeViewer),

  /** the code string to display in the code block */
  value: z.string(),

  /** the language of the code to apply syntax highlighting. If no language is provided, no syntax highlighting will be applied */
  language: z.string().optional(),

  /** the width of the code block. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** the height of the code block. Defaults to fitting the content height */
  height: z.union([z.number(), z.string()]).optional(),
});

export type BIQCodeViewerSchema = z.infer<typeof BIQCodeViewerZodSchema>;
```

## formComponents/display/divider

**Source:** `formComponents/display/divider.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQColorZodSchema, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a divider component */
export const BIQDividerZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `divider` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Divider),

  /** the color of the divider. Defaults to a dimmed gray color */
  color: BIQColorZodSchema.optional(),
  /** the weight of the divider. Defaults to 1 */
  weight: z.number().min(0).optional(),
  
  /** the text to display in the divider. If no text is provided, the divider will be displayed as just a line */
  text: z.string().optional(),
  /** the text alignment of the divider. Defaults to `center` and only applies if text is provided */
  textAlignment: z.enum(['left', 'center', 'right']).optional(),
});

export type BIQDividerSchema = z.infer<typeof BIQDividerZodSchema>;
```

## formComponents/display/fileDownload

**Source:** `formComponents/display/fileDownload.ts`

```typescript
import { z } from 'zod';

import { BIQFileSchema } from '../../schemas/file.js';
import { BIQFormComponentType, BIQColorZodSchema, BIQButtonStyleZodSchema, BIQButtonComponentSizeZodSchema, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a file download component */
export const BIQFileDownloadZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `fileDownload` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.FileDownload),

  /** the file to download. This can be a BIQFile, a file object, or a url to a file */
  file: z.union([
    // the BIQFile will use the metadata to fetch the file from the server and download it
    BIQFileSchema,
    // the file object will be downloaded directly building the file object in the browser
    z.object({
      name: z.string(),
      mimeType: z.string(),
      base64content: z.string(),
    }),
    // the url will be downloaded directly by opening the url in a new tab
    z.string(),
  ]),

  /** the button text. Defaults to `Download` */
  buttonText: z.string().optional(),
  /** the button color. Defaults to the primary color of the theme */
  buttonColor: BIQColorZodSchema.optional(),
  /** the button variant. Defaults to outlined */
  buttonVariant: BIQButtonStyleZodSchema.optional(),
  /** the button size. Defaults to medium */
  buttonSize: BIQButtonComponentSizeZodSchema.optional(),
});

export type BIQFileDownloadSchema = z.infer<typeof BIQFileDownloadZodSchema>;
```

## formComponents/display/formButton

**Source:** `formComponents/display/formButton.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQColorZodSchema, BIQButtonStyleZodSchema, BIQButtonComponentSizeZodSchema, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a form button component */
export const BIQFormButtonZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `formButton` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.FormButton),

  /** the text to display in the button. Defaults to `Submit` for a submit button and `Reset` for a reset button */
  text: z.string().optional(),
  /** the color of the button. Defaults to the primary color of the theme */
  color: BIQColorZodSchema.optional(),
  /** the variant of the button. Defaults to filled */
  variant: BIQButtonStyleZodSchema.optional(),
  /** the size of the button. Defaults to medium */
  size: BIQButtonComponentSizeZodSchema.optional(),

  /** the action type of the button to take on the form, submit submits the form, reset resets the form to default values. Defaults to submit */
  actionType: z.enum(['submit', 'reset']).optional(),
});

export type BIQFormButtonSchema = z.infer<typeof BIQFormButtonZodSchema>;
```

## formComponents/display/header

**Source:** `formComponents/display/header.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQColorZodSchema, BIQBaseComponentZodSchema, BIQTextSizeZodSchema } from '../base.js';

/** The schema for a header component */
export const BIQHeaderZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `header` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Header),

  /** the text to display in the main header */
  value: z.string(),
  /** the order of the header (it needs to be literals to match mantine's order type), can a number from 1 to 6. Defaults to 1 */
  order: z.union([
    z.literal(1),
    z.literal(2),
    z.literal(3),
    z.literal(4),
    z.literal(5),
    z.literal(6),
  ]).optional(),
  /** the color of the header. Defaults to the default text color based on the theme (black for light theme and white for dark theme) */
  color: BIQColorZodSchema.optional(),

  /** the subtitle text to display under the header. If no subtitle is provided, the header will not have a subtitle */
  subtitle: z.string().optional(),
  /** the color of the subtitle. Defaults to dimmed color */
  subtitleColor: BIQColorZodSchema.optional(),
  /** the size of the subtitle as a mantine size or a css string. Defaults to xs */
  subtitleSize: BIQTextSizeZodSchema.optional(),
});

export type BIQHeaderSchema = z.infer<typeof BIQHeaderZodSchema>;
```

## formComponents/display/image

**Source:** `formComponents/display/image.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQColorZodSchema, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a image component */
export const BIQImageZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `image` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Image),

  /** the src of the image. This can be the full base64 content of the image or a url to the image */
  src: z.string(),
  /** the width of the image. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** the height of the image. Defaults to 100% */
  height: z.union([z.number(), z.string()]).optional(),

  // ********* The props to add a border to the image. If borderColor and borderWidth are not provided, the image will not have a border *********
  /** the border color of the image. Defaults to black */
  borderColor: BIQColorZodSchema.optional(),
  /** the border width of the image. Defaults to 1px */
  borderWidth: z.union([z.number(), z.string()]).optional(),
  /** the border radius of the image. Defaults to no border radius */
  borderRadius: z.union([z.number(), z.string()]).optional(),
});

export type BIQImageSchema = z.infer<typeof BIQImageZodSchema>;
```

## formComponents/display/markdown

**Source:** `formComponents/display/markdown.ts`

```typescript
import { z } from 'zod';
import { BIQColorZodSchema, BIQFormComponentType, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a markdown component */
export const BIQMarkdownZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `markdown` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Markdown),

  /** the markdown content to display */
  value: z.string(),
 
  /** the width of the markdown area. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** the height of the markdown area. Defaults to 100% */
  height: z.union([z.number(), z.string()]).optional(),

  /** the background color of the markdown area. Defaults to transparent */
  backgroundColor: BIQColorZodSchema.optional(),
});

export type BIQMarkdownSchema = z.infer<typeof BIQMarkdownZodSchema>;
```

## formComponents/display/pdf

**Source:** `formComponents/display/pdf.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a pdf viewer component */
export const BIQPdfViewerZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `pdfViewer` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.PdfViewer),

  /** the src of the pdf. This can be the full base64 content of the pdf or a url to the pdf */
  src: z.string().refine((val) => {
    try {
      new URL(val);
      return true;
    } catch {
      return false;
    }
  }, {
    message: 'Invalid src URL',
  }),
  /** the width of the pdf. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** the height of the pdf. Defaults to 500px */
  height: z.union([z.number(), z.string()]).optional(),
});

export type BIQPdfViewerSchema = z.infer<typeof BIQPdfViewerZodSchema>;
```

## formComponents/display/progress

**Source:** `formComponents/display/progress.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQColorZodSchema, BIQBaseComponentZodSchema, BIQElementSizeZodSchema } from '../base.js';

/** The schema for a progress component */
export const BIQProgressZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `progress` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Progress),

  /** the color of the divider. Defaults to a dimmed gray color */
  color: BIQColorZodSchema.optional(),
  /** the value of the progress from 0 to 100, if steps is set, the value is the floor of the value divided by the steps */
  value: z.number().min(0).max(100),
  /** the number of steps in the progress. Defaults to 1 */
  steps: z.number().min(1).optional(),
  
  /** if the progress bar should be striped. Defaults to false */
  striped: z.boolean().optional(),
  /** if the progress bar should be animated. Defaults to false */
  animated: z.boolean().optional(),
  
  /** the label to display in the progress bar. Defaults to empty */
  label: z.string().optional(),
  /** the label color of the progress bar. Defaults to the color of the progress bar */
  labelColor: BIQColorZodSchema.optional(),
  /** the label font size of the progress bar. Defaults to md */
  labelSize: BIQElementSizeZodSchema.optional(),
  /** the label font weight of the progress bar. Defaults to 400 */
  labelWeight: z.number().optional(),
  /** the label font size of the progress bar. Defaults to 14 */
  labelPosition: z.enum(['top', 'bottom']).optional(),
  /** the label alignment of the progress bar. Defaults to `left` */
  labelAlignment: z.enum(['left', 'center', 'right']).optional(),
});

export type BIQProgressSchema = z.infer<typeof BIQProgressZodSchema>;
```

## formComponents/display/textDisplay

**Source:** `formComponents/display/textDisplay.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseComponentZodSchema, BIQColorZodSchema, BIQTextSizeZodSchema } from '../base.js';

/** The schema for a text display component that shows text with optional copy functionality */
export const BIQTextDisplayZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `textDisplay` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.TextDisplay),

  /** The text value to display */
  value: z.string(),

  /** The color of the text. Defaults to the default text color based on the theme */
  color: BIQColorZodSchema.optional(),

  /** The size of the text. Defaults to 'sm' */
  size: BIQTextSizeZodSchema.optional(),

  /** The font weight of the text (e.g., 'normal', 'bold', or a number like 500) */
  weight: z.union([z.string(), z.number()]).optional(),

  /** If true, the text will be displayed in italic style */
  italic: z.boolean().optional(),

  /** If true, the text will be underlined */
  underline: z.boolean().optional(),

  /** If true, the text will have a strikethrough */
  strikethrough: z.boolean().optional(),

  /** Text transform style: uppercase, lowercase, capitalize, or none */
  transform: z.enum(['uppercase', 'lowercase', 'capitalize', 'none']).optional(),

  /** If true, the text will be displayed in a monospace font */
  monospace: z.boolean().optional(),

  /** If true, shows a copy button to copy the text to clipboard */
  copyable: z.boolean().optional(),
});

export type BIQTextDisplaySchema = z.infer<typeof BIQTextDisplayZodSchema>;
```

## formComponents/display/urlButton

**Source:** `formComponents/display/urlButton.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQColorZodSchema, BIQButtonStyleZodSchema, BIQButtonComponentSizeZodSchema, BIQBaseComponentZodSchema } from '../base.js';

/** The schema for a url button component to navigate to a url */
export const BIQUrlButtonZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `urlButton` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.UrlButton),

  /** the text to display in the button. Defaults to `Open URL` */
  text: z.string().optional(),
  /** the color of the button. Defaults to the primary color of the theme */
  color: BIQColorZodSchema.optional(),
  /** the variant of the button. Defaults to outlined */
  variant: BIQButtonStyleZodSchema.optional(),
  /** the size of the button. Defaults to medium */
  size: BIQButtonComponentSizeZodSchema.optional(),

  /** the url that the button will open when clicked */
  url: z.string(),
  /** if to open the url in the current tab, defaults to false (open in a new tab) */
  openUrlInCurrentPage: z.boolean().optional(),
});

export type BIQUrlButtonSchema = z.infer<typeof BIQUrlButtonZodSchema>;
```

## formComponents/display/webViewer

**Source:** `formComponents/display/webViewer.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseComponentZodSchema } from '../base.js';
import { ZodIssueCode } from 'zod/v3';
import { PermissionsPolicyDirectiveZodSchema } from '../../actorSchemas/trigger/permissionsPolicy.js';

/** The schema for a web viewer component */
export const BIQWebViewZodSchema = BIQBaseComponentZodSchema.extend({
  /** The type of the component is `webViewer` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.WebViewer),

  /** the src url of the web viewer. This can be a url to the web viewer */
  src: z.string().optional().refine((val) => {
    if (!val) return true;
    try {
      new URL(val);
      return true;
    } catch {
      return false;
    }
  }, {
    message: 'Invalid src URL',
  }),
  /** the html content of the web viewer. This can be a html string */
  html: z.string().optional(),
  /** the width of the web viewer. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** the height of the web viewer. Defaults to 500px */
  height: z.union([z.number(), z.string()]).optional(),
  /** if the web viewer should be full screen, this would override the height and width and hide any other components. Defaults to false */
  fullScreen: z.boolean().optional(),
  /** allowed domains for external scripts (e.g., ['https://cdn.example.com', 'https://api.example.com']). Used for CSP script-src directive */
  allowedScriptDomains: z.array(z.url()).optional(),
  /** allowed domains for external stylesheets (e.g., ['https://fonts.googleapis.com', 'https://cdn.example.com']). Used for CSP style-src directive */
  allowedStyleDomains: z.array(z.url()).optional(),
  /** Permissions-Policy directives to enable for the webviewer (e.g., [PermissionsPolicyDirective.ClipboardWrite, PermissionsPolicyDirective.Fullscreen]). Controls access to browser APIs. */
  allowedPermissions: z.array(PermissionsPolicyDirectiveZodSchema).optional(),
  /** Enable unsafe-inline for styles, without hash verification (adds 'unsafe-inline' to style-src CSP). Use with caution as this reduces security. */
  allowInlineStyling: z.boolean().optional(),
  /** Enable unsafe-inline for scripts, without hash verification (adds 'unsafe-inline' to script-src CSP). Use with caution as this significantly reduces security. */
  allowInlineScripts: z.boolean().optional(),
}).superRefine((val, ctx) => {
  if (val.src && val.html) {
    ctx.addIssue({
      code: ZodIssueCode.custom,
      message: 'Only one of src or html must be provided',
      path: ['src'],
    });
    ctx.addIssue({
      code: ZodIssueCode.custom,
      message: 'Only one of src or html must be provided, but not both',
      path: ['html'],
    });
  } else if (!val.src && !val.html) {
    ctx.addIssue({
      code: ZodIssueCode.custom,
      message: 'Either src or html must be provided',
      path: ['src'],
    });
    ctx.addIssue({
      code: ZodIssueCode.custom,
      message: 'Either src or html must be provided',
      path: ['html'],
    });
  }
});

export type BIQWebViewSchema = z.infer<typeof BIQWebViewZodSchema>;
```

## formComponents/file/audioRecording

**Source:** `formComponents/file/audioRecording.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The mime types applicable for audio recordings */
export enum BIQAudioMimeType {
  MPEG = 'audio/mpeg',
  WAV = 'audio/wav',
  OGG = 'audio/ogg',
  WEBM = 'audio/webm',
  AAC = 'audio/aac',
}

/** The file extensions for each mime type for audio recordings */
export const BIQAudioFileExtension: Record<BIQAudioMimeType, string> = {
  [BIQAudioMimeType.MPEG]: 'mp3',
  [BIQAudioMimeType.WAV]: 'wav',
  [BIQAudioMimeType.OGG]: 'oga',
  [BIQAudioMimeType.WEBM]: 'weba',
  [BIQAudioMimeType.AAC]: 'aac',
};

/** The schema for an audio recording input component */
export const BIQAudioRecordingZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `audioRecordingInput` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.AudioRecordingInput),

  /** the max duration of the audio recording in seconds. If not set, the recording will continue until the user stops the recording */
  maxDuration: z.number().optional(),
  /** the mime type of the audio recording (defaults to audio/webm) */
  mimeType: z.enum(BIQAudioMimeType).optional(),
});

export type BIQAudioRecordingSchema = z.infer<typeof BIQAudioRecordingZodSchema>;
```

## formComponents/file/fileButton

**Source:** `formComponents/file/fileButton.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema, BIQColorZodSchema, BIQButtonStyleZodSchema } from '../base.js';

/** The schema for a file button input */
export const BIQFileButtonZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `fileButton` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.FileButton),

  // the accept file types formatted as a comma separated list of mime types. Defaults to `*/*` which means any file type is acceptable.
  // see https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept
  accept: z.string().optional(),

  /** the button text. Defaults to `Upload file` */
  buttonText: z.string().optional(),
  /** the button color. Defaults to the primary color of the theme */
  buttonColor: BIQColorZodSchema.optional(),
  /** the button variant. Defaults to `outline` */
  buttonVariant: BIQButtonStyleZodSchema.optional(),

  // ********** Multiple Files Properties *********
  /** if the input can accept multiple files */
  multiple: z.boolean().optional(),
  /** only if `multiple` is true, the max number of files that can be uploaded */
  maxLength: z.number().optional(),
  /** only if `multiple` is true, the min number of files that can be uploaded */
  minLength: z.number().optional(),

  /** the max file size in bytes. If no max file size is set, the file size will not be checked */
  maxFileSize: z.number().optional(),

  /** show the uploaded file */
  showUploadedFile: z.boolean().optional(),
});

export type BIQFileButtonSchema = z.infer<typeof BIQFileButtonZodSchema>;
```

## formComponents/file/fileDropzone

**Source:** `formComponents/file/fileDropzone.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema, BIQColorZodSchema } from '../base.js';

/** The schema for a file dropzone input */
export const BIQFileDropzoneZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `fileButton` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.FileDropzone),

  // the accept file types formatted as a comma separated list of mime types. Defaults to `*/*` which means any file type is acceptable.
  // see https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept
  accept: z.string().optional(),

  /** The text to display in the dropzone. Defaults to `Drag files here or click to select files` */
  dropzoneText: z.string().optional(),
  /** The color of the dropzone text. Defaults to the primary color of the theme */
  dropzoneTextColor: BIQColorZodSchema.optional(),
  /** The description to display in the dropzone. If not set, the description will not be displayed */
  dropzoneDescription: z.string().optional(),
  /** The color of the dropzone description. Defaults to `dimmed` a light gray color */
  dropzoneDescriptionColor: BIQColorZodSchema.optional(),

  // ********* Multiple Files Properties *********
  /** if the input can accept multiple files */
  multiple: z.boolean().optional(),
  /** If `multiple` is true, the max number of files that can be uploaded */
  maxLength: z.number().optional(),
  /** If `multiple` is true, the min number of files that can be uploaded */
  minLength: z.number().optional(),

  /** the max file size in bytes. If no max file size is set, the file size will not be checked */
  maxFileSize: z.number().optional(),

  /** If to render the list of uploaded files below the dropzone. Defaults to true */
  showUploadedFile: z.boolean().optional(),
});

export type BIQFileDropzoneSchema = z.infer<typeof BIQFileDropzoneZodSchema>;
```

## formComponents/file/fileInput

**Source:** `formComponents/file/fileInput.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a file input */
export const BIQFileInputZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `fileInput` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.FileInput),

  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  // the accept file types formatted as a comma separated list of mime types. Defaults to `*/*` which means any file type is acceptable.
  // see https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept
  accept: z.string().optional(),

  // ********* Multiple Files Properties *********
  /** if the input can accept multiple files */
  multiple: z.boolean().optional(),
  /** If `multiple` is true, the max number of files that can be uploaded */
  maxLength: z.number().optional(),
  /** If `multiple` is true, the min number of files that can be uploaded */
  minLength: z.number().optional(),

  /** the max file size in bytes. If no max file size is set, the file size will not be checked */
  maxFileSize: z.number().optional(),
});

export type BIQFileInputSchema = z.infer<typeof BIQFileInputZodSchema>;
```

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

## formComponents/index

**Source:** `formComponents/index.ts`

```typescript
export * from './any/index.js';
export * from './array/index.js';
export * from './boolean/index.js';
export * from './date/index.js';
export * from './display/index.js';
export * from './file/index.js';
export * from './number/index.js';
export * from './string/index.js';

export * from './form.js';

export {
  BIQFormComponentType,
  BIQFormComponentReturnType,
  NestedFormComponentTypes,
  BIQDisplayComponentsTypes,
} from './base.js';

export type {
  BIQFormSchemaOptions,
  BIQFormComponentHelperData,
} from './base.js';
```

## formComponents/number/currency

**Source:** `formComponents/number/currency.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a currency input */
export const BIQCurrencyZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `currency` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Currency),

  /** the default value for the input */
  default: z.number().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),
  /** The variant on how to render the input. This will only . Defaults to `decimal` */
  variant: z.enum(['decimal', 'integer']).optional(),

  /** the minimum value of the number. If not provided, there is no minimum value */
  minimum: z.number().optional(),
  /** the maximum value of the number. If not provided, there is no maximum value */
  maximum: z.number().optional(),
  /** if the minimum value is exclusive. Defaults to false */
  isExclusiveMinimum: z.boolean().optional(),
  /** if the maximum value is exclusive. Defaults to false */
  isExclusiveMaximum: z.boolean().optional(),

  /** hide controls for the input */
  hideControls: z.boolean().optional(),

  /** the currency to display in the input. Defaults to `$` */
  currencyPrefix: z.string().optional(),
});

export type BIQCurrencySchema = z.infer<typeof BIQCurrencyZodSchema>;
```

## formComponents/number/number

**Source:** `formComponents/number/number.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a number input */
export const BIQNumberZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `number` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Number),

  /** the default value for the input */
  default: z.number().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),
  /** The variant on if the input can have decimals or must be an integer. Defaults to `decimal` */
  variant: z.enum(['decimal', 'integer']).optional(),

  /** the minimum value of the number */
  minimum: z.number().optional(),
  /** the maximum value of the number */
  maximum: z.number().optional(),
  /** if the minimum value is exclusive */
  isExclusiveMinimum: z.boolean().optional(),
  /** if the maximum value is exclusive */
  isExclusiveMaximum: z.boolean().optional(),

  /** hide controls for the input */
  hideControls: z.boolean().optional(),
});

export type BIQNumberSchema = z.infer<typeof BIQNumberZodSchema>;
```

## formComponents/number/percentage

**Source:** `formComponents/number/percentage.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a percentage input */
export const BIQPercentageZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `percentage` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Percentage),

  /** the default value for the input */
  default: z.number().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),
  /** The variant on if the return value should be the decimal or percentage, eg `0.5` or `50` for `50%`. Defaults to `decimal` */
  variant: z.enum(['decimal', 'percentage']).optional(),

  /** the minimum value of the number. If not provided, there is no minimum value */
  minimum: z.number().optional(),
  /** the maximum value of the number. If not provided, there is no maximum value */
  maximum: z.number().optional(),
  /** if the minimum value is exclusive. Defaults to false */
  isExclusiveMinimum: z.boolean().optional(),
  /** if the maximum value is exclusive. Defaults to false */
  isExclusiveMaximum: z.boolean().optional(),

  /** hide controls for the input */
  hideControls: z.boolean().optional(),
});

export type BIQPercentageSchema = z.infer<typeof BIQPercentageZodSchema>;
```

## formComponents/number/rating

**Source:** `formComponents/number/rating.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a rating input */
export const BIQRatingZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `rating` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Rating),

  /** the default value for the input */
  default: z.number().optional(),

  /** the maximum value of the rating. Defaults to 5 */
  maximum: z.number().optional(),
  /** how many fractions each star can have. Defaults to 1 */
  fractions: z.number().optional(),
});

export type BIQRatingSchema = z.infer<typeof BIQRatingZodSchema>;
```

## formComponents/number/slider

**Source:** `formComponents/number/slider.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a slider input */
export const BIQSliderZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `slider` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Slider),

  /** the default value for the input */
  default: z.number().optional(),

  /** the minimum value of the slider */
  minimum: z.number().optional(),
  /** the maximum value of the slider */
  maximum: z.number().optional(),
  /** the marks of the slider. If not set, the slider will not have marks */
  marks: z.array(z.object({
    value: z.number(),
    label: z.string().optional(),
  })).optional(),

  /** the step value of the slider. Defaults to 1 */
  step: z.number().optional(),
  /** if the slider should be restricted to the marks. Defaults to false */
  restrictToMarks: z.boolean().optional(),
});

export type BIQSliderSchema = z.infer<typeof BIQSliderZodSchema>;
```

## formComponents/string/buttonGroup

**Source:** `formComponents/string/buttonGroup.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema, BIQColorZodSchema, BIQButtonStyleZodSchema } from '../base.js';

/**
 * The format of the options for the button group
 *
 * 1. It can be an array of strings defining the values of the buttons
 * 2. It can be an array of objects to format the buttons
 *
 **/
const BIQButtonOptionZodSchema = z.string();
const BIQButtonOptionsObjectZodSchema = z.object({
  /** The the label to render on the button. If not set, the value will be used as the label */
  label: z.string().optional(),
  /** The value of the button. This is what will be submitted when the button is clicked */
  value: z.string(),
  /** The variant of the button. Defaults to `outline` */
  variant: BIQButtonStyleZodSchema.optional(),
  /** The color of the button. Defaults to the theme color */
  color: BIQColorZodSchema.optional(),
  /** The src of the icon to render on the button. If not set, no icon will be rendered */
  icon: z.string().optional(),
  /** If the option's button should be disabled. Defaults to false */
  disabled: z.boolean().optional(),
});
const BIQBaseButtonOptionsZodSchema = z.union([BIQButtonOptionZodSchema, BIQButtonOptionsObjectZodSchema]);

export type BIQButtonOptionSchema = z.infer<typeof BIQBaseButtonOptionsZodSchema>;

/** Allow for buttons to be grouped together */
const BIQGroupedButtonOptionsZodSchema = z.object({
  /** The label of the group */
  group: z.string(),
  /** The buttons to render in the group */
  items: BIQBaseButtonOptionsZodSchema.array(),
});

const BIQButtonOptionsSchema = z.union([BIQBaseButtonOptionsZodSchema, BIQGroupedButtonOptionsZodSchema]).array();

export const BIQButtonGroupZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `buttonGroup` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.ButtonGroup),

  /** the default value for the input */
  default: z.string().optional(),

  /** the options for the button group to render the set of buttons */
  options: BIQButtonOptionsSchema,

  /** the orientation of the button group. Defaults to `horizontal` */
  orientation: z.enum(['horizontal', 'vertical']).optional(),
});

export type BIQButtonGroupSchema = z.infer<typeof BIQButtonGroupZodSchema>;
```

## formComponents/string/code

**Source:** `formComponents/string/code.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a code input */
export const BIQCodeZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `code` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Code),

  /** The default value for the input */
  default: z.string().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** the language of the code input to apply code highlighting. If not set, no code highlighting will be applied */
  language: z.string().optional(),
  

  /** the regex pattern to validate the input against. If not set, the input will not be validated */
  regex: z.string().optional(),
  /** error message to display if the input does not match the regex pattern. Defaults to `Invalid input` */
  regexErrorMessage: z.string().optional(),
  /** the minimum length of the input. Defaults to 0 for optional inputs and 1 for required inputs */
  minLength: z.number().optional(),
  /** the maximum length of the string input. If not set, the input does not have a maximum length */
  maxLength: z.number().optional(),

  /** If wrap the lines of the code in the input component. If false, the code input will scroll horizontally. Defaults to true */
  wrapLines: z.boolean().optional(),
  /** the minimum number of lines the input component will render. If not set, the input does not have a minimum height */
  minLines: z.number().optional(),
  /** the maximum number of lines the input component will render. If not set, the input does not have a maximum height */
  maxLines: z.number().optional(),
  /** the set height of the input component. If not set, the input will auto-resize to fit the content */
  height: z.union([z.number(), z.string()]).optional(),
  /** if the input should auto-resize to fit content. Defaults to true */
  autoResize: z.boolean().optional(),
  
  /** if the input should render a copy button on the top right corner. Defaults to false */
  copyable: z.boolean().optional(),
});

export type BIQCodeSchema = z.infer<typeof BIQCodeZodSchema>;
```

## formComponents/string/codeDiff

**Source:** `formComponents/string/codeDiff.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a code diff (compare two code blocks) input */
export const BIQCodeDiffZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `codeDiff` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.CodeDiff),

  /** The code block of the old value of the diff (this code will not be editable in the component) */
  oldValue: z.string(),
  /** The code block of the new value of the diff and the default value of the form component. This code will be editable in the component and can be reverted to the old value */
  default: z.string(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** the language of the code input to apply code highlighting. If not set, no code highlighting will be applied */
  language: z.string().optional(),

  /** the title to display above the old code block */
  oldCodeTitle: z.string().optional(),
  /** the title to display above the new code block */
  newCodeTitle: z.string().optional(),
  
  /** the regex pattern to validate the input against. If not set, the input will not be validated */
  regex: z.string().optional(),
  /** error message to display if the input does not match the regex pattern. Defaults to `Invalid input` */
  regexErrorMessage: z.string().optional(),
  /** the minimum length of the input. Defaults to 0 for optional inputs and 1 for required inputs */
  minLength: z.number().optional(),
  /** the maximum length of the string input. If not set, the input does not have a maximum length */
  maxLength: z.number().optional(),

  /** If wrap the lines of the code in the input component. If false, the code input will scroll horizontally. Defaults to true */
  wrapLines: z.boolean().optional(),
  /** the minimum number of lines the input component will render. If not set, the input does not have a minimum height */
  minLines: z.number().optional(),
  /** the maximum number of lines the input component will render. If not set, the input does not have a maximum height */
  maxLines: z.number().optional(),
  /** the set height of the input for input. If not set, the input will auto-resize to fit the content */
  height: z.union([z.number(), z.string()]).optional(),
  /** the width of the input. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** if the input should auto-resize to fit content. Defaults to true */
  autoResize: z.boolean().optional(),

  /** If the old code and new code should be rendered inline (in the same code area) or side by side. Defaults to false (side by side) */
  inline: z.boolean().optional(),
  /** whether to render the revert controls (only would render if readOnly is undefined or false) to revert the updated section of the new code back to the old code. Defaults to true */
  revertControls: z.boolean().optional(),
});

export type BIQCodeDiffSchema = z.infer<typeof BIQCodeDiffZodSchema>;
```

## formComponents/string/markdown

**Source:** `formComponents/string/markdown.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a markdown input */
export const BIQMarkdownInputZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `markdownInput` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.MarkdownInput),

  /** The default value of the markdown input */
  default: z.string(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** the regex pattern to validate the input against. If not set, the input will not be validated */
  regex: z.string().optional(),
  /** error message to display if the input does not match the regex pattern. Defaults to `Invalid input` */
  regexErrorMessage: z.string().optional(),
  /** the minimum length of the input. Defaults to 0 for optional inputs and 1 for required inputs */
  minLength: z.number().optional(),
  /** the maximum length of the string input. If not set, the input does not have a maximum length */
  maxLength: z.number().optional(),

  /** If the lines of the markdown should be wrapped in the input component. If false, the markdown input will scroll horizontally. Defaults to true */
  wrapLines: z.boolean().optional(),
  /** the minimum number of lines the input component will render. If not set, the input does not have a minimum height */
  minLines: z.number().optional(),
  /** the maximum number of lines the input component will render. If not set, the input does not have a maximum height */
  maxLines: z.number().optional(),
  /** the set height of the input for input. If not set, the input will auto-resize to fit the content */
  height: z.union([z.number(), z.string()]).optional(),
  /** the width of the input. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** if the input should auto-resize to fit content. Defaults to true */
  autoResize: z.boolean().optional(),

  /** whether to show a preview of the markdown side by side with the raw markdown input. Defaults to true */
  preview: z.boolean().optional(),
  
  /** if the input should render a copy button on the top right corner. Defaults to false */
  copyable: z.boolean().optional(),
});

export type BIQMarkdownInputSchema = z.infer<typeof BIQMarkdownInputZodSchema>;
```

## formComponents/string/password

**Source:** `formComponents/string/password.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a password input */
export const BIQPasswordZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `password` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Password),

  /** the default value for the input */
  default: z.string().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** the regex pattern to validate the input against. If not set, the input will not be validated */
  regex: z.string().optional(),
  /** error message to display if the input does not match the regex pattern. Defaults to `Invalid input` */
  regexErrorMessage: z.string().optional(),
  /** the minimum length of the input. Defaults to 0 for optional inputs and 1 for required inputs */
  minLength: z.number().optional(),
  /** the maximum length of the string input. If not set, the input does not have a maximum length */
  maxLength: z.number().optional(),
  
  /** if the input should allow unmasking the password (show the password in plain text). Defaults to true */
  allowUnmasking: z.boolean().optional(),
});

export type BIQPasswordSchema = z.infer<typeof BIQPasswordZodSchema>;
```

## formComponents/string/phoneNumber

**Source:** `formComponents/string/phoneNumber.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a phone number input */
export const BIQPhoneNumberZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `phoneNumber` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.PhoneNumber),

  /** the default value for the input */
  default: z.string().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /**
   * Format and validation
   * E.164: The full international phone number eg `+1234567890`
   * national: The phone number without the country code eg `(234) 567-890`
   * international: The phone number without the national prefix eg `+1 234 567 890`
   * defaults to `E.164`
   **/
  format: z.enum(['E.164', 'national', 'international']).optional(),

  /** The default country in ISO 3166 two-letter region code only valid for E.164 or international format, eg `US` for USA. Defaults to the user's locale. */
  defaultCountry: z.string().optional(),
  /**
   * If true, the country code will be fixed and not allow the user to update it. This is only valid for E.164 or international format.
   * This requires a defaultCountry to be set.
   * Defaults to true.
   **/
  fixedCountryCode: z.boolean().optional(),
});

export type BIQPhoneNumberSchema = z.infer<typeof BIQPhoneNumberZodSchema>;
```

## formComponents/string/pin

**Source:** `formComponents/string/pin.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a pin input */
export const BIQPinZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `pin` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Pin),

  /** the default value for the input */
  default: z.string().optional(),

  /** the regex pattern to validate the input against. If not set, the input will not be validated */
  regex: z.string().optional(),
  /** error message to display if the input does not match the regex pattern. Defaults to `Invalid input` */
  regexErrorMessage: z.string().optional(),

  /** the allowed characters of the pin input, if regex is used then this will be ignored. If not set and regex is not used, defaults to `alphanumeric` */
  valueType: z.enum(['number', 'alphanumeric']).optional(),
  /** if its a OTP input, this will update the keyboard modes to allow using the last SMS with a code to be used as the pin. Defaults to false */
  isOTP: z.boolean().optional(),
  /** the length of the pin input. Defaults to 4 */
  length: z.number().optional(),

  /** if the pin input should be masked. Defaults to true */
  masked: z.boolean().optional(),
  /** the keyboard mode of input for the pin input. Defaults to to `numeric` if valueType is `number` or `text` if valueType is not set. */
  inputMode: z.enum(['search', 'text', 'none', 'tel', 'url', 'email', 'numeric', 'decimal']).optional(),

  /** if the form should be submitted when the pin input is completed. Defaults to false */
  submitOnComplete: z.boolean().optional(),
});

export type BIQPinSchema = z.infer<typeof BIQPinZodSchema>;
```

## formComponents/string/radio

**Source:** `formComponents/string/radio.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQOptionsZodSchema, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a radio input */
export const BIQRadioZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `radio` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Radio),

  /** the default value for the input */
  default: z.string().optional(),
  /** the options to render the radio buttons with */
  options: BIQOptionsZodSchema,

  /** the orientation of the radio input. Defaults to `horizontal` */
  orientation: z.enum(['horizontal', 'vertical']).optional(),
});

export type BIQRadioSchema = z.infer<typeof BIQRadioZodSchema>;
```

## formComponents/string/select

**Source:** `formComponents/string/select.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQOptionsZodSchema, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a select input */
export const BIQSelectZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `select` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Select),

  /** the default value for the input */
  default: z.string().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),
  /** the options to render the dropdown options with */
  options: BIQOptionsZodSchema,

  /** if the input is searchable. Defaults to false */
  searchable: z.boolean().optional(),
  /** the message to display when no options are found. Defaults to `No options found` */
  nothingFoundMessage: z.string().optional(),
});

export type BIQSelectSchema = z.infer<typeof BIQSelectZodSchema>;
```

## formComponents/string/suggest

**Source:** `formComponents/string/suggest.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a suggest input (autocomplete) */
export const BIQSuggestZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `suggest` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Suggest),

  /** the default value for the input */
  default: z.string().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),
  /** the options to render the dropdown options with. Since suggestions cannot have a 'label' */
  options: z.union([
    z.array(z.string()),
    z.array(z.object({
      group: z.string(),
      items: z.array(z.string())
    }))
  ]),


  /** the regex pattern to validate the input against. If not set, the input will not be validated */
  regex: z.string().optional(),
  /** error message to display if the input does not match the regex pattern. Defaults to `Invalid input` */
  regexErrorMessage: z.string().optional(),
  /** the minimum length of the input. Defaults to 0 for optional inputs and 1 for required inputs */
  minLength: z.number().optional(),
  /** the maximum length of the string input. If not set, the input does not have a maximum length */
  maxLength: z.number().optional(),
});

export type BIQSuggestSchema = z.infer<typeof BIQSuggestZodSchema>;
```

## formComponents/string/text

**Source:** `formComponents/string/text.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a text input */
export const BIQTextZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `text` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.Text),

  /** the default value for the input */
  default: z.string().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),
  /** to specify a variant of the input that will add an icon to the input and complete validation. This will override the regex validation. When not specified, a generic input is rendered */
  variant: z.enum(['email', 'uri']).optional(),


  /** the regex pattern to validate the input against. If not set, the input will not be validated */
  regex: z.string().optional(),
  /** the regex error message to display if the input does not match the regex pattern. Defaults to `Invalid input` */
  regexErrorMessage: z.string().optional(),
  /** the minimum length of the input. Defaults to 0 for optional inputs and 1 for required inputs */
  minLength: z.number().optional(),
  /** the maximum length of the input. If not set, the input does not have a maximum length */
  maxLength: z.number().optional(),

  /** if the input should render a copy button on the top right corner. Defaults to false */
  copyable: z.boolean().optional(),
});

export type BIQTextSchema = z.infer<typeof BIQTextZodSchema>;
```

## formComponents/string/textArea

**Source:** `formComponents/string/textArea.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The schema for a text area input */
export const BIQTextAreaZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `textArea` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.TextArea),

  /** the default value for the input */
  default: z.string().optional(),
  /** The placeholder text to display in the input component when it is empty */
  placeholder: z.any().optional(),

  /** the regex pattern to validate the input against. If not set, the input will not be validated */
  regex: z.string().optional(),
  /** the regex error message to display if the input does not match the regex pattern. Defaults to `Invalid input` */
  regexErrorMessage: z.string().optional(),
  /** the minimum length of the input. Defaults to 0 for optional inputs and 1 for required inputs */
  minLength: z.number().optional(),
  /** the maximum length of the input. If not set, the input does not have a maximum length */
  maxLength: z.number().optional(),

  /** the minimum lines of the textarea. If not set, the textarea does not have a minimum height */
  minLines: z.number().optional(),
  /** the maximum lines of the textarea. If not set, the textarea does not have a maximum height */
  maxLines: z.number().optional(),
  /** the set height of the input component. If not set, the input will auto-resize to fit the content */
  height: z.union([z.number(), z.string()]).optional(),
  /** the width of the input component. Defaults to 100% */
  width: z.union([z.number(), z.string()]).optional(),
  /** if the input component should auto-resize to fit content. Defaults to true */
  autoResize: z.boolean().optional(),
  
  /** if the input should render a copy button on the top right corner. Defaults to false */
  copyable: z.boolean().optional(),
});

export type BIQTextAreaSchema = z.infer<typeof BIQTextAreaZodSchema>;
```
