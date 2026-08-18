# Actor Schemas: Core Task Actors

Zod schemas and TypeScript types for core task actors: AgentHarnessActor, AiActor, AiAgentActor, AiRouterActor, DenoActor, PythonActor, RouterActor, InterfaceActor, SendEmailActor, CallFlowActor, CallableResponseActor, WebhookResponseActor, and others.

## Table of Contents

- [actorSchemas/task/agentHarness.ts](#actorschemastaskagentharness)
- [actorSchemas/task/ai.ts](#actorschemastaskai)
- [actorSchemas/task/aiAgent.ts](#actorschemastaskaiagent)
- [actorSchemas/task/aiRouter.ts](#actorschemastaskairouter)
- [actorSchemas/task/callFlow.ts](#actorschemastaskcallflow)
- [actorSchemas/task/callableResponse.ts](#actorschemastaskcallableresponse)
- [actorSchemas/task/deno.ts](#actorschemastaskdeno)
- [actorSchemas/task/denoTest.ts](#actorschemastaskdenotest)
- [actorSchemas/task/deprecatedAiAgent.ts](#actorschemastaskdeprecatedaiagent)
- [actorSchemas/task/interface.ts](#actorschemastaskinterface)
- [actorSchemas/task/interfaceStatus.ts](#actorschemastaskinterfacestatus)
- [actorSchemas/task/mcpServer.ts](#actorschemastaskmcpserver)
- [actorSchemas/task/python.ts](#actorschemastaskpython)
- [actorSchemas/task/router.ts](#actorschemastaskrouter)
- [actorSchemas/task/sendEmail.ts](#actorschemastasksendemail)
- [actorSchemas/task/webhookResponse.ts](#actorschemastaskwebhookresponse)

## actorSchemas/task/agentHarness

**Source:** `actorSchemas/task/agentHarness.ts`

```typescript
import { z } from 'zod';

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
                title: 'MCP server actor ID',
                description: 'The actor id of the MCP Server Actor to expose to the harness.',
                pattern: 'ACTR[0123456789abcdefghjkmnpqrstvwxyz]{26}$',
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

## actorSchemas/task/ai

**Source:** `actorSchemas/task/ai.ts`

```typescript
import { z } from 'zod';

import { AiModel, AiModelInformationMap, AiDefaultParameters, BIQAiMessageSchema, AiToolCallSchema } from '../../ai/index.js';
import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

/** The options for the AIActor */
export const AiActorOptionsSchema = z.object({
  model: z.enum(AiModel).nullish()
    .describe('The model to use for the AI provider. Defaults to gpt-4o-mini if not provided'),
  prompt: z.string().nullish()
    .describe('The prompt to send to the AI model to generate a response'),
  temperature: z.number().min(0).max(2).nullish()
    .describe('The temperature to use for the AI model (0-1)'),
  maxTokens: z.number().int().positive().nullish()
    .describe('The maximum number of tokens to generate'),
  systemPrompt: z.string().nullish()
    .describe('The system prompt to provide as a background information to the AI model'),
  tools: z.array(z.object({
    name: z.string(),
    description: z.string(),
    jsonSchemaParameters: z.any().nullish()
      .describe('The parameters of the tool as a json schema'),
  })).nullish()
    .describe('The tools to use for the AI model'),
  messages: z.array(BIQAiMessageSchema)
    .nullish()
    .describe('The previous messages to provide to the AI model'),
  maxRetries: z.number().int().positive().nullish()
    .describe('The maximum number of retries to attempt if the AI model fails to generate a response'),
  outputSchema: z.any().nullish()
    .describe('The json schema to use for the AI model output, this would override the jsonMode if provided'),
  jsonMode: z.boolean().nullish()
    .describe('Whether to output the response as a json object, this would be overwritten by the outputSchema if provided'),
  emitInput: z.boolean().nullish()
    .describe('Whether to emit the input messages to the AI model'),
}).superRefine((data, ctx) => {
  if (!data.prompt && !data.messages) {
    ctx.addIssue({
      code: 'custom',
      message: 'Either prompt or messages must be provided',
    });
  }
});

export type AiActorOptions = z.infer<typeof AiActorOptionsSchema>;

const modelLabels = Object.values(AiModel).reduce((acc, model) => {
  acc[model] = AiModelInformationMap[model].label;
  return acc;
}, {} as Record<AiModel, string>);

const modelGroups = Object.values(AiModel).reduce((acc, model) => {
  if (!acc[AiModelInformationMap[model].providerLabel]) {
    acc[AiModelInformationMap[model].providerLabel] = [model];
  } else {
    acc[AiModelInformationMap[model].providerLabel].push(model);
  }
  return acc;
}, {} as Record<string, AiModel[]>);

export const AiActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    model: {
      type: BIQJsonSchemaType.String,
      description: 'The model to use for the AI provider',
      title: 'Model',
      enum: Object.values(AiModel),
      default: AiDefaultParameters.model,
      ui: {
        component: 'searchSelect',
        order: 0,
        options: {
          enumLabels: modelLabels,
          enumGroups: modelGroups,
        }
      }
    },
    systemPrompt: {
      type: BIQJsonSchemaType.String,
      description: 'The system prompt to provide as a background information to the AI model',
      title: 'System prompt',
      default: 'You are a helpful assistant...',
      ui: {
        component: 'textarea',
        order: 1,
        options: {
          autoResize: true,
          minLines: 5,
          maxLines: 30,
          placeholder: 'You are a helpful assistant...',
          editInModal: true,
        }
      }
    },
    tools: {
      type: BIQJsonSchemaType.Array,
      description: 'The tools to use for the AI model',
      title: 'Tools',
      items: {
        type: BIQJsonSchemaType.Object,
        properties: {
          name: {
            type: BIQJsonSchemaType.String,
            title: 'Name',
            description: 'The name of the tool',
          },
          description: {
            type: BIQJsonSchemaType.String,
            title: 'Description',
            description: 'The description of the tool',
          },
          jsonSchemaParameters: {
            type: BIQJsonSchemaType.Any,
            title: 'JSON schema parameters',
            description: 'The parameters of the tool as a json schema',
            ui: {
              options: {
                editInModal: true,
              }
            }
          }
        },
        required: ['name', 'description', 'jsonSchemaParameters'],
      },
    },
    messages: {
      type: BIQJsonSchemaType.Array,
      description: 'The previous messages to provide to the AI model',
      title: 'Messages',
      items: {
        anyOf: [
          {
            type: BIQJsonSchemaType.Object,
            properties: {
              role: {
                title: 'Role',
                description: 'The role of the user that sent the message',
                type: BIQJsonSchemaType.String,
                const: 'user',
              },
              content: {
                title: 'Content',
                description: 'The content of the user message',
                anyOf: [
                  {
                    type: BIQJsonSchemaType.String,
                    title: 'Chat message content',
                    description: 'The content of the user chat message',
                    ui: {
                      component: 'textarea',
                      options: {
                        editInModal: true,
                        autoResize: true,
                        minLines: 5,
                        maxLines: 30,
                      }
                    }
                  },
                  {
                    type: BIQJsonSchemaType.Array,
                    title: 'Multi-part content',
                    items: {
                      anyOf: [
                        {
                          title: 'Text',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'text',
                              ui: {
                                hidden: true,
                              }
                            },
                            text: {
                              type: BIQJsonSchemaType.String,
                              title: 'Text',
                              description: 'The text content',
                              ui: {
                                component: 'textarea',
                                options: {
                                  editInModal: true,
                                  autoResize: true,
                                  minLines: 5,
                                  maxLines: 30,
                                }
                              }
                            }
                          },
                          required: ['type', 'text'],
                        },
                        {
                          title: 'External image',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'image',
                              ui: {
                                hidden: true,
                              }
                            },
                            image: {
                              type: BIQJsonSchemaType.String,
                              title: 'Image URL or Base64',
                              description: 'The base64 encoded image OR url',
                            },
                            mediaType: {
                              type: BIQJsonSchemaType.String,
                              title: 'Media type',
                              description: 'The media/MIME type (only required when image is string)',
                            }
                          },
                          required: ['type', 'image', 'mediaType'],
                        },
                        {
                          title: 'BIQ file image',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'image',
                              ui: {
                                hidden: true,
                              }
                            },
                            image: {
                              type: BIQJsonSchemaType.Any,
                              title: 'Image',
                              description: 'BIQ File object for images',
                              default: '${{ }}',
                            },
                          },
                          required: ['type', 'image'],
                        },
                        {
                          title: 'External file',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'file',
                              ui: {
                                hidden: true,
                              }
                            },
                            data: {
                              type: BIQJsonSchemaType.String,
                              title: 'Data URL or Base64',
                              description: 'The base64 encoded file OR url',
                            },
                            fileName: {
                              type: BIQJsonSchemaType.String,
                              title: 'File name',
                              description: 'The name of the file',
                            },
                            mediaType: {
                              type: BIQJsonSchemaType.String,
                              title: 'Media type',
                              description: 'The media/MIME type',
                            }
                          },
                          required: ['type', 'data', 'fileName', 'mediaType'],
                        },
                        {
                          title: 'BIQ file',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'file',
                              ui: {
                                hidden: true,
                              }
                            },
                            file: {
                              type: BIQJsonSchemaType.Any,
                              title: 'File',
                              description: 'BIQ File object for files',
                              default: '${{ }}',
                            },
                          },
                          required: ['type', 'file'],
                        },
                      ],
                    },
                  }
                ],
              },
            },
            required: ['role', 'content'],
          },
          {
            type: BIQJsonSchemaType.Object,
            properties: {
              role: {
                title: 'Role',
                description: 'The role of the assistant',
                type: BIQJsonSchemaType.String,
                const: 'assistant',
              },
              content: {
                title: 'Content',
                description: 'The content of the assistant message',
                anyOf: [
                  {
                    type: BIQJsonSchemaType.String,
                    title: 'Chat message content',
                    description: 'The content of the chat message',
                    ui: {
                      component: 'textarea',
                      options: {
                        editInModal: true,
                        autoResize: true,
                        minLines: 5,
                        maxLines: 30,
                      }
                    }
                  },
                  {
                    type: BIQJsonSchemaType.Array,
                    title: 'Multi-part content',
                    items: {
                      anyOf: [
                        {
                          title: 'Text',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'text',
                              ui: {
                                hidden: true,
                              }
                            },
                            text: {
                              type: BIQJsonSchemaType.String,
                              title: 'Text',
                              description: 'The text part of the assistant message',
                              ui: {
                                component: 'textarea',
                                options: {
                                  editInModal: true,
                                  autoResize: true,
                                  minLines: 5,
                                  maxLines: 30,
                                }
                              }
                            }
                          },
                          required: ['type', 'text'],
                        },
                        {
                          title: 'External file',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'file',
                              ui: {
                                hidden: true,
                              }
                            },
                            data: {
                              type: BIQJsonSchemaType.String,
                              title: 'Data URL or Base64',
                              description: 'The base64 encoded file OR url',
                            },
                            fileName: {
                              type: BIQJsonSchemaType.String,
                              title: 'File name',
                              description: 'The name of the file',
                            },
                            mediaType: {
                              type: BIQJsonSchemaType.String,
                              title: 'Media type',
                              description: 'The media/MIME type',
                            }
                          },
                          required: ['type', 'data', 'fileName', 'mediaType'],
                        },
                        {
                          title: 'BIQ file',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'file',
                              ui: {
                                hidden: true,
                              }
                            },
                            file: {
                              type: BIQJsonSchemaType.Any,
                              title: 'File',
                              description: 'BIQ File object for files',
                              default: '${{ }}',
                            },
                          },
                          required: ['type', 'file'],
                        },
                        {
                          title: 'Reasoning',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'reasoning',
                              ui: {
                                hidden: true,
                              }
                            },
                            text: {
                              type: BIQJsonSchemaType.String,
                              title: 'Text',
                              description: 'The text part of the assistant message',
                              ui: {
                                component: 'textarea',
                                options: {
                                  editInModal: true,
                                  autoResize: true,
                                  minLines: 5,
                                  maxLines: 30,
                                }
                              }
                            },
                            signature: {
                              type: BIQJsonSchemaType.String,
                              title: 'Signature',
                              description: 'The signature of the assistant message',
                            }
                          },
                          required: ['type', 'text', 'signature'],
                        },
                        {
                          title: 'Tool call',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'tool-call',
                              ui: {
                                hidden: true,
                              }
                            },
                            toolCallId: {
                              type: BIQJsonSchemaType.String,
                              title: 'Tool call ID',
                              description: 'The ID of the tool call',
                            },
                            toolName: {
                              type: BIQJsonSchemaType.String,
                              title: 'Tool name',
                              description: 'The name of the tool',
                            },
                            input: {
                              type: BIQJsonSchemaType.Any,
                              title: 'Input',
                              description: 'The input arguments of the tool call',
                              ui: {
                                options: {
                                  editInModal: true,
                                }
                              }
                            },
                          },
                          required: ['type', 'toolCallId', 'toolName', 'input'],
                        },
                      ],
                    },
                  }
                ],
              },
            },
            required: ['role', 'content'],
          },
          {
            type: BIQJsonSchemaType.Object,
            properties: {
              role: {
                title: 'Role',
                description: 'The role of the tool',
                type: BIQJsonSchemaType.String,
                const: 'tool',
              },
              content: {
                type: BIQJsonSchemaType.Array,
                title: 'Tool call results',
                description: 'The content of the tool call response',
                items: {
                  type: BIQJsonSchemaType.Object,
                  properties: {
                    type: {
                      type: BIQJsonSchemaType.String,
                      const: 'tool-result',
                      ui: {
                        hidden: true,
                      }
                    },
                    toolCallId: {
                      type: BIQJsonSchemaType.String,
                      title: 'Tool call ID',
                      description: 'The ID of the tool call',
                    },
                    toolName: {
                      type: BIQJsonSchemaType.String,
                      title: 'Tool name',
                      description: 'The name of the tool',
                    },
                    output: {
                      title: 'Output',
                      description: 'The output of the tool call',
                      discriminatorKey: 'type',
                      anyOf: [
                        {
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              title: 'Type',
                              description: 'The type of the output',
                              type: BIQJsonSchemaType.String,
                              const: 'text',
                            },
                            value: {
                              type: BIQJsonSchemaType.String,
                              title: 'Text value',
                              description: 'The text result value',
                            },
                          },
                          required: ['type', 'value'],
                        },
                        {
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              title: 'Type',
                              description: 'The type of the output',
                              const: 'json',
                            },
                            value: {
                              type: BIQJsonSchemaType.Any,
                              title: 'JSON value',
                              description: 'The JSON result value',
                              ui: {
                                options: {
                                  editInModal: true,
                                }
                              }
                            },
                          },
                          required: ['type', 'value'],
                        },
                        {
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              title: 'Type',
                              description: 'The type of the output',
                              const: 'error-text',
                            },
                            value: {
                              type: BIQJsonSchemaType.String,
                              title: 'Error text',
                              description: 'The error text',
                            },
                          },
                          required: ['type', 'value'],
                        },
                        {
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              title: 'Type',
                              description: 'The type of the output',
                              const: 'error-json',
                            },
                            value: {
                              type: BIQJsonSchemaType.Any,
                              title: 'Error JSON',
                              description: 'The error JSON value',
                              ui: {
                                options: {
                                  editInModal: true,
                                }
                              }
                            },
                          },
                          required: ['type', 'value'],
                        },
                        {
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              title: 'Type',
                              description: 'The type of the output',
                              const: 'content',
                            },
                            value: {
                              type: BIQJsonSchemaType.Array,
                              title: 'Content',
                              description: 'Array of content items',
                              items: {
                                anyOf: [
                                  {
                                    title: 'Text',
                                    type: BIQJsonSchemaType.Object,
                                    properties: {
                                      type: {
                                        type: BIQJsonSchemaType.String,
                                        const: 'text',
                                        ui: {
                                          hidden: true,
                                        }
                                      },
                                      text: {
                                        type: BIQJsonSchemaType.String,
                                        title: 'Text',
                                        description: 'The text content',
                                      },
                                    },
                                    required: ['type', 'text'],
                                  },
                                  {
                                    title: 'External media',
                                    type: BIQJsonSchemaType.Object,
                                    properties: {
                                      type: {
                                        type: BIQJsonSchemaType.String,
                                        const: 'media',
                                        ui: {
                                          hidden: true,
                                        }
                                      },
                                      data: {
                                        type: BIQJsonSchemaType.String,
                                        title: 'Data URL or Base64',
                                        description: 'The base64 encoded media',
                                      },
                                      mediaType: {
                                        type: BIQJsonSchemaType.String,
                                        title: 'Media type',
                                        description: 'The media/MIME type',
                                      },
                                    },
                                    required: ['type', 'data', 'mediaType'],
                                  },
                                  {
                                    title: 'BIQ file media',
                                    type: BIQJsonSchemaType.Object,
                                    properties: {
                                      type: {
                                        type: BIQJsonSchemaType.String,
                                        const: 'media',
                                        ui: {
                                          hidden: true,
                                        }
                                      },
                                      data: {
                                        type: BIQJsonSchemaType.Any,
                                        title: 'Data',
                                        description: 'BIQ File object for media',
                                        default: '${{ }}',
                                      },
                                    },
                                    required: ['type', 'media'],
                                  },
                                ],
                              },
                            },
                          },
                          required: ['type', 'value'],
                        },
                      ],
                    },
                  },
                  required: ['type', 'toolCallId', 'toolName', 'output'],
                },
              },
            },
            required: ['role', 'content'],
          },
        ],
        discriminatorKey: 'role',
      },
      ui: {
        order: 2,
      }
    },
    prompt: {
      type: BIQJsonSchemaType.String,
      description: 'The prompt to send to the AI model to generate a response',
      title: 'Prompt',
      default: 'Your task is to...',
      minLength: 1,
      ui: {
        component: 'textarea',
        options: {
          editInModal: true,
          autoResize: true,
          minLines: 5,
          maxLines: 30,
          placeholder: 'Your task is to...',
        }
      }
    },
    jsonMode: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Whether to output the response as a json object, this would be overwritten by the Output Schema if provided',
      title: 'JSON mode',
      default: false,
      ui: {
        order: 3,
        component: 'switch',
      }
    },
    outputSchema: {
      title: 'Output schema',
      description: 'The json schema to format the AI model output. This would override the JSON Mode if provided',
      type: BIQJsonSchemaType.Any,
      default: {
        type: 'object',
        properties: null,
        required: []
      },
      ui: {
        order: 4,
        options: {
          editInModal: true,
        }
      }
    },
    maxRetries: {
      type: BIQJsonSchemaType.Integer,
      description: 'The maximum number of retries to attempt if the AI model fails to generate a response',
      title: 'Max retries',
      minimum: 0,
      default: 0,
      ui: {
        order: 5,
      }
    },
    maxTokens: {
      type: BIQJsonSchemaType.Integer,
      description: 'The maximum number of tokens to generate',
      title: 'Max tokens',
      default: AiDefaultParameters.maxTokens,
      ui: {
        order: 6,
      }
    },
    temperature: {
      type: BIQJsonSchemaType.Number,
      description: 'The temperature to use for the AI model (0-1)',
      title: 'Temperature',
      default: AiDefaultParameters.temperature,
      minimum: 0,
      maximum: 2,
      ui: {
        component: 'slider',
        order: 7,
        options: {
          step: 0.001,
        },
      },
    },
    emitInput: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Whether to emit the input messages to the AI model',
      title: 'Emit input',
      default: false,
      ui: {
        order: 8,
        component: 'switch',
      }
    },
  },
  required: [],
};

