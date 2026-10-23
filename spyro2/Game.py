# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

"""Spyro 2 (Ripto's Rage!) inside the Spyro Reignited Trilogy world.

Locations: orbs, talismans, the Money Bags ability purchases, boss-defeat
events, and gem checks. The region graph follows the game, and every gate
(talisman and orb doors, abilities, Money Bags payments, gem tiers) is data in
data/spyro2.json, turned into rules by ../gates.py.

Under spyro2_moneybags_abilities=sanity the Swim, Climb, and Headbash
abilities are shuffled items; under vanilla each purchase location holds its
ability as a locked event, so the ability rules apply in both modes.
spyro2_goal=ripto makes Spyro 2 requirable, meaning Ripto Defeated.

Under spyro2_orb_shuffle (default on) orb doors count received Orb items and
the mod reconciles the game's orb counter to them; off, they read the game's
own counter. Either way the doors' rules are the same gate data, only the
counting source moves.

Under spyro2_level_locks the mod locks 25 level portals behind shuffled level
key items. Homeworlds are never locked (the boss chain gates them), and the
spawn level Glimmer's key is precollected; the other 24 keys shuffle.
"""
from typing import List, Set

from BaseClasses import Region

from ..core import add_gate_rules, add_level_lock_rules, create_level_regions
from ..data import load
from ..gates import Gates
from . import Items as S2Items
from .Items import level_key_name, level_key_levels
from .Locations import (Kind, ability_item_name, check_levels, location_tables)
from .Names import s2
from .Options import MoneybagsAbilitiesOptions, S2GoalOptions

SWIM = S2Items.SWIM
CLIMB = S2Items.CLIMB
HEADBASH = S2Items.HEADBASH
ORB = S2Items.ORB
RIPTO = S2Items.RIPTO


class Spyro2Game:
    key = "spyro2"
    name = "Spyro 2"
    requirable = False

    def __init__(self, world):
        self.world = world
        self.player = world.player
        self.multiworld = world.multiworld
        self.enable_gem_checks = True
        self.enable_skillpoint_checks = True
        self.orb_shuffle = True
        self.moneybags_abilities = 0
        self.s2_goal = 0
        self.level_locks = False
        self.lockable_levels: List[str] = []
        self.level_key_pool_levels: List[str] = []
        self.gates = Gates(load("spyro2"), self.player)
        self.gates.item_counts = {"orbs": self._orb_item_counts}
        self.location_names: Set[str] = set()

    def generate_early(self):
        self.enable_gem_checks = bool(self.world.options.spyro2_enable_gem_checks.value)
        self.enable_skillpoint_checks = bool(
            self.world.options.spyro2_enable_skillpoint_checks.value
        )
        self.orb_shuffle = bool(self.world.options.spyro2_orb_shuffle.value)
        self.moneybags_abilities = int(self.world.options.spyro2_moneybags_abilities.value)
        self.s2_goal = int(self.world.options.spyro2_goal.value)
        self.level_locks = bool(self.world.options.spyro2_level_locks.value)
        self.requirable = self.s2_goal == S2GoalOptions.RIPTO
        # Glimmer is the spawn level, so its key is precollected and the other 24 keys shuffle.
        if self.level_locks:
            self.lockable_levels = list(level_key_levels)
            self.level_key_pool_levels = [
                level for level in self.lockable_levels if level != "Glimmer"]

    def create_regions(self, menu: Region):
        skipped = set()
        if not self.enable_gem_checks:
            skipped.add(Kind.GEM)
        if not self.enable_skillpoint_checks:
            skipped.add(Kind.SKILLPOINT)
        create_level_regions(self, menu, check_levels, location_tables,
                             prefix=s2, skipped=skipped, locked=self._locked_item)

    def _locked_item(self, level: str, data) -> str:
        """The item a location holds as a locked event, or None. Keep the real
        item code: a None code crashes the server's LocationStore."""
        if data.kind is Kind.BOSS:
            return s2(data.plain.split(": ")[-1])
        if (data.kind is Kind.ABILITY
                and self.moneybags_abilities != MoneybagsAbilitiesOptions.SANITY):
            return ability_item_name(data.plain.split(": ")[-1])
        return None

    def create_pool(self) -> List[str]:
        # Precollect the Glimmer key, the spawn level, like Spyro 1 does.
        if self.level_locks:
            self.multiworld.push_precollected(
                self.world.create_item(level_key_name("Glimmer")))
        names = [level_key_name(level) for level in self.level_key_pool_levels]
        if self.orb_shuffle:
            names += [ORB] * sum(
                1 for table in location_tables.values() for data in table
                if data.kind is Kind.ORB)
        if self.moneybags_abilities == MoneybagsAbilitiesOptions.SANITY:
            names += [SWIM, CLIMB, HEADBASH]
        return names

    def set_rules(self) -> None:
        # Every rule comes from the gate data in data/spyro2.json.
        add_gate_rules(self, s2, check_levels, location_tables, Kind.GEM)
        if self.level_locks:
            add_level_lock_rules(self, s2, self.lockable_levels, level_key_name)

    def _orb_item_counts(self, state) -> int:
        """Under orb shuffle the orb doors count received Orb items, else None
        falls back to gates.py's reachable-check count."""
        if self.orb_shuffle:
            return state.count(ORB, self.player)
        return None

    def is_complete(self, state) -> bool:
        if self.s2_goal == S2GoalOptions.RIPTO:
            return state.has(RIPTO, self.player)
        return False

    def slot_data(self) -> dict:
        goal_location = 0
        if self.s2_goal == S2GoalOptions.RIPTO:
            goal_location = self.world.location_name_to_id[s2("Ripto's Arena: Ripto Defeated")]
        # level_keys maps each lockable region to its key item name; the mod
        # locks regions whose key has not arrived yet. Precollected items
        # arrive in the backlog, so Glimmer is included.
        return {"options": {"enable_gem_checks": int(self.enable_gem_checks),
                            "enable_skillpoint_checks": int(self.enable_skillpoint_checks),
                            "orb_shuffle": int(self.orb_shuffle),
                            "moneybags_abilities": int(self.moneybags_abilities),
                            "goal": int(self.s2_goal),
                            "level_locks": int(self.level_locks)},
                "level_keys": {level: level_key_name(level) for level in self.lockable_levels},
                "goal_location": goal_location}
