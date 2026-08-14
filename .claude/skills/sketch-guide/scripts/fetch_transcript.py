#!/usr/bin/env python3
"""Fetch a YouTube video's transcript as clean, timestamped text.

Why this needs a tool at all: YouTube's caption URLs are gated behind a
proof-of-origin token, so the obvious approaches all return zero bytes —
scraping `captionTracks` out of the watch page, hitting `api/timedtext`, and
even yt-dlp on its default `web` client. The `android` player client still
serves captions without a token, which is what this uses. If that stops
working, the symptom is "no subtitles for the requested languages", and the
place to look is yt-dlp's PO-Token guide.

First run needs a one-off local install (a venv inside the repo, gitignored,
nothing touches the system):

    python3 .claude/skills/sketch-guide/scripts/fetch_transcript.py --setup

Then:

    python3 .claude/skills/sketch-guide/scripts/fetch_transcript.py sojFWKrv5OM
    python3 .claude/skills/sketch-guide/scripts/fetch_transcript.py "https://youtu.be/sojFWKrv5OM" --chunk 15

What it's for: confirming a video actually teaches what you're about to claim
it teaches, checking it's Godot 4 rather than Godot 3, and finding the
timestamp worth pointing at. It is research material, not copy — write the
guide in your own words and never paste transcript text into it.
"""

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
VENV = os.path.join(REPO, ".tools", "venv")
VENV_BIN = os.path.join(VENV, "bin", "yt-dlp")

# The one client that still serves captions without a proof-of-origin token.
CLIENT_ARGS = ["--extractor-args", "youtube:player_client=android"]


def find_ytdlp():
    return shutil.which("yt-dlp") or (VENV_BIN if os.path.exists(VENV_BIN) else None)


def setup():
    print(f"Creating a venv at {VENV} …")
    os.makedirs(os.path.dirname(VENV), exist_ok=True)
    subprocess.run([sys.executable, "-m", "venv", VENV], check=True)
    pip = os.path.join(VENV, "bin", "pip")
    subprocess.run([pip, "-q", "install", "--upgrade", "pip", "yt-dlp"], check=True)
    v = subprocess.run([VENV_BIN, "--version"], capture_output=True, text=True).stdout.strip()
    print(f"yt-dlp {v} ready.\n\n.tools/ is gitignored, so this stays on this machine.")
    print("Keep it current — YouTube changes often and yt-dlp tracks it:")
    print(f"  {pip} install --upgrade yt-dlp")
    return 0


def video_id(s):
    if re.fullmatch(r"[\w-]{11}", s):
        return s
    m = re.search(r"(?:v=|youtu\.be/|/embed/|/shorts/)([\w-]{11})", s)
    return m.group(1) if m else None


def parse_vtt(raw):
    """VTT → [(seconds, text)], with auto-caption roll-up removed.

    Auto-generated captions repeat the previous line as the next cue's first
    line, so a naive parse gives you every sentence two or three times.
    """
    cues = []
    for block in re.split(r"\n\n+", raw):
        m = re.search(r"(\d\d):(\d\d):(\d\d)\.\d+\s+-->", block)
        if not m:
            continue
        start = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
        body = block.split("-->", 1)[1].split("\n", 1)
        text = body[1] if len(body) > 1 else ""
        text = re.sub(r"<[^>]+>", "", text)          # word-level timing tags
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            cues.append((start, text))

    out = []
    for start, text in cues:
        if out:
            prev = out[-1][1]
            if text == prev:
                continue
            if text.startswith(prev):                # rolling caption grew
                out[-1] = (out[-1][0], text)
                continue
            if prev.endswith(text):                  # already absorbed
                continue
        out.append((start, text))
    return out


def chunk(cues, seconds):
    """Group cues into readable blocks, each tagged with a citable timestamp."""
    blocks, cur, cur_start = [], [], None
    for start, text in cues:
        if cur_start is None:
            cur_start = start
        if start - cur_start >= seconds and cur:
            blocks.append((cur_start, " ".join(cur)))
            cur, cur_start = [], start
        cur.append(text)
    if cur:
        blocks.append((cur_start, " ".join(cur)))
    return blocks


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", nargs="?", help="video ID or any YouTube URL")
    ap.add_argument("--setup", action="store_true", help="install yt-dlp into a repo-local venv, then exit")
    ap.add_argument("--chunk", type=int, default=30, help="seconds per timestamped block (default 30)")
    args = ap.parse_args()

    if args.setup:
        return setup()
    if not args.video:
        ap.error("give a video ID or URL (or --setup for the one-off install)")

    vid = video_id(args.video)
    if not vid:
        print(f"could not find a video ID in {args.video!r}", file=sys.stderr)
        return 2

    ytdlp = find_ytdlp()
    if not ytdlp:
        print("yt-dlp not found. Run this once:\n"
              f"  python3 {os.path.relpath(__file__, REPO)} --setup", file=sys.stderr)
        return 3

    with tempfile.TemporaryDirectory() as tmp:
        cmd = [ytdlp, "--skip-download", "--write-auto-subs", "--write-subs",
               "--sub-langs", "en.*", "--sub-format", "vtt", "--write-info-json",
               *CLIENT_ARGS, "-o", os.path.join(tmp, "%(id)s"),
               f"https://www.youtube.com/watch?v={vid}"]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        subs = sorted(glob.glob(os.path.join(tmp, "*.vtt")))
        if not subs:
            print("No captions came back. Two likely causes:\n"
                  "  1. the video genuinely has none, or\n"
                  "  2. the android-client workaround has stopped working — see\n"
                  "     https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide\n",
                  file=sys.stderr)
            tail = [ln for ln in proc.stderr.splitlines() if "WARNING" in ln or "ERROR" in ln]
            print("\n".join(tail[-4:]), file=sys.stderr)
            return 4

        # Prefer a human-written track over the auto-generated one.
        subs.sort(key=lambda p: ("orig" in p, "auto" in p, len(p)))
        raw = open(subs[0], encoding="utf-8").read()

        title = channel = None
        dur = 0
        info = glob.glob(os.path.join(tmp, "*.info.json"))
        if info:
            meta = json.load(open(info[0], encoding="utf-8"))
            title, channel, dur = meta.get("title"), meta.get("channel"), int(meta.get("duration") or 0)

    cues = parse_vtt(raw)
    if not cues:
        print("captions downloaded but parsed to nothing — check the VTT format", file=sys.stderr)
        return 5

    head = f"# {title or vid}"
    if channel:
        head += f" — {channel}"
    if dur:
        head += f" ({dur // 60}:{dur % 60:02d})"
    print(head)
    print(f"# https://www.youtube.com/watch?v={vid}")
    print(f"# {len(cues)} cues, {'auto-generated' if 'orig' in subs[0] or 'auto' in subs[0] else 'human-written'} captions")
    print("# Research material — verify claims and find timestamps. Do not paste into a guide.\n")

    for start, text in chunk(cues, args.chunk):
        print(f"[{start // 60:02d}:{start % 60:02d}] {text}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