/** The response schema for the AIActor */
export const AiActorResultSchema = z.object({
  response: z.any()
    .describe('The generated content from the AI model'),
  toolCalls: z.array(AiToolCallSchema).nullish()
    .describe('The tool calls made by the AI model'),
  meta: z.object({
    input: z.array(z.union([BIQAiMessageSchema, z.object({
      role: z.literal('system'),
      content: z.string(),
    })])).nullish()
      .describe('The input messages to the AI model'),
    model: z.string()
      .describe('The model used to generate the response'),
    usage: z.object({
      promptTokens: z.number().int()
        .describe('The number of tokens in the prompt'),
      completionTokens: z.number().int()
        .describe('The number of tokens in the completion'),
      totalTokens: z.number().int()
        .describe('The total number of tokens used'),
    }),
    fromCache: z.boolean()
      .describe('Whether the response was fetched from the cache'),
  }),
});

export type AiActorResult = z.infer<typeof AiActorResultSchema>;
```

## actorSchemas/task/aiAgent

**Source:** `actorSchemas/task/aiAgent.ts`

```typescript
import { z } from 'zod';

import { BIQFileSchema, BIQJsonSchema, BIQJsonSchemaType, McpAuthDataSchema } from '../../schemas/index.js';
import { AiModel, AiModelInformationMap, AiAgentModels } from '../../ai/index.js';
import { DeprecatedAiAgentStatusPortResultSchema } from './deprecatedAiAgent.js';

