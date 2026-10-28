#!/usr/bin/env bash
# mica lane board [--force] [--check [file]] [--json] [--more]
# Compiled lane board (lb02): one parser, two modes — no standalone linter.
#
# Output contract:
#   default : brief report of the compile (≤10 lines)
#   --force : compile even when nothing changed
#   --check : per-file conformance table; non-zero exit if any file gaps
#   --check <file> : single-file conformance
#   --more  : print the compiled board (~/memory/lanes/_lanes.md)
#   --json  : machine-readable compile stats
set -uo pipefail

BIN="$HOME/workspace/bin/lane-board-compile"
OUT="$HOME/memory/lanes/_lanes.md"

CHECK=0; FORCE=0; CHECKFILE=""; JSON=0; MORE=0
ARGS=()
for a in "$@"; do
  case "$a" in
    --check) CHECK=1 ;;
    --force) FORCE=1 ;;
    --json) JSON=1 ;;
    --more) MORE=1 ;;
    *) ARGS+=("$a") ;;
  esac
done
[[ ${#ARGS[@]} -gt 0 ]] && CHECKFILE="${ARGS[0]}"

if [[ $CHECK -eq 1 ]]; then
  exec "$BIN" --check $CHECKFILE
fi

flags=()
[[ $FORCE -eq 1 ]] && flags+=(--force)
result="$("$BIN" "${flags[@]}" 2>&1)" || { echo "$result"; exit 1; }

if [[ $JSON -eq 1 ]]; then
  n=$(grep -c '^- \[' "$OUT" 2>/dev/null || echo 0)
  gaps=$(grep -c 'GAP —' "$OUT" 2>/dev/null || echo 0)
  printf '{"out":"%s","items":%d,"gap_rows":%d}\n' "$OUT" "$n" "$gaps"
  exit 0
fi
if [[ $MORE -eq 1 ]]; then
  exec cat "$OUT"
fi
# brief report: header lines of the compiled board
head -6 "$OUT"
