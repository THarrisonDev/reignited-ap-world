# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

"""Spyro 1 (Spyro the Dragon) inside the Spyro Reignited Trilogy world.

Game data (all verified):
  - 80 dragons (74 unique + 6 re-rescues), 12 eggs, 14,000 gems (12,000 + 2,000 Loot)
  - 5 homeworlds + Gnorc Gnexus; balloonists: Marco(10 dragons), Gosnold(1200 gems),
    Tuco(5 eggs), Cray(50 dragons), Amos(6000 gems)
  - Boss portals: Toasty needs 1 Artisan realm done; Twilight Harbor needs Gnorc Cove +
    Delbin; Gnasty Gnorc needs Twilight Harbor done.
  - Gnasty's Loot: needs all dragons/eggs + 12,000 gems (before Loot gems).

Levels, their checks, gem totals and balloonist requirements all come from
Levels.py; this module only turns them into regions, rules and slot data.
Region objects carry the "Spyro 1: " prefix; the tables here and the slot data
use plain level names ("Stone Hill"), since slot data is already per game.
"""

from typing import Dict, List

from BaseClasses import Entrance, Region
from worlds.generic.Rules import add_rule, set_rule

from ..core import SRTLocation
from .Items import (
    DRAGON,
    DRAGON_EGG,
    level_key_levels,
    level_key_name,
    starting_unlock_candidates,
)
from .Levels import (
    CheckType,
    LevelType,
    Requirement,
    RequirementType,
    Spyro1Level,
    Spyro1Levels,
)
from .Locations import vanilla_item
from .Names import s1
from .Options import BalloonistGateOptions, DragonShuffleOptions, GoalOptions

SLOT_OPTIONS = (
    "goal",
    "balloonist_gates",
    "dragon_shuffle",
    "egg_shuffle",
    "enable_gem_checks",
    "enable_skillpoint_checks",
    "enable_flight_checks",
    "level_locks",
    "starting_unlocked_levels",
)


