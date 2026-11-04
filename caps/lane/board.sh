#!/usr/bin/env bash
# mica lane board — the rolling board surface (packet 0017, Q-1 landing).
# Use when: you need the lanes' live queue state — who holds what, what is
# blocked on whom, which queues disagree with their cited records (C7) or
# have gone quiet (C2) — compiled from the memory repo at HEAD.
#
#   board            brief: stamp, counts, coverage summary     (default)
#   board --more     the whole board (memory/board/BOARD.md, read back)
#   board --check    the C7 pair + C2 audit over HEAD (exit 1 if any pair)
#   board --write    one compiler pass (single writer; the cron's act)
#   board --force    legacy alias for --write (lb02 compatibility)
#
# The compiler is caps/lane/board-compiler.py (stdlib python3). The board
# itself lives in the memory repo at memory/board/BOARD.md beside its ping
# ledger; the compiler commits it there, never pushes (the sweep pushes).
# The lb02 predecessor (bin/lane-board-compile → memory/lanes/_lanes.md)
# is archived at caps/lane/archive/ with a pointer stub at the bin path.
set -euo pipefail
source "$HOME/workspace/caps/_shared/output.sh"
eval "$(mica_parse_output_flags "$@")"
set -- ${MICA_REMAINING[@]+"${MICA_REMAINING[@]}"}
COMPILER="$HOME/workspace/caps/lane/board-compiler.py"
BOARD_FILE="$HOME/memory/board/BOARD.md"

usage() {
  sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

case "${1:-}" in
  -h|--help)
    usage ;;
  --write|--force)
    exec python3 "$COMPILER" --write ;;
  --check)
    shift || true
    if [[ "${1:-}" == "--json" ]]; then
      exec python3 "$COMPILER" --check --json
    fi
    exec python3 "$COMPILER" --check ;;
  "")
    if [[ "${MICA_MORE:-0}" == "1" ]]; then
      if [[ -f "$BOARD_FILE" ]]; then
        cat "$BOARD_FILE"
      else
        python3 "$COMPILER" --render
      fi
    elif [[ -f "$BOARD_FILE" ]]; then
      # brief: the compiled board's own head — claim, coverage, stamp,
      # flip:close — plus the drill-down hint. Instant (no re-render).
      head -8 "$BOARD_FILE"
      echo "… (mica lane board --more for the whole board · --check for the C7/C2 audit)"
    else
      python3 "$COMPILER" --render | head -8
      echo "… (no board at HEAD yet — the cron's first pass lands it; --more renders full)"
    fi ;;
  --json)
    python3 "$COMPILER" --render --json ;;
  *)
    echo "unknown flag: $1 (try: mica lane board --help)" >&2
    exit 2 ;;
esac
