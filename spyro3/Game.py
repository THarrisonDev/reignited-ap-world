"""Spyro 3 (Year of the Dragon) inside the Spyro Reignited Trilogy world.

Locations: 25/50/75/100% gem checks for the 29 gem-bearing levels, the 146
save-named dragon eggs, the 4 boss-defeat events and the 20 skill-point checks.
The region graph follows the game: Menu -> Sunrise Spring -> Midday Gardens ->
Evening Lake -> Midnight Mountain, and every level connects from the homeworld
its portal stands in. What the game demands on top of that — the boss chain,
the egg portals, the Sparx realm chain, the companion and Money Bags payments,
the eggs behind paid doors, gem tiers — is data in data/spyro3.json, turned
into rules by ../gates.py (spyrosim reads the same data). Egg doors count the
eggs the player can catch, boss kills included (each boss dungeon's egg record
is the kill): they read the save's egg records, which the Dragon Egg items
never touch (the debug egg counter is display-only, live-proven). Eggs are
ALWAYS checks (each one is named in the save); only the paid doors give some
of them rules of their own. The boss events replace the boss dungeons' egg rows (there is no
EIT_S3Boss record in saves — the boss dungeon's named egg record IS the boss
kill, which checkd's egg scan already drops). The speedway flight checks land
with their feature task. spyro3_goal=sorceress makes Spyro 3 requirable:
complete means Sorceress Defeated. Abilities are granted by story in Spyro 3
(they carry over from Spyro 2), so there are no ability items.

Under spyro3_sparx_powers the 3 Sparx realm completions (Crawdad Farm, Starfish
Reef, Bugbot Factory) become checks whose default items are the 3 useful Sparx
power items; off, the rows disappear (they are option-gated like the skill
points).

spyro3_egg_shuffle only decides whether the egg checks release items: on, each
egg location's default item is a shuffled progression "Spyro 3: Dragon Egg"
(generic, 146 copies); off, eggs are vanilla checks whose default item is
FILLER.

spyro3_level_locks gates the 33 sub-levels whose portals the mod locks (every
sub-level's portal stands in one of the 4 homeworlds, Bugbot Factory's in
Midnight Mountain included) behind shuffled "Spyro 3: <Level> Key" items. The
homeworlds themselves are never locked — their access is the game's own boss
chain (balloon to Midday Gardens after Buzz, whirligig to Evening Lake after
Spike, rocket to Midnight Mountain after Scorch), the same reason Spyro 1
never locks its homeworlds — and the spawn level, Sunrise Spring, is a
homeworld, so unlike Spyro 2 there is no precollected key: all 33 shuffle.
"""
from typing import Dict, List, Set

from BaseClasses import Entrance, Region
from worlds.generic.Rules import add_rule

from ..core import FILLER, SRTLocation
from ..data import load
from ..gates import Gates
from . import Items as S3Items
from .Items import DRAGON_EGG, EXTRA_HIT_POINT, CHEST_BREAKING, GEM_COLLECT_RANGE, level_key_levels, level_key_name
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
        # No starting-unlocked option: the spawn level, Sunrise Spring, is a
        # homeworld and homeworlds are never locked, so all 33 keys shuffle.
        if self.level_locks:
            self.lockable_levels = list(level_key_levels)
            self.level_key_pool_levels = list(level_key_levels)

    def create_regions(self, menu: Region):
        regions: Dict[str, Region] = {}
        previous_hub = menu
        for level in TABLE_ORDER:
            if not location_tables[level] and level not in self.lockable_levels:
                # No checks, and Level Locks never locks its portal: the region
                # lands with its feature task (flight checks).
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
                    # Locked event: the boss dungeon's egg record (data.save_key)
                    # is the boss kill — the check fires when checkd scans it.
                    # Keep the event item's real code: stock AP serializes every
                    # addressed location as (code, player, flags) and a None
                    # code crashes the server's LocationStore.
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
        # Every rule comes from the gate data in data/spyro3.json (see
        # gates.py): the boss chain between homeworlds, the egg portals, the
        # companion and Money Bags payments, single checks and gem tiers.
        # Gates that count reachable eggs or gems read every region, so those
        # entrances get them all as indirect conditions.
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
        # Level Locks: every lockable level's entrance also needs its Key. No
        # key is precollected (the spawn is a homeworld), so every key rule
        # binds from the start.
        if self.level_locks:
            for level in self.lockable_levels:
                add_rule(multiworld.get_entrance(s3(level), player),
                         lambda state, key=level_key_name(level): state.has(key, player))

    def is_complete(self, state) -> bool:
        if self.s3_goal == GoalOptions.SORCERESS:
            return state.has(S3Items.SORCERESS, self.player)
        return False

    def slot_data(self) -> dict:
        goal_location = 0
        if self.s3_goal == GoalOptions.SORCERESS:
            goal_location = self.world.location_name_to_id[
                s3("Sorceress Lair: Sorceress Defeated")]
        # level_keys: region -> key item name, all lockable levels — the mod
        # locks the regions whose key it has not received yet.
        return {"options": {"enable_gem_checks": int(self.enable_gem_checks),
                            "enable_skillpoint_checks": int(self.enable_skillpoint_checks),
                            "sparx_powers": int(self.sparx_powers),
                            "goal": int(self.s3_goal),
                            "level_locks": int(self.level_locks),
                            "egg_shuffle": int(self.egg_shuffle)},
                "level_keys": {level: level_key_name(level) for level in self.lockable_levels},
                "goal_location": goal_location}