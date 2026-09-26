"""Spyro 2 (Ripto's Rage!) inside the Spyro Reignited Trilogy world.

Locations: orbs, talismans, the three Money Bags ability purchases, the three
boss-defeat events and gem checks. The region graph follows the game: Menu ->
Summer Forest -> Autumn Plains -> Winter Tundra, each homeworld opening behind
the previous one's boss, and every level connects from the homeworld its portal
stands in. What the game demands on top of that — talisman and orb doors, the
professor door, abilities, all twelve Money Bags payments, gem tiers — is data
in data/spyro2.json, turned into rules by ../gates.py (spyrosim reads the same
data).

Under spyro2_moneybags_abilities=sanity Swim/Climb/Headbash are shuffled items
(the mod revokes a purchase until the item arrives); under vanilla each
purchase location holds its ability as a locked event, so the ability rules
apply in both modes. spyro2_goal=ripto makes Spyro 2 requirable: complete
means Ripto Defeated.

spyro2_level_locks gates the 25 levels whose portals the mod locks (all portals
live in the 3 homeworlds and lead out of them) behind shuffled "Spyro 2:
<Level> Key" items. The homeworlds themselves are never locked — their access
is the boss chain above, the same reason Spyro 1 never locks its homeworlds —
and Dragon Shores is a post-game bonus world with no checks. Glimmer, the spawn
level, gets its key precollected; the other 24 are shuffled.
"""
from typing import Dict, List, Set

from BaseClasses import Entrance, Region
from worlds.generic.Rules import add_rule

from ..core import SRTLocation
from ..data import load
from ..gates import Gates
from . import Items as S2Items
from .Items import level_key_name, level_key_levels
from .Locations import (ABILITY, BOSS, GEM, SKILLPOINT, ability_item_name, check_levels,
                        location_tables)
from .Names import s2
from .Options import MoneybagsAbilitiesOptions, S2GoalOptions

SWIM = S2Items.SWIM
CLIMB = S2Items.CLIMB
HEADBASH = S2Items.HEADBASH
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
        self.moneybags_abilities = 0
        self.s2_goal = 0
        self.level_locks = False
        self.lockable_levels: List[str] = []
        self.level_key_pool_levels: List[str] = []
        self.gates = Gates(load("spyro2"), self.player)
        self.location_names: Set[str] = set()

    def generate_early(self):
        self.enable_gem_checks = bool(self.world.options.spyro2_enable_gem_checks.value)
        self.enable_skillpoint_checks = bool(self.world.options.spyro2_enable_skillpoint_checks.value)
        self.moneybags_abilities = int(self.world.options.spyro2_moneybags_abilities.value)
        self.s2_goal = int(self.world.options.spyro2_goal.value)
        self.level_locks = bool(self.world.options.spyro2_level_locks.value)
        self.requirable = self.s2_goal == S2GoalOptions.RIPTO
        # No starting-unlocked option: Glimmer is the spawn level, so its key is
        # precollected and the other 24 shuffle into the pool.
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
                if data.kind == GEM and not self.enable_gem_checks:
                    continue
                if data.kind == SKILLPOINT and not self.enable_skillpoint_checks:
                    continue
                location = SRTLocation(self.player, data.name, self.world.location_name_to_id[data.name],
                                       region)
                # Locked events keep the item's real code: stock AP serializes
                # every addressed location as (code, player, flags) and a None
                # code crashes the server's LocationStore. Boss checks fire from
                # the save's EIT_S2Boss record; vanilla purchases from the
                # ability's own save record.
                if data.kind == BOSS:
                    location.place_locked_item(self.world.create_item(s2(data.name.split(": ")[-1])))
                elif data.kind == ABILITY and \
                        self.moneybags_abilities != MoneybagsAbilitiesOptions.SANITY:
                    location.place_locked_item(self.world.create_item(ability_item_name(data.name)))
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
        # Level Locks precollects the Glimmer key (the spawn level) like
        # Spyro 1 precollects its starting keys inside create_pool.
        if self.level_locks:
            self.multiworld.push_precollected(
                self.world.create_item(level_key_name("Glimmer")))
        keys = [level_key_name(level) for level in self.level_key_pool_levels]
        if self.moneybags_abilities != MoneybagsAbilitiesOptions.SANITY:
            return keys
        return [SWIM, CLIMB, HEADBASH] + keys

    def set_rules(self) -> None:
        # Every rule comes from the gate data in data/spyro2.json (see
        # gates.py): level entrances, single checks, gem tiers and the Money
        # Bags purchases. Gates that count reachable locations or gems read
        # every region, so those entrances get them all as indirect conditions.
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
                if data.kind == GEM and data.name in self.location_names:
                    add_rule(multiworld.get_location(data.name, player),
                             gates.gem_rule(level, data.threshold))

        # Level Locks: every lockable level's entrance also needs its Key.
        # Glimmer's key is precollected, so its rule is always satisfied.
        if self.level_locks:
            for level in self.lockable_levels:
                add_rule(multiworld.get_entrance(s2(level), player),
                         lambda state, key=level_key_name(level): state.has(key, player))

    def is_complete(self, state) -> bool:
        if self.s2_goal == S2GoalOptions.RIPTO:
            return state.has(RIPTO, self.player)
        return False

    def slot_data(self) -> dict:
        goal_location = 0
        if self.s2_goal == S2GoalOptions.RIPTO:
            goal_location = self.world.location_name_to_id[s2("Ripto's Arena: Ripto Defeated")]
        # level_keys: region -> key item name, all lockable levels including the
        # precollected Glimmer key — the mod locks the regions whose key it has
        # not received yet, and precollected items arrive in the backlog.
        return {"options": {"enable_gem_checks": int(self.enable_gem_checks),
                            "enable_skillpoint_checks": int(self.enable_skillpoint_checks),
                            "moneybags_abilities": int(self.moneybags_abilities),
                            "goal": int(self.s2_goal),
                            "level_locks": int(self.level_locks)},
                "level_keys": {level: level_key_name(level) for level in self.lockable_levels},
                "goal_location": goal_location}
