# Toolkit seed — how to grow a tool like this one

> The seed of a micaforge toolkit: enough of the specifics that, given
> the same idea, an agent rebuilds almost the same tool. **mica-flow is
> the worked example** — every decision below is one mica-flow actually
> made, with the reason and what breaks if you change it. Copy the
> decisions, not just the files.

## The idea (one paragraph)

Multi-cycle flow orchestration for AI agents. Work too big for one turn
gets scaffolded as a *ring*: named flows, each a sequence of bounded
cycles. Every cycle has a written brief (the contract), gates (what
"done" means), and run records (what actually happened). Agents work
the briefs; the lead verifies the gates. No context loss, no vague
"continue" prompts.

## The load-bearing decisions

Each: the decision, why it exists, and the failure mode if you drop it.

1. **Rings live at `~/workspace/flows/<name>/`; cycles are
   `<prefix><NN>-<slug>`.** The prefix is project-specific — 1–2
   letters defined per flow in its ROUTER.md (`d01`, `r01`, `t02`);
   sub-phases take dot notation (`r03.01`). Not generic `aNN`:
   sortable names only help if the prefix says which project a
   cycle belongs to. Existing `aNN` flows keep their names — no
   retroactive renames.
   Sortable, greppable, machine-parseable — the status CLI reads the
   directory, not a database. Drop it and every tool has to learn your
   layout.
2. **Every cycle = `BRIEF.md` + `cycle.md` + `_run/`.** The brief is the
   contract: task, exact files in/out of scope, done criteria, stop
   conditions, budget. Learned the hard way: a vague "fix X" brief
   turned into a 25-minute token burn. The rule is *a builder gets the
   plan, not the problem.*
3. **Agents execute; they don't redesign.** Blocked, over budget, or the
   plan is wrong → stop and report (done / not done / why). The lead's
   map stays authoritative; improvisation is how scopes explode.
4. **One builder per cycle.** Check the cycle's `_run/` for deliverables
   or an in-flight marker before dispatching. Two waves double-built
   before this rule existed.
5. **Budget per cycle: 30 min / 60 tool calls.** Bounds the burn and
   forces honest scoping. A cycle that only shuffles paper is a bug.
6. **The lead harvests.** Reads the `_run/` deliverables, spot-checks
   2–3 claims against cited files, verifies gates before advancing.
   A builder's completion report is a claim, not a fact — *verify
   before relaying.*
7. **The finishing agent completes the next cycle's BRIEF.** The
   freshest context writes the next contract. "Successor will write it"
   is how briefs arrive as outlines.
8. **User forks become decision checkpoints → tappable cards.** One
   question, 2–4 options each with a one-line trade-off, relayed as a
   tappable card; one tap decides; the answer lands in
   `_run/checkpoints.md` and unblocks the next brief. The lead never
   invents the user's answer. **Standard example:**
   `workflows/01-decision-checkpoints.md` — copy this pattern
   idea-independent into every future toolkit.
9. **`bin/` holds single-purpose CLIs** (`mica-flow`, `mica-flow-status`,
   …), installed by symlinking onto PATH. One tool, one job,
   composable in scripts. A CLI that does three things is three CLIs
   wearing a trench coat.
10. **`SKILL.md` is the router.** It must say when to use the tool, give
    the 30-second quick start, point to `workflows/` for procedures and
    `references/` for deep docs, and name every `bin/` script with one
    line on when to reach for it. Test: a new agent (or a future you)
    uses the package from SKILL.md alone.
11. **`workflows/` = do-this, `references/` = learn-this.** Workflows are
    numbered procedures ending in a verifiable result; references are
    tutorials, architecture, troubleshooting. Never mix them — a
    procedure with a history lesson is a procedure nobody finishes.
12. **Publish guard.** Before anything goes public: scan for secrets and
    over-specific internals (`mica-audit`), one real 512×512
    `assets/icon.png` (never a symlink, never five variants), one clean
    initial commit. The org's bar is the same as the private bar.

## Anatomy map

| Path | Purpose | For your toolkit |
|------|---------|------------------|
| `SKILL.md` | Router: trigger, quick start, pointers | Copy the contract, fill your content |
| `bin/*` | Single-purpose CLIs | Copy the pattern, write your verbs |
| `workflows/01-*.md` | Numbered procedures | Copy `01-decision-checkpoints.md` as-is; write your own 02+ |
| `references/` | Deep docs | Grow as you learn; one-line `Use when:` per note |
| `templates/` | Scaffolds your tool installs | Adapt: what does your tool stamp out? |
| `hooks/` | Lifecycle enforcement (e.g. pre-push audit) | Copy; hooks are idea-independent |
| `assets/icon.png` | The one real 512px icon | Replace the pixels, keep the discipline |
| `PACKAGE.md` | The layout contract itself | Copy verbatim |
| `README.md` | Public face: what, why, quick start | Copy the shape, write your story |

## The adapt recipe

Given a new idea X:

1. Write the one-paragraph idea (like above). If it takes two
   paragraphs, the idea isn't ready.
2. Walk the 12 decisions. Keep or change each **deliberately** — write
   one line per changed decision saying why X differs. Unchanged
   decisions are inherited silently; that's the point of a seed.
3. Copy the skeleton: `SKILL.md`, `PACKAGE.md`, `bin/` naming pattern,
   `workflows/01-decision-checkpoints.md`, `hooks/pre-push`.
4. Write your tool's `workflows/02-*.md` for its core loop.
5. Scaffold `templates/` for whatever your tool stamps out (if anything).
6. Run the publish guard before the first commit, even a private one.

### Mini-example: adapting to "capsule" (versioned capability packs)

Idea: versioned, installable packs of agent capabilities (caps +
skills + docs) with dependency checks. Walking the decisions: 1–7
hold unchanged (a pack build is still multi-cycle work). 8 holds —
version bumps and dependency conflicts are user forks, so the
checkpoint pattern copies as-is. 9 adapts: `bin/` verbs become
`capsule-build`, `capsule-install`, `capsule-check`. 12 holds —
capsules ship to the org, so the audit bar is load-bearing, not
ceremony. Everything else inherits. That's the seed doing its job:
four deliberate changes, eight free decisions.

## What NOT to copy

- Instance data: specific cycle names, flow directories, run records.
  Those are the tool *in use*, not the tool.
- Build debris: generation working files, variant exports, drafts.
  They live outside the repo tree (`media-archive/`), never in
  `assets/`.
- Credentials, paths, or anything user-specific. The seed must be
  buildable by a stranger.
