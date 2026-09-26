"""Spyro 2 locations: 64 orbs, 14 talismans, the 3 Money Bags ability
purchases, the 3 boss-defeat events, 25/50/75/100% gem checks and 16
option-gated skill-point checks — a view over data/spyro2.json, the single
source (IDs come from world/data: baseId + tableOffset * regionIndex + row).

Region order is LS number - 201 and rows within a region go orbs, talisman,
ability purchase, boss, gem checks, skill points; both are append-only, since
the order fixes the IDs.

Orb and talisman names use the on-screen text; each row also keeps the save key
(the game's GreenOrbTable/TalismanNameTable key, which the save stores and the
client matches). Ability purchases have no per-ability save actor: the global
inventory's EIT_Swimming/EIT_Climbing/EIT_HeadBash records carry ownership.
Each boss level's save holds one EIT_S2Boss record, which fires the boss check.
Gem checks exist only for the 21 gem-bearing levels (400 gems each, verified
from a 100% save): the speedways' gems are post-run rewards the save does not
record per level, and the boss dungeons and Dragon Shores hold none. Skill
points never carry rules (they gate nothing in the game); the save's global
EIT_SkillPoint record holds one nameless float per earned point, each float the
ESkillPoint enum value (S2 = 15..30).
"""
from typing import List, NamedTuple

from ..data import load
from .Names import s2

ORB = "orb"
TALISMAN = "talisman"
GEM = "gem"
ABILITY = "ability"
BOSS = "boss"
SKILLPOINT = "skillpoint"


class Spyro2LocationData(NamedTuple):
    name: str
    kind: str            # ORB | TALISMAN | ABILITY | BOSS | GEM | SKILLPOINT
    save_key: str = ""   # orbs/talismans: the key the save stores
    threshold: int = 0   # gem checks: percent of the level's gems
    price: int = 0       # abilities: the Money Bags price in gems


_data = load("spyro2")

TABLE_ORDER: List[str] = list(_data.regions)

location_tables = {
    level: [Spyro2LocationData(row["name"], row["kind"], row.get("saveKey", ""),
                               row.get("threshold", 0), row.get("price", 0))
            for row in rows]
    for level, rows in _data.regions.items()
}
_unknown = {d.kind for table in location_tables.values() for d in table} - {
    ORB, TALISMAN, GEM, ABILITY, BOSS, SKILLPOINT}
if _unknown:
    raise ValueError(f"Spyro 2: unknown location kinds {sorted(_unknown)}")
del _unknown


def ability_item_name(location_name: str) -> str:
    """The shuffled item an ability purchase holds: the last name segment
    ("...: Swim Ability" -> "Spyro 2: Swim Ability", spyro2/Items.py)."""
    return s2(location_name.split(": ")[-1])


def get_name_to_id() -> dict:
    return {row["name"]: row["id"] for rows in _data.regions.values() for row in rows}


check_levels: List[str] = [level for level in TABLE_ORDER if location_tables[level]]

location_name_groups = {
    s2("Orbs"): {d.name for table in location_tables.values() for d in table if d.kind == ORB},
    s2("Talismans"): {d.name for table in location_tables.values() for d in table if d.kind == TALISMAN},
    s2("Abilities"): {d.name for table in location_tables.values() for d in table if d.kind == ABILITY},
    s2("Bosses"): {d.name for table in location_tables.values() for d in table if d.kind == BOSS},
    s2("Gem Checks"): {d.name for table in location_tables.values() for d in table if d.kind == GEM},
    s2("Skill Point Checks"): {d.name for table in location_tables.values() for d in table if d.kind == SKILLPOINT},
}