/** The ai agent done source port id */
export const AI_AGENT_DONE_SOURCE_PORT_ID = 'SPRTdone000';

/** The opt-in code-execution tool's name. Unlike the always-on built-ins it is only registered —
 * and therefore only reserved — when `enableDenoTool` is set; see AI_AGENT_BUILTIN_TOOLS. */
export const AI_AGENT_DENO_TOOL_NAME = 'deno';

/** Built-in tool names of the pi coding agent running in the lambda segment host.
 * Reserved: a BorgIQ tool actor whose msgVar collides with one of these is rejected when the signal
 * is processed — at RUN time, not by this schema (the LLM sees one flat tool list, so names must be
 * unambiguous).
 *
 * `deno` is conditional. It is the one name the product itself hands out — the first DenoActor on a
 * canvas is titled "Deno", giving it the msgVar `deno` — so it is reserved only when the deno tool
 * is actually enabled. See the collision check in orchestrator/src/lib/aiAgent.ts. */
export const AI_AGENT_BUILTIN_TOOLS = [
  'read', 'write', 'edit', 'bash', 'grep', 'find', 'ls', AI_AGENT_DENO_TOOL_NAME,
] as const;

const AI_AGENT_MODELS = AiAgentModels as unknown as [AiModel, ...AiModel[]];

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
  model: z.enum(AI_AGENT_MODELS).nullish()
    .describe('The model to use for the agent. Provider-agnostic; LLM calls are routed through the BorgIQ AI gateway.'),
  prompt: z.string()
    .describe('The task prompt for the agent'),
  systemPrompt: z.string().nullish()
    .describe('Background instructions appended to the agent\'s system prompt'),
  sessionId: z.string().max(64).optional()
    .describe('Session ID to continue or create a session with custom ID (maximum 64 characters). Auto-generated if empty.'),
  volumeZipFile: BIQFileSchema.nullish()
    .describe('A zip file extracted into the session workspace at session creation'),
  workingDirectory: z.string().nullish()
    .describe('Working directory for the agent, relative to the session workspace'),
  timeoutInMinutes: z.number().int().positive().nullish()
    .describe('Session timeout in minutes, measured across lambda segments. Defaults to 30.'),
  maxLoopCount: z.number().int().positive().nullish()
    .describe('The maximum number of assistant turns, defaults to unlimited'),
  allowedTools: z.array(z.string()).nullish()
    .describe('List of allowed built-in tools (read/write/edit/bash/grep/find/ls, plus deno when "Enable deno tool" is on). Empty means all allowed. Listing deno here does NOT enable it on its own.'),
  disallowedTools: z.array(z.string()).nullish()
    .describe('List of disallowed built-in tools'),
  enableDenoTool: z.boolean().nullish().default(false)
    .describe('Enable the deno tool: the agent can run a TypeScript/JavaScript file from its workspace with Deno (same sandbox permissions as the other tools; only dependencies already cached in the runtime image resolve, nothing can be installed). Defaults to false.'),
  allowNet: z.boolean().nullish().default(false)
    .describe('Allow outbound network access from the Deno tool runtime and its in-process bash interpreter. Defaults to false.'),
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
  // Enabled but filtered out. The runtime detects this too, but only as a CloudWatch warning the
  // author staring at a ticked checkbox will never read — so reject it here, where they can fix it.
  if (data.enableDenoTool === true) {
    if (data.disallowedTools?.includes(AI_AGENT_DENO_TOOL_NAME)) {
      ctx.addIssue({
        code: 'custom',
        path: ['disallowedTools'],
        message: 'enableDenoTool is on but "deno" is in disallowedTools, so the tool would never be registered. Remove it from disallowedTools or turn the option off.',
      });
    } else if (data.allowedTools?.length && !data.allowedTools.includes(AI_AGENT_DENO_TOOL_NAME)) {
      ctx.addIssue({
        code: 'custom',
        path: ['allowedTools'],
        message: 'enableDenoTool is on but allowedTools omits "deno", so the tool would never be registered. Add it to allowedTools or turn the option off.',
      });
    }
  }
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

const modelLabels = AI_AGENT_MODELS.reduce((acc, model) => {
  acc[model] = AiModelInformationMap[model].label;
  return acc;
}, {} as Record<AiModel, string>);

const modelGroups = AI_AGENT_MODELS.reduce((acc, model) => {
  if (!acc[AiModelInformationMap[model].providerLabel]) {
    acc[AiModelInformationMap[model].providerLabel] = [model];
  } else {
    acc[AiModelInformationMap[model].providerLabel].push(model);
  }
  return acc;
}, {} as Record<string, AiModel[]>);

/** The JSON Schema for AiAgentActor options (for UI rendering) */
export const AiAgentActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    model: {
      type: BIQJsonSchemaType.String,
      description: 'The model to use for the agent. LLM calls are routed through the BorgIQ AI gateway.',
      title: 'Model',
      enum: AI_AGENT_MODELS.map((model) => model.toString()),
      default: AI_AGENT_MODELS[0].toString(),
      ui: {
        component: 'searchSelect',
        order: 0,
        options: {
          enumLabels: modelLabels,
          enumGroups: modelGroups,
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
      description: 'A zip file extracted into the session workspace at session creation.',
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
    allowedTools: {
      type: BIQJsonSchemaType.Array,
      description: 'List of allowed built-in tools (read/write/edit/bash/grep/find/ls, plus deno when "Enable deno tool" is on). Empty means all allowed. Listing deno here does NOT enable it on its own.',
      title: 'Allowed tools',
      items: {
        type: BIQJsonSchemaType.String,
        title: 'Tool name',
      },
      ui: {
        order: 10,
      }
    },
    disallowedTools: {
      type: BIQJsonSchemaType.Array,
      description: 'List of disallowed built-in tools',
      title: 'Disallowed tools',
      items: {
        type: BIQJsonSchemaType.String,
        title: 'Tool name',
      },
      ui: {
        order: 11,
      }
    },
    allowNet: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Allow outbound network access from the Deno tool runtime and its in-process bash interpreter. Defaults to false.',
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
                title: 'MCP server actor ID',
                description: 'The actor id of the MCP Server Actor whose tools the agent may call.',
                pattern: 'ACTR[0123456789abcdefghjkmnpqrstvwxyz]{26}$',
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
    enableDenoTool: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Enable the deno tool: the agent can run a TypeScript/JavaScript file from its workspace with Deno (same sandbox permissions as the other tools; only dependencies already cached in the runtime image resolve, nothing can be installed). Defaults to false.',
      title: 'Enable deno tool',
      default: false,
      ui: {
        // Grouped with the controls it interacts with — allowedTools (10), disallowedTools (11) and
        // allowNet (12) — rather than stranded at the bottom of the form after the return-file
        // toggles. Either filter can suppress this tool, so the author needs to see them together.
        order: 9,
      }
    },
  },
  required: ['prompt'],
};

// ============================================================================
// Status Port Types
// ============================================================================

/** Status port envelope: identical to the DeprecatedAiAgent envelope ('ai-agent-loop' /
 * 'tool-result') so canvas UI renders this actor unchanged.
 * Events originate from the lambda segment's status-hook posts. */
export const AiAgentStatusPortResultSchema = DeprecatedAiAgentStatusPortResultSchema;

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

## actorSchemas/task/aiRouter

**Source:** `actorSchemas/task/aiRouter.ts`

```typescript
import { ZodObject, z } from 'zod';

import { RuntimeActorSourcePort } from '../../schemas/runtime.js';
import { DEFAULT_SOURCE_PORT_ID } from '../../canvas.js';
import { BIQJsonSchemaType } from '../../schemas/index.js';
import { BIQJsonSchema } from '../../schemas/index.js';
import { AiModel, AiModelInformationMap, BIQAiMessageSchema } from '../../ai/index.js';
import { AiDefaultParameters } from '../../ai/index.js';

export enum AiRouterActorEmitType {
  SingleRoute = 'singleRoute',
  MultiRoute = 'multiRoute',
}

/** The options schema builder for the AiRouterActor since it changes for the sourcePorts configuration for the actor */
export const buildAiRouterActorOptionsSchema = (sourcePorts: RuntimeActorSourcePort[]): ZodObject<any> => z.object({ // eslint-disable-line @typescript-eslint/no-explicit-any
  model: z.string().nullish()
    .describe('The model to use for the AI provider. Defaults to gpt-4o-mini if not provided'),
  emitType: z.enum(AiRouterActorEmitType).nullish()
    .describe('How the AI router actor will function, either can be singleRoute or multiRoute where singleRoute emits only on one of the conditions being true and multiRoute emits on all of the conditions being true'),
  input: z.any().describe('The input to the AI router actor'),
  routeDescriptions: z.record(z.string(), z.string()).superRefine((value, ctx) => {
    const invalidRoutes: string[] = [];

    for (const routeName of Object.keys(value)) {
      const port = sourcePorts.find((port) => port.name === routeName);
      // if the port is not found, add it to the invalidRoutes list
      if (!port) {
        invalidRoutes.push(routeName);
      // if the route is the default port, add an issue
      } else if (port.id === DEFAULT_SOURCE_PORT_ID) {
        ctx.addIssue({
          code: 'invalid_value',
          path: [routeName],
          values: [routeName],
          message: `Route name '${routeName}' is reserved for the default route`,
        });
      }
    }
    // if there are no invalid ports, return the value
    if (invalidRoutes.length === 0) return;
    // if there are invalid ports, add an issue for all invalid routes
    ctx.addIssue({
      code: 'unrecognized_keys',
      keys: invalidRoutes,
      message: `Unrecognized Route name(s) in route definitions: ${invalidRoutes.join(', ')}`,
    });
  })
    .describe('The text definitions for the routes on if the input follows the route definition, the keys for the conditions are the route name provided in the routes section, the value is the text definition for the route'),
  emitInput: z.boolean().nullish()
    .describe('Whether to emit the input to the AI router actor'),
});

export type AiRouterActorOptions = {
  input: unknown,
  model?: AiModel,
  emitType?: AiRouterActorEmitType,
  routeDescriptions: { [portName: string]: string },
  emitInput?: boolean,
};

const modelLabels = Object.values(AiModel).reduce((acc, model) => {
  acc[model] = AiModelInformationMap[model].label;
  return acc;
}, {} as Record<AiModel, string>);

const modelGroups = Object.values(AiModel).reduce((acc, model) => {
  if (!acc[AiModelInformationMap[model].providerLabel]) {
    acc[AiModelInformationMap[model].providerLabel] = [model];
  } else {
    acc[AiModelInformationMap[model].providerLabel].push(model);
  }
  return acc;
}, {} as Record<string, AiModel[]>);

/** this is a partial schema, since the emitType and routeDescriptions will be handled by the sourcePorts configuration */
export const AiRouterActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    model: {
      type: BIQJsonSchemaType.String,
      description: 'The model to use for the AI provider',
      title: 'Model',
      enum: Object.values(AiModel),
      default: AiDefaultParameters.model,
      ui: {
        component: 'searchSelect',
        order: 0,
        options: {
          enumLabels: modelLabels,
          enumGroups: modelGroups,
        },
      },
    },
    input: {
      type: BIQJsonSchemaType.Any,
      description: 'The input to the AI router actor that would be passed to the AI model',
      title: 'Input',
    },
    emitInput: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Whether to emit the input to the AI router actor',
      title: 'Emit input',
      default: false,
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['input'],
};

/** The result schema for the AiRouterActor */
export const AiRouterResultSchema = z.object({
  route: z.string()
    .describe('The port name that the message was emitted from'),
  meta: z.object({
    input: z.array(z.union([BIQAiMessageSchema, z.object({
      role: z.literal('system'),
      content: z.string(),
    })])).nullish()
      .describe('The input messages to the AI router actor'),
    model: z.string()
      .describe('The model used to generate the response to determine the route'),
    usage: z.object({
      promptTokens: z.number().int()
        .describe('The number of tokens in the prompt'),
      completionTokens: z.number().int()
        .describe('The number of tokens in the completion'),
      totalTokens: z.number().int()
        .describe('The total number of tokens used'),
    }),
    fromCache: z.boolean()
      .describe('Whether the response, to determine the route, was fetched from the cache'),
  }),
});

export type AiRouterResult = z.infer<typeof AiRouterResultSchema>;
```

