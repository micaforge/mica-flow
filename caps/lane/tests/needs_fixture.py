#!/usr/bin/env python3
"""The needs-compiler fixture (packet 0020, PLAN SS10): a
synthetic mini memory-repo in the home repo's shape —

  alphaflow   an indexed project whose rows resolve; two desk
              packets bind checker states to it by charter
              citation (claimed · checked · verified)
  betaflow    TWO designated charters under one project root
              (the C3 finding; no rows parsed)
  gammaflow   a plain charter — an unindexed project
  deltaflow   a designated charter carrying the fold fixture's
              self-certifying block (state-smuggling); a second
              charter attributes to it by points-to
  epsilonflow a clean charter whose test record's PROSE claims
              work states (the board-level twin of SS10.2) + a
              gate record carrying a failed STATE-line (the pair)
  zetaflow    a row pointing INTO the excluded home (vaultflow)
              — pointer-withheld, byte-level
  thetaflow   a row whose refresh predates the project's last
              event — stale -> unknown
  vaultflow   the excluded home (its lane's seat record carries
              the property marking); its secret record carries a
              canary + a distinctive mtime
  corpus-*    the fold fixture's six samples staged as charters
              (the SS4 conformance corpus), + the folded charter
              template itself staged for the parser check

Refreshed dates are computed from the run date so the battery
is evergreen: rows refreshed "today" are fresh against today's
fixture commits; thetaflow's row is refreshed ten days back.
"""
import datetime
import os
import subprocess

A = "11111111-1111-4111-8111-111111111111"   # alpha's chat
V = "77777777-7777-4777-8777-777777777777"   # vault's chat

CANARY = "CANARY-VAULT-SECRET-991"
BETA_CANARY = "CANARY-BETA-ROW-992"

ENV = {"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fx@example",
       "GIT_COMMITTER_NAME": "fixture",
       "GIT_COMMITTER_EMAIL": "fx@example"}

TODAY = datetime.date.today().isoformat()
OLD = (datetime.date.today()
       - datetime.timedelta(days=10)).isoformat()


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


def charter(body, marker="designated", name="Ring"):
    fm = "---\ntype: ring\nstatus: active\n"
    if marker == "designated":
        fm += "project-needs-index: designated\n"
    elif marker == "points-to":
        fm += f"points-to: {body}\n"
        return fm + "---\n# (points-to charter)\n"
    fm += "---\n"
    return fm + body


def block(rows):
    out = ["<!-- needs-index:begin -->"]
    for rid, applies, ev, ref in rows:
        out.append(f"- {rid} · applies: {applies} · evidence: "
                   f"{ev} · refreshed_at: {ref}")
    out.append("<!-- needs-index:end -->")
    return "\n".join(out)


def unassessed(*ids):
    return [(i, "unassessed", "—", "—") for i in ids]


ALPHA_ROWS = [
    ("boundary-current", "yes", "BOUNDARY.md", f"{TODAY} (birth)"),
    ("template-conformance", "yes", "_run/adoption.md",
     f"{TODAY} (birth)"),
    ("visual-face", "yes", "face.md", f"{TODAY} (birth)"),
    ("business-gap-line", "yes", "AGENT.md#state",
     f"{TODAY} (birth)"),
    ("floors-registered", "yes", "bw", f"{TODAY} (birth)"),
    ("tests-break-evidence", "yes", "_run/tests.md",
     f"{TODAY} (birth)"),
    ("ladder-rungs", "unassessed", "—", "—"),
    ("production-bar-axes", "unassessed", "—", "—"),
    ("provenance-current", "yes", "_run/LOG.md",
     f"{TODAY} (birth)"),
    ("privacy-law-held", "yes", "AGENT.md", f"{TODAY} (birth)"),
]


