#!/usr/bin/env bash
# mica lane needs — the project-needs board surface (packet 0020, Front
# Desk item 0004's build leg). Use when: you need each project's needs
# state — its one designated charter index resolved against the records
# of record, with work states only where checker records establish
# them — compiled from the memory repo at HEAD.
#
#   needs            brief: coverage, counts, findings summary (default)
#   needs --more     the whole needs board (memory/board/NEEDS.md)
#   needs --check    the findings audit over HEAD (exit 1 on findings)
#   needs --write    ONE writer pass for BOTH boards (the sibling
#                    board + the needs board, one lock, one commit)
#
# The compiler is caps/lane/needs-compiler.py (stdlib python3), a
# sibling leg on caps/lane/board-compiler.py's machinery (its
# primitives are imported by file path, never edited). The needs
# board lives in the memory repo at memory/board/NEEDS.md beside its
# state ledger (needs-ledger.jsonl); the writer commits both board
# pairs there, never pushes (the sweep pushes). The charter declares;
# other records prove — a row's work state exists only with the
# checker citation that establishes it.
set -euo pipefail
source "$HOME/workspace/caps/_shared/output.sh"
eval "$(mica_parse_output_flags "$@")"
set -- ${MICA_REMAINING[@]+"${MICA_REMAINING[@]}"}
COMPILER="$HOME/workspace/caps/lane/needs-compiler.py"
NEEDS_FILE="$HOME/memory/board/NEEDS.md"

usage() {
  sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

case "${1:-}" in
  -h|--help)
    usage ;;
  --write)
    exec python3 "$COMPILER" --write ;;
  --check)
    shift || true
    if [[ "${1:-}" == "--json" ]]; then
      exec python3 "$COMPILER" --check --json
    fi
    exec python3 "$COMPILER" --check ;;
  "")
    if [[ "${MICA_MORE:-0}" == "1" ]]; then
      if [[ -f "$NEEDS_FILE" ]]; then
        cat "$NEEDS_FILE"
      else
        python3 "$COMPILER" --render
      fi
    elif [[ -f "$NEEDS_FILE" ]]; then
      # brief: the compiled board's own head — claim, coverage,
      # stamp — plus the drill-down hint. Instant (no re-render).
      head -8 "$NEEDS_FILE"
      echo "… (mica lane needs --more for the whole board · --check for the findings audit)"
    else
      python3 "$COMPILER" --render | head -8
      echo "… (no needs board at HEAD yet — the first --write lands it; --more renders full)"
    fi ;;
  --json)
    python3 "$COMPILER" --render --json ;;
  *)
    echo "unknown flag: $1 (try: mica lane needs --help)" >&2
    exit 2 ;;
esac
