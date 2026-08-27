# Common Types and Utilities

Shared TypeScript types and utilities: common types, AI model definitions (Anthropic, OpenAI, Google, xAI), canvas types, runtime types, sandbox types, file types, flowrun types, lambda types, signal types, asset types, and prefix definitions.

## Table of Contents

- [ai/anthropic.ts](#aianthropic)
- [ai/google.ts](#aigoogle)
- [ai/index.ts](#aiindex)
- [ai/lib.ts](#ailib)
- [ai/openAi.ts](#aiopenai)
- [ai/xAi.ts](#aixai)
- [asset.ts](#asset)
- [canvas.ts](#canvas)
- [common.ts](#common)
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
}

/** Anthropic models proficient enough to drive agentic workflows (flagship + fast variants).
 * The first entry seeds the cross-provider agent default, so keep a balanced Sonnet first. */
export const AnthropicAgentModels = [
  AnthropicModels.CLAUDE_5_SONNET,
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
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
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
}

/** Google models proficient enough to drive agentic workflows (Gemini flagship + flash/lite). */
export const GoogleAgentModels = [
  GoogleAiModels.GEMINI_3_1_PRO_PREVIEW,
  GoogleAiModels.GEMINI_3_5_FLASH,
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

export { AiProvider } from './lib.js';
export { AnthropicAgentModels } from './anthropic.js';
export { OpenAiAgentModels } from './openAi.js';
export { GoogleAgentModels } from './google.js';
export { xAiAgentModels } from './xAi.js';

export enum AiModelType {
  Chat = 'chat',
  Reasoning = 'reasoning',
}

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
}

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
}

/** OpenAI models proficient enough to drive agentic workflows (GPT-5 family flagship + mini). */
export const OpenAiAgentModels = [
  OpenAiModels.GPT_5_6,
  OpenAiModels.GPT_5_6_TERRA,
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
  [OpenAiModels.GPT_5_6_TERRA]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.6 Terra',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2.5),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_6_LUNA]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.6 Luna',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1),
      output: convertCostPerMTokensToCostPer1kTokens(6),
    },
    maxTokens: 128000,
  },
} as const;
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
}

/** xAI models proficient enough to drive agentic workflows (flagship + fast/code). */
export const xAiAgentModels = [
  xAiModels.GROK_4_5,
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
  [xAiModels.GROK_4_3]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.3',
    providerLabel: PROVIDER_LABEL,
    date: '2026-04-30',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.25),
      output: convertCostPerMTokensToCostPer1kTokens(2.5),
    },
    maxTokens: 256000,
  },
  [xAiModels.GROK_4_5]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.5',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-08',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2),
      output: convertCostPerMTokensToCostPer1kTokens(6),
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
  McpServerActor = 'McpServerActor',
  StreamActor = 'StreamActor',
}

/** Authorization level for webhook trigger actors */
export enum BIQWebhookAuthorizationLevel {
  /** Anyone can call the webhook */
  Public = 'public',
  /** Only calls with a valid app actor webhook token are allowed */
  Apps = 'apps',
}

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
  AuditLog = 'ALOG',
  Asset = 'ASST',
  AwsLambdaRuntime = 'ALRT',
  BeeQueueJob = 'BQJB',
  BIQ = 'BIQ0',
  Canvas = 'CANV',
  CanvasData = 'CNDT',
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
  // store the code that is to be run in the runtime for the actor (ONLY NodeJS actor)
  code: string;
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
 * Sandbox types shared between the platform and the lambda runtime.
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

/** Content type for content status updates */
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

  // Generic message field
  message: z.string().optional(),
  exitCode: z.number().optional(),

  // Content/thinking fields (legacy)
  /** Generated content before this status (e.g., thinking before tool call) */
  generatedContent: z.string().optional(),
  /** Content type for content status updates */
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
