# Platform Shooter (working title)

> Source of truth. `##` are areas, `###` are features — each needs a `{#id}` so
> assignments can point at it. Sections in *italics* are not yet decided;
> **Open:** marks a specific question inside a section that is otherwise settled.

## The game

### Pitch {#pitch}

A single-arena platform shooter. Enemies pour in from the top of a multi-floor level and work
their way down. You move and shoot to stop them, and you survive as long as you can.

Two health bars, damaged by two different failures: **yours**, when an enemy touches you, and
**the base's**, when an enemy makes it out of the bottom of the level.

### Pillars {#pillars}

*Not decided yet. Three things this game is that you would refuse to compromise.*

## The run

### Core loop {#core-loop}

- Enemies spawn continuously at the **top** of a fixed arena.
- They walk, turn when they hit a wall, and descend by **walking off ledges** — no pathfinding,
  no intent. Deliberately dumb.
- The player moves, jumps and shoots to destroy them on the way down.
- Anything that reaches the **bottom** exits the level and damages the base.
- The arena never changes shape during a run. Everything that varies is the enemy pressure.

### Ending a run {#run-end}

Two independent health bars, neither of which refills during a run. **Either** one hitting zero
ends it — the player being overwhelmed, or the base being worn down by escapees.

The score is **time survived**. No waves, no rounds: pressure rises continuously and the run ends
when it beats you.

### Difficulty {#difficulty}

Pressure rises continuously rather than in waves, since the score is time survived.

*Not decided yet: which levers move — spawn rate, enemies per spawn, walk speed — and how fast.
Worth deciding by playing rather than by planning.*

### Rogue-lite {#roguelite}

**In-run drops only.** Kills sometimes drop a temporary upgrade — faster fire, more damage, a
health patch — and everything is lost when the run ends. Nothing persists between runs: no save
file, no currency, no meta screens.

*Not decided yet: which upgrades exist, drop rate, and whether they stack.*

## Mechanics

### Movement {#movement}

Platformer movement across a multi-floor arena — run, jump, and move between floors.

Because aiming is horizontal only, **movement is the core skill of this game**, not aiming. You
have to reach an enemy's floor to kill it, so a run is a series of routing decisions under time
pressure. Vertical traversal speed is therefore the single most important tuning value in the
project: too slow and escapees feel unfair, too fast and the arena stops mattering.

**Open:** how the player changes floors — jumping up, dropping through platforms, or both. Drop-
through almost certainly, since the same gaps the enemies fall through are the fast way down.

### Shooting {#shooting}

The player's only offensive verb, and deliberately the simple half of the game: **you shoot the
way you face, horizontally.** No up-aim, no mouse, no 360°.

The consequence is the whole design. You cannot shoot down through a gap at the floor below, so
killing something means standing on its floor — which turns every threat into a movement problem
rather than an aiming one, and makes camping self-defeating.

*Not decided yet: fire rate, whether the gun is hitscan or a visible projectile, and how many
enemies one shot should kill.*

### Enemies {#enemies}

One enemy type to start. Walks at a constant speed, turns on hitting a wall, falls off any ledge
it reaches. **No awareness of the player at all** — it never turns toward you, never chases,
never shoots.

The only threat is **contact damage**: touching one hurts. That keeps the threat positional, which
suits a game where position is already the main decision.

*Not decided yet: how many hits an enemy takes, and whether a second type arrives later.*

### The base {#base}

The thing at the bottom that takes damage when an enemy escapes the level.

**Open:** what the base actually is — a visible structure, or purely a number in the HUD.

### HUD {#hud}

Two health bars and the run's score, readable at a glance while everything else is moving.

## Art

### Player character {#player-art}

*Deferred — style and world not being decided yet.*

### Enemies {#enemy-art}

*Deferred.*

### Environment {#environment-art}

*Deferred. The arena's look; its shape is a mechanics question, under #core-loop.*

## Audio

### Sound effects {#sfx}

*Deferred.*

### Music {#music}

*Deferred.*

## Feel

### Game feel {#game-feel}

*Deferred — but a shooter lives or dies here, so it will not stay deferred long.*
