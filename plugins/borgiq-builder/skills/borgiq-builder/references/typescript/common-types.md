# Common Types and Utilities

Shared TypeScript types and utilities: common types, AI model definitions (Anthropic, OpenAI, Google, xAI, custom providers and model references), canvas types, connection auth types, runtime types, sandbox types, file types, flowrun types, lambda types, signal types, asset types, and prefix definitions.

## Table of Contents

- [ai/anthropic.ts](#aianthropic)
- [ai/google.ts](#aigoogle)
- [ai/index.ts](#aiindex)
- [ai/lib.ts](#ailib)
- [ai/modelRef.ts](#aimodelref)
- [ai/openAi.ts](#aiopenai)
- [ai/providerBaseUrl.ts](#aiproviderbaseurl)
- [ai/xAi.ts](#aixai)
- [asset.ts](#asset)
- [canvas.ts](#canvas)
- [common.ts](#common)
- [connection.ts](#connection)
- [file.ts](#file)
- [flowrun.ts](#flowrun)
- [lambda.ts](#lambda)
- [prefix.ts](#prefix)
- [runtime.ts](#runtime)
- [sandbox.ts](#sandbox)
- [signal.ts](#signal)

## ai/anthropic

**Source:** `ai/anthropic.ts`

```typescript
import { AiModelInformation, AiProvider, convertCostPerMTokensToCostPer1kTokens } from './lib.js';

export const PROVIDER_LABEL = 'Anthropic';

export enum AnthropicModels {
  CLAUDE_3_7_SONNET = 'claude-3-7-sonnet-latest',
  CLAUDE_3_7_SONNET_2025_02_19 = 'claude-3-7-sonnet-20250219',
  
  CLAUDE_3_5_SONNET = 'claude-3-5-sonnet-latest',
  CLAUDE_3_5_SONNET_2024_10_22 = 'claude-3-5-sonnet-20241022',
  CLAUDE_3_5_SONNET_2024_06_20 = 'claude-3-5-sonnet-20240620',

  CLAUDE_3_5_HAIKU = 'claude-3-5-haiku-latest',
  CLAUDE_3_5_HAIKU_2024_10_22 = 'claude-3-5-haiku-20241022',
  
  CLAUDE_3_OPUS = 'claude-3-opus-latest',
  CLAUDE_3_OPUS_2024_02_29 = 'claude-3-opus-20240229',
  CLAUDE_3_SONNET = 'claude-3-sonnet-latest',
  CLAUDE_3_SONNET_2024_02_29 = 'claude-3-sonnet-20240229',
  CLAUDE_3_HAIKU = 'claude-3-haiku-latest',
  CLAUDE_3_HAIKU_2024_03_07 = 'claude-3-haiku-20240307',

  CLAUDE_4_OPUS = 'claude-opus-4-0',
  CLAUDE_4_OPUS_2025_05_14 = 'claude-opus-4-20250514',
  CLAUDE_4_1_OPUS = 'claude-opus-4-1',
  CLAUDE_4_1_OPUS_2025_08_05 = 'claude-opus-4-1-20250805',
  CLAUDE_4_SONNET = 'claude-sonnet-4-0',
  CLAUDE_4_SONNET_2025_05_14 = 'claude-sonnet-4-20250514',
  CLAUDE_4_5_SONNET = 'claude-sonnet-4-5',
  CLAUDE_4_5_SONNET_2025_09_29 = 'claude-sonnet-4-5-20250929',
  CLAUDE_4_5_OPUS = 'claude-opus-4-5',
  CLAUDE_4_5_OPUS_2025_11_01 = 'claude-opus-4-5-20251101',
  CLAUDE_4_5_HAIKU = 'claude-haiku-4-5',
  CLAUDE_4_5_HAIKU_2025_10_01 = 'claude-haiku-4-5-20251001',

  CLAUDE_4_6_OPUS = 'claude-opus-4-6',
  CLAUDE_4_6_OPUS_2026_02_05 = 'claude-opus-4-6-20260205',
  CLAUDE_4_6_SONNET = 'claude-sonnet-4-6',
  CLAUDE_4_6_SONNET_2026_02_17 = 'claude-sonnet-4-6-20260217',

  CLAUDE_4_7_OPUS = 'claude-opus-4-7',

  CLAUDE_4_8_OPUS = 'claude-opus-4-8',

  CLAUDE_5_SONNET = 'claude-sonnet-5',
  CLAUDE_5_OPUS = 'claude-opus-5',

  /** Mythos-class tier. Claude Mythos 5 / 5.1 are the same underlying models with
   * safeguards lifted, but are restricted to Anthropic's trusted-access program and
   * are deliberately not listed here. */
  CLAUDE_5_FABLE = 'claude-fable-5',
  CLAUDE_5_1_FABLE = 'claude-fable-5-1',
}

/** Anthropic models proficient enough to drive agentic workflows (flagship + fast variants).
 * The first entry seeds the cross-provider agent default, so keep a balanced Sonnet first. */
export const AnthropicAgentModels = [
  AnthropicModels.CLAUDE_5_SONNET,
  AnthropicModels.CLAUDE_5_1_FABLE,
  AnthropicModels.CLAUDE_5_OPUS,
  AnthropicModels.CLAUDE_5_FABLE,
  AnthropicModels.CLAUDE_4_8_OPUS,
  AnthropicModels.CLAUDE_4_7_OPUS,
  AnthropicModels.CLAUDE_4_6_SONNET,
  AnthropicModels.CLAUDE_4_6_OPUS,
  AnthropicModels.CLAUDE_4_5_SONNET,
  AnthropicModels.CLAUDE_4_5_HAIKU,
  AnthropicModels.CLAUDE_4_5_OPUS,
] as const;

export const AnthropicModelInformationMap: Record<AnthropicModels, AiModelInformation> = {
  [AnthropicModels.CLAUDE_3_7_SONNET]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3.7 Sonnet',
    providerLabel: PROVIDER_LABEL,
    date: '2025-02-19',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_3_7_SONNET_2025_02_19]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3.7 Sonnet 2025-02-19',
    providerLabel: PROVIDER_LABEL,
    date: '2025-02-19',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 64000,
  },

  [AnthropicModels.CLAUDE_3_5_SONNET]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3.5 Sonnet',
    providerLabel: PROVIDER_LABEL,
    date: '2024-10-22',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 8192,
  },
  [AnthropicModels.CLAUDE_3_5_SONNET_2024_10_22]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3.5 Sonnet 2024-10-22',
    providerLabel: PROVIDER_LABEL,
    date: '2024-10-22',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 8192,
  },
  [AnthropicModels.CLAUDE_3_5_SONNET_2024_06_20]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3.5 Sonnet 2024-06-20',
    providerLabel: 'Anthropic',
    date: '2024-06-20',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 8192,
  },

  [AnthropicModels.CLAUDE_3_5_HAIKU]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3.5 Haiku',
    providerLabel: 'Anthropic',
    date: '2024-10-22',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.8),
      output: convertCostPerMTokensToCostPer1kTokens(4),
    },
    maxTokens: 8192,
  },
  [AnthropicModels.CLAUDE_3_5_HAIKU_2024_10_22]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3.5 Haiku 2024-10-22',
    providerLabel: 'Anthropic',
    date: '2024-10-22',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.8),
      output: convertCostPerMTokensToCostPer1kTokens(4),
    },
    maxTokens: 8192,
  },


  [AnthropicModels.CLAUDE_3_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3 Opus',
    providerLabel: 'Anthropic',
    date: '2024-02-29',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(75),
    },
    maxTokens: 4096,
  },
  [AnthropicModels.CLAUDE_3_OPUS_2024_02_29]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3 Opus 2024-02-29',
    providerLabel: 'Anthropic',
    date: '2024-02-29',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(75),
    },
    maxTokens: 4096,
  },
  [AnthropicModels.CLAUDE_3_SONNET]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3 Sonnet',
    providerLabel: 'Anthropic',
    date: '2024-02-29',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 4096,
  },
  [AnthropicModels.CLAUDE_3_SONNET_2024_02_29]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3 Sonnet 2024-02-29',
    providerLabel: 'Anthropic',
    date: '2024-02-29',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 4096,
  },
  [AnthropicModels.CLAUDE_3_HAIKU]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3 Haiku',
    providerLabel: 'Anthropic',
    date: '2024-03-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.25),
      output: convertCostPerMTokensToCostPer1kTokens(1.25),
    },
    maxTokens: 4096,
  },
  [AnthropicModels.CLAUDE_3_HAIKU_2024_03_07]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3 Haiku 2024-03-07',
    providerLabel: 'Anthropic',
    date: '2024-03-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.25),
      output: convertCostPerMTokensToCostPer1kTokens(1.25),
    },
    maxTokens: 4096,
  },

  [AnthropicModels.CLAUDE_4_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4 Opus',
    providerLabel: 'Anthropic',
    date: '2025-05-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(75),
    },
    maxTokens: 32000,
  },
  [AnthropicModels.CLAUDE_4_OPUS_2025_05_14]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4 Opus 2025-05-14',
    providerLabel: 'Anthropic',
    date: '2025-05-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(75),
    },
    maxTokens: 32000,
  },
  [AnthropicModels.CLAUDE_4_SONNET]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4 Sonnet',
    providerLabel: 'Anthropic',
    date: '2025-05-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_4_SONNET_2025_05_14]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4 Sonnet 2025-05-14',
    providerLabel: 'Anthropic',
    date: '2025-05-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_4_1_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.1 Opus',
    providerLabel: 'Anthropic',
    date: '2025-08-05',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(75),
    },
    maxTokens: 32000,
  },
  [AnthropicModels.CLAUDE_4_1_OPUS_2025_08_05]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.1 Opus 2025-08-05',
    providerLabel: 'Anthropic',
    date: '2025-08-05',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(75),
    },
    maxTokens: 32000,
  },
  [AnthropicModels.CLAUDE_4_5_SONNET]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.5 Sonnet',
    providerLabel: 'Anthropic',
    date: '2025-09-29',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_4_5_SONNET_2025_09_29]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.5 Sonnet 2025-09-29',
    providerLabel: 'Anthropic',
    date: '2025-09-29',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_4_5_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.5 Opus',
    providerLabel: 'Anthropic',
    date: '2025-11-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(25),
    },
    maxTokens: 32000,
  },
  [AnthropicModels.CLAUDE_4_5_OPUS_2025_11_01]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.5 Opus 2025-11-01',
    providerLabel: 'Anthropic',
    date: '2025-11-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(25),
    },
    maxTokens: 32000,
  },
  [AnthropicModels.CLAUDE_4_5_HAIKU]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.5 Haiku',
    providerLabel: 'Anthropic',
    date: '2025-10-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1),
      output: convertCostPerMTokensToCostPer1kTokens(5),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_4_5_HAIKU_2025_10_01]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.5 Haiku 2025-10-01',
    providerLabel: 'Anthropic',
    date: '2025-10-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1),
      output: convertCostPerMTokensToCostPer1kTokens(5),
    },
    maxTokens: 64000,
  },

  [AnthropicModels.CLAUDE_4_6_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.6 Opus',
    providerLabel: PROVIDER_LABEL,
    date: '2026-02-05',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(25),
    },
    maxTokens: 128000,
  },
  [AnthropicModels.CLAUDE_4_6_OPUS_2026_02_05]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.6 Opus 2026-02-05',
    providerLabel: PROVIDER_LABEL,
    date: '2026-02-05',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(25),
    },
    maxTokens: 128000,
  },
  [AnthropicModels.CLAUDE_4_6_SONNET]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.6 Sonnet',
    providerLabel: PROVIDER_LABEL,
    date: '2026-02-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_4_6_SONNET_2026_02_17]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.6 Sonnet 2026-02-17',
    providerLabel: PROVIDER_LABEL,
    date: '2026-02-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 64000,
  },

  [AnthropicModels.CLAUDE_4_7_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.7 Opus',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-13',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(25),
    },
    maxTokens: 128000,
  },
  [AnthropicModels.CLAUDE_4_8_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.8 Opus',
    providerLabel: PROVIDER_LABEL,
    date: '2026-05-28',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(25),
    },
    maxTokens: 128000,
  },

  [AnthropicModels.CLAUDE_5_SONNET]: {
    provider: AiProvider.Anthropic,
    label: 'Claude Sonnet 5',
    providerLabel: PROVIDER_LABEL,
    date: '2026-06-30',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 128000,
  },
  [AnthropicModels.CLAUDE_5_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude Opus 5',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-24',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(25),
    },
    maxTokens: 128000,
  },

  [AnthropicModels.CLAUDE_5_FABLE]: {
    provider: AiProvider.Anthropic,
    label: 'Claude Fable 5',
    providerLabel: PROVIDER_LABEL,
    date: '2026-06-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(10),
      output: convertCostPerMTokensToCostPer1kTokens(50),
    },
    maxTokens: 128000,
  },
  [AnthropicModels.CLAUDE_5_1_FABLE]: {
    provider: AiProvider.Anthropic,
    label: 'Claude Fable 5.1',
    providerLabel: PROVIDER_LABEL,
    date: '2026-09-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(10),
      output: convertCostPerMTokensToCostPer1kTokens(50),
    },
    maxTokens: 128000,
  },
} as const;
```

## ai/google

**Source:** `ai/google.ts`

```typescript
import { AiModelInformation, AiProvider, convertCostPerMTokensToCostPer1kTokens } from './lib.js';

const PROVIDER_LABEL = 'Google';

export enum GoogleAiModels {
  GEMMA_3_1B = 'gemma-3-1b-it',
  GEMMA_3_4B = 'gemma-3-4b-it',
  GEMMA_3_12B = 'gemma-3-12b-it',
  GEMMA_3_27B = 'gemma-3-27b-it',

  GEMINI_2_0_FLASH = 'gemini-2.0-flash',
  GEMINI_2_0_FLASH_001 = 'gemini-2.0-flash-001',
  
  GEMINI_2_0_FLASH_LITE = 'gemini-2.0-flash-lite',
  GEMINI_2_0_FLASH_LITE_001 = 'gemini-2.0-flash-lite-001',
  
  
  GEMINI_2_0_FLASH_THINKING_EXP = 'gemini-2.0-flash-thinking-exp',
  GEMINI_2_0_FLASH_THINKING_EXP_1_21 = 'gemini-2.0-flash-thinking-exp-01-21',
  
  GEMINI_2_5_PRO = 'gemini-2.5-pro',
  GEMINI_2_5_PRO_PREVIEW_03_25 = 'gemini-2.5-pro-preview-03-25',
  GEMINI_2_5_PRO_PREVIEW_06_05 = 'gemini-2.5-pro-preview-06-05',

  GEMINI_2_5_FLASH = 'gemini-2.5-flash',
  GEMINI_2_5_FLASH_PREVIEW_04_17 = 'gemini-2.5-flash-preview-04-17',
  GEMINI_2_5_FLASH_PREVIEW_05_20 = 'gemini-2.5-flash-preview-05-20',

  GEMINI_2_5_FLASH_LITE_PREVIEW_06_17 = 'gemini-2.5-flash-lite-preview-06-17',

  GEMINI_3_PRO_PREVIEW = 'gemini-3-pro-preview',

  GEMINI_3_FLASH_PREVIEW = 'gemini-3-flash-preview',

  GEMINI_3_1_PRO_PREVIEW = 'gemini-3.1-pro-preview',

  GEMINI_3_5_FLASH = 'gemini-3.5-flash',

  GEMINI_3_1_FLASH_LITE = 'gemini-3.1-flash-lite',
  GEMINI_3_5_FLASH_LITE = 'gemini-3.5-flash-lite',

  GEMINI_3_6_FLASH = 'gemini-3.6-flash',
  GEMINI_3_7_FLASH = 'gemini-3.7-flash',
  GEMINI_3_8_FLASH = 'gemini-3.8-flash',
}

/** Google models proficient enough to drive agentic workflows (Gemini flagship + flash/lite). */
export const GoogleAgentModels = [
  GoogleAiModels.GEMINI_3_1_PRO_PREVIEW,
  GoogleAiModels.GEMINI_3_8_FLASH,
  GoogleAiModels.GEMINI_3_7_FLASH,
  GoogleAiModels.GEMINI_3_6_FLASH,
  GoogleAiModels.GEMINI_3_5_FLASH,
  GoogleAiModels.GEMINI_3_5_FLASH_LITE,
  GoogleAiModels.GEMINI_3_1_FLASH_LITE,
  GoogleAiModels.GEMINI_2_5_PRO,
] as const;

export const GoogleModelInformationMap: Record<GoogleAiModels, AiModelInformation> = {
  [GoogleAiModels.GEMMA_3_1B]: {
    provider: AiProvider.Google,
    label: 'Gemma 3 1B',
    providerLabel: PROVIDER_LABEL,
    date: '2024-08-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0),
      output: convertCostPerMTokensToCostPer1kTokens(0),
    },
    maxTokens: 8192,
  },
  [GoogleAiModels.GEMMA_3_4B]: {
    provider: AiProvider.Google,
    label: 'Gemma 3 4B',
    providerLabel: PROVIDER_LABEL,
    date: '2024-08-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0),
      output: convertCostPerMTokensToCostPer1kTokens(0),
    },
    maxTokens: 8192,
  },
  [GoogleAiModels.GEMMA_3_12B]: {
    provider: AiProvider.Google,
    label: 'Gemma 3 12B',
    providerLabel: PROVIDER_LABEL,
    date: '2024-08-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0),
      output: convertCostPerMTokensToCostPer1kTokens(0),
    },
    maxTokens: 8192,
  },
  [GoogleAiModels.GEMMA_3_27B]: {
    provider: AiProvider.Google,
    label: 'Gemma 3 27B',
    providerLabel: PROVIDER_LABEL,
    date: '2024-08-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0),
      output: convertCostPerMTokensToCostPer1kTokens(0),
    },
    maxTokens: 8192,
  },

  [GoogleAiModels.GEMINI_2_0_FLASH]: {
    provider: AiProvider.Google,
    label: 'Gemini 2.0 Flash',
    providerLabel: PROVIDER_LABEL,
    date: '2024-06-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.1),
      output: convertCostPerMTokensToCostPer1kTokens(0.4),
    },
    maxTokens: 8192,
  },
  [GoogleAiModels.GEMINI_2_0_FLASH_001]: {
    provider: AiProvider.Google,
    label: 'Gemini 2.0 Flash 001',
    providerLabel: PROVIDER_LABEL,
    date: '2024-06-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.1),
      output: convertCostPerMTokensToCostPer1kTokens(0.4),
    },
    maxTokens: 8192,
  },

  [GoogleAiModels.GEMINI_2_0_FLASH_LITE]: {
    provider: AiProvider.Google,
    label: 'Gemini 2.0 Flash Lite',
    providerLabel: PROVIDER_LABEL,
    date: '2024-06-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.075),
      output: convertCostPerMTokensToCostPer1kTokens(0.3),
    },
    maxTokens: 8192,
  },
  [GoogleAiModels.GEMINI_2_0_FLASH_LITE_001]: {
    provider: AiProvider.Google,
    label: 'Gemini 2.0 Flash Lite 001',
    providerLabel: PROVIDER_LABEL,
    date: '2024-06-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.075),
      output: convertCostPerMTokensToCostPer1kTokens(0.3),
    },
    maxTokens: 8192,
  },

  [GoogleAiModels.GEMINI_2_0_FLASH_THINKING_EXP]: {
    provider: AiProvider.Google,
    label: 'Gemini 2.0 Flash Thinking Exp',
    providerLabel: PROVIDER_LABEL,
    date: '2025-01-21',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0),
      output: convertCostPerMTokensToCostPer1kTokens(0),
    },
    maxTokens: 8192,
  },
  [GoogleAiModels.GEMINI_2_0_FLASH_THINKING_EXP_1_21]: {
    provider: AiProvider.Google,
    label: 'Gemini 2.0 Flash Thinking Experimental 2025-01-21',
    providerLabel: PROVIDER_LABEL,
    date: '2025-01-21',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0),
      output: convertCostPerMTokensToCostPer1kTokens(0),
    },
    maxTokens: 8192,
  },

  [GoogleAiModels.GEMINI_2_5_PRO]: {
    provider: AiProvider.Google,
    label: 'Gemini 2.5 Pro',
    providerLabel: PROVIDER_LABEL,
    date: '2025-06-17',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(10),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(15),
      },
    },
    maxTokens: 65536,
  },

  [GoogleAiModels.GEMINI_2_5_PRO_PREVIEW_03_25]: {
    provider: AiProvider.Google,
    label: 'Gemini 2.5 Pro Preview 2025-03-25',
    providerLabel: PROVIDER_LABEL,
    date: '2025-03-25',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(10),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(15),
      },
    },
    maxTokens: 65536,
  },

  [GoogleAiModels.GEMINI_2_5_PRO_PREVIEW_06_05]: {
    provider: AiProvider.Google,
    label: 'Gemini 2.5 Pro Preview 2025-06-05',
    providerLabel: PROVIDER_LABEL,
    date: '2025-06-05',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(10),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(15),
      },
    },
    maxTokens: 65536,
  },


  [GoogleAiModels.GEMINI_2_5_FLASH]: {
    provider: AiProvider.Google,
    label: 'Gemini 2.5 Flash',
    providerLabel: PROVIDER_LABEL,
    date: '2025-06-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.3),
      output: convertCostPerMTokensToCostPer1kTokens(2.5),
    },
    maxTokens: 8192,
  },

  [GoogleAiModels.GEMINI_2_5_FLASH_PREVIEW_04_17]: {
    provider: AiProvider.Google,
    label: 'Gemini 2.5 Flash Preview 2025-04-17',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.15),
      output: convertCostPerMTokensToCostPer1kTokens(0.6),
    },
    maxTokens: 8192,
  },

  [GoogleAiModels.GEMINI_2_5_FLASH_PREVIEW_05_20]: {
    provider: AiProvider.Google,
    label: 'Gemini 2.5 Flash Preview 2025-05-20',
    providerLabel: PROVIDER_LABEL,
    date: '2025-05-20',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.15),
      output: convertCostPerMTokensToCostPer1kTokens(0.6),
    },
    maxTokens: 8192,
  },

  [GoogleAiModels.GEMINI_2_5_FLASH_LITE_PREVIEW_06_17]: {
    provider: AiProvider.Google,
    label: 'Gemini 2.5 Flash Lite Preview 2025-06-17',
    providerLabel: PROVIDER_LABEL,
    date: '2025-06-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.1),
      output: convertCostPerMTokensToCostPer1kTokens(0.4),
    },
    maxTokens: 64000,
  },

  [GoogleAiModels.GEMINI_3_PRO_PREVIEW]: {
    provider: AiProvider.Google,
    label: 'Gemini 3 Pro Preview',
    providerLabel: PROVIDER_LABEL,
    date: '2025-11-01',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(2.0),
        output: convertCostPerMTokensToCostPer1kTokens(12.0),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(4.0),
        output: convertCostPerMTokensToCostPer1kTokens(18.0),
      },
    },
    maxTokens: 65536,
  },

  [GoogleAiModels.GEMINI_3_FLASH_PREVIEW]: {
    provider: AiProvider.Google,
    label: 'Gemini 3 Flash Preview',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-01',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(0.5),
        output: convertCostPerMTokensToCostPer1kTokens(3.0),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(0.5),
        output: convertCostPerMTokensToCostPer1kTokens(3.0),
      },
    },
    maxTokens: 65536,
  },

  [GoogleAiModels.GEMINI_3_1_PRO_PREVIEW]: {
    provider: AiProvider.Google,
    label: 'Gemini 3.1 Pro Preview',
    providerLabel: PROVIDER_LABEL,
    date: '2026-02-19',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(2.0),
        output: convertCostPerMTokensToCostPer1kTokens(12.0),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(4.0),
        output: convertCostPerMTokensToCostPer1kTokens(18.0),
      },
    },
    maxTokens: 65536,
  },

  [GoogleAiModels.GEMINI_3_5_FLASH]: {
    provider: AiProvider.Google,
    label: 'Gemini 3.5 Flash',
    providerLabel: PROVIDER_LABEL,
    date: '2026-05-19',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.5),
      output: convertCostPerMTokensToCostPer1kTokens(9.0),
    },
    maxTokens: 65536,
  },

  [GoogleAiModels.GEMINI_3_1_FLASH_LITE]: {
    provider: AiProvider.Google,
    label: 'Gemini 3.1 Flash Lite',
    providerLabel: PROVIDER_LABEL,
    date: '2026-02-19',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.25),
      output: convertCostPerMTokensToCostPer1kTokens(1.5),
    },
    maxTokens: 65536,
  },
  [GoogleAiModels.GEMINI_3_5_FLASH_LITE]: {
    provider: AiProvider.Google,
    label: 'Gemini 3.5 Flash Lite',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-21',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.3),
      output: convertCostPerMTokensToCostPer1kTokens(2.5),
    },
    maxTokens: 65536,
  },

  /** The 3.6/3.7/3.8 Flash rate below is promotional: Google lists $0.75/$3.75 through
   * 2026-12-31 and $1.50/$7.50 from 2027-01-01. Revisit these three entries in January. */
  [GoogleAiModels.GEMINI_3_6_FLASH]: {
    provider: AiProvider.Google,
    label: 'Gemini 3.6 Flash',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-21',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.75),
      output: convertCostPerMTokensToCostPer1kTokens(3.75),
    },
    maxTokens: 65536,
  },
  [GoogleAiModels.GEMINI_3_7_FLASH]: {
    provider: AiProvider.Google,
    label: 'Gemini 3.7 Flash',
    providerLabel: PROVIDER_LABEL,
    date: '2026-08-13',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.75),
      output: convertCostPerMTokensToCostPer1kTokens(3.75),
    },
    maxTokens: 65536,
  },
  [GoogleAiModels.GEMINI_3_8_FLASH]: {
    provider: AiProvider.Google,
    label: 'Gemini 3.8 Flash',
    providerLabel: PROVIDER_LABEL,
    date: '2026-09-02',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.75),
      output: convertCostPerMTokensToCostPer1kTokens(3.75),
    },
    maxTokens: 65536,
  },
};
```

## ai/index

**Source:** `ai/index.ts`

```typescript
import { z } from 'zod';

import { AiModelInformation, AiProvider } from './lib.js';
import { OpenAiModelInformationMap, OpenAiModels, OpenAiAgentModels } from './openAi.js';
import { AnthropicModelInformationMap, AnthropicModels, AnthropicAgentModels } from './anthropic.js';
import { GoogleModelInformationMap, GoogleAiModels, GoogleAgentModels } from './google.js';
import { xAiModelInformationMap, xAiModels, xAiAgentModels } from './xAi.js';
import { BIQFileSchema } from '../schemas/file.js';
import type { AiModelRef } from './modelRef.js';

export { AiProvider, AI_MODEL_PROVIDERS, AiProviderLabels } from './lib.js';
export type { AiModelProvider, AiModelInformation } from './lib.js';
export * from './modelRef.js';
export * from './providerBaseUrl.js';
export { AnthropicAgentModels } from './anthropic.js';
export { OpenAiAgentModels } from './openAi.js';
export { GoogleAgentModels } from './google.js';
export { xAiAgentModels } from './xAi.js';

export enum AiModelType {
  Chat = 'chat',
  Reasoning = 'reasoning',
}

/** Thinking / reasoning depth requested from the model by the AI Agent (Lambda) actor. pi maps
 * each level to the provider's native parameter (Anthropic thinking budget, OpenAI reasoning
 * effort, Gemini thinking budget, ...) and clamps it to what the selected model supports. `off`
 * disables thinking; leaving the option unset keeps pi's own default (`medium`). */
export const AI_AGENT_THINKING_LEVELS = ['off', 'minimal', 'low', 'medium', 'high'] as const;
export const AiAgentThinkingLevelSchema = z.enum(AI_AGENT_THINKING_LEVELS);
export type AiAgentThinkingLevel = z.infer<typeof AiAgentThinkingLevelSchema>;

export enum AiFinishReason {
  Finish = 'finished',
  MaxLoopCountReached = 'max_loop_count_reached',
  MaxLength = 'max_length',
  ToolCalls = 'tool_calls',
  ContentFilter = 'content_filter',
  Error = 'error',
  Unknown = 'unknown',
}

export const AiModel = {
  ...OpenAiModels,
  ...AnthropicModels,
  ...GoogleAiModels,
  ...xAiModels,
} as const;
export type AiModel = (typeof AiModel)[keyof typeof AiModel];

/** What the AI services accept as a model: a validated reference (`AiModelRefSchema`), or a known
 * model id, which is a valid reference by construction. */
export type AiModelRefInput = AiModelRef | AiModel;

/** Curated agent lists per provider (single source of truth, defined alongside each
 * provider's models). The first entry seeds the cross-provider default — keep it an
 * Anthropic Sonnet. */
export const AiAgentModelsByProvider = {
  [AiProvider.Anthropic]: AnthropicAgentModels,
  [AiProvider.OpenAI]: OpenAiAgentModels,
  [AiProvider.Google]: GoogleAgentModels,
  [AiProvider.xAi]: xAiAgentModels,
} as const satisfies Partial<Record<AiProvider, readonly AiModel[]>>;

/** Every proficient agent model across all providers (drives the AI Agent actor dropdown). */
export const AiAgentModels = [
  ...AnthropicAgentModels,
  ...OpenAiAgentModels,
  ...GoogleAgentModels,
  ...xAiAgentModels,
] as const;

export const AiModelInformationMap: Record<AiModel, AiModelInformation> = {
  ...OpenAiModelInformationMap,
  ...AnthropicModelInformationMap,
  ...GoogleModelInformationMap,
  ...xAiModelInformationMap,
} as const;

export const AiMessageTextSchema = z.object({
  type: z.literal('text'),
  text: z.string(),
});

export type AiMessageText = z.infer<typeof AiMessageTextSchema>;

export const AiMessageImageSchema = z.object({
  type: z.literal('image'),
  /** the base64 encoded image OR url */
  image: z.string(),
  /** the media/MIME type */
  mediaType: z.string(),
});

export type AiMessageImage = z.infer<typeof AiMessageImageSchema>;

export const AiMessageFileSchema = z.object({
  type: z.literal('file'),
  /** the base64 encoded file OR url */
  data: z.string(),
  fileName: z.string().optional(),
  /** the media/MIME type */
  mediaType: z.string(),
});

export type AiMessageFile = z.infer<typeof AiMessageFileSchema>;

export const AiUserMessageContentSchema = z.discriminatedUnion('type', [
  AiMessageTextSchema,
  AiMessageImageSchema,
  AiMessageFileSchema,
]);

export type AiUserMessageContent = z.infer<typeof AiUserMessageContentSchema>;

export const AiUserMessageSchema = z.object({
  role: z.literal('user'),
  content: z.union([
    z.string(),
    z.array(AiUserMessageContentSchema),
  ]),
});

export type AiUserMessage = z.infer<typeof AiUserMessageSchema>;

export const AiAssistantMessageReasoningSchema = z.object({
  type: z.literal('reasoning'),
  text: z.string(),
  signature: z.string(),
});

export type AiAssistantMessageReasoning = z.infer<typeof AiAssistantMessageReasoningSchema>;


export const AiAssistantMessageToolCallSchema = z.object({
  type: z.literal('tool-call'),
  toolCallId: z.string(),
  toolName: z.string(),
  input: z.any(),
  providerOptions: z.record(z.string(), z.any()).optional(),
});

export type AiAssistantMessageToolCall = z.infer<typeof AiAssistantMessageToolCallSchema>;

export const AiAssistantMessageContentSchema = z.discriminatedUnion('type', [
  AiMessageTextSchema,
  AiMessageFileSchema,
  AiAssistantMessageReasoningSchema,
  AiAssistantMessageToolCallSchema,
]);

export type AiAssistantMessageContent = z.infer<typeof AiAssistantMessageContentSchema>;

export const AiAssistantMessageSchema = z.object({
  role: z.literal('assistant'),
  content: z.union([
    z.string(),
    z.array(AiAssistantMessageContentSchema),
  ]),
});

export type AiAssistantMessage = z.infer<typeof AiAssistantMessageSchema>;

export const AiToolMessageTextResultSchema = z.object({
  type: z.literal('text'),
  value: z.string(),
});

export type AiToolMessageTextResult = z.infer<typeof AiToolMessageTextResultSchema>;


export const AiToolMessageJsonResultSchema = z.object({
  type: z.literal('json'),
  value: z.any(),
});

export type AiToolMessageJsonResult = z.infer<typeof AiToolMessageJsonResultSchema>;


export const AiToolErrorTextResultSchema = z.object({
  type: z.literal('error-text'),
  value: z.string(),
});

export type AiToolErrorTextResult = z.infer<typeof AiToolErrorTextResultSchema>;


export const AiToolErrorJsonResultSchema = z.object({
  type: z.literal('error-json'),
  value: z.any(),
});

export type AiToolErrorJsonResult = z.infer<typeof AiToolErrorJsonResultSchema>;

export const AiToolContentMediaSchema = z.object({
  type: z.literal('media'),
  /** the base64 encoded media */
  data: z.string(),
  /** the media/MIME type */
  mediaType: z.string(),
});
export type AiToolContentMedia = z.infer<typeof AiToolContentMediaSchema>;

const AiToolMessageContentSchema = z.object({
  type: z.literal('content'),
  value: z.array(z.discriminatedUnion('type', [
    AiMessageTextSchema,
    AiToolContentMediaSchema,
  ])),
});

export type AiToolMessageContent = z.infer<typeof AiToolMessageContentSchema>;

export const AiToolMessageOutputSchema = z.discriminatedUnion('type', [
  AiToolMessageTextResultSchema,
  AiToolMessageJsonResultSchema,
  AiToolErrorTextResultSchema,
  AiToolErrorJsonResultSchema,
  AiToolMessageContentSchema,
]);

export type AiToolMessageOutput = z.infer<typeof AiToolMessageOutputSchema>;

export const AiToolMessageResultSchema = z.object({
  type: z.literal('tool-result'),
  toolCallId: z.string(),
  toolName: z.string(),
  output: AiToolMessageOutputSchema,
  providerOptions: z.record(z.string(), z.any()).optional(),
});

export type AiToolMessageResult = z.infer<typeof AiToolMessageResultSchema>;

export const AiToolMessageSchema = z.object({
  role: z.literal('tool'),
  content: z.array(AiToolMessageResultSchema),
});

export type AiToolMessage = z.infer<typeof AiToolMessageSchema>;


export const AiMessageSchema = z.discriminatedUnion('role', [
  AiUserMessageSchema,
  AiAssistantMessageSchema,
  AiToolMessageSchema,
]);

export type AiMessage = z.infer<typeof AiMessageSchema>;

export const AiToolCallSchema = AiAssistantMessageToolCallSchema.omit({
  type: true,
});

export type AiToolCall = z.infer<typeof AiToolCallSchema>;

export interface AiStepOutput {
  response: string;
  toolCalls?: AiToolCall[];
  toolResults?: AiToolMessageResult[];
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
}

export interface AiOutput<T = unknown> {
  response: T;
  toolCalls?: AiToolCall[];
  steps?: AiStepOutput[];
  finishReason?: AiFinishReason;
}

export interface AiResponse<T = unknown> extends AiOutput<T> {
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
}

export interface AiChatCompletionResponse<T = unknown> extends AiResponse<T> {
  fromCache: boolean;
}

export const AiDefaultParameters = {
  model: AiModel.GPT_4O_MINI,
  temperature: 0.2,
  maxTokens: 10000,
} as const;

/** The custom types for AI enabled actors to build the message history */

export const BIQAiMessageImageSchema = z.object({
  type: z.literal('image'),
  image: BIQFileSchema,
});

export type BIQAiMessageImage = z.infer<typeof BIQAiMessageImageSchema>;

export const BIQAiMessageFileSchema = z.object({
  type: z.literal('file'),
  data: BIQFileSchema,
});

export type BIQAiMessageFile = z.infer<typeof AiMessageFileSchema>;

export const BIQAiUserMessageContentSchema = z.union([
  AiMessageTextSchema,
  AiMessageImageSchema,
  BIQAiMessageImageSchema,
  AiMessageFileSchema,
  BIQAiMessageFileSchema,
]);

export type BIQAiUserMessageContent = z.infer<typeof BIQAiUserMessageContentSchema>;

export const BIQAiUserMessageSchema = z.object({
  role: z.literal('user'),
  content: z.union([
    z.string(),
    z.array(BIQAiUserMessageContentSchema),
  ]),
});

export type BIQAiUserMessage = z.infer<typeof BIQAiUserMessageSchema>;


export const BIQAiAssistantMessageContentSchema = z.union([
  AiMessageTextSchema,
  AiMessageFileSchema,
  AiMessageImageSchema,
  AiAssistantMessageReasoningSchema,
  AiAssistantMessageToolCallSchema,
]);

export type BIQAiAssistantMessageContent = z.infer<typeof BIQAiAssistantMessageContentSchema>;

export const BIQAiAssistantMessageSchema = z.object({
  role: z.literal('assistant'),
  content: z.union([
    z.string(),
    z.array(BIQAiAssistantMessageContentSchema),
  ]),
});

export type BIQAiAssistantMessage = z.infer<typeof BIQAiAssistantMessageSchema>;

export const BIQAiToolContentMediaSchema = z.object({
  type: z.literal('media'),
  data: BIQFileSchema,
});

export type BIQAiToolContentMedia = z.infer<typeof BIQAiToolContentMediaSchema>;

export const BIQAiToolContentSchema = z.object({
  type: z.literal('content'),
  value: z.array(z.union([
    AiMessageTextSchema,
    AiToolContentMediaSchema,
    BIQAiToolContentMediaSchema,
  ])),
});

export type BIQAiToolContent = z.infer<typeof BIQAiToolContentSchema>;

export const BIQAiToolMessageOutputSchema = z.discriminatedUnion('type', [
  AiToolMessageTextResultSchema,
  AiToolMessageJsonResultSchema,
  AiToolErrorTextResultSchema,
  AiToolErrorJsonResultSchema,
  BIQAiToolContentSchema,
]);

export type BIQAiToolMessageOutput = z.infer<typeof BIQAiToolMessageOutputSchema>;


export const BIQAiToolMessageResultSchema = z.object({
  type: z.literal('tool-result'),
  toolCallId: z.string(),
  toolName: z.string(),
  output: BIQAiToolMessageOutputSchema,
});

export type BIQAiToolMessageResult = z.infer<typeof BIQAiToolMessageResultSchema>;

export const BIQAiToolMessageSchema = z.object({
  role: z.literal('tool'),
  content: z.array(BIQAiToolMessageResultSchema),
});

export type BIQAiToolMessage = z.infer<typeof BIQAiToolMessageSchema>;

export const BIQAiMessageSchema = z.discriminatedUnion('role', [
  BIQAiUserMessageSchema,
  BIQAiAssistantMessageSchema,
  BIQAiToolMessageSchema,
]);

export type BIQAiMessage = z.infer<typeof BIQAiMessageSchema>;
```

## ai/lib

**Source:** `ai/lib.ts`

```typescript
export const convertCostPerMTokensToCostPer1kTokens = (costPerMTokens: number) => {
  // Convert cost per million tokens to cost per 1k tokens cost per million tokens * millicents per dollar * 1000 tokens / 1,000,000 tokens
  return costPerMTokens * 100_000 * 1000 / 1_000_000;
};

export enum AiProvider {
  OpenAI = 'openai',
  Anthropic = 'anthropic',
  Google = 'google',
  xAi = 'xai',
  ClaudeCode = 'claude-code',
  Codex = 'codex',
  /** A custom provider: any AI provider, gateway/router or self-hosted server that is
   * OpenAI-compatible or uses the OpenAI chat completions schema (Fireworks, Groq, Together,
   * DeepInfra, OpenRouter, LiteLLM, Ollama, vLLM, LM Studio, llama.cpp, Azure OpenAI's /openai/v1,
   * ...). A workspace may add several, each an AI setting whose `name` is the provider's slug, with
   * a connection for the key (a vendor connection type flagged `aiProvider`, a generic bearer /
   * API-key type, or `custom-provider-apikey`), a base URL (its own override, else the connection's,
   * else the connection type's vendor default — see ./providerBaseUrl.ts) and a model catalog;
   * models are referenced as `<slug>/<model-id>` (see ./modelRef.ts), not through a build-time enum. */
  Custom = 'custom',
}

/** The providers that serve models (every AiProvider except the agent-harness credential
 * providers `claude-code` and `codex`). A qualified model reference `<provider>/<model-id>` may
 * name one of the built-in ones; `custom` is reached through a custom provider's slug instead. */
export const AI_MODEL_PROVIDERS = [
  AiProvider.OpenAI,
  AiProvider.Anthropic,
  AiProvider.Google,
  AiProvider.xAi,
  AiProvider.Custom,
] as const satisfies readonly AiProvider[];

export type AiModelProvider = (typeof AI_MODEL_PROVIDERS)[number];

/** Human-readable provider names: the `providerLabel` of a built-in provider's model and the model
 * dropdown's group title for it. A custom provider's models group under "Custom Provider — <slug>"
 * (see ./modelRef.ts `getAiModelInformation`), so the `custom` label here is only its prefix. */
export const AiProviderLabels: Record<AiProvider, string> = {
  [AiProvider.OpenAI]: 'OpenAI',
  [AiProvider.Anthropic]: 'Anthropic',
  [AiProvider.Google]: 'Google',
  [AiProvider.xAi]: 'xAI Grok',
  [AiProvider.ClaudeCode]: 'Claude Code',
  [AiProvider.Codex]: 'Codex',
  [AiProvider.Custom]: 'Custom Provider',
};

type TokenWindow = number | 'default';

export interface  AiModelInformation {
  provider: AiProvider;
  label: string;
  providerLabel: string;
  date: string;
  costPer1kTokens: { input: number; output: number } | Record<TokenWindow, { input: number; output: number }>;
  maxTokens: number;
}
```

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

## ai/openAi

**Source:** `ai/openAi.ts`

```typescript
import { AiModelInformation, AiProvider, convertCostPerMTokensToCostPer1kTokens } from './lib.js';

const PROVIDER_LABEL = 'OpenAI';

export enum OpenAiModels {
  GPT_4O = 'gpt-4o',
  GPT_4O_2024_11_20 = 'gpt-4o-2024-11-20',
  GPT_4O_2024_08_06 = 'gpt-4o-2024-08-06',
  GPT_4O_2024_05_13 = 'gpt-4o-2024-05-13',

  GPT_4O_MINI = 'gpt-4o-mini',
  GPT_4O_MINI_2024_07_18 = 'gpt-4o-mini-2024-07-18',

  OPENAI_O1 = 'o1',
  OPENAI_O1_2024_12_17 = 'o1-2024-12-17',

  OPENAI_O1_PRO = 'o1-pro',
  OPENAI_O1_PRO_2025_03_19 = 'o1-pro-2025-03-19',

  OPENAI_O1_MINI = 'o1-mini',
  OPENAI_O1_MINI_2024_09_12 = 'o1-mini-2024-09-12',

  OPENAI_O3 = 'o3',
  OPENAI_O3_2025_04_16 = 'o3-2025-04-16',

  OPENAI_O3_MINI = 'o3-mini',
  OPENAI_O3_MINI_2025_01_31 = 'o3-mini-2025-01-31',

  OPENAI_O3_PRO = 'o3-pro',
  OPENAI_O3_PRO_2025_06_10 = 'o3-pro-2025-06-10',

  OPENAI_O4_MINI = 'o4-mini',
  OPENAI_O4_MINI_2025_04_16 = 'o4-mini-2025-04-16',

  GPT_4_1 = 'gpt-4.1',
  GPT_4_1_2025_04_14 = 'gpt-4.1-2025-04-14',

  GPT_4_1_MINI = 'gpt-4.1-mini',
  GPT_4_1_MINI_2025_04_14 = 'gpt-4.1-mini-2025-04-14',

  GPT_4_1_NANO = 'gpt-4.1-nano',
  GPT_4_1_NANO_2025_04_14 = 'gpt-4.1-nano-2025-04-14',

  GPT_5 = 'gpt-5',
  GPT_5_2025_08_07 = 'gpt-5-2025-08-07',

  GPT_5_MINI = 'gpt-5-mini',
  GPT_5_MINI_2025_08_07 = 'gpt-5-mini-2025-08-07',

  GPT_5_NANO = 'gpt-5-nano',
  GPT_5_NANO_2025_08_07 = 'gpt-5-nano-2025-08-07',

  GPT_5_CHAT_LATEST = 'gpt-5-chat-latest',
  GPT_5_CHAT_LATEST_2025_08_07 = 'gpt-5-chat-latest-2025-08-07',

  GPT_5_1_CHAT_LATEST = 'gpt-5.1-chat-latest',
  GPT_5_1 = 'gpt-5.1',

  GPT_5_2 = 'gpt-5.2',
  GPT_5_2_2025_12_09 = 'gpt-5.2-2025-12-09',

  GPT_5_2_CHAT_LATEST = 'gpt-5.2-chat-latest',
  GPT_5_2_CHAT_LATEST_2025_12_09 = 'gpt-5.2-chat-latest-2025-12-09',

  GPT_5_2_PRO = 'gpt-5.2-pro',
  GPT_5_2_PRO_2025_12_09 = 'gpt-5.2-pro-2025-12-09',

  GPT_5_4 = 'gpt-5.4',
  GPT_5_4_2026_03_17 = 'gpt-5.4-2026-03-17',

  GPT_5_4_MINI = 'gpt-5.4-mini',
  GPT_5_4_MINI_2026_03_17 = 'gpt-5.4-mini-2026-03-17',

  GPT_5_4_NANO = 'gpt-5.4-nano',
  GPT_5_4_NANO_2026_03_17 = 'gpt-5.4-nano-2026-03-17',

  GPT_5_4_PRO = 'gpt-5.4-pro',
  GPT_5_4_PRO_2026_03_17 = 'gpt-5.4-pro-2026-03-17',

  GPT_5_5 = 'gpt-5.5',
  GPT_5_5_2026_04_23 = 'gpt-5.5-2026-04-23',

  GPT_5_6 = 'gpt-5.6',
  GPT_5_6_SOL = 'gpt-5.6-sol',
  GPT_5_6_TERRA = 'gpt-5.6-terra',
  GPT_5_6_LUNA = 'gpt-5.6-luna',

  GPT_6_ASTRA = 'gpt-6-astra',
}

/** OpenAI models proficient enough to drive agentic workflows (flagship + mid + budget tiers).
 * The first entry is the Codex harness default, so it stays on the balanced `gpt-5.6` alias
 * (which routes to Sol) rather than the pricier GPT-6 Astra. */
export const OpenAiAgentModels = [
  OpenAiModels.GPT_5_6,
  OpenAiModels.GPT_6_ASTRA,
  OpenAiModels.GPT_5_6_TERRA,
  OpenAiModels.GPT_5_6_LUNA,
  OpenAiModels.GPT_5_5,
  OpenAiModels.GPT_5_4,
  OpenAiModels.GPT_5_4_MINI,
  OpenAiModels.GPT_5_2,
  OpenAiModels.GPT_5_1,
  OpenAiModels.GPT_5,
  OpenAiModels.GPT_5_MINI,
] as const;

export const OpenAiModelInformationMap: Record<OpenAiModels, AiModelInformation> = {
  [OpenAiModels.GPT_4O]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4o',
    providerLabel: PROVIDER_LABEL,
    date: '2024-08-06',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2.5),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 16384,
  },
  [OpenAiModels.GPT_4O_2024_08_06]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4o 2024-08-06',
    providerLabel: PROVIDER_LABEL,
    date: '2024-08-06',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2.5),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 16384,
  },
  [OpenAiModels.GPT_4O_2024_11_20]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4o 2024-11-20',
    providerLabel: PROVIDER_LABEL,
    date: '2024-11-20',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2.5),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 16384,
  },
  [OpenAiModels.GPT_4O_2024_05_13]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4o 2024-05-13',
    providerLabel: PROVIDER_LABEL,
    date: '2024-05-13',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 16384,
  },

  [OpenAiModels.GPT_4O_MINI]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4o Mini',
    providerLabel: PROVIDER_LABEL,
    date: '2024-07-18',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.150),
      output: convertCostPerMTokensToCostPer1kTokens(0.600),
    },
    maxTokens: 16384,
  },

  [OpenAiModels.GPT_4O_MINI_2024_07_18]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4o Mini 2024-07-18',
    providerLabel: PROVIDER_LABEL,
    date: '2024-07-18',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.150),
      output: convertCostPerMTokensToCostPer1kTokens(0.600),
    },
    maxTokens: 16384,
  },

  [OpenAiModels.OPENAI_O1]: {
    provider: AiProvider.OpenAI,
    label: 'o1',
    providerLabel: PROVIDER_LABEL,
    date: '2024-12-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(60),
    },
    maxTokens: 100000,
  },

  [OpenAiModels.OPENAI_O1_2024_12_17]: {
    provider: AiProvider.OpenAI,
    label: 'o1 2024-12-17',
    providerLabel: PROVIDER_LABEL,
    date: '2024-12-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(60),
    },
    maxTokens: 100000,
  },

  [OpenAiModels.OPENAI_O1_PRO]: {
    provider: AiProvider.OpenAI,
    label: 'o1 Pro',
    providerLabel: PROVIDER_LABEL,
    date: '2025-03-19',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(150),
      output: convertCostPerMTokensToCostPer1kTokens(600),
    },
    maxTokens: 100000,
  },
  [OpenAiModels.OPENAI_O1_PRO_2025_03_19]: {
    provider: AiProvider.OpenAI,
    label: 'o1 Pro 2025-03-19',
    providerLabel: PROVIDER_LABEL,
    date: '2025-03-19',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(150),
      output: convertCostPerMTokensToCostPer1kTokens(600),
    },
    maxTokens: 100000,
  },

  [OpenAiModels.OPENAI_O1_MINI]: {
    provider: AiProvider.OpenAI,
    label: 'o1 Mini',
    providerLabel: PROVIDER_LABEL,
    date: '2024-09-12',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.1),
      output: convertCostPerMTokensToCostPer1kTokens(4.4),
    },
    maxTokens: 65536,
  },
  [OpenAiModels.OPENAI_O1_MINI_2024_09_12]: {
    provider: AiProvider.OpenAI,
    label: 'o1 Mini 2024-09-12',
    providerLabel: PROVIDER_LABEL,
    date: '2024-09-12',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.1),
      output: convertCostPerMTokensToCostPer1kTokens(4.4),
    },
    maxTokens: 65536,
  },

  [OpenAiModels.OPENAI_O3]: {
    provider: AiProvider.OpenAI,
    label: 'o3',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-16',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2),
      output: convertCostPerMTokensToCostPer1kTokens(8),
    },
    maxTokens: 100000,
  },
  [OpenAiModels.OPENAI_O3_2025_04_16]: {
    provider: AiProvider.OpenAI,
    label: 'o3 2025-04-16',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-16',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2),
      output: convertCostPerMTokensToCostPer1kTokens(8),
    },
    maxTokens: 100000,
  },

  [OpenAiModels.OPENAI_O3_MINI]: {
    provider: AiProvider.OpenAI,
    label: 'o3 Mini',
    providerLabel: PROVIDER_LABEL,
    date: '2025-01-31',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.1),
      output: convertCostPerMTokensToCostPer1kTokens(4.4),
    },
    maxTokens: 100000,
  },
  [OpenAiModels.OPENAI_O3_MINI_2025_01_31]: {
    provider: AiProvider.OpenAI,
    label: 'o3 Mini 2025-01-31',
    providerLabel: PROVIDER_LABEL,
    date: '2025-01-31',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.1),
      output: convertCostPerMTokensToCostPer1kTokens(4.4),
    },
    maxTokens: 100000,
  },

  [OpenAiModels.OPENAI_O3_PRO]: {
    provider: AiProvider.OpenAI,
    label: 'o3 Pro',
    providerLabel: PROVIDER_LABEL,
    date: '2025-06-10',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(20),
      output: convertCostPerMTokensToCostPer1kTokens(80),
    },
    maxTokens: 100000,
  },
  [OpenAiModels.OPENAI_O3_PRO_2025_06_10]: {
    provider: AiProvider.OpenAI,
    label: 'o3 Pro 2025-06-10',
    providerLabel: PROVIDER_LABEL,
    date: '2025-06-10',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(20),
      output: convertCostPerMTokensToCostPer1kTokens(80),
    },
    maxTokens: 100000,
  },

  [OpenAiModels.OPENAI_O4_MINI]: {
    provider: AiProvider.OpenAI,
    label: 'o4 Mini',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-16',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.1),
      output: convertCostPerMTokensToCostPer1kTokens(4.4),
    },
    maxTokens: 100000,
  },
  [OpenAiModels.OPENAI_O4_MINI_2025_04_16]: {
    provider: AiProvider.OpenAI,
    label: 'o4 Mini 2025-04-16',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-16',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.1),
      output: convertCostPerMTokensToCostPer1kTokens(4.4),
    },
    maxTokens: 100000,
  },

  [OpenAiModels.GPT_4_1]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4.1',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2),
      output: convertCostPerMTokensToCostPer1kTokens(8),
    },
    maxTokens: 32768,
  },
  [OpenAiModels.GPT_4_1_2025_04_14]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4.1 2025-04-14',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2),
      output: convertCostPerMTokensToCostPer1kTokens(8),
    },
    maxTokens: 32768,
  },

  [OpenAiModels.GPT_4_1_MINI]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4.1 Mini',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.4),
      output: convertCostPerMTokensToCostPer1kTokens(1.6),
    },
    maxTokens: 32768,
  },
  [OpenAiModels.GPT_4_1_MINI_2025_04_14]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4.1 Mini 2025-04-14',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.4),
      output: convertCostPerMTokensToCostPer1kTokens(1.6),
    },
    maxTokens: 32768,
  },

  [OpenAiModels.GPT_4_1_NANO]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4.1 Nano',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.1),
      output: convertCostPerMTokensToCostPer1kTokens(0.4),
    },
    maxTokens: 32768,
  },
  [OpenAiModels.GPT_4_1_NANO_2025_04_14]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4.1 Nano 2025-04-14',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.1),
      output: convertCostPerMTokensToCostPer1kTokens(0.4),
    },
    maxTokens: 32768,
  },

  [OpenAiModels.GPT_5]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.25),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_2025_08_07]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5 2025-08-07',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.25),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_MINI]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5 Mini',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.25),
      output: convertCostPerMTokensToCostPer1kTokens(2),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_MINI_2025_08_07]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5 Mini 2025-08-07',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.25),
      output: convertCostPerMTokensToCostPer1kTokens(2),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_NANO]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5 Nano',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.05),
      output: convertCostPerMTokensToCostPer1kTokens(0.4),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_NANO_2025_08_07]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5 Nano 2025-08-07',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.05),
      output: convertCostPerMTokensToCostPer1kTokens(0.4),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_CHAT_LATEST]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5 Chat Latest',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.25),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_CHAT_LATEST_2025_08_07]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5 Chat Latest 2025-08-07',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.25),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_1_CHAT_LATEST]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.1 Chat Latest',
    providerLabel: PROVIDER_LABEL,
    date: '2025-11-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.25),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_1]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.1',
    providerLabel: PROVIDER_LABEL,
    date: '2025-11-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.25),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 196000,
  },

  [OpenAiModels.GPT_5_2]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.2',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.75),
      output: convertCostPerMTokensToCostPer1kTokens(14),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_2_2025_12_09]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.2 2025-12-09',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.75),
      output: convertCostPerMTokensToCostPer1kTokens(14),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_2_CHAT_LATEST]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.2 Chat Latest',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.75),
      output: convertCostPerMTokensToCostPer1kTokens(14),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_2_CHAT_LATEST_2025_12_09]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.2 Chat Latest 2025-12-09',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.75),
      output: convertCostPerMTokensToCostPer1kTokens(14),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_2_PRO]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.2 Pro',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(21),
      output: convertCostPerMTokensToCostPer1kTokens(168),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_2_PRO_2025_12_09]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.2 Pro 2025-12-09',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(21),
      output: convertCostPerMTokensToCostPer1kTokens(168),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_4]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2.5),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_4_2026_03_17]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 2026-03-17',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2.5),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_4_MINI]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 Mini',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.75),
      output: convertCostPerMTokensToCostPer1kTokens(4.5),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_4_MINI_2026_03_17]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 Mini 2026-03-17',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.75),
      output: convertCostPerMTokensToCostPer1kTokens(4.5),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_4_NANO]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 Nano',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.2),
      output: convertCostPerMTokensToCostPer1kTokens(1.25),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_4_NANO_2026_03_17]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 Nano 2026-03-17',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.2),
      output: convertCostPerMTokensToCostPer1kTokens(1.25),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_4_PRO]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 Pro',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(30),
      output: convertCostPerMTokensToCostPer1kTokens(180),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_4_PRO_2026_03_17]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 Pro 2026-03-17',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(30),
      output: convertCostPerMTokensToCostPer1kTokens(180),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_5]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.5',
    providerLabel: PROVIDER_LABEL,
    date: '2026-04-23',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(30),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_5_2026_04_23]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.5 2026-04-23',
    providerLabel: PROVIDER_LABEL,
    date: '2026-04-23',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(30),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_6]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.6',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(30),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_6_SOL]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.6 Sol',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(30),
    },
    maxTokens: 128000,
  },
  /** Repriced 2026-07-30: Terra -20%, Luna -80%. Sol stayed at its launch rate. */
  [OpenAiModels.GPT_5_6_TERRA]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.6 Terra',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2),
      output: convertCostPerMTokensToCostPer1kTokens(12),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_6_LUNA]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.6 Luna',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.2),
      output: convertCostPerMTokensToCostPer1kTokens(1.2),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_6_ASTRA]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 6 Astra',
    providerLabel: PROVIDER_LABEL,
    date: '2026-09-03',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(10),
      output: convertCostPerMTokensToCostPer1kTokens(50),
    },
    maxTokens: 128000,
  },
} as const;
```

## ai/providerBaseUrl

**Source:** `ai/providerBaseUrl.ts`

```typescript
import { z } from 'zod';

/**
 * The base URL an AI provider's LLM requests go to, and where it comes from.
 *
 * A custom provider (`AiProvider.Custom`) resolves its base URL from three places, first hit wins:
 *
 * 1. **the AI setting** — `data.baseURL`, an explicit override the user typed on the provider;
 * 2. **the connection** — the connection's own `baseUrl` input (rendered as `result.baseUrl`), for
 *    connection types whose base URL *is* the LLM endpoint (`custom-provider-apikey`, or a vendor
 *    type whose optional base URL was filled in);
 * 3. **the connection type** — the vendor default declared on the connection type
 *    (`aiProvider.baseUrl` in its YAML: `https://api.groq.com/openai/v1` for `groq-bearer`, ...).
 *
 * The same function serves the credential resolver (what the LLM call uses), the API (what it
 * reports as `effectiveBaseUrl` / `derivedBaseUrl`) and the web add form (the placeholder it
 * shows before a setting exists). They never disagree only because of a contract on flagged
 * connection types: the API and the web read the connection's *input* `baseUrl` (they have no
 * secrets to render the result template with) while the resolver reads the *rendered*
 * `result.baseUrl`. So a connection type flagged `aiProvider` must name its base URL input
 * `baseUrl`, and its result's base URL must be exactly `{{ inputs.baseUrl }}` — a type that
 * renders anything else would report one URL and call another.
 */

/** Upper bound on a base URL (matches the connection input's own limit). */
export const AI_PROVIDER_BASE_URL_MAX_LENGTH = 2048;

/** A base URL a custom provider may use: absolute `http(s)://` URL, no query or fragment. */
export const AiProviderBaseUrlSchema = z.string()
  .trim()
  .min(1, 'Base URL is required')
  .max(AI_PROVIDER_BASE_URL_MAX_LENGTH)
  .refine((value) => normalizeAiProviderBaseUrl(value) !== undefined, {
    message: 'Base URL must be an absolute http:// or https:// URL without a query, fragment or credentials, e.g. https://api.groq.com/openai/v1',
  });

/** The outcome of checking a base URL candidate: the normalized URL, or why it is unusable. */
export type AiProviderBaseUrlCheck = { ok: true; baseUrl: string } | { ok: false; reason: string };

/**
 * Check a base URL candidate: trim it and strip a trailing slash, or say why it is unusable — not a
 * string, empty, too long, not an absolute `http(s)://` URL, carrying a query/fragment, or carrying
 * credentials (`https://user:pass@host`: a key belongs on the connection, never in the URL, which is
 * logged and shown).
 */
export function checkAiProviderBaseUrl(value: unknown): AiProviderBaseUrlCheck {
  if (typeof value !== 'string') return { ok: false, reason: 'not a string' };
  const trimmed = value.trim();
  if (trimmed.length === 0) return { ok: false, reason: 'empty' };
  if (trimmed.length > AI_PROVIDER_BASE_URL_MAX_LENGTH) return { ok: false, reason: `longer than ${AI_PROVIDER_BASE_URL_MAX_LENGTH} characters` };
  let url: URL;
  try {
    url = new URL(trimmed);
  } catch {
    return { ok: false, reason: 'not an absolute URL' };
  }
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return { ok: false, reason: `unsupported scheme ${url.protocol}` };
  if (!url.hostname) return { ok: false, reason: 'no host' };
  if (url.search || url.hash) return { ok: false, reason: 'has a query string or fragment' };
  if (url.username || url.password) return { ok: false, reason: 'has credentials in the URL' };
  return { ok: true, baseUrl: trimmed.replace(/\/+$/, '') };
}

/**
 * Trim a base URL and strip a trailing slash; `undefined` for an empty value or anything that is
 * not an absolute `http(s)://` URL without a query, fragment or `user:password@` (so a junk legacy
 * value falls through to the next source instead of being sent to the SDK).
 */
export function normalizeAiProviderBaseUrl(value: unknown): string | undefined {
  const check = checkAiProviderBaseUrl(value);
  return check.ok ? check.baseUrl : undefined;
}

/** Where an effective base URL came from. */
export type AiProviderBaseUrlSource = 'setting' | 'connection' | 'connectionType';

export interface AiProviderBaseUrlCandidates {
  /** the AI setting's `data.baseURL` (explicit override) */
  settingBaseUrl?: unknown;
  /** the connection's own base URL (its `baseUrl` input / rendered `result.baseUrl`) */
  connectionBaseUrl?: unknown;
  /** the connection type's vendor default (`aiProvider.baseUrl`) */
  connectionTypeBaseUrl?: unknown;
}

/** A candidate that was set but unusable, and so skipped for the next source. */
export interface DiscardedAiProviderBaseUrl {
  source: AiProviderBaseUrlSource;
  /** why it was skipped (see checkAiProviderBaseUrl) */
  reason: string;
}

export interface ResolvedAiProviderBaseUrl {
  /** the base URL to use, normalized; `undefined` when no candidate is usable */
  baseUrl?: string;
  /** which candidate won */
  source?: AiProviderBaseUrlSource;
  /** candidates that were set (non-empty) but invalid and were skipped — a stored override
   * silently rerouting to the next source; callers with a logger should warn about each. Only
   * candidates before the winner are listed. */
  discarded?: DiscardedAiProviderBaseUrl[];
}

/** Pick a custom provider's effective base URL: setting override → connection → connection type. */
export function resolveEffectiveAiProviderBaseUrl(candidates: AiProviderBaseUrlCandidates): ResolvedAiProviderBaseUrl {
  const ordered: [AiProviderBaseUrlSource, unknown][] = [
    ['setting', candidates.settingBaseUrl],
    ['connection', candidates.connectionBaseUrl],
    ['connectionType', candidates.connectionTypeBaseUrl],
  ];
  const discarded: DiscardedAiProviderBaseUrl[] = [];
  for (const [source, candidate] of ordered) {
    const check = checkAiProviderBaseUrl(candidate);
    if (check.ok) return discarded.length ? { baseUrl: check.baseUrl, source, discarded } : { baseUrl: check.baseUrl, source };
    // absent (undefined / null / blank) is "not set", not a discard
    if (candidate !== undefined && candidate !== null && !(typeof candidate === 'string' && candidate.trim() === '')) {
      discarded.push({ source, reason: check.reason });
    }
  }
  return discarded.length ? { discarded } : {};
}

/** Whether a base URL is plaintext `http://` (the secret proxy never injects a key into plaintext requests). */
export function isPlaintextAiProviderBaseUrl(baseUrl: string | undefined): boolean {
  return typeof baseUrl === 'string' && /^http:\/\//i.test(baseUrl.trim());
}
```

## ai/xAi

**Source:** `ai/xAi.ts`

```typescript
import { AiModelInformation, AiProvider, convertCostPerMTokensToCostPer1kTokens } from './lib.js';

export const PROVIDER_LABEL = 'xAI Grok';

export enum xAiModels {
  GROK_4 = 'grok-4',
  GROK_4_0709 = 'grok-4-0709',

  GROK_4_FAST_REASONING = 'grok-4-fast-reasoning',
  GROK_4_FAST_NON_REASONING = 'grok-4-fast-non-reasoning',

  GROK_CODE_FAST_1 = 'grok-code-fast-1',

  GROK_4_3 = 'grok-4.3',

  GROK_4_5 = 'grok-4.5',

  GROK_4_6 = 'grok-4.6',

  GROK_4_20_REASONING = 'grok-4.20-0309-reasoning',
  GROK_4_20_NON_REASONING = 'grok-4.20-0309-non-reasoning',
  GROK_4_20_MULTI_AGENT = 'grok-4.20-multi-agent-0309',

  GROK_BUILD_0_1 = 'grok-build-0.1',
}

/** xAI models proficient enough to drive agentic workflows (flagship + fast/code). */
export const xAiAgentModels = [
  xAiModels.GROK_4_6,
  xAiModels.GROK_4_5,
  xAiModels.GROK_4_20_REASONING,
  xAiModels.GROK_4_20_MULTI_AGENT,
  xAiModels.GROK_BUILD_0_1,
  xAiModels.GROK_4_3,
  xAiModels.GROK_4_FAST_REASONING,
  xAiModels.GROK_CODE_FAST_1,
] as const;

export const xAiModelInformationMap: Record<xAiModels, AiModelInformation> = {
  [xAiModels.GROK_4]: {
    provider: AiProvider.xAi,
    label: 'Grok 4',
    providerLabel: PROVIDER_LABEL,
    date: '2025-07-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 256000,
  },
  [xAiModels.GROK_4_0709]: {
    provider: AiProvider.xAi,
    label: 'Grok 4 (2025-07-09)',
    providerLabel: PROVIDER_LABEL,
    date: '2025-07-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 256000,
  },
  [xAiModels.GROK_4_FAST_REASONING]: {
    provider: AiProvider.xAi,
    label: 'Grok 4 Fast (Reasoning)',
    providerLabel: PROVIDER_LABEL,
    date: '2025-09-20',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.2),
      output: convertCostPerMTokensToCostPer1kTokens(0.5),
    },
    maxTokens: 2000000,
  },
  [xAiModels.GROK_4_FAST_NON_REASONING]: {
    provider: AiProvider.xAi,
    label: 'Grok 4 Fast (Non-Reasoning)',
    providerLabel: PROVIDER_LABEL,
    date: '2025-09-20',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.2),
      output: convertCostPerMTokensToCostPer1kTokens(0.5),
    },
    maxTokens: 2000000,
  },
  [xAiModels.GROK_CODE_FAST_1]: {
    provider: AiProvider.xAi,
    label: 'Grok Code Fast 1',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.2),
      output: convertCostPerMTokensToCostPer1kTokens(1.5),
    },
    maxTokens: 256000,
  },
  /** From Grok 4.3 onwards xAI prices in two tiers: prompts at or below 200k input
   * tokens bill at the base rate, anything larger bills the whole request at double. */
  [xAiModels.GROK_4_3]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.3',
    providerLabel: PROVIDER_LABEL,
    date: '2026-04-30',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(2.5),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(5),
      },
    },
    maxTokens: 1000000,
  },
  [xAiModels.GROK_4_5]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.5',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-08',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(2),
        output: convertCostPerMTokensToCostPer1kTokens(6),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(4),
        output: convertCostPerMTokensToCostPer1kTokens(12),
      },
    },
    maxTokens: 500000,
  },
  [xAiModels.GROK_4_6]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.6',
    providerLabel: PROVIDER_LABEL,
    date: '2026-08-12',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(2),
        output: convertCostPerMTokensToCostPer1kTokens(6),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(4),
        output: convertCostPerMTokensToCostPer1kTokens(12),
      },
    },
    maxTokens: 500000,
  },

  [xAiModels.GROK_4_20_REASONING]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.20 (Reasoning)',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-09',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(2.5),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(5),
      },
    },
    maxTokens: 1000000,
  },
  [xAiModels.GROK_4_20_NON_REASONING]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.20 (Non-Reasoning)',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-09',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(2.5),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(5),
      },
    },
    maxTokens: 1000000,
  },
  [xAiModels.GROK_4_20_MULTI_AGENT]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.20 (Multi-Agent)',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-09',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(2.5),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(5),
      },
    },
    maxTokens: 1000000,
  },

  [xAiModels.GROK_BUILD_0_1]: {
    provider: AiProvider.xAi,
    label: 'Grok Build 0.1',
    providerLabel: PROVIDER_LABEL,
    date: '2026-05-29',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1),
        output: convertCostPerMTokensToCostPer1kTokens(2),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2),
        output: convertCostPerMTokensToCostPer1kTokens(4),
      },
    },
    maxTokens: 256000,
  },
} as const;
```

## asset

**Source:** `asset.ts`

```typescript
import { BIQFile } from './schemas/file.js';

