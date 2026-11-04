#!/usr/bin/env python3
"""The inclusion battery + interval/crash battery for packet 0017
(stage 1's proof, re-run at every later stage).

Forward battery: the compiler runs against a synthetic fixture repo
(make_fixture.py). Assertions: the excluded lane (beta, marked by
its OWN property) appears in NO compiler output — board, ledger,
check, render — and its canaries appear in no generated file and in
no board-subtree history; delta's pointer into beta's home renders
withheld at extraction AND in the ping path; gamma's stub is
followed, eta's renders AS a stub; epsilon's A->B->C interval wakes
BOTH intermediate holders in one compile; zeta's included->excluded
transition drops it at the marking's first compile with no new
accrual (N4a); a no-op run commits nothing.

Break battery (the proof the forward battery can fail): two scratch
COPIES of the compiler — (1) the structural resolution bypassed for
a read-everything set, (2) a name-based skip list with the lane
renamed — must LEAK the canaries onto the board. A battery that
passes both ways proves nothing and does not ship.

Crash battery: kill mid-compile at walk / render / after-dispatch;
the stamp must not advance, and the clean re-run must ping each
flip exactly once. Plus the whole-tree tolerance: a simulated sweep
committing the renamed board first makes the writer's own commit
empty — success, verified identical (N3(i)).

Run: python3 battery.py [--compiler PATH] [--keep]
Exit 0 iff every forward assertion passes AND both break variants
leak as required.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_fixture as fx  # noqa: E402

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'}  {name}"
          + (f" — {detail}" if detail and not cond else ""))


def run_compiler(compiler, root, *args, env_extra=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [sys.executable, compiler, "--repo", root,
         "--workspace-root", os.path.join(root, "workspace"),
         "--desks-root", os.path.join(root, "skills"), *args],
        capture_output=True, text=True, env=env)
    return r


def git(root, *args, text=True):
    r = subprocess.run(["git", "-C", root, *args], capture_output=True,
                       text=text)
    return r.stdout if text else r.stdout


def head(root):
    return git(root, "rev-parse", "HEAD").strip()


def board_at(root, rev="HEAD"):
    r = subprocess.run(["git", "-C", root, "show",
                        f"{rev}:memory/board/BOARD.md"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def ledger(root):
    path = os.path.join(root, "memory/board/ping-ledger.jsonl")
    if not os.path.isfile(path):
        return []
    return [json.loads(ln) for ln in open(path) if ln.strip()]


def pings(root):
    return [e for e in ledger(root) if e.get("kind") == "ping"]


def committed_pings(root):
    r = subprocess.run(["git", "-C", root, "show",
                        "HEAD:memory/board/ping-ledger.jsonl"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return []
    return [json.loads(ln) for ln in r.stdout.splitlines()
            if ln.strip() and json.loads(ln).get("kind") == "ping"]


def canary_free(text):
    return not any(c in text for c in fx.CANARIES)


def main():
    compiler = os.path.join(HERE, "..", "board-compiler.py")
    keep = "--keep" in sys.argv
    if "--compiler" in sys.argv:
        compiler = sys.argv[sys.argv.index("--compiler") + 1]
    compiler = os.path.abspath(compiler)
    work = os.path.join(HERE, "..", "_run", "battery-work")
    if os.path.isdir(work):
        shutil.rmtree(work)
    os.makedirs(work)

    # ---------- forward battery ----------
    root = os.path.join(work, "fx")
    fx.seed(root)
    r = run_compiler(compiler, root, "--write", "--json")
    res = json.loads(r.stdout) if r.returncode == 0 else {}
    check("baseline write succeeds", r.returncode == 0 and
          res.get("baseline"), r.stdout + r.stderr)
    board = board_at(root)
    check("baseline board carries no canary", canary_free(board))
    check("baseline board has no beta entry", "## beta" not in board)
    check("baseline board has no beta chat id", fx.B not in board)
    check("gamma's stub is FOLLOWED (its queue renders)",
          "gamma item one" in board)
    check("eta renders AS a stub, never an empty queue",
          "rendered AS a stub" in board)
    check("zeta renders while included", "zeta item one" in board)
    check("delta's pointer into beta renders withheld",
          "(pointer withheld)" in board and
          f"side-chats/{fx.B}/" not in board)
    check("baseline ledger has no pings", pings(root) == [])
    r = run_compiler(compiler, root, "--check")
    check("check leg is canary-free, exit 0 on a clean fleet",
          canary_free(r.stdout) and r.returncode == 0, r.stdout)
    # render over a flip-bearing interval is read-only
    fx.c2(root)
    fx.c3(root)
    head_before, board_before = head(root), board_at(root)
    r = run_compiler(compiler, root, "--render")
    check("render over a flip-bearing interval commits nothing",
          head(root) == head_before and board_at(root) == board_before)
    check("render output is canary-free", canary_free(r.stdout))
    # the interval compile: A->B->C in ONE interval wakes both
    r = run_compiler(compiler, root, "--write", "--json")
    res = json.loads(r.stdout) if r.returncode == 0 else {}
    ps = pings(root)
    eps = [p for p in ps if p["lane"] == "epsilon"]
    check("interval write succeeds", r.returncode == 0, r.stdout)
    check("A->B->C: BOTH intermediate holders woken in one compile",
          [p["assignee"]["slug"] for p in eps] == ["delta", "gamma"],
          str([(p["assignee"], p["trigger"]["kind"]) for p in eps]))
    check("delta's assignment ping fires to alpha",
          any(p["lane"] == "delta" and
              p["assignee"]["slug"] == "alpha" for p in ps))
    check("exactly 3 pings in the interval", len(ps) == 3, str(len(ps)))
    check("no ping text carries the excluded pointer",
          all(fx.B not in p.get("ping_text", "") for p in ps))
    board = board_at(root)
    check("zeta dropped at its exclusion's first compile (N4a)",
          "## zeta" not in board and "zeta item one" not in board)
    check("zeta's prior state remains in board history (no purge)",
          "zeta item one" in board_at(root, "HEAD~1"))
    check("no zeta ping ever composed",
          all(p["lane"] != "zeta" for p in ps))
    hist = git(root, "log", "-p", "--", "memory/board/")
    check("canaries absent from the board subtree's whole history",
          canary_free(hist))
    check("post-flip board still canary-free", canary_free(board))
    # dependency landed via the band diff
    fx.c4(root)
    r = run_compiler(compiler, root, "--write", "--json")
    ps = pings(root)
    check("dependency-landed ping fires when the blocker clears",
          any(p["lane"] == "delta" and
              p["trigger"]["kind"] == "dependency-landed"
              for p in ps), str([p["trigger"] for p in ps]))
    # no-op discipline
    h = head(root)
    r = run_compiler(compiler, root, "--write")
    check("a no-event run commits nothing",
          head(root) == h and "nothing committed" in r.stdout,
          r.stdout)

    # ---------- break variants ----------
    src = open(compiler).read()
    # (1) bypass the structural resolution -> read-everything set
    anchor = "v.all_lanes, v.included = resolve_inclusion(repo, head0)"
    assert anchor in src, "bypass anchor not found in compiler source"
    v1 = os.path.join(work, "compiler-bypass.py")
    open(v1, "w").write(src.replace(
        anchor, "v.all_lanes, _xi = resolve_inclusion(repo, head0)\n"
                "    v.included = dict(v.all_lanes)"))
    broot = os.path.join(work, "fx-bypass")
    fx.seed(broot)
    run_compiler(v1, broot, "--write")
    leaked = not canary_free(board_at(broot))
    check("BREAK 1 (resolution bypassed): canaries LEAK onto the "
          "board — the battery can fail", leaked)
    # (2) name-based skip list + rename the lane
    anchor2 = "repo.prop_at(head, rec)"
    assert anchor2 in src, "name-skip anchor not found"
    v2 = os.path.join(work, "compiler-nameskip.py")
    open(v2, "w").write(src.replace(anchor2, "(slug == 'beta')"))
    for tag, comp, expect_leak in (("nameskip", v2, True),
                                   ("property", compiler, False)):
        rroot = os.path.join(work, f"fx-rename-{tag}")
        fx.seed(rroot)
        # rename beta -> beta2 (slug, page, flow dir); marking stays
        idxp = os.path.join(rroot, "memory/lanes/INDEX.md")
        t = open(idxp).read().replace("| beta | betaflow |",
                                      "| beta2 | beta2flow |")
        open(idxp, "w").write(t)
        os.rename(os.path.join(rroot, "memory/lanes/beta.md"),
                  os.path.join(rroot, "memory/lanes/beta2.md"))
        os.rename(os.path.join(rroot, "workspace/flows/betaflow"),
                  os.path.join(rroot, "workspace/flows/beta2flow"))
        fx.commit(rroot, "rename beta -> beta2 (marking unchanged)")
        run_compiler(comp, rroot, "--write")
        leaked = not canary_free(board_at(rroot))
        check(f"BREAK 2 ({tag}): renamed lane "
              f"{'LEAKS under a name-skip list' if expect_leak else 'stays excluded by property'}",
              leaked == expect_leak)

    # ---------- crash battery ----------
    for point in ("walk", "render", "dispatch"):
        croot = os.path.join(work, f"fx-crash-{point}")
        fx.seed(croot)
        run_compiler(compiler, croot, "--write")
        import re as _re2
        base_stamp = _re2.search(r"compiled-through: ([0-9a-f]{40})",
                                 board_at(croot)).group(1)
        fx.c2(croot)
        r = run_compiler(compiler, croot, "--write",
                         env_extra={"BOARD_COMPILER_CRASH_AT": point})
        # judged on COMMITTED state: after a dispatch crash the
        # worktree legitimately holds the renamed, uncommitted
        # ledger — the residue the design names; HEAD must not move
        # and no ping may be committed.
        import re as _re
        m = _re.search(r"compiled-through: ([0-9a-f]{40})",
                       board_at(croot))
        stamp_ok = bool(m) and m.group(1) == base_stamp and \
            not committed_pings(croot)
        check(f"crash at {point}: exit 70, stamp unmoved, no pings "
              f"committed", r.returncode == 70 and stamp_ok,
              f"rc={r.returncode}")
        r = run_compiler(compiler, croot, "--write", "--json")
        ps = pings(croot)
        ids = [p["flip_id"] for p in ps]
        check(f"crash at {point}: clean re-run pings each flip "
              f"exactly once", r.returncode == 0 and
              len(ids) == len(set(ids)) and len(ps) == 2,
              str([(p['lane'], p['assignee']['slug']) for p in ps]))
    # whole-tree tolerance: the sweep lands the rename first (N3(i))
    sroot = os.path.join(work, "fx-sweepsim")
    fx.seed(sroot)
    run_compiler(compiler, sroot, "--write")
    fx.c2(sroot)
    r = run_compiler(compiler, sroot, "--write", "--json",
                     env_extra={
                         "BOARD_COMPILER_SIM_SWEEP_AFTER_RENAME": "1"})
    res = json.loads(r.stdout) if r.returncode == 0 else {}
    check("whole-tree sweep landing first: writer tolerates the "
          "empty commit (N3(i))", r.returncode == 0 and
          res.get("landed_by_sweep") is True, r.stdout + r.stderr)

    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks pass")
    if not keep:
        pass  # work dir kept for evidence either way (packet _run)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
