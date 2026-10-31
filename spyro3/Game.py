# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-31

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
from typing import List, Set

from BaseClasses import Region

from ..core import add_gate_rules, add_level_lock_rules, create_level_regions
from ..data import load
from ..gates import Gates
from . import Items as S3Items
from .Items import (DRAGON_EGG, EXTRA_HIT_POINT, CHEST_BREAKING, GEM_COLLECT_RANGE,
                    level_key_levels, level_key_name)
from .Locations import (Kind, BOSSES, EGG_CATALOG,
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
        self.enable_skillpoint_checks = bool(
            self.world.options.spyro3_enable_skillpoint_checks.value
        )
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
        skipped = set()
        if not self.enable_gem_checks:
            skipped.add(Kind.GEM)
        if not self.enable_skillpoint_checks:
            skipped.add(Kind.SKILLPOINT)
        if not self.sparx_powers:
            skipped.add(Kind.SPARX_POWER)
        self.region_levels = list(create_level_regions(
            self, menu, TABLE_ORDER, location_tables,
            prefix=s3, skipped=skipped, locked=self._locked_item))

    def _locked_item(self, level: str, data) -> str:
        """The item a location holds as a locked event, or None. The boss
        dungeon's egg record is the boss kill; keep its real item code, since a
        None code crashes the server's LocationStore."""
        if data.kind is Kind.BOSS:
            return s3(BOSSES[level][1])
        return None

    def create_pool(self) -> List[str]:
        names = [level_key_name(level) for level in self.level_key_pool_levels]
        if self.egg_shuffle:
            names += [DRAGON_EGG] * sum(len(eggs) for level, eggs in EGG_CATALOG.items()
                                        if level not in BOSSES)
        if self.sparx_powers:
            names += [GEM_COLLECT_RANGE, EXTRA_HIT_POINT, CHEST_BREAKING]
        return names

    def set_rules(self) -> None:
        # Every rule comes from the gate data in data/spyro3.json.
        add_gate_rules(self, s3, self.region_levels, location_tables, Kind.GEM)
        # Level Locks: each lockable level's entrance also needs its key, and
        # no key is precollected.
        if self.level_locks:
            add_level_lock_rules(self, s3, self.lockable_levels, level_key_name)

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
