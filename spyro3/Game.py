# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

"""Spyro 3 (Year of the Dragon) inside the Spyro Reignited Trilogy world.

Locations: gem checks, dragon eggs, boss-defeat events, and skill-point
checks. The region graph follows the game, and every gate (the boss chain,
egg portals, Sparx realm chain, companion and Money Bags payments, gem tiers)
is data in data/spyro3.json, turned into rules by ../gates.py. Eggs are always
checks; only the paid egg doors give some of them rules of their own. The boss
events replace the boss dungeons' egg rows, which checkd's egg scan already
drops. spyro3_goal=sorceress makes Spyro 3 requirable, meaning Sorceress
Defeated. Abilities are granted by story in Spyro 3, so there are no ability
items.

Under spyro3_egg_shuffle (default on) egg portals count received Dragon Egg
items and the mod re-tunes each portal's EggRequirement to match; off, they
read the game's save-recorded egg count. Either way the doors' rules are the
same gate data, only the counting source moves.

Under spyro3_sparx_powers the three Sparx realm completions become checks
whose default items are the three Sparx power items; off, the checks
disappear.

Under spyro3_level_locks the mod locks 33 sub-level portals behind shuffled
level key items. Homeworlds are never locked (the game's boss chain gates
them), and the spawn level Sunrise Spring is a homeworld, so all 33 keys
shuffle.
"""
from typing import Dict, List, Set

from BaseClasses import Entrance, Region
from worlds.generic.Rules import add_rule

from ..core import FILLER, SRTLocation
from ..data import load
from ..gates import Gates
from . import Items as S3Items
from .Items import (DRAGON_EGG, EXTRA_HIT_POINT, CHEST_BREAKING, GEM_COLLECT_RANGE,
                    level_key_levels, level_key_name)
from .Locations import (Kind, BOSSES, EGG_CATALOG, SPARX_REALM_POWERS,
                        TABLE_ORDER, location_tables)
from .Names import s3
from .Options import GoalOptions


