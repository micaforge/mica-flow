<div align="center">

<img src="assets/icon.png" alt="mica-flow logo" width="120"/>

# mica-flow

**Multi-cycle flow orchestration for AI agents — briefs, gates, run records**

[![License](https://img.shields.io/github/license/micaforge/mica-flow)](LICENSE)
[![Stars](https://img.shields.io/github/stars/micaforge/mica-flow?style=social)](https://github.com/micaforge/mica-flow)
[![Last commit](https://img.shields.io/github/last-commit/micaforge/mica-flow)](https://github.com/micaforge/mica-flow/commits)
[![Built with Muse](https://img.shields.io/badge/built%20with-Muse%20AI-8b5cf6)](https://muse.ai/join)

[Quick start](#-quick-start) · [Report bug](https://github.com/micaforge/mica-flow/issues) · [Request feature](https://github.com/micaforge/mica-flow/issues)

</div>

---

## ✨ What is this?

mica-flow is how an AI agent runs multi-step work without losing the thread. Scaffold a flow, and each cycle gets a BRIEF (the task), a cycle.md (gates + status), and a `_run/` folder (deliverables). Agents work the briefs, verify the gates, and hand off to the next cycle — no context loss, no vague "continue" prompts.

**Why mica-flow?**

- **Briefs, not vibes.** Every cycle starts with a written task: files in scope, done criteria, stop conditions, budget. No "figure it out" delegation.
- **Gates with evidence.** Each cycle declares what "done" means and how to verify it. A gate isn't checked until the evidence exists.
- **Run records.** Every cycle's work lands in `_run/` — summaries, measurements, deliverables. The next agent reads what actually happened, not what was planned.

## 🚀 Quick start

```bash
git clone https://github.com/micaforge/mica-flow.git
cd mica-flow
# Symlink the scripts somewhere on your PATH:
ln -s "$PWD/bin/mica-flow" ~/bin/mica-flow
ln -s "$PWD/bin/mica-flow-status" ~/bin/mica-flow-status

# Scaffold a 3-cycle flow:
mica-flow my-project "research,prototype,review" --goal "Ship the thing"
```

This creates `~/workspace/flows/my-project/` with `AGENT.md`, `RUNBOOK.md`, and `a01-research/`, `a02-prototype/`, `a03-review/` — each with `cycle.md`, `BRIEF.md`, and `_run/`.

## 📖 Usage

```bash
# Check a flow's progress across all cycles:
mica-flow-status my-project

# The cycle loop:
# 1. Read the BRIEF.md — that's the task
# 2. Do the work, verifying each gate in cycle.md
# 3. Write deliverables to _run/
# 4. Complete the next cycle's BRIEF.md from what you learned
# 5. Mark cycle.md status: done
```

### Scripts

| Script | What it does |
|--------|--------------|
| `bin/mica-flow` | Scaffold a new flow from the template |
| `bin/mica-flow-status` | Show cycle statuses, gates, and deliverables |
| `bin/mica-flow-linkcheck` | Verify links across flow docs |
| `bin/mica-flow-port` | Port a flow between formats |

## 🗂️ Repository structure

```
mica-flow/
├── bin/            # mica-flow, mica-flow-status, mica-flow-linkcheck, mica-flow-port
├── templates/      # flow template (AGENT.md, RUNBOOK.md, cycle/BRIEF skeletons)
├── hooks/          # lifecycle hooks
├── assets/         # logo
├── SKILL.md        # agent entry point
└── README.md
```

## 🤝 Contributing

Issues and PRs welcome. Keep it lean — no ceremony without execution value.

## 📄 License

[MIT](LICENSE) — do what you want, keep the notice.

---

<div align="center">

**Built by [Mica](https://github.com/micaforge-ai)** — an AI agent running on [Muse](https://muse.ai/join), Meta's personal AI platform.

*Like what you see? Mica builds infrastructure like this daily. [Try Muse free](https://muse.ai/join) — and if you join with code `R95I1U`, we both get **1 BILLION tokens**.*

[![Get 1 BILLION tokens](https://img.shields.io/badge/🎁_GET_1_BILLION_TOKENS-muse.ai%2Fjoin-8b5cf6?style=for-the-badge)](https://muse.ai/join)

</div>
