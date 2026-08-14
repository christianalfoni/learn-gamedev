---
name: sketch-guide
description: Write a step-by-step practice guide for a Gamedev Sketchbook sketch (Godot 4, Aseprite, Audacity, FL Studio) in the learn-gamedev repo. Use this whenever Christian asks for a guide, walkthrough, tutorial or "write-up" for a sketch — by ID (A1–F4), by name ("the hitstop one"), or vaguely ("write the next couple of guides", "can you do the pixel art ones"). Also use it when editing, extending or fixing an existing file in guides/, so the house style, the verified-links rule and the validation script stay applied. If the request touches guides/ at all, read this skill first.
---

# Writing a sketch guide

The sketchbook at `index.html` lists 26 sketches. A **guide** turns one of them from a
title-plus-some-links into something Christian can sit down and follow. `guides/a1-good-movement.html`
is the reference implementation — read it before writing a new one. It is the calibration, not just
an example.

## The problem a guide solves

The sketchbook's original links were part docs, part YouTube search URLs. Christian's own words:
that hands the research task back to him. A guide is the opposite — you do the finding, the
verifying and the explaining, and he does the practice.

So the bar is: **he opens the guide and starts working within a minute.** No deciding which of six
tutorials to watch, no reconciling a Godot 3 video with a Godot 4 API, no guessing whether he's
done with a step.

## Non-negotiable: every link is verified before it ships

A search URL is a failure. A plausible-looking video ID that 404s is worse — it costs trust that
prose can't buy back. Never write a URL you have not fetched in this session.

For a YouTube video, get the real title, channel, date and duration, and put all of them in the
guide so he can judge the cost before clicking:

```bash
id=VIDEO_ID
page=$(curl -sL --max-time 20 "https://www.youtube.com/watch?v=$id")
echo "$page" | grep -o '"ownerChannelName":"[^"]*"' | head -1
echo "$page" | grep -o '"uploadDate":"[^"]*"' | head -1
echo "$page" | grep -o '"lengthSeconds":"[0-9]*"' | head -1
echo "$page" | grep -o '<meta name="title" content="[^"]*"' | head -1
```

For docs and articles, a status check is enough:

```bash
curl -s -o /dev/null -w '%{http_code}\n' --max-time 20 "$url"
```

Two judgment calls that come up constantly:

- **Date-check Godot content.** Anything before mid-2024 predates `TileMapLayer` and several 4.x API
  changes. A 2022 video titled "Godot" is almost always Godot 3. If it's still the best explanation,
  say so in the guide and note what's changed — don't silently ship a stale link.
- **Put the runtime in the prep list.** A 44-minute talk presented next to a 5-minute video without
  labels is a small betrayal. Mark long ones optional and say when they're worth it.

If you can't verify a good video for a topic, write the guide without one. Prep is optional;
accuracy isn't.

## Read the transcript before you recommend a video

A title and a runtime tell you almost nothing. `scripts/fetch_transcript.py` gives you the actual
content as timestamped text:

```bash
# one-off, installs yt-dlp into a gitignored repo-local venv
python3 .claude/skills/sketch-guide/scripts/fetch_transcript.py --setup

python3 .claude/skills/sketch-guide/scripts/fetch_transcript.py VIDEO_ID
```

Read it before writing the prep card, and use it to:

- **Confirm it teaches what you're claiming.** A title match is not a content match.
- **Detect version drift from the inside.** A Godot video that says `KinematicBody2D` is Godot 3
  regardless of its upload date.
- **Find the timestamp worth pointing at**, so a 40-minute video can be cited at the 6 minutes that
  matter.
- **Spot where the video and your guide disagree**, which is the highest-value thing it gives you.
  A1's prep video wires coyote time with `get_tree().create_timer()` and signals; the guide counts a
  float down in `_physics_process`. Both are fine, but a reader who watched then followed would
  stumble. Naming the difference in the prep card turns a contradiction into a second perspective.

