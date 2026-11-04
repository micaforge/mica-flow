#!/usr/bin/env python3
"""The C2 leg's own test (stage 3): relative freshness as a prompt.
A lane whose flow records move AFTER its band last moved earns a
prompt carrying both ages; a lane whose band is its newest activity
earns none; a bulk-machinery touch of the band (a schema
conversion) does not count as the band moving."""
import importlib.util
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_fixture as fx  # noqa: E402


def load_compiler(path):
    spec = importlib.util.spec_from_file_location("board_compiler",
                                                  path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def commit_at(root, msg, when):
    env = dict(os.environ)
    env.update(fx.ENV)
    env["GIT_AUTHOR_DATE"] = when
    env["GIT_COMMITTER_DATE"] = when
    subprocess.run(["git", "-C", root, "add", "-A"], check=True,
                   env=env, capture_output=True)
    subprocess.run(["git", "-C", root, "commit", "-q", "-m", msg],
                   check=True, env=env, capture_output=True)


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")


def main():
    compiler = os.path.join(HERE, "..", "board-compiler.py")
    if "--compiler" in sys.argv:
        compiler = sys.argv[sys.argv.index("--compiler") + 1]
    bc = load_compiler(os.path.abspath(compiler))
    work = os.path.join(HERE, "..", "_run", "c2-work")
    if os.path.isdir(work):
        shutil.rmtree(work)
    os.makedirs(work)
    root = os.path.join(work, "fx")
    fx.seed(root)
    # the seed commits carry the real clock; the dated test commits
    # must order AFTER them, so the base is tomorrow, not a fixed
    # past date.
    t0 = datetime.now(timezone.utc) + timedelta(days=1)
    repo = bc.Repo(root)
    lane = bc.Lane("alpha")
    lane.chat_id = fx.A
    lane.flows = ["alphaflow"]
    band_path = f"side-chats/{fx.A}/LANE_MEMORY.md"
    results = []

    def check(name, cond):
        results.append((name, bool(cond)))
        print(f"{'PASS' if cond else 'FAIL'}  {name}")

    # activity lands in alpha's flow AFTER the band's last move
    fx.put(root, "workspace/flows/alphaflow/notes.md",
           "# alphaflow notes — the lane worked here\n")
    commit_at(root, "alphaflow work lands", iso(t0 + timedelta(days=2)))
    p = bc.c2_prompt(repo, lane, band_path)
    check("lane active outside its band after the band moved → "
          "prompt with both ages", p is not None and
          p["active_last"] > p["band_last"])
    # the band then moves newest → no prompt
    fx.put(root, band_path, fx.band(
        "alpha", ["alpha item one: build the widget → alpha",
                  "alpha item two: review the plan",
                  "alpha item three: fresh off the press"],
        ["2026-11-03 — alpha seeded the fixture"]))
    commit_at(root, "alpha band moves", iso(t0 + timedelta(days=3)))
    p = bc.c2_prompt(repo, lane, band_path)
    check("band newest → no prompt", p is None)
    # a bulk-machinery touch of the band is not the band moving:
    # activity outside, then a 'conversion' commit on the band,
    # then the prompt must STILL fire (band_last excludes it)
    fx.put(root, "workspace/flows/alphaflow/notes.md",
           "# more alphaflow work\n")
    commit_at(root, "alphaflow work again", iso(t0 + timedelta(days=4)))
    fx.put(root, band_path, fx.band(
        "alpha", ["alpha item one: build the widget → alpha",
                  "alpha item two: review the plan",
                  "alpha item three: fresh off the press"],
        ["2026-11-03 — alpha seeded the fixture"]) + "\n<!-- swept -->\n")
    commit_at(root, "lane-memory: schema v3 conversion — alpha",
              iso(t0 + timedelta(days=5)))
    p = bc.c2_prompt(repo, lane, band_path)
    check("a bulk conversion touching the band does not count as "
          "the band moving → prompt still fires", p is not None)
    failed = [n for n, ok in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} C2 checks "
          f"pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
