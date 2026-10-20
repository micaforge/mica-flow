#!/usr/bin/env bash
# mica lane status --parent <flow-dir> [--json]
# Lane dashboard from files (no chat API in bash — chat reads are agent-side).
# Reads the parent LANES.md, checks each lane flow's _run/ for the latest
# summary, and renders one table: lane | state | last summary | blockers.
# LANES.md carries a chat_id column (backfilled at scaffold); the agent uses
# chat.read_messages per chat_id for verbatim last words when needed.
set -uo pipefail
source ~/workspace/caps/_shared/output.sh
eval "$(mica_parse_output_flags "$@")"

PARENT=""; JSON=0
for a in "${MICA_REMAINING[@]}"; do
  case "$a" in
    --parent) PARENT="NEXT";;
    --json) JSON=1;;
    *) if [[ "$PARENT" == "NEXT" ]]; then PARENT="$a";
       elif [[ -z "$PARENT" ]]; then PARENT="$a"; fi;;
  esac
done
[[ -z "$PARENT" ]] && { echo "usage: mica lane status --parent <flow-dir> [--json]" >&2; exit 1; }
[[ "$PARENT" != /* ]] && PARENT="$HOME/workspace/flows/$PARENT"
[[ -d "$PARENT" ]] || { echo "unknown parent: $PARENT" >&2; exit 1; }
LANES="$PARENT/LANES.md"
[[ -f "$LANES" ]] || { echo "no LANES.md in $PARENT" >&2; exit 1; }

# Parse the markdown table: | Lane | Flow | State | Owner | Blockers | Human taps | Chat |
lanes=()
while IFS= read -r line; do
  [[ "$line" =~ ^\| ]] || continue
  [[ "$line" =~ ^\|[[:space:]]*- ]] && continue
  [[ "$line" =~ Lane ]] && continue
  # split on |, trim
  IFS='|' read -ra cols <<< "$line"
  trim() { printf '%s' "$1" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'; }
  lane="$(trim "${cols[1]:-}")"; flow="$(trim "${cols[2]:-}")"
  state="$(trim "${cols[3]:-}")"; blockers="$(trim "${cols[5]:-}")"
  taps="$(trim "${cols[6]:-}")"; chat="$(trim "${cols[7]:-}")"
  [[ -z "$lane" ]] && continue
  lanes+=("$lane|$flow|$state|$blockers|$taps|$chat")
done < "$LANES"

out_lines=()
json_items=()
for entry in "${lanes[@]}"; do
  IFS='|' read -r lane flow state blockers taps chat <<< "$entry"
  flow="${flow//\`/}"
  [[ "$flow" != /* ]] && flow="$HOME/workspace/$flow"
  # latest summary.md under <flow>/*/_run/
  latest="$(find "$flow" -path "*/_run/summary.md" -type f 2>/dev/null | xargs ls -t 2>/dev/null | head -1)"
  if [[ -n "$latest" ]]; then
    age="$(stat -c %y "$latest" 2>/dev/null | cut -d. -f1)"
    headline="$(head -5 "$latest" 2>/dev/null | grep -m1 -E "^# " | sed 's/^# //')"
    summ="${age:-?} ${headline:-summary}"
  else
    summ="no summary yet"
  fi
  blocker_txt="$blockers"
  [[ "$taps" != "—" && -n "$taps" ]] && blocker_txt="${blocker_txt} [tap: $taps]"
  out_lines+=("$lane | $state | $summ | $blocker_txt")
  json_items+=("$(printf '{"lane":%s,"flow":%s,"state":%s,"last_summary":%s,"blockers":%s,"chat_id":%s}' \
    "$(printf '%s' "$lane" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')" \
    "$(printf '%s' "$flow" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')" \
    "$(printf '%s' "$state" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')" \
    "$(printf '%s' "$summ" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')" \
    "$(printf '%s' "$blocker_txt" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')" \
    "$(printf '%s' "$chat" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')")")
done

if [[ $JSON -eq 1 ]]; then
  printf '[%s]\n' "$(IFS=,; echo "${json_items[*]}")"
else
  printf '%s\n' "${out_lines[@]}" | mica_truncate
fi