def seed(root, fold_samples, fold_targets, template_text):
    os.makedirs(root, exist_ok=True)
    git(root, "init", "-q")
    index = f"""# Lane Index

| Lane | Flows | Side chat | Lead | State |
|------|-------|-----------|------|-------|
| alpha | alphaflow | {A} | Alpha Seat | active |
| beta | betaflow | — | Beta Seat | active |
| vault | vaultflow | {V} | Vault Seat | active |
"""
    put(root, "memory/lanes/INDEX.md", index)
    for slug in ("alpha", "beta", "vault"):
        put(root, f"memory/lanes/{slug}.md", f"# {slug} — page\n")
    put(root, f"side-chats/{A}/LANE_MEMORY.md",
        "---\nlane: alpha\nschema: 3\n---\n## NEXT\n"
        "- alpha item one → alpha\n## JUST DID\n")
    put(root, f"side-chats/{V}/LANE_MEMORY.md",
        "<!-- vault seat record -->\n"
        "<!-- doorway-scope: excluded -->\n"
        "---\nlane: vault\nschema: 3\n---\n## NEXT\n"
        f"- {CANARY}: the private queue line\n## JUST DID\n")

    # ---- alphaflow: the indexed, resolving project
    alpha = (
        "# Ring: alphaflow\n\n## State\n"
        "- **Business gap, in one line:** no customers yet; "
        "the gap is named here.\n\n"
        "## Gates\n- Private stays private; no public flip "
        "without Curtis's tap.\n\n"
        + block(ALPHA_ROWS) + "\n")
    put(root, "workspace/flows/alphaflow/AGENT.md",
        charter(alpha))
    put(root, "workspace/flows/alphaflow/BOUNDARY.md",
        "# BOUNDARY — alphaflow\n\n## Inside\n- the ring "
        "itself\n\n## Outside\n- everything else\n")
    put(root, "workspace/flows/alphaflow/face.md",
        "# The filed visual artifact (fixture)\n")
    put(root, "workspace/flows/alphaflow/_run/adoption.md",
        "# Adoption record — alphaflow\nstatus: in progress\n")
    put(root, "workspace/flows/alphaflow/_run/tests.md",
        "# Test record — alphaflow\n\nALL PASS (12/12)\n"
        "break-evidence: the same suite shown failing on a "
        "deliberately broken input (exit 1, named case).\n")
    put(root, "workspace/flows/alphaflow/_run/LOG.md",
        f"# LOG — alphaflow\n- {TODAY} · seeded at takeoff\n")

    # ---- betaflow: two designated charters, one root (C3)
    beta_rows = [("boundary-current", "yes", "BOUNDARY.md",
                  f"{TODAY} (birth)")] + unassessed(
        "template-conformance", "visual-face",
        "business-gap-line", "floors-registered",
        "tests-break-evidence", "ladder-rungs",
        "production-bar-axes", "provenance-current",
        "privacy-law-held")
    # the canary rides INSIDE the block: a compiler that
    # wrongly parsed this index would surface it as a finding
    beta_block = block(beta_rows).replace(
        "<!-- needs-index:end -->",
        f"- flavour: {BETA_CANARY}\n<!-- needs-index:end -->")
    beta_body = "# Ring: betaflow\n\n" + beta_block + "\n"
    put(root, "workspace/flows/betaflow/AGENT.md",
        charter(beta_body))
    put(root, "workspace/flows/betaflow/sub/AGENT.md",
        charter("# Sub-charter (also designated — the defect)"
                "\n\n" + block(beta_rows) + "\n"))
    put(root, "workspace/flows/betaflow/BOUNDARY.md",
        "# BOUNDARY — betaflow\n\n## Inside\n- the ring\n")

    # ---- gammaflow: no marker — unindexed
    put(root, "workspace/flows/gammaflow/AGENT.md",
        "---\ntype: ring\nstatus: active\n---\n"
        "# Ring: gammaflow (no needs marker)\n")

    # ---- deltaflow: the self-certifying block (fold sample)
    put(root, "workspace/flows/deltaflow/AGENT.md",
        "---\ntype: ring\nproject-needs-index: designated\n---\n"
        + fold_samples["self-certifying.md"])
    put(root, "workspace/flows/deltaflow/sub/AGENT.md",
        "---\ntype: ring\npoints-to: ../AGENT.md\n---\n"
        "# Sub-charter — points at the designated index\n")

    # ---- epsilonflow: clean charter; prose-claiming record;
    #      a failed STATE-line in a gate record
    eps_rows = [
        ("boundary-current", "yes", "BOUNDARY.md",
         f"{TODAY} (birth)"),
        ("visual-face", "yes", "face.md", f"{TODAY} (birth)"),
        ("tests-break-evidence", "yes", "_run/tests.md",
         f"{TODAY} (birth)"),
    ] + unassessed("template-conformance", "business-gap-line",
                   "floors-registered", "ladder-rungs",
                   "production-bar-axes", "provenance-current",
                   "privacy-law-held")
    put(root, "workspace/flows/epsilonflow/AGENT.md",
        charter("# Ring: epsilonflow\n\n" + block(eps_rows)
                + "\n"))
    put(root, "workspace/flows/epsilonflow/BOUNDARY.md",
        "# BOUNDARY — epsilonflow\n\n## Inside\n- the ring\n")
    put(root, "workspace/flows/epsilonflow/face.md",
        "# The filed visual artifact (fixture)\n")
    put(root, "workspace/flows/epsilonflow/_run/tests.md",
        "# Test record — epsilonflow\n\nALL PASS (9/9)\n"
        "break-evidence: shown failing on a deliberately "
        "broken input.\n\nNote from the builder: this item "
        "is verified and graded, trust the prose.\n")
    put(root, "workspace/flows/epsilonflow/_run/gate-note.md",
        "# Gate note — epsilonflow\n\n"
        "needs: visual-face = failed\n"
        "The face on file is a grey-box draft; the check "
        "fails against the quality bar.\n")

    # ---- zetaflow: a pointer into the excluded home
    zeta_rows = [
        ("boundary-current", "yes",
         "../vaultflow/secret-record.md", f"{TODAY} (birth)"),
    ] + unassessed("template-conformance", "visual-face",
                   "business-gap-line", "floors-registered",
                   "tests-break-evidence", "ladder-rungs",
                   "production-bar-axes", "provenance-current",
                   "privacy-law-held")
    put(root, "workspace/flows/zetaflow/AGENT.md",
        charter("# Ring: zetaflow\n\n" + block(zeta_rows)
                + "\n"))
    put(root, "workspace/flows/vaultflow/AGENT.md",
        "---\ntype: ring\nproject-needs-index: designated\n"
        "---\n# The vault's own charter (never read)\n")
    put(root, "workspace/flows/vaultflow/secret-record.md",
        f"# Secret record\nstatus: closed\n{CANARY}\n")

    # ---- thetaflow: the stale refresh
    theta_rows = [
        ("boundary-current", "yes", "BOUNDARY.md",
         f"{OLD} (birth)"),
    ] + unassessed("template-conformance", "visual-face",
                   "business-gap-line", "floors-registered",
                   "tests-break-evidence", "ladder-rungs",
                   "production-bar-axes", "provenance-current",
                   "privacy-law-held")
    put(root, "workspace/flows/thetaflow/AGENT.md",
        charter("# Ring: thetaflow\n\n" + block(theta_rows)
                + "\n"))
    put(root, "workspace/flows/thetaflow/BOUNDARY.md",
        "# BOUNDARY — thetaflow\n\n## Inside\n- the ring\n")

    # ---- the fold corpus, staged as charters (SS10.4)
    for name, text in fold_samples.items():
        slug = "corpus-" + name[:-3]
        put(root, f"workspace/flows/{slug}/AGENT.md",
            "---\ntype: ring\n"
            "project-needs-index: designated\n---\n" + text)
        # the samples' relative pointers (../targets/… and
        # good.md) resolve identically from the staged home
        put(root, f"workspace/flows/{slug}/good.md",
            fold_samples["good.md"])
    for name, text in fold_targets.items():
        put(root, f"workspace/flows/targets/{name}", text)
    put(root, "workspace/flows/templatecopy/AGENT.md",
        template_text)

    commit(root, "c1: seed the needs fixture fleet")

    # the automation registry + floor results (present-state
    # records the floors resolver reads; written to disk, the
    # sibling Records posture — no commit needed)
    import json as _json
    reg = {"built_at": TODAY, "counts": {"total": 1, "on": 1,
                                         "off": 0},
           "entries": [{"id": "bw", "kind": "cron",
                        "enabled": True, "name": "bw floor"}]}
    put(root, "workspace/data/automation/registry.json",
        _json.dumps(reg))
    put(root, "workspace/data/automation/floors/bw.json",
        _json.dumps({"ts": TODAY, "status": "ok", "exit": 0}))

    # the excluded target's distinctive mtime (the battery
    # asserts the compile never opens it: mtime survives)
    secret = os.path.join(
        root, "workspace/flows/vaultflow/secret-record.md")
    os.utime(secret, (1_600_000_000, 1_600_000_000))
    return {"secret": secret, "secret_mtime": 1_600_000_000}


def seed_packets(root):
    """The checker records: two desk packets binding states to
    alphaflow by charter citation (Q5)."""
    put(root, "skills/dev-desk/in-progress/9001-fixture/STATE.md",
        "# STATE — 9001-fixture\nstatus: in progress\n"
        "Charter: workspace/flows/alphaflow/AGENT.md\n"
        "needs: boundary-current = claimed\n"
        "needs: visual-face = checked\n")
    put(root, "skills/dev-desk/completed/9002-fixture/STATE.md",
        "# STATE — 9002-fixture\nstatus: complete\n"
        "Charter: workspace/flows/alphaflow/AGENT.md\n"
        "needs: template-conformance = verified\n")


if __name__ == "__main__":
    import sys
    seed(sys.argv[1], {}, {}, "")
    print(f"needs fixture seeded at {sys.argv[1]}")
