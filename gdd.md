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

Two independent health bars. Neither refills during a run (assumed — say if not).

**Open:** what ends a run — player health hitting zero, base health hitting zero, or either?
**Open:** what "as far as you can" measures. Time survived, waves cleared, or enemies killed?
That number is the score, and it decides what the HUD shows.

### Difficulty {#difficulty}

*Not decided yet. How pressure escalates over a run — spawn rate, enemy count, enemy types.*

### Rogue-lite {#roguelite}

*Not decided yet. Whether anything carries between runs, or whether "rogue-lite" here just means
escalating pressure and a fresh start each time.*

## Mechanics

### Movement {#movement}

Platformer movement across a multi-floor arena — run, jump, and move between floors. Needs to
feel good enough that repositioning under pressure is the fun part rather than the friction.

**Open:** how the player changes floors — jumping up, dropping through platforms, or both.

### Shooting {#shooting}

The player's only offensive verb. Destroys enemies before they descend.

**Open:** the aiming scheme. This is the single biggest open question in the document — it decides
the movement scheme, the controls, and how the arena should be laid out.

### Enemies {#enemies}

One enemy type to start. Walks at a constant speed, turns on hitting a wall, falls off any ledge
it reaches. No awareness of the player at all.

**Open:** whether enemies threaten the player only by contact, or also attack.

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
