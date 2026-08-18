# AI Actor Examples

Complete examples for building AiActor configurations.

## Table of Contents
1. [Generate System Prompt](#generate-system-prompt)
2. [Generate SERP Queries with Structured Output](#generate-serp-queries-with-structured-output)
3. [Gmail Filter Query Generator](#gmail-filter-query-generator)

---

## Generate System Prompt

Demonstrates using an AI model to refine and enhance user prompts with expert prompt engineering techniques.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01jm8ygng9vyp7c6r6c4hk9rqr:
    name: Generate System Prompt
    type: AiActor
    msgVar: generate_system_prompt
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: The AI actor will allow to use an AI model to generate a response.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        model: claude-opus-4-5
        maxRetry: 3
        prompt: >-
          Please write a LLM prompt using the users's initial prompt as the
          starting point. Only return the final prompt, don't include any
          explanations or any other text.


          <initial-prompt>

          ${{ msg.prompt_writer.body.prompt }}

          </initial-prompt>
        systemPrompt: >-
          You are an expert prompt engineer specialized in refining and
          enhancing any prompt I provide. Every prompt that I give you is purely
          for prompt enhancement, not to action. Your single goal is to maximize
          the clarity, specificity, and creativity of my prompt to ensure the
          LLM produces the best and most accurate results when entered into the
          LLM. When I input a prompt, improve it using the following techniques:


          1) Clarify vague instructions.

          2) Add context and examples if necessary.

          3) Break down complex tasks into clear, actionable steps.

          4) Include formatting or directives (e.g., tables, bullets, specific
          tones) to suit the output I want.

          5) Identify potential gaps in the prompt and fill them to ensure
          completeness.


          For example, if I ask for 'Write a blog about AI,' you would refine it
          to: 'Write a 1,000-word blog post in a professional yet engaging tone
          about the latest advancements in AI. Focus on how large language
          models like ChatGPT are impacting industries such as healthcare,
          education, and customer service. Include at least three specific
          examples, and conclude with predictions for the next five years.'
        emitInput: true
    continueOnError: false
    id: ACTR01jm8ygng9vyp7c6r6c4hk9rqr
    position:
      x: -4419.777579950832
      'y': 590.5529255580108
    edges: {}
```

**Key Features:**
- Uses `claude-opus-4-5` model for high-quality prompt refinement
- References upstream actor output via `msg.prompt_writer.body.prompt`
- Includes detailed system prompt with prompt engineering best practices
- Sets `emitInput: true` to include input messages in output for debugging
- Uses `maxRetry: 3` for resilience

**Sample Response:**
```json
{
  "response": "Write a comprehensive 1,500-word technical blog post...",
  "meta": {
    "input": [...],
    "model": "claude-opus-4-5",
    "usage": {
      "promptTokens": 450,
      "completionTokens": 380,
      "totalTokens": 830
    },
    "fromCache": false
  }
}
```

---

## Generate SERP Queries with Structured Output

Demonstrates using `outputSchema` to get structured JSON output with a nested array of objects. Uses dynamic date injection and input-driven limits.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kcwyn16ssy0zkr9d0x8p9z2m:
    name: Generate SERP Queries
    type: AiActor
    msgVar: generate_serp_queries
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: The AI actor will allow to use an AI model to generate a response.
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        model: claude-haiku-4-5
        prompt: >+
          Given the following prompt from the user, generate a list of SERP
          queries to research the topic. Return a maximum of ${{
          inputs.numQueries }} queries, but feel free to return less if the
          original prompt is clear. Make sure each query is unique and not
          similar to each other: <prompt>${{inputs.query }}</prompt>


        systemPrompt: >
          You are an expert researcher. Today is ${{new Date().toISOString()}}.
          Follow these instructions when responding:
            - You may be asked to research subjects that is after your knowledge cutoff, assume the user is right when presented with news.
            - The user is a highly experienced analyst, no need to simplify it, be as detailed as possible and make sure your response is correct.
            - Be highly organized.
            - Suggest solutions that I didn't think about.
            - Be proactive and anticipate my needs.
            - Treat me as an expert in all subject matter.
            - Mistakes erode my trust, so be accurate and thorough.
            - Provide detailed explanations, I'm comfortable with lots of detail.
            - Value good arguments over authorities, the source is irrelevant.
            - Consider new technologies and contrarian ideas, not just the conventional wisdom.
            - You may use high levels of speculation or prediction, just flag it for me.
        outputSchema:
          title: Search Queries Schema
          description: Follow up questions to clarify the research direction
          type: object
          properties:
            queries:
              type: array
              description: List of SERP queries, max of ${{ inputs.numQueries }}
              items:
                type: object
                properties:
                  query:
                    type: string
                    description: The SERP query
                  researchGoal:
                    type: string
                    description: >-
                      First talk about the goal of the research that this query
                      is meant to accomplish, then go deeper into how to advance
                      the research once the results are found, mention
                      additional research directions. Be as specific as
                      possible, especially for additional research directions.
                required:
                  - query
                  - researchGoal
          required:
            - queries
        emitInput: true
      inputs:
        query: Elon Musk
        numQueries: 5
    continueOnError: false
    id: ACTR01kcwyn16ssy0zkr9d0x8p9z2m
    position:
      x: -806.1758931854508
      'y': 2238.360555166338
    edges: {}
```

