# Example: Output contract (token-efficient CLI design)

**When:** building any CLI tool or cap that could return large results.
**Source:** mica caps system (2026-10-16).

## The contract

1. Default to ≤10 lines of output. Never dump large lists.
2. Cache full findings (e.g. `~/.cache/mica/`). Report the cache path.
3. Support `--more` / `--all` for explicit full output, `--limit N` to adjust.
4. Truncated output ends with: `... (N more — use --more for full output)`

## The pattern

**Brief report → cache → drill down.** The tool covers large scope but only
surfaces what serves the user's intent. Token efficiency is the design goal,
not a nice-to-have.

Shared implementation lives in `caps/_shared/output.sh` — source it, parse
flags, pipe through the truncator. Enforce at the dispatcher level as a
backstop (e.g. 50-line hard cap), not just author discipline.
