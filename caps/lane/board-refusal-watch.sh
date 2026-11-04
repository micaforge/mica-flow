#!/usr/bin/env bash
# board-refusal-watch — poll the rolling-board compiler's refusal
# alert (packet 0019); wake the lane's lead seat when a refused
# --write has left an alert nobody has woken for yet. The alert
# file is the condition source: ~/workspace/data/lane/
# board-alert.json, the sweep-alert.json shape the compiler
# mirrors from the memory-commit-sweep (whose own hook cats
# sweep-alert.json into its wake payload the same way). Source of
# record: ~/workspace/caps/lane/board-refusal-watch.sh — the
# installed copy at ~/hooks/scripts/ is byte-identical; edit the
# source, re-install in the same act.
#
# Wake bookkeeping: ~/hooks/state/board-refusal-watch.seen holds
# the sha256 of the alert content last woken for. A refused cron
# tick rewrites the alert (fresh ts), so each distinct refusal
# wakes exactly once and an unchanged alert stays silent. The
# seen key is written BEFORE the wake call — wake() is terminal,
# so the order is load-bearing (the board-ping-watch pattern).
# When the alert disappears (a clean compile unlinks it), the
# seen key is cleared so the next refusal wakes fresh.
set -euo pipefail
[ -f "${HATCH_HOOK_RUNTIME:-}" ] && . "$HATCH_HOOK_RUNTIME" || true

ALERT="$HOME/workspace/data/lane/board-alert.json"
STATE_DIR="$HOME/hooks/state"
SEEN="$STATE_DIR/board-refusal-watch.seen"
mkdir -p "$STATE_DIR"

if [[ ! -f "$ALERT" ]]; then
  if [[ "${HATCH_HOOK_DRY_RUN:-0}" != "1" && -f "$SEEN" ]]; then
    rm -f "$SEEN"
    log "refusal alert cleared (a clean compile landed)" '{}'
  fi
  silent "no board refusal alert" '{}'
  exit 0
fi

KEY="$(sha256sum "$ALERT" | cut -d' ' -f1)"
if [[ -f "$SEEN" && "$(cat "$SEEN")" == "$KEY" ]]; then
  silent "refusal alert unchanged since its wake" '{}'
  exit 0
fi

PAYLOAD="$(cat "$ALERT")"

if [[ "${HATCH_HOOK_DRY_RUN:-0}" == "1" ]]; then
  log "dry-run probe" '{"would_wake": true}'
  silent "dry-run: an unwoken refusal alert is present" '{}'
  exit 0
fi

printf '%s' "$KEY" > "$SEEN"
log "refusal alert" "$PAYLOAD"
wake "board-compiler: scan-guard refusal needs eyes" "$PAYLOAD"
