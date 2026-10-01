# actorSchemas/trigger/permissionsPolicy

Generated from the platform's runtime types. Do not edit.

Valid Permissions-Policy directives that can be enabled for iframes.

## actorSchemas/trigger/permissionsPolicy

**Source:** `actorSchemas/trigger/permissionsPolicy.ts`

```typescript
import { z } from 'zod';

/**
 * Valid Permissions-Policy directives that can be enabled for iframes.
 * These control access to browser APIs and features.
 * @see https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy
 */
export enum PermissionsPolicyDirective {
  /** Access to the Accelerometer interface */
  Accelerometer = 'accelerometer',
  /** Access to the AmbientLightSensor interface */
  AmbientLightSensor = 'ambient-light-sensor',
  /** Autoplay of media requested through HTMLMediaElement */
  Autoplay = 'autoplay',
  /** Access to the BatteryManager interface */
  Battery = 'battery',
  /** Access to video input devices */
  Camera = 'camera',
  /** Access to read clipboard contents via Clipboard API */
  ClipboardRead = 'clipboard-read',
  /** Access to write to clipboard via Clipboard API */
  ClipboardWrite = 'clipboard-write',
  /** Access to use the Screen Capture API (getDisplayMedia) */
  DisplayCapture = 'display-capture',
  /** Access to the Encrypted Media Extensions API */
  EncryptedMedia = 'encrypted-media',
  /** Access to the Fullscreen API */
  Fullscreen = 'fullscreen',
  /** Access to the Geolocation API */
  Geolocation = 'geolocation',
  /** Access to the Gyroscope interface */
  Gyroscope = 'gyroscope',
  /** Access to the Magnetometer interface */
  Magnetometer = 'magnetometer',
  /** Access to audio input devices */
  Microphone = 'microphone',
  /** Access to the Web MIDI API */
  Midi = 'midi',
  /** Access to the Payment Request API */
  Payment = 'payment',
  /** Access to the Picture-in-Picture API */
  PictureInPicture = 'picture-in-picture',
  /** Access to the Web Authentication API */
  PublicKeyCredentialsGet = 'publickey-credentials-get',
  /** Access to the Screen Wake Lock API */
  ScreenWakeLock = 'screen-wake-lock',
  /** Access to the WebUSB API */
  Usb = 'usb',
  /** Access to the Web Share API */
  WebShare = 'web-share',
  /** Access to WebXR Device API */
  XrSpatialTracking = 'xr-spatial-tracking',
}

/** Zod schema for PermissionsPolicyDirective enum */
export const PermissionsPolicyDirectiveZodSchema = z.nativeEnum(PermissionsPolicyDirective);
```