/** The types of assets */
export enum BIQAssetType {
  PlainText = 'plainText',
  Yaml = 'yaml',
  Json = 'json',
  File = 'file',
}


// if the asset is a file, it will be a BIQFile object
// if the asset is a plain text, it will be a string
// if the asset is a yaml or json, it will be an unknown type
export type BIQRuntimeAssets = BIQFile | string | unknown;
```

## canvas

**Source:** `canvas.ts`

```typescript
/**
 * NOTE:
 * Any types that is not used in the runtime is found in packages/types/src/canvas.ts
 * This file is to ONLY be used for types that is used in the runtime.
 */

/**
 * NOTE:
 * - In the UI (web), the draggable actor from the toolbox (sidebar) is of type BIQActor
 * - The actor that is part of the Canvas (an instance of BIQActor) is of type BIQCanvasActor
 * - The canvas data in the UI reactflow (editor) is an array of Node<N> and Edge<E> which is from BIQCanvasActor and BIQCanvasConnection
*/

/** the different types of actors in borgiq. */
export enum BIQActorType {
  CommentActor = 'CommentActor',
  EchoActor = 'EchoActor',
  CallableResponseActor = 'CallableResponseActor',
  CallFlowActor = 'CallFlowActor',
  HttpRequestActor = 'HttpRequestActor',
  RouterActor = 'RouterActor',
  MessageProcessorActor = 'MessageProcessorActor',
  DenoActor = 'DenoActor',
  DenoTestActor = 'DenoTestActor',
  SendEmailActor = 'SendEmailActor',
  DataStoreActor = 'DataStoreActor',
  WebhookResponseActor = 'WebhookResponseActor',
  ButtonTriggerActor = 'ButtonTriggerActor',
  CallableTriggerActor = 'CallableTriggerActor',
  ScheduledTriggerActor = 'ScheduledTriggerActor',
  UniversalTriggerActor = 'UniversalTriggerActor',
  WebhookTriggerActor = 'WebhookTriggerActor',
  EmailTriggerActor = 'EmailTriggerActor',
  InterfaceTriggerActor = 'InterfaceTriggerActor',
  InterfaceActor = 'InterfaceActor',
  InterfaceStatusActor = 'InterfaceStatusActor',
  AiActor = 'AiActor',
  AiRouterActor = 'AiRouterActor',
  AiAgentActor = 'AiAgentActor',
  /** The legacy orchestrator-loop AI agent. Deprecated + hidden from the palette; existing
   *  instances keep running. New AI agents use AiAgentActor (the Lambda implementation). */
  DeprecatedAiAgent = 'DeprecatedAiAgent',
  PythonActor = 'PythonActor',
  AgentHarnessActor = 'AgentHarnessActor',
  AppTriggerActor = 'AppTriggerActor',
  ReactAppTriggerActor = 'ReactAppTriggerActor',
  CollectionActor = 'CollectionActor',
  StreamActor = 'StreamActor',
  McpServerActor = 'McpServerActor',
}