## actorSchemas/task/callFlow

**Source:** `actorSchemas/task/callFlow.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

/** The options schema for the CallFlowActor */
export const CallFlowActorOptionsSchema = z.object({
  workspaceSlug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'need a valid borgIQ workspace slug')
    .min(5, 'must be 5 or more characters long').max(10, 'must be 10 or fewer characters long').nullish()
    .describe('The workspace the Callable Trigger Actor is in, defaults to the current workspace'),
  canvasSlug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'need a valid borgIQ canvas slug')
    .min(2, 'must be 2 or more characters long').max(255, 'must be 255 or fewer characters long').nullish()
    .describe('The canvas the Callable Trigger Actor is in, defaults to the current canvas'),
  callableTriggerActorId: z.string().regex(new RegExp('ACTR[0123456789abcdefghjkmnpqrstvwxyz]{26}$'), 'need a valid borgIQ callable trigger actor id')
    .describe('The actor id of the Callable Trigger Actor that wants to be triggered'),
  waitForResponse: z.boolean().nullish()
    .describe('If this actor should wait for a response from the Callable Response Actor from the called flow or emit a message immediately'),
  timeoutInSeconds: z.number().positive().nullish()
    .describe('The timeout in seconds for the sub-flow to return a response, defaults to no timeout'),
  payload: z.any()
    .describe('The payload to send to the Callable Trigger Actor, the parameters of the callable trigger flow'),
});

export type CallFlowActorOptions = z.infer<typeof CallFlowActorOptionsSchema>;

export const CallFlowActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    workspaceSlug: {
      type: BIQJsonSchemaType.String,
      title: 'Workspace slug',
      description: 'The workspace the Callable Trigger Actor is in, defaults to the current workspace',
    },
    canvasSlug: {
      type: BIQJsonSchemaType.String,
      title: 'Canvas slug',
      description: 'The canvas the Callable Trigger Actor is in, defaults to the current canvas',
    },
    callableTriggerActorId: {
      type: BIQJsonSchemaType.String,
      title: 'Callable trigger actor ID',
      description: 'The actor id of the Callable Trigger Actor that wants to be triggered',
      pattern: 'ACTR[0123456789abcdefghjkmnpqrstvwxyz]{26}$',
    },
    payload: {
      type: BIQJsonSchemaType.Any,
      title: 'Payload',
      description: 'The payload to send to the Callable Trigger Actor, the parameters of the callable trigger flow',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
    waitForResponse: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Wait for response',
      description: 'If this actor should wait for a response from the Callable Response Actor from the called flow or emit a message immediately',
      default: false,
      ui: {
        component: 'switch',
      },
    },
    timeoutInSeconds: {
      type: BIQJsonSchemaType.Number,
      title: 'Timeout in seconds',
      description: 'The timeout in seconds for the sub-flow to return a response, defaults to no timeout',
      default: 900, // 15 minutes
    },
  },
  required: ['callableTriggerActorId'],
};

export const CallFlowActorReceiveResultSchema = z.any();

export type CallFlowActorResult = z.infer<typeof CallFlowActorReceiveResultSchema>;
```

## actorSchemas/task/callableResponse

**Source:** `actorSchemas/task/callableResponse.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

/** The options schema for the CallableResponseActor */
export const CallableResponseActorOptionsSchema = z.object({
  payload: z.any().describe('The payload to emit on the Call flow actor that trigged the flow'),
  throwError: z.boolean().nullish()
    .describe('If the callable response actor should throw an error to the call flow actor'),
});

export type CallableResponseActorOptions = z.infer<typeof CallableResponseActorOptionsSchema>;

export const CallableResponseActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    payload: {
      type: BIQJsonSchemaType.Any,
      title: 'Payload',
      description: 'The payload to emit on the Call flow actor that trigged the flow',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
    throwError: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Throw error',
      description: 'If the callable response actor should throw an error to the call flow actor',
      default: false,
      ui: {
        component: 'switch',
      },
    },
  },
};

/** The response schema for the CallableResponseActor */
export const CallableResponseActorResultSchema = z.any().describe('The payload provided from the options of the CallableResponseActor');

export type CallableResponseActorResult = z.infer<typeof CallableResponseActorResultSchema>;
```

## actorSchemas/task/deno

**Source:** `actorSchemas/task/deno.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

export const DenoActorCodeSchema = z.string().min(1);

/** The options for the DenoActor */
export const DenoActorOptionsSchema = z.object({
  emitArrayAsSingleMessage: z.boolean().nullish()
    .describe('Emit the array as a single message instead of an array of messages, defaults to true').default(true),
  allowNet: z.boolean().nullish()
    .describe('Allow network access. By default when this is true, all network call is allowed but if allowNetList is provided then only that subset of URLs are allowed').default(false),
  allowNetList: z.array(z.string()).nullish()
    .describe('List of URLs that are allowed to be accessed when allowNet is true. This is ignored if allowNet is false').default([]),
  denyNetList: z.array(z.string()).nullish()
    .describe('List of URLs that are denied to be accessed when allowNet is true. This is ignored if allowNet is false').default([]),
  allowFs: z.boolean().nullish()
    .describe('Allow file system access to the temporary directory. By default when this is true, all file system access is allowed within the temporary directory').default(false),
  env: z.array(z.object({
    name: z.string()
      .regex(/^[A-Z0-9_]+$/, 'Environment variable name must contain only uppercase letters, numbers and underscores')
      .regex(/^(?!TMPDIR$)/, 'Environment variable name cannot be TMPDIR')
      .regex(/^(?!DENO_NO_UPDATE_CHECK$)/, 'Environment variable name cannot be DENO_NO_UPDATE_CHECK')
      .describe('Environment variable name (must contain only uppercase letters, numbers and underscores). If allowEnv is false, this will be ignored'),
    value: z.string().nullish()
      .describe('Environment variable value. If allowEnv is false, this will be ignored')
  })).nullish().default([])
    .describe('List of environment variables to pass to the Deno runtime'),
});

export type DenoActorOptions = z.infer<typeof DenoActorOptionsSchema>;

export const DenoActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    emitArrayAsSingleMessage: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit array as single message',
      description: 'Emit the array as a single message instead of an array of messages',
      default: true,
      ui: {
        component: 'switch',
      },
    },
    allowNet: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Allow net',
      description: 'Allow network access. By default when this is true, all network call is allowed but if allowNetList is provided then only that subset of URLs are allowed',
      ui: {
        component: 'switch',
      },
    },
    allowNetList: {
      type: BIQJsonSchemaType.Array,
      title: 'Allow net list',
      description: 'List of URLs that are allowed to be accessed when allowNet is true. This is ignored if allowNet is false',
      items: {
        type: BIQJsonSchemaType.String,
      },
    },
    denyNetList: {
      type: BIQJsonSchemaType.Array,
      title: 'Deny net list',
      description: 'List of URLs that are denied to be accessed when allowNet is true. This is ignored if allowNet is false',
      items: {
        type: BIQJsonSchemaType.String,
      },
    },
    allowFs: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Allow file system',
      description: 'Allow file system access to the temporary directory. By default when this is true, all file system access is allowed within the temporary directory',
      ui: {
        component: 'switch',
      },
    },
    env: {
      type: BIQJsonSchemaType.Array,
      title: 'Environment variables',
      description: 'List of environment variables to pass to the Deno runtime',
      items: {
        type: BIQJsonSchemaType.Object,
        properties: {
          name: {
            type: BIQJsonSchemaType.String,
            title: 'Name',
            description: 'Environment variable name (must contain only uppercase letters, numbers and underscores)',
            pattern: '^(?!TMPDIR$)(?!DENO_NO_UPDATE_CHECK$)[A-Z0-9_]+$'
          },
          value: {
            type: BIQJsonSchemaType.String,
            title: 'Value',
            description: 'Environment variable value'
          }
        },
        required: ['name']
      }
    }
  },
};

/** The response schema for the DenoActor */
export const DenoActorResultSchema = z.any();

export type DenoActorResult = z.infer<typeof DenoActorResultSchema>;
```

## actorSchemas/task/denoTest

