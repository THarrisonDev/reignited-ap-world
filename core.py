# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-23

"""Shared world plumbing: the item/location types and the region and rule
wiring every tabular game (Spyro 2/3) uses, so each game module keeps only
its own option- and item-specific logic.
"""

from typing import Callable, Dict, Optional, Sequence

from BaseClasses import Entrance, Item, Location, Region
from worlds.generic.Rules import add_rule

GAME = "Spyro Reignited Trilogy"


class SRTItem(Item):
    game: str = GAME


class SRTLocation(Location):
    game: str = GAME


def create_level_regions(game, menu: Region, levels: Sequence[str], tables: Dict[str, list],
                         *, prefix: Callable[[str], str], skipped: Sequence = (),
                         locked: Optional[Callable[[str, object], Optional[str]]] = None
                         ) -> Dict[str, Region]:
    """Create one Region per level, fill it with its included locations and wire
    its hub entrance.

    `skipped` holds the check kinds the slot's options switch off; `locked`
    names the item a location holds as a locked event (returning None leaves the
    location empty for the pool).
    """
    regions: Dict[str, Region] = {}
    previous_hub = menu
    for level in levels:
        region = Region(prefix(level), game.player, game.multiworld)
        for data in tables[level]:
            if data.kind in skipped:
                continue
            location = SRTLocation(
                game.player, data.name, game.world.location_name_to_id[data.name], region
            )
            item = locked(level, data) if locked else None
            if item:
                location.place_locked_item(game.world.create_item(item))
            region.locations.append(location)
            game.location_names.add(data.name)
        game.multiworld.regions.append(region)
        regions[level] = region
        if game.gates.is_homeworld(level):
            parent, previous_hub = previous_hub, region
        else:
            parent = regions[game.gates.homeworld_of(level)]
        entrance = Entrance(game.player, prefix(level), parent)
        parent.exits.append(entrance)
        entrance.connect(region)
    return regions


def add_gate_rules(game, prefix: Callable[[str], str], levels: Sequence[str],
                   tables: Dict[str, list], gem_kind) -> None:
    """Add every data-driven rule from the game's gate data: entrance gates,
    Money Bags payments, check gates and gem tiers."""
    _entrance_rules(game, prefix, levels)
    _location_rules(game, prefix, levels, tables, gem_kind)


def _entrance_rules(game, prefix: Callable[[str], str], levels: Sequence[str]) -> None:
    """Gate each level's entrance, and give a gate that reads other regions all
    of them as indirect conditions."""
    player = game.player
    multiworld = game.multiworld
    gates = game.gates
    for level, gate in gates.gates.items():
        if level not in levels:
            continue
        entrance = multiworld.get_entrance(prefix(level), player)
        add_rule(entrance, gates.rule(gate))
        if gates.reads_regions(gate):
            for other in levels:
                multiworld.register_indirect_condition(
                    multiworld.get_region(prefix(other), player), entrance)
    for payment in gates.payments:
        if "location" not in payment:
            continue
        add_rule(multiworld.get_location(prefix(payment["location"]), player),
                 gates.payment_rule(payment["name"]))


def _location_rules(game, prefix: Callable[[str], str], levels: Sequence[str],
                    tables: Dict[str, list], gem_kind) -> None:
    """Gate the locations that carry a check gate, and each gem check by tier."""
    player = game.player
    multiworld = game.multiworld
    gates = game.gates
    for name, gate in gates.check_gates.items():
        if prefix(name) in game.location_names:
            add_rule(multiworld.get_location(prefix(name), player), gates.rule(gate))
    for level in levels:
        for data in tables[level]:
            if data.kind is gem_kind and data.name in game.location_names:
                add_rule(multiworld.get_location(data.name, player),
                         gates.gem_rule(level, data.threshold))


def add_level_lock_rules(game, prefix: Callable[[str], str], levels: Sequence[str],
                         key_name: Callable[[str], str]) -> None:
    """Require each lockable level's shuffled key at its entrance."""
    player = game.player
    for level in levels:
        add_rule(game.multiworld.get_entrance(prefix(level), player),
                 lambda state, key=key_name(level): state.has(key, player))