/** Authorization level for webhook trigger actors */
export enum BIQWebhookAuthorizationLevel {
  /** Anyone can call the webhook */
  Public = 'public',
  /** Only calls with a valid app actor webhook token are allowed */
  Apps = 'apps',
  /**
   * Only calls presenting a valid API key (`Authorization: Bearer` or `X-Api-Key`) are allowed. Today the
   * accepted API key is a personal access token whose owner is a member of the trigger's workspace;
   * workspace-scoped keys slot into the same level later.
   */
  ApiKey = 'apiKey',
  /** Calls presenting either a valid app actor webhook token or a valid API key are allowed */
  AppsAndApiKey = 'appsAndApiKey',
}

/**
 * Whether a webhook authorization level admits an app actor webhook token (`x-app-actor-token`).
 * Accepts the raw stored string so callers reading un-narrowed configuration (editor stores,
 * select-option rows) can ask without casting; an unknown or missing level answers false.
 */
export const webhookLevelAcceptsAppToken = (level: string | null | undefined): boolean =>
  level === BIQWebhookAuthorizationLevel.Apps || level === BIQWebhookAuthorizationLevel.AppsAndApiKey;

/** Whether a webhook authorization level admits an API key (`Authorization: Bearer` / `X-Api-Key`). */
export const webhookLevelAcceptsApiKey = (level: string | null | undefined): boolean =>
  level === BIQWebhookAuthorizationLevel.ApiKey || level === BIQWebhookAuthorizationLevel.AppsAndApiKey;

