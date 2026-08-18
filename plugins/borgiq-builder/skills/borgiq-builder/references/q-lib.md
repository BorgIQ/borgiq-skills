# Q-lib Function Reference for LLM Code Generation

This document provides comprehensive documentation for all Q-lib functions for LLM code generation. All functions are accessed via the `Q` object using the format `Q.functionName()`.

## Table of Contents

- [Available Libraries](#available-libraries)
- [Function Categories](#function-categories)
  - [Text Processing Functions](#text-processing-functions) - 17 functions
  - [Encoding Functions](#encoding-functions) - 3 functions
  - [Decoding Functions](#decoding-functions) - 5 functions
  - [Data Format Functions](#data-format-functions) - 9 functions
  - [Utility Functions](#utility-functions) - 4 functions
  - [Date/Time Functions](#datetime-functions) - 3 functions
  - [Array Functions](#array-functions) - 1 function
  - [Network Functions](#network-functions) - 4 functions
  - [HTTP Functions](#http-functions) - 1 function
  - [Cryptographic Functions](#cryptographic-functions) - 8 functions
  - [Lodash Functions](#lodash-functions-via-qlo) - 20 functions + full library
  - [Date-fns Functions](#date-fns-functions-via-qdatefns) - full library
- [Usage in YAML Interpolation](#usage-in-yaml-interpolation)
- [Function Categories Summary](#function-categories-summary)

## Available Libraries
- **Q.lo** - Lodash library functions ([Lodash Documentation](https://lodash.com/docs/4.17.21))
- **Q.dateFns** - date-fns library functions ([date-fns Documentation](https://date-fns.org/docs/Getting-Started))

## Function Categories

### Text Processing Functions

**Q.appendText(...items)**
- Appends multiple text items together
- Signature: `Q.appendText(...items: (string | number | boolean | null | undefined)[]): string`
- Example: `Q.appendText("Hello", " ", "World")` → `"Hello World"`

**Q.asTable(data, config?)**
- Renders data as an ASCII table
- Signature: `Q.asTable(data: (string | number)[][], config?: TableUserConfig): string`
- Example: `Q.asTable([["Name", "Age"], ["Alice", "30"]])`

**Q.asText(value)**
- Converts any value to its string representation
- Signature: `Q.asText(value: number | string | boolean | null | undefined): string`
- Example: `Q.asText(123)` → `"123"`

**Q.byteSize(text)**
- Calculates the byte size of a string
- Signature: `Q.byteSize(str: string): number`
- Example: `Q.byteSize("Hello")` → `5`

**Q.defang(text)**
- Defangs URLs and IP addresses to prevent accidental clicks
- Signature: `Q.defang(text: string): string`
- Example: `Q.defang("https://example.com")` → `"hxxps[://]example[.]com"`

**Q.escapeHTML(text)**
- Escapes HTML special characters
- Signature: `Q.escapeHTML(str: string): string`
- Example: `Q.escapeHTML("<p>Hello</p>")` → `"&lt;p&gt;Hello&lt;/p&gt;"`

**Q.escapeOnce(text)**
- Escapes HTML without changing existing escaped entities
- Signature: `Q.escapeOnce(text: string): string`
- Example: `Q.escapeOnce("&amp; <script>")` → `"&amp; &lt;script&gt;"`

**Q.htmlToText(html, options?)**
- Converts HTML to plain text
- Signature: `Q.htmlToText(html: string, options?: HtmlToTextOptions): string`
- Example: `Q.htmlToText("<p>Hello <b>World</b></p>")` → `"Hello World"`

**Q.levenshteinDistance(str1, str2)**
- Calculates edit distance between two strings
- Signature: `Q.levenshteinDistance(str1: string, str2: string): number`
- Example: `Q.levenshteinDistance("kitten", "sitting")` → `3`

**Q.markdownToHTML(markdown)**
- Converts Markdown to HTML
- Signature: `Q.markdownToHTML(markdown: string): string`
- Example: `Q.markdownToHTML("# Hello")` → `"<h1>Hello</h1>"`

**Q.newLineToBR(text)**
- Converts newlines to HTML break tags
- Signature: `Q.newLineToBR(str: string): string`
- Example: `Q.newLineToBR("Hello\nWorld")` → `"Hello<br>World"`

**Q.pluralize(count, singular, plural?)**
- Returns singular or plural form based on count
- Signature: `Q.pluralize(counter: number, singular: string, plural?: string): string`
- Example: `Q.pluralize(1, "item")` → `"item"`, `Q.pluralize(2, "item")` → `"items"`

**Q.stripHTML(text)**
- Removes HTML tags from text
- Signature: `Q.stripHTML(html: string): string`
- Example: `Q.stripHTML("<p>Hello</p>")` → `"Hello"`

**Q.stripNewLines(text)**
- Removes newline characters from text
- Signature: `Q.stripNewLines(text: string): string`
- Example: `Q.stripNewLines("Hello\nWorld")` → `"HelloWorld"`

**Q.stripCodeFence(text)**
- Removes the outermost markdown code fence (triple backticks) from a string
- Commonly used to extract code from LLM-generated responses
- Signature: `Q.stripCodeFence(text: string): string`
- Example: `Q.stripCodeFence("```json\n{\"key\": \"value\"}\n```")` → `"{\"key\": \"value\"}"`

**Q.unescapeHTML(text)**
- Unescapes HTML entities
- Signature: `Q.unescapeHTML(str: string): string`
- Example: `Q.unescapeHTML("&lt;p&gt;Hello&lt;/p&gt;")` → `"<p>Hello</p>"`

**Q.dedent(text)**
- Removes indentation from multi-line strings while preserving relative indentation
- Useful for writing clean multi-line template literals in indented code
- Signature: `Q.dedent(text: string): string`
- Example: `Q.dedent("    Line 1\n    Line 2\n      Indented")` → `"Line 1\nLine 2\n  Indented"`

### Encoding Functions

**Q.toBase64(data)**
- Encodes data to Base64
- Signature: `Q.toBase64(input: string | Uint8Array | ArrayBuffer): string`
- Example: `Q.toBase64("Hello")` → `"SGVsbG8="`

**Q.toBase64URL(data)**
- Encodes data to Base64URL (URL-safe)
- Signature: `Q.toBase64URL(input: string | Uint8Array | ArrayBuffer): string`
- Example: `Q.toBase64URL("Hello")` → `"SGVsbG8"`

**Q.toURIEncode(text)**
- URL-encodes a string
- Signature: `Q.toURIEncode(input: string): string`
- Example: `Q.toURIEncode("Hello World!")` → `"Hello%20World%21"`

### Decoding Functions

**Q.fromBase64AsText(base64String)**
- Decodes Base64 to text
- Signature: `Q.fromBase64AsText(input: string): string`
- Example: `Q.fromBase64AsText("SGVsbG8=")` → `"Hello"`

**Q.fromBase64AsBinary(base64String)**
- Decodes Base64 to binary data
- Signature: `Q.fromBase64AsBinary(input: string): Uint8Array`
- Example: `Q.fromBase64AsBinary("SGVsbG8=")`

**Q.fromBase64URLAsText(base64URLString)**
- Decodes Base64URL to text
- Signature: `Q.fromBase64URLAsText(input: string): string`
- Example: `Q.fromBase64URLAsText("SGVsbG8")` → `"Hello"`

**Q.fromBase64URLAsBinary(base64URLString)**
- Decodes Base64URL to binary data
- Signature: `Q.fromBase64URLAsBinary(input: string): Uint8Array`
- Example: `Q.fromBase64URLAsBinary("SGVsbG8")`

**Q.fromURIEncode(uriEncodedString)**
- Decodes URL-encoded string
- Signature: `Q.fromURIEncode(input: string): string`
- Example: `Q.fromURIEncode("Hello%20World%21")` → `"Hello World!"`

### Data Format Functions

**Q.parseCSV(csvString, options?)**
- Parses CSV string to array of arrays
- Signature: `Q.parseCSV(csvString: string, options?: Partial<ParseOptions>): Record<string, string>[] | string[][]`
- Example: `Q.parseCSV("name,age\nAlice,30")` → `[["name", "age"], ["Alice", "30"]]`

**Q.parseCSVToObject(csvString, options?)**
- Parses CSV string to array of objects
- Signature: `Q.parseCSVToObject(csvString: string, options?: Partial<ParseOptions>): Record<string, string>[]`
- Example: `Q.parseCSVToObject("name,age\nAlice,30")` → `[{name: "Alice", age: "30"}]`

**Q.parseJSON(jsonString)**
- Parses JSON string to object
- Signature: `Q.parseJSON(jsonString: string): unknown`
- Example: `Q.parseJSON('{"name": "Alice"}')` → `{name: "Alice"}`

**Q.parseXML(xmlString, options?)**
- Parses XML string to object
- Signature: `Q.parseXML(xmlString: string, options?: parse_options): Record<string, unknown>`
- Example: `Q.parseXML("<root><name>Alice</name></root>")` → `{root: {name: "Alice"}}`

**Q.parseYAML(yamlString, options?)**
- Parses YAML string to object
- Signature: `Q.parseYAML(yamlString: string, options?: ParseOptions): unknown`
- Example: `Q.parseYAML("name: Alice\nage: 30")` → `{name: "Alice", age: 30}`

**Q.toCSV(data, options?)**
- Converts data to CSV string
- Signature: `Q.toCSV(data: Record<string, unknown>[] | unknown[][], options?: StringifyOptions): string`
- Example: `Q.toCSV([{name: "Alice", age: 30}])` → `"name,age\r\nAlice,30\r\n"`

**Q.toJSON(value, space?)**
- Converts value to JSON string
- Signature: `Q.toJSON(value: unknown, space?: number | string): string`
- Example: `Q.toJSON({name: "Alice"})` → `'{"name":"Alice"}'`

**Q.toXML(obj, options?)**
- Converts object to XML string
- Signature: `Q.toXML(obj: Record<string, unknown>, options?: XMLOptions): string`
- Example: `Q.toXML({person: {name: "Alice"}})` → `"<person><name>Alice</name></person>"`

**Q.toYAML(value, options?)**
- Converts value to YAML string
- Signature: `Q.toYAML(value: unknown, options?: StringifyOptions): string`
- Example: `Q.toYAML({name: "Alice"})` → `"name: Alice"`

### Utility Functions

**Q.ifTrue(condition, trueValue, falseValue?)**
- Conditional value selection
- Signature: `Q.ifTrue<T, U>(condition: unknown, trueValue: T, falseValue?: U): T | U`
- Example: `Q.ifTrue(true, "Yes", "No")` → `"Yes"`

**Q.jsonPath(obj, path)**
- Evaluates JSONPath expression on object
- Signature: `Q.jsonPath(obj: object, path: string): unknown`
- Example: `Q.jsonPath(data, "$.store.book[*].title")` → `["Book1", "Book2"]`

**Q.uuid()**
- Generates a UUID v4
- Signature: `Q.uuid(): string`
- Example: `Q.uuid()` → `"123e4567-e89b-12d3-a456-426614174000"`

**Q.ulid()**
- Generates a ULID
- Signature: `Q.ulid(): string`
- Example: `Q.ulid()` → `"01HYFKMDF3HVJ4J3JZW8KXPVTY"`

### Date/Time Functions

**Q.currentDateTime()**
- Returns current date and time
- Signature: `Q.currentDateTime(): Date`
- Example: `Q.currentDateTime()`

**Q.now()**
- Returns current date and time
- Signature: `Q.now(): Date`
- Example: `Q.now()`

**Q.today()**
- Returns current date at midnight
- Signature: `Q.today(): Date`
- Example: `Q.today()`

### Array Functions

**Q.rotate(arr, steps?)**
- Rotates array elements
- Signature: `Q.rotate<T>(arr: T[], steps?: number): T[]`
- Example: `Q.rotate([1, 2, 3, 4, 5])` → `[5, 1, 2, 3, 4]`

### Network Functions

**Q.isIPAddress(ipAddress)**
- Checks if string is valid IP address (IPv4 or IPv6)
- Signature: `Q.isIPAddress(ip: string): boolean`
- Example: `Q.isIPAddress("192.168.1.1")` → `true`

**Q.isIPv4Address(ipAddress)**
- Checks if string is valid IPv4 address
- Signature: `Q.isIPv4Address(ip: string): boolean`
- Example: `Q.isIPv4Address("192.168.1.1")` → `true`

**Q.isIPv6Address(ipAddress)**
- Checks if string is valid IPv6 address
- Signature: `Q.isIPv6Address(ip: string): boolean`
- Example: `Q.isIPv6Address("2001:db8::1")` → `true`

**Q.isIPAddressInCIDR(ipAddress, cidr)**
- Checks if IP address is within CIDR range
- Signature: `Q.isIPAddressInCIDR(ipAddress: string, cidr: string): boolean`
- Example: `Q.isIPAddressInCIDR("192.168.1.100", "192.168.1.0/24")` → `true`

### HTTP Functions

**Q.isHTTPStatusInRange(statusCode, ranges)**
- Checks if HTTP status code is within specified ranges
- Signature: `Q.isHTTPStatusInRange(statusCode: number | string, ranges: Array<number | string>): boolean`
- Example: `Q.isHTTPStatusInRange(503, ["500-599"])` → `true`

### Cryptographic Functions

**Q.aesDecrypt(encryptedData, key)**
- Decrypts AES-256-CBC encrypted data
- Signature: `Q.aesDecrypt(encryptedData: string, key: string | Uint8Array): string`
- Example: `Q.aesDecrypt("iv:ciphertext", "32-byte-key")`

**Q.aesEncrypt(data, key, iv?)**
- Encrypts data using AES-256-CBC
- Signature: `Q.aesEncrypt(data: string | Uint8Array, key: string | Uint8Array, iv?: string | Uint8Array): string`
- Example: `Q.aesEncrypt("Hello", "32-byte-key")`

**Q.hash(hashAlgorithm, data, options?)**
- Generates hash for data
- Signature: `Q.hash(hashAlgorithm: HashAlgorithm, data: string, options?: HashOptions): string`
- Example: `Q.hash('SHA256', 'Hello, World!')`

**Q.hmac(hashAlgorithm, key, data, options?)**
- Generates HMAC for data
- Signature: `Q.hmac(hashAlgorithm: HashAlgorithm, key: string | Uint8Array, data: string, options?: HmacOptions): string`
- Example: `Q.hmac('SHA256', 'secret-key', 'Hello, World!')`

**Q.jwtSign(payload, secret, options?)**
- Signs a JSON Web Token
- Signature: `Q.jwtSign(payload: string | object | Uint8Array, secret: string | Uint8Array, options?: JwtSignOptions): string`
- Example: `Q.jwtSign({userId: 123}, "secret", {expiresIn: "1h"})`

**Q.jwtVerify(token, secret, options?)**
- Verifies a JWT and returns payload
- Signature: `Q.jwtVerify(token: string, secret: string | Uint8Array, options?: JwtVerifyOptions): jwt.JwtPayload | string`
- Example: `Q.jwtVerify(token, "secret", {algorithms: ["HS256"]})`

**Q.randomBytes(size)**
- Generates cryptographically strong random bytes
- Signature: `Q.randomBytes(size: number): Uint8Array`
- Example: `Q.randomBytes(16)`

**Q.timingSafeEqual(a, b)**
- Compares two buffers or strings in constant time to prevent timing attacks
- Signature: `Q.timingSafeEqual(a: string | Uint8Array, b: string | Uint8Array): boolean`
- Example: `Q.timingSafeEqual("secret", "secret")` → `true`

### Lodash Functions (via Q.lo)

All Lodash functions are available through `Q.lo`. See the [Lodash Documentation](https://lodash.com/docs/4.17.21) for the complete API reference.

Common utility functions are also directly available:

**Type Checking Functions:**
- `Q.isEmpty(value)` - Checks if value is empty
- `Q.isObject(value)` - Checks if value is an object
- `Q.isString(value)` - Checks if value is a string
- `Q.isNumber(value)` - Checks if value is a number
- `Q.isBoolean(value)` - Checks if value is a boolean
- `Q.isArray(value)` - Checks if value is an array
- `Q.isDate(value)` - Checks if value is a Date object
- `Q.isRegExp(value)` - Checks if value is a RegExp
- `Q.isNil(value)` - Checks if value is null or undefined
- `Q.isEqual(value, other)` - Performs deep equality comparison
- `Q.isUndefined(value)` - Checks if value is undefined
- `Q.isNull(value)` - Checks if value is null
- `Q.isFinite(value)` - Checks if value is finite number
- `Q.isInteger(value)` - Checks if value is an integer
- `Q.isSafeInteger(value)` - Checks if value is a safe integer
- `Q.isNaN(value)` - Checks if value is NaN

**Conversion Functions:**
- `Q.toString(value)` - Converts value to string
- `Q.toNumber(value)` - Converts value to number
- `Q.toInteger(value)` - Converts value to integer
- `Q.toSafeInteger(value)` - Converts value to safe integer

### Date-fns Functions (via Q.dateFns)

All date-fns functions are available through `Q.dateFns`. See the [date-fns Documentation](https://date-fns.org/docs/Getting-Started) for the complete API reference.

Examples:
- `Q.dateFns.format(date, 'yyyy-MM-dd')` - Format date
- `Q.dateFns.addDays(date, 7)` - Add days to date
- `Q.dateFns.subDays(date, 7)` - Subtract days from date
- `Q.dateFns.isAfter(date1, date2)` - Check if date1 is after date2
- `Q.dateFns.isBefore(date1, date2)` - Check if date1 is before date2
- `Q.dateFns.parseISO(dateString)` - Parse ISO date string

## Usage in YAML Interpolation

All functions are designed to be used in YAML interpolation contexts using the `${{ }}` syntax:

```yaml
# String manipulation
title: ${{ Q.appendText("Hello", " ", "World") }}
escaped: ${{ Q.escapeHTML("<script>alert('xss')</script>") }}

# Data conversion
json_data: ${{ Q.toJSON({name: "Alice", age: 30}) }}
csv_data: ${{ Q.toCSV([{name: "Alice", age: 30}]) }}

# Conditional logic
status: ${{ Q.ifTrue(user.isActive, "Active", "Inactive") }}

# Date formatting
current_date: ${{ Q.dateFns.format(Q.now(), 'yyyy-MM-dd') }}

# Array operations
rotated: ${{ Q.rotate([1, 2, 3, 4, 5], 2) }}

# Cryptographic operations
token: ${{ Q.jwtSign({userId: user.id}, "secret", {expiresIn: "1h"}) }}
hash: ${{ Q.hash('SHA256', 'sensitive-data') }}

# Network validation
is_valid_ip: ${{ Q.isIPAddress(trigger.request.meta.ipAddress) }}
in_range: ${{ Q.isIPAddressInCIDR(trigger.request.meta.ipAddress, "192.168.1.0/24") }}
```

## Function Categories Summary

- **Text Processing**: 17 functions for string manipulation, HTML escaping, formatting
- **Encoding/Decoding**: 8 functions for Base64, Base64URL, URI encoding/decoding
- **Data Formats**: 8 functions for JSON, XML, YAML, CSV parsing and generation
- **Date/Time**: 3 functions + full date-fns library access
- **Array**: 1 function + full Lodash array functions
- **Network**: 4 functions for IP address validation and CIDR checking
- **HTTP**: 1 function for status code validation
- **Cryptography**: 8 functions for hashing, HMAC, JWT, AES encryption, timing-safe comparison
- **Utilities**: 4 functions for conditionals, UUIDs, JSONPath
- **Type Checking**: 16 functions for runtime type validation
- **Lodash**: Full Lodash library access via Q.lo
- **date-fns**: Full date-fns library access via Q.dateFns

Total: 70+ functions with extensive library support for comprehensive data processing and manipulation.