**Source:** `actorSchemas/task/denoTest.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

export const DenoTestActorCodeSchema = z.string().min(1);

/** The options for the DenoTestActor */
export const DenoTestActorOptionsSchema = z.object({
  emitArrayAsSingleMessage: z.boolean().nullish()
    .describe('Emit the array as a single message instead of an array of messages').default(false),
  argList: z.array(z.string()).nullish()
    .describe('List of command line arguments to pass to deno.').default([]),
  env: z.array(z.object({
    name: z.string()
      .regex(/^[A-Z0-9_]+$/)
      .describe('Environment variable name (must contain only uppercase letters, numbers and underscores)'),
    value: z.string().describe('Environment variable value')
  })).nullish().default([])
    .describe('List of environment variables to pass to the Deno runtime'),
});

export type DenoTestActorOptions = z.infer<typeof DenoTestActorOptionsSchema>;

export const DenoTestActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    emitArrayAsSingleMessage: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit array as single message',
      description: 'Emit the array as a single message instead of an array of messages',
      ui: {
        component: 'switch',
      },
    },
    argList: {
      type: BIQJsonSchemaType.Array,
      title: 'Argument list',
      description: 'List of command line arguments to pass to deno.',
      items: {
        type: BIQJsonSchemaType.String,
      },
    },
    env: {
      type: BIQJsonSchemaType.Array,
      title: 'Environment variables',
      description: 'List of environment variables to pass to the Deno runtime',
      items: {
        type: BIQJsonSchemaType.Object,
        properties: {
          name: {
            type: BIQJsonSchemaType.String,
            title: 'Name',
            description: 'Environment variable name (must contain only uppercase letters, numbers and underscores)',
            pattern: '^[A-Z0-9_]+$'
          },
          value: {
            type: BIQJsonSchemaType.String,
            title: 'Value',
            description: 'Environment variable value'
          }
        }
      }
    }
  },
};

/** The response schema for the DenoTestActor */
export const DenoTestActorResultSchema = z.any();

export type DenoTestActorResult = z.infer<typeof DenoTestActorResultSchema>;
```

## actorSchemas/task/deprecatedAiAgent

**Source:** `actorSchemas/task/deprecatedAiAgent.ts`

