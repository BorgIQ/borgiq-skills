# ai/modelRef

Generated from the platform's runtime types. Do not edit.

Model references: the accepted `<model-id>` and `<slug>/<model-id>` forms, slug rules and reserved slugs.

See also: [ai/lib](lib.md), [ai/openAi](openAi.md), [ai/anthropic](anthropic.md), [ai/google](google.md), [ai/xAi](xAi.md).

## ai/modelRef

**Source:** `ai/modelRef.ts`

```typescript
import { z } from 'zod';

import {
  AI_MODEL_PROVIDERS,
  AiModelInformation,
  AiProvider,
  AiProviderLabels,
  convertCostPerMTokensToCostPer1kTokens,
} from './lib.js';
import { OpenAiModelInformationMap } from './openAi.js';
import { AnthropicModelInformationMap } from './anthropic.js';
import { GoogleModelInformationMap } from './google.js';
import { xAiModelInformationMap } from './xAi.js';

/**
 * Model references.
 *
 * A model is referenced by a string, the `AiModelRef`. Three forms are accepted:
 *
 * - a **known** model id — any member of the build-time `AiModel` enum (`gpt-4o-mini`,
 *   `claude-sonnet-4-5`, ...). Resolves to its provider and pricing through the static
 *   `AiModelInformationMap`.
 * - a **built-in provider's** model the build does not list: `<provider>/<model-id>` where
 *   `<provider>` is a built-in model provider (`BuiltinAiProvider`: every entry of
 *   `AI_MODEL_PROVIDERS` except `custom`, which is never a prefix) — `openai/gpt-6`.
 * - a **custom provider's** model: `<slug>/<model-id>` where `<slug>` names one of the workspace's
 *   custom providers (an AI setting with `provider: custom` — any OpenAI-compatible endpoint,
 *   gateway or self-hosted server): `fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct`,
 *   `openrouter/moonshotai/kimi-k2`. Only the FIRST `/` separates the slug, so nested model ids
 *   pass through. The slug is chosen when the custom provider is added (kebab-case, and never a
 *   built-in provider id); which slugs exist is workspace data, so a reference to a slug that
 *   does not exist fails at resolution time, not at parse time.
 *
 * A bare id that is neither a known model nor `<something>/<model-id>` is rejected — a typo in a
 * built-in model id must not silently route anywhere.
 *
 * The metadata for a custom reference comes from the custom provider's model catalog (the AI
 * setting's `data.models`, see `AiCustomModelCatalogEntrySchema`) when the id is listed there,
 * from the static record when the model id is itself a known model served through a gateway
 * (`openrouter/gpt-4o-mini`), and from defaults (label = id, zero cost) otherwise.
 */

/** Separator between the provider prefix / slug and the model id of a qualified reference. */
export const AI_MODEL_REF_SEPARATOR = '/';

/** `ai_logs.model` is VARCHAR(255); references are capped to fit. */
export const AI_MODEL_REF_MAX_LENGTH = 255;

/** Output-token cap assumed for a custom model whose catalog entry does not say. */
export const DEFAULT_CUSTOM_MODEL_MAX_TOKENS = 8192;

/** Context window assumed for a custom model whose catalog entry does not say (pi needs one). */
export const DEFAULT_CUSTOM_MODEL_CONTEXT_WINDOW = 128_000;

/** A custom provider's slug: short kebab-case, so it reads as a path segment of a model reference. */
export const AI_PROVIDER_SLUG_REGEX = /^[a-z0-9][a-z0-9-]{0,39}$/;

/** Slugs a custom provider may not take: every provider id, so `<slug>/<id>` never shadows
 * `<built-in provider>/<id>` (or the `custom` provider id itself). */
export const RESERVED_AI_PROVIDER_SLUGS: ReadonlySet<string> = new Set<string>(Object.values(AiProvider));

const KNOWN_MODEL_INFORMATION: Record<string, AiModelInformation> = {
  ...OpenAiModelInformationMap,
  ...AnthropicModelInformationMap,
  ...GoogleModelInformationMap,
  ...xAiModelInformationMap,
};

/** A built-in model provider: one a `<provider>/<model-id>` reference may name, and the only
 * providers whose models the build-time catalog lists. Excludes `custom` (reached through a
 * custom provider's slug) and the agent-harness credential providers (`claude-code`, `codex`). */
export type BuiltinAiProvider = Exclude<AiProvider, AiProvider.Custom | AiProvider.ClaudeCode | AiProvider.Codex>;

/** The built-in providers a `<provider>/<model-id>` reference may name (every model provider but `custom`). */
const BUILTIN_MODEL_PROVIDER_SET: ReadonlySet<string> = new Set<string>(
  AI_MODEL_PROVIDERS.filter((provider) => provider !== AiProvider.Custom),
);

/** Whether a string is a built-in model provider id. */
function isBuiltinAiProvider(prefix: string): prefix is BuiltinAiProvider {
  return BUILTIN_MODEL_PROVIDER_SET.has(prefix);
}

/** Whether a string is an acceptable custom provider slug (shape + not a reserved provider id). */
export function isValidCustomProviderSlug(slug: unknown): slug is string {
  return typeof slug === 'string' && AI_PROVIDER_SLUG_REGEX.test(slug) && !RESERVED_AI_PROVIDER_SLUGS.has(slug);
}

/** Connection-type name suffixes that name the auth method rather than the vendor (`groq-bearer` → `groq`). */
const CONNECTION_TYPE_AUTH_SUFFIX_REGEX = /-(bearer|apikey|api-key|oauth2|oauth1|basic|pat|token|awskeybased|awsrolebased)$/;

/** Connection-type name prefixes that name no vendor, so they suggest no slug. */
const NON_VENDOR_CONNECTION_TYPE_REGEX = /^(generic-|custom)/;

/**
 * The slug to prefill for a custom provider backed by a connection of the given type: the type's
 * name without its auth-method suffix (`groq-bearer` → `groq`, `openrouter-bearer` → `openrouter`).
 * `undefined` for generic and custom types, for a name that is a reserved provider id (an
 * `openai-bearer` connection is fine behind a custom provider, but `openai` cannot be its slug),
 * or for anything that is not a valid slug.
 */
export function suggestCustomProviderSlug(connectionTypeName: unknown): string | undefined {
  if (typeof connectionTypeName !== 'string' || NON_VENDOR_CONNECTION_TYPE_REGEX.test(connectionTypeName)) return undefined;
  const slug = connectionTypeName.replace(CONNECTION_TYPE_AUTH_SUFFIX_REGEX, '');
  return isValidCustomProviderSlug(slug) ? slug : undefined;
}

/** One model of a custom provider's catalog (stored in the AI setting's `data.models`). Only `id`
 * is required; everything else refines pricing, limits and the flags the two LLM stacks need
 * (pi's `reasoning`/`input`/`compat`, the AI SDK's structured-output support). */
export const AiCustomModelCatalogEntrySchema = z.object({
  /** the model id sent to the endpoint (`llama3.1:8b`, `meta-llama/llama-3.3-70b-instruct`, ...) */
  id: z.string().min(1).max(200),
  /** human-readable label for dropdowns; defaults to the id */
  label: z.string().max(200).optional(),
  /** context window in tokens (pi uses it for compaction); defaults to 128k */
  contextWindow: z.number().int().positive().optional(),
  /** maximum output tokens; defaults to 8192 */
  maxTokens: z.number().int().positive().optional(),
  /** whether the model supports extended thinking / reasoning (pi clamps `thinkingLevel` to this) */
  reasoning: z.boolean().optional(),
  /** whether the model accepts image input */
  supportsImages: z.boolean().optional(),
  /** whether the endpoint accepts `response_format: json_schema` for this model; defaults to true.
   * Set false for servers that only do prompt-based JSON — the AI actor then falls back to text +
   * repair. */
  structuredOutputs: z.boolean().optional(),
  /** whether the AI Agent actor may run on this model (tool calling over long sessions).
   * Undefined means usable — every catalog model is offered to the agent unless the entry says
   * `false`, which hides it from the agent's model picker and makes the orchestrator refuse it. */
  agent: z.boolean().optional(),
  /** pricing in USD per million tokens, for the `aiLog` cost estimate; defaults to zero */
  costPerMTokens: z.object({
    input: z.number().nonnegative(),
    output: z.number().nonnegative(),
  }).optional(),
  /** pi OpenAI-completions compatibility overrides, passed through verbatim to the Lambda's pi
   * provider registration. The listed keys are pi's `OpenAICompletionsCompat`; unknown keys pass
   * through so a newer pi option needs no schema change. */
  compat: z.object({
    supportsStore: z.boolean().optional(),
    supportsDeveloperRole: z.boolean().optional(),
    supportsReasoningEffort: z.boolean().optional(),
    supportsUsageInStreaming: z.boolean().optional(),
    supportsFinishReason: z.boolean().optional(),
    requiresToolResultName: z.boolean().optional(),
    requiresAssistantAfterToolResult: z.boolean().optional(),
    requiresThinkingAsText: z.boolean().optional(),
    maxTokensField: z.enum(['max_completion_tokens', 'max_tokens']).optional(),
  }).passthrough().optional(),
});

export type AiCustomModelCatalogEntry = z.infer<typeof AiCustomModelCatalogEntrySchema>;

/** The non-secret `data` of a custom provider's AI setting. */
export const CustomProviderAiSettingDataSchema = z.object({
  /** the provider's base URL override — wins over the connection's own base URL and the connection
   * type's vendor default (see ./providerBaseUrl.ts). Lenient here so a stale value never hides the
   * catalog; the API validates it strictly on write and the resolver ignores an unusable one. */
  baseURL: z.string().max(2048).optional(),
  /** the custom provider's model catalog; ids are unique within it (an id is looked up by
   * `<slug>/<id>`, so a repeated id would make one entry unreachable) */
  models: z.array(AiCustomModelCatalogEntrySchema).max(500).optional()
    .superRefine((models, ctx) => {
      if (!models) return;
      const seen = new Set<string>();
      models.forEach((entry, index) => {
        if (seen.has(entry.id)) {
          ctx.addIssue({ code: 'custom', path: [index, 'id'], message: `Duplicate model id "${entry.id}" in the model catalog` });
        }
        seen.add(entry.id);
      });
    }),
});

export type CustomProviderAiSettingData = z.infer<typeof CustomProviderAiSettingDataSchema>;

/** A custom provider's slug together with its catalog — what the model pickers merge in. */
export interface AiCustomProviderCatalog {
  /** the custom provider's slug (its AI setting `name`) */
  slug: string;
  /** its model catalog */
  models: readonly AiCustomModelCatalogEntry[];
}

/** The parsed parts of a model reference, discriminated by `kind`:
 * - `known` — a model of the build-time catalog (`AiModelInformationMap`), bare or qualified with
 *   its own provider (`gpt-4o-mini`, `openai/gpt-4o-mini`);
 * - `builtin` — a built-in provider's model the catalog does not list (`openai/gpt-6`);
 * - `custom` — a model served by one of the workspace's custom providers, named by slug
 *   (`fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct`). */
export type AiModelRefParts = KnownAiModelRefParts | BuiltinAiModelRefParts | CustomAiModelRefParts;

/** A reference to a model of the build-time catalog. */
export interface KnownAiModelRefParts {
  kind: 'known';
  /** the reference as written */
  ref: AiModelRef;
  /** the built-in provider the model runs on */
  provider: BuiltinAiProvider;
  /** the id sent to the provider (the reference itself when bare) */
  modelId: string;
  /** the id is in the build-time catalog */
  known: true;
}

/** A reference to a built-in provider's model the build-time catalog does not list. */
export interface BuiltinAiModelRefParts {
  kind: 'builtin';
  /** the reference as written */
  ref: AiModelRef;
  /** the built-in provider the model runs on */
  provider: BuiltinAiProvider;
  /** the id sent to the provider */
  modelId: string;
  /** the id is not in the build-time catalog */
  known: false;
}

/** A reference to a custom provider's model; the provider it runs on is `AiProvider.Custom`. */
export interface CustomAiModelRefParts {
  kind: 'custom';
  /** the reference as written */
  ref: AiModelRef;
  /** the custom provider's slug (the AI setting's `name`) */
  slug: string;
  /** the id sent to the endpoint */
  modelId: string;
  /** a custom provider's model is never in the build-time catalog, even when its id is a known
   * model's (`openrouter/gpt-4o-mini` runs on the gateway, not on OpenAI) */
  known: false;
}

/** Parse a model reference; `undefined` when it is neither a known id nor a valid qualified reference. */
export function parseAiModelRef(ref: unknown): AiModelRefParts | undefined {
  if (typeof ref !== 'string' || ref.length === 0 || ref.length > AI_MODEL_REF_MAX_LENGTH) return undefined;
  // every parsed reference is by definition a valid one
  const validRef = ref as AiModelRef;

  const known = KNOWN_MODEL_INFORMATION[ref];
  // the build-time catalog only lists built-in providers' models (see the invariant test)
  if (known && isBuiltinAiProvider(known.provider)) {
    return { kind: 'known', ref: validRef, provider: known.provider, modelId: ref, known: true };
  }

  const separatorIndex = ref.indexOf(AI_MODEL_REF_SEPARATOR);
  if (separatorIndex <= 0 || separatorIndex === ref.length - 1) return undefined;
  const prefix = ref.slice(0, separatorIndex);
  const modelId = ref.slice(separatorIndex + 1);

  if (isBuiltinAiProvider(prefix)) {
    // `openai/gpt-4o-mini` names a known model through its provider; keep its metadata.
    return KNOWN_MODEL_INFORMATION[modelId]?.provider === prefix
      ? { kind: 'known', ref: validRef, provider: prefix, modelId, known: true }
      : { kind: 'builtin', ref: validRef, provider: prefix, modelId, known: false };
  }

  if (isValidCustomProviderSlug(prefix)) {
    return { kind: 'custom', ref: validRef, slug: prefix, modelId, known: false };
  }

  return undefined;
}

/** Zod schema for a model reference: a known model id, `<provider>/<model-id>` for a built-in
 * provider, or `<custom-provider-slug>/<model-id>`. Branded, so a plain string only becomes an
 * `AiModelRef` by parsing (`AiModelRefSchema.parse`, `qualifyAiModelRef`, `isValidAiModelRef`). */
export const AiModelRefSchema = z.string()
  .superRefine((ref, ctx) => {
    if (parseAiModelRef(ref) === undefined) {
      ctx.addIssue({
        code: 'custom',
        message: 'Unknown model. Use a known model id, "<provider>/<model-id>" for a built-in provider, or "<custom-provider-slug>/<model-id>" for a custom provider (e.g. "fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct").',
      });
    }
  })
  .brand<'AiModelRef'>();

/** A validated model reference string — a known model id, `<provider>/<model-id>` or `<slug>/<model-id>`. */
export type AiModelRef = z.infer<typeof AiModelRefSchema>;

/** Whether a string is a valid model reference. */
export function isValidAiModelRef(ref: unknown): ref is AiModelRef {
  return parseAiModelRef(ref) !== undefined;
}

/** Build a qualified reference for a built-in provider's or a custom provider's (slug) model;
 * `undefined` when the pair does not form a valid reference (a reserved or malformed slug, an
 * empty id, over the length cap). */
export function qualifyAiModelRef(providerOrSlug: string, modelId: string): AiModelRef | undefined {
  const parsed = AiModelRefSchema.safeParse(`${providerOrSlug}${AI_MODEL_REF_SEPARATOR}${modelId}`);
  return parsed.success ? parsed.data : undefined;
}

/** The provider a parsed reference runs on: its built-in provider, or `custom` for a custom provider's model. */
export function getAiModelRefProvider(parts: AiModelRefParts): AiProvider {
  return parts.kind === 'custom' ? AiProvider.Custom : parts.provider;
}

/** The provider a model reference runs on, or `undefined` for an invalid reference. */
export function getAiModelProvider(ref: unknown): AiProvider | undefined {
  const parts = parseAiModelRef(ref);
  return parts ? getAiModelRefProvider(parts) : undefined;
}

/** The provider label used for a custom model's `providerLabel`. */
export function getAiProviderLabel(provider: AiProvider): string {
  return AiProviderLabels[provider] ?? provider;
}

/**
 * The `AiModelInformation` for a model reference: the static catalog entry for a known model;
 * for a qualified reference to a model the build does not list, a record synthesized from the
 * catalog entry (when given) over defaults — or over the known model's record when the model id
 * is itself a known model served through another provider (`openrouter/gpt-4o-mini` keeps
 * GPT-4o mini's label, pricing and limits unless the catalog entry overrides them).
 * `undefined` for an invalid reference.
 */
export function getAiModelInformation(ref: unknown, catalogEntry?: AiCustomModelCatalogEntry): AiModelInformation | undefined {
  const parts = parseAiModelRef(ref);
  if (!parts) return undefined;
  if (parts.kind === 'known') return KNOWN_MODEL_INFORMATION[parts.modelId];
  const base = KNOWN_MODEL_INFORMATION[parts.modelId];
  const cost = catalogEntry?.costPerMTokens;
  const provider = getAiModelRefProvider(parts);
  const providerLabel = parts.kind === 'custom'
    ? `${getAiProviderLabel(provider)} — ${parts.slug}`
    : getAiProviderLabel(provider);
  return {
    provider,
    label: catalogEntry?.label ?? base?.label ?? parts.modelId,
    providerLabel,
    date: base?.date ?? '',
    costPer1kTokens: cost
      ? {
        input: convertCostPerMTokensToCostPer1kTokens(cost.input),
        output: convertCostPerMTokensToCostPer1kTokens(cost.output),
      }
      : base?.costPer1kTokens ?? { input: 0, output: 0 },
    maxTokens: catalogEntry?.maxTokens ?? base?.maxTokens ?? DEFAULT_CUSTOM_MODEL_MAX_TOKENS,
  };
}

/** Find a reference's catalog entry in a single catalog (by unqualified model id). */
export function findAiModelCatalogEntry(
  ref: unknown,
  catalog: readonly AiCustomModelCatalogEntry[] | undefined,
): AiCustomModelCatalogEntry | undefined {
  const parts = parseAiModelRef(ref);
  if (!parts || !catalog) return undefined;
  return catalog.find((entry) => entry.id === parts.modelId);
}

/** Find a custom reference's catalog entry among the workspace's custom providers (by slug, then id). */
export function findAiModelCatalogEntryForProviders(
  ref: unknown,
  customProviders: readonly AiCustomProviderCatalog[] | undefined,
): AiCustomModelCatalogEntry | undefined {
  const parts = parseAiModelRef(ref);
  if (parts?.kind !== 'custom' || !customProviders) return undefined;
  const provider = customProviders.find((candidate) => candidate.slug === parts.slug);
  return provider ? findAiModelCatalogEntry(ref, provider.models) : undefined;
}

/** The UI options of a `suggestion` model field: the given references as grouped, labelled suggestions. */
export interface AiModelSuggestionUiOptions {
  suggestions: string[];
  suggestionLabels: Record<string, string>;
  suggestionGroups: Record<string, string[]>;
}

/** Build the `suggestion` field options for a list of model references, grouped by provider label
 * (custom providers group as "Custom Provider — <slug>"; a known model served through a custom
 * provider is labelled "<label> (via <slug>)"). Used by the AI actors' options JSON schema
 * (curated known models) and by the web, which merges the workspace's custom providers'
 * `<slug>/<id>` references into the same structure. */
export function buildAiModelSuggestionUiOptions(
  refs: readonly string[],
  customProviders?: readonly AiCustomProviderCatalog[],
): AiModelSuggestionUiOptions {
  const options: AiModelSuggestionUiOptions = { suggestions: [], suggestionLabels: {}, suggestionGroups: {} };
  for (const ref of refs) {
    const parts = parseAiModelRef(ref);
    const information = getAiModelInformation(ref, findAiModelCatalogEntryForProviders(ref, customProviders));
    if (!parts || !information || options.suggestions.includes(ref)) continue;
    const gatewaySlug = parts.kind === 'custom' && KNOWN_MODEL_INFORMATION[parts.modelId] ? parts.slug : undefined;
    options.suggestions.push(ref);
    options.suggestionLabels[ref] = gatewaySlug ? `${information.label} (via ${gatewaySlug})` : information.label;
    (options.suggestionGroups[information.providerLabel] ??= []).push(ref);
  }
  return options;
}
```
