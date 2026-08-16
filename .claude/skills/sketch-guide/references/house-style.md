# House style

The guides are read by one person, at his desk, about to do the thing. Everything below follows from
that.

## Voice

Second person, present tense, plain. "Attach a script to the Player root" — not "we will now attach"
or "you should consider attaching". He's an experienced programmer, so don't explain what a variable
is; do explain what's idiomatic in Godot specifically, because that's where the actual learning is.

Say what's true, including when it's unflattering:

> Most tutorials hand you `gravity = 980` and leave you guessing what happens if you want a jump
> that's a bit higher. Those aren't the units you think in.

Avoid: "simply", "just", "easy", "of course", exclamation marks, and encouragement he didn't ask for.
A guide that says "Great job!" after step 3 is a guide that doesn't trust its own content.

Contractions are fine. British-ish spelling matches the rest of the repo ("colour", "behaviour"),
but don't be precious about it — Godot's own API is American and code always wins.

## The three callouts

Each has a distinct job. Reaching for one when plain prose would do is the most common way these
pages get bloated.

| Callout | Use it for | Heading style |
|---|---|---|
| `.feel` | What to notice when he runs it. Sensory, not technical. | "Run it and feel this" |
| `.why` | The reasoning behind a choice he'd otherwise cargo-cult. | Specific: "The units are the useful part" |
| `.trap` | A concrete failure with a recognisable symptom. | "Easy to miss", "Y points down" |

A good `.trap` names the symptom before the cause, because that's the order he'll meet it in: *"If
your player falls through the world, check both shapes before you check your code."*

Generic headings ("Note", "Tip", "Important") waste the one line that gets read.

## Steps

- **Imperative, concrete titles.** "The input map", "Coyote time", "A jump you can actually tune".
  Not "Setting up your project" or "Understanding movement".
- **Time estimate on every step**, and make them honest — under-promising here is worse than
  over-promising, because a step that runs long makes the whole guide feel unreliable.
- **6–10 steps.** Fewer and progress doesn't feel like progress; more and the rail stops feeling
  achievable in one sitting.
- **One idea per step.** If a step needs two `.why` callouts it's probably two steps.
- **The last step is the play, not the polish.** Whatever the sketch is *for* — tuning, layering,
  listening — that's the final step, with real space given to it.

## Length

A1 is about 30 KB and that's roughly the ceiling. If a guide is running longer, the usual cause is
explaining something the tool's own docs explain better — link those instead and spend the words on
what's specific to this sketch.

Prose paragraphs: 2–4 sentences. Long enough to make an argument, short enough to skim past when
he's already typing.

## What never appears in a guide

- **Search URLs.** The whole reason guides exist.
- **Unverified links.** See the rule in SKILL.md.
- **Shipping talk.** No "now you could turn this into a game", no roadmaps, no scope. The sketch is
  complete when he stops.
- **References to other sketches.** No "if you did A1", no "next sketches" footer, no assumed
  earlier project. Each guide starts from an empty project and ends when it ends.
- **"Études".** They're sketches.
- **External images or CDN assets.** Diagrams are inline SVG; everything is offline-capable.
- **Fake encouragement or filler transitions** ("Now that we've got that out of the way…").
