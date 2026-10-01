# Interface Page Examples

Complete, minimal pages to copy: a contact form, an approval page, a multi-step form, conditional fields and an editable table. Each block is the actor's `configuration.options`; the actor document around it is in [interface-trigger-actor.md](interface-trigger-actor.md) and [interface-actor.md](interface-actor.md). Page rules are in [interface-pages.md](interface-pages.md), component props in [interface-components.md](interface-components.md).

## Contents

- [Contact form](#contact-form)
- [Approval page](#approval-page)
- [Multi-step form](#multi-step-form)
- [Conditional fields](#conditional-fields)
- [Editable table](#editable-table)

## Contact form

An InterfaceTriggerActor page. Every field's value arrives in the trigger's `body` under its `key`: `${{ msg.<msgVar>.body.email }}`.

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
      variant: email
      placeholder: your@email.com
      required: true
    - key: message
      type: textarea
      label: Message
      placeholder: How can we help?
      required: true
    - key: submit
      type: formButton
      text: Send Message
onSubmit:
  type: successMessage
  successMessage: Thank you for your submission!
```

## Approval page

An InterfaceActor page that shows upstream data read-only (`default` with an expression) and captures a decision. Wire its Meta port (`SPRTdefault`) to the SendEmailActor that mails `interfaceUrl` to the approver, and its Event port (`SPRTevent00`) to the actor that acts on `body.decision` ([interface-actor.md](interface-actor.md)). The approver must be a workspace member.

```yaml
page:
  pageTitle: Approval Required
  formWidth: half
  children:
    - key: header
      type: header
      value: Request Approval
    - key: requestDetails
      type: section
      label: Request Details
      extendParentObject: true        # body gets requestId, requestedBy, amount at the top level
      children:
        - key: requestId
          type: text
          label: Request ID
          readOnly: true
          default: ${{ msg.request.id }}
        - key: requestedBy
          type: text
          label: Requested By
          readOnly: true
          default: ${{ msg.request.submittedBy }}
        - key: amount
          type: currency
          label: Amount
          readOnly: true
          default: ${{ msg.request.amount }}
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
      text: Submit Decision
onSubmit:
  type: successMessage
  successMessage: Thank you for your response!
timeoutInMinutes: 4320   # stop waiting after 3 days; the actor then fails with a TimeoutError
```

Downstream of the Event port, read `${{ msg.<msgVar>.body.decision }}`, `${{ msg.<msgVar>.body.comments }}` and the approver's `${{ msg.<msgVar>.meta.user.email }}`.

## Multi-step form

Each step is its own page. A step with `onSubmit: nextInterface` shows a waiting page after submission; the first InterfaceActor that renders downstream in the same flow run replaces it. Each later step's body arrives on that InterfaceActor's Event port.

Step 1, the InterfaceTriggerActor (`msgVar: registration`):

```yaml
page:
  pageTitle: Registration - Step 1
  children:
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
        - key: email
          type: text
          label: Email
          variant: email
          required: true
    - key: submit
      type: formButton
      text: Continue to Step 2
onSubmit:
  type: nextInterface
  loadingMessage: Processing your request...
showProgressStatus: true      # show the flow's progress on the waiting page
```

Step 2, a downstream InterfaceActor, carries step 1's answers forward read-only:

```yaml
page:
  pageTitle: Registration - Step 2
  children:
    - key: progress
      type: progress
      value: 66
      label: Step 2 of 3
    - key: email
      type: text
      label: Email
      readOnly: true
      default: ${{ msg.registration.body.email }}
    - key: company
      type: text
      label: Company
      required: true
    - key: submit
      type: formButton
      text: Finish
onSubmit:
  type: nextInterface
```

Step 3, the result page: an InterfaceActor after the processing actors. Code actors cannot render a page, so a computed result is shown this way.

```yaml
page:
  children:
    - key: header
      type: header
      value: Submission Received!
    - key: reference
      type: textDisplay
      value: Your reference number is ${{ msg.process_submission.id }}
      copyable: true
onSubmit:
  type: successMessage
```

## Conditional fields

The `conditionalField` select decides which `children` entry renders; `children` has one entry per option value.

```yaml
page:
  children:
    - key: contact
      type: conditional
      conditionalField:
        key: method
        type: select
        label: Contact Method
        default: email
        options:
          - label: Email
            value: email
          - label: Phone
            value: phone
      children:
        email:
          - key: email
            type: text
            label: Email Address
            variant: email
        phone:
          - key: phone
            type: phoneNumber
            label: Phone Number
    - key: submit
      type: formButton
      text: Submit
onSubmit:
  type: successMessage
```

The body is `{ contact: { method: email, email: … } }`. With `extendParentObject: true` on the conditional it is `{ method: email, email: … }`.

## Editable table

A table the viewer edits, adds to and selects from. With `enableRowSelection` the body holds the selected rows (`{ labels: [ … ] }`); without it, all rows with the viewer's edits.

```yaml
page:
  formWidth: full
  pageTitle: Gmail Labels
  themeColor: '#1c7ed6'
  children:
    - key: labels
      type: table
      description: Select the labels to apply
      enableRowSelection: true
      enableEditing: true
      enableCreate: true
      columns:
        - header: Name
          key: name
          size: 150
        - header: ID
          key: id
          size: 100
          enableEditing: false
          enableClickToCopy: true
        - header: Type
          key: type
          size: 100
          editVariant: select
          editSelectOptions:
            - system
            - user
      data:
        - id: INBOX
          name: INBOX
          type: system
        - id: Label_1
          name: Receipts
          type: user
    - key: submit
      type: formButton
      text: Submit
onSubmit:
  type: successMessage
```