```typescript
import { z } from 'zod';

import { AiModel, AiModelInformationMap, AiDefaultParameters, AiToolCallSchema, AiToolMessageResultSchema, BIQAiMessageSchema, AiAgentModels, AiFinishReason } from '../../ai/index.js';
import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

/** the input value for injecting ai input values into the actor inputs */
export const AI_INPUT_VALUE = '${{aiInput}}';

/** The options for the DeprecatedAiAgent (legacy loop agent) */
export const DeprecatedAiAgentOptionsSchema = z.object({
  model: z.enum(AiAgentModels).nullish()
    .describe('The model to use for the AI provider. Defaults to gpt-4o-mini if not provided'),
  prompt: z.string().nullish()
    .describe('The prompt to send to the AI model to generate a response'),
  temperature: z.number().min(0).max(2).nullish()
    .describe('The temperature to use for the AI model (0-1)'),
  maxTokens: z.number().int().positive().nullish()
    .describe('The maximum number of tokens to generate'),
  systemPrompt: z.string().nullish()
    .describe('Background instructions provided to the AI model before each invocation'),
  messages: z.array(BIQAiMessageSchema)
    .nullish()
    .describe('The previous messages to provide to the AI model'),
  maxLoopCount: z.number().int().positive().nullish()
    .describe('The maximum number of ai agent loops to run, defaults to unlimited'),
  enableTodoTool: z.boolean().nullish()
    .describe('Whether to enable the todo tool for the AI agent'),
}).superRefine((data, ctx) => {
  if (!data.prompt && !data.messages) {
    ctx.addIssue({
      code: 'custom',
      message: 'Either prompt or messages must be provided',
    });
  }
});

export type DeprecatedAiAgentOptions = z.infer<typeof DeprecatedAiAgentOptionsSchema>;

const modelLabels = AiAgentModels.reduce((acc, model) => {
  acc[model] = AiModelInformationMap[model].label;
  return acc;
}, {} as Record<AiModel, string>);

const modelGroups = AiAgentModels.reduce((acc, model) => {
  if (!acc[AiModelInformationMap[model].providerLabel]) {
    acc[AiModelInformationMap[model].providerLabel] = [model];
  } else {
    acc[AiModelInformationMap[model].providerLabel].push(model);
  }
  return acc;
}, {} as Record<string, AiModel[]>);

export const DeprecatedAiAgentOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    model: {
      type: BIQJsonSchemaType.String,
      description: 'The model to use for the AI provider',
      title: 'Model',
      enum: AiAgentModels.map((model) => model.toString()),
      default: AiAgentModels[0].toString(),
      ui: {
        component: 'searchSelect',
        order: 0,
        options: {
          enumLabels: modelLabels,
          enumGroups: modelGroups,
        }
      }
    },
    systemPrompt: {
      type: BIQJsonSchemaType.String,
      description: 'Background instructions provided to the AI model before each invocation.',
      title: 'System prompt',
      default: 'You are a helpful assistant...',
      ui: {
        component: 'textarea',
        order: 1,
        options: {
          editInModal: true,
          autoResize: true,
          minLines: 5,
          maxLines: 30,
          placeholder: 'You are a helpful assistant...',
        }
      }
    },
    messages: {
      type: BIQJsonSchemaType.Array,
      description: 'The previous messages to provide to the AI model',
      title: 'Messages',
      items: {
        anyOf: [
          {
            type: BIQJsonSchemaType.Object,
            properties: {
              role: {
                title: 'Role',
                description: 'The role of the user that sent the message',
                type: BIQJsonSchemaType.String,
                const: 'user',
              },
              content: {
                title: 'Content',
                description: 'The content of the user message',
                anyOf: [
                  {
                    type: BIQJsonSchemaType.String,
                    title: 'Chat message content',
                    description: 'The content of the user chat message',
                    ui: {
                      component: 'textarea',
                      options: {
                        editInModal: true,
                        autoResize: true,
                        minLines: 5,
                        maxLines: 30,
                      }
                    }
                  },
                  {
                    type: BIQJsonSchemaType.Array,
                    title: 'Multi-part content',
                    items: {
                      anyOf: [
                        {
                          title: 'Text',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'text',
                              ui: {
                                hidden: true,
                              }
                            },
                            text: {
                              type: BIQJsonSchemaType.String,
                              title: 'Text',
                              description: 'The text content',
                              ui: {
                                component: 'textarea',
                                options: {
                                  editInModal: true,
                                  autoResize: true,
                                  minLines: 5,
                                  maxLines: 30,
                                }
                              }
                            }
                          },
                          required: ['type', 'text'],
                        },
                        {
                          title: 'External image',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'image',
                              ui: {
                                hidden: true,
                              }
                            },
                            image: {
                              type: BIQJsonSchemaType.String,
                              title: 'Image URL or Base64',
                              description: 'The base64 encoded image OR url',
                            },
                            mediaType: {
                              type: BIQJsonSchemaType.String,
                              title: 'Media type',
                              description: 'The media/MIME type (only required when image is string)',
                            }
                          },
                          required: ['type', 'image', 'mediaType'],
                        },
                        {
                          title: 'BIQ file image',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'image',
                              ui: {
                                hidden: true,
                              }
                            },
                            image: {
                              type: BIQJsonSchemaType.Any,
                              title: 'Image',
                              description: 'BIQ File object for images',
                              default: '${{ }}',
                            },
                          },
                          required: ['type', 'image'],
                        },
                        {
                          title: 'External file',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'file',
                              ui: {
                                hidden: true,
                              }
                            },
                            data: {
                              type: BIQJsonSchemaType.String,
                              title: 'Data URL or Base64',
                              description: 'The base64 encoded file OR url',
                            },
                            fileName: {
                              type: BIQJsonSchemaType.String,
                              title: 'File name',
                              description: 'The name of the file',
                            },
                            mediaType: {
                              type: BIQJsonSchemaType.String,
                              title: 'Media type',
                              description: 'The media/MIME type',
                            }
                          },
                          required: ['type', 'data', 'fileName', 'mediaType'],
                        },
                        {
                          title: 'BIQ file',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'file',
                              ui: {
                                hidden: true,
                              }
                            },
                            file: {
                              type: BIQJsonSchemaType.Any,
                              title: 'File',
                              description: 'BIQ File object for files',
                              default: '${{ }}',
                            },
                          },
                          required: ['type', 'file'],
                        },
                      ],
                    },
                  }
                ],
              },
            },
            required: ['role', 'content'],
          },
          {
            type: BIQJsonSchemaType.Object,
            properties: {
              role: {
                title: 'Role',
                description: 'The role of the assistant',
                type: BIQJsonSchemaType.String,
                const: 'assistant',
              },
              content: {
                title: 'Content',
                description: 'The content of the assistant message',
                anyOf: [
                  {
                    type: BIQJsonSchemaType.String,
                    title: 'Chat message content',
                    description: 'The content of the chat message',
                    ui: {
                      component: 'textarea',
                      options: {
                        editInModal: true,
                        autoResize: true,
                        minLines: 5,
                        maxLines: 30,
                      }
                    }
                  },
                  {
                    type: BIQJsonSchemaType.Array,
                    title: 'Multi-part content',
                    items: {
                      anyOf: [
                        {
                          title: 'Text',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'text',
                              ui: {
                                hidden: true,
                              }
                            },
                            text: {
                              type: BIQJsonSchemaType.String,
                              title: 'Text',
                              description: 'The text part of the assistant message',
                              ui: {
                                component: 'textarea',
                                options: {
                                  editInModal: true,
                                  autoResize: true,
                                  minLines: 5,
                                  maxLines: 30,
                                }
                              }
                            }
                          },
                          required: ['type', 'text'],
                        },
                        {
                          title: 'External file',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'file',
                              ui: {
                                hidden: true,
                              }
                            },
                            data: {
                              type: BIQJsonSchemaType.String,
                              title: 'Data URL or Base64',
                              description: 'The base64 encoded file OR url',
                            },
                            fileName: {
                              type: BIQJsonSchemaType.String,
                              title: 'File name',
                              description: 'The name of the file',
                            },
                            mediaType: {
                              type: BIQJsonSchemaType.String,
                              title: 'Media type',
                              description: 'The media/MIME type',
                            }
                          },
                          required: ['type', 'data', 'fileName', 'mediaType'],
                        },
                        {
                          title: 'BIQ file',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'file',
                              ui: {
                                hidden: true,
                              }
                            },
                            file: {
                              type: BIQJsonSchemaType.Any,
                              title: 'File',
                              description: 'BIQ File object for files',
                              default: '${{ }}',
                            },
                          },
                          required: ['type', 'file'],
                        },
                        {
                          title: 'Reasoning',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'reasoning',
                              ui: {
                                hidden: true,
                              }
                            },
                            text: {
                              type: BIQJsonSchemaType.String,
                              title: 'Text',
                              description: 'The text part of the assistant message',
                              ui: {
                                component: 'textarea',
                                options: {
                                  editInModal: true,
                                  autoResize: true,
                                  minLines: 5,
                                  maxLines: 30,
                                }
                              }
                            },
                            signature: {
                              type: BIQJsonSchemaType.String,
                              title: 'Signature',
                              description: 'The signature of the assistant message',
                            }
                          },
                          required: ['type', 'text', 'signature'],
                        },
                        {
                          title: 'Tool call',
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              const: 'tool-call',
                              ui: {
                                hidden: true,
                              }
                            },
                            toolCallId: {
                              type: BIQJsonSchemaType.String,
                              title: 'Tool call ID',
                              description: 'The ID of the tool call',
                            },
                            toolName: {
                              type: BIQJsonSchemaType.String,
                              title: 'Tool name',
                              description: 'The name of the tool',
                            },
                            input: {
                              type: BIQJsonSchemaType.Any,
                              title: 'Input',
                              description: 'The input arguments of the tool call',
                              ui: {
                                options: {
                                  editInModal: true,
                                }
                              }
                            },
                          },
                          required: ['type', 'toolCallId', 'toolName', 'input'],
                        },
                      ],
                    },
                  }
                ],
              },
            },
            required: ['role', 'content'],
          },
          {
            type: BIQJsonSchemaType.Object,
            properties: {
              role: {
                title: 'Role',
                description: 'The role of the tool',
                type: BIQJsonSchemaType.String,
                const: 'tool',
              },
              content: {
                type: BIQJsonSchemaType.Array,
                title: 'Tool call results',
                description: 'The content of the tool call response',
                items: {
                  type: BIQJsonSchemaType.Object,
                  properties: {
                    type: {
                      type: BIQJsonSchemaType.String,
                      const: 'tool-result',
                      ui: {
                        hidden: true,
                      }
                    },
                    toolCallId: {
                      type: BIQJsonSchemaType.String,
                      title: 'Tool call ID',
                      description: 'The ID of the tool call',
                    },
                    toolName: {
                      type: BIQJsonSchemaType.String,
                      title: 'Tool name',
                      description: 'The name of the tool',
                    },
                    output: {
                      title: 'Output',
                      description: 'The output of the tool call',
                      discriminatorKey: 'type',
                      anyOf: [
                        {
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              title: 'Output type',
                              description: 'The type of the output',
                              type: BIQJsonSchemaType.String,
                              const: 'text',
                            },
                            value: {
                              type: BIQJsonSchemaType.String,
                              title: 'Text value',
                              description: 'The text result value',
                            },
                          },
                          required: ['type', 'value'],
                        },
                        {
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              title: 'Output type',
                              description: 'The type of the output',
                              const: 'json',
                            },
                            value: {
                              type: BIQJsonSchemaType.Any,
                              title: 'JSON value',
                              description: 'The JSON result value',
                              ui: {
                                options: {
                                  editInModal: true,
                                }
                              }
                            },
                          },
                          required: ['type', 'value'],
                        },
                        {
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              title: 'Output type',
                              description: 'The type of the output',
                              const: 'error-text',
                            },
                            value: {
                              type: BIQJsonSchemaType.String,
                              title: 'Error text',
                              description: 'The error text',
                            },
                          },
                          required: ['type', 'value'],
                        },
                        {
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              title: 'Output type',
                              description: 'The type of the output',
                              const: 'error-json',
                            },
                            value: {
                              type: BIQJsonSchemaType.Any,
                              title: 'Error JSON',
                              description: 'The error JSON value',
                              ui: {
                                options: {
                                  editInModal: true,
                                }
                              }
                            },
                          },
                          required: ['type', 'value'],
                        },
                        {
                          type: BIQJsonSchemaType.Object,
                          properties: {
                            type: {
                              type: BIQJsonSchemaType.String,
                              title: 'Output type',
                              description: 'The type of the output',
                              const: 'content',
                            },
                            value: {
                              type: BIQJsonSchemaType.Array,
                              title: 'Content',
                              description: 'Array of content items',
                              items: {
                                anyOf: [
                                  {
                                    title: 'Text',
                                    type: BIQJsonSchemaType.Object,
                                    properties: {
                                      type: {
                                        type: BIQJsonSchemaType.String,
                                        const: 'text',
                                        ui: {
                                          hidden: true,
                                        }
                                      },
                                      text: {
                                        type: BIQJsonSchemaType.String,
                                        title: 'Text',
                                        description: 'The text content',
                                      },
                                    },
                                    required: ['type', 'text'],
                                  },
                                  {
                                    title: 'External media',
                                    type: BIQJsonSchemaType.Object,
                                    properties: {
                                      type: {
                                        type: BIQJsonSchemaType.String,
                                        const: 'media',
                                        ui: {
                                          hidden: true,
                                        }
                                      },
                                      data: {
                                        type: BIQJsonSchemaType.String,
                                        title: 'Data URL or Base64',
                                        description: 'The base64 encoded media',
                                      },
                                      mediaType: {
                                        type: BIQJsonSchemaType.String,
                                        title: 'Media type',
                                        description: 'The media/MIME type',
                                      },
                                    },
                                    required: ['type', 'data', 'mediaType'],
                                  },
                                  {
                                    title: 'BIQ file media',
                                    type: BIQJsonSchemaType.Object,
                                    properties: {
                                      type: {
                                        type: BIQJsonSchemaType.String,
                                        const: 'media',
                                        ui: {
                                          hidden: true,
                                        }
                                      },
                                      data: {
                                        type: BIQJsonSchemaType.Any,
                                        title: 'Data',
                                        description: 'BIQ File object for media',
                                        default: '${{ }}',
                                      },
                                    },
                                    required: ['type', 'media'],
                                  },
                                ],
                              },
                            },
                          },
                          required: ['type', 'value'],
                        },
                      ],
                    },
                  },
                  required: ['type', 'toolCallId', 'toolName', 'output'],
                },
              },
            },
            required: ['role', 'content'],
          },
        ],
        discriminatorKey: 'role',
      },
      ui: {
        order: 2,
      }
    },
    prompt: {
      type: BIQJsonSchemaType.String,
      description: 'The prompt to send to the AI model to generate a response',
      title: 'Prompt',
      default: 'Your task is to...',
      minLength: 1,
      ui: {
        component: 'textarea',
        options: {
          editInModal: true,
          autoResize: true,
          minLines: 5,
          maxLines: 30,
          placeholder: 'Your task is to...',
        }
      }
    },
    maxLoopCount: {
      type: BIQJsonSchemaType.Integer,
      description: 'The maximum number of ai agent loops to run, defaults to unlimited',
      title: 'Max loop count',
      minimum: 1,
      default: 5,
      ui: {
        order: 5,
      }
    },
    maxTokens: {
      type: BIQJsonSchemaType.Integer,
      description: 'The maximum number of tokens to generate',
      title: 'Max tokens',
      default: AiDefaultParameters.maxTokens,
      ui: {
        order: 6,
      }
    },
    temperature: {
      type: BIQJsonSchemaType.Number,
      description: 'The temperature to use for the AI model (0-1)',
      title: 'Temperature',
      default: AiDefaultParameters.temperature,
      minimum: 0,
      maximum: 2,
      ui: {
        component: 'slider',
        order: 7,
        options: {
          step: 0.001,
        },
      },
    },

    enableTodoTool: {
      type: BIQJsonSchemaType.Boolean,
      description: 'Whether to enable the todo tool for the AI agent',
      title: 'Enable todo tool',
      default: false,
      ui: {
        order: 8,
        component: 'switch',
      }
    },
  },
  required: ['tools'],
};

/** The response schema for the AiAgentActor */
export const DeprecatedAiAgentLoopStatusPortResultSchema = z.object({
  type: z.literal('ai-agent-loop'),
  response: z.string()
    .describe('The current response from the AI agent loop'),
  toolCalls: z.array(AiToolCallSchema).nullish()
    .describe('The tool calls made by the AI model'),
  meta: z.object({
    model: z.string()
      .describe('The model used to generate the response'),
    usage: z.object({
      promptTokens: z.number().int()
        .describe('The number of tokens in the prompt'),
      completionTokens: z.number().int()
        .describe('The number of tokens in the completion'),
      totalTokens: z.number().int()
        .describe('The total number of tokens used'),
    }),
  }),
});

export type DeprecatedAiAgentLoopStatusPortResult = z.infer<typeof DeprecatedAiAgentLoopStatusPortResultSchema>;

/** The response schema for the AiAgentActor */
export const DeprecatedAiAgentToolResultStatusPortResultSchema = AiToolMessageResultSchema;

export type DeprecatedAiAgentToolResultStatusPortResult = z.infer<typeof DeprecatedAiAgentToolResultStatusPortResultSchema>;

export const DeprecatedAiAgentStatusPortResultSchema = z.discriminatedUnion('type', [
  DeprecatedAiAgentLoopStatusPortResultSchema,
  DeprecatedAiAgentToolResultStatusPortResultSchema,
]);

export type DeprecatedAiAgentStatusPortResult = z.infer<typeof DeprecatedAiAgentStatusPortResultSchema>;

/** The response schema for the AiAgentActor */
export const DeprecatedAiAgentLoopActorDoneResultSchema = z.object({
  response: z.array(BIQAiMessageSchema)
    .describe('The full chat history of the AI agent'),
  meta: z.object({
    model: z.string()
      .describe('The model used to generate the response'),
    endReason: z.enum(AiFinishReason)
      .describe('The reason the AI agent loop ended'),
    usage: z.object({
      promptTokens: z.number().int()
        .describe('The number of tokens in the prompt'),
      completionTokens: z.number().int()
        .describe('The number of tokens in the completion'),
      totalTokens: z.number().int()
        .describe('The total number of tokens used'),
    }),
  }),
});

export type DeprecatedAiAgentLoopActorDoneResult = z.infer<typeof DeprecatedAiAgentLoopActorDoneResultSchema>;
```

## actorSchemas/task/interface

