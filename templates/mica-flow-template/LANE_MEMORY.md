---
type: lane-memory
lane: {{FLOW_NAME}}
owner: TODO — the lane lead (name + seat/chat id)
updated: {{DATE}}
status: active
cap: 300
upkeep:
  - queue at top, dated; update as steps complete, not at cycle end
  - newest first; prune superseded lines in place — history lives in SoT
  - pointers, never copies: state + SoT links + recall commands only
  - update on: completion · decision · tool/app change · compaction approach
  - over cap or stale frontmatter = a finding, fix in the same session
---

# LANE_MEMORY — {{FLOW_NAME}}

<!-- For chat-less lanes: this file is the lane's memory slot, in
     the flow dir. Lanes WITH a side chat keep LANE_MEMORY at
     ~/side-chats/<chat-id>/LANE_MEMORY.md instead and delete this
     file at seeding. -->

## Next steps (queue — updated as steps complete)

1. TODO — the lane's next real step, named.

## Durability buckets (A56 audit rule)

- Bucket 1 (in ~/workspace): this flow's files.
- Bucket 2 (floor-restored): TODO — anything outside ~/workspace
  this lane depends on that a floor restores from a workspace
  source; name the floor.
- Bucket 3 (named exceptions): TODO — anything outside both,
  with the reason; anything in no bucket is a defect to fix or file.

## Current state

- Seeded {{DATE}} from the mica-flow template.