class Spyro1Game:
    key = "spyro1"
    name = "Spyro 1"

    def __init__(self, world):
        self.world = world
        self.player = world.player
        self.multiworld = world.multiworld
        self.generation_options: Dict[str, int] = {}
        # Balloonist requirement per homeworld (vanilla, or re-rolled when shuffled).
        self.gate_requirements: Dict[str, Requirement] = {
            hub.name: hub.requirement for hub in Spyro1Levels if hub.requirement
        }
        self.lockable_levels: List[str] = []
        self.starting_unlocked_levels: List[str] = []
        self.level_key_pool_levels: List[str] = []
        # Levels (hubs included) that get a region this seed, and what each holds.
        self.levels: List[Spyro1Level] = []
        self._gems_in: Dict[str, int] = {}
        self._eggs_in: Dict[str, int] = {}
        self._dragons_in: Dict[str, int] = {}

    # ------------------------------------------------------------------
    # Option handling
    # ------------------------------------------------------------------
    def generate_early(self):
        options = self.world.options
        opts = self.generation_options
        opts["goal"] = options.spyro1_goal.value
        opts["balloonist_gates"] = options.spyro1_balloonist_gates.value
        opts["dragon_shuffle"] = options.spyro1_dragon_shuffle.value
        opts["egg_shuffle"] = options.spyro1_egg_shuffle.value
        opts["enable_gem_checks"] = options.spyro1_enable_gem_checks.value
        opts["enable_skillpoint_checks"] = int(
            options.spyro1_enable_skillpoint_checks.value
        )
        opts["enable_flight_checks"] = options.spyro1_enable_flight_checks.value
        opts["level_locks"] = int(options.spyro1_level_locks.value)
        opts["starting_unlocked_levels"] = int(
            options.spyro1_starting_unlocked_levels.value
        )

        is_ut = getattr(self.multiworld, "generation_is_fake", False)

        if opts["balloonist_gates"] == BalloonistGateOptions.SHUFFLED and not is_ut:
            self._shuffle_gate_requirements()

        # Gnasty's Loot goal needs Loot region and gem checks always on
        if opts["goal"] == GoalOptions.GNASTYS_LOOT and not opts["enable_gem_checks"]:
            opts["enable_gem_checks"] = True

        if opts["level_locks"]:
            self.lockable_levels = [
                level
                for level in level_key_levels
                if level != "Gnasty's Loot" or opts["goal"] == GoalOptions.GNASTYS_LOOT
            ]
            self.starting_unlocked_levels = self.multiworld.random.sample(
                starting_unlock_candidates, opts["starting_unlocked_levels"]
            )
            self.level_key_pool_levels = [
                level
                for level in self.lockable_levels
                if level not in self.starting_unlocked_levels
            ]

    def _gate_ceilings(self) -> Dict[str, int]:
        """The most of each gate's resource obtainable before that homeworld is
        entered: every level of every earlier homeworld. A balloonist is only
        ever raised to this number, so asking for more would demand what the
        seed cannot give."""
        counts = {
            RequirementType.DRAGONS: 0,
            RequirementType.GEMS: 0,
            RequirementType.EGGS: 0,
        }
        ceilings: Dict[str, int] = {}
        for hub in Spyro1Levels:
            if hub.requirement:
                ceilings[hub.name] = counts[hub.requirement.type]
            for level in (hub, *hub.levels):
                counts[RequirementType.DRAGONS] += level.dragons
                counts[RequirementType.EGGS] += level.dragon_eggs
                counts[RequirementType.GEMS] += level.gem_total
        return ceilings

    def _shuffle_gate_requirements(self):
        """Shuffled mode: re-roll each balloonist to a random requirement between
        its vanilla number and the most of that resource obtainable before the
        homeworld is entered. The mod only ever raises a balloonist, so vanilla
        is the floor; the ceiling keeps the seed beatable."""
        random = self.multiworld.random
        ceilings = self._gate_ceilings()
        shuffled: Dict[str, Requirement] = {}
        for homeworld, req in self.gate_requirements.items():
            ceiling = ceilings[homeworld]
            if ceiling < req.needed:
                raise ValueError(
                    f"spyro1: {homeworld} balloonist needs {req.needed} "
                    f"{req.type.name.lower()}, but only {ceiling} is obtainable "
                    f"before it — the gate would be unreachable"
                )
            shuffled[homeworld] = Requirement(req.type, random.randint(req.needed, ceiling))
        self.gate_requirements = shuffled

    # ------------------------------------------------------------------
    # Regions
    # ------------------------------------------------------------------
    def create_regions(self, menu: Region):
        # Gnasty's Loot (the one bonus level) is only a region under the Loot goal;
        # its gem checks only exist for that goal.
        loot_goal = self.generation_options["goal"] == GoalOptions.GNASTYS_LOOT
        self.levels = [
            level
            for hub in Spyro1Levels
            for level in (hub, *hub.levels)
            if level.type != LevelType.BONUS or loot_goal
        ]
        self._gems_in = {level.name: level.gem_total for level in self.levels}
        self._eggs_in = {level.name: level.dragon_eggs for level in self.levels}
        self._dragons_in = {level.name: level.dragons for level in self.levels}

        regions = {
            level.name: self._create_region(level)
            for level in self.levels
        }

        def connect(parent: Region, child: Region):
            entrance = Entrance(self.player, child.name, parent)
            parent.exits.append(entrance)
            entrance.connect(child)

        # Menu -> first hub -> next hub ...; each hub -> its levels.
        previous = menu
        for hub in Spyro1Levels:
            connect(previous, regions[hub.name])
            for level in hub.levels:
                if level.name in regions:
                    connect(regions[hub.name], regions[level.name])
            previous = regions[hub.name]

    def _create_region(self, level: Spyro1Level) -> Region:
        opts = self.generation_options
        region = Region(s1(level.name), self.player, self.multiworld)
        for check in level.checks:
            if check.type == CheckType.GEM_CHECK and not opts["enable_gem_checks"]:
                continue
            if (
                check.type == CheckType.SKILL_POINT
                and not opts["enable_skillpoint_checks"]
            ):
                continue
            # A flight's Complete check is optional side content: it holds a
            # shuffled item and needs only the flight region (clearing the 4
            # target sets needs no item). The flight region itself stays either
            # way: its gems count toward the balloonists' gem gates.
            is_flight_check = check.type == CheckType.EVENT and level.type == LevelType.FLIGHT
            if is_flight_check and not opts["enable_flight_checks"]:
                continue
            name = s1(check.name)
            location = SRTLocation(
                self.player, name, self.world.location_name_to_id[name], region
            )
            if check.type == CheckType.EVENT and not is_flight_check:
                # Level/boss events hold a locked item of their own name; they
                # are checked when the boss dies / level completes. Event codes
                # are unused network-side (the client reports the location, not
                # the item); logic matches on the item NAME. See
                # core.SRTLocation for why the event item keeps a real code.
                location.place_locked_item(self.world.create_item(vanilla_item(check)))
            region.locations.append(location)
        self.multiworld.regions.append(region)
        return region

    # ------------------------------------------------------------------
    # Items
    # ------------------------------------------------------------------
    def create_pool(self) -> List[str]:
        """Precollects the starting level keys; returns this game's progression item names."""
        for level in self.starting_unlocked_levels:
            self.multiworld.push_precollected(
                self.world.create_item(level_key_name(level))
            )

        opts = self.generation_options
        names: List[str] = []
        if opts["dragon_shuffle"] == DragonShuffleOptions.DRAGONSANITY:
            names += [DRAGON] * sum(self._dragons_in.values())
        if opts["egg_shuffle"]:
            names += [DRAGON_EGG] * sum(self._eggs_in.values())
        names += [level_key_name(level) for level in self.level_key_pool_levels]
        return names

    # ------------------------------------------------------------------
    # Rules / logic
    # ------------------------------------------------------------------
    def _reachable_total(self, state, counts: Dict[str, int]) -> int:
        return sum(
            n
            for region_name, n in counts.items()
            if state.can_reach_region(s1(region_name), self.player)
        )

    def _count_dragons(self, state) -> int:
        if self.generation_options["dragon_shuffle"] == DragonShuffleOptions.DRAGONSANITY:
            return state.count(DRAGON, self.player)
        return self._reachable_total(state, self._dragons_in)

    def set_rules(self) -> None:
        player = self.player
        multiworld = self.multiworld

        # Balloonists read the game's own counters, so a gate counts what the
        # player can actually hold. Gems and eggs
        # come only from reachable levels: the mod syncs no gem or egg counter,
        # so Dragon Egg items never stand in for eggs. Dragons are Dragon items
        # under dragonsanity (the mod reconciles the counter to them), otherwise
        # the dragons in reachable levels.
        def meets_gate(state, homeworld: str) -> bool:
            req = self.gate_requirements[homeworld]
            if req.type == RequirementType.GEMS:
                return self._reachable_total(state, self._gems_in) >= req.needed
            if req.type == RequirementType.EGGS:
                return self._reachable_total(state, self._eggs_in) >= req.needed
            return self._count_dragons(state) >= req.needed

        # A gate depends on every level's reachability, so each level is an
        # indirect condition of each homeworld entrance.
        for homeworld in self.gate_requirements:
            entrance = multiworld.get_entrance(s1(homeworld), player)
            set_rule(entrance, lambda state, hw=homeworld: meets_gate(state, hw))
            for level in self.levels:
                multiworld.register_indirect_condition(
                    multiworld.get_region(s1(level.name), player), entrance
                )

        # Boss portals gate the whole level, so the rules sit on its entrance:
        #   Toasty needs one Artisans realm complete.
        #   Twilight Harbor needs Gnorc Cove complete and Delbin freed (a Gnorc
        #     Gnexus dragon, so that hub is an indirect condition).
        #   Gnasty Gnorc needs Twilight Harbor complete.
        #   Gnasty's Loot (a region only under the Loot goal) needs Gnasty
        #     defeated, every dragon and egg, and the 12,000 gems outside the
        #     Loot; it counts every level, so each is an indirect condition.
        add_rule(
            multiworld.get_entrance(s1("Toasty"), player),
            lambda state: (
                state.has(s1("Stone Hill Complete"), player)
                or state.has(s1("Dark Hollow Complete"), player)
                or state.has(s1("Town Square Complete"), player)
            ),
        )
        twilight = multiworld.get_entrance(s1("Twilight Harbor"), player)
        add_rule(
            twilight,
            lambda state: (
                state.has(s1("Gnorc Cove Complete"), player)
                and state.can_reach_location(s1("Gnorc Gnexus: Free Delbin"), player)
            ),
        )
        multiworld.register_indirect_condition(
            multiworld.get_region(s1("Gnorc Gnexus"), player), twilight
        )
        add_rule(
            multiworld.get_entrance(s1("Gnasty Gnorc"), player),
            lambda state: state.has(s1("Twilight Harbor Complete"), player),
        )
        if "Gnasty's Loot" in self._gems_in:
            gems_outside = {name: n for name, n in self._gems_in.items() if name != "Gnasty's Loot"}
            loot = multiworld.get_entrance(s1("Gnasty's Loot"), player)
            add_rule(
                loot,
                lambda state: (
                    state.has(s1("Gnasty Gnorc Defeated"), player)
                    and self._count_dragons(state) >= sum(self._dragons_in.values())
                    and self._reachable_total(state, self._eggs_in) >= sum(self._eggs_in.values())
                    and self._reachable_total(state, gems_outside) >= sum(gems_outside.values())
                ),
            )
            for level in self.levels:
                multiworld.register_indirect_condition(
                    multiworld.get_region(s1(level.name), player), loot
                )

        # Level Locks: each lockable level's portal entrance also needs its Key.
        for level in self.lockable_levels:
            add_rule(
                multiworld.get_entrance(s1(level), player),
                lambda state, key=level_key_name(level): state.has(key, player),
            )

    def is_complete(self, state) -> bool:
        goal = self.generation_options["goal"]
        if goal == GoalOptions.GNASTY:
            return state.has(s1("Gnasty Gnorc Defeated"), self.player)
        if goal == GoalOptions.ALL_DRAGONS:
            return (
                state.has(s1("Gnasty Gnorc Defeated"), self.player)
                and self._count_dragons(state) >= sum(self._dragons_in.values())
            )
        if goal == GoalOptions.GNASTYS_LOOT:
            return state.has(s1("Gnasty's Loot Complete"), self.player)
        return False

    # ------------------------------------------------------------------
    # Slot data for the client (under slot_data["games"]["spyro1"])
    # ------------------------------------------------------------------
    def slot_data(self) -> dict:
        # goal_location: the client reports GOAL when this location's event item
        # is received. ALL_DRAGONS emits 0: the 80-dragon part is a counter the
        # client cannot verify reliably, so v1 keeps S1's goal reporting to the
        # location-event goals.
        goal_location = 0
        goal = self.generation_options["goal"]
        if goal == GoalOptions.GNASTY:
            goal_location = self.world.location_name_to_id[s1("Gnasty Gnorc Defeated")]
        elif goal == GoalOptions.GNASTYS_LOOT:
            goal_location = self.world.location_name_to_id[s1("Gnasty's Loot Complete")]
        return {
            "options": {name: self.generation_options[name] for name in SLOT_OPTIONS},
            "level_keys": {
                level: level_key_name(level) for level in self.lockable_levels
            },
            "gate_requirements": {
                homeworld: {"type": req.type.name.lower(), "needed": req.needed}
                for homeworld, req in self.gate_requirements.items()
            },
            "goal_location": goal_location,
        }