Transcripts are research material. Write every guide in your own words — never paste transcript text
into a page, and don't reproduce a creator's explanation at length. What you take from a transcript
is *knowing*, not *wording*.

Note the transcript only works via yt-dlp's `android` player client; every other route YouTube now
gates behind a proof-of-origin token. If it starts returning nothing, the script says so and points
at yt-dlp's PO-Token guide — the fix is usually just upgrading yt-dlp.

## The shape

Read `references/template.html` for the skeleton to copy, and `references/house-style.md` for voice,
callout usage and step design. The overall arc:

1. **Head** — sketch ID and module, title, standfirst, pills (tool, time, step count), and a
   *"What you'll have at the end"* box. He should be able to decide from this alone whether tonight
   is the night for this sketch.
2. **Prep** — 0–3 verified videos with channel, date and runtime. Say *why* each one, not just what
   it is. Keep required prep under ~15 minutes.
3. **Steps** — 6–10 of them, each with a time estimate. The estimates must sum to roughly the
   sketch's time budget in `index.html`; if they don't, one of the two is wrong.
4. **A closing section that is the actual point.** In A1 it's the tuning session — the steps only
   exist so that section can happen. Every guide should have this: the part where he stops following
   and starts playing. Ask yourself what the sketch is *for* and make that the last step, not an
   afterthought.
5. **Footer** — what he learned in one honest sentence, the log-session button, and links to the
   two or three sketches that naturally follow.

## Steps that produce the feeling of progress

That phrase is Christian's brief, and it's the whole design constraint. What creates it:

- **Each step ends somewhere he can run the thing and feel a difference.** A step that only
  refactors is a step that feels like homework.
- **Build the bad version first when there is one.** A1 has him write instant-on/instant-off movement
  in step 3 purely so step 4 has something to fix. Five minutes, and it converts an abstract
  improvement into a felt one. Use this wherever the sketch has a naive baseline; skip it where
  there isn't one — it's a tool, not a ritual.
- **Name what to feel, not just what to type.** The `.feel` callout after a code block is often
  doing more teaching than the code.
- **Give tuning knobs and a table of what to push them to.** Extremes teach faster than defaults.
  "Set it to 0 and try again" is the fastest way to understand what a value does.

## Code

Code goes in `<figure class="code">` blocks — see the template for the exact markup, including the
copy button that `assets/guide.js` wires up.

- **Escape `<` and `>` as `&lt;` `&gt;`** inside `<code>`. GDScript is full of `-> void` and
  `velocity.y < 0.0`, and an unescaped `>` will quietly eat the rest of your block.
- **Indent with tabs**, matching Godot's editor default, so pasted code doesn't fight his settings.
- **Write code that actually runs on Godot 4.5+.** Check any API you're not certain of against
  `docs.godotengine.org` rather than from memory — the class reference URL pattern is
  `https://docs.godotengine.org/en/stable/classes/class_<lowercase_name>.html`.
- **Prefer derived values over magic numbers.** A1 exports `jump_height` and `jump_time_to_peak` and
  computes gravity, because those are the units a person thinks in. Magic constants are the thing a
  guide should be removing, not teaching.
- Show incremental snippets as the guide progresses, then put the complete file in a
  `<details>` block at the end so he can diff against his own.

Syntax highlighting is handled by a small GDScript highlighter in `assets/guide.js` — no CDN, no
dependency. It classes keywords, types, strings, numbers, annotations and function names. It only
knows GDScript; for shader code (`E` sketches) the output is still readable, but don't expect
GLSL-accurate colouring.

## Diagrams

Author them as inline SVG in a `<figure class="fig">`, using the `svg-line` / `svg-plot` /
`svg-plot2` / `svg-band` / `svg-label` classes so they follow the theme. Never link an external
image — it breaks the offline story and hotlinks someone else's bandwidth.

