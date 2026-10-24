# Lane-split playbook — exact tool calls

Run these in order. The lead runs every step; builders only ever see step 6.

## 0. Decide the lanes

Write the parent `SPEC.md`: vision in one paragraph, then one section per
lane — source, rework plan, tie-in to the whole, license posture, and
whether it's **parallel-safe** or **feeds the next lane**. Name human gates
explicitly (whose tap, what exactly).

## 1. Recon (per external source)

```bash
git clone --depth 1 <url> ~/workspace/recon/<name>-recon/
```

Never /tmp — a VM replacement wipes it. Read-only reference; briefs forbid
copying code out (matters for AGPL sources).

## 2. Scaffold one flow per lane

```bash
mica-flow <lane-name> "a01-first-cycle,a02-second-cycle" --goal "<one line>"
```

Cycles come from the spec. Keep them small: one wave = one builder.

## 3. Collision check (before ANY dispatch)

```bash
ls ~/workspace/flows/<lane>/a01-*/_run/
grep <lane> ~/workspace/.jarvis/agent-registry.jsonl | tail -5
```

Empty `_run/` is not enough — another lead may have dispatched 10 minutes
ago. If a duplicate is in flight, stand down.

## 4. Research assistant per lane

```bash
chat.create(name="<Lane> — research", context_mode="fresh",
            message="Pre-scope/research assistant for the <lane> flow: <one line>.")

chat.send_message(chat_id, """
You're the research assistant for the <lane> flow.

Context: <2-3 sentences: what the lane is, what it ties into.>
Recon: ~/workspace/recon/<name>-recon/ (read-only — do not write to it).

Your mission:
1. Map <the specific seam: engine registry / public API / pipeline overlap>.
2. Note what fights headless/server use, license posture, infra constraints.
3. Fill in a01-<cycle>/BRIEF.md in ~/workspace/flows/<lane>/ — concrete
   enough that a builder can start: exact files, done criteria, stop
   conditions, budget. Cite file:line.

Keep the chat's MEMORY.md current. End reports with an explicit "ready"
state. Never contact Curtis directly — Mica relays both ways.
""")
```

One assistant per lane. They work in parallel.

## 5. Collect the briefs

Each assistant reports READY with a filled a01 BRIEF.md. Read the brief
before dispatching — the lead verifies the brief is concrete, not the
builder.

## 6. Dispatch builders (parallel or sequential)

```bash
subagent.spawn(message="""
<Lane> wave-1 builder: <cycle>.

Read and execute exactly: ~/workspace/flows/<lane>/a01-<cycle>/BRIEF.md
(status: ready). Execute the plan; don't redesign it.

Scope: <exact>. Files in scope: <exact paths>. Touch nothing else.
Done criteria: <from the brief>. Stop conditions: <from the brief>.
Budget: <time> / <tool calls>. If blocked: stop, report done / not done / why.
""")
```

Then append the registry line (Prism Live view needs it):

```bash
python3 -c "
import json, time
open('$HOME/workspace/.jarvis/agent-registry.jsonl','a').write(json.dumps({
  'agent_id': '<id>', 'task_label': '<lane> <cycle> builder',
  'flow': '<lane>', 'cycle': '<cycle>',
  'parent_id': 'main', 'spawned_at': int(time.time())}) + '\n')"
```

**Sequential mode:** dispatch lane N+1 only after lane N's wave closes —
its brief gets lane N's outputs appended.

## 7. Relay + close

- Relay each completion to Curtis with: what shipped, verification notes,
  deviations, what's next.
- Close every piece of lane work with the **five-line relay** to the
  parent, sent in the same turn the work lands:

  ```
  what landed — <the deliverable, one line>
  gate — <the gate it waits on, or "none">
  ask — <the decision or answer needed, or "none">
  state — <the lane's state after this landing>
  links — <file/chat links to the source docs>
  ```

  A report inside the lane's own chat is not a relay. The same turn
  also updates the lane's LANE_MEMORY and sends the same-form notice
  to any peer lane whose inputs the work changed. Ungated
  completions deliver through their records alone.

  *(Pattern source: lane-relay standing rule, 2026-10-21.)*
- Run the close gate yourself — never the builder:

```bash
mica flow close <lane> --cycle <cycle>
```

BLOCKED is a stop, not a suggestion. A blocked wave parks in LANES.md
with its unblock condition.

## 8. Update LANES.md, then next

Mark the lane's new state. Then per lane: next wave (back to step 5 with
the crew-drafted next brief), or park. Adding a lane later = steps 1–4 for
the new lane only; existing lanes are untouched.
