# LANES.md — parent lane registry

Copy per project. The lead updates this on every completion. One glance =
the whole project.

| Lane | Flow | State | Owner | Blockers | Human taps | Chat |
|------|------|-------|-------|----------|------------|------|
| 1 · <name> | `flows/<flow>/` | 🟢 wave-2 ready / 🟡 wave-1 running / 🔴 blocked / ⬛ done / 💀 killed / ⏸ parked | lead | <what's stuck> | <whose tap, what exactly> | <research chat_id> |

## Rules

- **Chat column:** the lane's research/worker chat_id, written at scaffold
  time (PLAYBOOK step 4). This is what makes lanes compaction-proof: the
  lead's `chat.read_messages` and `mica lane status` resolve lanes from
  this file, never from memory.
- **State** is the lead's live view — update on every completion, block,
  or park. Emoji legend: 🟢 advancing · 🟡 running · 🔴 blocked · ⬛ done ·
  💀 killed · ⏸ parked.
- **Human taps** is the live outstanding-decision set — write the exact tap
  the moment it's known; clear the cell + log the decision when Curtis
  answers. `mica lane taps` renders every parent's outstanding taps.

## Integration track

- Status: not started (starts after 2+ lanes close wave-1)
- Design questions: <...>

## Log

- 2026-10-18: <lane> wave-1 closed (PASS). <one line.>
- 2026-10-18: <lane> blocked: <condition>. Parks until <unblock>.
