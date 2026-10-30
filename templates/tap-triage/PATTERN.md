# PATTERN — tap triage: class every decision point at source

Standing text, inherited by every flow and lane.
Adopted at Mica's gate 2026-10-30 (Steward rubric-
adoption packet, t01). Design of record:
`flows/template-steward/a04-arc2-seed/_run/
tap-triage-design.md` — this pattern states the rule;
the design carries the rationale. Tooling:
`tap-digest --triage` / `--json` PROPOSES a class per
open tap; an agent disposes. The script never judges
a borderline, decides, or sends.

## The rule

A lane decision point never terminal-surfaces to
Curtis by default. It is classed first, at its source,
in the lane's own documents. Only a Curtis-tier class
earns his screen; everything else is decided at
desk/Mica and reported with his overrule standing.

## The rubric — six ordered tests, FIRST match wins → Curtis

1. **Public face / outreach** — puts words, content,
   or a contact in front of anyone outside the
   household in Curtis's or Gravicity's name: email
   sent for him, anything private → public (even when
   planned), contacting a person. Borderline: a repo
   already slated public in a plan → still Curtis;
   the plan is not the tap.
2. **Money** — spends, commits, refunds, or changes a
   price/billing state. Borderline: a $0 free-tier
   signup is not money; it falls to test 3 if it
   creates an account.
3. **Credentials / external accounts** — creates,
   holds, rotates, or grants access via a credential,
   token, or external account (incl. his own sign-ins
   and any Meta contact route). Borderline: adding an
   already-vaulted key to an internal config → not
   external; decidable, logged.
4. **Irreversible acts** — can the state after be
   restored from records/backups alone? Borderline:
   deleting a scratch branch → reversible; deleting a
   repo or a vault item → Curtis.
5. **Human timing / personal affairs** — sets when a
   human does something, or touches family/personal
   matters (his hands-on steps, replies, calls, the
   kids' schedule). Borderline: scheduling an internal
   cron → not human timing; asking Curtis to paste a
   key at a chosen moment → Curtis.
6. **Persona / identity picks** — chooses a name,
   voice, face, or character representing him or Mica
   publicly. Borderline: an internal-only agent
   codename → decidable; the show Host's name/voice →
   Curtis.

No match on any test = decidable at desk/Mica.

## Filing discipline (part of the pattern)

- **Tap frontmatter carries premises** — and the
  triage proposals where the tool has run them:
  `class?` / `route?`. Premises are the classing
  evidence; a tap without them cannot be classed.
- **Completeness rule:** an item missing its class or
  premises does not route upward half-formed — it
  BOUNCES to its owning lane for a complete
  escalation packet (claim · file:line pointer ·
  verified-vs-unknown split · recommendation · tier
  call). Before bouncing, READ the tap file itself —
  a bounce can be an extraction gap, not a thin
  packet (calibration note, 2026-10-24).
- **Decidable discipline (the 90% rule):** decided at
  desk/Mica by pattern, logged at the item's home,
  reported with overrule standing. Decided ≠ vanished.
- **Stale taps are revised, not pushed**; superseded
  taps hide by default.
- **Aging:** at ~2h untapped, decidable items surface
  with the deciding pattern NAMED (untapped = decided
  interplay); Curtis-tier items age silently — the
  carve-out never expires.
