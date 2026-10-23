# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

"""Spyro 1 locations: the Archipelago view of the checks in Levels.py. Location
and item names carry the "Spyro 1: " prefix; IDs come straight from the checks.

Skill-point checks are option-gated side content: the save's global
EIT_SkillPoint record holds one nameless float per earned point, each float the
ESkillPoint enum value (S1 = 1..14)."""
from .Levels import Check, CheckType, LevelType, iter_checks, iter_levels
from .Names import s1


def _flight_checks() -> set:
    return {level.event_check.name for level in iter_levels() if level.type == LevelType.FLIGHT}


FLIGHT_CHECKS = _flight_checks()


def vanilla_item(check: Check) -> str:
    """The locked item a level/boss completion event holds: an item of the
    event's own name. Only called for a non-flight event — a flight's Complete
    check holds a shuffled item instead."""
    return s1(check.name)


def get_name_to_id() -> dict:
    return {s1(check.name): check.id for check in iter_checks()}


def _names(checks) -> set:
    return {s1(check.name) for check in checks}


def _of_type(check_type: CheckType) -> set:
    return _names(check for check in iter_checks() if check.type == check_type)


location_name_groups = {
    s1("Dragons"): _of_type(CheckType.DRAGON),
    s1("Eggs"): _of_type(CheckType.EGG),
    s1("Gem Checks"): _of_type(CheckType.GEM_CHECK),
    s1("Flight Checks"): {s1(name) for name in FLIGHT_CHECKS},
    s1("Skill Point Checks"): _of_type(CheckType.SKILL_POINT),
}