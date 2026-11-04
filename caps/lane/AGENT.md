# lane caps — agent notes

## board (added 2026-11-04)

`mica lane board` (board.sh → `board-compiler.py`, this directory): the
rolling board compiler, dev-desk packet 0017 (Front Desk item 0002's
build leg). Compiles the lanes' LANE_MEMORY queue state from the memory
repo at HEAD into `memory/board/BOARD.md` + `ping-ledger.jsonl` (in the
repo; the compiler commits them, never pushes — the sweep pushes).
Modes: brief (default) · `--more` the board · `--check` the C7/C2 audit
(exit 1 on any C7 pair) · `--write`/`--force` one compiler pass.
Cadence: cron `board-compile` (30m, :07/:37) · ping carrier: hook
`board-ping-watch` (script source of record `board-ping-watch.sh` here;
tests in `tests/`). It supersedes lb02: `bin/lane-board-compile` is a
pointer stub, the original + old board.sh are in `archive/`, and
`memory/lanes/_lanes.md` is a worktree pointer. Build record: the
packet's BUILD.md (`~/skills/dev-desk/completed/0017-rolling-board-compiler/`).

Scan guard (packets 0018/0019): `--write` runs the sweep's own
secret-scan patterns (imported live from `bin/memory-commit-sweep`,
never copied) over the composed board + ledger before the commit and
fails closed. A refused write leaves the sweep-alert shape at
`~/workspace/data/lane/board-alert.json` (hit: file + pattern class ·
load failure: the cause · the value never persisted; unlinked by the
next clean compile). Refusal reader: hook `board-refusal-watch`
(script source of record `board-refusal-watch.sh` here, 300s poll,
wakes the DevOps Lead seat once per distinct alert). Build records:
the packets' BUILD.md (`~/skills/dev-desk/completed/0018-board-scan-guard/`
· `~/skills/dev-desk/in-progress/0019-board-refusal-alert/`).

## needs (added 2026-11-04)

`mica lane needs` (needs.sh → `needs-compiler.py`, this directory): the
project-needs board compiler, dev-desk packet 0020 (Front Desk item
0004's build leg). Compiles each project's ONE designated charter
needs-index (the estate-template fold, gate conditions C1–C7) from the
memory repo at HEAD into `memory/board/NEEDS.md` + `needs-ledger.jsonl`:
rows resolve against their records of record; work states (pending ·
claimed · checked · verified · graded) project ONLY from checker
records carrying the STATE-line binding (`needs: <item-id> = <state>`,
bound by home or charter citation); pointers into excluded homes
render pointer-withheld, byte-level. It imports board-compiler.py's
primitives by file path and never edits them; `--write` is ONE writer
pass carrying BOTH boards under the sibling's flock in a single
commit (scan guard + refusal alert shared with 0018/0019). Modes:
brief (default) · `--more` the board · `--check` the findings audit
(exit 1 on findings; unknowns never fail) · `--write` one joint pass.
Tests: `tests/needs_battery.py` + `tests/needs_fixture.py` (30/30,
 incl. the two break variants). Build record: the packet
(`~/skills/dev-desk/in-progress/0020-project-needs-compiler/`).

## routes (added 2026-11-03)

`mica lane routes` (worker `~/workspace/bin/lane-routes`): declarative
routing — LANE_MEMORY frontmatter `routes:` blocks compiled against cron
projection deliveries. `show` = the map (snapshot →
`~/workspace/data/lane-routes/routes.json`) · `check` = drift (hard) +
undeclared/no-routes (warnings) · `set` writes the declaration and records
a pending apply — the cron delivery change itself is agent-side
(cron.update), confirmed by `mica lane routes applied <job-id>`.
Spec: `~/workspace/docs/lane-routes-spec-2026-11-03.md`.

## Why there is no `mica chat digest` / `mica chat send`

Bash cannot reach the agent runtime's chat API — verified 2026-10-19 (no
CLI, no socket; the DB path needs agent credentials). Hollow wrappers
were deliberately not built. `mica lane status` covers the file-based
view; verbatim last-words stay agent-side via the recipe below.

## Agent-side digest recipe (the 30-second path)

1. Get chat IDs: `mica lane status --parent <flow-dir> --json` → `chat_id`
   per lane (backfilled in LANES.md at scaffold; never from memory).
2. `chat.read_messages(chat_id, limit=1)` per lane — newest turn first.
   The last substantive assistant message is the lane's last word; if the
   newest turn is the user (Curtis drops into side chats), include it.
3. For deeper history: pass `cursor` from the result to page older.

Do NOT re-learn the bash dead-end: if you're tempted to script chat
reads, stop — there is no API. Update LANES.md state instead; that's what
`mica lane status` renders.