export const DEFAULT_SOURCE_PORT_ID = 'SPRTdefault';
export const DEFAULT_TARGET_PORT_ID = 'TPRTdefault';
```

## common

**Source:** `common.ts`

```typescript
/**
 * NOTE:
 * Any types that is not used in the runtime is found in packages/types/src/common.ts
 * This file is to ONLY be used for types that is used in the runtime.
 */

/** the attributes to use to filter the listings in borgiq */
export interface BIQListFilter {
  /** the current page. initial page is 0. */
  page: number;
  /** number of records to show per page. */
  pageSize: number;
  /** search query to use for the listing */
  search: string;
  /** the column to sort by */
  sortBy: string;
  /** the order to sort by */
  sortOrder: 'asc' | 'desc';
  /** the additional params to filter by */
  [key: string]: undefined | number | string | string[]
}

/** The engines used to store the assets */
export enum BIQFileStorageEngine {
  S3 = 's3',
}

/** The S3 file status */
export enum BIQFileStatus {
  UploadPending = 'upload_pending',
  UploadSuccess = 'upload_success',
  UploadFailure = 'upload_failure',
  DeletePending = 'delete_pending',
}

/** The file usage type/purpose */
export enum BIQFileUsageType {
  /** Files associated with workspace assets (images, documents, etc.) */
  Asset = 'ASSET',
  /** Claude Code session data (conversation history, settings) for session persistence */
  SandboxSessionData = 'SANDBOX_SESSION_DATA',
  /** Files attached to actor messages (user uploads, interface uploads, sandbox output, generated content) */
  ActorMessage = 'ACTOR_MESSAGE',
  /** Temporary files used during processing */
  Temporary = 'TEMPORARY',
  /** ReactAppTriggerActor built `dist/` artifacts — survive build-flowrun archival; only superseded builds are GC'd (§4.4.5) */
  ReactDistArtifact = 'REACT_DIST_ARTIFACT',
}
```

## connection

**Source:** `connection.ts`

```typescript
/** The authentication types for connections */
export enum BIQConnectionAuthType {
  AWS = 'awsKeyBased',
  AWS_ROLE = 'awsRoleBased',
  OAUTH1 = 'oauth1',
  OAUTH2 = 'oauth2',
  MCP_OAUTH = 'mcpOauth',
  BEARER = 'bearer',
  BASIC = 'basic',
  API_KEY = 'apiKey',
  CUSTOM = 'custom',
  NONE = 'none',
}
```

## file

**Source:** `file.ts`

```typescript

