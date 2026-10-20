# lane caps — agent notes

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
