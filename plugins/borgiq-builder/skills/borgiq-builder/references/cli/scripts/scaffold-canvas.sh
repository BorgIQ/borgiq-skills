#!/usr/bin/env bash
set -euo pipefail

# scaffold-canvas.sh — Generate a canvas JSON file in ExportedCanvasData format
# for use with: borgiq canvases create-with-data --file <output> --json
#
# Usage:
#   ./scaffold-canvas.sh --name "My Flow" --slug my-flow
#   ./scaffold-canvas.sh --name "My Flow" --slug my-flow --template button-http
#   ./scaffold-canvas.sh --name "My Flow" --slug my-flow --template webhook-router
#   ./scaffold-canvas.sh --name "My Flow" --slug my-flow --template button-deno
#   ./scaffold-canvas.sh --name "My Flow" --slug my-flow --output outputs/my-flow.json

# Defaults
NAME=""
SLUG=""
DESCRIPTION=""
TEMPLATE="button-http"
OUTPUT=""
TTL=7

usage() {
  echo "Usage: $0 --name <name> --slug <slug> [options]"
  echo ""
  echo "Options:"
  echo "  --name <name>          Canvas name (required)"
  echo "  --slug <slug>          Canvas slug (required, lowercase-hyphenated)"
  echo "  --description <desc>   Canvas description (optional)"
  echo "  --template <template>  Template: button-http, webhook-router, button-deno (default: button-http)"
  echo "  --ttl <days>           Message TTL in days, 1-14 (default: 7)"
  echo "  --output <path>        Output file path (default: stdout)"
  exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --name) NAME="$2"; shift 2 ;;
    --slug) SLUG="$2"; shift 2 ;;
    --description) DESCRIPTION="$2"; shift 2 ;;
    --template) TEMPLATE="$2"; shift 2 ;;
    --ttl) TTL="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

if [[ -z "$NAME" || -z "$SLUG" ]]; then
  echo "Error: --name and --slug are required" >&2
  usage
fi

# Generate IDs and msgVars via the verified BorgIQ CLI (borgiq generate)
gen_id() {
  borgiq generate id "$1" 2>/dev/null
}

gen_msgvar() {
  borgiq generate msgvar "$1" 2>/dev/null
}

# Generate the canvas JSON based on template
generate_button_http() {
  local trigger_id edge_id http_id trigger_var http_var
  trigger_id=$(gen_id actor)
  http_id=$(gen_id actor)
  edge_id=$(gen_id edge)
  trigger_var=$(gen_msgvar "Manual Trigger")
  http_var=$(gen_msgvar "HTTP Request")

  cat <<ENDJSON
{
  "name": "$NAME",
  "slug": "$SLUG",
  "description": "$DESCRIPTION",
  "messageTTLInDays": $TTL,
  "runtimeSlug": "",
  "data": {
    "schemaVersion": "1",
    "actors": {
      "$trigger_id": {
        "id": "$trigger_id",
        "type": "ButtonTriggerActor",
        "version": 1,
        "name": "Manual Trigger",
        "msgVar": "$trigger_var",
        "description": "Click to start the flow",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }],
        "configuration": { "options": {} },
        "schemas": {},
        "position": { "x": 0, "y": 0 },
        "edges": {
          "$edge_id": {
            "id": "$edge_id",
            "sourceActorId": "$trigger_id",
            "sourcePortId": "SPRTdefault",
            "targetActorId": "$http_id",
            "targetPortId": "TPRTdefault",
            "type": "borgiqEdge"
          }
        }
      },
      "$http_id": {
        "id": "$http_id",
        "type": "HttpRequestActor",
        "version": 1,
        "name": "HTTP Request",
        "msgVar": "$http_var",
        "description": "Makes an HTTP request",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }],
        "configuration": {
          "options": {
            "method": "GET",
            "url": "https://example.com"
          },
          "outputs": "\${{ results.body }}"
        },
        "schemas": {},
        "position": { "x": 0, "y": 200 },
        "edges": {}
      }
    }
  }
}
ENDJSON
}

