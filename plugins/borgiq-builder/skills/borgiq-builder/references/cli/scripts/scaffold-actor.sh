#!/usr/bin/env bash
set -euo pipefail

# scaffold-actor.sh — Generate a single actor JSON file in CanvasActor format
# for use with: borgiq canvas-actors create <canvasSlugOrId> <actorId> --file <output> --json
#
# Configuration fields are YAML strings within JSON (CanvasActorSchema format).
#
# Usage:
#   ./scaffold-actor.sh --type HttpRequestActor --name "Fetch Users"
#   ./scaffold-actor.sh --type DenoActor --name "Process Data"
#   ./scaffold-actor.sh --type RouterActor --name "Route by Status" --routes "Active,Inactive"
#   ./scaffold-actor.sh --type WebhookTriggerActor --name "Webhook"
#   ./scaffold-actor.sh --type HttpRequestActor --name "Fetch Users" --output actor.json

# Defaults
TYPE=""
NAME=""
ROUTES=""
OUTPUT=""

usage() {
  echo "Usage: $0 --type <ActorType> --name <name> [options]"
  echo ""
  echo "Options:"
  echo "  --type <type>        Actor type (required, e.g., HttpRequestActor, DenoActor)"
  echo "  --name <name>        Actor name (required)"
  echo "  --routes <routes>    Comma-separated route names for RouterActor/AiRouterActor"
  echo "  --output <path>      Output file path (default: stdout)"
  echo ""
  echo "Also prints the generated actor ID to stderr for use in CLI commands."
  exit 1
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --type) TYPE="$2"; shift 2 ;;
    --name) NAME="$2"; shift 2 ;;
    --routes) ROUTES="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

if [[ -z "$TYPE" || -z "$NAME" ]]; then
  echo "Error: --type and --name are required" >&2
  usage
fi

gen_id() {
  borgiq generate id "$1" 2>/dev/null
}

gen_msgvar() {
  borgiq generate msgvar "$1" 2>/dev/null
}

actor_id=$(gen_id actor)
msgvar=$(gen_msgvar "$NAME")

echo "Actor ID: $actor_id" >&2

# Build source ports
build_source_ports() {
  case "$TYPE" in
    RouterActor|AiRouterActor)
      local ports="["
      if [[ -n "$ROUTES" ]]; then
        IFS=',' read -ra route_names <<< "$ROUTES"
        for rname in "${route_names[@]}"; do
          local port_id
          port_id=$(gen_id sourceport)
          ports="$ports{ \"id\": \"$port_id\", \"name\": \"$rname\" }, "
        done
      fi
      ports="$ports{ \"id\": \"SPRTdefault\", \"name\": \"F\" }]"
      echo "$ports"
      ;;
    AgentHarnessActor|AiAgentActor)
      echo '[{ "id": "SPRTdone000", "name": "Done" }, { "id": "SPRTdefault", "name": "Status" }]'
      ;;
    InterfaceActor)
      echo '[{ "id": "SPRTevent00", "name": "Event" }, { "id": "SPRTdefault", "name": "Meta" }]'
      ;;
    AppTriggerActor|CommentActor)
      echo '[]'
      ;;
    *)
      echo '[{ "id": "SPRTdefault" }]'
      ;;
  esac
}

# Build configuration based on actor type
build_configuration() {
  case "$TYPE" in
    HttpRequestActor)
      echo '"options": "method: GET\nurl: https://example.com"'
      ;;
    # Code actors carry their source as configuration.codeDir: a JSON array of
    # {path, content} files (never a YAML string) whose entrypoint is main.ts /
    # main.py. Add further files to the array as the actor grows.
    DenoActor|DenoTestActor)
      echo '"options": "",
      "codeDir": [{ "path": "main.ts", "content": "import type { Request, Response } from \"@borgiq/actors\";\n\nexport default async function receive(req: Request): Promise<Response> {\n  return { results: req.inputs };\n}\n" }]'
      ;;
    UniversalTriggerActor)
      echo '"options": "",
      "codeDir": [{ "path": "main.ts", "content": "import type { TriggerRequest, Response } from \"@borgiq/actors\";\n\nexport default async function receive(req: TriggerRequest): Promise<Response> {\n  return { results: { firedBy: req.trigger.type } };\n}\n" }]'
      ;;
    PythonActor)
      echo '"options": "",
      "codeDir": [{ "path": "main.py", "content": "from borgiq import Request, Response\n\n\ndef receive(req: Request) -> Response:\n    return Response(results=req.inputs)\n" }]'
      ;;
    AiActor)
      echo '"options": "model: claude-sonnet-4-5-20250514\nmaxTokens: 4096\nsystemPrompt: You are a helpful assistant.\nprompt: ${{ inputs.prompt }}"'
      ;;
    AiAgentActor)
      echo '"options": "model: claude-sonnet-4-6\nsystemPrompt: You are a helpful agent.\nprompt: ${{ inputs.prompt }}"'
      ;;
    RouterActor)
      local conditions=""
      if [[ -n "$ROUTES" ]]; then
        IFS=',' read -ra route_names <<< "$ROUTES"
        conditions="emitType: singleRoute\nconditions:"
        for rname in "${route_names[@]}"; do
          conditions="$conditions\n  $rname: \${{ true }}"
        done
      else
        conditions="emitType: singleRoute\nconditions:\n  Match: \${{ true }}"
      fi
      echo "\"options\": \"$conditions\""
      ;;
    AiRouterActor)
      echo '"options": "model: claude-sonnet-4-5-20250514\nprompt: Route the message to the appropriate handler."'
      ;;
    WebhookTriggerActor)
      local wh_key
      wh_key=$(gen_id webhooktriggerkey)
      echo "\"webhookTriggerKey\": \"$wh_key\",
      \"options\": \"allowedMethods:\\n  - post\\nrespondImmediately: false\\nemitRawBody: false\""
      ;;
    ButtonTriggerActor|ScheduledTriggerActor|EmailTriggerActor|CallableTriggerActor|InterfaceTriggerActor)
      echo '"options": ""'
      ;;
    WebhookResponseActor)
      echo '"options": "statusCode: 200\nbody:\n  success: true\nheaders:\n  content-type: application/json"'
      ;;
    CallableResponseActor)
      echo '"options": ""'
      ;;
    SendEmailActor)
      echo '"options": "to: \"\"\nsubject: \"\"\nbody: \"\""'
      ;;
    DataStoreActor)
      echo '"options": "scope: canvas\naction: set\nkey: myKey\nvalue: myValue"'
      ;;
    CollectionActor)
      echo '"options": "action: putItem\ncollectionName: my-collection\nitem:\n  id: \${{ inputs.id }}\n  data: \${{ inputs.data }}"'
      ;;
    CallFlowActor)
      echo '"options": "canvasId: \"\"\nactorId: \"\""'
      ;;
    *)
      echo '"options": ""'
      ;;
  esac
}

source_ports=$(build_source_ports)
configuration=$(build_configuration)

result=$(cat <<ENDJSON
{
  "type": "$TYPE",
  "version": 1,
  "name": "$NAME",
  "msgVar": "$msgvar",
  "description": "",
  "isActive": true,
  "continueOnError": false,
  "enableLTM": false,
  "enableSTM": false,
  "sourcePorts": $source_ports,
  "configuration": {
    $configuration
  },
  "schemas": {},
  "position": { "x": 0, "y": 0 },
  "edges": {}
}
ENDJSON
)

if [[ -n "$OUTPUT" ]]; then
  echo "$result" > "$OUTPUT"
  echo "Actor JSON written to $OUTPUT" >&2
else
  echo "$result"
fi