class Spyro3Game:
    key = "spyro3"
    name = "Spyro 3"
    requirable = False

    def __init__(self, world):
        self.world = world
        self.player = world.player
        self.multiworld = world.multiworld
        self.enable_gem_checks = True
        self.enable_skillpoint_checks = True
        self.sparx_powers = True
        self.egg_shuffle = True
        self.level_locks = False
        self.s3_goal = 0
        self.lockable_levels: List[str] = []
        self.region_levels: List[str] = []
        self.gates = Gates(load("spyro3"), self.player)
        self.gates.item_counts = {"eggs": self._egg_item_counts}
        self.location_names: Set[str] = set()
        self.level_key_pool_levels: List[str] = []

    def generate_early(self):
        self.enable_gem_checks = bool(self.world.options.spyro3_enable_gem_checks.value)
        self.enable_skillpoint_checks = bool(self.world.options.spyro3_enable_skillpoint_checks.value)
        self.sparx_powers = bool(self.world.options.spyro3_sparx_powers.value)
        self.egg_shuffle = bool(self.world.options.spyro3_egg_shuffle.value)
        self.level_locks = bool(self.world.options.spyro3_level_locks.value)
        self.s3_goal = int(self.world.options.spyro3_goal.value)
        self.requirable = self.s3_goal == GoalOptions.SORCERESS
        # The spawn level is a homeworld, so no key is precollected and all 33 keys shuffle.
        if self.level_locks:
            self.lockable_levels = list(level_key_levels)
            self.level_key_pool_levels = list(level_key_levels)

    def create_regions(self, menu: Region):
        regions: Dict[str, Region] = {}
        previous_hub = menu
        for level in TABLE_ORDER:
            if not location_tables[level] and level not in self.lockable_levels:
                # No checks and its portal is never locked; the region lands with its feature task.
                continue
            region = Region(s3(level), self.player, self.multiworld)
            for data in location_tables[level]:
                if data.kind is Kind.GEM and not self.enable_gem_checks:
                    continue
                if data.kind is Kind.SKILLPOINT and not self.enable_skillpoint_checks:
                    continue
                if data.kind is Kind.SPARX_POWER and not self.sparx_powers:
                    continue
                default_item = FILLER
                if data.kind is Kind.EGG and self.egg_shuffle:
                    default_item = DRAGON_EGG
                elif data.kind is Kind.SPARX_POWER:
                    default_item = s3(SPARX_REALM_POWERS[level][0].replace(" (Power)", ""))
                elif data.kind is Kind.BOSS:
                    default_item = s3(BOSSES[level][1])
                location = SRTLocation(self.player, data.name, self.world.location_name_to_id[data.name],
                                       region)
                if data.kind is Kind.BOSS:
                    # Locked event: the boss dungeon's egg record is the boss
                    # kill. Keep the item's real code; a None code crashes the
                    # server's LocationStore.
                    location.place_locked_item(self.world.create_item(default_item))
                region.locations.append(location)
                self.location_names.add(data.name)
            self.multiworld.regions.append(region)
            regions[level] = region
            self.region_levels.append(level)
            if self.gates.is_homeworld(level):
                parent, previous_hub = previous_hub, region
            else:
                parent = regions[self.gates.homeworld_of(level)]
            entrance = Entrance(self.player, s3(level), parent)
            parent.exits.append(entrance)
            entrance.connect(region)

    def create_pool(self) -> List[str]:
        names = [level_key_name(level) for level in self.level_key_pool_levels]
        if self.egg_shuffle:
            names += [DRAGON_EGG] * sum(len(eggs) for level, eggs in EGG_CATALOG.items()
                                        if level not in BOSSES)
        if self.sparx_powers:
            names += [GEM_COLLECT_RANGE, EXTRA_HIT_POINT, CHEST_BREAKING]
        return names

    def set_rules(self) -> None:
        # Every rule comes from the gate data in data/spyro3.json. Gates that
        # read other regions get all of them as indirect conditions.
        player = self.player
        multiworld = self.multiworld
        gates = self.gates
        for level, gate in gates.gates.items():
            if level not in self.region_levels:
                continue
            entrance = multiworld.get_entrance(s3(level), player)
            add_rule(entrance, gates.rule(gate))
            if gates.reads_regions(gate):
                for other in self.region_levels:
                    multiworld.register_indirect_condition(
                        multiworld.get_region(s3(other), player), entrance)
        for name, gate in gates.check_gates.items():
            if s3(name) in self.location_names:
                add_rule(multiworld.get_location(s3(name), player), gates.rule(gate))
        for level in self.region_levels:
            for data in location_tables[level]:
                if data.kind is Kind.GEM and data.name in self.location_names:
                    add_rule(multiworld.get_location(data.name, player),
                             gates.gem_rule(level, data.threshold))
        # Level Locks: each lockable level's entrance also needs its key, and
        # no key is precollected.
        if self.level_locks:
            for level in self.lockable_levels:
                add_rule(multiworld.get_entrance(s3(level), player),
                         lambda state, key=level_key_name(level): state.has(key, player))

    def is_complete(self, state) -> bool:
        if self.s3_goal == GoalOptions.SORCERESS:
            return state.has(S3Items.SORCERESS, self.player)
        return False

    def _egg_item_counts(self, state) -> int:
        """Under egg shuffle the egg portals count received Dragon Egg items
        plus reachable boss dungeons' eggs (boss kills are never shuffled, and
        Super Bonus Round needs 149 of 150); None falls back to gates.py's
        reachable-check count."""
        if self.egg_shuffle:
            bosses = sum(1 for level in BOSSES if state.can_reach_region(s3(level), self.player))
            return state.count(DRAGON_EGG, self.player) + bosses
        return None

    def slot_data(self) -> dict:
        goal_location = 0
        if self.s3_goal == GoalOptions.SORCERESS:
            goal_location = self.world.location_name_to_id[
                s3("Sorceress Lair: Sorceress Defeated")]
        # level_keys maps each lockable region to its key item name; the mod
        # locks regions whose key has not arrived yet. egg_gates carries the
        # vanilla egg requirements so the mod can re-tune the egg portals
        # under egg_shuffle.
        return {"options": {"enable_gem_checks": int(self.enable_gem_checks),
                            "enable_skillpoint_checks": int(self.enable_skillpoint_checks),
                            "sparx_powers": int(self.sparx_powers),
                            "goal": int(self.s3_goal),
                            "level_locks": int(self.level_locks),
                            "egg_shuffle": int(self.egg_shuffle)},
                "level_keys": {level: level_key_name(level) for level in self.lockable_levels},
                "egg_gates": {level: int(gate["eggs"]) for level, gate in self.gates.gates.items()
                              if "eggs" in gate},
                "goal_location": goal_location}