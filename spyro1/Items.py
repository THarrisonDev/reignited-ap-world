# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

"""Spyro 1 items. Names carry the "Spyro 1: " prefix; IDs are 100000 + code.
Filler and traps are shared by every game and live in ../Items.py."""
from enum import IntEnum
from typing import Dict, NamedTuple

from BaseClasses import ItemClassification

from .Names import s1

BASE_ID = 100000  # Spyro 1 block: 1xxxxx (game 1), code < 100000


class Spyro1ItemCategory(IntEnum):
    DRAGON = 0
    EGG = 1
    EVENT = 4
    LEVEL_KEY = 8


class Spyro1ItemData(NamedTuple):
    name: str
    code: int
    category: Spyro1ItemCategory


DRAGON = s1("Dragon")
DRAGON_EGG = s1("Dragon Egg")

homeworlds = ["Peace Keepers", "Magic Crafters", "Beast Makers", "Dream Weavers", "Gnorc Gnexus"]

level_key_levels = [
    "Stone Hill", "Dark Hollow", "Town Square", "Sunny Flight", "Toasty",
    "Dry Canyon", "Cliff Town", "Ice Cavern", "Night Flight", "Doctor Shemp",
    "Alpine Ridge", "High Caves", "Wizard Peak", "Crystal Flight", "Blowhard",
    "Terrace Village", "Misty Bog", "Tree Tops", "Wild Flight", "Metalhead",
    "Dark Passage", "Lofty Castle", "Haunted Towers", "Icy Flight", "Jacques",
    "Gnorc Cove", "Twilight Harbor", "Gnasty Gnorc", "Gnasty's Loot",
]

starting_unlock_candidates = ["Stone Hill", "Dark Hollow", "Town Square", "Sunny Flight"]


def level_key_name(level: str) -> str:
    return s1(f"{level} Key")


_items = [Spyro1ItemData(s1(name), code, category) for name, code, category in [
    # Level/boss completion events (locked, not shuffled)
    ("Stone Hill Complete", 2000, Spyro1ItemCategory.EVENT),
    ("Dark Hollow Complete", 2001, Spyro1ItemCategory.EVENT),
    ("Town Square Complete", 2002, Spyro1ItemCategory.EVENT),
    ("Toasty Defeated", 2003, Spyro1ItemCategory.EVENT),
    ("Dry Canyon Complete", 2004, Spyro1ItemCategory.EVENT),
    ("Cliff Town Complete", 2005, Spyro1ItemCategory.EVENT),
    ("Ice Cavern Complete", 2006, Spyro1ItemCategory.EVENT),
    ("Doctor Shemp Defeated", 2007, Spyro1ItemCategory.EVENT),
    ("Alpine Ridge Complete", 2008, Spyro1ItemCategory.EVENT),
    ("High Caves Complete", 2009, Spyro1ItemCategory.EVENT),
    ("Wizard Peak Complete", 2010, Spyro1ItemCategory.EVENT),
    ("Blowhard Defeated", 2011, Spyro1ItemCategory.EVENT),
    ("Terrace Village Complete", 2012, Spyro1ItemCategory.EVENT),
    ("Misty Bog Complete", 2013, Spyro1ItemCategory.EVENT),
    ("Tree Tops Complete", 2014, Spyro1ItemCategory.EVENT),
    ("Metalhead Defeated", 2015, Spyro1ItemCategory.EVENT),
    ("Dark Passage Complete", 2016, Spyro1ItemCategory.EVENT),
    ("Lofty Castle Complete", 2017, Spyro1ItemCategory.EVENT),
    ("Haunted Towers Complete", 2018, Spyro1ItemCategory.EVENT),
    ("Jacques Defeated", 2019, Spyro1ItemCategory.EVENT),
    ("Gnorc Cove Complete", 2020, Spyro1ItemCategory.EVENT),
    ("Twilight Harbor Complete", 2021, Spyro1ItemCategory.EVENT),
    ("Gnasty Gnorc Defeated", 2022, Spyro1ItemCategory.EVENT),
    ("Gnasty's Loot Complete", 2023, Spyro1ItemCategory.EVENT),
    # Retired: flight Complete locations now hold shuffled items, so these are
    # never created. Kept so the ids stay reserved in the datapackage.
    ("Sunny Flight Complete", 2024, Spyro1ItemCategory.EVENT),
    ("Night Flight Complete", 2025, Spyro1ItemCategory.EVENT),
    ("Crystal Flight Complete", 2026, Spyro1ItemCategory.EVENT),
    ("Wild Flight Complete", 2027, Spyro1ItemCategory.EVENT),
    ("Icy Flight Complete", 2028, Spyro1ItemCategory.EVENT),

    # Progression items
    ("Dragon", 1000, Spyro1ItemCategory.DRAGON),
    ("Dragon Egg", 1001, Spyro1ItemCategory.EGG),

    # Per-level portal keys (Level Locks); codes 4000..4028 in level_key_levels order
    *[(f"{level} Key", 4000 + i, Spyro1ItemCategory.LEVEL_KEY) for i, level in enumerate(level_key_levels)],
]]

item_table: Dict[str, Spyro1ItemData] = {data.name: data for data in _items}
item_name_to_id: Dict[str, int] = {data.name: BASE_ID + data.code for data in _items}

_PROGRESSION = {Spyro1ItemCategory.DRAGON, Spyro1ItemCategory.EGG,
                Spyro1ItemCategory.LEVEL_KEY, Spyro1ItemCategory.EVENT}


def classification(name: str):
    return (ItemClassification.progression if item_table[name].category in _PROGRESSION
            else ItemClassification.filler)


item_name_groups = {
    s1("Dragons"): {DRAGON},
    s1("Eggs"): {DRAGON_EGG},
    s1("Level Keys"): {level_key_name(level) for level in level_key_levels},
}
