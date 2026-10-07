# AI Models

How to write the `model` option of AiActor, AiRouterActor, AiAgentActor and AgentHarnessActor: the three reference
forms, which models each actor accepts, what an unset `model` runs, and which model to pick.

## Rules

- **Always set `model`.** The fallbacks differ per actor and are rarely the model you want.
- Pick from the [picks table](#picks) for new work. The provider enums also keep retired ids, so that existing actors
  still load.
- The workspace needs an AI credential for the model's provider (for `<slug>/<model-id>`, a custom provider with that
  slug), or the run fails fast.

## Reference forms

| Form | Example | Resolves to |
|---|---|---|
| Known model id | `claude-sonnet-5`, `gpt-6-luna` | The built-in provider's credential |
| `<provider>/<model-id>` | `openai/gpt-6` | That built-in provider, for a model the platform does not list |
| `<slug>/<model-id>` | `openrouter/moonshotai/kimi-k2` | The workspace [custom provider](custom-ai-providers.md) with that slug |

- A bare id that is not a known model (`llama3.1:8b`) is rejected when the canvas is validated.
- A slug the workspace does not have only warns in the editor and in `borgiq canvases validate`; the actor fails at run
  time: `Model "<ref>" does not exist: no custom provider named "<slug>" in this workspace. …`.
- `openai/gpt-4o-mini` names the known model `gpt-4o-mini`, so the rules for known ids apply to it.
- `borgiq ai-providers models` lists every reference usable in the workspace; its `agent` column says which ones the AI
  Agent accepts.

## Which actor accepts what

| Actor | Accepts | Unset `model` runs |
|---|---|---|
| AiActor, AiRouterActor | All three forms; any known id, dated snapshots included | `gpt-6-luna` |
| AiAgentActor | All three forms. A known id must be an agent model; a custom catalog entry with `agent: false` is refused at run time | The runtime's default Anthropic model (the editor fills in `claude-sonnet-5`) |
| AgentHarnessActor | Agent models only, per `harness`: `claude` the Anthropic ones, `codex` the OpenAI ones, `opencode` and `pi` all. No custom providers | The harness's first model: `claude-sonnet-5`, or `gpt-6.1-sol` for `codex` |
| DeprecatedAiAgent (legacy) | Agent models | `gpt-6-luna` |

The agent models are the curated `AiAgentModels`: each provider file's `…AgentModels` list in
[typescript/ai/anthropic.md](typescript/ai/anthropic.md), [openAi.md](typescript/ai/openAi.md),
[google.md](typescript/ai/google.md) and [xAi.md](typescript/ai/xAi.md), which also hold every model id and its price.
A known id outside them fails AiAgentActor validation: `Model "<id>" is not one of the AI Agent actor's <provider>
models (…)`.

## Picks

USD per million input / output tokens, as the platform meters them.

| Model | $ in / out | Use |
|---|---|---|
| `claude-haiku-5-5` | 0.10 / 0.50 | Start here on AiActor and AiRouterActor: classification, extraction, routing, short generation. A prompt over 100K tokens bills 0.50 / 2.50. Thinks by default, billed as output and counted in `maxTokens` |
| `claude-haiku-4-5` | 1 / 5 | Takes `temperature`; the cheap AiAgentActor pick, with `thinkingLevel: off` |
| `claude-sonnet-5`, `gpt-6.1-sol` | 2 / 10 | The step up; the agent default for multi-step work (Sonnet: 128K output) |
| `claude-opus-5-5` | 4 / 20 | Hard reasoning, complex agents |
| `claude-opus-5`, `claude-opus-4-8` | 5 / 25 | |
| `claude-fable-5-1`, `gpt-6-astra` | 10 / 50 | Top tiers |
| `gpt-6-luna`; `gpt-5.6-luna` | 0.10 / 0.50; 0.20 / 1.20 | Budget, cheap high-volume agents |
| `gpt-5.6-terra` | 2 / 12 | |
| `gemini-3.5-flash-lite` | 0.30 / 2.50 | Simple classification and extraction, cheap agents |
| `grok-4.7` | 2 / 6 | From 200K input tokens the whole request bills double (all Grok 4.3+ models) |
| `gpt-5.5-pro`, `gpt-5.4-pro` | 30 / 180 | Research-grade single calls; not agent models |

OpenAI bills a prompt over 272K input tokens at 2× input and 1.5× output for the whole request. On an agent, pair a
cheap model with `thinkingLevel: off`: the default `medium` thinking is billed as output tokens every turn.

## Retired ids

Calls to retired ids fail or are redirected by the provider: Claude 3.x, Opus 4, Sonnet 4 and Opus 4.1, the o-series
(`o1`, `o3`, `o3-mini`, `o4-mini`), `gpt-4.1-nano`, the Gemini 2.0 family, `gemini-3-pro-preview`, `grok-4-0709`,
`grok-4-fast-*` and `grok-code-fast-1` (xAI serves `grok-4-fast-reasoning` and `grok-code-fast-1` with `grok-4.3`
and `grok-build-0.1`). The dated `gpt-5` and `gpt-5-mini` snapshots shut down on 2026-12-11. Google serves the
Gemini 2.5 models only to projects that already used them.
