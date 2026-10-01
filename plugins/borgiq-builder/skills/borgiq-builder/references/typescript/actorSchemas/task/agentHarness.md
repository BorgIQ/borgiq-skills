# actorSchemas/task/agentHarness

Generated from the platform's runtime types. Do not edit.

AgentHarnessActor options and results: the models each harness CLI offers, MCP servers, and the Done and Status ports.

See also: [canvas](../../canvas.md), [sandbox](../../sandbox.md), [schemas/file](../../schemas/file.md), [schemas/connection](../../schemas/connection.md), [ai/index](../../ai/index.md), [ai/anthropic](../../ai/anthropic.md), [ai/openAi](../../ai/openAi.md).

## actorSchemas/task/agentHarness

**Source:** `actorSchemas/task/agentHarness.ts`

```typescript
import { z } from 'zod';

import { BIQActorType } from '../../canvas.js';
import { BIQSandboxProviders, BIQAgentHarnessType } from '../../sandbox.js';
import { BIQFileSchema, BIQJsonSchema, BIQJsonSchemaType, McpAuthDataSchema } from '../../schemas/index.js';
import { AiModel, AiModelInformationMap, AiToolCallSchema, BIQAiToolMessageOutputSchema, AiAgentModels, AnthropicAgentModels, OpenAiAgentModels } from '../../ai/index.js';

/** Models offered per harness CLI. Single-provider CLIs are scoped to that provider's agent
 * list; the provider-agnostic CLIs (OpenCode, Pi) offer every proficient agent model and
 * resolve the credential from the selected model's provider. The first entry of each list is
 * that harness's default. */
export const AgentHarnessModels = {
  [BIQAgentHarnessType.Claude]: AnthropicAgentModels,
  [BIQAgentHarnessType.Codex]: OpenAiAgentModels,
  [BIQAgentHarnessType.OpenCode]: AiAgentModels,
  [BIQAgentHarnessType.Pi]: AiAgentModels,
} as const satisfies Record<BIQAgentHarnessType, readonly AiModel[]>;

/** Returns the models valid for a harness (defaulting to Claude when unset). */
export const modelsForHarness = (
  harness: BIQAgentHarnessType | null | undefined
): readonly AiModel[] => AgentHarnessModels[harness ?? BIQAgentHarnessType.Claude];

/** Union of every model selectable across harnesses (deduped), for the UI dropdown + Zod enum.
 * Derived from AgentHarnessModels so it can never drift from the per-harness lists. */
const ALL_HARNESS_MODELS = Array.from(
  new Set<AiModel>(Object.values(AgentHarnessModels).flat())
) as [AiModel, ...AiModel[]];

/** The agent harness done source port id */
export const AGENT_HARNESS_DONE_SOURCE_PORT_ID = 'SPRTdone000';

/** The agent harness status source port id */
export const AGENT_HARNESS_STATUS_SOURCE_PORT_ID = 'SPRTstatus0';

/** Server names namespace the gateway route and gate the sandbox's JWT claim, so they must be safe
 * in a URL path segment and a config key. */
const MCP_SERVER_NAME_REGEX = /^[a-zA-Z0-9_-]+$/;

/** An MCP server run as a subprocess inside the sandbox. `type` is optional purely for back-compat:
 * entries authored before remote MCP support have no discriminant and are stdio by definition. */
export const StdioMcpServerSchema = z.object({
  type: z.literal('stdio').nullish(),
  name: z.string().min(1).regex(MCP_SERVER_NAME_REGEX, 'MCP server name may only contain letters, numbers, hyphens and underscores'),
  command: z.string().min(1),
  args: z.array(z.string()).optional(),
  /** Env for the subprocess. Encrypted in transit and only decrypted at sandbox launch. */
  env: z.record(z.string(), z.string()).optional(),
});

/** A remote MCP server the harness reaches THROUGH the BorgIQ MCP gateway. The sandbox is handed only
 * the gateway URL plus its own session JWT; the platform forwards the JSON-RPC and injects the
 * resolved auth, so credentials (and even the upstream URL) never enter the sandbox — and an
 * OAuth-backed connection can refresh mid-session without restarting the harness. */
export const HttpMcpServerSchema = z.object({
  type: z.literal('http'),
  name: z.string().min(1).regex(MCP_SERVER_NAME_REGEX, 'MCP server name may only contain letters, numbers, hyphens and underscores'),
  url: z.string().url(),
  /** Auth for the upstream server. Prefer a connection reference (`${{credentials.<alias>}}`). */
  auth: McpAuthDataSchema.nullish(),
});

/** An MCP server actor inside BorgIQ, reached through the same gateway as a remote server but
 * dispatched in-process — no auth field, because the sandbox's own session JWT already scopes it to
 * exactly the servers declared here. The target is resolved CallFlow-style at session start: the
 * slugs default to this actor's own workspace/canvas, and the actor must be an active
 * McpServerActor. */
export const BorgiqMcpServerSchema = z.object({
  type: z.literal('borgiq'),
  name: z.string().min(1).regex(MCP_SERVER_NAME_REGEX, 'MCP server name may only contain letters, numbers, hyphens and underscores'),
  /** The MCP Server Actor to expose. Required — slugs only narrow where to look for it. */
  actorId: z.string().regex(new RegExp('ACTR[0123456789abcdefghjkmnpqrstvwxyz]{26}$'), 'need a valid borgIQ MCP server actor id'),
  workspaceSlug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'need a valid borgIQ workspace slug')
    .min(5, 'must be 5 or more characters long').max(10, 'must be 10 or fewer characters long').nullish(),
  canvasSlug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'need a valid borgIQ canvas slug')
    .min(2, 'must be 2 or more characters long').max(255, 'must be 255 or fewer characters long').nullish(),
});

/** An MCP server wired to the harness: remote (gateway-proxied), borgiq (an internal McpServerActor,
 * also gateway-fronted but dispatched in-process) or stdio (in-sandbox subprocess).
 * A plain `z.union` rather than a discriminated one, because `type` is optional on the stdio member
 * (back-compat) and a discriminated union cannot key off an absent discriminant. The stdio member is
 * last so the members carrying a literal discriminant match first. */
export const AgentHarnessMcpServerSchema = z.union([HttpMcpServerSchema, BorgiqMcpServerSchema, StdioMcpServerSchema]);

export type StdioMcpServer = z.infer<typeof StdioMcpServerSchema>;
export type HttpMcpServer = z.infer<typeof HttpMcpServerSchema>;
export type BorgiqMcpServer = z.infer<typeof BorgiqMcpServerSchema>;
export type AgentHarnessMcpServer = z.infer<typeof AgentHarnessMcpServerSchema>;

/** Narrow a wired MCP server to the remote (gateway-proxied) variant. */
export function isHttpMcpServer(server: AgentHarnessMcpServer): server is HttpMcpServer {
  return server.type === 'http';
}

/** Narrow a wired MCP server to the internal BorgIQ McpServerActor variant. */
export function isBorgiqMcpServer(server: AgentHarnessMcpServer): server is BorgiqMcpServer {
  return server.type === 'borgiq';
}

/** Servers the sandbox reaches over the MCP gateway (remote upstreams + internal BorgIQ servers) —
 * i.e. everything that is not an in-sandbox stdio subprocess. These are the names that go into the
 * session's `allowedMcpServers` JWT claim and the gateway stash. */
export function isGatewayMcpServer(server: AgentHarnessMcpServer): server is HttpMcpServer | BorgiqMcpServer {
  return isHttpMcpServer(server) || isBorgiqMcpServer(server);
}

/** The options for the AgentHarnessActor (Zod schema for validation) */
export const AgentHarnessActorOptionsSchema = z.object({
  harness: z.enum(BIQAgentHarnessType).nullish()
    .describe('The agent harness CLI to run in the sandbox. Defaults to Claude Code.'),
  model: z.enum(ALL_HARNESS_MODELS).nullish()
    .describe('The model to use in the agent harness. Must be valid for the selected harness; defaults to that harness\'s default model.'),
  prompt: z.string()
    .describe('The prompt to send to Claude Code in the agent harness'),
  systemPrompt: z.string().nullish()
    .describe('The system prompt to provide as context to Claude Code'),
  sandboxProvider: z.enum(BIQSandboxProviders).nullish()
    .describe('The sandbox provider to use. Daytona is recommended for most use cases. E2B offers full internet access.'),
  maxLoopCount: z.number().int().positive().nullish()
    .describe('The maximum number of agentic loops to run, defaults to unlimited'),
  maxTokens: z.number().int().positive().nullish()
    .describe('The maximum number of tokens to generate per response'),
  temperature: z.number().min(0).max(1).nullish()
    .describe('The temperature to use for generation (0-1)'),
  sessionId: z.string().max(64).optional()
    .describe('Session ID to continue or create a session with custom ID (maximum 64 characters). Auto-generated if empty.'),
  volumeZipFile: BIQFileSchema.nullish()
    .describe('A zip file to extract into the sandbox volume. The contents will be available in the working directory.'),
  timeoutInMinutes: z.number().int().positive().nullish()
    .describe('The timeout of the sandbox session in minutes. Defaults to 15 minutes'),
  workingDirectory: z.string().nullish()
    .describe('Working directory for Claude Code, relative to the workspace where the volume zip is extracted'),
  allowedTools: z.array(z.string()).nullish()
    .describe('List of allowed tools for Claude Code (empty means all tools allowed)'),
  disallowedTools: z.array(z.string()).nullish()
    .describe('List of disallowed tools for Claude Code'),
  allowNet: z.boolean().nullish()
    .describe('Allow all outbound network access. Defaults to true. When true, all traffic is allowed unless further restricted by allowNetList or denyNetList. When false, outbound access is limited to only the domains required for functionality (AI provider API, BorgIQ API).'),
  allowNetList: z.array(z.string()).nullish()
    .describe('Only these hosts/CIDRs are allowed for outbound network access (system endpoints are always included). Mutually exclusive with denyNetList.'),
  denyNetList: z.array(z.string()).nullish()
    .describe('Block these hosts/CIDRs from outbound network access (system endpoints cannot be denied). Mutually exclusive with allowNetList.'),
  mcpServers: z.array(AgentHarnessMcpServerSchema).nullish()
    .describe('MCP servers to expose to the harness. `type: http` servers are proxied through the BorgIQ MCP gateway — the sandbox only ever sees the gateway URL and its own session token, never the upstream URL or credentials. `type: borgiq` servers target an MCP Server Actor inside BorgIQ and need no auth; they are dispatched internally. `type: stdio` servers run as a subprocess in the sandbox; their env values are encrypted in transit.'),
  env: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])).nullish()
    .describe('Environment variables to pass to the sandbox. Values will be encrypted during transit.'),
  returnOutputZipFile: z.boolean().nullish()
    .describe('Include the workspace directory zip file in the done port result. Defaults to true.'),
  returnSessionDataFile: z.boolean().nullish()
    .describe('Include the harness session data zip file in the done port result. Defaults to true.'),
  /** @deprecated Back-compat alias for returnSessionDataFile. */
  returnClaudeSessionDataFile: z.boolean().nullish()
    .describe('Deprecated alias of returnSessionDataFile.'),
}).superRefine((data, ctx) => {
  if (!data.prompt) {
    ctx.addIssue({
      code: 'custom',
      message: 'Prompt is required',
    });
  }
  // Enforce harness <-> model consistency server-side. The UI dropdown filters visually via
  // optionsByFieldValue, but a programmatic signal could still pair a model with a harness that
  // can't run it (e.g. a Claude model with the Codex CLI), so validate it here too.
  if (data.model && !modelsForHarness(data.harness).includes(data.model)) {
    ctx.addIssue({
      code: 'custom',
      path: ['model'],
      message: `Model "${data.model}" is not available for the ${data.harness ?? BIQAgentHarnessType.Claude} harness.`,
    });
  }
  const mcpServers = data.mcpServers ?? [];
  // Names key the gateway route, the session stash and the JWT claim, and namespace the harness's
  // own config entries — a duplicate would shadow one server and misroute its calls.
  const mcpNames = mcpServers.map((server) => server.name);
  const duplicateMcpName = mcpNames.find((name, index) => mcpNames.indexOf(name) !== index);
  if (duplicateMcpName) {
    ctx.addIssue({
      code: 'custom',
      path: ['mcpServers'],
      message: `Duplicate MCP server name "${duplicateMcpName}" — names must be unique`,
    });
  }
  // Pi has no MCP client of its own; it reaches gateway-fronted servers (remote + borgiq) only via
  // the gateway adapter, so a stdio subprocess server can't be wired to it. Reject rather than
  // silently dropping it (which is what the Claude-only implementation did for every other harness).
  if ((data.harness ?? BIQAgentHarnessType.Claude) === BIQAgentHarnessType.Pi) {
    const stdioServer = mcpServers.find((server) => !isGatewayMcpServer(server));
    if (stdioServer) {
      ctx.addIssue({
        code: 'custom',
        path: ['mcpServers'],
        message: `The Pi harness does not support stdio MCP servers ("${stdioServer.name}"). Use a remote (type: http) server instead.`,
      });
    }
  }
});

export type AgentHarnessActorOptions = z.infer<typeof AgentHarnessActorOptionsSchema>;

const modelLabels = ALL_HARNESS_MODELS.reduce((acc, model) => {
  acc[model] = AiModelInformationMap[model].label;
  return acc;
}, {} as Record<AiModel, string>);

const modelGroups = ALL_HARNESS_MODELS.reduce((acc, model) => {
  if (!acc[AiModelInformationMap[model].providerLabel]) {
    acc[AiModelInformationMap[model].providerLabel] = [model];
  } else {
    acc[AiModelInformationMap[model].providerLabel].push(model);
  }
  return acc;
}, {} as Record<string, AiModel[]>);

/** Map of harness -> valid model ids, driving the UI's harness-conditional model dropdown
 * (optionsFilterField/optionsByFieldValue). Built from the same AgentHarnessModels map the
 * Zod superRefine validates against, so the visual filter and server validation stay in sync. */
const modelOptionsByHarness = Object.fromEntries(
  Object.entries(AgentHarnessModels).map(([harness, models]) => [
    harness,
    (models as readonly AiModel[]).map((m) => m.toString()),
  ])
) as Record<BIQAgentHarnessType, string[]>;

/** The JSON Schema for AgentHarnessActor options (for UI rendering) */
export const AgentHarnessActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    harness: {
      type: BIQJsonSchemaType.String,
      description: 'The agent harness CLI to run in the sandbox.',
      title: 'Harness',
      enum: Object.values(BIQAgentHarnessType),
      default: BIQAgentHarnessType.Claude,
      ui: {
        component: 'select',
        order: -1,
        options: {
          enumLabels: {
            [BIQAgentHarnessType.Claude]: 'Claude Code',
            [BIQAgentHarnessType.Codex]: 'Codex',
            [BIQAgentHarnessType.OpenCode]: 'OpenCode',
            [BIQAgentHarnessType.Pi]: 'Pi',
          },
        }
      }
    },
    model: {
      type: BIQJsonSchemaType.String,
      description: 'The model to use in the agent harness. Pick one valid for the selected harness.',
      title: 'Model',
      enum: ALL_HARNESS_MODELS.map((model) => model.toString()),
      // Default to the first Anthropic agent model — valid for the default (Claude) harness.
      default: AnthropicAgentModels[0].toString(),
      ui: {
        component: 'searchSelect',
        order: 0,
        options: {
          enumLabels: modelLabels,
          enumGroups: modelGroups,
          // Show only the models valid for the selected harness (mirrors the Zod superRefine).
          optionsFilterField: 'harness',
          optionsByFieldValue: modelOptionsByHarness,
        }
      }
    },
    systemPrompt: {
      type: BIQJsonSchemaType.String,
      description: 'Background instructions provided to the coding agent before each invocation.',
      title: 'System prompt',
      default: 'You are a helpful coding assistant...',
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
    sandboxProvider: {
      type: BIQJsonSchemaType.String,
      description: 'The sandbox provider to use. Daytona is recommended for most use cases. E2B offers full internet access.',
      title: 'Sandbox provider',
      enum: Object.values(BIQSandboxProviders),
      default: BIQSandboxProviders.E2B,
      ui: {
        component: 'select',
        order: 2,
        options: {
          enumLabels: {
            [BIQSandboxProviders.E2B]: 'E2B',
            [BIQSandboxProviders.DAYTONA]: 'Daytona',
          },
        }
      }
    },
    prompt: {
      type: BIQJsonSchemaType.String,
      description: 'The prompt to send to Claude Code in the agent harness',
      title: 'Prompt',
      minLength: 1,
      ui: {
        component: 'textarea',
        order: 3,
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
        order: 4,
        options: {
          placeholder: 'Leave empty to auto-generate, or provide a custom ID',
        }
      }
    },
    volumeZipFile: {
      type: BIQJsonSchemaType.Object,
      description: 'A zip file to extract into the sandbox volume. The contents will be available in the working directory.',
      title: 'Volume zip file',
      ui: {
        component: 'file',
        order: 5,
        options: {
          accept: '.zip,application/zip',
        }
      }
    },
    maxLoopCount: {
      type: BIQJsonSchemaType.Integer,
      description: 'The maximum number of agentic loops to run, defaults to unlimited',
      title: 'Max loop count',
      minimum: 1,
      default: 10,
      ui: {
        order: 6,
      }
    },
    maxTokens: {
      type: BIQJsonSchemaType.Integer,
      description: 'The maximum number of tokens to generate per response',
      title: 'Max tokens',
      default: 16384,
      ui: {
        order: 7,
      }
    },
    temperature: {
      type: BIQJsonSchemaType.Number,
      description: 'The temperature to use for generation (0-1)',
      title: 'Temperature',
      default: 1,
      minimum: 0,
      maximum: 1,
      ui: {
        component: 'slider',
        order: 8,
        options: {
          step: 0.01,
        },
      },
    },
    timeoutInMinutes: {
      type: BIQJsonSchemaType.Integer,
      description: 'The timeout of the sandbox session in minutes. Defaults to 15 minutes',
      title: 'Timeout (min)',
      default: 15,
      minimum: 0,
      ui: {
        order: 9,
      }
    },
    workingDirectory: {
      type: BIQJsonSchemaType.String,
      description: 'Working directory for Claude Code, relative to the workspace where the volume zip is extracted',
      title: 'Working directory',
      ui: {
        order: 10,
        options: {
          placeholder: 'my-project',
        }
      }
    },
    allowedTools: {
      type: BIQJsonSchemaType.Array,
      description: 'List of allowed tools for Claude Code (empty means all tools allowed)',
      title: 'Allowed tools',
      items: {
        type: BIQJsonSchemaType.String,
        title: 'Tool name',
      },
      ui: {
        order: 11,
      }
    },
    disallowedTools: {
      type: BIQJsonSchemaType.Array,
      description: 'List of disallowed tools for Claude Code',
      title: 'Disallowed tools',
      items: {
        type: BIQJsonSchemaType.String,
        title: 'Tool name',
      },
      ui: {
        order: 12,
      }
    },
    allowNet: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Allow all outbound network access. Defaults to true. When true, all traffic is allowed unless further restricted by Allow/Deny net list. When false, outbound access is limited to only the domains required for functionality (AI provider API, BorgIQ API).',
      title: 'Allow network access',
      default: true,
      ui: {
        order: 13,
      }
    },
    allowNetList: {
      type: BIQJsonSchemaType.Array,
      description: 'Only these hosts/CIDRs are allowed for outbound network access (system endpoints are always included). Mutually exclusive with Deny net list.',
      title: 'Allow net list',
      items: {
        type: BIQJsonSchemaType.String,
        title: 'Host or CIDR',
      },
      ui: {
        order: 14,
      }
    },
    denyNetList: {
      type: BIQJsonSchemaType.Array,
      description: 'Block these hosts/CIDRs from outbound network access (system endpoints cannot be denied). Mutually exclusive with Allow net list.',
      title: 'Deny net list',
      items: {
        type: BIQJsonSchemaType.String,
        title: 'Host or CIDR',
      },
      ui: {
        order: 15,
      }
    },
    mcpServers: {
      type: BIQJsonSchemaType.Array,
      description: 'MCP servers to configure for Claude Code',
      title: 'MCP servers',
      items: {
        discriminatorKey: 'type',
        anyOf: [
          {
            title: 'Remote (HTTP)',
            description: 'A remote MCP server, proxied through BorgIQ. The sandbox only receives the gateway URL and its own session token — never the upstream URL or credentials.',
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
                description: 'Name of the MCP server. Letters, numbers, hyphens and underscores only.',
              },
              url: {
                type: BIQJsonSchemaType.String,
                title: 'Server URL',
                description: 'The remote MCP server endpoint (HTTPS).',
              },
              auth: {
                type: BIQJsonSchemaType.Any,
                title: 'Auth',
                description: 'Authentication for the server. Defaults to the actor\'s bound connection (${{connection.auth}}); or reference a specific workspace connection, e.g. ${{credentials.linearMcp}}. Credentials are resolved per request (OAuth refreshes automatically) and never reach the sandbox.',
                default: '${{connection.auth}}',
              },
            },
            required: ['type', 'name', 'url'],
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
                description: 'Name of the MCP server. Letters, numbers, hyphens and underscores only.',
              },
              actorId: {
                type: BIQJsonSchemaType.String,
                title: 'MCP server',
                description: 'The MCP Server Actor to expose to the harness.',
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
          {
            title: 'Local (stdio)',
            description: 'An MCP server run as a subprocess inside the sandbox. Not supported by the Pi harness.',
            type: BIQJsonSchemaType.Object,
            properties: {
              type: {
                type: BIQJsonSchemaType.String,
                title: 'Type',
                description: 'The type of MCP server',
                const: 'stdio',
                default: 'Local (stdio)',
              },
              name: {
                type: BIQJsonSchemaType.String,
                title: 'Server name',
                description: 'Name of the MCP server. Letters, numbers, hyphens and underscores only.',
              },
              command: {
                type: BIQJsonSchemaType.String,
                title: 'Command',
                description: 'Command to start the MCP server',
              },
              args: {
                type: BIQJsonSchemaType.Array,
                title: 'Arguments',
                description: 'Command-line arguments for the MCP server',
                items: {
                  type: BIQJsonSchemaType.String,
                  title: 'Argument',
                },
              },
              env: {
                type: BIQJsonSchemaType.Any,
                title: 'Environment variables',
                description: 'Environment variables for the MCP server. Values are encrypted during transit.',
                ui: {
                  options: {
                    editInModal: true,
                  }
                }
              },
            },
            required: ['type', 'name', 'command'],
          },
        ],
      },
      ui: {
        order: 16,
      }
    },
    env: {
      type: BIQJsonSchemaType.Any,
      description: 'Environment variables to pass to the sandbox. Values will be encrypted during transit.',
      title: 'Environment variables',
      ui: {
        order: 17,
        options: {
          placeholder: 'ENV_KEY: ENV_VALUE',
          editInModal: true,
        }
      }
    },
    returnOutputZipFile: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Include the workspace directory zip file in the done port result.',
      title: 'Return output zip file',
      default: true,
      ui: {
        order: 18,
      }
    },
    returnSessionDataFile: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Include the harness session data zip file in the done port result.',
      title: 'Return session data',
      default: true,
      ui: {
        order: 19,
      }
    },
  },
  required: ['prompt'],
};

// ============================================================================
// Status Port Types for Agent Harness Actor (aligned with AI Agent pattern)
// ============================================================================

/** Meta information included with status messages */
export const AgentHarnessMetaSchema = z.object({
  cwd: z.string().optional()
    .describe('Current working directory in the sandbox'),
  timestamp: z.number()
    .describe('Timestamp of this event'),
});

export type AgentHarnessMeta = z.infer<typeof AgentHarnessMetaSchema>;

/** Loop result - emitted before tool calls with accumulated response text */
export const AgentHarnessLoopResultSchema = z.object({
  type: z.literal('agent-harness-loop'),
  response: z.string()
    .describe('Accumulated text content generated before the tool calls'),
  toolCalls: z.array(AiToolCallSchema).nullish()
    .describe('The tool calls that are about to be made (null if just response text)'),
  reasoning: z.string().nullish()
    .describe('The model\'s thinking / reasoning for this turn, when the harness surfaced it. Clipped by the orchestrator; a loop may carry only reasoning (empty response, no tool calls).'),
  meta: AgentHarnessMetaSchema,
});

export type AgentHarnessLoopResult = z.infer<typeof AgentHarnessLoopResultSchema>;

/** Tool result - emitted when tool execution completes */
export const AgentHarnessToolResultSchema = z.object({
  type: z.literal('tool-result'),
  toolCallId: z.string()
    .describe('Identifier of the tool call this result belongs to'),
  toolName: z.string()
    .describe('Name of the tool that was called'),
  output: BIQAiToolMessageOutputSchema
    .describe('Output from the tool execution'),
  isError: z.boolean().optional()
    .describe('Whether the tool call resulted in an error'),
  meta: AgentHarnessMetaSchema,
});

export type AgentHarnessToolResult = z.infer<typeof AgentHarnessToolResultSchema>;

/** Error result - emitted when an error occurs */
export const AgentHarnessErrorResultSchema = z.object({
  type: z.literal('agent-harness-error'),
  message: z.string()
    .describe('Error message'),
  code: z.string().optional()
    .describe('Error code'),
  meta: AgentHarnessMetaSchema,
});

export type AgentHarnessErrorResult = z.infer<typeof AgentHarnessErrorResultSchema>;

/** Notification result - emitted for stdout/stderr and Claude Code notifications */
export const AgentHarnessNotificationResultSchema = z.object({
  type: z.literal('agent-harness-notification'),
  notificationType: z.string().optional()
    .describe('Type of notification (e.g., permission_prompt, idle_prompt)'),
  title: z.string().optional()
    .describe('Notification title'),
  message: z.string().optional()
    .describe('Notification message'),
  meta: AgentHarnessMetaSchema,
});

export type AgentHarnessNotificationResult = z.infer<typeof AgentHarnessNotificationResultSchema>;

/** Complete result - emitted when execution finishes */
export const AgentHarnessCompleteResultSchema = z.object({
  type: z.literal('agent-harness-complete'),
  message: z.string().optional()
    .describe('Completion message'),
  response: z.string().optional()
    .describe('The final assistant text, when the harness reported one on completion'),
  reasoning: z.string().nullish()
    .describe('The final turn\'s thinking / reasoning, when the harness surfaced it (Claude Code reports a text-only final turn only on stop)'),
  meta: AgentHarnessMetaSchema,
});

export type AgentHarnessCompleteResult = z.infer<typeof AgentHarnessCompleteResultSchema>;

/** Discriminated union for all agent harness status types (aligned with AI Agent pattern) */
export const AgentHarnessStatusPortResultSchema = z.discriminatedUnion('type', [
  AgentHarnessLoopResultSchema,        // type: 'agent-harness-loop' - response + toolCalls before execution
  AgentHarnessToolResultSchema,        // type: 'tool-result' - tool execution result
  AgentHarnessErrorResultSchema,       // type: 'agent-harness-error' - error events
  AgentHarnessNotificationResultSchema, // type: 'agent-harness-notification' - notifications
  AgentHarnessCompleteResultSchema,    // type: 'agent-harness-complete' - execution complete
]);

export type AgentHarnessStatusPortResult = z.infer<typeof AgentHarnessStatusPortResultSchema>;

// ============================================================================
// Done Port Result Schema
// ============================================================================

/** The final result schema for the AgentHarnessActor */
export const AgentHarnessActorResultSchema = z.object({
  sessionId: z.string()
    .describe('The session ID for the agent harness execution'),
  success: z.boolean()
    .describe('Whether the agent harness execution was successful'),
  result: z.unknown().optional()
    .describe('The result from the agent harness session'),
  outputZipFile: BIQFileSchema.optional()
    .describe('A zip file of the workspace directory after execution completes'),
  sessionDataFile: BIQFileSchema.optional()
    .describe('A zip file of the harness session data (e.g. ~/.claude or ~/.codex) for session continuation'),
  /** @deprecated Back-compat alias of sessionDataFile. */
  claudeSessionDataFile: BIQFileSchema.optional()
    .describe('Deprecated alias of sessionDataFile.'),
  meta: z.object({
    endReason: z.enum(['completed', 'timeout', 'error'])
      .describe('The reason the agent harness execution was ended'),
    model: z.string()
      .describe('The model used for the execution').optional(),
    duration: z.number().optional()
      .describe('Total duration of the execution in milliseconds'),
    usage: z.object({
      promptTokens: z.number().int().optional()
        .describe('The number of tokens in the prompts'),
      completionTokens: z.number().int().optional()
        .describe('The number of tokens in the completions'),
      totalTokens: z.number().int().optional()
        .describe('The total number of tokens used'),
    }).optional(),
  }),
});

export type AgentHarnessActorResult = z.infer<typeof AgentHarnessActorResultSchema>;
```