**Source:** `actorSchemas/task/interface.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchemaType, BIQJsonSchema, BIQInterfacePageDataSchema } from '../../schemas/index.js';

/** the interface event source port id */
export const INTERFACE_EVENT_SOURCE_PORT_ID = 'SPRTevent00';

/** The options schema for the InterfaceActor */
export const InterfaceActorOptionsSchema = z.object({
  page: BIQInterfacePageDataSchema
    .describe('The page data to build the components for the interface actor'),
  defaultValues: z.record(z.string(), z.any()).nullish()
    .describe('The default values to inject into the url as query params'),
  autoSubmitAfterSeconds: z.number().int().min(0).nullish()
    .describe('Auto submit the form after it has been opened after a certain number of seconds'),
  timeoutInMinutes: z.number().min(0).nullish()
    .describe('How long to wait for the interface actor to submit the form before timing out. Default to no timeout.'),
  onSubmit: z.discriminatedUnion('type', [
    z.object({
      type: z.literal('nextInterface')
        .describe('when the interface form is successfully submitted, redirect to the next interface rendered in the flow'),
      loadingMessage: z.string().nullish()
        .describe('The message to show while the next interface is loading'),
    }),
    z.object({
      type: z.literal('successMessage'),
      successMessage: z.string().nullish()
        .describe('The message to show when the interface form is successfully submitted'),
    }),
    z.object({
      type: z.literal('urlRedirect'),
      url: z.url()
        .describe('The url to redirect to when the interface form is successfully submitted'),
    })
  ])
    .describe('What page to redirect to when the interface form is submitted'),
  showProgressStatus: z.boolean().nullish()
    .describe('Show real-time flow progress and actor status on the waiting page. Requires onSubmit type to be nextInterface.'),
  emitPage: z.boolean().nullish()
    .describe('Whether to emit the page data on the meta port'),
});

export type InterfaceActorOptions = z.infer<typeof InterfaceActorOptionsSchema>;

export const InterfaceActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    page: {
      type: BIQJsonSchemaType.Any,
      title: 'Page',
      description: 'The page data to render for the interface trigger',
      ui: {
        component: 'modal',
        options: {
          language: 'yaml',
        },
      }
    },
    defaultValues: {
      type: BIQJsonSchemaType.Any,
      title: 'Default values',
      description: 'The default values to inject into the url as query params',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
    autoSubmitAfterSeconds: {
      type: BIQJsonSchemaType.Integer,
      title: 'Auto submit after seconds',
      description: 'Auto submit the form after it has been opened after a certain number of seconds',
    },
    timeoutInMinutes: {
      type: BIQJsonSchemaType.Number,
      title: 'Timeout in minutes',
      description: 'How long to wait for the interface actor to submit the form before timing out. Default to infinite timeout.',
    },
    onSubmit: {
      discriminatorKey: 'type',
      anyOf: [
        {
          type: BIQJsonSchemaType.Object,
          title: 'On submit',
          description: 'The action to perform when the interface form is successfully submitted',
          properties: {
            type: {
              type: BIQJsonSchemaType.String,
              title: 'On submit type',
              description: 'The type of on submit action',
              const: 'nextInterface',
              default: 'Next Interface',
            },
            loadingMessage: {
              type: BIQJsonSchemaType.String,
              title: 'Loading message',
              description: 'The message to show while the next interface is loading',
              ui: {
                options: {
                  placeholder: 'Loading...',
                },
              },
            },
          },
          required: ['type'],
        },
        {
          type: BIQJsonSchemaType.Object,
          title: 'On submit',
          description: 'The action to perform when the interface form is successfully submitted',
          properties: {
            type: {
              type: BIQJsonSchemaType.String,
              title: 'Type',
              description: 'The type of on submit action',
              const: 'successMessage',
              default: 'Success Message',
            },
            successMessage: {
              type: BIQJsonSchemaType.String,
              title: 'Success message',
              description: 'The message to show when the interface form is successfully submitted',
              ui: {
                options: {
                  placeholder: 'Success!',
                },
              },
            },
          },
          required: ['type'],
        },
        {
          type: BIQJsonSchemaType.Object,
          title: 'On submit',
          description: 'The action to perform when the interface form is successfully submitted',
          properties: {
            type: {
              type: BIQJsonSchemaType.String,
              title: 'On submit type',
              description: 'The type of on submit action',
              const: 'urlRedirect',
              default: 'URL Redirect',
            },
            url: {
              type: BIQJsonSchemaType.String,
              title: 'URL',
              description: 'The url to redirect to when the interface form is successfully submitted',
              format: 'uri',
            },
          },
          required: ['type', 'url'],
        },
      ],
    },
    showProgressStatus: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Show progress status',
      description: 'Show real-time flow progress and actor status on the waiting page. Requires onSubmit type to be nextInterface.',
      ui: {
        component: 'switch',
      },
    },
    emitPage: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit page',
      description: 'Whether to emit the page data on the meta port',
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['page', 'onSubmit'],
};

/** the message response schema for the InterfaceActor */
export const InterfaceActorMetadataReceiveResponseSchema = z.object({
  interfaceId: z.string()
    .describe('The interface id to use for the interface session'),
  interfaceUrl: z.string()
    .describe('The url the interface page lives under'),
  page: BIQInterfacePageDataSchema.optional()
    .describe('The page data to render for the interface actor'),
});

export type InterfaceActorMetadataReceiveResponse = z.infer<typeof InterfaceActorMetadataReceiveResponseSchema>;

export const InterfaceActorResultSchema = z.object({
  meta: z.object({
    interfaceId: z.string()
      .describe('The interface id that was used to submit the form'),
    submissionInterfaceId: z.string()
      .describe('The interface id that was used to submit the form and will be used to render the next page'),
    ipAddress: z.string().optional()
      .describe('The IP address of the user who submitted the form'),
  }),
  body: z.record(z.string(), z.any())
    .describe('The body of the interface submission'),
});

export type InterfaceActorResult = z.infer<typeof InterfaceActorResultSchema>;
```

## actorSchemas/task/interfaceStatus

**Source:** `actorSchemas/task/interfaceStatus.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchemaType, BIQJsonSchema } from '../../schemas/index.js';
import { BIQFormComponentZodSchema } from '../../formComponents/form.js';

/** The options schema for the InterfaceStatusActor */
export const InterfaceStatusActorOptionsSchema = z.object({
  component: BIQFormComponentZodSchema.optional()
    .describe('The component to add/update to the status area of a waiting for interface page'),
  emitComponents: z.boolean().optional()
    .describe('Whether to emit the components to the status area of a waiting for interface page'),
  order: z.enum(['append', 'prepend']).optional()
    .describe('The order to add the component if not already present to the status area of a waiting for interface page'),
});

export type InterfaceStatusActorOptions = z.infer<typeof InterfaceStatusActorOptionsSchema>;

export const InterfaceStatusActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    component: {
      type: BIQJsonSchemaType.Any,
      title: 'Component',
      description: 'The component to add/update to the status area of a waiting for interface page',
      ui: {
        component: 'modal',
        options: {
          language: 'yaml',
        },
      }
    },
    emitComponents: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit components',
      description: 'Whether to emit the components to the status area of a waiting for interface page',
    },
    order: {
      type: BIQJsonSchemaType.String,
      title: 'Order',
      description: 'The order to add the component if not already present to the status area of a waiting for interface page',
      enum: ['append', 'prepend'],
      default: 'prepend',
    },
  },
  required: [],
};

/** the message response schema for the InterfaceStatusActor */
export const InterfaceStatusActorResultSchema = z.object({
  status: z.string()
    .describe('The status of the interface'),
  statusComponents: z.array(BIQFormComponentZodSchema).optional()
    .describe('The components to add/update to the status area of a waiting for interface page'),
});

export type InterfaceStatusActorResult = z.infer<typeof InterfaceStatusActorResultSchema>;
```

## actorSchemas/task/mcpServer

**Source:** `actorSchemas/task/mcpServer.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

/** The options for the McpServerActor */
export const McpServerActorOptionsSchema = z.object({
  responseTimeoutSeconds: z.number()
    .int()
    .min(1)
    .max(300)
    .default(60)
    .describe('Maximum time in seconds to wait for a tool call to complete'),
  serverName: z.string()
    .max(128)
    .nullish()
    .describe('Custom name for the MCP server (shown to clients during initialization)'),
  serverVersion: z.string()
    .max(32)
    .default('1.0.0')
    .describe('Version string for the MCP server'),
});

export type McpServerActorOptions = z.infer<typeof McpServerActorOptionsSchema>;

export const McpServerActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    responseTimeoutSeconds: {
      type: BIQJsonSchemaType.Integer,
      description: 'Maximum time in seconds to wait for a tool call to complete',
      title: 'Response timeout (seconds)',
      default: 60,
      minimum: 1,
      maximum: 300,
      ui: {
        order: 0,
      },
    },
    serverName: {
      type: BIQJsonSchemaType.String,
      description: 'Custom name for the MCP server (shown to clients during initialization)',
      title: 'Server name',
      ui: {
        component: 'input',
        order: 1,
        options: {
          placeholder: 'e.g. Customer data tools',
        },
      },
    },
    serverVersion: {
      type: BIQJsonSchemaType.String,
      description: 'Version string for the MCP server',
      title: 'Server version',
      default: '1.0.0',
      ui: {
        component: 'input',
        order: 2,
      },
    },
  },
};
```

## actorSchemas/task/python

