"""Unified location/item engine: every game's data lives in data/<game>.json
and every game plugs into the same loader. The JSON is the single source of
truth; Python keeps only per-game LOGIC (rules, goals, region graphs).

This module stays stdlib-only and imports nothing from the world: the client's
generator (client/checkd/scripts/gen_locations.py) loads it standalone, with
no Archipelago install, so every location ID is derived here and only here.

Schema, spyro1:
  baseId                   int   location ID block (100000)
  levels[]                       {name, type, id, gemTotal, checks[], hub?}
    type                         HUB|NORMAL|FLIGHT|BOSS|BONUS
    checks[]                     {id, name, type}  name is PLAIN (no prefix);
                                 type DRAGON|EGG|SKILL_POINT
  gemThresholds            list  [[pct, label], ...] per-level gem-check template
  gemThresholdIdBase       int   derived gem-check IDs:
  gemThresholdIdsPerLevel  int     base + levelId * perLevel + tier
  eventIdBase              int   derived event IDs: base + levelId
  balloonistGates          map   homeworld -> {type, needed} (type
                                 dragons/eggs/gems)

Schema, spyro2/spyro3:
  baseId, tableOffset      int   IDs: baseId + tableOffset * regionIndex + row
  regions                  map   region name -> {gemTotal, locations[]}
    locations[]                  {name, kind, ...}  name is FULL (prefix
                                 included); kind orb|talisman|gem|ability|boss|
                                 skillpoint (spyro2) or gem|egg|boss|skillpoint|
                                 sparxpower (spyro3); saveKey/threshold/price
                                 where the kind has one
  homeworlds, payments, gates, checkGates, gemGates   gate data (../gates.py)

IDs are stable: regions and rows are append-only.
"""
import json
import os
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

# The data dir: beside this module on disk, or inside the .apworld zip when
# imported through AP's zipimport (open() on a zip member fails — read the
# bytes through the zip instead).
_DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def _read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _read_json_in_zip(rel: str) -> dict:
    """Read data/<rel> from inside the .apworld zip. data/__init__.py was
    imported through AP's zipimport: __file__ looks like
    "<...>/spyro_reignited.apworld/spyro_reignited/data/__init__.py" but the
    file system only has the .apworld file itself."""
    import zipfile
    marker = ".apworld" + os.sep
    if marker in __file__:
        zip_path = __file__.split(marker, 1)[0] + ".apworld"
        member = "spyro_reignited/data/" + rel
    else:
        # Loaded from disk but the JSON file is missing: maybe an installed
        # apworld unzipped without the data dir — last resort, sibling zip.
        pkg_root = os.path.dirname(_DATA_DIR)
        zip_path = pkg_root + ".apworld"
        member = os.path.basename(pkg_root) + "/data/" + rel
    with zipfile.ZipFile(zip_path) as z:
        return json.loads(z.read(member).decode("utf-8-sig"))


SPYRO1_LEVEL_TYPES = ("HUB", "NORMAL", "FLIGHT", "BOSS", "BONUS")
# Gem thresholds and events are derived per level, never listed as checks.
SPYRO1_CHECK_TYPES = ("DRAGON", "EGG", "SKILL_POINT")


class GameData:
    """One game's static data, loaded once and shared by all players."""

    def __init__(self, game_key: str):
        self.key = game_key  # "spyro1" | "spyro2" | "spyro3"
        rel = f"{game_key}.json"
        disk = os.path.join(_DATA_DIR, rel)
        raw = _read_json(disk) if os.path.isfile(disk) else _read_json_in_zip(rel)
        self.raw = raw
        self.base_id: int = raw["baseId"]
        self.prefix: str = f"Spyro {game_key[-1]}: "
        if self.key == "spyro1":
            self._build_spyro1()
        else:
            self._build_tabular()

    # -- spyro1: levels carry ids; gem thresholds and events are derived ---
    def _build_spyro1(self):
        raw = self.raw
        self.gem_thresholds = [(pct, label) for pct, label in raw["gemThresholds"]]
        self.gates: Dict[str, dict] = raw.get("balloonistGates", {})
        if len(self.gem_thresholds) > raw["gemThresholdIdsPerLevel"]:
            raise ValueError("spyro1: more gem thresholds than ids per level")
        for level in raw["levels"]:
            if level["type"] not in SPYRO1_LEVEL_TYPES:
                raise ValueError(f"spyro1: level {level['name']!r} has unknown "
                                 f"type {level['type']!r}")
            for check in level["checks"]:
                if check["type"] not in SPYRO1_CHECK_TYPES:
                    raise ValueError(f"spyro1: check {check['name']!r} has "
                                     f"unknown type {check['type']!r}")

    def gem_threshold_checks(self, level: dict) -> List[Tuple[int, str, int]]:
        """A Spyro 1 level's derived gem-threshold checks as (id, plain name,
        percent). Flights carry none; bosses carry only All Gems."""
        if level["type"] == "FLIGHT":
            return []
        raw = self.raw
        tiers = [len(self.gem_thresholds) - 1] if level["type"] == "BOSS" \
            else range(len(self.gem_thresholds))
        return [(raw["gemThresholdIdBase"]
                 + level["id"] * raw["gemThresholdIdsPerLevel"] + t,
                 f"{level['name']}: {self.gem_thresholds[t][1]}",
                 self.gem_thresholds[t][0])
                for t in tiers]

    def event_check(self, level: dict) -> Optional[Tuple[int, str]]:
        """A Spyro 1 level's derived completion event as (id, plain name):
        "<Level> Complete" or "<Boss> Defeated"; hubs have none."""
        if level["type"] == "HUB":
            return None
        suffix = "Defeated" if level["type"] == "BOSS" else "Complete"
        return (self.raw["eventIdBase"] + level["id"],
                f"{level['name']} {suffix}")

    # -- tabular games (spyro2/3): baseId + offset * regionIndex + entry ---
    def _build_tabular(self):
        raw = self.raw
        self.regions: Dict[str, list] = {}
        self.gem_totals: Dict[str, int] = {}
        # Every region consumes an index, even one without locations, so a
        # region's IDs never move when another region gains or loses rows.
        for i, (region, data) in enumerate(raw["regions"].items()):
            rows = []
            for n, loc in enumerate(data["locations"]):
                row = dict(loc)
                # Names are FULL: the on-screen text with the game prefix.
                # gates.py strips the prefix by length, so a bare name is a
                # data error, not something to patch up here.
                if not row["name"].startswith(self.prefix):
                    raise ValueError(f"{self.key}: location {row['name']!r} "
                                     f"lacks the {self.prefix!r} prefix")
                row["id"] = self.base_id + raw["tableOffset"] * i + n
                rows.append(row)
            self.regions[region] = rows
            self.gem_totals[region] = int(data.get("gemTotal", 0))


@lru_cache(maxsize=None)
def load(game_key: str) -> GameData:
    """The cached GameData for a game key. One parse per process."""
    return GameData(game_key)