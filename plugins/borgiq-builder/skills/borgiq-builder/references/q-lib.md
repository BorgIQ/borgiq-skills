# Q-lib Function Reference

`Q` is the helper object available in every `${{ }}` expression: text, encoding, data formats, dates, network, HTTP and
crypto helpers, plus Lodash (`Q.lo`) and date-fns (`Q.dateFns`). Read it to find a helper and its signature.

## Contents

- [Text](#text)
- [Encoding and decoding](#encoding-and-decoding)
- [Data formats](#data-formats)
- [Utility, date and array](#utility-date-and-array)
- [Network and HTTP](#network-and-http)
- [Cryptography](#cryptography)
- [Lodash and date-fns](#lodash-and-date-fns)
- [Usage in YAML](#usage-in-yaml)

## Text

| Function | Returns | Example |
|---|---|---|
| `appendText(...items: (string\|number\|boolean\|null\|undefined)[])` | the items joined | `Q.appendText("Hello", " ", "World")` → `"Hello World"` |
| `asTable(data: (string\|number)[][], config?: TableUserConfig)` | an ASCII table | `Q.asTable([["Name", "Age"], ["Alice", "30"]])` |
| `asText(value: number\|string\|boolean\|null\|undefined)` | the value as a string | `Q.asText(123)` → `"123"` |
| `byteSize(str)` | the string's byte size | `Q.byteSize("Hello")` → `5` |
| `dedent(text)` | text without common indentation; relative indentation kept | `Q.dedent("    Line 1\n      Indented")` → `"Line 1\n  Indented"` |
| `defang(text)` | URLs and IPs made unclickable | `Q.defang("https://example.com")` → `"hxxps[://]example[.]com"` |
| `escapeHTML(str)` | HTML-escaped text | `Q.escapeHTML("<p>Hello</p>")` → `"&lt;p&gt;Hello&lt;/p&gt;"` |
| `escapeOnce(text)` | escaped text, existing entities kept | `Q.escapeOnce("&amp; <script>")` → `"&amp; &lt;script&gt;"` |
| `htmlToText(html, options?: HtmlToTextOptions)` | plain text | `Q.htmlToText("<p>Hello <b>World</b></p>")` → `"Hello World"` |
| `levenshteinDistance(str1, str2)` | the edit distance | `Q.levenshteinDistance("kitten", "sitting")` → `3` |
| `markdownToHTML(markdown)` | HTML | `Q.markdownToHTML("# Hello")` → `"<h1>Hello</h1>"` |
| `newLineToBR(str)` | newlines as `<br/>` | `Q.newLineToBR("Hello\nWorld")` → `"Hello<br/>World"` |
| `pluralize(counter, singular, plural?)` | the form for `counter` | `Q.pluralize(1, "item")` → `"item"`; `Q.pluralize(2, "item")` → `"items"` |
| `stripCodeFence(text)` | text without its outermost ```` ``` ```` fence, e.g. code from an LLM answer | `Q.stripCodeFence("```json\n{\"key\": \"value\"}\n```")` → `"{\"key\": \"value\"}"` |
| `stripHTML(html)` | text without tags | `Q.stripHTML("<p>Hello</p>")` → `"Hello"` |
| `stripNewLines(text)` | text without newlines | `Q.stripNewLines("Hello\nWorld")` → `"HelloWorld"` |
| `unescapeHTML(str)` | unescaped text | `Q.unescapeHTML("&lt;p&gt;Hello&lt;/p&gt;")` → `"<p>Hello</p>"` |

## Encoding and decoding

Encoders take `string | Uint8Array | ArrayBuffer`; `toURIEncode` and the decoders take a string.

| Function | Returns | Example |
|---|---|---|
| `toBase64(input)` | Base64 | `Q.toBase64("Hello")` → `"SGVsbG8="` |
| `toBase64URL(input)` | URL-safe Base64 | `Q.toBase64URL("Hello")` → `"SGVsbG8"` |
| `toURIEncode(input)` | `encodeURIComponent` output | `Q.toURIEncode("Hello World!")` → `"Hello%20World!"` |
| `fromBase64AsText(input)` | text | `Q.fromBase64AsText("SGVsbG8=")` → `"Hello"` |
| `fromBase64AsBinary(input)` | `Uint8Array` | `Q.fromBase64AsBinary("SGVsbG8=")` |
| `fromBase64URLAsText(input)` | text | `Q.fromBase64URLAsText("SGVsbG8")` → `"Hello"` |
| `fromBase64URLAsBinary(input)` | `Uint8Array` | `Q.fromBase64URLAsBinary("SGVsbG8")` |
| `fromURIEncode(input)` | decoded text | `Q.fromURIEncode("Hello%20World%21")` → `"Hello World!"` |

## Data formats

| Function | Returns | Example |
|---|---|---|
| `parseCSV(csvString, options?: Partial<ParseOptions>)` | `string[][]` or `Record<string, string>[]`, per options | `Q.parseCSV("name,age\nAlice,30")` → `[["name", "age"], ["Alice", "30"]]` |
| `parseCSVToObject(csvString, options?)` | `Record<string, string>[]` | `Q.parseCSVToObject("name,age\nAlice,30")` → `[{name: "Alice", age: "30"}]` |
| `parseJSON(jsonString)` | `unknown` | `Q.parseJSON('{"name": "Alice"}')` → `{name: "Alice"}` |
| `parseXML(xmlString, options?)` | `Record<string, unknown>` | `Q.parseXML("<root><name>Alice</name></root>")` → `{root: {name: "Alice"}}` |
| `parseYAML(yamlString, options?)` | `unknown` | `Q.parseYAML("name: Alice\nage: 30")` → `{name: "Alice", age: 30}` |
| `toCSV(data: Record<string, unknown>[] \| unknown[][], options?)` | a CSV string; an array of objects needs `options.columns`, or the call throws | `Q.toCSV([{name: "Alice", age: 30}], {columns: ["name", "age"]})` → `"name,age\r\nAlice,30\r\n"` |
| `toJSON(value, space?: number\|string)` | a JSON string | `Q.toJSON({name: "Alice"})` → `'{"name":"Alice"}'` |
| `toXML(obj, options?: XMLOptions)` | an XML string | `Q.toXML({person: {name: "Alice"}})` → `"<person><name>Alice</name></person>"` |
| `toYAML(value, options?)` | a YAML string | `Q.toYAML({name: "Alice"})` → `"name: Alice\n"` |

## Utility, date and array

| Function | Returns | Example |
|---|---|---|
| `ifTrue(condition, trueValue, falseValue?)` | `trueValue` when `condition` is truthy, else `falseValue` | `Q.ifTrue(true, "Yes", "No")` → `"Yes"` |
| `jsonPath(obj, path)` | the JSONPath result | `Q.jsonPath(data, "$.store.book[*].title")` → `["Book1", "Book2"]` |
| `uuid()` | a UUID v4 | `"123e4567-e89b-12d3-a456-426614174000"` |
| `ulid()` | a ULID | `"01HYFKMDF3HVJ4J3JZW8KXPVTY"` |
| `now()`, `currentDateTime()` | the current `Date` | `Q.now()` |
| `today()` | today at midnight, a `Date` | `Q.today()` |
| `rotate(arr, steps?)` | the array rotated | `Q.rotate([1, 2, 3, 4, 5])` → `[5, 1, 2, 3, 4]` |

## Network and HTTP

| Function | Returns | Example |
|---|---|---|
| `isIPAddress(ip)` | IPv4 or IPv6? | `Q.isIPAddress("192.168.1.1")` → `true` |
| `isIPv4Address(ip)` | IPv4? | `Q.isIPv4Address("192.168.1.1")` → `true` |
| `isIPv6Address(ip)` | IPv6? | `Q.isIPv6Address("2001:db8::1")` → `true` |
| `isIPAddressInCIDR(ipAddress, cidr)` | in the range? | `Q.isIPAddressInCIDR("192.168.1.100", "192.168.1.0/24")` → `true` |
| `isHTTPStatusInRange(statusCode: number\|string, ranges: (number\|string)[])` | in any range? | `Q.isHTTPStatusInRange(503, ["500-599"])` → `true` |

## Cryptography

| Function | Returns | Example |
|---|---|---|
| `aesEncrypt(data, key, iv?)` | AES-256-CBC ciphertext (`string`); inputs are `string \| Uint8Array` | `Q.aesEncrypt("Hello", "32-byte-key")` |
| `aesDecrypt(encryptedData: string, key)` | the plaintext | `Q.aesDecrypt("iv:ciphertext", "32-byte-key")` |
| `hash(hashAlgorithm, data: string, options?)` | the hash | `Q.hash('SHA256', 'Hello, World!')` |
| `hmac(hashAlgorithm, key, data: string, options?)` | the HMAC | `Q.hmac('SHA256', 'secret-key', 'Hello, World!')` |
| `jwtSign(payload: string\|object\|Uint8Array, secret, options?)` | a JWT | `Q.jwtSign({userId: 123}, "secret", {expiresIn: "1h"})` |
| `jwtVerify(token, secret, options?)` | the payload (`JwtPayload \| string`) | `Q.jwtVerify(token, "secret", {algorithms: ["HS256"]})` |
| `randomBytes(size)` | cryptographically strong `Uint8Array` | `Q.randomBytes(16)` |
| `timingSafeEqual(a, b)` | a constant-time equality check | `Q.timingSafeEqual("secret", "secret")` → `true` |

## Lodash and date-fns

- **`Q.lo`** is the whole [Lodash](https://lodash.com/docs/4.17.21) library, e.g. `Q.lo.compact(list)`. These are also
  on `Q` directly: `isEmpty`, `isObject`, `isString`, `isNumber`, `isBoolean`, `isArray`, `isDate`, `isRegExp`, `isNil`
  (null or undefined), `isEqual` (deep), `isUndefined`, `isNull`, `isFinite`, `isInteger`, `isSafeInteger`, `isNaN`,
  `toString`, `toNumber`, `toInteger`, `toSafeInteger`.
- **`Q.dateFns`** is the whole [date-fns](https://date-fns.org/docs/Getting-Started) library:
  `Q.dateFns.format(date, 'yyyy-MM-dd')`, `addDays(date, 7)`, `subDays(date, 7)`, `isAfter(date1, date2)`,
  `isBefore(date1, date2)`, `parseISO(dateString)`.

## Usage in YAML

Quote a value that contains `: ` (a plain YAML value cannot):

```yaml
title: ${{ Q.appendText("Hello", " ", "World") }}
json_data: '${{ Q.toJSON({name: "Alice", age: 30}) }}'
status: ${{ Q.ifTrue(inputs.user.isActive, "Active", "Inactive") }}
current_date: ${{ Q.dateFns.format(Q.now(), 'yyyy-MM-dd') }}
token: '${{ Q.jwtSign({userId: inputs.user.id}, "secret", {expiresIn: "1h"}) }}'
is_valid_ip: ${{ Q.isIPAddress(trigger.request.meta.ipAddress) }}
```