// this is the return type of AWS S3 presigned post
export interface S3PresignedPost {
  url: string;
  fields: { [key: string]: string };
}

export interface FileRuntimeUploadResponse {
  files: {
    id: string;
    uploadIndex: number;
    uploadUrl: S3PresignedPost;
  }[];
}
```

## flowrun

**Source:** `flowrun.ts`

```typescript
/**
 * NOTE:
 * Any types that is used in the runtime is found in packages/runtime-types/src/flowrun.ts
 * This file is to ONLY be used for types that is used in the runtime.
 */

export const TRIGGER_MESSAGE_TYPES = ['webhookTrigger', 'scheduledTrigger', 'buttonTrigger', 'manualTrigger', 'callableTrigger', 'emailTrigger', 'interfaceGetTrigger', 'interfacePostTrigger', 'testActorTrigger', 'appGetTrigger', 'reactAppBuildTrigger', 'reactAppServeTrigger', 'mcpToolCallTrigger', 'mcpInitializeTrigger', 'mcpToolListTrigger', 'universalTrigger', 'lifecycleTrigger'] as const;

export const MESSAGE_TYPES = ['actor', ...TRIGGER_MESSAGE_TYPES] as const;

export interface BIQTraceRecord {
  source: 'orchestrator' | 'runtime' | 'actor';
  type: 'info' | 'warning' | 'error' | 'stdout' | 'stderr';
  timestamp: number;
  message: string;
  stack?: string;
  orgId?: string;
  wspId?: string;
  canvasId?: string;
  flowrunId?: string;
  flowrunJobId?: string;
  actorId?: string;
  /** OTel trace id of the invocation that produced this record — correlates run logs to Honeycomb traces. */
  traceId?: string;
}
```

## lambda

**Source:** `lambda.ts`

```typescript
/** NOTE: This file is to ONLY be used for types that is used in the runtime. */

