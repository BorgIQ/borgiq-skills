# HTTP Request Actor Examples

Complete examples for building HttpRequestActor configurations.

## Table of Contents
1. [Basic GET Request with Query Params](#basic-get-request-with-query-params)
2. [Gmail: Fetch Label ID by Name](#gmail-fetch-label-id-by-name)
3. [Gmail: Create a Draft](#gmail-create-a-draft)
4. [Gmail: Get Email by ID](#gmail-get-email-by-id)
5. [Airtable: Append Data to Table](#airtable-append-data-to-table)
6. [Gmail: Search Email](#gmail-search-email)
7. [Firecrawl: Scrape](#firecrawl-scrape)

---

## Basic GET Request with Query Params

Simple GET request demonstrating query parameters and untyped connection.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01k49as4vfdydgy6q0n436wtyj:
    type: HttpRequestActor
    version: 1
    name: A Simple GET Request with Query Params
    msgVar: a_simple_get_request_with_query_params
    description: The HTTP Request Actor can make HTTP requests
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        url: https://www.example.com
        method: GET
        headers:
          content-type: application/json; charset=utf-8
        queryParams:
          searchString: xxx
          limit: 10
        auth: ${{connection.auth}}
      connection:
        key: a-key-from-the-workspace-connections
    schemas: {}
    id: ACTR01k49as4vfdydgy6q0n436wtyj
    position:
      x: -8808.062646516164
      'y': -199.72314974881743
    edges: {}
```

**Sample Response:**
```json
{
  "body": "<!doctype html>...",
  "statusCode": 200,
  "headers": {
    "content-type": "text/html",
    "cache-control": "max-age=769"
  }
}
```

---

## Gmail: Fetch Label ID by Name

Demonstrates using `outputs` to extract specific data from the response.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01jrtpyfz09s6xqem7aj5rs678:
    name: Fetch label ID by name from Gmail
    type: HttpRequestActor
    msgVar: gmail_fetch_label_id_by_name
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: Fetch all Gmail labels
    continueOnError: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        labelName: Receipts
      options:
        url: https://gmail.googleapis.com/gmail/v1/users/me/labels
        method: GET
        headers:
          content-type: application/json; charset=utf-8
        auth: ${{connection.auth}}
        emitRequest: false
      outputs: |-
        ${{ results.body.labels.find(label => label.name ===
        inputs.labelName).id }}
      connection:
        key: john-gmail
        type: gmail
      error:
        if: ${{!Q.isHTTPStatusInRange(results.statusCode, ["200-299"])}}
        includeResult: true
        retryIf: ${{Q.isHTTPStatusInRange(results.statusCode, ["500-599"])}}
        message: ${{Q.toJSON(results)}}
    id: ACTR01jrtpyfz09s6xqem7aj5rs678
    position:
      x: 628.6306629866151
      'y': 328.3419873221628
    edges: {}
```

---

## Gmail: Create a Draft

Demonstrates using `vars` for complex computations before building the request body.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01jrv27scxfhrv7vj1nzh74rqv:
    name: Create a draft in Gmail
    type: HttpRequestActor
    msgVar: gmail_create_a_draft
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: The HTTP Request Actor can make HTTP requests
    continueOnError: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      vars:
        - headerContent:
            - 'From: ${{ inputs.from }}'
            - 'To: ${{ inputs.to }}'
            - '${{ inputs.cc ? `Cc: ${inputs.cc}` : undefined  }}'
            - '${{ inputs.bcc ? `Bcc: ${inputs.bcc}` : undefined  }}'
            - 'Subject: ${{inputs.subject}}'
        - header: ${{ Q.lo.compact(vars.headerContent) }}
        - body:
            - ''
            - ${{ inputs.body }}
        - base64Message: ${{ Q.toBase64([...vars.header, ...vars.body].join('\r\n')) }}
      inputs:
        from: alex@example.com
        to: alexp@example.com, taylor@example.com
        cc: jordan@example.com
        bcc: morgan@example.com
        subject: Test Email from BorgIQ Integration!
        body: |
          Hi there,

          have a great day

          Today is ${{ new Date() }}

          ----
          Alex Thompson
          CEO, Acme Corp
      options:
        url: https://gmail.googleapis.com/gmail/v1/users/me/drafts/
        method: POST
        headers:
          content-type: application/json; charset=utf-8
        auth: ${{connection.auth}}
        body:
          message:
            raw: ${{ vars.base64Message }}
        emitRequest: false
      connection:
        key: john-gmail
        type: gmail
    id: ACTR01jrv27scxfhrv7vj1nzh74rqv
    position:
      x: -33.68313019049873
      'y': 1517.940113341475
    edges: {}
```

---

## Gmail: Get Email by ID

Demonstrates comprehensive input schema with enums and descriptions.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01jta1jz97zrjmwveq430hg05m:
    name: Get email by ID from Gmail
    type: HttpRequestActor
    msgVar: gmail_get_email_by_id
    schemas:
      inputs:
        type: object
        properties:
          userId:
            type: string
            title: User Id
            description: >-
              The user's email address. The special value me can be used to
              indicate the authenticated user.
            default: me
          gmailMailId:
            type: string
            title: Mail Id
            description: Gmail Mail Id
          format:
            type: string
            title: Format
            description: >-
              The format of the email message data to be returned. Options
              include: - minimal: Returns only email message ID and labels; does
              not return the email headers, body, or payload. - full: Returns
              the full email message data with body content parsed in the
              payload field; the raw field is not used. Format cannot be used
              when accessing the API using the gmail.metadata scope. - raw:
              Returns the full email message data with body content in the raw
              field as a base64url encoded string; the payload field is not
              used. Format cannot be used when accessing the API using the
              gmail.metadata scope. - metadata: Returns only email message ID,
              labels, and email headers.
            enum:
              - minimal
              - full
              - raw
              - metadata
        required:
          - userId
          - gmailMailId
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: The HTTP Request Actor can make HTTP requests
    continueOnError: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        userId: me
        gmailMailId: 197316a18debab40
        format: full
      options:
        url: >-
          https://gmail.googleapis.com/gmail/v1/users/${{ inputs.userId
          }}/messages/${{ inputs.gmailMailId }}
        method: GET
        headers:
          content-type: application/json; charset=utf-8
        queryParams:
          format: ${{ inputs.format }}
        auth: ${{connection.auth}}
        emitRequest: true
      connection:
        key: john-gmail
    id: ACTR01jta1jz97zrjmwveq430hg05m
    position:
      x: 1304.860745068128
      'y': 84.38514785364455
    edges: {}
```

---

## Airtable: Append Data to Table

Demonstrates using `type: any` for flexible array of records input.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01k4qwbvvnbnvg0m1r42scmg6r:
    type: HttpRequestActor
    version: 1
    name: Append data to table in Airtable
    msgVar: airtable_append_data_to_table
    description: Append records to an Airtable table
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        baseId: ''
        tableId: ''
        records: []
      options:
        url: https://api.airtable.com/v0/${{inputs.baseId}}/${{inputs.tableId}}
        method: POST
        headers:
          Content-Type: application/json
        body:
          records: ${{inputs.records}}
        auth: ${{connection.auth}}
      connection:
        key: airtable
      error:
        if: ${{!Q.isHTTPStatusInRange(results.statusCode, ["200-299"])}}
        retryIf: ${{Q.isHTTPStatusInRange(results.statusCode, ["429", "500-599"])}}
        includeResult: true
        message: ${{Q.toJSON(results)}}
    schemas:
      inputs:
        type: object
        properties:
          baseId:
            type: string
            title: Base ID
            description: The Airtable base ID
          tableId:
            type: string
            title: Table ID
            description: The Airtable table ID or name
          records:
            type: array
            title: Records
            description: Array of records to append
            items:
              type: object
              properties:
                fields:
                  type: any
                  description: Field values for the record
        required:
          - baseId
          - tableId
          - records
    id: ACTR01k4qwbvvnbnvg0m1r42scmg6r
    position:
      x: -1398.1464876509183
      'y': 779.3218996411707
    edges: {}
```

---

## Gmail: Search Email

Demonstrates typed connection and complex query parameters with optional handling.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01jwrz45vq4bq4c3pagpj5dyhk:
    icon:
      type: borgiq
      value: >-
        160ac19845:google-gmail
    name: Search email in Gmail
    type: HttpRequestActor
    msgVar: gmail_search_email
    schemas:
      inputs:
        type: object
        properties:
          query:
            type: string
            title: Search Query
            description: >-
              Enter the search query to find emails (e.g.,
              'from:example@gmail.com').
          maxResults:
            type: integer
            title: Maximum Results
            description: Specify the maximum number of email results to return.
          pageToken:
            type: string
            title: Page Token
            description: Use this token to retrieve the next set of results.
          labelIds:
            type: array
            title: Label IDs
            description: Select the labels to filter the emails.
            items:
              type: string
        required:
          - query
          - maxResults
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: >-
      Search for email in Gmail. It supports Gmail advanced operator:
      https://support.google.com/mail/answer/7190
    continueOnError: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        query: >-
          in:inbox from:mail.anthropic.com subject:"Secure link to log in to
          Claude.ai" from:anthropic.com subject:"Secure link to log in to
          Claude.ai" newer_than:1d
        maxResults: 100
      options:
        url: https://gmail.googleapis.com/gmail/v1/users/me/messages/
        method: GET
        queryParams:
          q: ${{ inputs.query }}
          labelIds: ${{ inputs?.labelIds }}
          includeSpamTrash: ${{ inputs?.includeSpamTrash || false }}
          maxResults: ${{ inputs?.includeSpamTrash || 100 }}
          pageToken: ${{ inputs?.pageToken }}
        auth: ${{connection.auth}}
        emitRequest: false
      connection:
        key: john-gmail
        type: gmail
    id: ACTR01jwrz45vq4bq4c3pagpj5dyhk
    position:
      x: 3864.305238937567
      'y': 75.47393092989334
    edges: {}
```

---

## Firecrawl: Scrape

Demonstrates complex body construction with conditional fields using `|` operator.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kan0ey740zjdeq9ex9k80ay9:
    type: HttpRequestActor
    version: 1
    name: Scrape URL with Firecrawl
    msgVar: firecrawl_scrape
    description: Scrape a URL using Firecrawl API
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        url: https://api.firecrawl.dev/v2/scrape
        method: POST
        headers:
          Content-Type: application/json
        body:
          url: ${{inputs.url}}
          formats: ${{inputs.formats}}
          onlyMainContent: ${{inputs.onlyMainContent}}
          includeTags: |
            ${{inputs.includeTags?.length > 0 ? inputs.includeTags : undefined}}
          excludeTags: |
            ${{inputs.excludeTags?.length > 0 ? inputs.excludeTags : undefined}}
          maxAge: ${{inputs.maxAge}}
          headers: >
            ${{Object.keys(inputs?.headers ?? {})?.length > 0 ? inputs.headers :
            undefined}}
          waitFor: ${{inputs.waitFor}}
          mobile: ${{inputs.mobile}}
          skipTlsVerification: ${{inputs.skipTlsVerification}}
          timeout: ${{inputs.timeout}}
          parsers: ${{inputs.parsers}}
          actions: |
            ${{inputs.actions?.length > 0 ? inputs.actions : undefined}}
          location: ${{inputs.location}}
          removeBase64Images: ${{inputs.removeBase64Images}}
          blockAds: ${{inputs.blockAds}}
          proxy: ${{inputs.proxy}}
          storeInCache: ${{inputs.storeInCache}}
          zeroDataRetention: ${{inputs.zeroDataRetention}}
        auth: ${{connection.auth}}
      connection:
        key: firecrawl
      error:
        if: ${{!Q.isHTTPStatusInRange(results.statusCode, ["200-299"])}}
        retryIf: ${{Q.isHTTPStatusInRange(results.statusCode, ["429", "500-599"])}}
        includeResult: true
        message: ${{Q.toJSON(results)}}
      inputs:
        url: https://docs.firecrawl.dev/api-reference/endpoint/scrape
    schemas:
      inputs:
        type: object
        properties:
          url:
            type: string
            format: uri
            title: URL
            description: The URL to scrape
          formats:
            type: array
            title: Formats
            description: Output formats to include in the response
            items:
              type: any
            default:
              - markdown
          onlyMainContent:
            type: boolean
            title: Only Main Content
            description: >-
              Only return the main content of the page excluding headers, navs,
              footers, etc.
            default: true
          includeTags:
            type: array
            title: Include Tags
            description: Tags to include in the output
            items:
              type: string
          excludeTags:
            type: array
            title: Exclude Tags
            description: Tags to exclude from the output
            items:
              type: string
          maxAge:
            type: integer
            title: Max Age
            description: >-
              Returns a cached version of the page if it is younger than this
              age in milliseconds
            default: 172800000
          headers:
            type: object
            title: Headers
            description: Headers to send with the request
          waitFor:
            type: integer
            title: Wait For
            description: Specify a delay in milliseconds before fetching the content
            default: 0
          mobile:
            type: boolean
            title: Mobile
            description: Set to true if you want to emulate scraping from a mobile device
            default: false
          skipTlsVerification:
            type: boolean
            title: Skip TLS Verification
            description: Skip TLS certificate verification when making requests
            default: true
          timeout:
            type: integer
            title: Timeout
            description: Timeout in milliseconds for the request
          parsers:
            type: array
            title: Parsers
            description: Controls how files are processed during scraping
            items:
              type: any
            default:
              - pdf
          actions:
            type: array
            title: Actions
            description: Actions to perform on the page before grabbing the content
            items:
              type: any
          location:
            type: object
            title: Location
            description: Location settings for the request
            properties:
              country:
                type: string
                title: Country
                description: ISO 3166-1 alpha-2 country code
                default: US
              languages:
                type: array
                title: Languages
                description: Preferred languages and locales for the request
                items:
                  type: string
                default:
                  - en-US
          removeBase64Images:
            type: boolean
            title: Remove Base64 Images
            description: Removes all base 64 images from the output
            default: true
          blockAds:
            type: boolean
            title: Block Ads
            description: Enables ad-blocking and cookie popup blocking
            default: true
          proxy:
            type: string
            title: Proxy
            description: Specifies the type of proxy to use
            enum:
              - basic
              - stealth
              - auto
            default: auto
          storeInCache:
            type: boolean
            title: Store In Cache
            description: If true, the page will be stored in the Firecrawl index and cache
            default: true
          zeroDataRetention:
            type: boolean
            title: Zero Data Retention
            description: If true, this will enable zero data retention for this scrape
            default: false
        required:
          - url
    id: ACTR01kan0ey740zjdeq9ex9k80ay9
    position:
      x: -1166.233673529532
      'y': 526.8324789094753
    edges: {}
```
