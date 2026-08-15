#!/usr/bin/env python3
"""Rank candidate YouTube videos by reach, so prep picks aren't a matter of taste.

Relevance still decides — a perfect 900-view video beats a vaguely related
million-view one, and a popular Godot 3 tutorial is worse than useless. But
among videos that genuinely teach the thing, reach is a real signal: it means
more people found it clear, and it usually means better audio, editing and
pacing. Left to itself, a search will happily surface a 1,200-view video and
this makes that visible before it ships.

Usage:
    python3 .claude/skills/sketch-guide/scripts/video_stats.py ID [ID ...]
    python3 .claude/skills/sketch-guide/scripts/video_stats.py --guide guides/a1-good-movement.html

Feed it every candidate from a search, read the table, then judge relevance
yourself — normally by pulling the transcript of the top two or three.
"""

import argparse
import re
import sys
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124 Safari/537.36")


def human(n):
    if n is None:
        return "?"
    for limit, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "k")):
        if n >= limit:
            v = n / limit
            return f"{v:.1f}{suffix}" if v < 10 else f"{v:.0f}{suffix}"
    return str(n)


def stats(vid):
    req = urllib.request.Request(f"https://www.youtube.com/watch?v={vid}",
                                 headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    try:
        page = urllib.request.urlopen(req, timeout=25).read(3_000_000).decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return {"id": vid, "error": f"{type(e).__name__}: {e}"}

    def grab(pattern, cast=str):
        m = re.search(pattern, page)
        return cast(m.group(1)) if m else None

    return {
        "id": vid,
        "title": grab(r'<meta name="title" content="([^"]*)"') or "?",
        "channel": grab(r'"ownerChannelName":"([^"]*)"') or "?",
        "date": (grab(r'"uploadDate":"([^"]*)"') or "?")[:10],
        "seconds": grab(r'"lengthSeconds":"(\d+)"', int),
        "views": grab(r'"viewCount":"(\d+)"', int),
        "likes": grab(r'"likeCount":"(\d+)"', int),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", help="video IDs or URLs")
    ap.add_argument("--guide", help="rank the videos already linked in a guide file")
    args = ap.parse_args()

    ids = []
    if args.guide:
        with open(args.guide, encoding="utf-8") as fh:
            ids += re.findall(r"youtube\.com/watch\?v=([\w-]{11})", fh.read())
    for raw in args.ids:
        m = re.search(r"(?:v=|youtu\.be/|/shorts/)([\w-]{11})", raw)
        ids.append(m.group(1) if m else raw)

    ids = list(dict.fromkeys(ids))
    if not ids:
        ap.error("give at least one video ID, or --guide <file>")

    rows = [stats(v) for v in ids]
    ok = [r for r in rows if "error" not in r]
    ok.sort(key=lambda r: r.get("views") or 0, reverse=True)

    print(f"\n{'views':>7}  {'likes':>6}  {'like/1k':>7}  {'length':>6}  {'date':10}  channel / title")
    print("  " + "─" * 96)
    for r in ok:
        v, l, s = r.get("views"), r.get("likes"), r.get("seconds") or 0
        ratio = f"{(l / v * 1000):.0f}" if v and l else "?"
        print(f"{human(v):>7}  {human(l):>6}  {ratio:>7}  {s // 60:>3}:{s % 60:02d}  {r['date']:10}  "
              f"{r['channel']}\n{'':38}{r['title'][:76]}\n{'':38}https://www.youtube.com/watch?v={r['id']}")

    for r in rows:
        if "error" in r:
            print(f"\n  FAILED  {r['id']} — {r['error']}")

    if ok:
        top = ok[0].get("views") or 0
        weak = [r for r in ok if (r.get("views") or 0) * 50 < top]
        if weak:
            print("\n  Much smaller reach than the leader — keep only if clearly more relevant:")
            for r in weak:
                print(f"    {human(r.get('views')):>7} views  {r['channel']} — {r['title'][:60]}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
