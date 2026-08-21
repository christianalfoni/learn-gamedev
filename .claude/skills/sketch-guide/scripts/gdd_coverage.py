#!/usr/bin/env python3
"""Report which parts of the design document have assignments, and which don't.

This is the input to deriving new work. Run it before proposing assignments so
the proposal is grounded in what the document actually says rather than in what
you remember it saying.

    python3 .claude/skills/sketch-guide/scripts/gdd_coverage.py
    python3 .claude/skills/sketch-guide/scripts/gdd_coverage.py --since HEAD~1

`--since` diffs gdd.md against a git revision and marks the sections that
changed — those are usually exactly the ones that need new assignments.
"""

import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
GDD = os.path.join(ROOT, "gdd.md")
INDEX = os.path.join(ROOT, "index.html")


def parse_gdd(md):
    """-> [(area, id, title, body)] for every ### section."""
    sections, area, cur = [], "", None
    for line in md.split("\n"):
        h3 = re.match(r"^###\s+(.*)$", line)
        h2 = re.match(r"^##\s+(.*)$", line)
        if h3:
            raw = h3.group(1)
            m = re.search(r"\{#([a-z0-9-]+)\}\s*$", raw, re.I)
            title = re.sub(r"\{#[a-z0-9-]+\}\s*$", "", raw, flags=re.I).strip()
            sid = m.group(1) if m else re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            cur = {"area": area, "id": sid, "title": title, "body": ""}
            sections.append(cur)
        elif h2:
            area = re.sub(r"\{#[a-z0-9-]+\}\s*$", "", h2.group(1), flags=re.I).strip()
            cur = None
        elif cur is not None:
            cur["body"] += line + "\n"
    return sections


def described(body):
    """Prose that isn't an italic prompt, a blockquote, or an empty bullet."""
    s = re.sub(r"^>.*$", "", body, flags=re.M)
    s = re.sub(r"\*[^*]*\*", "", s)
    s = re.sub(r"^[-*]\s*$", "", s, flags=re.M)
    return bool(s.strip())


def parse_assignments(html):
    """-> [(id, title, [gdd ids])] from the ASSIGNMENTS array."""
    out = []
    block = re.search(r"const ASSIGNMENTS = \[(.*?)\n  \];", html, re.S)
    if not block:
        return out
    # Split on blank lines rather than matching entry-to-entry: the final entry
    # has no trailing blank line, and a lookahead-based match silently drops it.
    for entry in re.split(r"\n\s*\n", block.group(1)):
        aid = re.search(r'id:\s*"([^"]+)"', entry)
        title = re.search(r'\bt:\s*"([^"]+)"', entry)
        if not aid or not title:
            continue
        gdd = re.search(r"gdd:\s*\[([^\]]*)\]", entry)
        refs = re.findall(r'"([^"]+)"', gdd.group(1)) if gdd else []
        out.append((aid.group(1), title.group(1), refs))
    return out


def changed_sections(since):
    try:
        diff = subprocess.run(["git", "-C", ROOT, "diff", since, "--", "gdd.md"],
                              capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError as e:
        print(f"git diff failed: {e}", file=sys.stderr)
        return set()
    changed, cur = set(), None
    for line in diff.split("\n"):
        h = re.match(r"^[+ ]###\s+(.*)$", line)
        if h:
            m = re.search(r"\{#([a-z0-9-]+)\}", h.group(1))
            cur = m.group(1) if m else None
        elif line.startswith("+") and not line.startswith("+++") and cur:
            if line[1:].strip():
                changed.add(cur)
    return changed


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", help="git revision to diff gdd.md against (e.g. HEAD~1)")
    args = ap.parse_args()

    if not os.path.exists(GDD):
        print("no gdd.md at the repo root", file=sys.stderr)
        return 2

    sections = parse_gdd(open(GDD, encoding="utf-8").read())
    assignments = parse_assignments(open(INDEX, encoding="utf-8").read())
    changed = changed_sections(args.since) if args.since else set()

    by_section = {}
    for aid, title, refs in assignments:
        for r in refs:
            by_section.setdefault(r, []).append((aid, title))

    known = {s["id"] for s in sections}
    ready, blank_, covered = [], [], []

    for s in sections:
        has = by_section.get(s["id"], [])
        # An assignment counts as coverage whether or not the prose is written —
        # otherwise existing work vanishes from the report the moment a section
        # is still a placeholder.
        if has:
            covered.append((s, has))
        elif described(s["body"]):
            ready.append(s)
        else:
            blank_.append(s)

    print(f"\n  {len(sections)} sections · {len(covered)} covered · {len(ready)} ready to derive · "
          f"{len(blank_)} not described\n")

    if changed:
        print("  CHANGED since " + args.since + " — derive from these first")
        for s in sections:
            if s["id"] in changed:
                mark = "covered" if by_section.get(s["id"]) else "NO ASSIGNMENT"
                print(f"    #{s['id']:<18} {s['area']} · {s['title']}  [{mark}]")
        print()

    if ready:
        print("  READY TO DERIVE — described, but nothing built from them")
        for s in ready:
            first = " ".join(re.sub(r"\*[^*]*\*", "", s["body"]).split())[:72]
            print(f"    #{s['id']:<18} {s['area']} · {s['title']}")
            if first:
                print(f"    {'':19} {first}…")
        print()

    if covered:
        print("  COVERED")
        for s, has in covered:
            names = ", ".join(f"{a} {t}" for a, t in has)
            print(f"    #{s['id']:<18} {names}")
        print()

    if blank_:
        print("  NOT DESCRIBED YET — nothing to derive from")
        print("    " + ", ".join("#" + s["id"] for s in blank_))
        print()

    broken = [(aid, r) for aid, _, refs in assignments for r in refs if r not in known]
    if broken:
        print("  BROKEN REFERENCES — assignment points at a section that no longer exists")
        for aid, r in broken:
            print(f"    {aid} -> #{r}")
        print()
        return 1

    orphans = [(aid, t) for aid, t, refs in assignments if not refs]
    if orphans:
        print("  NOT TIED TO THE DOCUMENT")
        for aid, t in orphans:
            print(f"    {aid} {t}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
