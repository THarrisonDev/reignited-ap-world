# reignited-ap-world

An Archipelago(AP) World for the Spyro Reignited Trilogy!

## Why Reignited AP?

- **Modernized experience** — quality-of-life improvements built on top of
the original foundation.
- **Community-driven** — shaped by feedback and contributions from people who
care about it.
- **Accessible to everyone** — designed so both new and returning users can
get started quickly.

## Getting Started

Head over to the [Releases](../../releases) page to grab the latest version,
then check out the installation instructions in the parent
[README](../README.md) to get up and running.

Player-facing documentation lives in `docs/`: the game info page
(`en_Spyro Reignited Trilogy.md`) and the multiworld setup guide
(`setup_en.md`).

## Package Layout

For contributors orienting in the codebase:

- `__init__.py` — the `SpyroReignitedWorld` class: one slot covers any
  combination of the trilogy's games, each game plugs in through the same
  interface (`generate_early`, `create_regions`, `create_pool`, `set_rules`,
  `is_complete`, `slot_data`).
- `core.py` — types shared by every game (`SRTItem`, `SRTLocation`, the
  `GAME` constant, filler item name).
- `Items.py` / `Options.py` — shared items (filler, traps) and the slot
  options dataclass.
- `spyro1/`, `spyro2/`, `spyro3/` — one subpackage per game, each with its
  own `Game.py` (regions, pool, rules, goal), `Items.py`, `Locations.py`,
  `Names.py`, and `Options.py`.
- `archipelago.json` — AP world metadata (version, minimum AP version).

## Acknowledgments

- **[Archipelago](https://github.com/ArchipelagoMW/Archipelago)** (MIT) — the
  multiworld randomizer platform this world is built for.
- **[S2AP](https://github.com/Uroogla/S2AP)** and
  **[S3AP](https://github.com/ArsonAssassin/S3AP)** by
  Uroogla and ArsonAssassin (MIT) — this world's architecture closely mirrors
  theirs: generation and logic in the apworld, with the client watching the
  game and syncing checks/items with the AP server. Their per-game
  subpackage structure and several design precedents (e.g. Spyro 3's
  one-name-many-copies dragon eggs) carry over directly.

## Contributing

Contributions are welcome! Whether you want to fix a bug, add a feature, or
improve the documentation, your help is appreciated.

1. Fork the repository and create a new branch for your changes.
2. Make your changes, keeping the existing code style in mind.
3. Test your changes locally to make sure everything works.
4. Open a pull request with a clear description of what you changed and why.

If you're not sure where to start, check the open issues for good first tasks —
or open a new issue to discuss an idea before writing code.