**Key Features:**
- Uses `claude-haiku-4-5` for fast, cost-effective generation
- Demonstrates `outputSchema` for structured JSON output with nested objects
- Injects dynamic date via `${{new Date().toISOString()}}` in system prompt
- Uses `inputs.numQueries` to control output size dynamically
- Detailed system prompt establishes expert researcher persona
- Sets `emitInput: true` for debugging

**Sample Response:**
```json
{
  "response": {
    "queries": [
      {
        "query": "Elon Musk SpaceX Starship 2024 launch schedule",
        "researchGoal": "Understand current SpaceX development timeline..."
      },
      {
        "query": "Elon Musk Tesla AI robotics Optimus progress",
        "researchGoal": "Investigate Tesla's humanoid robot development..."
      }
    ]
  },
  "meta": {
    "model": "claude-haiku-4-5",
    "usage": {
      "promptTokens": 320,
      "completionTokens": 450,
      "totalTokens": 770
    },
    "fromCache": false
  }
}
```

---

## Gmail Filter Query Generator

Demonstrates using AI to convert natural language into domain-specific syntax (Gmail search queries). Features comprehensive system prompt with operator reference, input schema for UI generation, and low temperature for deterministic output.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kc0jfpxsssgznd6jbdztbprj:
    name: Gmail Filter Query Generator
    type: AiActor
    msgVar: gmail_filter_query_generator
    schemas:
      inputs:
        type: object
        properties:
          description:
            type: string
            ui:
              options: {}
              component: input
              order: 0
            title: Describe your search query
        required:
          - description
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: >-
      Generates Gmail search filter queries based on natural language
      requirements and specific criteria like sender, subject, attachments,
      keywords, and date ranges.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        description: Unread email received in the last 7 days
      options:
        model: claude-haiku-4-5
        systemPrompt: >-
          You are an expert at creating Gmail search filter queries. Your task
          is to generate valid Gmail search syntax based on natural language
          description of the user requirements.


          Gmail Search Operators:

          - from:email@example.com - emails from specific sender

          - to:email@example.com - emails to specific recipient

          - subject:keyword - search in subject line

          - has:attachment - emails with attachments

          - filename:pdf - specific file type attachments

          - label:labelname - emails with specific label

          - is:unread, is:read, is:starred - email status

          - in:inbox, in:trash, in:spam - location

          - after:YYYY/MM/DD, before:YYYY/MM/DD - date filters

          - newer_than:7d, older_than:2y - relative date (d=days, m=months,
          y=years)

          - larger:10M, smaller:5M - size filters

          - OR - combine conditions (must be uppercase)

          - AND - combine conditions (default, can be implicit)

          - NOT or - (minus) - exclude results

          - ( ) - group conditions

          - "exact phrase" - search for exact phrase


          Examples:

          - from:boss@company.com subject:urgent

          - has:attachment filename:pdf newer_than:7d

          - (from:john OR from:jane) subject:"project update"

          - from:newsletter@company.com -subject:unsubscribe

          - subject:(meeting OR conference) after:2024/01/01
        prompt: >-
          Generate a Gmail search filter query based on these requirements: ${{
          inputs.description }}


          Generate ONLY the Gmail search query string without any explanation.
          The query should:

          1. Use proper Gmail search operators

          2. Combine conditions appropriately with AND/OR/NOT

          3. Use parentheses for complex conditions

          4. Be a valid, working Gmail search query

          5. Return only the query string, nothing else
        jsonMode: true
        outputSchema:
          type: object
          properties:
            query:
              type: string
              description: The Gmail search filter query
            explanation:
              type: string
              description: Brief explanation of what the query does
          required:
            - query
            - explanation
        maxRetries: 2
        temperature: 0.3
    continueOnError: false
    id: ACTR01kc0jfpxsssgznd6jbdztbprj
    position:
      x: -7981.06343940706
      'y': -558.0400200927904
    edges: {}
```

**Key Features:**
- Uses `claude-haiku-4-5` for fast, cost-effective generation
- Comprehensive system prompt with Gmail search operator reference and examples
- Input schema with `ui` configuration for form generation
- Uses both `jsonMode: true` and `outputSchema` for structured output
- Low `temperature: 0.3` for deterministic, reliable query generation
- `maxRetries: 2` for resilience

**Sample Response:**
```json
{
  "response": {
    "query": "is:unread newer_than:7d",
    "explanation": "Finds all unread emails received within the last 7 days"
  },
  "meta": {
    "model": "claude-haiku-4-5",
    "usage": {
      "promptTokens": 520,
      "completionTokens": 45,
      "totalTokens": 565
    },
    "fromCache": false
  }
}
```

---
