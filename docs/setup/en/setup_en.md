# Multiworld Setup Guide

## Required Software

- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.1 or later
- Spyro Reignited Trilogy (PC, Steam) **or** a PS1 emulator with a legal Spyro the Dragon ROM
- The in-game client (UE4SS mod `srt_bridge` + Go daemon `srtap_checkd`;
  see the project README in the client repo)

## Installation

1. Install Archipelago.
2. Double-click `reignited.apworld` (from this repo's releases) to install it into your
   Archipelago installation. Remove any older `spyro_reignited.apworld` or
   `spyro1.apworld` first: all three declare the game "Spyro Reignited Trilogy".
3. Generate a game as normal: create a YAML via the Launcher's "Generate Template Options",
   edit your settings, place it in the `players` folder, and run Generate.
4. Host the output on archipelago.gg or locally.

## YAML example

```yaml
name: YourName
game: Spyro Reignited Trilogy
Spyro Reignited Trilogy:
  progression_balancing: '50'
  accessibility: full
  included_games: ['Spyro 1']
  required_games: ['Spyro 1']
  spyro1_goal: gnasty
  spyro1_balloonist_gates: vanilla
  spyro1_dragon_shuffle: dragonsanity
  spyro1_egg_shuffle: 'true'
  spyro1_enable_gem_checks: 'true'
  spyro1_enable_flight_checks: 'true'
  enable_filler_extra_lives: 'true'
```

Per-game options carry the game's prefix (`spyro1_…`); filler, trap and DeathLink
options apply to the whole slot.

## Connecting

Phase 2 work. When ready:

- **Reignited (PC):** drop the UE4SS mod into the game folder, launch, open the mod's
  connect UI, enter host/slot. The mod reads dragon/egg/gem state from game memory and
  syncs with the server.
- **PS1 (DuckStation/BizHawk):** launch the included client, point it at your emulator
  (same pattern as the Spyro 2 randomizer), connect, and play.

## Game changes

- Items you find in-game are sent to the multiworld: freeing a dragon, catching an egg
  thief, gem percentage milestones, clearing a flight level's 4 target sets, skill points.
  Level completions and boss defeats are tracked as progress.
- Items you receive are shown by the client overlay. Depending on client capability,
  some may have in-game effects (extra lives, colors, modes).
- Homeworld gates behave per your `spyro1_balloonist_gates` option (vanilla or
  shuffled thresholds; see the options reference in the game info page).

## Known limitations

- Item effects (extra lives, colors, modes, traps) and DeathLink require the
  UE4SS mod client; with it they are live in-game.
- Gnasty's Loot goal requires collecting every dragon and egg plus 12,000 gems —
  expect a long game.