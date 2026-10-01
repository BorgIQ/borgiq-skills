# actorSchemas/task/aiAgent

Generated from the platform's runtime types. Do not edit.

AiAgentActor options and results: built-in and filterable tools, MCP servers, sessions, compaction and the Done port.

See also: [canvas](../../canvas.md), [schemas/file](../../schemas/file.md), [schemas/connection](../../schemas/connection.md), [ai/modelRef](../../ai/modelRef.md), [ai/index](../../ai/index.md).

## actorSchemas/task/aiAgent

**Source:** `actorSchemas/task/aiAgent.ts`

```typescript
import { z } from 'zod';

import { BIQActorType } from '../../canvas.js';
import { BIQFileSchema, BIQJsonSchema, BIQJsonSchemaType, McpAuthDataSchema } from '../../schemas/index.js';
import { AiModelRefSchema, AiAgentModels, AiAgentModelsByProvider, AI_AGENT_THINKING_LEVELS, AiAgentThinkingLevelSchema, buildAiModelSuggestionUiOptions, parseAiModelRef } from '../../ai/index.js';
import { DeprecatedAiAgentStatusPortResultSchema } from './deprecatedAiAgent.js';

/** The ai agent done source port id */
export const AI_AGENT_DONE_SOURCE_PORT_ID = 'SPRTdone000';

/** The opt-in Code Execution tool's model-facing name. Anthropic tool names must match
 * ^[a-zA-Z0-9_-]{1,64}$ (no spaces), so the wire-level name is `code_execution`; human-facing
 * labels say "Code Execution". Registered — and therefore reserved — only when
 * `enableCodeExecution` is set; see AI_AGENT_BUILTIN_TOOLS. */
export const AI_AGENT_CODE_EXECUTION_TOOL_NAME = 'code_execution';

/** The always-on built-in tools, and the only names `allowedTools`/`disallowedTools` control.
 * `code_execution` is deliberately absent: it is governed solely by `enableCodeExecution`, and the
 * segment host never consults the filters for it, so listing it either way does nothing. */
export const AI_AGENT_FILTERABLE_TOOLS = [
  'read', 'write', 'edit', 'bash', 'grep', 'find', 'ls',
] as const;

/** One-line descriptions of the filterable built-ins, shown as the option labels on the
 * allowed/disallowed tool pickers so an author choosing between them does not have to guess. */
export const AI_AGENT_FILTERABLE_TOOL_LABELS: Record<typeof AI_AGENT_FILTERABLE_TOOLS[number], string> = {
  read: 'read — read a file from the workspace',
  write: 'write — create or overwrite a workspace file',
  edit: 'edit — modify part of an existing file',
  bash: 'bash — run built-in shell commands (no external programs)',
  grep: 'grep — search file contents',
  find: 'find — find files by name',
  ls: 'ls — list directory contents',
};

/** Built-in tool names of the pi coding agent running in the lambda segment host.
 * Reserved: a BorgIQ tool actor whose msgVar collides with one of these is rejected when the signal
 * is processed — at RUN time, not by this schema (the LLM sees one flat tool list, so names must be
 * unambiguous).
 *
 * `code_execution` is reserved only while `enableCodeExecution` is on, since the runtime otherwise
 * never registers it and there is nothing to be ambiguous with. See the collision check in
 * orchestrator/src/lib/aiAgent.ts. */
export const AI_AGENT_BUILTIN_TOOLS = [
  ...AI_AGENT_FILTERABLE_TOOLS, AI_AGENT_CODE_EXECUTION_TOOL_NAME,
] as const;

/** The curated agent models offered as suggestions. A known model id must be one of them; the
 * field also accepts any other valid reference, so a built-in provider's unlisted model
 * (`<provider>/<id>`) and a workspace's custom providers' models (`<slug>/<id>`) run here too — pi
 * is told about them at segment start from the workspace catalog. */
const AI_AGENT_MODELS: readonly string[] = AiAgentModels;

/** The AI Agent actor's model: a valid reference whose known model, if it is one, is in its
 * provider's curated agent list (`AiAgentModelsByProvider`). Unlisted built-in and custom models
 * pass here; a custom model's `agent: false` catalog flag is enforced at dispatch, where the
 * workspace catalog is at hand. */
const AiAgentModelRefSchema = AiModelRefSchema.superRefine((model, ctx) => {
  const parts = parseAiModelRef(model);
  if (parts?.kind !== 'known') return;
  const agentModels: readonly string[] = AiAgentModelsByProvider[parts.provider];
  if (!agentModels.includes(parts.modelId)) {
    ctx.addIssue({
      code: 'custom',
      message: `Model "${model}" is not one of the AI Agent actor's ${parts.provider} models (${agentModels.join(', ')})`,
    });
  }
});

