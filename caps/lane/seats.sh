#!/usr/bin/env bash
# mica lane seats — seat-registry audit: live chat titles vs Curtis's
# naming convention (dev-desk packet 0010). Proposes only — it never
# renames, archives, or pins.
#
# Usage:
#   mica lane seats [--more] [--json] [--out <file>]
#   mica lane seats --chats <snapshot.json> [--index <file>]
#
# Reads ~/memory/lanes/INDEX.md + LANE_MEMORY frontmatter + a live
# chat-list snapshot (default ~/workspace/data/seat-registry/
# chats.json — refresh it from the live chat list before a run).
# Implementation: ~/workspace/bin/seat-audit (its --help teaches).
set -uo pipefail

BIN="$HOME/workspace/bin/seat-audit"

for a in "$@"; do
  case "$a" in
    --help|-h) sed -n '2,13p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
  esac
done

exec python3 "$BIN" "$@"
