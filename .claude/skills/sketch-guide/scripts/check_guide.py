#!/usr/bin/env python3
"""Validate a sketch guide before it ships.

Every check here exists because the thing it catches has actually gone wrong:
an unescaped `>` swallowing half a code block, a step count in the progress rail
that no longer matches reality, a guide written but never linked from the
sketchbook, a video that has since been taken down.

Usage:
    python3 .claude/skills/sketch-guide/scripts/check_guide.py guides/a1-good-movement.html
    python3 .claude/skills/sketch-guide/scripts/check_guide.py guides/a1-good-movement.html --links

Exits non-zero if anything is broken, so it can gate a commit.
"""

import argparse
import html
import os
import re
import sys
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

errors = []
warnings = []
notes = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def note(msg):
    notes.append(msg)


# ── structure ───────────────────────────────────────────────────────────────

def check_structure(src):
    for tag in ("<!DOCTYPE html>", "<html lang=", "</head>", "<body", "</body>", "</html>"):
        n = src.count(tag)
        if n != 1:
            err(f"expected exactly one {tag!r}, found {n}")

    for meta in ('name="viewport"', 'charset="utf-8"', 'name="color-scheme"'):
        if meta not in src:
            warn(f"missing <meta {meta}> — the page needs it as a standalone document on Pages")

    if "<title>" not in src:
        err("no <title> — it names the browser tab and the bookmark")


def check_body_attrs(src, path):
    m = re.search(r"<body([^>]*)>", src)
    if not m:
        err("no <body> tag")
        return
    attrs = m.group(1)

    guide = re.search(r'data-guide="([^"]+)"', attrs)
    sketch = re.search(r'data-sketch="([^"]+)"', attrs)

    if not guide:
        err('<body> is missing data-guide — assets/guide.js keys step progress on it')
    else:
        stem = os.path.splitext(os.path.basename(path))[0]
        if guide.group(1) != stem:
            err(f'data-guide="{guide.group(1)}" should match the filename stem "{stem}"')

    if not sketch:
        err('<body> is missing data-sketch — without it the "Log this session" button does nothing')
    elif not re.fullmatch(r"[A-Z][1-9][0-9]?", sketch.group(1)):
        warn(f'data-sketch="{sketch.group(1)}" does not look like an assignment ID (a letter plus a number)')


def check_assets(src, path):
    base = os.path.dirname(os.path.abspath(path))
    for rel in re.findall(r'(?:href|src)="((?:\.\./)+[^"]*)"', src):
        # Strip the fragment and query: "../#e-A4" is a link to the sketchbook's
        # A4 card, not a file called "#e-A4".
        clean = rel.split("#")[0].split("?")[0]
        if not clean or clean.endswith("/"):
            continue
        target = os.path.normpath(os.path.join(base, clean))
        if not os.path.exists(target):
            err(f"relative asset does not exist on disk: {rel}")

    if "assets/guide.css" not in src:
        err("guide.css is not linked — the page will render unstyled")
    if "assets/guide.js" not in src:
        err("guide.js is not linked — no highlighting, no progress, no copy buttons")


# ── code blocks ─────────────────────────────────────────────────────────────

def check_code_blocks(src):
    figs = re.findall(r'<figure class="code"[^>]*>(.*?)</figure>', src, re.S)
    if not figs:
        note("no code blocks — fine for an Aseprite or listening sketch, suspicious for Godot")

    for i, fig in enumerate(figs):
        if "<figcaption>" not in fig:
            err(f"code block {i}: no <figcaption> — the reader can't tell which file this is")
        if 'class="copy"' not in fig:
            err(f"code block {i}: no copy button")

        code = re.search(r"<code>(.*?)</code>", fig, re.S)
        if not code:
            err(f"code block {i}: no <code> element")
            continue
        body = code.group(1)

        if "<" in body:
            err(f"code block {i}: unescaped '<' — write &lt;, or the browser eats the rest of the block")
        if ">" in body:
            warn(f"code block {i}: bare '>' — write &gt; for consistency (GDScript's -> is easy to miss)")

        space_indented = [ln for ln in body.split("\n") if re.match(r"^ {2,}\S", ln)]
        if space_indented:
            warn(f"code block {i}: {len(space_indented)} space-indented line(s) — Godot's editor uses tabs")


# ── steps ───────────────────────────────────────────────────────────────────

def check_steps(src):
    steps = re.findall(r'<section class="step" id="([^"]+)">(.*?)</section>', src, re.S)
    if not steps:
        err("no steps found — a guide without steps is a blog post")
        return 0

    for i, (sid, body) in enumerate(steps, start=1):
        expected = f"s{i}"
        if sid != expected:
            err(f'step {i} has id="{sid}", expected id="{expected}" (guide.js counts them in order)')
        if 'class="step-check"' not in body:
            err(f"step {sid}: no check button, so it can never be marked done")
        if 'class="step-time"' not in body:
            warn(f"step {sid}: no time estimate — that's how he decides whether to start tonight")

    n = len(steps)
    if n < 4:
        warn(f"{n} steps — under about 6 the progress rail stops feeling like progress")
    if n > 12:
        warn(f"{n} steps — over about 10 it stops feeling achievable in one sitting")

    rail = re.search(r'<span class="pct">\s*0/(\d+) steps\s*</span>', src)
    if not rail:
        warn("progress rail is missing its initial '0/N steps' text")
    elif int(rail.group(1)) != n:
        err(f"progress rail says 0/{rail.group(1)} steps but there are {n} — update the rail")

    return n


