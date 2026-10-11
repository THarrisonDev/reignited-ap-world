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
from typing import Dict, List, Set

from BaseClasses import Entrance, Region
from worlds.generic.Rules import add_rule

from ..core import SRTLocation
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
        self.enable_skillpoint_checks = bool(self.world.options.spyro2_enable_skillpoint_checks.value)
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
        regions: Dict[str, Region] = {}
        previous_hub = menu
        for level in check_levels:
            region = Region(s2(level), self.player, self.multiworld)
            for data in location_tables[level]:
                if data.kind is Kind.GEM and not self.enable_gem_checks:
                    continue
                if data.kind is Kind.SKILLPOINT and not self.enable_skillpoint_checks:
                    continue
                location = SRTLocation(self.player, data.name, self.world.location_name_to_id[data.name],
                                       region)
                # Keep the item's real code: a None code crashes the server's LocationStore.
                if data.kind is Kind.BOSS:
                    location.place_locked_item(self.world.create_item(s2(data.plain.split(": ")[-1])))
                elif data.kind is Kind.ABILITY and \
                        self.moneybags_abilities != MoneybagsAbilitiesOptions.SANITY:
                    location.place_locked_item(self.world.create_item(ability_item_name(data.plain.split(": ")[-1])))
                region.locations.append(location)
                self.location_names.add(data.name)
            self.multiworld.regions.append(region)
            regions[level] = region
            if self.gates.is_homeworld(level):
                parent, previous_hub = previous_hub, region
            else:
                parent = regions[self.gates.homeworld_of(level)]
            entrance = Entrance(self.player, s2(level), parent)
            parent.exits.append(entrance)
            entrance.connect(region)

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
        # Every rule comes from the gate data in data/spyro2.json. Gates that
        # read other regions get all of them as indirect conditions.
        player = self.player
        multiworld = self.multiworld
        gates = self.gates
        for level, gate in gates.gates.items():
            entrance = multiworld.get_entrance(s2(level), player)
            add_rule(entrance, gates.rule(gate))
            if gates.reads_regions(gate):
                for other in check_levels:
                    multiworld.register_indirect_condition(
                        multiworld.get_region(s2(other), player), entrance)
        for payment in gates.payments:
            if "location" in payment:
                add_rule(multiworld.get_location(s2(payment["location"]), player),
                         gates.payment_rule(payment["name"]))
        for name, gate in gates.check_gates.items():
            if s2(name) in self.location_names:
                add_rule(multiworld.get_location(s2(name), player), gates.rule(gate))
        for level in check_levels:
            for data in location_tables[level]:
                if data.kind is Kind.GEM and data.name in self.location_names:
                    add_rule(multiworld.get_location(data.name, player),
                             gates.gem_rule(level, data.threshold))

        # Level Locks: each lockable level's entrance also needs its key.
        if self.level_locks:
            for level in self.lockable_levels:
                add_rule(multiworld.get_entrance(s2(level), player),
                         lambda state, key=level_key_name(level): state.has(key, player))

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
