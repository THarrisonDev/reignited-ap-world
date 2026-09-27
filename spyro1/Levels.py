"""Spyro 1 level/check views over the JSON data (world/data/spyro1.json).

The JSON is the single source of truth; this module only re-shapes it into the
named tuples the game module consumes (region graph, rules, slot data). Names
here are PLAIN ("Stone Hill: Free Lindar") — s1() adds the "Spyro 1: " prefix
where Archipelago names are built. Unique check IDs come straight from the
JSON (hand-written, never reused); gem-threshold and event checks, and their
IDs, are derived by the data engine (world/data), which the client generator
shares.
"""
from typing import List, NamedTuple

from ..data import CheckType, LevelType, RequirementType, load


class Requirement(NamedTuple):
    type: RequirementType
    needed: int


class Check(NamedTuple):
    id: int
    name: str
    type: CheckType


_data = load("spyro1")


class Spyro1Level:
    """One level (hub or sub-level). `checks` is its unique checks plus the
    gem-threshold and event checks the data engine derives."""

    def __init__(self, raw: dict):
        self._raw = raw
        self.name = raw["name"]
        self.type = LevelType(raw["type"])
        self.id = raw["id"]
        self.gem_total = raw["gemTotal"]
        self.hub = raw.get("hub")
        self.gate = raw.get("gate")
        self.levels: tuple["Spyro1Level", ...] = ()
        # Balloonist requirement, hubs only (set by the loader below).
        self.requirement: Requirement | None = None

    @property
    def gem_checks(self) -> list:
        return [Check(check_id, name, CheckType.GEM_CHECK)
                for check_id, name, _pct in _data.gem_threshold_checks(self._raw)]

    @property
    def event_check(self) -> Check | None:
        event = _data.event_check(self._raw)
        return Check(*event, CheckType.EVENT) if event else None

    @property
    def unique_checks(self) -> list[Check]:
        return [Check(c["id"], c["name"], CheckType(c["type"]))
                for c in self._raw["checks"]]

    @property
    def checks(self) -> tuple[Check, ...]:
        event = self.event_check
        return tuple(self.unique_checks + self.gem_checks
                     + ([event] if event else []))

    @property
    def dragons(self) -> int:
        return sum(1 for check in self.checks if check.type == CheckType.DRAGON)

    @property
    def dragon_eggs(self) -> int:
        return sum(1 for check in self.checks if check.type == CheckType.EGG)


_by_name = {lvl["name"]: lvl for lvl in _data.raw["levels"]}


Spyro1Levels: List[Spyro1Level] = []
for _raw in _data.raw["levels"]:
    if LevelType(_raw["type"]) is LevelType.HUB:
        hub = Spyro1Level(_raw)
        gate = _data.gates.get(hub.name)
        if gate:
            hub.requirement = Requirement(RequirementType(gate["type"]), gate["needed"])
        hub.levels = tuple(
            Spyro1Level(_by_name[lvl["name"]])
            for lvl in _data.raw["levels"] if lvl.get("hub") == hub.name
        )
        Spyro1Levels.append(hub)

# Gnasty's Loot (the one bonus level): Menu-reachable, belongs to no hub.
_loot = [lvl for lvl in _data.raw["levels"]
         if LevelType(lvl["type"]) is LevelType.BONUS and "hub" not in lvl]
if _loot:
    _loot_raw = _loot[0]
    _previous_hub = Spyro1Levels[-1]
    _loot_level = Spyro1Level(_loot_raw)
    _previous_hub.levels = (*_previous_hub.levels, _loot_level)


def iter_levels() -> list[Spyro1Level]:
    """All levels, flattened, in order (hubs followed by their levels)."""
    result: list[Spyro1Level] = []
    for hub in Spyro1Levels:
        result.append(hub)
        result.extend(hub.levels)
    return result


def iter_checks() -> list[Check]:
    """Every check, level by level."""
    return [check for lvl in iter_levels() for check in lvl.checks]


assert sum(lvl.gem_total for lvl in iter_levels()) == 14000
assert sum(lvl.dragons for lvl in iter_levels()) == 80
assert sum(lvl.dragon_eggs for lvl in iter_levels()) == 12
assert len({lvl.id for lvl in iter_levels()}) == len(iter_levels()), "duplicate level ID"
assert len({check.id for check in iter_checks()}) == len(iter_checks()), (
    "duplicate check ID"
)
assert len({check.name for check in iter_checks()}) == len(iter_checks()), (
    "duplicate check name"
)