def check_footer(src, n_steps):
    if 'id="logSession"' not in src:
        err('no "Log this session" button — finishing the guide should reach the sketchbook')
    if "data-when-finished" not in src:
        warn("no data-when-finished block — nothing confirms the guide is complete")

    m = re.search(r"<b>All (\w+) steps done\.</b>", src)
    if m and n_steps:
        words = {"four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
                 "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
        got = words.get(m.group(1).lower())
        if got is None and m.group(1).isdigit():
            got = int(m.group(1))
        if got is not None and got != n_steps:
            err(f'footer says "All {m.group(1)} steps done" but there are {n_steps}')


# ── repo wiring ─────────────────────────────────────────────────────────────

def check_registered(path):
    root = os.path.dirname(os.path.dirname(os.path.abspath(path)))
    index = os.path.join(root, "index.html")
    if not os.path.exists(index):
        note("no index.html next to guides/ — skipping the registration check")
        return
    rel = "guides/" + os.path.basename(path)
    with open(index, encoding="utf-8") as fh:
        if f'guide: "{rel}"' not in fh.read():
            err(f'not registered in index.html — add  guide: "{rel}",  to that sketch in SKETCHES')


# ── links ───────────────────────────────────────────────────────────────────

def check_video_claims(src, url, label, title_m, secs_m, ch_m):
    """Compare what the guide claims about a video against what YouTube says.

    Getting a runtime wrong is a small lie with real cost: he budgets a session
    around "5 minutes of prep" and loses forty.
    """
    block = re.search(r'<a class="vid[^"]*" href="' + re.escape(url) + r'"[^>]*>(.*?)</a>', src, re.S)
    if not block:
        return
    body = html.unescape(block.group(1))

    if secs_m:
        actual = int(secs_m.group(1))
        claim = re.search(r'<span class="len">\s*(?:(\d+):)?(\d+):(\d{2})', block.group(1))
        if claim:
            h = int(claim.group(1) or 0)
            claimed = h * 3600 + int(claim.group(2)) * 60 + int(claim.group(3))
            if abs(claimed - actual) > 2:
                err(f"guide claims {claimed // 60}:{claimed % 60:02d} for {url} "
                    f"but it runs {actual // 60}:{actual % 60:02d}")
        else:
            warn(f"no runtime shown for {url} — he needs it to budget the session")

    if ch_m:
        # Channel names sometimes carry trailing spaces or non-breaking ones.
        channel = " ".join(html.unescape(ch_m.group(1)).split())
        if channel.lower() not in " ".join(body.split()).lower():
            warn(f'guide does not credit "{channel}" for {url} — check the byline')


def check_links(src):
    urls = sorted(set(re.findall(r'href="(https?://[^"]+)"', src)))
    if not urls:
        note("no external links")
        return

    for url in urls:
        if "google.com/search" in url or "youtube.com/results" in url:
            err(f"search URL — the reason guides exist is to not ship these: {url}")
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as resp:
                code = resp.status
                if "youtube.com/watch" in url:
                    # The metadata sits well past the first megabyte of a watch
                    # page, so a partial read finds nothing. Read the lot.
                    page = resp.read(3_000_000).decode("utf-8", "replace")
                    t = re.search(r'<meta name="title" content="([^"]*)"', page)
                    ch = re.search(r'"ownerChannelName":"([^"]*)"', page)
                    secs = re.search(r'"lengthSeconds":"(\d+)"', page)
                    views = re.search(r'"viewCount":"(\d+)"', page)
                    likes = re.search(r'"likeCount":"(\d+)"', page)
                    if not t:
                        warn(f"reachable but no title found — is {url} still a public video?")
                    label = t.group(1) if t else "?"
                    if ch:
                        label += f"  · {ch.group(1)}"
                    if secs:
                        s = int(secs.group(1))
                        label += f"  [{s // 60}:{s % 60:02d}]"
                    if views:
                        v = int(views.group(1))
                        label += f"  · {v:,} views"
                        if likes:
                            label += f", {int(likes.group(1)):,} likes"
                        # Reach isn't the whole story, but a few hundred views usually
                        # means a search result nobody vetted rather than a good pick.
                        if v < 5000:
                            warn(f"only {v:,} views — {url}\n        "
                                 f"rank the alternatives with video_stats.py and keep this only if "
                                 f"it is clearly more relevant than anything bigger")
                    note(f"{code}  {url}\n        → {label}")
                    check_video_claims(src, url, label, t, secs, ch)
                else:
                    note(f"{code}  {url}")
        except urllib.error.HTTPError as e:
            err(f"HTTP {e.code} — {url}")
        except Exception as e:  # noqa: BLE001 — network flakiness shouldn't crash the check
            err(f"unreachable ({type(e).__name__}) — {url}")


# ── main ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Validate a sketch guide.")
    ap.add_argument("guide", help="path to the guide HTML file")
    ap.add_argument("--links", action="store_true",
                    help="also fetch every external URL (slow, and the check that matters most)")
    args = ap.parse_args()

    if not os.path.exists(args.guide):
        print(f"no such file: {args.guide}", file=sys.stderr)
        return 2

    with open(args.guide, encoding="utf-8") as fh:
        src = fh.read()

    check_structure(src)
    check_body_attrs(src, args.guide)
    check_assets(src, args.guide)
    check_code_blocks(src)
    n = check_steps(src)
    check_footer(src, n)
    check_registered(args.guide)
    if args.links:
        check_links(src)

    print(f"\n{os.path.basename(args.guide)} — {n} steps\n")
    for label, items in (("NOTE", notes), ("WARN", warnings), ("ERROR", errors)):
        for item in items:
            print(f"  {label:5} {item}")

    print()
    if errors:
        print(f"{len(errors)} error(s), {len(warnings)} warning(s) — fix the errors before pushing.")
        return 1
    print(f"clean — {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
