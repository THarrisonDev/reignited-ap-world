"""Spyro 2 items. Names carry the "Spyro 2: " prefix; IDs are 200000 + code.

The Money Bags abilities (Swim/Climb/Headbash) are shuffled progression items
under spyro2_moneybags_abilities=sanity; the boss events (Crush/Gulp/Ripto
Defeated) are locked items on their boss locations, never in the pool. Under
spyro2_level_locks, the 25 levels whose portals the mod locks each get a
"<Level> Key" item (the 3 homeworlds and Dragon Shores are excluded; Glimmer's
— the spawn level — is precollected). Under the default spyro2_orb_shuffle,
each of the 64 orb checks releases a shuffled "Spyro 2: Orb" item and the
orb doors read received Orb items (the mod reconciles the game's orb counter
to them, the Spyro 1 dragon pattern). Superflame is the Dragon Shores 100%
reward, not a purchase, and stays out.
"""
from typing import Dict, NamedTuple

from BaseClasses import ItemClassification

from .Locations import TABLE_ORDER
from .Names import s2

BASE_ID = 200000  # Spyro 2 block: 2xxxxx (game 2), code < 100000


class Spyro2ItemData(NamedTuple):
    name: str
    code: int


SWIM = s2("Swim Ability")
CLIMB = s2("Climb Ability")
HEADBASH = s2("Headbash Ability")

# Core collectible, shuffled by default: 64 pooled copies (one per orb check),
# reconciled onto the game's orb counter by the mod (spyro2/orbs.lua).
ORB = s2("Orb")

# Locked boss-defeat events (never shuffled): each boss level's save carries a
# collected EIT_S2Boss record, which checkd sends as the matching location.
CRUSH = s2("Crush Defeated")
GULP = s2("Gulp Defeated")
RIPTO = s2("Ripto Defeated")

# Lockable levels (Level Locks): the mod only locks portals standing in the 3
# homeworlds that lead out of them, so keys exist for exactly those targets —
# the homeworlds themselves stay open (the game's own Crush/Gulp talisman doors
# gate them, the same reason Spyro 1 never locks its homeworlds) and Dragon
# Shores is a post-game bonus world with no checks. Glimmer — the spawn level —
# has its key precollected. Codes 4200..4224.
level_key_levels = [level for level in TABLE_ORDER
                    if level not in ("Dragon Shores", "Summer Forest", "Autumn Plains",
                                     "Winter Tundra")]


def level_key_name(level: str) -> str:
    return s2(f"{level} Key")


_items = [Spyro2ItemData(name, code) for name, code in [
    (SWIM, 5000),
    (CLIMB, 5001),
    (HEADBASH, 5002),
    (ORB, 5300),
    (CRUSH, 5100),
    (GULP, 5101),
    (RIPTO, 5102),
    *[(level_key_name(level), 4200 + i) for i, level in enumerate(level_key_levels)],
]]

item_table: Dict[str, Spyro2ItemData] = {data.name: data for data in _items}
item_name_to_id: Dict[str, int] = {data.name: BASE_ID + data.code for data in _items}


def classification(name: str):
    return ItemClassification.progression


item_name_groups = {
    s2("Orbs"): {ORB},
    s2("Abilities"): {SWIM, CLIMB, HEADBASH},
    s2("Bosses"): {CRUSH, GULP, RIPTO},
    s2("Level Keys"): {level_key_name(level) for level in level_key_levels},
}