/**
 * See: https://docs.aws.amazon.com/lambda/latest/dg/nodejs-context.html
 * The types were obtained from @types/aws-lambda
 */


/** callback function parameter signature in the lambda function handler */
export type Callback<TResult = any> = (error?: Error | string | null, result?: TResult) => void; // eslint-disable-line @typescript-eslint/no-explicit-any

/** the context parameter in the lambda function handler */
export interface LambdaContext {
  callbackWaitsForEmptyEventLoop: boolean;
  functionName: string;
  functionVersion: string;
  invokedFunctionArn: string;
  memoryLimitInMB: string;
  awsRequestId: string;
  logGroupName: string;
  logStreamName: string;
  getRemainingTimeInMillis(): number;
}
```

## prefix

**Source:** `prefix.ts`

```typescript
/** NOTE: This file is to ONLY be used for types that is used in the runtime. */

/** Prefix to use when generating new model id's. Model prefix should be unique across borgiq. */
enum Prefix {
  AiSetting = 'AISG',
  Actor = 'ACTR',
  ActorTemplate = 'ATMP',
  AiAssistantSession = 'AISN',
  AppSession = 'APSN',
  AuditLog = 'ALOG',
  Asset = 'ASST',
  AwsLambdaRuntime = 'ALRT',
  BeeQueueJob = 'BQJB',
  BIQ = 'BIQ0',
  Canvas = 'CANV',
  CanvasData = 'CNDT',
  CanvasRuntimeBuild = 'CRBD',
  Connection = 'CONN',
  DataStore = 'DAST',
  Edge = 'EDGE',
  Email = 'EMAL',
  EmailVerificationCode = 'EVCD',
  File = 'FILE',
  Flowrun = 'FLRN',
  FlowrunMessage = 'FMSG',
  FlowrunJob = 'FJOB',
  FlowrunJobInvocation = 'FJBI',
  FlowrunJobLog = 'FJBL',
  FlowrunJobResult = 'FJBR',
  FlowrunCallbackTokenResponse = 'FCTR',
  FlowrunInterfaceSubmission = 'FISB',
  Invocation = 'INVC',
  McpOauthDiscovery = 'MCPD',
  OAuthAccount = 'OATH',
  OauthApplication = 'OAPP',
  OauthAccessToken = 'OATK',
  OauthConsent = 'OACS',
  OnboardingStep = 'OBST',
  Org = 'ORG0',
  OrgMembership = 'ORMS',
  OrgAndWorkspaceInvitation = 'INVI',
  Runtime = 'RUNT',
  Runner = 'RUNR',
  SandboxSession = 'SBXS',
  Secret = 'SECR',
  Session = 'SESS',
  SourcePort = 'SPRT',
  StorageBucket = 'STBU',
  StorageFile = 'STFI',
  Stream = 'STRM',
  TargetPort = 'TPRT',
  TemplateApp = 'TAPP',
  TemplateCategory = 'TCTG',
  Token = 'TOKN',
  User = 'USER',
  UserAuthSession = 'USAS',
  UserOauthAccount = 'USAK',
  Workspace = 'WKSP',
  WorkspaceMembership = 'WSMS',
  WebhookRequest = 'WREQ',
  WebViewerContent = 'WVCN',
}