/** Transport for a remote MCP server. The AI agent only supports REMOTE MCP servers over Streamable
 * HTTP — the orchestrator makes the JSON-RPC calls so they survive segment checkpoints; there is no
 * in-segment stdio MCP server. (The SDK's SSE client transport is deprecated, so it isn't offered.) */
export const AI_AGENT_MCP_TRANSPORTS = ['streamable-http'] as const;

/** Server names namespace their tools (`mcp__{name}__{tool}`) and gate the segment's JWT claim, so
 * they must be safe in a tool identifier — no separators that could confuse the namespacing. */
const MCP_SERVER_NAME_REGEX = /^[a-zA-Z0-9_-]+$/;

/** A remote MCP server the AI agent can call. The orchestrator connects to `url`, lists its tools at
 * session start, and bridges each `tools/call` over the runtime-API poll path so it's resumable across
 * Lambda segments. `auth` is a standard BorgIQ auth object restricted to the MCP-valid (header-based)
 * types: reference a workspace connection (`${{credentials.<alias>}}`) so tokens resolve — and OAuth
 * refreshes — fresh per call, or inline a literal/secret which rides the signal encrypted. Neither the
 * server URL nor its credentials ever reach the Lambda segment. */
export const RemoteAiAgentMcpServerSchema = z.object({
  /** Discriminant. Optional purely for back-compat: entries authored before internal BorgIQ servers
   * existed have no `type` and are remote by definition. */
  type: z.literal('http').nullish(),
  /** Label for the server; namespaces its tools (`mcp__{name}__{tool}`) and authorizes the segment. */
  name: z.string().min(1).regex(MCP_SERVER_NAME_REGEX, 'MCP server name may only contain letters, numbers, hyphens and underscores'),
  /** The remote MCP server endpoint (HTTPS). */
  url: z.string().url(),
  /** Transport the server speaks. Only streamable-http is supported. */
  transport: z.enum(AI_AGENT_MCP_TRANSPORTS).nullish(),
  /** Auth for the server. Prefer a connection reference (`${{credentials.linearMcp}}`); connection-backed
   * fields interpolate to placeholders so no secret lands on the signal. */
  auth: McpAuthDataSchema.nullish(),
});

/** An MCP Server Actor inside BorgIQ. No `auth`: the orchestrator dispatches these in-process and the
 * session's own scoping (the `allowedMcpServers` claim + stash) is the authorization. Resolved
 * CallFlow-style at session start — slugs default to this actor's own workspace/canvas. */
export const BorgiqAiAgentMcpServerSchema = z.object({
  type: z.literal('borgiq'),
  name: z.string().min(1).regex(MCP_SERVER_NAME_REGEX, 'MCP server name may only contain letters, numbers, hyphens and underscores'),
  /** The MCP Server Actor to expose. Required — slugs only narrow where to look for it. */
  actorId: z.string().regex(new RegExp('ACTR[0123456789abcdefghjkmnpqrstvwxyz]{26}$'), 'need a valid borgIQ MCP server actor id'),
  workspaceSlug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'need a valid borgIQ workspace slug')
    .min(5, 'must be 5 or more characters long').max(10, 'must be 10 or fewer characters long').nullish(),
  canvasSlug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'need a valid borgIQ canvas slug')
    .min(2, 'must be 2 or more characters long').max(255, 'must be 255 or fewer characters long').nullish(),
});

