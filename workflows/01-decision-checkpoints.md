# Workflow 01 — Decision checkpoints

> **Standard example.** This workflow is the reference implementation
> every future micaforge toolkit copies for user-facing forks. When your
> tool needs a human decision mid-run, do it exactly like this.

**Use when:** a flow wave hits a genuine fork — two defensible designs, a
wording choice, a scope question only the user can answer. Not for
something the lead can just decide (see "when the best choice is
obvious, make the call" in the cycle loop); this is for calls that
belong to the user.

**Result:** every open fork becomes a tappable card in chat; the user
answers in one tap; the decision lands back in the cycle's `_run/` and
unblocks the downstream brief. Feedback is one tap, not a paragraph.

## 1. Write the checkpoint

The wave lead writes each fork as a **decision checkpoint** in the
cycle's `_run/checkpoints.md`:

- **One question** — the fork, plainly stated.
- **2–4 options**, each with a one-line trade-off. Say what it costs,
  not just what it does. If a review panel or expert weighed in, note
  the lean (and who leaned) — it informs, never decides.
- **A visual reference** where the choice is visual (screenshot, mockup,
  or annotated mockup). Point at the file; don't paste the image into
  the checkpoint.
- **Status OPEN.** An unanswered checkpoint stays open — the lead never
  invents the user's answer and never defaults it.

Template:

```markdown
## CPN — <one question>
*From <finding or observation>. <One line of context.>*

**Options:**
- **A. <name>** — <one-line trade-off>. *(Panel lean: <who> — optional)*
- **B. <name>** — <one-line trade-off>.
- **C. <name>** — <one-line trade-off>.

**Status: OPEN**
```

## 2. Relay as tappable cards

The lead relays open checkpoints to the user as tappable cards via
`muse.create_options`:

1. **Index card first** — if several checkpoints are open, one message
   lists them briefly with a single options widget ("Take up CP1
   (empty capture)", "Take up CP2 (dormant streams)", …). The user
   picks which fork to take up first.
2. **One card per checkpoint** — present the question with the options
   written out in full (same wording as `checkpoints.md`), then the
   options widget. Each option label is a **complete reply** the user
   could send in plain text, e.g. `"CP1: last good snapshot, greyed,
   with an honestly-aging banner"`. Fresh widget per checkpoint; one
   widget per message max.
3. **After the answer**, record it (step 3), then offer the next
   checkpoint or the natural next action ("Take up CP3…", "Kick off
   rung 2") — again as options, so the user can keep tapping.

Message shape for a checkpoint card:

```
**CPN — <question>**

**A.** <name> — <one-line trade-off>. <Optional: who's leaning.>
**B.** <name> — <one-line trade-off>.
**C.** <name> — <one-line trade-off>.

[[hatch_widget:...]]
```

## 3. Record the decision

On the user's answer, in `checkpoints.md`:

```markdown
**✅ DECIDED by <user> <date>: Option <letter>** — <the choice in the
user's own words>. <Any hard constraint that came with it.>
```

Then resolve the downstream brief: plan items the brief marked
**"pending CPN"** get rewritten to design to the decision. The brief
never designed around an assumed answer in the first place — items
carried the branches, so this is an edit, not a rework.

## 4. Keep the loop honest

- **Don't batch-decide.** Present forks; don't bundle them into one
  "approve all." Each checkpoint is its own tap.
- **No fake urgency.** An open checkpoint is a standing invitation, not
  a nudge. Never re-present one unprompted unless the work it blocks
  becomes the critical path.
- **Disagreements survive.** If a panel split on a checkpoint, the
  split stays in the record verbatim — the user may want to see it.

## Origin

This pattern was built the night of 2026-10-17 on the `prism-ux-review`
flow's `a01-panel-review` cycle: 5 checkpoints (CP1–CP5), all decided
by the user in ~20 minutes of tapping, each feeding straight into the
rung-2 brief. The checklist entry and the AGENTS.md convention
("Decision checkpoints") date from that night.
