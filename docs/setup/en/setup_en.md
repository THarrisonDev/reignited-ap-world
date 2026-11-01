# Multiworld Setup Guide

## Required Software

- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.1 or later
- Spyro Reignited Trilogy (PC, Steam)
- The Reignited AP client bundle from the project's
  [releases](https://github.com/THarrisonDev/reignited-ap/releases) page: the
  UE4SS mod `srt_bridge`, the save scanner `srtap_checkd`, and the launcher (see
  `INSTALL.md`).

## Installation

1. Install Archipelago.
2. Add the world to your Archipelago installation:
   - **In the launcher:** click **Install APWorld** and select
     `reignited.apworld`; dragging the file onto the launcher also works.
     If the launcher reports the world is already loaded, restart it.
   - **By hand:** copy it into your installation's `custom_worlds` folder —
     for the Linux AppImage that is `~/.local/share/Archipelago/worlds`.
   Double-clicking the file only works where `.apworld` files are associated
   with the launcher. Keep the file name as `reignited.apworld`: Archipelago
   imports a world under its file name, so a renamed copy does not load.
   Remove any older build of this project (`spyro_reignited.apworld`, or a
   dated `reignited_<version>.apworld`) first: it declares the same game
   "Spyro Reignited Trilogy", and Archipelago only loads one of them.
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

1. Download and extract the client bundle from the project's releases.
2. Run `install.bat` (Windows) or `install.sh` (Linux / Proton) to install the
   mod, the save scanner, and UE4SS.
3. Open the launcher, enter the server address and your slot name, and click
   **Save & launch game**. The mod connects once you are actually playing, reads
   dragon/egg/gem state from the game, and syncs with the server.
4. Keep the launcher page open to watch checks you send and items you receive.

## Game changes

- Items you find in-game are sent to the multiworld: freeing a dragon, catching an egg
  thief, gem percentage milestones, clearing a flight level's 4 target sets, skill points.
  Level completions and boss defeats are tracked as progress.
- Items you receive are shown by the client overlay. Depending on client capability,
  some may have in-game effects (extra lives, colors, modes).
- Homeworld gates behave per your `spyro1_balloonist_gates` option (vanilla or
  shuffled thresholds; see the options reference in the game info page).

## Known limitations

- PC (Steam) only: the client runs inside the game via UE4SS. There is no
  emulator support.
- Item effects (extra lives, colors, modes, traps) and DeathLink require the
  UE4SS mod client; with it they are live in-game.
- Gnasty's Loot goal requires collecting every dragon and egg plus 12,000 gems —
  expect a long game.
- The *All Dragons* goal is reported complete when Gnasty Gnorc is defeated; the
  80-dragon requirement is enforced at generation, not by the in-game client.