export default Prefix;
```

## runtime

**Source:** `runtime.ts`

```typescript
/** NOTE: This file is to ONLY be used for types that is used in the runtime. */

import { RuntimeError, RuntimeSignal, RuntimeValidationError } from './schemas/index.js';

/** The type of invocation for an actor. It is basically in invocation of a particular function in an actor instance. i.e. actor.receive(), actor.interpolate(), etc... */
export enum BIQRuntimeInvocationType {
  Ping = 'ping',
  Receive = 'receive',
  Interpolate = 'interpolate',
  Validate = 'validate',
  InterpolateOutputs = 'interpolate-outputs',
}

/** the response status for invoking the runtime */
export enum BIQRuntimeResponseStatus {
  Success = 'success',
  Error = 'error',
}


/** information about the borgIQ flowrun message type associated with the runtime actor being invoked. */
export enum BIQFlowrunMessageType {
  Actor = 'actor',
  WebhookTrigger = 'webhookTrigger',
  ScheduledTrigger = 'scheduledTrigger',
  ButtonTrigger = 'buttonTrigger',
  ManualTrigger = 'manualTrigger',
  CallableTrigger = 'callableTrigger',
  EmailTrigger = 'emailTrigger',
  InterfaceGetTrigger = 'interfaceGetTrigger',
  InterfacePostTrigger = 'interfacePostTrigger',
  AppGetTrigger = 'appGetTrigger',
  UniversalTrigger = 'universalTrigger',
  LifecycleTrigger = 'lifecycleTrigger',
}

/** this indicates where the error occurred when invoking actor's runtime method. in the orchestrator or in the runtime. */
export enum BIQRuntimeErrorLocation {
  Orchestrator = 'orchestrator',
  Runtime = 'runtime',
}

export enum BIQRuntimeRetryStrategy {
  Immediate = 'immediate',
  Fixed = 'fixed',
  Exponential = 'exponential'
}

