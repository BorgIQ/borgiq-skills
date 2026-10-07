# actorSchemas/task/deprecatedAiAgent

Generated from the platform's runtime types. Do not edit.

Legacy: DeprecatedAiAgent is kept only so existing canvases load. Build new agents with AiAgentActor.

DeprecatedAiAgent options and results.

See also: [ai/index](../../../ai/index.md), [schemas/jsonSchema](../../schemas/jsonSchema.md).

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
    .describe('The model to use for the AI provider. Defaults to gpt-6-luna if not provided'),
  prompt: z.string().nullish()
    .describe('The prompt to send to the AI model to generate a response'),
  temperature: z.number().min(0).max(2).nullish()
    .describe('The sampling temperature (0-2); lower is more deterministic. Unset uses the model\'s default. Claude models take at most 1 (a higher value is sent as 1). Ignored by models that take none: OpenAI reasoning models (o-series, GPT-5 and later) and Claude Opus 4.7 and later, Sonnet 5 and Fable 5'),
  maxTokens: z.number().int().positive().nullish()
    .describe('The maximum number of tokens to generate. Unset uses the model\'s output limit'),
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
      description: 'The maximum number of tokens to generate. Unset uses the model\'s output limit',
      title: 'Max tokens',
      default: AiDefaultParameters.maxTokens,
      ui: {
        order: 6,
      }
    },
    temperature: {
      type: BIQJsonSchemaType.Number,
      description: 'The sampling temperature (0-2); lower is more deterministic. Unset uses the model\'s default. Claude models take at most 1 (a higher value is sent as 1). Ignored by models that take none: OpenAI reasoning models (o-series, GPT-5 and later) and Claude Opus 4.7 and later, Sonnet 5 and Fable 5',
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
  reasoning: z.string().nullish()
    .describe('The model\'s thinking / reasoning for this turn, when the provider returned it. Clipped by the orchestrator; absent when the model did not think or the provider hides it.'),
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
