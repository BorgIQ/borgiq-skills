# Interface Pages Reference

This reference documents the `page` configuration used by both InterfaceTriggerActor and InterfaceActor to render web forms and interfaces.

## Table of Contents

- [Page Structure](#page-structure)
- [Page Options](#page-options)
- [Design Guidelines](#design-guidelines)
- [Component Properties](#component-properties)
- [Component Types](#component-types)
  - [Input Components](#input-components)
  - [Numeric Components](#numeric-components)
  - [Selection Components](#selection-components)
  - [Boolean Components](#boolean-components)
  - [Date/Time Components](#datetime-components)
  - [File Components](#file-components)
  - [Layout Components](#layout-components)
  - [Display Components](#display-components)
  - [Action Components](#action-components)
  - [Advanced Components](#advanced-components)
- [Dynamic Default Values](#dynamic-default-values)
- [Read-Only Fields](#read-only-fields)
- [onSubmit Configuration](#onsubmit-configuration)
- [Examples](#examples)
- [Frontend Design Guidelines for webViewer](#frontend-design-guidelines-for-webviewer)
  - [Design Philosophy](#design-philosophy)
  - [Typography Excellence](#typography-excellence)
  - [Color Systems](#color-systems)
  - [Motion & Animation](#motion--animation)
  - [Spatial Composition & Layout](#spatial-composition--layout)
  - [Backgrounds & Visual Texture](#backgrounds--visual-texture)
  - [Complete webViewer Design Example](#complete-webviewer-design-example)
  - [Design Anti-Patterns to Avoid](#design-anti-patterns-to-avoid)
  - [Design Checklist](#design-checklist)
- [Theming Support](#theming-support)
  - [Available Themes](#available-themes)
  - [Using Themes](#using-themes)
  - [Theme Application Examples](#theme-application-examples)
  - [Creating Custom Themes](#creating-custom-themes)

## Page Structure

```yaml
configuration:
  options:
    page:
      pageTitle: My Form Title
      formWidth: half
      themeColor: blue
      children:
        - key: header
          type: header
          value: Form Header
        - key: fieldName
          type: text
          label: Field Label
          placeholder: Enter value...
          required: true
        - key: submit
          type: formButton
          value: Submit
```

## Page Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `children` | array | Yes | Array of UI components to render |
| `pageTitle` | string | No | Browser tab title |
| `formWidth` | string | No | Form width: `full`, `half`, `third` |
| `themeColor` | string | No | Theme color for the form |
| `backgroundColor` | string | No | Background color for the page |

## Design Guidelines

When creating interface pages, aim for distinctive, production-grade designs that avoid generic aesthetics.

### Design Thinking Process

Before configuring components, consider:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Choose a clear aesthetic direction - minimalist, editorial, playful, industrial, refined, etc.
- **Differentiation**: What makes this interface memorable and context-appropriate?

### Typography Best Practices

- Choose fonts that match the interface's purpose and tone
- Avoid defaulting to generic system fonts without intention
- Use header hierarchy (`order` property) to create visual rhythm
- Pair distinctive display headers with readable body text

### Color & Theme Guidelines

- Use `themeColor` and `backgroundColor` to establish atmosphere
- Commit to a cohesive color palette across components
- Use component `color` properties for accent and emphasis
- Dominant colors with sharp accents outperform evenly-distributed palettes
- Consider light vs dark themes based on context and use case

### Spatial Composition

- Use `formWidth` intentionally: `full` for data-dense layouts, `half` for focused forms, `third` for simple inputs
- Group related fields with `section` and `collapse` components
- Use `divider` components with custom styling to create visual rhythm
- Balance density with generous spacing using layout components

### Visual Details

- Apply custom styling to headers, dividers, and buttons for personality
- Use `markdown` components for rich instructional content
- For full creative control, use `webViewer` with custom HTML/CSS (see [Web Viewer](#web-viewer) section)

## Component Properties

Each child element in `page.children` represents a UI component:

| Property | Type | Description |
|----------|------|-------------|
| `key` | string | **Required.** Unique identifier for the component. Used to access the value in form submission. |
| `type` | string | **Required.** Component type (see Component Types below) |
| `label` | string | Display label for form inputs |
| `description` | string | Help text displayed below the field |
| `placeholder` | string | Placeholder text for inputs |
| `required` | boolean | Whether field is required for submission |
| `readOnly` | boolean | Display value without allowing edits |
| `defaultValue` | any | Default/initial value (supports BorgIQ expressions) |
| `value` | any | Static value (for display components like header) |
| `options` | array | Options for select, radio, buttonGroup components |

## Component Types

### Input Components

#### Text Input (`text`)

Single-line text input field.

```yaml
- key: name
  type: text
  label: Your Name
  placeholder: Enter your full name
  required: true
```

#### Text Area (`textarea`)

Multi-line text input field.

```yaml
- key: message
  type: textarea
  label: Message
  placeholder: Enter your message...
  required: true
```

#### Password (`password`)

Password input with masked characters.

```yaml
- key: password
  type: password
  label: Password
  placeholder: Enter your password
  required: true
```

#### PIN (`pin`)

PIN code input with individual digit boxes.

```yaml
- key: verificationCode
  type: pin
  label: Verification Code
  required: true
```

#### Code (`code`)

Code editor with syntax highlighting.

```yaml
- key: snippet
  type: code
  label: Code Snippet
  placeholder: Enter your code...
```

#### Markdown Input (`markdownInput`)

Markdown editor with preview.

```yaml
- key: notes
  type: markdownInput
  label: Notes
  placeholder: Write your notes in markdown...
```

### Numeric Components

#### Number (`number`)

Numeric input field.

```yaml
- key: quantity
  type: number
  label: Quantity
  defaultValue: 1
```

#### Currency (`currency`)

Currency input with formatting.

```yaml
- key: amount
  type: currency
  label: Amount
  defaultValue: 0
```

#### Phone Number (`phoneNumber`)

Phone number input with formatting.

```yaml
- key: phone
  type: phoneNumber
  label: Phone Number
  placeholder: (555) 123-4567
```

#### Percentage (`percentage`)

Percentage input.

```yaml
- key: discount
  type: percentage
  label: Discount
  defaultValue: 0
```

#### Rating (`rating`)

Star rating input.

```yaml
- key: rating
  type: rating
  label: Your Rating
```

#### Slider (`slider`)

Numeric slider input.

```yaml
- key: volume
  type: slider
  label: Volume
  defaultValue: 50
```

### Selection Components

#### Select (`select`)

Dropdown selection.

```yaml
- key: category
  type: select
  label: Category
  options:
    - label: Support
      value: support
    - label: Sales
      value: sales
    - label: Other
      value: other
```

#### Suggest (`suggest`)

Autocomplete/typeahead selection.

```yaml
- key: city
  type: suggest
  label: City
  options:
    - label: New York
      value: nyc
    - label: Los Angeles
      value: la
    - label: Chicago
      value: chi
```

#### Radio (`radio`)

Radio button group.

```yaml
- key: priority
  type: radio
  label: Priority
  options:
    - label: Low
      value: low
    - label: Medium
      value: medium
    - label: High
      value: high
  defaultValue: medium
```

#### Button Group (`buttonGroup`)

Button group selection.

```yaml
- key: action
  type: buttonGroup
  label: Action
  options:
    - label: Approve
      value: approve
    - label: Reject
      value: reject
    - label: Defer
      value: defer
```

#### Multi-Select (`multiSelect`)

Multiple selection dropdown.

```yaml
- key: tags
  type: multiSelect
  label: Tags
  options:
    - label: Urgent
      value: urgent
    - label: Important
      value: important
    - label: Review
      value: review
```

#### Multi-Checkbox (`multiCheckbox`)

Multiple checkbox selection.

```yaml
- key: features
  type: multiCheckbox
  label: Features
  options:
    - label: Email Notifications
      value: email
    - label: SMS Notifications
      value: sms
    - label: Push Notifications
      value: push
```

### Boolean Components

#### Checkbox (`checkbox`)

Boolean checkbox.

```yaml
- key: subscribe
  type: checkbox
  label: Subscribe to newsletter
  defaultValue: false
```

#### Switch (`switch`)

Toggle switch.

```yaml
- key: enabled
  type: switch
  label: Enable notifications
  defaultValue: true
```

### Date/Time Components

Date/time components share common properties:

| Property | Type | Description |
|----------|------|-------------|
| `default` | string/object | Default value in ISO format (e.g., `'2000-01-01T00:00:00.000Z'`) |
| `highlightToday` | boolean | Highlight today's date in the picker |
| `hideWeekdays` | boolean | Hide weekday headers in calendar view |
| `allowDeselect` | boolean | Allow clearing the selected date |
| `firstDayOfTheWeek` | number | First day of week (0=Sunday, 1=Monday, etc.) |

#### Date (`date`)

Date picker.

```yaml
- key: birthDate
  type: date
  label: Birth Date
  required: false
  default: '2000-01-01T00:00:00.000Z'
  highlightToday: true
  hideWeekdays: false
  allowDeselect: false
```

#### Date Time (`dateTime`)

Date and time picker.

```yaml
- key: departTime
  type: dateTime
  label: Departure Time
  required: false
  default: '2000-01-01T00:00:00.000Z'
  highlightToday: true
  hideWeekdays: false
  allowDeselect: false
  withSeconds: true
```

#### Time (`time`)

Time picker.

```yaml
- key: theTime
  type: time
  label: Landing Time
  required: false
  withSeconds: true
```

#### Calendar (`calendar`)

Calendar date picker with inline calendar display.

```yaml
- key: theCalendar
  type: calendar
  label: Departure Date
  required: false
  default: '2000-01-01T00:00:00.000Z'
  highlightToday: true
  hideWeekdays: false
  allowDeselect: false
  firstDayOfTheWeek: 0
  readOnly: true
```

#### Date Range (`dateRange`)

Date range picker for selecting start and end dates.

```yaml
- key: theDateRange
  type: dateRange
  label: Select Date Range
  default:
    startDate: '2000-01-01T00:00:00.000Z'
    endDate: '2000-02-01T00:00:00.000Z'
  highlightToday: true
  hideWeekdays: false
  firstDayOfTheWeek: 0
```

#### Calendar Range (`calendarRange`)

Calendar-style date range picker with inline calendar display.

```yaml
- key: theCalendarRange
  type: calendarRange
  label: Select Calendar Range
  default:
    startDate: '2000-01-01T00:00:00.000Z'
    endDate: '2000-02-01T00:00:00.000Z'
  highlightToday: true
  hideWeekdays: false
  firstDayOfTheWeek: 0
```

### File Components

#### File Input (`fileInput`)

File upload input.

```yaml
- key: attachment
  type: fileInput
  label: Attachment
```

#### File Button (`fileButton`)

Button-style file upload.

```yaml
- key: document
  type: fileButton
  label: Upload Document
```

#### Audio Recording (`audioRecordingInput`)

Audio recording input.

```yaml
- key: voiceNote
  type: audioRecordingInput
  label: Voice Note
```

#### File Dropzone (`fileDropzone`)

Drag-and-drop file upload area.

```yaml
- key: files
  type: fileDropzone
  label: Drop files here
```

### Layout Components

#### Header (`header`)

Header/title text.

```yaml
- key: pageTitle
  type: header
  value: Contact Form
```

With variables:

```yaml
- key: pageTitle
  type: header
  variables:
    title: Contact Form
    order: 1
```

#### Divider (`divider`)

Visual separator line.

```yaml
- key: separator
  type: divider
```

#### Section (`section`)

Group of related fields. Use `extendParentObject: true` to flatten children into parent object.

```yaml
- key: contactInfo
  type: section
  label: Contact Information
  extendParentObject: true
  children:
    - key: email
      type: text
      label: Email
    - key: phone
      type: phoneNumber
      label: Phone
```

#### Collapse (`collapse`)

Collapsible section.

```yaml
- key: advancedOptions
  type: collapse
  label: Advanced Options
  children:
    - key: debug
      type: switch
      label: Enable Debug Mode
```

### Display Components

#### Markdown (`markdown`)

Render markdown content.

```yaml
- key: instructions
  type: markdown
  value: |
    ## Instructions
    Please fill out the form below.
    - All fields marked with * are required
    - Your information is kept confidential
```

#### Code Viewer (`codeViewer`)

Display code with syntax highlighting (read-only).

```yaml
- key: codePreview
  type: codeViewer
  value: |
    function hello() {
      console.log("Hello, World!");
    }
```

#### Image (`image`)

Display an image.

```yaml
- key: logo
  type: image
  value: https://example.com/logo.png
```

#### PDF Viewer (`pdfViewer`)

Display a PDF document.

```yaml
- key: document
  type: pdfViewer
  value: ${{ msg.document.url }}
```

#### Web Viewer (`webViewer`)

Embed a web page or custom HTML content in an iframe.

**Basic URL Example:**
```yaml
- key: preview
  type: webViewer
  src: https://example.com/preview
```

**Custom HTML Example:**
```yaml
- key: app
  type: webViewer
  fullScreen: true
  html: |
    <!DOCTYPE html>
    <html>
    <head><title>My App</title></head>
    <body>
      <h1>Hello World</h1>
      <script>console.log('App loaded');</script>
    </body>
    </html>
```

**With External Resources (CSP Domains):**
```yaml
- key: web
  type: webViewer
  fullScreen: true
  allowedStyleDomains:
    - https://fonts.googleapis.com
    - https://fonts.gstatic.com
    - https://cdn.jsdelivr.net
  allowedScriptDomains:
    - https://cdn.jsdelivr.net
    - https://unpkg.com
  html: |
    <!DOCTYPE html>
    <html>
    <head>
      <link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" rel="stylesheet">
      <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>...</body>
    </html>
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `src` | string | One of src/html | URL to embed (mutually exclusive with `html`) |
| `html` | string | One of src/html | Custom HTML content (mutually exclusive with `src`) |
| `width` | number/string | No | Width of viewer (default: `100%`) |
| `height` | number/string | No | Height of viewer (default: `500px`) |
| `fullScreen` | boolean | No | Full-screen mode, hides other components |
| `allowedScriptDomains` | array | No | Allowed domains for external scripts (CSP script-src) |
| `allowedStyleDomains` | array | No | Allowed domains for external stylesheets (CSP style-src) |

**Important Notes:**
- You must provide either `src` OR `html`, but not both
- External scripts and stylesheets are blocked by default (Content Security Policy)
- Use `allowedScriptDomains` and `allowedStyleDomains` to whitelist external resources
- Domain URLs must be fully qualified (e.g., `https://cdn.example.com`)

#### File Download (`fileDownload`)

File download link.

```yaml
- key: report
  type: fileDownload
  value: ${{ msg.report.downloadUrl }}
  label: Download Report
```

#### Progress (`progress`)

Progress bar.

```yaml
- key: completion
  type: progress
  value: 75
  label: Completion
```

### Action Components

#### Form Button (`formButton`)

Submit button for the form.

```yaml
- key: submit
  type: formButton
  value: Submit Form
```

#### URL Button (`urlButton`)

Button that links to a URL.

```yaml
- key: learnMore
  type: urlButton
  value: Learn More
  url: https://example.com/docs
```

### Advanced Components

#### Union (`union`)

Conditional fields based on selection.

```yaml
- key: contactMethod
  type: union
  label: Contact Method
  children:
    - key: email
      type: text
      label: Email Address
    - key: phone
      type: phoneNumber
      label: Phone Number
```

#### Conditional (`conditional`)

Show/hide fields based on conditions.

```yaml
- key: conditionalField
  type: conditional
  condition: ${{ inputs.showAdvanced === true }}
  children:
    - key: advancedSetting
      type: text
      label: Advanced Setting
```

#### Array Parent (`arrayParent`)

Repeatable field group.

```yaml
- key: items
  type: arrayParent
  label: Items
  children:
    - key: name
      type: text
      label: Item Name
    - key: quantity
      type: number
      label: Quantity
```

#### Table (`table`)

Editable table.

```yaml
- key: lineItems
  type: table
  label: Line Items
  columns:
    - key: product
      label: Product
      type: text
    - key: qty
      label: Qty
      type: number
    - key: price
      label: Price
      type: currency
```

## Dynamic Default Values

Use BorgIQ expressions to populate form fields with data from upstream actors:

```yaml
- key: customerName
  type: text
  label: Customer Name
  readOnly: true
  defaultValue: ${{ msg.fetch_customer.body.name }}
```

```yaml
- key: orderTotal
  type: number
  label: Order Total
  readOnly: true
  defaultValue: ${{ msg.calculate_total.total }}
```

```yaml
- key: lastUpdated
  type: dateTime
  label: Last Updated
  readOnly: true
  defaultValue: ${{ msg.data?.lastUpdated || new Date().toISOString() }}
```

## Read-Only Fields

Set `readOnly: true` to display data without allowing edits. Useful for review interfaces.

```yaml
- key: orderId
  type: text
  label: Order ID
  readOnly: true
  defaultValue: ${{ msg.order.id }}
```

## onSubmit Configuration

Configure what happens after form submission:

### Success Message

Display a message after submission.

```yaml
onSubmit:
  type: successMessage
  successMessage: Thank you for your submission!
```

### URL Redirect

Redirect to an external URL.

```yaml
onSubmit:
  type: urlRedirect
  url: https://example.com/thank-you
```

### Next Interface

Redirect to the next interface in the workflow.

```yaml
onSubmit:
  type: nextInterface
  loadingMessage: Processing your request...
```

## Examples

<!-- TODO: Add more comprehensive examples here -->

### Simple Contact Form

```yaml
page:
  pageTitle: Contact Us
  formWidth: half
  children:
    - key: header
      type: header
      value: Get in Touch
    - key: name
      type: text
      label: Name
      placeholder: Your full name
      required: true
    - key: email
      type: text
      label: Email
      placeholder: your@email.com
      required: true
    - key: message
      type: textarea
      label: Message
      placeholder: How can we help?
      required: true
    - key: submit
      type: formButton
      value: Send Message
```

### Approval Form with Read-Only Data

```yaml
page:
  pageTitle: Approval Required
  children:
    - key: header
      type: header
      value: Request Approval
    - key: requestDetails
      type: section
      label: Request Details
      extendParentObject: true
      children:
        - key: requestId
          type: text
          label: Request ID
          readOnly: true
          defaultValue: ${{ msg.request.id }}
        - key: requestedBy
          type: text
          label: Requested By
          readOnly: true
          defaultValue: ${{ msg.request.submittedBy }}
        - key: amount
          type: currency
          label: Amount
          readOnly: true
          defaultValue: ${{ msg.request.amount }}
    - key: divider
      type: divider
    - key: decision
      type: buttonGroup
      label: Decision
      required: true
      options:
        - label: Approve
          value: approved
        - label: Reject
          value: rejected
    - key: comments
      type: textarea
      label: Comments
      placeholder: Add any comments...
    - key: submit
      type: formButton
      value: Submit Decision
```

### Multi-Step Form Section

```yaml
page:
  pageTitle: Registration - Step 1
  children:
    - key: header
      type: header
      value: Personal Information
    - key: progress
      type: progress
      value: 33
      label: Step 1 of 3
    - key: personalInfo
      type: section
      label: Personal Details
      extendParentObject: true
      children:
        - key: firstName
          type: text
          label: First Name
          required: true
        - key: lastName
          type: text
          label: Last Name
          required: true
        - key: email
          type: text
          label: Email
          required: true
        - key: phone
          type: phoneNumber
          label: Phone Number
    - key: submit
      type: formButton
      value: Continue to Step 2
```

### Date Input Showcase

```yaml
page:
  children:
    - type: header
      key: formHeader
      value: Date Input Showcase Form
    - type: date
      key: birthDate
      label: Birth Date (date)
      required: false
      default: '2000-01-01T00:00:00.000Z'
      highlightToday: true
      hideWeekdays: false
      allowDeselect: false
    - type: dateTime
      key: departTime
      label: Departure Time (dateTime)
      required: false
      default: '2000-01-01T00:00:00.000Z'
      highlightToday: true
      hideWeekdays: false
      allowDeselect: false
      withSeconds: true
    - type: time
      key: theTime
      label: Landing Time (time)
      required: false
      withSeconds: true
    - type: calendar
      key: theCalendar
      label: Departure Date (calendar)
      required: false
      default: '2000-01-01T00:00:00.000Z'
      highlightToday: true
      hideWeekdays: false
      allowDeselect: false
      firstDayOfTheWeek: 0
      readOnly: true
    - type: dateRange
      key: theDateRange
      label: Select Date Range (dateRange)
      default:
        startDate: '2000-01-01T00:00:00.000Z'
        endDate: '2000-02-01T00:00:00.000Z'
      highlightToday: true
      hideWeekdays: false
      firstDayOfTheWeek: 0
    - type: calendarRange
      key: theCalendarRange
      label: Select Calendar Range (calendarRange)
      default:
        startDate: '2000-01-01T00:00:00.000Z'
        endDate: '2000-02-01T00:00:00.000Z'
      highlightToday: true
      hideWeekdays: false
      firstDayOfTheWeek: 0
    - type: formButton
      key: submitButton
      text: Submit
      required: true
      actionType: submit
onSubmit:
  type: successMessage
```

### Display Components with Styles

```yaml
page:
  formWidth: full
  pageTitle: Sample BorgIQ Form Title
  themeColor: purple
  backgroundColor: gray
  children:
    - type: header
      key: formTitle
      value: Sample Form Title (header)
      order: 2
      color: blue
      subtitle: Welcome to BorgIQ Platform Form
      subtitleColor: red
      subtitleSize: xs
    - type: divider
      key: sectionDivider
      text: This is divider -- You can insert text HERE (divider)
      color: violet
      weight: 2
      textAlignment: center
    - type: formButton
      key: approveButton
      text: Approve (formButton)
      variant: filled
      color: green
      size: xl
      actionType: submit
    - type: urlButton
      key: learnMoreButton
      text: Open BorgIQ Home Page
      url: https://borgiq.ai
      openUrlInCurrentPage: false
      color: orange
      variant: outline
    - type: image
      key: sampleImage
      src: https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-8.png
      width: 200
      height: 80
      borderWidth: 4
      borderColor: cyan
      borderRadius: xl
    - type: markdown
      key: markdownContent
      value: |
        # Markdown Content
        This is a **markdown** content block with custom styling.
        - Item 1
        - Item 2
      width: 400
      backgroundColor: gray
    - type: codeViewer
      key: codePreview
      value: |
        function greet(name: string) {
          console.log(`Hello, ${name}!`);
        }
        greet("BorgIQ");
      language: typescript
      height: 150
    - type: pdfViewer
      key: documentViewer
      src: ${{ msg.document.url }}
      width: 100%
onSubmit:
  type: successMessage
```

#### Display Component Style Properties

| Component | Property | Type | Description |
|-----------|----------|------|-------------|
| `header` | `color` | string | Text color (e.g., `blue`, `red`, `green`) |
| `header` | `order` | number | Heading level (1-6) |
| `header` | `subtitle` | string | Subtitle text below the header |
| `header` | `subtitleColor` | string | Subtitle text color |
| `header` | `subtitleSize` | string | Subtitle size (`xs`, `sm`, `md`, `lg`, `xl`) |
| `divider` | `text` | string | Text to display in the divider |
| `divider` | `color` | string | Divider line color |
| `divider` | `weight` | number | Line thickness |
| `divider` | `textAlignment` | string | Text alignment (`left`, `center`, `right`) |
| `formButton` | `text` | string | Button text (alternative to `value`) |
| `formButton` | `variant` | string | Button style (`filled`, `outline`, `light`, `subtle`) |
| `formButton` | `color` | string | Button color |
| `formButton` | `size` | string | Button size (`xs`, `sm`, `md`, `lg`, `xl`) |
| `formButton` | `actionType` | string | Action type (`submit`) |
| `urlButton` | `text` | string | Button text |
| `urlButton` | `url` | string | Target URL |
| `urlButton` | `openUrlInCurrentPage` | boolean | Open in same tab if true |
| `urlButton` | `color` | string | Button color |
| `urlButton` | `variant` | string | Button style (`filled`, `outline`, `light`, `subtle`) |
| `image` | `src` | string | Image URL |
| `image` | `width` | number/string | Image width (pixels or percentage) |
| `image` | `height` | number/string | Image height (pixels or percentage) |
| `image` | `borderWidth` | number | Border thickness |
| `image` | `borderColor` | string | Border color |
| `image` | `borderRadius` | string | Corner rounding (`xs`, `sm`, `md`, `lg`, `xl`) |
| `markdown` | `width` | number/string | Container width |
| `markdown` | `backgroundColor` | string | Background color |
| `codeViewer` | `language` | string | Syntax highlighting language (e.g., `typescript`, `python`, `json`) |
| `codeViewer` | `height` | number/string | Viewer height |
| `pdfViewer` | `src` | string | PDF URL (supports expressions) |
| `pdfViewer` | `width` | string | Viewer width (e.g., `100%`, `500px`) |

### Input Components Showcase

```yaml
page:
  children:
    - type: header
      key: formHeader
      value: BorgIQ Interface Showcase Form
    - type: text
      key: userName
      label: Name (text)
      description: Enter your full name
      infoText: Enter your full name here
      placeholder: John Doe
      required: false
    - type: text
      key: email
      label: Email (text)
      description: Enter your email address here
      default: user@example.com
      placeholder: user@example.com
      required: false
      variant: email
      copyable: true
    - type: text
      key: linkedIn
      label: LinkedIn Profile URL (text)
      description: LinkedIn Profile URL
      default: https://www.linkedin.com/xxxx
      placeholder: https://www.linkedin.com/xxxx
      required: false
      variant: uri
      copyable: true
    - type: textarea
      key: userComments
      label: User comments (textarea)
      default: Please enter your comments here...
      placeholder: Please enter your comments here...
      required: false
      copyable: true
    - type: password
      label: Password (password)
      key: userPassword
      default: ''
      required: false
    - type: pin
      key: thePin
      label: Enter your pin sent to your email (pin)
      valueType: number
      isOTP: true
      length: 6
      masked: false
      inputMode: search
      submitOnComplete: false
    - type: formButton
      key: submitButton
      text: Submit
      required: true
      actionType: submit
onSubmit:
  type: successMessage
```

#### Text Input Variants

| Property | Type | Description |
|----------|------|-------------|
| `variant` | string | Input variant: `email`, `uri`, or default text |
| `copyable` | boolean | Show copy button for the field value |
| `infoText` | string | Tooltip text for additional help |

#### PIN Input Properties

| Property | Type | Description |
|----------|------|-------------|
| `valueType` | string | Type of PIN value: `number` or `string` |
| `isOTP` | boolean | Enable OTP mode for one-time passwords |
| `length` | number | Number of PIN digits |
| `masked` | boolean | Hide entered digits |
| `inputMode` | string | Keyboard input mode |
| `submitOnComplete` | boolean | Auto-submit when all digits entered |

### Select Components with Groups

```yaml
page:
  children:
    - type: select
      key: userRole
      default: User
      required: false
      label: User role (select)
      placeholder: Please select a role
      options:
        - Admin
        - User
        - Moderator
      searchable: true
      nothingFoundMessage: No roles found
    - type: select
      key: userRoleWithGroup
      default: User
      required: false
      label: User role (select) with group
      placeholder: Please select a role
      options:
        - group: A
          items:
            - Admin
            - User
            - Moderator
        - group: B
          items:
            - Fake User
            - Fake Admin
            - Fake Moderator
      searchable: true
      nothingFoundMessage: No roles found
    - type: suggest
      key: userRoleSuggest
      label: User role (suggest)
      placeholder: Please select a role
      options:
        - Admin
        - User
        - Moderator
    - type: suggest
      key: userRoleSuggestGroup
      label: User role (suggest) with group
      placeholder: Please select a role
      options:
        - group: A
          items:
            - Admin
            - User
            - Moderator
        - group: B
          items:
            - Fake User
            - Fake Admin
            - Fake Moderator
    - type: formButton
      key: submitButton
      text: Submit
      actionType: submit
onSubmit:
  type: successMessage
```

#### Select/Suggest Properties

| Property | Type | Description |
|----------|------|-------------|
| `searchable` | boolean | Enable search/filter in dropdown |
| `nothingFoundMessage` | string | Message when no options match search |
| `options` | array | Simple array or grouped options with `group` and `items` |

### Checkbox, Switch, and Radio Components

```yaml
page:
  children:
    - type: checkbox
      key: subscribeNewsletter
      label: Subscribe to Newsletter (checkbox)
      default: false
      required: false
      inlineLabel: true
      labelPosition: right
      color: red
    - type: switch
      key: enableNotifications
      label: Enable Notifications (switch)
      default: true
      required: false
      inlineLabel: true
      labelPosition: right
    - type: radio
      key: gender
      label: Gender (radio)
      default: male
      required: false
      options:
        - label: Male
          value: male
        - label: Female
          value: female
        - label: Other
          value: other
    - type: formButton
      key: submitButton
      text: Submit
      actionType: submit
onSubmit:
  type: successMessage
```

#### Checkbox/Switch Properties

| Property | Type | Description |
|----------|------|-------------|
| `inlineLabel` | boolean | Display label inline with the control |
| `labelPosition` | string | Position of label: `left` or `right` |
| `color` | string | Color of the checkbox/switch |

### Number and Rating Components

```yaml
page:
  children:
    - type: number
      key: age
      label: Age (number)
      default: 30
      required: false
      variant: integer
      hideControls: false
    - type: rating
      key: theRating
      label: Stars (rating)
      default: 2
      required: false
      maximum: 5
      fractions: 1
    - type: slider
      key: theSlider
      label: Volume (slider)
      default: 5
      minimum: 1
      maximum: 10
      step: 1
      restrictToMarks: true
      marks:
        - value: 1
          label: Low
        - value: 5
          label: Medium
        - value: 10
          label: High
    - type: formButton
      key: submitButton
      text: Submit
      actionType: submit
onSubmit:
  type: successMessage
```

#### Number Properties

| Property | Type | Description |
|----------|------|-------------|
| `variant` | string | Number variant: `integer` or default |
| `hideControls` | boolean | Hide increment/decrement controls |

#### Rating Properties

| Property | Type | Description |
|----------|------|-------------|
| `maximum` | number | Maximum rating value |
| `fractions` | number | Fractional rating steps (1 = whole stars only) |

#### Slider Properties

| Property | Type | Description |
|----------|------|-------------|
| `minimum` | number | Minimum slider value |
| `maximum` | number | Maximum slider value |
| `step` | number | Step increment |
| `restrictToMarks` | boolean | Only allow values at marks |
| `marks` | array | Array of `{value, label}` mark definitions |

### Button Group with Styled Options

```yaml
page:
  children:
    - type: buttonGroup
      key: theButtonGroup
      label: Button Group (buttonGroup)
      placeholder: Approve or Reject?
      orientation: horizontal
      options:
        - label: Approve
          value: approve
          style: filled
          color: green
        - label: Reject
          value: reject
          style: light
          color: red
    - type: formButton
      key: submitButton
      text: Submit
      actionType: submit
onSubmit:
  type: successMessage
```

#### Button Group Properties

| Property | Type | Description |
|----------|------|-------------|
| `orientation` | string | Layout: `horizontal` or `vertical` |
| `options[].style` | string | Button style: `filled`, `light`, `outline`, `subtle` |
| `options[].color` | string | Button color |

### Multi-Select Components

```yaml
page:
  children:
    - type: multiSelect
      key: labelsToApply
      default:
        - INBOX
      required: false
      label: Labels (multiSelect)
      placeholder: Please select labels to apply
      checkIconPosition: left
      options:
        - INBOX
        - DRAFT
        - SPAM
      searchable: true
      nothingFoundMessage: No labels found
    - type: multiCheckbox
      key: labelsCheckbox
      default:
        - INBOX
      required: false
      label: Labels (multiCheckbox)
      placeholder: Please select labels to apply
      selectAllOption: true
      selectAllOptionLabel: Apply All Labels
      orientation: horizontal
      options:
        - INBOX
        - DRAFT
        - SPAM
    - type: formButton
      key: submitButton
      text: Submit
      actionType: submit
onSubmit:
  type: successMessage
```

#### Multi-Select Properties

| Property | Type | Description |
|----------|------|-------------|
| `checkIconPosition` | string | Position of check icon: `left` or `right` |

#### Multi-Checkbox Properties

| Property | Type | Description |
|----------|------|-------------|
| `selectAllOption` | boolean | Show "Select All" option |
| `selectAllOptionLabel` | string | Label for the select all option |
| `orientation` | string | Layout: `horizontal` or `vertical` |

### Code Input Components

```yaml
page:
  children:
    - type: header
      key: formHeader
      value: BorgIQ Code Input
    - type: code
      key: theCode
      label: Code Input (code)
      placeholder: Insert your code here
      language: python
      default: |
        print("Hello World!")
      wrapLines: true
      minLines: 10
      maxLines: 50
      autoResize: true
      copyable: true
    - type: codeDiff
      key: theCodeDiff
      label: Code Diff (codeDiff)
      language: python
      newCodeTitle: The New File
      default: |
        def calculate(a, b):
            return a + b
      oldCodeTitle: The Old File
      oldValue: |
        def calculate(a, b, c):
            return a + b + c
      wrapLines: true
      inline: false
      revertControls: true
      minLines: 10
      maxLines: 50
      autoResize: true
      copyable: true
    - type: markdownInput
      key: theMarkdownInput
      label: Markdown Input (markdownInput)
      default: |
        # Welcome to BorgIQ

        ## What's BorgIQ
      wrapLines: true
      minLines: 10
      maxLines: 50
      autoResize: true
      copyable: true
      preview: true
    - type: formButton
      key: submitButton
      text: Submit
      actionType: submit
onSubmit:
  type: successMessage
```

#### Code Input Properties

| Property | Type | Description |
|----------|------|-------------|
| `language` | string | Syntax highlighting language |
| `wrapLines` | boolean | Wrap long lines |
| `minLines` | number | Minimum visible lines |
| `maxLines` | number | Maximum visible lines |
| `autoResize` | boolean | Auto-resize to fit content |
| `copyable` | boolean | Show copy button |

#### Code Diff Properties

| Property | Type | Description |
|----------|------|-------------|
| `oldValue` | string | Original code for comparison |
| `oldCodeTitle` | string | Title for original code panel |
| `newCodeTitle` | string | Title for new code panel |
| `inline` | boolean | Show inline diff vs side-by-side |
| `revertControls` | boolean | Show revert controls |

#### Markdown Input Properties

| Property | Type | Description |
|----------|------|-------------|
| `preview` | boolean | Show markdown preview |

### File Upload Components

```yaml
page:
  children:
    - type: header
      key: formHeader
      value: BorgIQ File and Audio Input
    - type: fileInput
      key: uploadFile
      label: Upload your Resume (fileInput)
      required: false
      placeholder: Click here to upload your file(s)
      multiple: false
      maxFileSize: 10000000
      accept: application/*
    - type: fileButton
      key: fileButtonImage
      label: Upload your Images (fileButton)
      buttonText: Click here to add image(s)
      buttonColor: blue
      buttonVariant: light
      required: false
      placeholder: Click here to upload your file(s)
      multiple: true
      maxFileSize: 10000000
      showUploadedFile: true
      accept: image/*,application/*
    - type: fileDropzone
      key: theFileDropzone
      label: Drag and drop your PDFs here (fileDropzone)
      dropzoneText: Drag and drop here to upload your file(s)
      dropzoneTextColor: yellow
      dropzoneDescription: You can upload PDFs, .MDs, Any Text Files
      dropzoneDescriptionColor: yellow
      multiple: true
      maxLength: 5
      maxFileSize: 10000000
      showUploadedFile: true
      accept: image/*,application/*,text/*
    - type: audioRecordingInput
      key: theAudioRecordingInput
      label: Record a welcome message (audioRecordingInput)
      maxDuration: 60
      mimeType: audio/mpeg
    - type: formButton
      key: submitButton
      text: Submit
      actionType: submit
onSubmit:
  type: successMessage
```

#### File Input Properties

| Property | Type | Description |
|----------|------|-------------|
| `multiple` | boolean | Allow multiple file selection |
| `maxFileSize` | number | Maximum file size in bytes |
| `accept` | string | Accepted MIME types (comma-separated) |

#### File Button Properties

| Property | Type | Description |
|----------|------|-------------|
| `buttonText` | string | Text displayed on the button |
| `buttonColor` | string | Button color |
| `buttonVariant` | string | Button style variant |
| `showUploadedFile` | boolean | Show uploaded file preview |

#### File Dropzone Properties

| Property | Type | Description |
|----------|------|-------------|
| `dropzoneText` | string | Main dropzone text |
| `dropzoneTextColor` | string | Color of dropzone text |
| `dropzoneDescription` | string | Description text below main text |
| `dropzoneDescriptionColor` | string | Color of description text |
| `maxLength` | number | Maximum number of files |

#### Audio Recording Properties

| Property | Type | Description |
|----------|------|-------------|
| `maxDuration` | number | Maximum recording duration in seconds |
| `mimeType` | string | Output audio format |

### Collapsible Section

```yaml
page:
  children:
    - type: collapse
      key: userInfoSection
      label: User Info
      infoText: You'll find User info in this section
      description: User info for the current user
      children:
        - type: header
          key: formHeader
          value: BorgIQ Interface Form
        - type: text
          key: userName
          label: Name (text)
          description: Enter your full name
          infoText: Enter your full name here
          placeholder: John Doe
          required: false
        - type: text
          key: email
          label: Email (text)
          description: Enter your email address here
          default: user@example.com
          placeholder: user@example.com
          required: false
          variant: email
          copyable: true
        - type: formButton
          key: submitButton
          text: Submit
          actionType: submit
onSubmit:
  type: successMessage
```

### Conditional Fields

```yaml
page:
  children:
    - key: ui
      type: section
      required: true
      children:
        - key: componentUi
          extendParentObject: true
          type: conditional
          required: true
          conditionalField:
            key: component
            type: select
            label: Component type
            description: The component type to use for the input
            default: input
            options:
              - value: input
                label: Input
              - value: textarea
                label: Textarea
              - value: password
                label: Password
          children:
            input:
              - key: options
                type: section
                label: Options
                children:
                  - key: placeholder
                    type: text
                    label: Placeholder
                    description: The placeholder text for the input
            password:
              - key: options
                type: section
                label: Options
                children:
                  - key: placeholder
                    type: text
                    label: Placeholder
            textarea:
              - key: options
                type: section
                label: Options
                children:
                  - key: placeholder
                    type: text
                    label: Placeholder
                  - key: minLines
                    type: number
                    label: Minimum Lines
                    minimum: 1
                  - key: maxLines
                    type: number
                    label: Maximum Lines
                    minimum: 1
                  - key: autoResize
                    type: checkbox
                    label: Auto Resize
                    default: true
    - type: formButton
      key: submitButton
      text: Submit
      actionType: submit
onSubmit:
  type: successMessage
```

#### Conditional Properties

| Property | Type | Description |
|----------|------|-------------|
| `conditionalField` | object | The select field that controls which children to show |
| `conditionalField.key` | string | Key for the conditional selector |
| `conditionalField.type` | string | Usually `select` |
| `conditionalField.options` | array | Options with `value` and `label` |
| `children` | object | Map of option values to arrays of child components |
| `extendParentObject` | boolean | Flatten children into parent object |

### Array Parent (Repeatable Fields)

```yaml
page:
  formWidth: full
  pageTitle: Create PostgreSQL Table
  children:
    - type: header
      key: formHeader
      value: Create PostgreSQL Table
    - type: arrayParent
      key: columns
      label: Columns
      item:
        key: Column
        type: section
        children:
          - key: columnName
            label: Column Name
            description: The column header for the table
            type: text
            default: Default Header
            required: true
          - key: dataType
            label: Data Type
            description: The data type for the column
            type: select
            options:
              - INTEGER
              - VARCHAR
              - BOOLEAN
              - DATE
              - TIMESTAMP
              - JSONB
            required: true
          - key: isRequired
            label: Is Required?
            description: Whether the column is required (not nullable)
            type: checkbox
            default: false
            inlineLabel: true
          - key: isPrimary
            label: Is The Primary Key?
            description: Whether the column is the primary key
            type: checkbox
            default: false
            inlineLabel: true
          - key: defaultValue
            label: Default Value
            description: Specify a default value for the column
            type: text
            default: ''
      allowReorder: false
      addButtonText: Add a Column
    - type: formButton
      key: submitButton
      text: Submit
      actionType: submit
onSubmit:
  type: successMessage
```

#### Array Parent Properties

| Property | Type | Description |
|----------|------|-------------|
| `item` | object | Template for each array item (section with children) |
| `allowReorder` | boolean | Allow drag-and-drop reordering |
| `addButtonText` | string | Text for the add item button |

### Editable Table

```yaml
page:
  formWidth: full
  pageTitle: Gmail Labels
  themeColor: '#ffffff'
  backgroundColor: '#f0f0f0'
  children:
    - type: table
      key: gmailLabelsTable
      description: Table displaying Gmail labels with names, IDs, and types
      enableRowSelection: true
      enableCreate: true
      columns:
        - header: Name
          key: name
          size: 150
          enableEditing: false
          editVariant: text
          filterVariant: checkbox
        - header: ID
          key: id
          size: 100
          enableEditing: false
          enableClickToCopy: true
        - header: Type
          key: type
          size: 100
          enableEditing: false
          editVariant: select
          editSelectOptions:
            - system
            - user
        - header: Visibility
          key: visibility
          size: 100
          enableEditing: false
          editVariant: text
      data:
        - id: INBOX
          name: INBOX
          type: system
        - id: SENT
          name: SENT
          type: system
        - id: DRAFT
          name: DRAFT
          type: system
        - id: Label_1
          name: Receipts
          type: user
          labelListVisibility: labelShow
    - type: formButton
      key: submitButton
      text: Submit
onSubmit:
  type: successMessage
```

#### Table Properties

| Property | Type | Description |
|----------|------|-------------|
| `enableRowSelection` | boolean | Allow selecting rows |
| `enableCreate` | boolean | Allow creating new rows |
| `columns` | array | Column definitions |
| `data` | array | Initial table data |

#### Table Column Properties

| Property | Type | Description |
|----------|------|-------------|
| `header` | string | Column header text |
| `key` | string | Data field key |
| `size` | number | Column width in pixels |
| `enableEditing` | boolean | Allow editing this column |
| `editVariant` | string | Editor type: `text`, `select`, etc. |
| `editSelectOptions` | array | Options for select editor |
| `filterVariant` | string | Filter type: `checkbox`, `text`, etc. |
| `enableClickToCopy` | boolean | Enable click-to-copy for cell values |

### Web Viewer

**External URL Example:**
```yaml
page:
  formWidth: full
  children:
    - key: web
      type: webViewer
      height: 1000px
      src: ${{ msg.get_webpage_url.url }}
onSubmit:
  type: successMessage
```

**Full-Screen HTML Application Example:**
```yaml
page:
  formWidth: full
  children:
    - key: web
      type: webViewer
      fullScreen: true
      allowedStyleDomains:
        - https://fonts.googleapis.com
        - https://fonts.gstatic.com
        - https://cdn.jsdelivr.net
      allowedScriptDomains:
        - https://cdn.jsdelivr.net
      html: |
        <!DOCTYPE html>
        <html>
        <head>
          <link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" rel="stylesheet">
          <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
          <style>
            body { font-family: 'Inter', sans-serif; }
          </style>
        </head>
        <body>
          <div id="app">Loading...</div>
          <script>
            // Your application code here
          </script>
        </body>
        </html>
onSubmit:
  type: successMessage
```

#### Web Viewer Properties

| Property | Type | Description |
|----------|------|-------------|
| `src` | string | URL to display (supports expressions). Mutually exclusive with `html`. |
| `html` | string | Custom HTML content to render. Mutually exclusive with `src`. |
| `width` | number/string | Viewer width (e.g., `500px`, `100%`). Default: `100%` |
| `height` | number/string | Viewer height (e.g., `1000px`, `100%`). Default: `500px` |
| `fullScreen` | boolean | If true, fills entire viewport and hides other components |
| `allowedScriptDomains` | array | List of allowed domains for external `<script>` sources (CSP) |
| `allowedStyleDomains` | array | List of allowed domains for external stylesheets and fonts (CSP) |

#### Content Security Policy (CSP) Configuration

The webViewer uses Content Security Policy to protect against XSS and other injection attacks. By default, external scripts and stylesheets are blocked.

**Common Domain Configurations:**

| Use Case | allowedStyleDomains | allowedScriptDomains |
|----------|---------------------|----------------------|
| Google Fonts | `https://fonts.googleapis.com`, `https://fonts.gstatic.com` | - |
| Tailwind CSS (CDN) | `https://cdn.jsdelivr.net` | `https://cdn.jsdelivr.net` |
| Chart.js | - | `https://cdn.jsdelivr.net` |
| Bootstrap | `https://cdn.jsdelivr.net` | `https://cdn.jsdelivr.net` |
| Font Awesome | `https://cdnjs.cloudflare.com` | - |
| React (CDN) | - | `https://unpkg.com` |

**CSP Rules:**

1. **Always use HTTPS** - Domain URLs must use `https://` protocol
2. **Include all required domains** - Some libraries load from multiple domains (e.g., Google Fonts uses both `fonts.googleapis.com` for CSS and `fonts.gstatic.com` for font files)
3. **Script tags are allowed** - You can use `<script>` tags with JavaScript code
4. **Style tags are allowed** - You can use `<style>` tags with CSS rules
5. **Minimize external dependencies** - Only whitelist domains you actually need

**CSP Restrictions (BLOCKED):**

| Blocked Pattern | Why Blocked | Alternative |
|-----------------|-------------|-------------|
| Inline event handlers (`onclick`, `onload`, etc.) | XSS attack vector | Use `addEventListener()` in `<script>` tags |
| Inline `style` attributes (`style="..."`) | XSS attack vector | Use CSS classes in `<style>` tags |
| `javascript:` URLs | XSS attack vector | Use `addEventListener()` for click handlers |
| `eval()` and similar | Code injection risk | Refactor to avoid dynamic code execution |
| Libraries using inline styles (e.g., older jQuery UI) | CSP violation | Use modern CSS-based alternatives |

**Example - Converting Inline Handlers to Event Listeners:**

```html
<!-- WRONG: Inline event handlers are BLOCKED -->
<button onclick="handleClick()">Click Me</button>
<img src="logo.png" onload="imageLoaded()">
<div onmouseover="highlight(this)">Hover me</div>

<!-- CORRECT: Use addEventListener -->
<button id="myButton">Click Me</button>
<img id="logo" src="logo.png">
<div id="hoverDiv">Hover me</div>
<script>
  document.getElementById('myButton').addEventListener('click', handleClick);
  document.getElementById('logo').addEventListener('load', imageLoaded);
  document.getElementById('hoverDiv').addEventListener('mouseover', function() {
    highlight(this);
  });
</script>
```

**Example - Converting Inline Styles to CSS Classes:**

```html
<!-- WRONG: Inline style attributes are BLOCKED -->
<div style="color: red; font-size: 16px;">Styled text</div>
<span style="display: none;">Hidden</span>

<!-- CORRECT: Use CSS classes -->
<style>
  .error-text { color: red; font-size: 16px; }
  .hidden { display: none; }
</style>
<div class="error-text">Styled text</div>
<span class="hidden">Hidden</span>
```

**Example - Dynamic Styles via JavaScript:**

```html
<!-- WRONG: Setting style properties directly may be blocked -->
<script>
  element.style.color = 'red';  // May be blocked
</script>

<!-- CORRECT: Toggle CSS classes instead -->
<style>
  .highlight { background-color: yellow; }
  .error { color: red; border: 1px solid red; }
</style>
<script>
  element.classList.add('highlight');
  element.classList.toggle('error');
  element.classList.remove('highlight');
</script>
```

**Libraries to Avoid:**

Some JavaScript libraries dynamically inject inline styles and will not work:
- Older versions of jQuery UI
- Libraries that use `element.style.property = value` extensively
- Animation libraries that set inline styles directly
- Any library that relies on inline event handlers

**Recommended CSP-Compatible Libraries:**

| Category | Recommended |
|----------|-------------|
| CSS Framework | Tailwind CSS, Bootstrap 5 |
| Charts | Chart.js, ApexCharts |
| Icons | Font Awesome (CSS), Heroicons |
| Animations | Animate.css, CSS transitions/keyframes |
| UI Components | Alpine.js, HTMX |
| State Management | Vanilla JS, Alpine.js |

#### CDN and Source Map Guidelines

When including external JavaScript libraries in webViewer HTML, prefer CDN URLs that don't trigger source map warnings.

**Prefer cdnjs.cloudflare.com over cdn.jsdelivr.net for JavaScript libraries:**

| Library | ✅ Preferred | ❌ Avoid |
|---------|-------------|----------|
| Chart.js | `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js` | `https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js` |
| Alpine.js | `https://cdnjs.cloudflare.com/ajax/libs/alpinejs/3.13.3/cdn.min.js` | `https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js` |
| Day.js | `https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.11.10/dayjs.min.js` | `https://cdn.jsdelivr.net/npm/dayjs@1.11.10/dayjs.min.js` |
| Lodash | `https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.21/lodash.min.js` | `https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js` |
| Moment.js | `https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.30.1/moment.min.js` | `https://cdn.jsdelivr.net/npm/moment@2.30.1/moment.min.js` |

**Why:** jsdelivr serves files that reference `.map` source map files, which the browser tries to fetch via `connect-src`. Since webViewer's CSP restricts `connect-src`, this causes console warnings. cdnjs-hosted minified files typically don't trigger these warnings.

**Update allowedScriptDomains accordingly:**
```yaml
allowedScriptDomains:
  - https://cdnjs.cloudflare.com
```

**Note:** For styles and fonts, cdn.jsdelivr.net is generally fine since style source maps don't trigger the same CSP issues.

## Frontend Design Guidelines for webViewer

When building custom HTML interfaces with `webViewer`, aim for distinctive, production-grade designs that avoid generic "AI slop" aesthetics. The webViewer component gives you full creative control—use it to create memorable, context-appropriate interfaces.

**CRITICAL CSP REMINDER**: All styles must be in `<style>` tags (no `style="..."` attributes). All event handlers must use `addEventListener()` (no `onclick`, `onload`, etc.). See [CSP Restrictions](#csp-restrictions-blocked) above.

### Design Philosophy

Before writing HTML/CSS, commit to a **bold aesthetic direction**:

| Aesthetic | Characteristics | Best For |
|-----------|-----------------|----------|
| Brutally Minimal | Maximum whitespace, stark typography, monochrome | Data dashboards, professional tools |
| Maximalist | Rich textures, layered elements, bold colors | Creative portfolios, marketing pages |
| Retro-Futuristic | Neon accents, gradients, geometric shapes | Tech products, gaming interfaces |
| Organic/Natural | Soft curves, earth tones, subtle textures | Wellness apps, eco-focused products |
| Editorial/Magazine | Strong typography hierarchy, grid layouts | Content-heavy interfaces, reports |
| Industrial/Utilitarian | Raw materials aesthetic, functional focus | Admin panels, developer tools |
| Art Deco/Geometric | Bold patterns, symmetry, metallic accents | Luxury products, event pages |
| Soft/Pastel | Gentle gradients, rounded corners, light palette | Consumer apps, onboarding flows |

**CRITICAL**: Choose one direction and execute with precision. Bold maximalism and refined minimalism both work—the key is intentionality.

### Typography Excellence

Typography makes or breaks an interface. Avoid generic defaults.

**Font Pairing Examples:**
```html
<!-- AVOID: Generic, forgettable -->
<link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">

<!-- BETTER: Distinctive, memorable -->
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+3&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=DM+Sans&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@700&family=Work+Sans&display=swap" rel="stylesheet">
```

**Typography CSS Pattern:**
```html
<style>
  :root {
    --font-display: 'Playfair Display', serif;
    --font-body: 'Source Sans 3', sans-serif;
    --type-scale: 1.25;
  }

  h1 {
    font-family: var(--font-display);
    font-size: calc(1rem * var(--type-scale) * var(--type-scale) * var(--type-scale));
    letter-spacing: -0.02em;
    line-height: 1.1;
  }

  body {
    font-family: var(--font-body);
    font-size: 1rem;
    line-height: 1.6;
  }
</style>
```

### Color Systems

Build cohesive color palettes using CSS custom properties:

```html
<style>
  :root {
    /* Primary palette */
    --color-primary: #1a365d;
    --color-primary-light: #2a4a7f;
    --color-primary-dark: #0d1b2a;

    /* Accent - use sparingly for impact */
    --color-accent: #f59e0b;
    --color-accent-hover: #d97706;

    /* Neutrals */
    --color-surface: #fafafa;
    --color-surface-elevated: #ffffff;
    --color-text: #1f2937;
    --color-text-muted: #6b7280;

    /* Semantic */
    --color-success: #059669;
    --color-warning: #d97706;
    --color-error: #dc2626;
  }

  /* Dark theme variant */
  .dark {
    --color-surface: #0f172a;
    --color-surface-elevated: #1e293b;
    --color-text: #f1f5f9;
    --color-text-muted: #94a3b8;
  }
</style>
```

**Color Usage Principles:**
- Dominant colors with sharp accents outperform evenly-distributed palettes
- Reserve accent colors for CTAs and key interactive elements
- Use semantic colors consistently for feedback states

### Motion & Animation

Well-crafted animations create delight. Focus on high-impact moments.

**Page Load Animation Pattern:**
```html
<style>
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-in {
    animation: fadeInUp 0.6s ease-out forwards;
    opacity: 0;
  }

  /* Staggered reveals create rhythm */
  .animate-in.delay-1 { animation-delay: 100ms; }
  .animate-in.delay-2 { animation-delay: 200ms; }
  .animate-in.delay-3 { animation-delay: 300ms; }
</style>

<div class="container">
  <h1 class="animate-in">Welcome</h1>
  <p class="animate-in delay-1">Your dashboard is ready</p>
  <button class="animate-in delay-2">Get Started</button>
</div>
```

**Micro-interaction Pattern:**
```html
<style>
  .btn {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    transform: translateY(0);
  }

  .btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .btn:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
</style>
```

### Spatial Composition & Layout

Break free from predictable layouts:

```html
<style>
  /* Asymmetric grid layout */
  .hero-grid {
    display: grid;
    grid-template-columns: 1.5fr 1fr;
    gap: 4rem;
    align-items: center;
  }

  /* Overlapping elements create depth */
  .card-stack {
    position: relative;
  }

  .card-stack .card-behind {
    position: absolute;
    top: 2rem;
    left: 2rem;
    z-index: -1;
    opacity: 0.6;
  }

  /* Generous negative space */
  .section {
    padding: clamp(4rem, 10vw, 8rem) clamp(1rem, 5vw, 4rem);
  }
</style>
```

### Backgrounds & Visual Texture

Create atmosphere beyond solid colors:

**Gradient Mesh Background:**
```html
<style>
  .gradient-bg {
    background:
      radial-gradient(ellipse at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 20%, rgba(255, 119, 115, 0.2) 0%, transparent 50%),
      radial-gradient(ellipse at 40% 40%, rgba(72, 187, 120, 0.15) 0%, transparent 40%),
      linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%);
  }
</style>
```

**Noise Texture Overlay:**
```html
<style>
  .textured {
    position: relative;
  }

  .textured::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    opacity: 0.05;
    pointer-events: none;
  }
</style>
```

**Geometric Pattern:**
```html
<style>
  .geometric-bg {
    background-color: #1a1a2e;
    background-image:
      linear-gradient(30deg, #2d2d44 12%, transparent 12.5%, transparent 87%, #2d2d44 87.5%, #2d2d44),
      linear-gradient(150deg, #2d2d44 12%, transparent 12.5%, transparent 87%, #2d2d44 87.5%, #2d2d44),
      linear-gradient(30deg, #2d2d44 12%, transparent 12.5%, transparent 87%, #2d2d44 87.5%, #2d2d44),
      linear-gradient(150deg, #2d2d44 12%, transparent 12.5%, transparent 87%, #2d2d44 87.5%, #2d2d44);
    background-size: 80px 140px;
    background-position: 0 0, 0 0, 40px 70px, 40px 70px;
  }
</style>
```

### Complete webViewer Design Example

Here's a complete CSP-compliant example applying these principles:

```yaml
page:
  formWidth: full
  children:
    - key: app
      type: webViewer
      fullScreen: true
      allowedStyleDomains:
        - https://fonts.googleapis.com
        - https://fonts.gstatic.com
      html: |
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
          <style>
            *, *::before, *::after {
              box-sizing: border-box;
              margin: 0;
              padding: 0;
            }

            :root {
              --font-display: 'Fraunces', serif;
              --font-body: 'DM Sans', sans-serif;
              --color-bg: #0a0a0f;
              --color-surface: #12121a;
              --color-text: #f4f4f5;
              --color-text-muted: #71717a;
              --color-accent: #fbbf24;
              --color-accent-glow: rgba(251, 191, 36, 0.2);
            }

            body {
              font-family: var(--font-body);
              background: var(--color-bg);
              color: var(--color-text);
              min-height: 100vh;
              line-height: 1.6;
            }

            /* Gradient mesh background */
            .bg-mesh {
              position: fixed;
              inset: 0;
              background:
                radial-gradient(ellipse at 20% 0%, rgba(251, 191, 36, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 100%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
              pointer-events: none;
            }

            .container {
              max-width: 1200px;
              margin: 0 auto;
              padding: 6rem 2rem;
              position: relative;
            }

            .hero {
              display: grid;
              grid-template-columns: 1.2fr 1fr;
              gap: 4rem;
              align-items: center;
              min-height: 80vh;
            }

            .hero-title {
              font-family: var(--font-display);
              font-size: clamp(3rem, 8vw, 5rem);
              font-weight: 900;
              line-height: 1.05;
              letter-spacing: -0.03em;
              margin-bottom: 1.5rem;
            }

            .hero-title .accent {
              color: var(--color-accent);
              text-shadow: 0 0 40px var(--color-accent-glow);
            }

            .hero-description {
              font-size: 1.25rem;
              color: var(--color-text-muted);
              max-width: 480px;
              margin-bottom: 2rem;
            }

            .btn {
              display: inline-flex;
              align-items: center;
              gap: 0.5rem;
              padding: 1rem 2rem;
              background: var(--color-accent);
              color: var(--color-bg);
              font-family: var(--font-body);
              font-weight: 600;
              font-size: 1rem;
              border: none;
              border-radius: 8px;
              cursor: pointer;
              transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            }

            .btn:hover {
              transform: translateY(-2px);
              box-shadow: 0 8px 30px var(--color-accent-glow);
            }

            /* Animation */
            @keyframes fadeInUp {
              from { opacity: 0; transform: translateY(30px); }
              to { opacity: 1; transform: translateY(0); }
            }

            .animate-in {
              animation: fadeInUp 0.8s ease-out forwards;
              opacity: 0;
            }

            .animate-delay-1 { animation-delay: 150ms; }
            .animate-delay-2 { animation-delay: 300ms; }
            .animate-delay-3 { animation-delay: 450ms; }

            /* Card with glow effect */
            .card {
              background: var(--color-surface);
              border: 1px solid rgba(255, 255, 255, 0.06);
              border-radius: 16px;
              padding: 2rem;
              position: relative;
              overflow: hidden;
            }

            .card::before {
              content: '';
              position: absolute;
              top: 0;
              left: 0;
              right: 0;
              height: 1px;
              background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            }

            .card-title {
              font-weight: 600;
              margin-bottom: 0.5rem;
            }

            .card-description {
              color: var(--color-text-muted);
            }
          </style>
        </head>
        <body>
          <div class="bg-mesh"></div>
          <div class="container">
            <div class="hero">
              <div class="hero-content">
                <h1 class="hero-title animate-in">Build something <span class="accent">remarkable</span></h1>
                <p class="hero-description animate-in animate-delay-1">Create interfaces that leave a lasting impression. Design with intention, execute with precision.</p>
                <button id="cta-btn" class="btn animate-in animate-delay-2">Get Started →</button>
              </div>
              <div class="card animate-in animate-delay-3">
                <h3 class="card-title">Dashboard Preview</h3>
                <p class="card-description">Your content here</p>
              </div>
            </div>
          </div>
          <script>
            document.getElementById('cta-btn').addEventListener('click', function() {
              console.log('Button clicked');
            });
          </script>
        </body>
        </html>
onSubmit:
  type: successMessage
```

### Design Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails | Better Approach |
|--------------|--------------|-----------------|
| Purple gradients on white | Overused, generic AI aesthetic | Choose unexpected color combinations |
| Inter/Roboto/Arial everywhere | Forgettable, lacks personality | Pick fonts that match the context |
| Evenly-spaced grid layouts | Predictable, lacks visual interest | Asymmetry, overlap, varied spacing |
| Same card component repeated | Monotonous, no hierarchy | Vary sizes, styles, create focal points |
| Subtle gray text on white | Low contrast, accessibility issues | Proper contrast ratios, intentional muting |
| Drop shadows on everything | Dated, cluttered appearance | Strategic elevation for key elements |

### Design Checklist

Before finalizing your webViewer interface:

- [ ] **Aesthetic Direction**: Is there a clear, intentional design direction?
- [ ] **Typography**: Are fonts distinctive and well-paired?
- [ ] **Color Palette**: Is the palette cohesive with intentional accent usage?
- [ ] **Hierarchy**: Do users know where to look first, second, third?
- [ ] **Breathing Room**: Is there enough whitespace (or intentional density)?
- [ ] **Motion**: Do animations enhance without overwhelming?
- [ ] **Uniqueness**: Would this be recognizable as distinct from generic templates?
- [ ] **Context Fit**: Does the design serve the interface's actual purpose?
- [ ] **CSP Compliance**: No inline styles or inline event handlers?

## Theming Support

BorgIQ provides a curated collection of professional themes with carefully selected color palettes and font pairings. Each theme includes cohesive colors with hex codes, complementary font pairings for headers and body text, and a distinct visual identity suitable for different contexts and audiences.

### Available Themes

| Theme | Description | Best For |
|-------|-------------|----------|
| **Ocean Depths** | Professional and calming maritime theme | Corporate presentations, financial reports, trust-building content |
| **Sunset Boulevard** | Warm and vibrant sunset colors | Creative pitches, marketing presentations, lifestyle brands |
| **Forest Canopy** | Natural and grounded earth tones | Environmental presentations, sustainability reports, wellness content |
| **Modern Minimalist** | Clean and contemporary grayscale | Tech presentations, architecture portfolios, data visualization |
| **Golden Hour** | Rich and warm autumnal palette | Restaurant presentations, hospitality brands, artisan products |
| **Arctic Frost** | Cool and crisp winter-inspired theme | Healthcare presentations, technology solutions, pharmaceutical content |
| **Desert Rose** | Soft and sophisticated dusty tones | Fashion presentations, beauty brands, interior design |
| **Tech Innovation** | Bold and modern tech aesthetic | Tech startups, software launches, AI/ML presentations |
| **Botanical Garden** | Fresh and organic garden colors | Garden centers, food presentations, natural products |
| **Midnight Galaxy** | Dramatic and cosmic deep tones | Entertainment industry, gaming presentations, luxury brands |

Theme definitions are located in [themes.md](themes.md) with complete specifications.

**Custom HTML in webViewer:** style webViewer content with the app theme library — [react-app-themes.md](react-app-themes.md). It is plain CSS (custom properties + component recipes), so it works in raw HTML+CSS with no React and no CDN: paste the Base Contract + one theme block (default `hearth`) into the webViewer styles and use Tabler icons as inline SVG.

### Using Themes

To apply a theme to your interface:

1. **Select an appropriate theme** based on context and audience
2. **Read the theme definition** from [themes.md](themes.md)
3. **Apply colors and fonts** consistently throughout your interface
4. **Ensure proper contrast** and readability

**Default theme**: Use **Modern Minimalist** when no specific theme is requested.

### Theme Application Examples

#### Using Ocean Depths Theme

```yaml
page:
  formWidth: full
  themeColor: '#2d8b8b'
  backgroundColor: '#1a2332'
  children:
    - key: app
      type: webViewer
      fullScreen: true
      allowedStyleDomains:
        - https://fonts.googleapis.com
        - https://fonts.gstatic.com
      html: |
        <!DOCTYPE html>
        <html>
        <head>
          <link href="https://fonts.googleapis.com/css2?family=DejaVu+Sans:wght@400;700&display=swap" rel="stylesheet">
          <style>
            :root {
              /* Ocean Depths Color Palette */
              --color-primary: #1a2332;     /* Deep Navy */
              --color-accent: #2d8b8b;      /* Teal */
              --color-secondary: #a8dadc;   /* Seafoam */
              --color-text: #f1faee;        /* Cream */
              --font-headers: 'DejaVu Sans', sans-serif;
              --font-body: 'DejaVu Sans', sans-serif;
            }
            body {
              font-family: var(--font-body);
              background: var(--color-primary);
              color: var(--color-text);
            }
            h1, h2, h3 {
              font-family: var(--font-headers);
              font-weight: 700;
              color: var(--color-secondary);
            }
            .accent { color: var(--color-accent); }
          </style>
        </head>
        <body>
          <h1>Corporate Dashboard</h1>
          <p class="accent">Professional and calming design</p>
        </body>
        </html>
onSubmit:
  type: successMessage
```

#### Using Botanical Garden Theme

```yaml
page:
  formWidth: half
  themeColor: '#4a7c59'
  backgroundColor: '#f5f3ed'
  children:
    - key: header
      type: header
      value: Garden Center Intake Form
      color: '#4a7c59'
    - key: divider
      type: divider
      color: '#b7472a'
    - key: name
      type: text
      label: Your Name
      required: true
    - key: plantType
      type: select
      label: Plant Category
      options:
        - label: Flowering Plants
          value: flowering
        - label: Succulents
          value: succulents
        - label: Herbs
          value: herbs
    - key: submit
      type: formButton
      value: Submit Request
      color: '#4a7c59'
      variant: filled
onSubmit:
  type: successMessage
```

#### Using Tech Innovation Theme for Dashboard

```yaml
page:
  formWidth: full
  children:
    - key: dashboard
      type: webViewer
      fullScreen: true
      allowedStyleDomains:
        - https://fonts.googleapis.com
        - https://fonts.gstatic.com
      html: |
        <!DOCTYPE html>
        <html>
        <head>
          <link href="https://fonts.googleapis.com/css2?family=DejaVu+Sans:wght@400;700&display=swap" rel="stylesheet">
          <style>
            :root {
              /* Tech Innovation Color Palette */
              --color-bg: #1e1e1e;          /* Dark Gray */
              --color-primary: #0066ff;     /* Electric Blue */
              --color-accent: #00ffff;      /* Neon Cyan */
              --color-text: #ffffff;        /* White */
              --font-headers: 'DejaVu Sans', sans-serif;
              --font-body: 'DejaVu Sans', sans-serif;
            }
            body {
              font-family: var(--font-body);
              background: var(--color-bg);
              color: var(--color-text);
              margin: 0;
              padding: 2rem;
            }
            h1 {
              font-family: var(--font-headers);
              font-weight: 700;
              background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
              -webkit-background-clip: text;
              -webkit-text-fill-color: transparent;
              background-clip: text;
            }
            .card {
              background: rgba(0, 102, 255, 0.1);
              border: 1px solid var(--color-primary);
              border-radius: 8px;
              padding: 1.5rem;
              margin: 1rem 0;
            }
            .metric {
              font-size: 2.5rem;
              font-weight: 700;
              color: var(--color-accent);
            }
          </style>
        </head>
        <body>
          <h1>AI Analytics Dashboard</h1>
          <div class="card">
            <p>Total Processes</p>
            <div class="metric">1,247</div>
          </div>
        </body>
        </html>
onSubmit:
  type: successMessage
```

### Creating Custom Themes

When existing themes don't fit your use case, create a custom theme following this structure:

```markdown
# Theme Name

A brief description of the theme's aesthetic and mood.

## Color Palette

- **Color Name**: `#hexcode` - Usage description
- **Color Name**: `#hexcode` - Usage description
- **Color Name**: `#hexcode` - Usage description
- **Color Name**: `#hexcode` - Usage description

## Typography

- **Headers**: Font Name Weight
- **Body Text**: Font Name

## Best Used For

List of appropriate use cases and contexts.
```

**Guidelines for custom themes:**

1. **Choose 4 primary colors** - A dark base, primary accent, secondary accent, and text/background color
2. **Select complementary fonts** - One for headers (can be bold/distinctive) and one for body text (prioritize readability)
3. **Test contrast ratios** - Ensure text is readable against all background colors
4. **Document use cases** - Help others understand when to apply the theme
