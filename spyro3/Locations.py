"""Spyro 3 locations: 25/50/75/100% gem checks for the 29 gem-bearing levels,
the 146 save-named dragon eggs, the 4 boss-defeat events, 20 option-gated
skill-point checks and the 3 option-gated Sparx power checks — a view over
data/spyro3.json, the single source (IDs come from world/data: baseId +
tableOffset * regionIndex + row).

Region names use the on-screen LevelDisplayNameTable spellings (extracted from
the game paks); region order = LS number - 301, the save's /LS3xx_<name>/
order. Regions and the rows within them are append-only, since the order fixes
the IDs: gem checks, then eggs (or the boss event), then skill points, then the
Sparx power. Data verified against a 100% save.

Gem checks exist only where the save records gems per level: the speedways and
the boss/challenge dungeons hold none (their rewards are granted on post-run
summary screens). Dino Mines totals 702, the wiki-documented gem-shrub oddity.

Every S3 egg is NAMED in the save's itemParamList: the save key IS the dragon
name, and all 150 (region, name) pairs are unique. The boss-defeat events
REPLACE the boss dungeons' egg rows: there is no EIT_S3Boss record in saves —
the boss-kill save surface IS the boss dungeon's own named egg record (its
saveKey), which checkd's egg scan already drops. EGG_CATALOG below restores the
full 150 (it pins the save).

Skill points are checks only: they gate nothing in the game, and the save's
global EIT_SkillPoint record holds one nameless float per earned point, each
float the ESkillPoint enum value (S3 = 31..50).

The 3 Sparx power checks sit in the Sparx realms (Crawdad Farm, Starfish Reef,
Bugbot Factory): completing the realm grants Sparx a power, stored in the
save's globalFloatMap as EIT_SparxPower_<saveKey>. The 4th power's radar
(EIT_SparxPower_GemFinder) ships default-on in Reignited and is not a check.
"""
from typing import Dict, List, NamedTuple, Tuple

from ..data import load
from .Names import PREFIX, s3

# Kinds for the checks this game has. Eggs are ALWAYS checks (the save names
# every one of them — spyro3_egg_shuffle only decides whether they release
# items); FLIGHT locations land with their feature task.
EGG = "egg"
BOSS = "boss"
FLIGHT = "flight"
GEM = "gem"
SKILLPOINT = "skillpoint"
SPARX_POWER = "sparxpower"


class Spyro3LocationData(NamedTuple):
    name: str
    kind: str            # EGG | BOSS | FLIGHT | GEM | SKILLPOINT | SPARX_POWER
    save_key: str = ""   # eggs/bosses: the dragon name the save's itemParamList
                         # stores; Sparx powers: the EIT_SparxPower_ suffix
    threshold: int = 0   # gem checks: percent of the level's gems


_data = load("spyro3")

TABLE_ORDER: List[str] = list(_data.regions)

location_tables = {
    level: [Spyro3LocationData(row["name"], row["kind"], row.get("saveKey", ""),
                               row.get("threshold", 0))
            for row in rows]
    for level, rows in _data.regions.items()
}
_unknown = {d.kind for table in location_tables.values() for d in table} - {
    EGG, BOSS, FLIGHT, GEM, SKILLPOINT, SPARX_POWER}
if _unknown:
    raise ValueError(f"Spyro 3: unknown location kinds {sorted(_unknown)}")
del _unknown


def _plain(name: str) -> str:
    return name[len(PREFIX):]


# Boss-defeat events, keyed by level: (location name, event item name, save
# key). The event item names are bare (the s2 CRUSH precedent).
BOSSES: Dict[str, Tuple[str, str, str]] = {
    level: (_plain(d.name), d.name.split(": ")[-1], d.save_key)
    for level, table in location_tables.items() for d in table if d.kind == BOSS
}

# The dragon eggs per level in save order (the Guide Book's egg order): every
# egg row, plus each boss dungeon's egg, whose row the boss event took.
EGG_CATALOG: Dict[str, List[str]] = {
    level: [d.save_key for d in table if d.kind in (EGG, BOSS)]
    for level, table in location_tables.items()
}

# Sparx realm -> (location name suffix, EInventoryType name).
SPARX_REALM_POWERS: Dict[str, Tuple[str, str]] = {
    level: (d.name.split(": ")[-1], "EIT_SparxPower_" + d.save_key)
    for level, table in location_tables.items() for d in table if d.kind == SPARX_POWER
}


def get_name_to_id() -> dict:
    return {row["name"]: row["id"] for rows in _data.regions.values() for row in rows}


location_name_groups = {
    s3("Gem Checks"): {d.name for table in location_tables.values() for d in table if d.kind == GEM},
    s3("Eggs"): {d.name for table in location_tables.values() for d in table if d.kind == EGG},
    s3("Bosses"): {d.name for table in location_tables.values() for d in table if d.kind == BOSS},
    s3("Skill Point Checks"): {d.name for table in location_tables.values()
                               for d in table if d.kind == SKILLPOINT},
    s3("Sparx Powers"): {d.name for table in location_tables.values()
                         for d in table if d.kind == SPARX_POWER},
}