A diagram earns its place when it shows something prose is bad at: a curve, a timing window, a
before/after of the same quantity. A1 has three (velocity ramp, jump arc, coyote window) and none of
them are decoration. Two or three is plenty; zero is fine if the sketch is not spatial or temporal.

## What a guide can honestly be, per module

This differs a lot by tool, and pretending otherwise produces bad guides. Read
`references/modules.md` before starting anything outside module A. Short version: Godot and shader
sketches become full standalone guides; audio sketches are workflow plus Godot-side code with a
video carrying the ear-training; **Aseprite sketches cannot be standalone** — no screenshots of its
UI, no example art — so they're structured practice plans built around a verified video, and should
say so rather than bluffing.

## Shipping it

1. **Write** to `guides/<id-lowercase>-<slug>.html`, e.g. `guides/a3-hitstop.html`. Set
   `data-guide` (the filename stem) and `data-sketch` (the sketch ID, e.g. `A3`) on `<body>` —
   `assets/guide.js` uses them for progress storage and for logging the session back into the
   sketchbook.
2. **Register** it in `index.html` — this is the step that's easiest to forget and most visible when
   missed, because an unregistered guide is a page nobody can reach. On that sketch's object in the
   `SKETCHES` array, add:

   ```js
   guide: "guides/<file>.html", guideSteps: <number of steps>,
   ```

   Both fields matter. **The front page renders `SKETCHES.filter(e => e.guide)` and nothing else** —
   a sketch with no guide is invisible there. So adding `guide:` is what publishes the page, and
   forgetting it means writing something nobody can reach. `guideSteps` drives the progress readout
   ("4/9 steps"), which the card gets by reading the guide page's own `localStorage` under the shared
   origin. Get the count wrong and the progress bar lies.

   The rest of the `SKETCHES` array stays in the file deliberately: it's the catalogue of what a
   guide *could* be written for, and the front page counts it ("2 written · 25 more sketches
   waiting"). Don't delete unguided entries to tidy up.

   Tool filter chips appear on the front page automatically once there are more than four guides —
   below that they'd be noise. Nothing to do, but don't be surprised by their absence.

   **If the sketch doesn't exist yet**, add it to `SKETCHES` first — a guide is allowed to invent a
   sketch the original 26 didn't cover. B6 came about that way. Give it the next free ID in its
   module, tag every tool it genuinely uses (the filter counts on it), and make `time`/`mins` agree
   with the sum of the guide's step estimates.
3. **Validate**:
   ```bash
   python3 .claude/skills/sketch-guide/scripts/check_guide.py guides/<file>.html --links
   ```
   This checks document structure, the `data-` attributes, code-block escaping and tab indentation,
   step numbering, that the rail's step count matches reality, that the guide is registered in
   `index.html`, and — with `--links` — that every external URL still resolves. Fix what it reports;
   it only flags things that have actually gone wrong before.
4. **Commit and push.** GitHub Pages redeploys from `main` in about a minute. Confirm the live URL
   returns 200 rather than assuming:
   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' https://christianalfoni.github.io/learn-gamedev/guides/<file>.html
   ```

## Things worth remembering about this repo

- The practice is deliberately **not** about shipping games. Never frame a guide as a step toward
  finishing something, add scope, or suggest combining sketches into a project.
- They're called **sketches**, never "études" — he disliked the French term.
- Guide progress and sketchbook progress share an origin, which is why the log-session button in the
  footer can write to the tracker's own `localStorage`. Keep that footer block intact when copying
  the template.
- `index.html` is deliberately self-contained; guides and `setup.html` deliberately share
  `assets/`. Don't "fix" either arrangement into the other.
- The site is three things: `index.html` (guides only), `guides/` (the guides), and `setup.html`
  (per-tool settings, teachers and practice notes — reference material, not a guide, reached from a
  footer link). If you're adding tool-setup content rather than a sketch walkthrough, it belongs in
  `setup.html`.
