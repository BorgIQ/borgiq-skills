# formComponents/array/table

Generated from the platform's runtime types. Do not edit.

The schema for a table input and its column types.

See also: [formComponents/base](../base.md).

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
