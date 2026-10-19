#!/usr/bin/env bash
# mica taps [--json]
# Unified pending-decision view: walks every parent LANES.md under
# ~/workspace/flows, collects non-empty "Human taps" cells, renders one list.
# A tap clears when the lead resolves it in LANES.md (tap cell emptied, decision
# logged) — so this output is always the live outstanding set.
set -uo pipefail
source ~/workspace/caps/_shared/output.sh
eval "$(mica_parse_output_flags "$@")"

JSON=0
for a in "${MICA_REMAINING[@]}"; do
  [[ "$a" == "--json" ]] && JSON=1
done

FLOWS_DIR="${FLOWS_DIR:-$HOME/workspace/flows}"
taps=()
while IFS= read -r lanes_file; do
  parent="$(basename "$(dirname "$lanes_file")")"
  while IFS= read -r line; do
    [[ "$line" =~ ^\| ]] || continue
    [[ "$line" =~ ^\|[[:space:]]*- ]] && continue
    [[ "$line" =~ Lane ]] && continue
    IFS='|' read -ra cols <<< "$line"
    trim() { printf '%s' "$1" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'; }
    lane="$(trim "${cols[1]:-}")"; tap="$(trim "${cols[6]:-}")"
    [[ -z "$lane" || -z "$tap" || "$tap" == "—" ]] && continue
    [[ "$tap" == *"<"* ]] && continue   # template placeholder, not a real tap
    taps+=("$parent · $lane — $tap")
  done < "$lanes_file"
done < <(find "$FLOWS_DIR" -maxdepth 3 -name LANES.md 2>/dev/null | sort)

if [[ $JSON -eq 1 ]]; then
  printf '['; first=1
  for t in "${taps[@]}"; do
    [[ $first -eq 0 ]] && printf ','
    printf '%s' "$t" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()),end="")'
    first=0
  done
  printf ']\n'
else
  if [[ ${#taps[@]} -eq 0 ]]; then
    echo "no pending taps"
  else
    printf '%s\n' "${taps[@]}" | mica_truncate
  fi
fi
