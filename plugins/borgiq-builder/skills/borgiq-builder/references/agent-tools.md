# Agent Tools

How to give AiAgentActor, AgentHarnessActor and McpServerActor BorgIQ actors as tools (`aiAgentToolActorIds`,
`${{aiInput}}`, tool schemas), and how to give the two agents MCP servers (`mcpServers`). Read it whenever an agent or
an MCP server needs tools.

## Rules

- List **every** tool actor's id in `configuration.aiAgentToolActorIds`, a sibling of `inputs` and `options` (never
  inside `options`). Order does not matter.
- A tool actor has `edges: {}`. Its result goes back to its host only; the editor draws it inside the host.
- The tool's name is its `msgVar`. The calling model picks tools by `msgVar`, `description` and input schema: write
  them for that model, and keep secret hints out of them.
- Set each input the model fills to `${{aiInput}}`, and describe it in the tool actor's `schemas.inputs` (type,
  description, `required`). The model's tool schema keeps only the `${{aiInput}}` properties; fixed inputs,
  connections and secrets never reach it.
- `continueOnError` does not change what the host sees: a failed tool returns its error message to the agent (or MCP
  client), which can react to it. With `continueOnError: false` the tool's own job also ends in error state.
- An AiAgentActor, AgentHarnessActor, DeprecatedAiAgent or McpServerActor cannot be a tool. The editor also refuses
  triggers, CommentActor, routers, interface actors and response actors, and attaches at most 12 tools to one host.
- On an AiAgentActor, a tool `msgVar` must not be a built-in tool name ([reserved names](ai-agent-actor.md#built-in-tools)).
  On an McpServerActor, duplicate `msgVar`s fail canvas validation.

## Tool input by actor type

| Tool actor | Put `${{aiInput}}` in |
|---|---|
| HttpRequestActor, DenoActor, PythonActor, … | `configuration.inputs.<param>`; options read `${{ inputs.<param> }}` |
| CallFlowActor: a sub-flow, e.g. a specialised sub-agent | `configuration.options.payload.<param>`, not `inputs` |

## Example: an agent with one HTTP tool

```yaml
ACTR01m3snakp7ymqm59erz27xbqgv:
  type: AiAgentActor
  # … name, msgVar, ports as in ai-agent-actor.md
  configuration:
    options:
      model: claude-sonnet-5
      systemPrompt: |
        Use web_search to find sources. Save findings as markdown files.
      prompt: ${{ inputs.question }}
    aiAgentToolActorIds:
      - ACTR01m3snakyskc7vxx8hwsqfg1br   # web_search
ACTR01m3snakyskc7vxx8hwsqfg1br:
  type: HttpRequestActor
  version: 1
  name: Web Search
  msgVar: web_search                   # the tool name
  description: Search the web and return the top results
  isActive: true
  continueOnError: false
  enableLTM: false
  enableSTM: false
  sourcePorts:
    - id: SPRTdefault
  configuration:
    inputs:
      query: ${{aiInput}}
      limit: ${{aiInput}}
    options:
      url: https://api.exa.ai/search
      method: POST
      headers:
        Content-Type: application/json
      body:
        query: ${{ inputs.query }}
        numResults: ${{ inputs.limit || 10 }}
      auth: ${{ connection.auth }}
    connection:
      key: exa-api
  schemas:
    inputs:
      type: object
      properties:
        query:
          type: string
          description: The search query
        limit:
          type: integer
          description: Maximum number of results
          default: 10
      required:
        - query
  id: ACTR01m3snakyskc7vxx8hwsqfg1br
  position:
    x: 0
    'y': 100
  edges: {}
```

A CallFlowActor tool puts the parameters in the payload:

```yaml
configuration:
  options:
    workspaceSlug: my-workspace
    canvasSlug: research-agent-flow
    callableTriggerActorId: ACTR01m3snam7d4edr3xvygm994v5j
    payload:
      topic: ${{aiInput}}
    waitForResponse: true
    timeoutInSeconds: 120
```

## MCP servers (`mcpServers`)

Agents also take tools from MCP servers, listed in `options.mcpServers`:

| `type` | AiAgentActor | AgentHarnessActor | Fields |
|---|---|---|---|
| `http`: a remote server, proxied through BorgIQ | yes; the type when `type` is omitted | yes | `name`, `url`; optional `auth` (usually `${{ credentials.<key> }}`); AiAgentActor also `transport`, only `streamable-http` |
| `borgiq`: an McpServerActor inside BorgIQ | yes | yes | `name`, `actorId`; optional `canvasSlug` and `workspaceSlug` (default: this actor's). No auth: the session is scoped to the servers listed |
| `stdio`: a subprocess in the sandbox | no | yes, except with `harness: pi`; the type when `type` is omitted | `name`, `command`; optional `args`, `env` |

```yaml
options:
  mcpServers:
    - type: http
      name: linear
      url: https://mcp.linear.app/mcp
      auth: ${{ credentials.linearMcp }}
    - type: borgiq
      name: support-tools
      actorId: ACTR01m3snamg2j1w1gamsvnb73w8v
      canvasSlug: support-desk          # optional
    - type: stdio                       # AgentHarnessActor only
      name: filesystem-server
      command: npx
      args: ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
```

- A `borgiq` entry must say `type: borgiq`. Give every entry a `type`: an untyped one is `http` on an AiAgentActor and
  `stdio` on an AgentHarnessActor.
- `name` is letters, numbers, hyphens and underscores, unique in the list.
- `http` auth resolves server-side on every request, so an OAuth connection refreshes mid-session; neither the upstream
  URL nor the credentials reach the agent's runtime or sandbox. Literal auth values and stdio `env` are encrypted in
  transit.
- MCP protocol versions (`2026-07-28`, or the older `initialize` handshake) are negotiated automatically.
- Internal MCP calls are depth-limited: an agent and an MCP server that call each other end with a tool error.
- To reuse an [McpServerActor](mcp-server-actor.md) inside BorgIQ, use a `type: borgiq` entry rather than its public
  endpoint and a token.
