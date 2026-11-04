#!/usr/bin/env bash
# board-ping-watch — poll the rolling board's ping ledger at HEAD;
# wake the ping courier when the ledger carries pings not yet
# delivered. The ledger is the condition source (packet 0017, gate
# ruling Q-5: the hook-on-the-ledger carrier). Source of record:
# ~/workspace/caps/lane/board-ping-watch.sh — this installed copy is
# byte-identical; edit the source, re-install in the same act.
#
# Delivery bookkeeping: ~/hooks/state/board-ping-watch.delivered
# holds one flip_id per line, appended BY THE COURIER after each
# successful relay. A ping whose flip_id never lands there re-fires
# on a later poll (at-least-once; every ping text carries its flip
# identity, so a duplicate is self-identifying). State (the pending
# payload) is written BEFORE the wake call — wake() is terminal, so
# the order is load-bearing (the dev-desk-watch pattern).
set -euo pipefail
[ -f "${HATCH_HOOK_RUNTIME:-}" ] && . "$HATCH_HOOK_RUNTIME" || true

REPO="$HOME"
STATE_DIR="$HOME/hooks/state"
DELIVERED="$STATE_DIR/board-ping-watch.delivered"
PENDING="$STATE_DIR/board-ping-watch.pending.json"
mkdir -p "$STATE_DIR"
touch "$DELIVERED"

LEDGER="$(git -C "$REPO" show HEAD:memory/board/ping-ledger.jsonl 2>/dev/null || true)"
if [[ -z "$LEDGER" ]]; then
  silent "no ping ledger at HEAD yet" '{}'
  exit 0
fi

DELIVERED_JSON="$(jq -R -s 'split("\n") | map(select(length > 0))' "$DELIVERED")"
PAYLOAD="$(printf '%s' "$LEDGER" | jq -c -s --argjson del "$DELIVERED_JSON" '
  {pings: [ .[]
    | select(.kind == "ping")
    | select(.assignee.chat_id != null)
    | select(.flip_id as $f | ($del | index($f) | not))
    | {flip_id: .flip_id, chat_id: .assignee.chat_id,
       slug: .assignee.slug, ping_text: .ping_text} ]}')"
COUNT="$(printf '%s' "$PAYLOAD" | jq '.pings | length')"

if [[ "${HATCH_HOOK_DRY_RUN:-0}" == "1" ]]; then
  log "dry-run probe" "{\"undelivered\": $COUNT}"
  silent "dry-run: $COUNT undelivered ping(s) would wake" '{}'
  exit 0
fi

if [[ "$COUNT" == "0" ]]; then
  silent "no undelivered pings" '{}'
  exit 0
fi

printf '%s' "$PAYLOAD" > "$PENDING"
log "undelivered pings" "{\"count\": $COUNT}"
wake "$COUNT undelivered board ping(s)" "$PAYLOAD"
