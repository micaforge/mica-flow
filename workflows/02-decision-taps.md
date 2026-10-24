# Workflow 02 — Decision taps

> **Standard example.** The tap is the decision-checkpoint's grown-up
> form: a decision that outlives one cycle gets its own file, its own
> premises, and a supersede chain. Workflow 01
> (`01-decision-checkpoints.md`) is the ancestor — a checkpoint is a
> fork *inside* a cycle's `_run/checkpoints.md`; a tap is a
> first-class artefact that lives in the flow's `taps/` folder and
> can be picked up, re-sent, or revised as the situation changes.

**Use when:** a decision belongs to the user, will be judged against
the project's history, and may need to be re-presented or revised —
a scope call, a naming lock, an approval that gates a lane. For a
fork that opens and closes inside one wave, workflow 01 is enough.

**Result:** every such decision is one file —
`flows/<parent>/taps/<tap-id>.md` — carrying its own context,
premises, and verdict history. Anyone can judge it from the file
alone; nobody has to reconstruct it from chat.

## 1. The tap file

Frontmatter first, then the brief as the body:

```markdown
---
id: <tap-id>
parent: <flow or lane name>
lane: <owning lane>
status: pending
premises:
  - <a fact the decision rests on, stated so it can be checked>
  - <another premise — if one stops being true, the tap is stale>
superseded_by: null
history: <command that reconstructs this idea's history, e.g.
  `mica search map "<idea>"`, plus the bundle path it wrote>
---

# <tap-id> — <the decision, plainly named>

<the 7-part brief, §2>
```

- **status** — `pending` until answered; then `decided`, with the
  verdict and date appended to the body. A tap whose premises have
  shifted is **revised in place**, never re-presented stale.
- **superseded_by** — when a newer tap replaces this one, name it
  here. Superseded taps hide by default; the chain is the record.
- **history** — whoever judges the tap (the lead deciding it as
  already determined, or the user tapping) judges against the
  recorded history, not memory. The line names the exact command
  that rebuilds it.

## 2. The 7-part brief

Every tap message — and therefore every tap file's body — is the
same seven parts, in order:

1. **Plain explanation** (1–2 terse paragraphs). What is being
   decided and why it matters, in plain language. A stranger
   should understand it.
2. **Project specifics.** Which project / lane / flow the decision
   belongs to, named explicitly; all of them, if it affects several.
3. **Outcome per option.** Concrete consequences for each option —
   what actually happens, not abstractions.
4. **Recommendation + decision-tree reasoning.** Lead with the
   recommended choice and why; then terse Q&A per option: what it
   is, why this one, why not the others, the catch. The user should
   be able to decide from this section alone.
5. **Pros/cons bullets** — only when the trade-offs don't fit the
   decision tree. One line each.
6. **Tappable options.** The options widget (embed token) on its
   own line, after the brief. Each option is a complete reply the
   user could send in plain text. 2–4 options max.
7. **Shareable.** The whole message (minus the embed token, the one
   session-specific part) must stand alone if copied into another
   chat, a doc, or the tap file. No "as I mentioned above."

Rules that keep taps honest:

- **Recommendation first.** Never bury the lead.
- **One decision per tap.** Coupled decisions are named as coupled
  and presented in order.
- **No stale premises.** New findings change the decision → revise
  the tap (and its premises) before re-presenting. A stale tap is a
  misleading tap.

## 3. Relay, decide, record

1. Relay the tap as a message built exactly as §2 — brief first,
   options widget last, one widget per message.
2. On the answer, set `status: decided` in the file and append the
   verdict: the choice **in the user's own words**, with date and
   any constraint that came with it.
3. Resolve the work the tap gated: brief items written against the
   open decision get rewritten to the decision — an edit, not a
   rework, because the briefs carried the branches.
4. If a later tap replaces this decision, set `superseded_by` on
   the old file; don't delete it. The chain *is* the history.

## Origin

Canonical spec: Curtis, 2026-10-19 (tap format), with the
decision-history addendum 2026-10-21 (the `history:` frontmatter
line). The format runs the estate's standing decisions — scope
calls, naming locks, credential and publishing gates — as files
under each flow's `taps/` folder, read by the tap-digest tooling
rather than held in anyone's memory.