/** the object representing an actor's interpolated configuration information */
export interface BIQRuntimeActorConfiguration<O> {
  // the interpolated connection
  connection: { [key: string]: any }; // eslint-disable-line @typescript-eslint/no-explicit-any
  // the interpolated credentials
  credentials: { [key: string]: string };
  // the interpolated inputs
  inputs: { [key: string]: any }; // eslint-disable-line @typescript-eslint/no-explicit-any
  // the interpolated vars
  vars: { [key: string]: any }; // eslint-disable-line @typescript-eslint/no-explicit-any
  // the interpolated options
  options: O;
  // the interpolated assets
  assets: { [key: string]: any }; // eslint-disable-line @typescript-eslint/no-explicit-any
}


export interface BIQActorReceiveResponse<M> {
  status: BIQRuntimeResponseStatus;

  /** if there was an error invoking the runtime method */
  error?: RuntimeError;

  /** The array of new messages emitted by the actor due to the invocation of the `receive` method */
  messages: { [sourcePortId: string]: M[] };

  /** The validation errors that occurred when invoking the runtime method */
  validationErrors?: RuntimeValidationError[];

  /** We need to signal the orchestrator to do some work (i.e delay, wait for external events, etc) **/
  signal?: RuntimeSignal;
}
```

## sandbox

**Source:** `sandbox.ts`

```typescript
/**
 * Sandbox types shared between borgiq-platform and borgiq-lambda-runtime.
 * NOTE: This file is to ONLY be used for types needed in both the platform and the lambda runtime.
 */
import { z } from 'zod';

import { AiToolCallSchema, BIQAiToolMessageOutputSchema } from './ai/index.js';
import { BIQFileSchema } from './schemas/file.js';


/** Agent harness provider options for display in UI */
export enum BIQSandboxProviders {
  E2B = 'e2b',
  DAYTONA = 'daytona',
  /** AgentLambdaActor sessions: segments run in the agent-sessions Lambda function, not a
   * sandbox VM. Never valid for SandboxProviderFactory — it exists so SandboxSessionData
   * can carry the session's runtime kind. */
  LAMBDA = 'lambda',
}

/** Agent harness CLI type. Selects which coding-agent CLI runs in the sandbox.
 * Defaults to 'claude' everywhere for backward compatibility.
 */
export enum BIQAgentHarnessType {
  Claude = 'claude',
  Codex = 'codex',
  OpenCode = 'opencode',
  Pi = 'pi',
}

export const BIQAgentHarnessTypeSchema = z.nativeEnum(BIQAgentHarnessType);

/** Status of a sandbox instance */
export enum BIQSandboxStatus {
  Creating = 'creating',
  Running = 'running',
  Idle = 'idle',
  ShuttingDown = 'shutting_down',
  Stopped = 'stopped',
  Error = 'error',
}

export const BIQSandboxStatusSchema = z.enum(BIQSandboxStatus);

/** Status update types from sandbox to orchestrator.
 * These values match what the Claude Code hooks script sends to the status endpoint.
 */
export enum BIQAgentHarnessStatusUpdateType {
  /** Loop result with accumulated response and tool calls (from pre-tool-use hook) */
  AgentHarnessLoop = 'agent-harness-loop',
  /** Tool execution result (from post-tool-use and post-tool-use-failure hooks) */
  ToolResult = 'tool-result',
  /** Execution completed successfully (from stop hook) */
  Complete = 'complete',
  /** Notification from Claude Code - permission prompts, etc. (from notification hook) */
  Notification = 'notification',
  /** Error occurred during execution */
  Error = 'error',
  /** Agent lambda segment liveness signal (~60s cadence); reschedules the watchdog */
  Heartbeat = 'heartbeat',
  /** Agent lambda segment reached its deadline margin and persisted state; the
   * orchestrator should launch the next segment */
  Checkpointed = 'checkpointed',
}

export const BIQAgentHarnessStatusUpdateTypeSchema = z.enum(BIQAgentHarnessStatusUpdateType);

/** Output stream type */
export enum BIQSandboxOutputStream {
  Stdout = 'stdout',
  Stderr = 'stderr',
}

export const BIQSandboxOutputStreamSchema = z.enum(BIQSandboxOutputStream);

/** Basic session info returned to the runtime */
export const SandboxSessionInfoSchema = z.object({
  sessionId: z.string(),
  sandboxId: z.string(),
  status: BIQSandboxStatusSchema,
});

export type SandboxSessionInfo = z.infer<typeof SandboxSessionInfoSchema>;

/** Content type for content status updates.
 * @deprecated Never produced by any hook or sidecar and never read by the orchestrator. Kept so
 * old payloads still parse; reasoning travels on `SandboxStatusUpdateDataSchema.reasoning`. */
export const SandboxContentTypeSchema = z.enum(['thinking', 'response', 'partial']);
export type SandboxContentType = z.infer<typeof SandboxContentTypeSchema>;

/** Data for sandbox status update */
export const SandboxStatusUpdateDataSchema = z.object({
  // Tool-related fields (from PostToolUse hook - legacy)
  toolName: z.string().optional(),
  toolCallId: z.string().optional(),
  toolInput: z.unknown().optional(),
  toolOutput: z.unknown().optional(),

  // New aligned format fields (for agent-harness-loop and tool-result messages)
  /** Accumulated response text before this event (for agent-harness-loop) */
  response: z.string().optional(),
  /** Tool calls data (for agent-harness-loop) - array of concurrent tool calls */
  toolCalls: z.array(AiToolCallSchema).optional(),
  /** Tool output (for tool-result) */
  output: BIQAiToolMessageOutputSchema.optional(),
  /** Whether the tool call resulted in an error (for tool-result) */
  isError: z.boolean().optional(),
  /** The model's thinking / reasoning for this turn (for agent-harness-loop). Posted by the
   * lambda segment host (pi thinking blocks) and the harness hook/sidecars (Claude transcript
   * thinking blocks, Codex reasoning items, pi/OpenCode reasoning parts). Clipped by the
   * orchestrator before it is persisted. */
  reasoning: z.string().optional(),

  // Generic message field
  message: z.string().optional(),
  exitCode: z.number().optional(),

  // Content/thinking fields (legacy)
  /** @deprecated Never produced; use `response` (text) and `reasoning` (thinking) instead. */
  generatedContent: z.string().optional(),
  /** @deprecated Never produced; see SandboxContentTypeSchema. */
  contentType: SandboxContentTypeSchema.optional(),

  // Notification fields (from Notification hook)
  /** Type of notification (e.g., 'permission_prompt', 'idle_prompt', 'auth_success') */
  notificationType: z.string().optional(),
  /** Notification title */
  title: z.string().optional(),

  // Working directory (provided by all hooks)
  /** Current working directory in the sandbox */
  cwd: z.string().optional(),

  // Raw hook data for debugging/extensibility
  /** Raw hook data when event type is unknown */
  hookData: z.unknown().optional(),

  // Agent lambda segment fields (heartbeat / checkpointed / complete posts)
  /** The segment index this post belongs to; stale-segment posts are dropped */
  segmentIndex: z.number().int().nonnegative().optional(),
  /** The epoch token granted to this segment; must match the session record */
  epochToken: z.string().optional(),
  /** Workspace size as last measured by the segment host (feeds the AgentSession ledger) */
  workspaceSizeInBytes: z.number().int().optional(),
  /** Workspace file count as last measured by the segment host */
  workspaceFileCount: z.number().int().optional(),
  /** Workspace zip the segment uploaded at finalize (complete posts only) */
  outputZipFile: BIQFileSchema.optional(),
  /** Pi session zip the segment uploaded at finalize (complete posts only) */
  sessionDataFile: BIQFileSchema.optional(),
  /** Zip-fallback mode: BIQFile id of the combined checkpoint the segment uploaded
   * (checkpointed posts only); the orchestrator carries it into the next segment. */
  checkpointFileId: z.string().optional(),
  /** Why the run ended, set by the segment host on a terminal post (complete/error).
   * Drives the done-port `meta.endReason`; defaults to completed/error when absent. */
  endReason: z.enum(['completed', 'timeout', 'error', 'max-loop-count']).optional(),
  /** Host-reported LLM token usage for THIS segment (per-segment delta of pi's session stats —
   * not cumulative, so the orchestrator writes one aiLog row per segment without double-counting).
   * Posted on checkpointed + complete. */
  usageReport: z.object({
    promptTokens: z.number().int().nonnegative(),
    completionTokens: z.number().int().nonnegative(),
    totalTokens: z.number().int().nonnegative(),
    cacheReadTokens: z.number().int().nonnegative().optional(),
    cacheWriteTokens: z.number().int().nonnegative().optional(),
  }).optional(),
  /** Host-estimated Lambda billing for this segment. Event invokes return no LogResult, so the
   * host reports its own wall-clock (billedDurationMs) + function memory; the orchestrator accrues
   * cost from it via the lambda-cost map. Posted on checkpointed + complete. */
  lambdaBilling: z.object({
    billedDurationMs: z.number().nonnegative(),
    memoryMB: z.number().int().positive(),
    /** Function ephemeral storage (/tmp) size — the host knows it from its segment payload;
     * carried here so the orchestrator can price the invoke without re-resolving runtime config. */
    ephemeralMB: z.number().int().positive(),
    /** The architecture the host ran on (`x86_64` | `arm64`), so the orchestrator prices the segment
     * at the right rate. Absent from hosts predating arm64 support (priced as x86_64). */
    architecture: z.enum(['x86_64', 'arm64']).optional(),
  }).optional(),
  /** Assistant turns consumed across ALL segments so far (this segment's count seeded by the prior
   * segments' total). Reported on checkpointed + complete; the orchestrator persists it to the
   * session and forwards it to the next segment so maxLoopCount is enforced session-wide rather
   * than reset per segment. */
  loopCountUsed: z.number().int().nonnegative().optional(),
});

export type SandboxStatusUpdateData = z.infer<typeof SandboxStatusUpdateDataSchema>;

/** Sandbox status update payload */
export const AgentHarnessStatusUpdateSchema = z.object({
  sessionId: z.string(),
  // Accept both enum values and string literals for new message types
  type: BIQAgentHarnessStatusUpdateTypeSchema,
  data: SandboxStatusUpdateDataSchema,
});

export type AgentHarnessStatusUpdate = z.infer<typeof AgentHarnessStatusUpdateSchema>;

/** Sandbox output stream payload */
export const SandboxOutputStreamPayloadSchema = z.object({
  sessionId: z.string(),
  stream: BIQSandboxOutputStreamSchema,
  chunk: z.string(),
});

export type SandboxOutputStreamPayload = z.infer<typeof SandboxOutputStreamPayloadSchema>;

/** External tool invocation request from sandbox */
export const SandboxExternalToolInvokeSchema = z.object({
  sessionId: z.string(),
  toolCallId: z.string(),
  toolName: z.string(),
  toolInput: z.unknown(),
});

export type SandboxExternalToolInvoke = z.infer<typeof SandboxExternalToolInvokeSchema>;

/** Tool definition passed to Claude Code in sandbox */
export const SandboxExternalToolDefinitionSchema = z.object({
  name: z.string(),
  description: z.string(),
  jsonSchema: z.record(z.string(), z.unknown()).optional(),
  actorId: z.string(),
});

export type SandboxExternalToolDefinition = z.infer<typeof SandboxExternalToolDefinitionSchema>;
```

## signal

**Source:** `signal.ts`

```typescript

export enum BIQRuntimeSignalType {
  DelayUntil = 'delayUntil',
  CallFlow = 'callFlow',
  CallableResponse = 'callableResponse',
  WaitForCallbackToken = 'waitForCallbackToken',
  NotifyCallbackToken = 'notifyCallbackToken',
  WebhookRespond = 'webhookRespond',
  InterfaceGet = 'interfaceGet',
  InterfacePost = 'interfacePost',
  InterfaceRender = 'interfaceRender',
  AiAgent = 'aiAgent',
  Ai = 'ai',
  AgentHarness = 'agentHarness',
  AgentLambda = 'agentLambda',
  AppGet = 'appGet',
  ReactAppBuild = 'reactAppBuild',
  McpServer = 'mcpServer',
}
```
