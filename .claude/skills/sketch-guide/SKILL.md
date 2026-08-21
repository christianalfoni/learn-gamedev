---
name: sketch-guide
description: Derive assignments from the game design document in the learn-gamedev repo, and write them up as step-by-step guides for Godot 4, Aseprite, Audacity or FL Studio. Use this whenever Christian asks to derive, generate or propose assignments from the GDD, says he has extended or changed gdd.md and wants work from it, asks what is not covered yet, or asks for a guide/walkthrough/write-up by section, by name ("the grappling one") or by assignment ID. Also use it when editing anything in guides/ or gdd.md, so the derivation rules, house style, verified-links rule and validation scripts stay applied.
---

# Deriving and writing assignments

`gdd.md` at the repo root is the game design document, and it is the source of truth. Everything
else exists to serve it: **assignments** are derived from what the document describes, and each one
builds a real piece of the game. `index.html` renders the document with its assignments underneath
each section, so a described feature with nothing built from it shows up as a visible gap.

`guides/a1-good-movement.html` is the reference implementation — read it before writing a new one.
It is the calibration, not just an example.

## The problem an assignment solves

Two things at once. It gives Christian a piece of his game he doesn't yet know how to build, and it
does the research for him: you find the sources, verify them, and explain the thing. He builds.

So the bar is: **he opens it and starts working within a minute.** No deciding which of six
tutorials to watch, no reconciling a Godot 3 video with a Godot 4 API, no guessing whether he's done
with a step.

## Deriving assignments from the document

When he asks for new assignments, don't guess at what's needed — read the document and diff it:

```bash
python3 .claude/skills/sketch-guide/scripts/gdd_coverage.py
python3 .claude/skills/sketch-guide/scripts/gdd_coverage.py --since HEAD~1
```

The report splits every `###` section into **covered** (has assignments), **ready to derive**
(described, nothing built from it) and **not described** (nothing to derive from yet). With
`--since`, it also marks the sections whose prose changed in that range — after he extends the
document, those are almost always the ones he means.

Then, before writing anything:

1. **Propose first, in chat.** List the assignments you'd derive, each with the section it serves and
   one line on what it contributes. He picks. Writing three guides he didn't want is expensive for
   both of you.
2. **One assignment per buildable thing**, sized to a session (45–120 min). "Implement the combat
   system" is a project; "an attack that connects — hitbox, hitstop, one impact sound" is an
   assignment.
3. **Derive from what the document actually says**, not from what would be generically useful. If it
   says the character is 32px with a four-colour ramp, the art assignment uses those numbers.
4. **Say so when a section is too vague to derive from.** "This says the core verb is grappling but
   not what it attaches to — tell me that and I can write it" is more useful than a guess.
5. **Reuse before inventing.** If an existing assignment already covers a section, extending it or
   pointing at it beats writing a near-duplicate.

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

## Rank candidates: relevance first, then reach

A search will happily hand you a 1,200-view video that matches the title exactly, and that's how the
first pass of these guides shipped a video with 33 likes as *required* prep. Don't let search
ordering pick for you — gather every candidate, then rank them:

```bash
python3 .claude/skills/sketch-guide/scripts/video_stats.py ID1 ID2 ID3
python3 .claude/skills/sketch-guide/scripts/video_stats.py --guide guides/a1-good-movement.html
```

It prints views, likes, likes-per-thousand, runtime and date, sorted by reach, and flags anything
with a fraction of the leader's audience.

**Relevance is still the deciding vote.** A 900-view video that teaches exactly the thing beats a
million-view video that's merely adjacent, and a hugely popular Godot 3 tutorial is worse than
nothing because it teaches an API that no longer exists. Two real examples from this repo:

- A 34k-view "complete 2D player movement" video lost to a 27k one because its transcript said
  *KinematicBody2D* — Godot 3.
- Brackeys' GDScript tutorial has 2.3M views and was still wrong for A1, because A1 is about movement
  feel and the video is about the language.

**Among genuinely relevant candidates, take the bigger one.** Reach means more people found it clear,
and it usually correlates with better audio, editing and pacing. Likes-per-thousand is the useful
tiebreaker between two videos of similar size — 50/1k is exceptional, 30/1k is good, under 15/1k on a
big channel suggests people watched and weren't helped.

Put the view count in the byline (`Saultoons · Mar 2021 · 276k views`) so the reader can weigh the
recommendation themselves. `check_guide.py --links` warns on anything under 5,000 views, which is a
prompt to justify the pick or replace it — not an automatic veto.

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

## Every guide stands completely alone

A guide assumes a **fresh, empty project** and a reader who has done none of the others. No "if you
did A1, paste your movement code in", no "the same principle as A4", no *Natural next sketches*
footer. If a guide needs code or an asset another sketch also produces, include it inline as
something to paste and move past — and say it's deliberately plain so nobody wonders whether they
should be tuning it.

This is Christian's explicit preference and it's also just better: cross-references make a guide feel
like chapter six of something, which is exactly the finish-the-course pressure this whole repo
exists to avoid. He should be able to open any guide on any evening and start.

Two things may point outward. The footer's **Reference** block — official docs, a tool's own manual,
an archive worth bookmarking. And **the design document**: an assignment should open by naming what
it contributes to the game ("this is the walk cycle §player-art calls for"), because that's the whole
reason it exists. Referencing the document is the point; referencing a sibling assignment is not.

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
2. **Register** it in the `ASSIGNMENTS` array in `index.html`. This is what places it under the right
   section of the document — an unregistered guide is a page nobody can reach:

   ```js
   { id: "X1", t: "Short title", time: "45–90 min", tools: ["godot"],
     gdd: ["section-id"], guide: "guides/x1-slug.html", steps: 8,
     blurb: "One sentence on what it builds." },
   ```

   - **`gdd`** is the list of `###` section ids it serves, and it is what makes the assignment appear
     on the page at all. An assignment with an empty `gdd` falls into "Not tied to the document",
     which is a visible smell rather than an error — use it only when something genuinely serves no
     described feature yet.
   - **`steps`** drives the progress readout, which is read from the guide page's own `localStorage`
     under the shared origin. Get it wrong and the bar lies.
   - **`id`** is a stable handle used by `data-sketch` and by the progress store. Pick the next free
     one in its letter family and don't renumber existing ones.

   Then confirm the wiring with `gdd_coverage.py` — it reports broken `gdd` references and exits
   non-zero on them.

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

- **Real pieces, no deadlines.** Assignments now build usable parts of an actual game, so drop the
  old "this artefact is disposable" framing — what he makes here is meant to be kept. What has not
  changed: no deadlines, no milestones, no dependency chains, and every assignment stays finishable
  and abandonable in one sitting. The skill he gains still outranks the artefact; the artefact is
  just no longer thrown away.
- They're called **sketches**, never "études" — he disliked the French term.
- Guide progress and sketchbook progress share an origin, which is why the log-session button in the
  footer can write to the tracker's own `localStorage`. Keep that footer block intact when copying
  the template.
- `index.html` is deliberately self-contained and reads `gdd.md` over `fetch` at runtime, so the
  document stays the single source of truth with no build step. That also means the site must be
  served over HTTP — opening `index.html` as a local file shows a clear error rather than the page.
- The site is four things: `gdd.md` (the document), `index.html` (renders it with assignments under
  each section), `guides/` (the assignments themselves), and `setup.html` (per-tool settings and
  teachers — reference material, reached from a footer link). Tool-setup content belongs in
  `setup.html`, never in an assignment.
