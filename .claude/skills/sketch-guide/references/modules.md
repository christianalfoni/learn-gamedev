# What a guide can honestly be, per module

The four tools give you very different amounts of leverage. A guide that pretends otherwise — that
writes confident prose about which shade of orange to pick, or claims a screenshot it can't produce —
is worse than one that says "watch this person do it, then do these five things."

Work out which category your sketch is in before you start, and set the guide's ambition accordingly.

---

## Module A — Godot game-feel · **full standalone guides**

The best case. You can write correct GDScript, explain every line, derive constants from first
principles, and draw the curves as SVG. `a1-good-movement.html` is the calibration.

What makes these good:
- Derived values over magic numbers (`jump_height` + `time_to_peak` → gravity, not `gravity = 980`).
- A naive baseline step so the improvement is felt, not asserted.
- A tuning table at the end with values to push to extremes.
- `@export` everything he'll want to feel, and tell him about the Scene dock's **Remote** tab so he
  can tune the running game.

Prep video: usually one short conceptual piece plus, if it exists, one current Godot 4 technical one.

---

## Module E — Shaders · **full standalone guides**

Same as A. You can write GDShader, explain uniforms and UV maths, and show the effect's mechanism as
a diagram. Two caveats:

- The highlighter in `assets/guide.js` only knows GDScript. Shader code renders readably but the
  colouring isn't GLSL-accurate — don't add a second highlighter for this, it isn't worth it.
- Link `godotshaders.com` for community examples to read and adapt. Reading shaders is most of
  learning shaders.

---

## Module C — Audacity + SFX · **workflow guides with an ear-training video**

You can write the exact steps: which generator, which settings, which Audacity operations in which
order, the zero-crossing snap, the export settings, and the Godot-side code
(`AudioStreamRandomizer`, buses). That's most of a guide.

What you cannot do is judge whether it sounds good. So:
- Carry the "does this sound right" part with a verified Marshall McGee or Akash Thakkar video, and
  say explicitly that the video is doing the ear training.
- Describe sounds in terms of their construction (sub / body / click, transient, tail), which is
  teachable, rather than adjectives, which aren't.
- A waveform diagram as SVG is genuinely useful — layering, envelope shape, a loop seam.

---

## Module D — FL Studio · **workflow guides, thinner than they look**

Christian already knows music theory, so a guide should skip the theory and cover the game-music
idiom: loop seams, vertical layering, stingers, export settings that don't break loops.

Honest limits:
- No FL Studio screenshots, and FL's workflow is heavily UI-driven. Lean on the official FL channel
  or SeamlessR for the DAW mechanics and spend your words on what's specific to *game* music.
- The Godot side (two `AudioStreamPlayer`s, bus fades) is code you can write properly — that half of
  a D guide can be as solid as an A guide.

---

## Module B — Aseprite · **structured practice plans, not tutorials**

Be upfront about this one. You cannot screenshot Aseprite's interface, you cannot produce example
pixel art, and for drawing technique a good video genuinely teaches better than prose. A guide that
pretends to teach shading in paragraphs is worse than no guide.

What a B guide should be instead:
1. **A verified video as the spine** — AdamCYounis, Brandon James Greer, MortMort, or a Saint11
   article — chosen for exactly the technique the sketch practises.
2. **Setup steps you *can* write precisely**: grid size, pixel-perfect pencil, tags, slices, the
   update-on-save pipeline, the Aseprite executable path in Godot's editor settings.
3. **A constraint list** — frame count, palette size, canvas size. Constraints are the actual
   teaching content of a pixel-art sketch and they transmit perfectly in text.
4. **A self-check list** — "does it read at 100%?", "does the loop have a visible pop?", "is any
   colour used exactly once?" Questions he can answer by looking, without you seeing the art.
5. **The Godot-side import steps**, which are as writable as any A guide.

Say in the guide that the video is doing the drawing instruction. He'd rather be told than discover
it three paragraphs in.

---

## Module F — Toy sketches, all tools · **assembly guides**

These combine outputs from other sketches. The guide's job is orchestration and timing — what
happens on which frame, in what order, and how the pieces layer — rather than teaching any one
craft again.

- Link back to the component sketches' guides for the parts he may not have done yet, and say what
  to substitute (a Kenney asset, a jsfxr export) if he wants to do this one first.
- The Godot code is fully writable, so these lean closer to module A in quality.
- The closing section should be a layering exercise: turn each element off one at a time and notice
  which one was carrying the feel. That's the lesson these sketches exist for.