generate_webhook_router() {
  local trigger_id router_id resp_a_id resp_b_id trigger_var router_var resp_a_var resp_b_var
  local edge1 edge2 edge3 port_a webhook_key
  trigger_id=$(gen_id actor)
  router_id=$(gen_id actor)
  resp_a_id=$(gen_id actor)
  resp_b_id=$(gen_id actor)
  edge1=$(gen_id edge)
  edge2=$(gen_id edge)
  edge3=$(gen_id edge)
  port_a=$(gen_id sourceport)
  webhook_key=$(gen_id webhooktriggerkey)
  trigger_var=$(gen_msgvar "Webhook Trigger")
  router_var=$(gen_msgvar "Router")
  resp_a_var=$(gen_msgvar "Success Response")
  resp_b_var=$(gen_msgvar "Error Response")

  cat <<ENDJSON
{
  "name": "$NAME",
  "slug": "$SLUG",
  "description": "$DESCRIPTION",
  "messageTTLInDays": $TTL,
  "runtimeSlug": "",
  "data": {
    "schemaVersion": "1",
    "actors": {
      "$trigger_id": {
        "id": "$trigger_id",
        "type": "WebhookTriggerActor",
        "version": 1,
        "name": "Webhook Trigger",
        "msgVar": "$trigger_var",
        "description": "Receives incoming webhook requests",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }],
        "configuration": {
          "webhookTriggerKey": "$webhook_key",
          "options": {
            "allowedMethods": ["post"],
            "respondImmediately": false,
            "emitRawBody": false
          }
        },
        "schemas": {},
        "position": { "x": 0, "y": 0 },
        "edges": {
          "$edge1": {
            "id": "$edge1",
            "sourceActorId": "$trigger_id",
            "sourcePortId": "SPRTdefault",
            "targetActorId": "$router_id",
            "targetPortId": "TPRTdefault",
            "type": "borgiqEdge"
          }
        }
      },
      "$router_id": {
        "id": "$router_id",
        "type": "RouterActor",
        "version": 1,
        "name": "Router",
        "msgVar": "$router_var",
        "description": "Routes by condition",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [
          { "id": "$port_a", "name": "Success" },
          { "id": "SPRTdefault", "name": "F" }
        ],
        "configuration": {
          "options": {
            "emitType": "singleRoute",
            "conditions": {
              "Success": "\${{ msg.$trigger_var.body?.status === 'ok' }}"
            }
          }
        },
        "schemas": {},
        "position": { "x": 0, "y": 200 },
        "edges": {
          "$edge2": {
            "id": "$edge2",
            "sourceActorId": "$router_id",
            "sourcePortId": "$port_a",
            "targetActorId": "$resp_a_id",
            "targetPortId": "TPRTdefault",
            "type": "borgiqEdge"
          },
          "$edge3": {
            "id": "$edge3",
            "sourceActorId": "$router_id",
            "sourcePortId": "SPRTdefault",
            "targetActorId": "$resp_b_id",
            "targetPortId": "TPRTdefault",
            "type": "borgiqEdge"
          }
        }
      },
      "$resp_a_id": {
        "id": "$resp_a_id",
        "type": "WebhookResponseActor",
        "version": 1,
        "name": "Success Response",
        "msgVar": "$resp_a_var",
        "description": "Returns 200 OK",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }],
        "configuration": {
          "options": {
            "statusCode": 200,
            "body": { "success": true, "message": "OK" },
            "headers": { "content-type": "application/json" }
          }
        },
        "schemas": {},
        "position": { "x": -300, "y": 400 },
        "edges": {}
      },
      "$resp_b_id": {
        "id": "$resp_b_id",
        "type": "WebhookResponseActor",
        "version": 1,
        "name": "Error Response",
        "msgVar": "$resp_b_var",
        "description": "Returns 400 Bad Request",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }],
        "configuration": {
          "options": {
            "statusCode": 400,
            "body": { "success": false, "message": "Bad request" },
            "headers": { "content-type": "application/json" }
          }
        },
        "schemas": {},
        "position": { "x": 300, "y": 400 },
        "edges": {}
      }
    }
  }
}
ENDJSON
}

generate_button_deno() {
  local trigger_id edge_id deno_id trigger_var deno_var
  trigger_id=$(gen_id actor)
  deno_id=$(gen_id actor)
  edge_id=$(gen_id edge)
  trigger_var=$(gen_msgvar "Manual Trigger")
  deno_var=$(gen_msgvar "Process Data")

  cat <<ENDJSON
{
  "name": "$NAME",
  "slug": "$SLUG",
  "description": "$DESCRIPTION",
  "messageTTLInDays": $TTL,
  "runtimeSlug": "",
  "data": {
    "schemaVersion": "1",
    "actors": {
      "$trigger_id": {
        "id": "$trigger_id",
        "type": "ButtonTriggerActor",
        "version": 1,
        "name": "Manual Trigger",
        "msgVar": "$trigger_var",
        "description": "Click to start the flow",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }],
        "configuration": { "options": {} },
        "schemas": {},
        "position": { "x": 0, "y": 0 },
        "edges": {
          "$edge_id": {
            "id": "$edge_id",
            "sourceActorId": "$trigger_id",
            "sourcePortId": "SPRTdefault",
            "targetActorId": "$deno_id",
            "targetPortId": "TPRTdefault",
            "type": "borgiqEdge"
          }
        }
      },
      "$deno_id": {
        "id": "$deno_id",
        "type": "DenoActor",
        "version": 1,
        "name": "Process Data",
        "msgVar": "$deno_var",
        "description": "Custom TypeScript processing",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }],
        "configuration": {
          "options": {},
          "codeDir": [
            {
              "path": "main.ts",
              "content": "import type { Request, Response } from \"@borgiq/actors\";\n\nexport default async function receive(req: Request): Promise<Response> {\n  return {\n    results: {\n      processed: true,\n      result: req.inputs.message,\n      timestamp: new Date().toISOString(),\n    },\n  };\n}\n"
            }
          ],
          "inputs": {
            "message": "\${{ msg.$trigger_var.body }}"
          },
          "outputs": "\${{ results }}"
        },
        "schemas": {},
        "position": { "x": 0, "y": 200 },
        "edges": {}
      }
    }
  }
}
ENDJSON
}

# Generate based on template
result=""
case "$TEMPLATE" in
  button-http) result=$(generate_button_http) ;;
  webhook-router) result=$(generate_webhook_router) ;;
  button-deno) result=$(generate_button_deno) ;;
  *) echo "Error: Unknown template '$TEMPLATE'. Use: button-http, webhook-router, button-deno" >&2; exit 1 ;;
esac

# Output
if [[ -n "$OUTPUT" ]]; then
  echo "$result" > "$OUTPUT"
  echo "Canvas JSON written to $OUTPUT" >&2
else
  echo "$result"
fi
