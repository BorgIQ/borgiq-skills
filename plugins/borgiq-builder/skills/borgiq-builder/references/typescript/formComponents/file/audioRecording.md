# formComponents/file/audioRecording

Generated from the platform's runtime types. Do not edit.

The schema for an audio recording input and its mime types.

See also: [formComponents/base](../base.md).

## formComponents/file/audioRecording

**Source:** `formComponents/file/audioRecording.ts`

```typescript
import { z } from 'zod';
import { BIQFormComponentType, BIQBaseFormComponentZodSchema } from '../base.js';

/** The mime types applicable for audio recordings */
export enum BIQAudioMimeType {
  MPEG = 'audio/mpeg',
  WAV = 'audio/wav',
  OGG = 'audio/ogg',
  WEBM = 'audio/webm',
  AAC = 'audio/aac',
}

/** The file extensions for each mime type for audio recordings */
export const BIQAudioFileExtension: Record<BIQAudioMimeType, string> = {
  [BIQAudioMimeType.MPEG]: 'mp3',
  [BIQAudioMimeType.WAV]: 'wav',
  [BIQAudioMimeType.OGG]: 'oga',
  [BIQAudioMimeType.WEBM]: 'weba',
  [BIQAudioMimeType.AAC]: 'aac',
};

/** The schema for an audio recording input component */
export const BIQAudioRecordingZodSchema = BIQBaseFormComponentZodSchema.extend({
  /** The type of the component is `audioRecordingInput` for the form builder to know what component to render */
  type: z.literal(BIQFormComponentType.AudioRecordingInput),

  /** the max duration of the audio recording in seconds. If not set, the recording will continue until the user stops the recording */
  maxDuration: z.number().optional(),
  /** the mime type of the audio recording (defaults to audio/webm) */
  mimeType: z.enum(BIQAudioMimeType).optional(),
});

export type BIQAudioRecordingSchema = z.infer<typeof BIQAudioRecordingZodSchema>;
```