/** A plain `z.union` rather than a discriminated one: `type` is optional on the remote member
 * (back-compat) and a discriminated union cannot key off an absent discriminant. */
export const AiAgentMcpServerSchema = z.union([BorgiqAiAgentMcpServerSchema, RemoteAiAgentMcpServerSchema]);

export type RemoteAiAgentMcpServer = z.infer<typeof RemoteAiAgentMcpServerSchema>;
export type BorgiqAiAgentMcpServer = z.infer<typeof BorgiqAiAgentMcpServerSchema>;
export type AiAgentMcpServer = z.infer<typeof AiAgentMcpServerSchema>;

/** Narrow an AI-agent MCP server to the internal BorgIQ McpServerActor variant. */
export function isBorgiqAiAgentMcpServer(server: AiAgentMcpServer): server is BorgiqAiAgentMcpServer {
  return server.type === 'borgiq';
}

/** The options for the AiAgentActor (Zod schema for validation).
 * Modeled on AgentHarnessActorOptionsSchema minus harness/sandboxProvider; MCP servers are REMOTE
 * (orchestrator-mediated) here rather than stdio subprocesses. The harness is always pi and the
 * runtime is always the agent-sessions Lambda. */
export const AiAgentActorOptionsSchema = z.object({
  model: AiAgentModelRefSchema.nullish()
    .describe('The model to use: a known model id, "<provider>/<model-id>" for a built-in provider\'s unlisted model, or "<custom-provider-slug>/<model-id>" for a model served by one of the workspace\'s custom providers (e.g. "fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct"). A known model id must be one of the curated agent models. Provider-agnostic; LLM calls are routed through the BorgIQ AI gateway.'),
  prompt: z.string()
    .describe('The task prompt for the agent'),
  systemPrompt: z.string().nullish()
    .describe('Background instructions appended to the agent\'s system prompt'),
  thinkingLevel: AiAgentThinkingLevelSchema.nullish()
    .describe('How much the model thinks before each turn (off, minimal, low, medium, high). Clamped to what the selected model supports; unset keeps the default (medium). Thinking is shown in the chat timeline and billed as output tokens.'),
  autoCompaction: z.boolean().nullish().default(true)
    .describe('Summarise the conversation automatically when it grows past the context budget, so long sessions keep running instead of overflowing the model. Defaults to true. Off leaves only the emergency compaction after a context-overflow error.'),
  compactionInstructions: z.string().nullish()
    .describe('Extra focus for the compaction summary, for example what must never be dropped ("keep the list of files changed and the customer\'s constraints").'),
  contextBudgetTokens: z.number().int().min(32000).nullish()
    .describe('How large the conversation may grow, in tokens, before it is compacted (at 85% of this budget, capped at the model\'s window). Defaults to 200000: Anthropic doubles input pricing beyond 200K tokens. Raise it on a 1M-context model to keep more history at higher cost.'),
  sessionId: z.string().max(64).optional()
    .describe('Session ID to continue or create a session with custom ID (maximum 64 characters). Auto-generated if empty.'),
  volumeZipFile: BIQFileSchema.nullish()
    .describe('A zip file extracted into the session workspace when the session is created. Each later run that reuses the session with a zip extracts it again over the restored workspace: files at the paths it names are reset to the zip\'s version, other files are kept'),
  workingDirectory: z.string().nullish()
    .describe('Working directory for the agent, relative to the session workspace'),
  timeoutInMinutes: z.number().int().positive().nullish()
    .describe('Session timeout in minutes, measured across lambda segments. Defaults to 30.'),
  maxLoopCount: z.number().int().positive().nullish()
    .describe('The maximum number of assistant turns, defaults to unlimited'),
  allowedTools: z.array(z.string()).nullish()
    .describe('Built-in tools the agent may use (read/write/edit/bash/grep/find/ls). Empty means all are allowed. Does not affect the Code Execution tool, which is controlled only by enableCodeExecution.'),
  disallowedTools: z.array(z.string()).nullish()
    .describe('Built-in tools the agent may NOT use (read/write/edit/bash/grep/find/ls). Does not affect the Code Execution tool, which is controlled only by enableCodeExecution.'),
  enableCodeExecution: z.boolean().nullish().default(false)
    .describe('Let the agent execute code: it writes a TypeScript/JavaScript file into its workspace and runs it with Deno, sandboxed with the same filesystem and network permissions as its other tools. Only dependencies already cached in the runtime image resolve — nothing can be downloaded or installed. This is the only switch for the tool; the allowed/disallowed tool lists do not affect it. Defaults to false.'),
  allowNet: z.boolean().nullish().default(false)
    .describe('Allow outbound network access from the agent\'s tool runtime (Code Execution scripts and the in-process bash interpreter). Defaults to false.'),
  allowNetList: z.array(z.string()).nullish()
    .describe('Only these hosts/CIDRs are allowed for outbound network access from the tool runtime (system endpoints are always included). Mutually exclusive with denyNetList.'),
  denyNetList: z.array(z.string()).nullish()
    .describe('Block these hosts/CIDRs from outbound network access from the tool runtime (system endpoints cannot be denied). Mutually exclusive with allowNetList.'),
  mcpServers: z.array(AiAgentMcpServerSchema).nullish()
    .describe('MCP servers whose tools the agent may call. Tools are discovered at session start and each call is bridged through BorgIQ (resumable across segments). Remote servers take auth from the referenced connection; `type: borgiq` servers target an MCP Server Actor inside BorgIQ and need none. Server URLs/credentials never reach the agent runtime.'),
  env: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])).nullish()
    .describe('Environment variables exposed to the tools and bash. Values are encrypted during transit. Reserved names (HOME, PATH, AWS_*) are rejected.'),
  returnOutputZipFile: z.boolean().nullish()
    .describe('Include the workspace zip file in the done port result. Defaults to true.'),
  returnSessionDataFile: z.boolean().nullish()
    .describe('Include the pi session data zip file in the done port result. Defaults to true.'),
}).superRefine((data, ctx) => {
  if (!data.prompt) {
    ctx.addIssue({
      code: 'custom',
      message: 'Prompt is required',
    });
  }
  if (data.allowNetList?.length && data.denyNetList?.length) {
    ctx.addIssue({
      code: 'custom',
      path: ['denyNetList'],
      message: 'allowNetList and denyNetList are mutually exclusive',
    });
  }
  // No allowed/disallowed conflict check for the Code Execution tool: `enableCodeExecution` is its
  // only switch, and the segment host never consults the filters for it, so no combination of the
  // three can contradict itself.
  //
  // Server names namespace tools (`mcp__{name}__{tool}`) and key the session stash, so a duplicate
  // would silently shadow one server's tools and route its calls to the other.
  const mcpNames = (data.mcpServers ?? []).map((server) => server.name);
  const duplicateMcpName = mcpNames.find((name, index) => mcpNames.indexOf(name) !== index);
  if (duplicateMcpName) {
    ctx.addIssue({
      code: 'custom',
      path: ['mcpServers'],
      message: `Duplicate MCP server name "${duplicateMcpName}" — names must be unique`,
    });
  }
  // Reserved env names: the segment host owns HOME/PATH (pi session + tool layout); the bash spawn
  // env must never carry the function role's AWS credentials or influence the loader; and the
  // Deno/runtime plumbing (DENO_*, BORGIQ_*) must not be user-overridable.
  const reservedExact = ['HOME', 'PATH', 'TMPDIR', 'NODE_OPTIONS', 'LD_PRELOAD', 'LD_LIBRARY_PATH'];
  // Whole families are reserved: any AWS_* (execution-role creds + credential-source vars like
  // AWS_CONTAINER_CREDENTIALS_*), any DENO_* (DENO_CERT/DENO_DIR/permission plumbing), any BORGIQ_*
  // (proxy host, internal wiring). A prefix match is required — the old exact list let e.g.
  // AWS_CONTAINER_CREDENTIALS_FULL_URI or DENO_CERT through.
  const reservedPrefixes = ['AWS_', 'DENO_', 'BORGIQ_'];
  for (const key of Object.keys(data.env ?? {})) {
    const upper = key.toUpperCase();
    if (reservedExact.includes(upper) || reservedPrefixes.some((p) => upper.startsWith(p))) {
      ctx.addIssue({
        code: 'custom',
        path: ['env'],
        message: `Environment variable name "${key}" is reserved`,
      });
    }
  }
});

