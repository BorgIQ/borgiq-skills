# connection

Generated from the platform's runtime types. Do not edit.

The authentication types for connections.

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