**Source:** `actorSchemas/task/python.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

export const PythonActorCodeSchema = z.string().min(1);

/** The options for the PythonActor */
export const PythonActorOptionsSchema = z.object({
  emitArrayAsSingleMessage: z.boolean().nullish()
    .describe('Emit the array as a single message instead of an array of messages, defaults to true').default(true),
  dependencies: z.array(z.string()).nullish()
    .describe('List of Python package dependencies (e.g., ["pandas>=2.0.0", "numpy>=1.24.0"]). These will be installed using UV').default([]),
  env: z.array(z.object({
    name: z.string()
      .regex(/^[A-Z0-9_]+$/, 'Environment variable name must contain only uppercase letters, numbers and underscores')
      .regex(/^(?!TMPDIR$)/, 'Environment variable name cannot be TMPDIR')
      .regex(/^(?!HOME$)/, 'Environment variable name cannot be HOME')
      .regex(/^(?!PYTHONUNBUFFERED$)/, 'Environment variable name cannot be PYTHONUNBUFFERED')
      .regex(/^(?!UV_CACHE_DIR$)/, 'Environment variable name cannot be UV_CACHE_DIR')
      .regex(/^(?!UV_PROJECT_ENVIRONMENT$)/, 'Environment variable name cannot be UV_PROJECT_ENVIRONMENT')
      .regex(/^(?!PYTHONUSERBASE$)/, 'Environment variable name cannot be PYTHONUSERBASE')
      .describe('Environment variable name (must contain only uppercase letters, numbers and underscores)'),
    value: z.string().nullish()
      .describe('Environment variable value')
  })).nullish().default([])
    .describe('List of environment variables to pass to the Python runtime'),
});

export type PythonActorOptions = z.infer<typeof PythonActorOptionsSchema>;

export const PythonActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    emitArrayAsSingleMessage: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit array as single message',
      description: 'Emit the array as a single message instead of an array of messages',
      default: true,
      ui: {
        component: 'switch',
      },
    },
    dependencies: {
      type: BIQJsonSchemaType.Array,
      title: 'Python dependencies',
      description: 'List of Python package dependencies (e.g., "pandas>=2.0.0", "numpy>=1.24.0"). These will be installed using UV',
      items: {
        type: BIQJsonSchemaType.String,
      },
    },
    env: {
      type: BIQJsonSchemaType.Array,
      title: 'Environment variables',
      description: 'List of environment variables to pass to the Python runtime',
      items: {
        type: BIQJsonSchemaType.Object,
        properties: {
          name: {
            type: BIQJsonSchemaType.String,
            title: 'Name',
            description: 'Environment variable name (must contain only uppercase letters, numbers and underscores)',
            pattern: '^(?!TMPDIR$)(?!HOME$)(?!PYTHONUNBUFFERED$)(?!UV_CACHE_DIR$)(?!UV_PROJECT_ENVIRONMENT$)(?!PYTHONUSERBASE$)[A-Z0-9_]+$'
          },
          value: {
            type: BIQJsonSchemaType.String,
            title: 'Value',
            description: 'Environment variable value'
          }
        },
        required: ['name']
      }
    }
  },
};

/** The response schema for the PythonActor */
export const PythonActorResultSchema = z.any();

export type PythonActorResult = z.infer<typeof PythonActorResultSchema>;
```

## actorSchemas/task/router

**Source:** `actorSchemas/task/router.ts`

```typescript
import { ZodObject, z } from 'zod';

import { RuntimeActorSourcePort } from '../../schemas/runtime.js';
import { DEFAULT_SOURCE_PORT_ID } from '../../canvas.js';

export enum RouterActorEmitType {
  SingleRoute = 'singleRoute',
  MultiRoute = 'multiRoute',
}
/** The options schema builder for the RouterActor since it changes for the sourcePorts configuration for the actor */
export const buildRouterActorOptionsSchema = (sourcePorts: RuntimeActorSourcePort[]): ZodObject<any> => z.object({ // eslint-disable-line @typescript-eslint/no-explicit-any
  emitType: z.enum(RouterActorEmitType).nullish()
    .describe('How the router actor will function, either can be singleRoute or multiRoute where singleRoute emits only on the first true condition and multiRoute emits on all true condition route. Defaults to singleRoute'),
  conditions: z.record(z.string(), z.any()).superRefine((value, ctx) => {
    const invalidRoutes: string[] = [];

    for (const routeName of Object.keys(value)) {
      const port = sourcePorts.find((port) => port.name === routeName);
      // if the port is not found, add it to the invalidRoutes list
      if (!port) {
        invalidRoutes.push(routeName);
      // if the route is the default port, add an issue
      } else if (port.id === DEFAULT_SOURCE_PORT_ID) {
        ctx.addIssue({
          code: 'invalid_value',
          path: [routeName],
          values: [routeName],
          message: `Route name '${routeName}' is reserved for the default route`,
        });
      }
    }
    // if there are no invalid ports, return the value
    if (invalidRoutes.length === 0) return;
    // if there are invalid ports, add an issue for all invalid routes
    ctx.addIssue({
      code: 'unrecognized_keys',
      keys: invalidRoutes,
      message: `Unrecognized Route name(s) in conditions: ${invalidRoutes.join(', ')}`,
    });
  })
    .describe('The conditions for the routes on if to emit, the keys for the conditions are the route name provided in the routes section, the value is the boolean condition to be evaluated and determine if the route should emit a message'),
});

export type RouterActorOptions = {
  emitType?: RouterActorEmitType,
  conditions: { [portName: string]: boolean },
};

/** The result schema for the RouterActor */
export const RouterActionResultSchema = z.string().describe('The port name that the message was emitted from');

export type RouterActionResult = z.infer<typeof RouterActionResultSchema>;
```

## actorSchemas/task/sendEmail

**Source:** `actorSchemas/task/sendEmail.ts`

```typescript
import { z } from 'zod';

import { BIQFileSchema, BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

const emailRegex = /^(?:"?([^"]*)"?\s)?(?:<)?([a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*)(>)?$/;

/** The options schema for the SendEmailActor */
export const SendEmailActorOptionsSchema = z.object({
  to: z.string().refine((value) => {
    const emails = value.split(',');
    return emails.every((email) => emailRegex.test(email.trim()));
  }, 'Invalid email address(es) provided')
    .describe('The email address(es) to send the email to, multiple emails should be a comma separated list of emails'),
  subject: z.string()
    .describe('The subject of the email to send'),
  cc: z.string().refine((value) => {
    const emails = value.split(',');
    return emails.every((email) => emailRegex.test(email.trim()));
  }, 'Invalid email address(es) provided').nullish()
    .describe('Any email address(es) to cc the email to, multiple emails should be a comma separated list of emails'),
  bcc: z.string().refine((value) => {
    const emails = value.split(',');
    return emails.every((email) => emailRegex.test(email.trim()));
  }, 'Invalid email address(es) provided').nullish()
    .describe('Any email address(es) to bcc the email to, multiple emails should be a comma separated list of emails'),
  textBody: z.string().nullish()
    .describe('The text body of the email to send (is required if html body is not defined)'),
  htmlBody: z.string().nullish()
    .describe('The html body of the email to send (is required if text body is not defined'),
  attachments: z.union([z.array(BIQFileSchema), BIQFileSchema]).nullish()
    .describe('The attachments included in the email sent'),
}).refine((data) => data.textBody || data.htmlBody, {
  error: 'Either textbody or htmlbody must be defined',
  path: ['textbody', 'htmlbody'] // specify the fields this refinement is about
});

export type SendEmailActorOptions = z.infer<typeof SendEmailActorOptionsSchema>;

export const SendEmailActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    to: {
      type: BIQJsonSchemaType.String,
      title: 'To',
      description: 'The email address(es) to send the email to, multiple emails should be a comma separated list of emails',
    },
    subject: {
      type: BIQJsonSchemaType.String,
      title: 'Subject',
      description: 'The subject of the email to send',
    },
    cc: {
      type: BIQJsonSchemaType.String,
      title: 'Cc',
      description: 'Any email address(es) to cc the email to, multiple emails should be a comma separated list of emails',
    },
    bcc: {
      type: BIQJsonSchemaType.String,
      title: 'Bcc',
      description: 'Any email address(es) to bcc the email to, multiple emails should be a comma separated list of emails',
    },
    textBody: {
      type: BIQJsonSchemaType.String,
      title: 'Text body',
      description: 'The text body of the email to send (is required if html body is not defined)',
      ui: {
        component: 'textarea',
      },
    },
    htmlBody: {
      type: BIQJsonSchemaType.String,
      title: 'HTML body',
      description: 'The html body of the email to send (is required if text body is not defined)',
      ui: {
        component: 'code',
        options: {
          language: 'html',
        },
      },
    },
    attachments: {
      type: BIQJsonSchemaType.Array,
      title: 'Attachments',
      description: 'The attachments included in the email sent',
      default: [
        '${{}}',
      ],
      items: {
        type: BIQJsonSchemaType.Object,
        default: '${{}}',
        ui: {
          component: 'file',
          options: {
            multiple: true,
          },
        },
      }
    },
  },
  required: ['to', 'subject'],
};

export const SendEmailActorResultSchema = z.object({
  meta: z.object({
    /** the borgiq email id of the email sent */
    emailId: z.string()
      .describe('The borgiq email id of the email sent'),
  }),
  to: z.string()
    .describe('The email address(es) the email was sent to'),
  cc: z.string().nullish()
    .describe('The email addresses(es) the email was cc\'d to'),
  bcc: z.string().nullish()
    .describe('The email addresses(es) the email was bcc\'d to'),
  subject: z.string()
    .describe('The subject of the email sent'),
  textBody: z.string().nullish()
    .describe('The text body of the email sent'),
  htmlBody: z.string().nullish()
    .describe('The html body of the email sent'),
  attachments: z.array(BIQFileSchema).nullish()
    .describe('The attachments included in the email sent'),
});

export type SendEmailActorResult = z.infer<typeof SendEmailActorResultSchema>;
```

## actorSchemas/task/webhookResponse

**Source:** `actorSchemas/task/webhookResponse.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

/** The options schema for the WebhookResponseActor */
export const WebhookResponseActorOptionsSchema = z.object({
  statusCode: z.number().nullish()
    .describe('The status code of the response to return to the webhook request, defaults to 200'),
  body: z.unknown().nullish()
    .describe('The body of the response to return to the webhook request'),
  headers: z.record(z.string(), z.unknown()).nullish()
    .describe('The headers of the response to return to the webhook request'),
});

export type WebhookResponseActorOptions = z.infer<typeof WebhookResponseActorOptionsSchema>;

export const WebhookResponseActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    statusCode: {
      type: BIQJsonSchemaType.Number,
      title: 'Status code',
      description: 'The status code of the response to return to the webhook request, defaults to 200',
      default: 200,
    },
    body: {
      type: BIQJsonSchemaType.Any,
      title: 'Body',
      description: 'The body of the response to return to the webhook request',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
    headers: {
      type: BIQJsonSchemaType.Any,
      title: 'Headers',
      description: 'The headers of the response to return to the webhook request',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
  },
};

/** The result schema for the WebhookResponseActor */
export const WebhookResponseActorResultSchema = z.object({
  statusCode: z.number()
    .describe('The status code of the response to return to the webhook request'),
  body: z.unknown()
    .describe('The body of the response to return to the webhook request'),
  headers: z.record(z.string(), z.unknown()).nullable()
    .describe('The headers of the response to return to the webhook request'),
});

export type WebhookResponseActorResult = z.infer<typeof WebhookResponseActorResultSchema>;
```