export type AiAgentActorOptions = z.infer<typeof AiAgentActorOptionsSchema>;

const modelSuggestionUi = buildAiModelSuggestionUiOptions(AI_AGENT_MODELS);

/** The JSON Schema for AiAgentActor options (for UI rendering) */
export const AiAgentActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    model: {
      type: BIQJsonSchemaType.String,
      description: 'The model to use: a known model id, "<provider>/<model-id>" for a built-in provider\'s unlisted model, or "<custom-provider-slug>/<model-id>" for a model served by one of the workspace\'s custom providers (e.g. "fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct"). A known model id must be one of the curated agent models. Provider-agnostic; LLM calls are routed through the BorgIQ AI gateway.',
      title: 'Model',
      default: AI_AGENT_MODELS[0],
      ui: {
        component: 'suggestion',
        order: 0,
        options: {
          placeholder: 'Select or type a model',
          ...modelSuggestionUi,
        }
      }
    },
    systemPrompt: {
      type: BIQJsonSchemaType.String,
      description: 'Background instructions appended to the agent\'s system prompt.',
      title: 'System prompt',
      ui: {
        component: 'textarea',
        order: 1,
        options: {
          editInModal: true,
          autoResize: true,
          minLines: 5,
          maxLines: 30,
          placeholder: 'You are a helpful coding assistant...',
        }
      }
    },
    prompt: {
      type: BIQJsonSchemaType.String,
      description: 'The task prompt for the agent',
      title: 'Prompt',
      minLength: 1,
      ui: {
        component: 'textarea',
        order: 2,
        options: {
          editInModal: true,
          autoResize: true,
          minLines: 5,
          maxLines: 30,
          placeholder: 'Your task is to...',
        }
      }
    },
    sessionId: {
      type: BIQJsonSchemaType.String,
      description: 'Session ID to continue or create a session with custom ID (maximum 64 characters). Auto-generated if empty.',
      title: 'Session ID',
      maxLength: 64,
      ui: {
        order: 3,
        options: {
          placeholder: 'Leave empty to auto-generate, or provide a custom ID',
        }
      }
    },
    volumeZipFile: {
      type: BIQJsonSchemaType.Object,
      description: 'A zip file extracted into the session workspace when the session is created. Each later run that reuses the session with a zip extracts it again over the restored workspace: files at the paths it names are reset to the zip\'s version, other files are kept.',
      title: 'Volume zip file',
      ui: {
        component: 'file',
        order: 4,
        options: {
          accept: '.zip,application/zip',
        }
      }
    },
    workingDirectory: {
      type: BIQJsonSchemaType.String,
      description: 'Working directory for the agent, relative to the session workspace',
      title: 'Working directory',
      ui: {
        order: 5,
        options: {
          placeholder: 'my-project',
        }
      }
    },
    timeoutInMinutes: {
      type: BIQJsonSchemaType.Integer,
      description: 'Session timeout in minutes, measured across lambda segments.',
      title: 'Timeout (min)',
      default: 30,
      minimum: 1,
      ui: {
        order: 6,
      }
    },
    maxLoopCount: {
      type: BIQJsonSchemaType.Integer,
      description: 'The maximum number of assistant turns, defaults to unlimited',
      title: 'Max loop count',
      minimum: 1,
      default: 25,
      ui: {
        order: 7,
      }
    },
    thinkingLevel: {
      type: BIQJsonSchemaType.String,
      description: 'How much the model thinks before each turn. Clamped to what the selected model supports. Thinking is shown in the chat timeline and billed as output tokens.',
      title: 'Thinking level',
      enum: [...AI_AGENT_THINKING_LEVELS],
      default: 'medium',
      ui: {
        component: 'select',
        order: 8,
        options: {
          enumLabels: {
            off: 'Off',
            minimal: 'Minimal',
            low: 'Low',
            medium: 'Medium',
            high: 'High',
          },
        },
      }
    },
    // Both tool lists are pickers over AI_AGENT_FILTERABLE_TOOLS rather than free text: the names
    // are a fixed runtime vocabulary, and a typo previously produced a silently ineffective filter
    // (an allow list is a whitelist, so a misspelt entry quietly drops the real tool). An `enum` on
    // `items` is what selects the MultiSelect renderer — arrays cannot carry `ui.component`
    // themselves, so the component/labels live on `items.ui`.
    allowedTools: {
      type: BIQJsonSchemaType.Array,
      description: 'Built-in tools the agent may use. Leave empty to allow all of them. Code Execution is not listed here — it is controlled only by Enable Code Execution.',
      title: 'Allowed tools',
      uniqueItems: true,
      items: {
        type: BIQJsonSchemaType.String,
        title: 'Tool name',
        enum: [...AI_AGENT_FILTERABLE_TOOLS],
        ui: {
          component: 'select',
          options: {
            enumLabels: AI_AGENT_FILTERABLE_TOOL_LABELS,
          },
        },
      },
      ui: {
        order: 10,
      }
    },
    disallowedTools: {
      type: BIQJsonSchemaType.Array,
      description: 'Built-in tools the agent may NOT use. Code Execution is not listed here — it is controlled only by Enable Code Execution.',
      title: 'Disallowed tools',
      uniqueItems: true,
      items: {
        type: BIQJsonSchemaType.String,
        title: 'Tool name',
        enum: [...AI_AGENT_FILTERABLE_TOOLS],
        ui: {
          component: 'select',
          options: {
            enumLabels: AI_AGENT_FILTERABLE_TOOL_LABELS,
          },
        },
      },
      ui: {
        order: 11,
      }
    },
    allowNet: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Allow outbound network access from the agent\'s tool runtime (Code Execution scripts and the in-process bash interpreter). Defaults to false.',
      title: 'Allow network access',
      default: false,
      ui: {
        order: 12,
      }
    },
    allowNetList: {
      type: BIQJsonSchemaType.Array,
      description: 'Only these hosts/CIDRs are allowed for outbound network access from the tool runtime (system endpoints are always included). Mutually exclusive with Deny Net List.',
      title: 'Allow net list',
      items: {
        type: BIQJsonSchemaType.String,
        title: 'Host or CIDR',
      },
      ui: {
        order: 13,
      }
    },
    denyNetList: {
      type: BIQJsonSchemaType.Array,
      description: 'Block these hosts/CIDRs from outbound network access from the tool runtime (system endpoints cannot be denied). Mutually exclusive with Allow Net List.',
      title: 'Deny net list',
      items: {
        type: BIQJsonSchemaType.String,
        title: 'Host or CIDR',
      },
      ui: {
        order: 14,
      }
    },
    mcpServers: {
      type: BIQJsonSchemaType.Array,
      description: 'MCP servers whose tools the agent may call. Tools are discovered at session start and each call is bridged through BorgIQ so it survives segment checkpoints.',
      title: 'MCP servers',
      items: {
        discriminatorKey: 'type',
        anyOf: [
          {
            title: 'Remote (HTTP)',
            description: 'A remote MCP server. The orchestrator connects to it and bridges each call; the URL and credentials never reach the agent runtime.',
            type: BIQJsonSchemaType.Object,
            properties: {
              type: {
                type: BIQJsonSchemaType.String,
                title: 'Type',
                description: 'The type of MCP server',
                const: 'http',
                default: 'Remote (HTTP)',
              },
              name: {
                type: BIQJsonSchemaType.String,
                title: 'Server name',
                description: 'Label for the server; namespaces its tools as mcp__{name}__{tool}. Letters, numbers, hyphens and underscores only.',
              },
              url: {
                type: BIQJsonSchemaType.String,
                title: 'Server URL',
                description: 'The remote MCP server endpoint (HTTPS).',
              },
              transport: {
                type: BIQJsonSchemaType.String,
                title: 'Transport',
                description: 'Transport the server speaks. Defaults to streamable-http.',
                enum: [...AI_AGENT_MCP_TRANSPORTS],
                default: AI_AGENT_MCP_TRANSPORTS[0],
              },
              auth: {
                type: BIQJsonSchemaType.Any,
                title: 'Auth',
                description: 'Authentication for the server. Defaults to the actor\'s bound connection (${{connection.auth}}); or reference a specific workspace connection, e.g. ${{credentials.linearMcp}}. Credentials are resolved per call (OAuth refreshes automatically) and never reach the agent runtime.',
                default: '${{connection.auth}}',
              },
            },
            required: ['name', 'url'],
          },
          {
            title: 'BorgIQ MCP server',
            description: 'An MCP Server Actor inside BorgIQ. No auth needed — the session is already scoped to the servers listed here.',
            type: BIQJsonSchemaType.Object,
            properties: {
              type: {
                type: BIQJsonSchemaType.String,
                title: 'Type',
                description: 'The type of MCP server',
                const: 'borgiq',
                default: 'BorgIQ MCP server',
              },
              name: {
                type: BIQJsonSchemaType.String,
                title: 'Server name',
                description: 'Label for the server; namespaces its tools as mcp__{name}__{tool}. Letters, numbers, hyphens and underscores only.',
              },
              actorId: {
                type: BIQJsonSchemaType.String,
                title: 'MCP server',
                description: 'The MCP Server Actor whose tools the agent may call.',
                pattern: 'ACTR[0123456789abcdefghjkmnpqrstvwxyz]{26}$',
                // the picker also writes workspaceSlug / canvasSlug below; leaving them blank
                // targets this actor's own canvas, which is what the runtime resolves to
                ui: {
                  component: 'actorSelect',
                  options: {
                    actorTypes: [BIQActorType.McpServerActor],
                    workspaceKey: 'workspaceSlug',
                    canvasKey: 'canvasSlug',
                    entityLabel: 'MCP server',
                  },
                },
              },
              workspaceSlug: {
                type: BIQJsonSchemaType.String,
                title: 'Workspace slug',
                description: 'The workspace the MCP Server Actor is in, defaults to the current workspace',
              },
              canvasSlug: {
                type: BIQJsonSchemaType.String,
                title: 'Canvas slug',
                description: 'The canvas the MCP Server Actor is in, defaults to the current canvas',
              },
            },
            required: ['type', 'name', 'actorId'],
          },
        ],
      },
      ui: {
        order: 15,
      }
    },
    env: {
      type: BIQJsonSchemaType.Any,
      description: 'Environment variables exposed to the tools and bash. Values are encrypted during transit.',
      title: 'Environment variables',
      ui: {
        order: 16,
        options: {
          placeholder: 'ENV_KEY: ENV_VALUE',
          editInModal: true,
        }
      }
    },
    returnOutputZipFile: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Include the workspace zip file in the done port result.',
      title: 'Return output zip file',
      default: true,
      ui: {
        order: 17,
      }
    },
    returnSessionDataFile: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Include the pi session data zip file in the done port result.',
      title: 'Return session data',
      default: true,
      ui: {
        order: 18,
      }
    },
    autoCompaction: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Summarise the conversation automatically when it grows past the context budget, so long sessions keep running instead of overflowing the model. Off leaves only the emergency compaction after a context-overflow error.',
      title: 'Auto compaction',
      default: true,
      ui: {
        order: 19,
      }
    },
    compactionInstructions: {
      type: BIQJsonSchemaType.String,
      description: 'Extra focus for the compaction summary: what must never be dropped when the conversation is summarised.',
      title: 'Compaction instructions',
      ui: {
        component: 'textarea',
        order: 20,
      }
    },
    contextBudgetTokens: {
      type: BIQJsonSchemaType.Integer,
      description: 'How large the conversation may grow, in tokens, before it is compacted (at 85% of this budget, capped at the model window). Anthropic doubles input pricing beyond 200K tokens.',
      title: 'Context budget (tokens)',
      default: 200000,
      minimum: 32000,
      ui: {
        order: 21,
      }
    },
    enableCodeExecution: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Let the agent execute code: it writes a TypeScript/JavaScript file into its workspace and runs it with Deno, sandboxed with the same filesystem and network permissions as its other tools. Only dependencies already cached in the runtime image resolve — nothing can be downloaded or installed.',
      title: 'Enable Code Execution',
      default: false,
      ui: {
        // Sits with the other tool controls — allowedTools (10), disallowedTools (11), allowNet
        // (12) — rather than stranded after the return-file toggles, since an author deciding what
        // the agent may do reads them together. It is the sole switch for this tool; the two lists
        // beneath it cover the always-on built-ins only.
        order: 9,
      }
    },
  },
  required: ['prompt'],
};

