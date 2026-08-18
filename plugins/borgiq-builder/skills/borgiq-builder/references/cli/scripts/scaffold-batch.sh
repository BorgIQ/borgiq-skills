#!/usr/bin/env bash
set -euo pipefail

# scaffold-batch.sh — Generate a batch operations JSON file in ActorOperation format
# for use with: borgiq canvas-actors batch <canvasSlugOrId> --file <output> --json
#
# Configuration fields use YAML strings within JSON (CanvasActorSchema format).
#
# Usage:
#   ./scaffold-batch.sh --add "HttpRequestActor:Fetch Data"
#   ./scaffold-batch.sh --add "DenoActor:Process" --add "HttpRequestActor:Send"
#   ./scaffold-batch.sh --update "ACTR01existing:name=New Name"
#   ./scaffold-batch.sh --remove "ACTR01existing"
#   ./scaffold-batch.sh --add "HttpRequestActor:Fetch" --remove "ACTR01old" --output batch.json

OUTPUT=""
declare -a ADDS=()
declare -a UPDATES=()
declare -a REMOVES=()

usage() {
  echo "Usage: $0 [operations...] [--output <path>]"
  echo ""
  echo "Operations:"
  echo "  --add <Type:Name>              Add a new actor (e.g., 'HttpRequestActor:Fetch Data')"
  echo "  --update <ActorId:field=value>  Update an existing actor (e.g., 'ACTR01...:name=New Name')"
  echo "  --remove <ActorId>             Remove an actor by ID"
  echo "  --output <path>                Output file path (default: stdout)"
  exit 1
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --add) ADDS+=("$2"); shift 2 ;;
    --update) UPDATES+=("$2"); shift 2 ;;
    --remove) REMOVES+=("$2"); shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

if [[ ${#ADDS[@]} -eq 0 && ${#UPDATES[@]} -eq 0 && ${#REMOVES[@]} -eq 0 ]]; then
  echo "Error: At least one operation (--add, --update, --remove) is required" >&2
  usage
fi

gen_id() {
  borgiq generate id "$1" 2>/dev/null
}

gen_msgvar() {
  borgiq generate msgvar "$1" 2>/dev/null
}

timestamp=$(date +%s)000
operations=""

# Process --add operations
for add_spec in "${ADDS[@]}"; do
  IFS=':' read -r actor_type actor_name <<< "$add_spec"
  actor_id=$(gen_id actor)
  msgvar=$(gen_msgvar "$actor_name")

  # Default options based on type
  case "$actor_type" in
    HttpRequestActor) options_yaml="method: GET\nurl: https://example.com" ;;
    DenoActor) options_yaml="" ;;
    *) options_yaml="" ;;
  esac

  if [[ -n "$operations" ]]; then operations="$operations,"; fi
  operations="$operations
    {
      \"type\": \"add\",
      \"actorId\": \"$actor_id\",
      \"data\": {
        \"type\": \"$actor_type\",
        \"version\": 1,
        \"name\": \"$actor_name\",
        \"msgVar\": \"$msgvar\",
        \"description\": \"\",
        \"isActive\": true,
        \"continueOnError\": false,
        \"enableLTM\": false,
        \"enableSTM\": false,
        \"sourcePorts\": [{ \"id\": \"SPRTdefault\" }],
        \"configuration\": {
          \"options\": \"$options_yaml\"
        },
        \"schemas\": {},
        \"position\": { \"x\": 0, \"y\": 0 },
        \"edges\": {}
      },
      \"timestamp\": $timestamp
    }"
  timestamp=$((timestamp + 1))
  echo "Add: $actor_type '$actor_name' -> $actor_id" >&2
done

# Process --update operations
for update_spec in "${UPDATES[@]}"; do
  IFS=':' read -r actor_id field_value <<< "$update_spec"
  IFS='=' read -r field value <<< "$field_value"

  if [[ -n "$operations" ]]; then operations="$operations,"; fi
  operations="$operations
    {
      \"type\": \"update\",
      \"actorId\": \"$actor_id\",
      \"data\": {
        \"$field\": \"$value\"
      },
      \"editVersion\": 1,
      \"timestamp\": $timestamp
    }"
  timestamp=$((timestamp + 1))
  echo "Update: $actor_id ($field=$value)" >&2
done

# Process --remove operations
for actor_id in "${REMOVES[@]}"; do
  if [[ -n "$operations" ]]; then operations="$operations,"; fi
  operations="$operations
    {
      \"type\": \"remove\",
      \"actorId\": \"$actor_id\",
      \"editVersion\": 1,
      \"timestamp\": $timestamp
    }"
  timestamp=$((timestamp + 1))
  echo "Remove: $actor_id" >&2
done

result=$(cat <<ENDJSON
{
  "operations": [$operations
  ]
}
ENDJSON
)

if [[ -n "$OUTPUT" ]]; then
  echo "$result" > "$OUTPUT"
  echo "Batch JSON written to $OUTPUT" >&2
else
  echo "$result"
fi
