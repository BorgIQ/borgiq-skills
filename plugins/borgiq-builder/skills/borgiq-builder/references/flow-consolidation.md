# Converting Flows to Single Actors

When a user asks to convert a flow (multiple connected actors) into a single actor, **always use DenoActor**. This consolidates multiple API calls and data transformations into one cohesive unit.

## Connection Handling

**Key rule:** An actor can have **only ONE connection**, but **multiple credentials**. This determines how to handle credentials when consolidating flows.

### Single Connection

If all actors in the flow use the same `connection`, use that connection in the DenoActor:

```yaml
configuration:
  options:
    code: |
      // Access connection via the connection object
      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${connection.auth.accessToken}` }
      });
  connection:
    key: my-google-connection
```

### Multiple Connections

If the flow uses multiple different connections, use `credentials` instead of `connection`. Map each connection as a credential with `source: connection`:

```yaml
configuration:
  options:
    code: |
      // Access connections via credentials
      const googleAuth = credentials['google-sheets-connection'].auth;
      const slackAuth = credentials['slack-connection'].auth;

      // Use each connection for its respective API
      const sheetsResponse = await fetch(sheetsUrl, {
        headers: { Authorization: `Bearer ${googleAuth.accessToken}` }
      });
      const slackResponse = await fetch(slackUrl, {
        headers: { Authorization: `Bearer ${slackAuth.accessToken}` }
      });
  credentials:
    google-sheets-connection:
      workspaceKey: my-google-sheets-connection
      source: connection
    slack-connection:
      workspaceKey: my-slack-connection
      source: connection
```

**Key points:**
- `workspaceKey` is the connection key configured in the workspace
- `source: connection` tells BorgIQ to treat this credential as a connection object
- Access credentials via `credentials['key-name'].auth`

## When to Consolidate

| Scenario | Consolidate? |
|----------|--------------|
| Multiple sequential API calls with data dependencies | Yes |
| Simple linear flow with independent actors | Optional |
| Flow with branching/routing logic | No - keep separate actors |
| Flow with AI actors needing different models | Case-by-case |
| User explicitly requests consolidation | Yes |
