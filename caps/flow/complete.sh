#!/usr/bin/env bash
# -- caps/flow/complete.sh --
# name: mica flow complete
# description: Cross-flow completion report — which flows finished, which stalled, progress %.
# Use when: Curtis asks "what's done, what's stuck" across all flows.
# Output contract: ≤10 lines default, --all for full, --json for machine mode.
set -uo pipefail
source ~/workspace/caps/_shared/output.sh

FLOWS_DIR="${FLOWS_DIR:-$HOME/workspace/flows}"
JSON=0; ALL=0
for a in "$@"; do case "$a" in --json) JSON=1;; --all|--more) ALL=1;; esac; done

tmp=$(mktemp); trap 'rm -f "$tmp"' EXIT

for flow_dir in "$FLOWS_DIR"/*/; do
  [ -d "$flow_dir" ] || continue
  flow=$(basename "$flow_dir")
  # find cycle dirs (aNN-*) one level deep, excluding a00-scaffold nesting
  cycles=$(find "$flow_dir" -maxdepth 2 -name "a[0-9][0-9]-*" -type d ! -name "a00-scaffold" | sort)
  [ -z "$cycles" ] && continue
  total=0; done_n=0; ready_n=0; gates_total=0; gates_pass=0
  pending_tasks=""
  while IFS= read -r cdir; do
    cyc=$(basename "$cdir"); total=$((total+1))
    st=$(grep -m1 "^status:" "$cdir/cycle.md" 2>/dev/null | awk '{print $2}')
    case "$st" in done) done_n=$((done_n+1));; ready) ready_n=$((ready_n+1));; esac
    # gates: count lines starting with | G or - [ ] patterns in cycle.md table
    g=$(grep -cE "^\| G[0-9]" "$cdir/cycle.md" 2>/dev/null || true)
    gates_total=$((gates_total + g))
    if [ "$st" = done ]; then gates_pass=$((gates_pass + g)); fi
    # remaining: next BRIEF TODOs in non-done cycles
    if [ "$st" != done ] && [ -f "$cdir/BRIEF.md" ]; then
      t=$(grep -c "TODO" "$cdir/BRIEF.md" 2>/dev/null || true)
      [ "$t" -gt 0 ] && pending_tasks="$pending_tasks $cyc:$t"
    fi
  done <<< "$cycles"
  pct=$(( total > 0 ? done_n * 100 / total : 0 ))
  verdict="incomplete"; [ "$pct" -eq 100 ] && verdict="complete"
  printf '%s\t%d\t%d\t%d\t%d\t%d\t%s\t%s\n' \
    "$flow" "$total" "$done_n" "$ready_n" "$pct" "$gates_total" "$verdict" "$pending_tasks" >> "$tmp"
done

if [ "$JSON" -eq 1 ]; then
  echo "["; first=1
  while IFS=$'\t' read -r flow total done_n ready_n pct gates verdict pending; do
    [ "$first" -eq 0 ] && echo ","
    printf '  {"flow":"%s","cycles":%d,"done":%d,"ready":%d,"pct":%d,"gates":%d,"verdict":"%s","pending":"%s"}' \
      "$flow" "$total" "$done_n" "$ready_n" "$pct" "$gates" "$verdict" "$pending"
    first=0
  done < "$tmp"; echo; echo "]"
  exit 0
fi

total_flows=$(wc -l < "$tmp")
complete_n=$(awk -F'\t' '$7=="complete"' "$tmp" | wc -l)
echo "flows: $total_flows ($complete_n complete, $((total_flows - complete_n)) in progress)"
echo "---"
shown=0
while IFS=$'\t' read -r flow total done_n ready_n pct gates verdict pending; do
  if [ "$verdict" = "complete" ]; then
    printf '✓ %s — %d/%d cycles, %d%%\n' "$flow" "$done_n" "$total" "$pct"
  else
    printf '○ %s — %d/%d cycles, %d%% (ready: %d)%s\n' "$flow" "$done_n" "$total" "$pct" "$ready_n" \
      "${pending:+ | pending TODOs:$pending}"
  fi
  shown=$((shown+1))
  [ "$ALL" -eq 0 ] && [ "$shown" -ge 10 ] && {
    rest=$((total_flows - shown))
    [ "$rest" -gt 0 ] && echo "… $rest more (use --all)"
    break
  }
done < <(sort -t$'\t' -k5 -n "$tmp")
exit 0
