#!/usr/bin/env bash
# mica lane routes — declarative routing map for lanes + jobs
#
# Usage:
#   mica lane routes show [--more] [--json]
#   mica lane routes check [--json]
#   mica lane routes set <lane> <field> <value>
#   mica lane routes set <lane> job <job-id> delivers_to <dest> [protocol <p>]
#   mica lane routes applied <job-id>
#
# Declarations live in LANE_MEMORY frontmatter `routes:` blocks; the cap
# compiles them against the cron machinery, diffs for drift, and writes
# declaration changes (job applies go through an agent + `applied` verify).
# Spec: ~/workspace/docs/lane-routes-spec-2026-11-03.md
set -uo pipefail

BIN="$HOME/workspace/bin/lane-routes"

for a in "$@"; do
  case "$a" in
    --help|-h) sed -n '2,15p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
  esac
done

exec python3 "$BIN" "$@"
