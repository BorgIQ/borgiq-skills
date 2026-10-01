# ai/google

Generated from the platform's runtime types. Do not edit.

Google Gemini model ids, the agent model list, and per-model information including prices.

See also: [ai/lib](lib.md).

## ai/google

**Source:** `ai/google.ts`

```typescript
import { AiModelInformation, AiProvider, convertCostPerMTokensToCostPer1kTokens } from './lib.js';

const PROVIDER_LABEL = 'Google';

export enum GoogleAiModels {
  /** No longer served by the Gemini API, which now lists only Gemma 4. */
  GEMMA_3_1B = 'gemma-3-1b-it',
  GEMMA_3_4B = 'gemma-3-4b-it',
  GEMMA_3_12B = 'gemma-3-12b-it',
  GEMMA_3_27B = 'gemma-3-27b-it',

  /** Every Gemini 2.0 id is shut down: Flash and Flash-Lite on 2026-06-01, the Flash Thinking
   * experiment on 2025-12-02. */
  GEMINI_2_0_FLASH = 'gemini-2.0-flash',
  GEMINI_2_0_FLASH_001 = 'gemini-2.0-flash-001',
  
  GEMINI_2_0_FLASH_LITE = 'gemini-2.0-flash-lite',
  GEMINI_2_0_FLASH_LITE_001 = 'gemini-2.0-flash-lite-001',
  
  
  GEMINI_2_0_FLASH_THINKING_EXP = 'gemini-2.0-flash-thinking-exp',
  GEMINI_2_0_FLASH_THINKING_EXP_1_21 = 'gemini-2.0-flash-thinking-exp-01-21',
  
  /** Since 2026-09-18 the 2.5 models serve only projects that already used them; they are not
   * deprecated. The dated 2.5 preview snapshots are shut down (the last on 2025-12-02). */
  GEMINI_2_5_PRO = 'gemini-2.5-pro',
  GEMINI_2_5_PRO_PREVIEW_03_25 = 'gemini-2.5-pro-preview-03-25',
  GEMINI_2_5_PRO_PREVIEW_06_05 = 'gemini-2.5-pro-preview-06-05',

  GEMINI_2_5_FLASH = 'gemini-2.5-flash',
  GEMINI_2_5_FLASH_PREVIEW_04_17 = 'gemini-2.5-flash-preview-04-17',
  GEMINI_2_5_FLASH_PREVIEW_05_20 = 'gemini-2.5-flash-preview-05-20',

  GEMINI_2_5_FLASH_LITE_PREVIEW_06_17 = 'gemini-2.5-flash-lite-preview-06-17',

  /** Shut down 2026-03-09; the id now points to gemini-3.1-pro-preview. */
  GEMINI_3_PRO_PREVIEW = 'gemini-3-pro-preview',

  GEMINI_3_FLASH_PREVIEW = 'gemini-3-flash-preview',

  GEMINI_3_1_PRO_PREVIEW = 'gemini-3.1-pro-preview',

  GEMINI_3_5_FLASH = 'gemini-3.5-flash',

  /** Shuts down 2027-05-07 (Google's substitute: gemini-3.5-flash-lite). */
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
    maxTokens: 65536,
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
    date: '2025-11-18',
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
    date: '2025-12-17',
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
    date: '2026-05-07',
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
