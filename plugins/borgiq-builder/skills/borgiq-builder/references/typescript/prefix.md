# prefix

Generated from the platform's runtime types. Do not edit.

Id prefixes per object type: the first four characters of every id.

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
  Recipe = 'RCPE',
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
