"""Spyro 3 items. Names carry the "Spyro 3: " prefix; IDs are 300000 + code.

Under spyro3_level_locks, the 33 sub-levels whose portals the mod locks each
get a "<Level> Key" item (the 4 homeworlds are excluded and never locked; the
spawn is Sunrise Spring — a homeworld — so no key is precollected). Under
spyro3_egg_shuffle, each of the 146 shuffling egg checks releases a generic
"Spyro 3: Dragon Egg" item (one name, N copies — the save names
the eggs, the item stays generic). The 3 Sparx powers granted by the Sparx
realms (Crawdad Farm, Starfish Reef, Bugbot Factory) shuffle as useful items.
The boss events (Buzz/Spike/Scorch/
Sorceress Defeated) are locked items on their boss locations, never in the
pool. Abilities are granted by story in Spyro 3 (they carry over from Spyro 2,
so there are no Money-Bags purchases to shuffle). Shared filler and traps stay
in ../Items.py.
"""
from typing import Dict, NamedTuple

from BaseClasses import ItemClassification

from .Locations import TABLE_ORDER
from .Names import s3

BASE_ID = 300000  # Spyro 3 block: 3xxxxx (game 3), code < 100000


class Spyro3ItemData(NamedTuple):
    name: str
    code: int


# Lockable levels (Level Locks): the mod only locks portals standing in the 4
# homeworlds, so keys exist for exactly the 33 sub-levels — every sub-level's
# portal stands in a homeworld (researcher-verified, including Bugbot
# Factory's in Midnight Mountain). The homeworlds themselves stay open (the
# game's own boss-chain + egg-gate progression gates them, the same reason
# Spyro 1 never locks its homeworlds). The spawn is Sunrise Spring — a
# homeworld — so unlike Spyro 2 there is no precollected spawn key.
# Codes 6300..6332.
level_key_levels = [level for level in TABLE_ORDER
                    if level not in ("Sunrise Spring", "Midday Gardens", "Evening Lake",
                                     "Midnight Mountain")]


def level_key_name(level: str) -> str:
    return s3(f"{level} Key")


DRAGON_EGG = s3("Dragon Egg")

# The Sparx powers granted for completing the Sparx realms: Crawdad Farm
# (Sunrise Spring) widens the gem collect range, Starfish Reef (Evening Lake)
# adds an extra hit point and Bugbot Factory (Midnight Mountain, post-Sorceress)
# lets Sparx break chests. Real items in the save (EInventoryType 45/47/48 as
# globalFloatMap keys) but useful only: they gate nothing, and the 4th power's
# radar (EIT_SparxPower_GemFinder, 46) ships default-on in Reignited, so it is
# not randomized.
GEM_COLLECT_RANGE = s3("Sparx Gem Collect Range")
EXTRA_HIT_POINT = s3("Sparx Extra Hit Point")
CHEST_BREAKING = s3("Sparx Chest Breaking")
SPARX_POWERS = (GEM_COLLECT_RANGE, EXTRA_HIT_POINT, CHEST_BREAKING)

# Locked boss-defeat events (never shuffled): each boss dungeon's save carries
# a collected egg record (its EGG_CATALOG name), which checkd sends as the
# matching boss location — there is no EIT_S3Boss record in saves.
BUZZ = s3("Buzz Defeated")
SPIKE = s3("Spike Defeated")
SCORCH = s3("Scorch Defeated")
SORCERESS = s3("Sorceress Defeated")

_items = [Spyro3ItemData(name, code) for name, code in [
    *[(level_key_name(level), 6300 + i) for i, level in enumerate(level_key_levels)],
    (DRAGON_EGG, 6400),
    (GEM_COLLECT_RANGE, 6500),
    (EXTRA_HIT_POINT, 6501),
    (CHEST_BREAKING, 6502),
    (BUZZ, 5300),
    (SPIKE, 5301),
    (SCORCH, 5302),
    (SORCERESS, 5303),
]]

item_table: Dict[str, Spyro3ItemData] = {data.name: data for data in _items}
item_name_to_id: Dict[str, int] = {data.name: BASE_ID + data.code for data in _items}


def classification(name: str):
    if name in SPARX_POWERS:
        return ItemClassification.useful
    return ItemClassification.progression


item_name_groups = {
    s3("Level Keys"): {level_key_name(level) for level in level_key_levels},
    s3("Eggs"): {DRAGON_EGG},
    s3("Bosses"): {BUZZ, SPIKE, SCORCH, SORCERESS},
    s3("Sparx Powers"): set(SPARX_POWERS),
}