// ============================================================================
// Status Port Types
// ============================================================================

/** A notice about the session itself rather than something the model said or a tool returned.
 * Today: a context compaction the segment host ran (`notificationType: 'compaction'`, message
 * "Compacted context: N → ~M tokens"). Rendered as an info card in the chat timeline. */
export const AiAgentNotificationStatusPortResultSchema = z.object({
  type: z.literal('ai-agent-notification'),
  notificationType: z.string().optional()
    .describe('Kind of notice, e.g. compaction'),
  title: z.string().optional()
    .describe('Short heading for the notice'),
  message: z.string().optional()
    .describe('The notice text'),
  meta: z.object({
    cwd: z.string().optional(),
    timestamp: z.number().optional(),
  }).optional(),
});

export type AiAgentNotificationStatusPortResult = z.infer<typeof AiAgentNotificationStatusPortResultSchema>;

/** Status port envelope: the DeprecatedAiAgent envelope ('ai-agent-loop' / 'tool-result'), so
 * canvas UI renders this actor unchanged, plus the runtime notice ('ai-agent-notification').
 * Events originate from the lambda segment's status-hook posts. */
export const AiAgentStatusPortResultSchema = z.discriminatedUnion('type', [
  ...DeprecatedAiAgentStatusPortResultSchema.options,
  AiAgentNotificationStatusPortResultSchema,
]);

export type AiAgentStatusPortResult = z.infer<typeof AiAgentStatusPortResultSchema>;

// ============================================================================
// Done Port Result Schema
// ============================================================================

/** The final result schema for the AiAgentActor (harness-parity payload). */
export const AiAgentActorResultSchema = z.object({
  sessionId: z.string()
    .describe('The session ID for the agent execution'),
  success: z.boolean()
    .describe('Whether the agent execution was successful'),
  result: z.string().optional()
    .describe('The final assistant message or error message'),
  outputZipFile: BIQFileSchema.optional()
    .describe('A zip file of the session workspace after execution completes'),
  sessionDataFile: BIQFileSchema.optional()
    .describe('A zip file of the pi session data for cross-tier session continuation'),
  meta: z.object({
    endReason: z.enum(['completed', 'timeout', 'error', 'max-loop-count'])
      .describe('The reason the agent execution ended'),
    model: z.string().optional()
      .describe('The model used for the execution'),
    segments: z.number().int().positive().optional()
      .describe('How many lambda segments the run spanned'),
    duration: z.number().optional()
      .describe('Total duration of the execution in milliseconds'),
  }),
});

export type AiAgentActorResult = z.infer<typeof AiAgentActorResultSchema>;
```
