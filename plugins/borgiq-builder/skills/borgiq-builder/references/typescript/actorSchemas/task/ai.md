# actorSchemas/task/ai

Generated from the platform's runtime types. Do not edit.

AiActor options and result.

See also: [ai/index](../../ai/index.md), [ai/modelRef](../../ai/modelRef.md).

## actorSchemas/task/ai

**Source:** `actorSchemas/task/ai.ts`

```typescript
import { z } from 'zod';

import { AiModel, AiModelRefSchema, AiDefaultParameters, BIQAiMessageSchema, AiToolCallSchema, buildAiModelSuggestionUiOptions } from '../../ai/index.js';
import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

/** The options for the AIActor */
export const AiActorOptionsSchema = z.object({
  model: AiModelRefSchema.nullish()
    .describe('The model to use: a known model id, "<provider>/<model-id>" for a built-in provider\'s unlisted model, or "<custom-provider-slug>/<model-id>" for a model served by one of the workspace\'s custom providers (e.g. "fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct"). Defaults to gpt-6-luna if not provided'),
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

/** Curated suggestions: every known model, grouped by provider. The field is free text, so a
 * workspace's custom providers' models (`<slug>/<id>`) are typed or merged in by the web. */
const modelSuggestionUi = buildAiModelSuggestionUiOptions(Object.values(AiModel));

export const AiActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    model: {
      type: BIQJsonSchemaType.String,
      description: 'The model to use: a known model id, "<provider>/<model-id>" for a built-in provider\'s unlisted model, or "<custom-provider-slug>/<model-id>" for a model served by one of the workspace\'s custom providers (e.g. "fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct"). Defaults to gpt-6-luna if not provided',
      title: 'Model',
      default: AiDefaultParameters.model,
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
