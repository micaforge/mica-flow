#!/usr/bin/env python3
"""The stage-1 fixture: a synthetic mini memory-repo (lanes alpha..
eta) in the home repo's shape — INDEX, seat records, pointer stubs,
an excluded lane (beta) whose seat record carries the property and
whose files carry unique canaries, an included lane (delta) pointing
INTO beta's home, an assignment chain (epsilon), a transition lane
(zeta), and an unfollowable stub (eta). Commits land in stages so
the battery can drive compiles between them:
  c1 seed · c2 flips · c3 flip + zeta marking · c4 unblock.
"""
import os
import subprocess

A = "11111111-1111-4111-8111-111111111111"
B = "22222222-2222-4222-8222-222222222222"
G = "33333333-3333-4333-8333-333333333333"
D = "44444444-4444-4444-8444-444444444444"
E = "55555555-5555-4555-8555-555555555555"
Z = "66666666-6666-4666-8666-666666666666"

CANARIES = ["CANARY-BETA-QUEUE-771", "CANARY-BETA-DID-772",
            "CANARY-BETA-BODY-773", "CANARY-BETA-FLOW-774"]

ENV = {"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fx@example",
       "GIT_COMMITTER_NAME": "fixture",
       "GIT_COMMITTER_EMAIL": "fx@example"}


def git(root, *args):
    env = dict(os.environ)
    env.update(ENV)
    subprocess.run(["git", "-C", root, *args], check=True, env=env,
                   capture_output=True, text=True)


def put(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


def commit(root, msg):
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", msg)


def band(lane, queue, did=None, extra=""):
    did = did or []
    q = "\n".join(f"- {x}" for x in queue)
    d = "\n".join(f"- {x}" for x in did)
    return (f"---\ntype: lane-memory\nlane: {lane}\nowner: {lane} seat\n"
            f"updated: 2026-11-04\nstatus: active\nschema: 3\ncap: 300\n"
            f"---\n## NEXT\n{q}\n## JUST DID\n{d}\n{extra}")


def seed(root):
    os.makedirs(root, exist_ok=True)
    git(root, "init", "-q")
    index = """# Lane Index

| Lane | Flows | Side chat | Lead | State |
|------|-------|-----------|------|-------|
| alpha | alphaflow | %s | Alpha Seat | active |
| beta | betaflow | %s | Beta Seat | active |
| gamma | gamma | — | Gamma Seat | active |
| delta | deltaflow | %s | Delta Seat | active |
| epsilon | epsilonflow | %s | Epsilon Seat | active |
| zeta | zetaflow | %s | Zeta Seat | active |
| eta | eta | — | (chat-less) | active |
""" % (A, B, D, E, Z)
    put(root, "memory/lanes/INDEX.md", index)
    for slug in ("alpha", "beta", "gamma", "delta", "epsilon", "zeta",
                 "eta"):
        put(root, f"memory/lanes/{slug}.md", f"# {slug} — lane page\n")
    put(root, f"side-chats/{A}/LANE_MEMORY.md", band(
        "alpha",
        ["alpha item one: build the widget → alpha",
         "alpha item two: review the plan"],
        ["2026-11-03 — alpha seeded the fixture"]))
    beta = ("<!-- beta seat record -->\n"
            "<!-- doorway-scope: excluded -->\n"
            + band("beta",
                   ["CANARY-BETA-QUEUE-771: the private thing → beta"],
                   ["CANARY-BETA-DID-772: a private act landed"])
            + "\nBody text: CANARY-BETA-BODY-773\n")
    put(root, f"side-chats/{B}/LANE_MEMORY.md", beta)
    put(root, "workspace/flows/betaflow/LANE_MEMORY.md", band(
        "beta", ["CANARY-BETA-FLOW-774: flow-side private item"]))
    # gamma: chat-less in the INDEX; its flow file is a pointer stub
    # to the seat file under side-chats/<G>/ (the followed case).
    put(root, "workspace/flows/gamma/LANE_MEMORY.md",
        "---\ntype: lane-memory-pointer\nlane: gamma\n"
        "owner: Gamma Seat\n---\nQueue held in the seat file: "
        f"`side-chats/{G}/LANE_MEMORY.md`\n")
    put(root, f"side-chats/{G}/LANE_MEMORY.md", band(
        "gamma",
        ["gamma item one: file the report → gamma",
         "gamma item two: sweep the shelf"],
        ["2026-11-02 — gamma stood up"]))
    put(root, f"side-chats/{D}/LANE_MEMORY.md", band(
        "delta",
        [f"delta item one: unblock the archive — blocked-on: "
         f"side-chats/{B}/records/thing.md → alpha",
         "delta item three: polish the door"],
        []))
    put(root, f"side-chats/{E}/LANE_MEMORY.md", band(
        "epsilon",
        ["epsilon item one: carry the parcel → alpha"], []))
    put(root, f"side-chats/{Z}/LANE_MEMORY.md", band(
        "zeta", ["zeta item one: hold the line → zeta"], []))
    # eta: chat-less; its stub target sits outside the repo entirely
    put(root, "workspace/flows/eta/LANE_MEMORY.md",
        "---\ntype: lane-memory-pointer\nlane: eta\n"
        "owner: Eta Seat\n---\nQueue held in the seat file: "
        "`~/outside/eta-seat.md`\n")
    commit(root, "c1: seed the fixture fleet")


def c2(root):
    put(root, f"side-chats/{E}/LANE_MEMORY.md", band(
        "epsilon",
        ["epsilon item one: carry the parcel → delta"], []))
    put(root, f"side-chats/{D}/LANE_MEMORY.md", band(
        "delta",
        [f"delta item one: unblock the archive — blocked-on: "
         f"side-chats/{B}/records/thing.md → alpha",
         "delta item two: take the hand-off → alpha",
         "delta item three: polish the door"], []))
    commit(root, "c2: epsilon hands to delta; delta takes an item")


def c3(root):
    put(root, f"side-chats/{E}/LANE_MEMORY.md", band(
        "epsilon",
        ["epsilon item one: carry the parcel → gamma"], []))
    zeta = open(os.path.join(root, f"side-chats/{Z}/LANE_MEMORY.md")) \
        .read()
    put(root, f"side-chats/{Z}/LANE_MEMORY.md",
        "<!-- doorway-scope: excluded -->\n" + zeta)
    commit(root, "c3: epsilon hands to gamma; zeta's posture changes")


def c4(root):
    put(root, f"side-chats/{D}/LANE_MEMORY.md", band(
        "delta",
        ["delta item one: unblock the archive → alpha",
         "delta item two: take the hand-off → alpha",
         "delta item three: polish the door"], []))
    commit(root, "c4: delta's blocker clears")


if __name__ == "__main__":
    import sys
    seed(sys.argv[1])
    print(f"fixture seeded at {sys.argv[1]}")
