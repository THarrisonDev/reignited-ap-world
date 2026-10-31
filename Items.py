# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-23

"""Items shared by every game: filler and traps.

They take effect in whichever game is being played, so they carry no game
prefix. IDs sit in the shared block below the games (0xxxxx; game N owns
N00000-N99999).
"""
from typing import List, NamedTuple

from BaseClasses import ItemClassification

SHARED_BASE_ID = 0


class SharedItemData(NamedTuple):
    name: str
    code: int
    trap: bool = False


_shared_items = [SharedItemData(*row) for row in [
    ("Extra Life", 1007),
    ("Turn Spyro Red", 1009),
    ("Turn Spyro Blue", 1010),
    ("Turn Spyro Pink", 1011),
    ("Turn Spyro Yellow", 1012),
    ("Turn Spyro Green", 1013),
    ("Turn Spyro Black", 1014),
    ("Big Head Mode", 1015),
    ("Flat Spyro Mode", 1016),
    ("Damage Trap", 1017, True),
]]

shared_item_table = {data.name: data for data in _shared_items}
shared_item_name_to_id = {data.name: SHARED_BASE_ID + data.code for data in _shared_items}


def shared_classification(name: str):
    return ItemClassification.trap if shared_item_table[name].trap else ItemClassification.filler


def filler_choices(options) -> List[str]:
    """Weighted filler/trap names allowed by the slot's shared item-pool options.
    Falls back to Extra Life when every filler and trap is off, so the caller
    always has something to place."""
    choices: List[str] = []
    for data in _shared_items:
        name = data.name
        if name == "Extra Life":
            enabled, weight = options.enable_filler_extra_lives.value, 8
        elif name.startswith("Turn Spyro "):
            enabled, weight = options.enable_filler_color_change.value, 1
        elif name in ("Big Head Mode", "Flat Spyro Mode"):
            enabled, weight = options.enable_filler_color_change.value, 3
        elif name == "Damage Trap":
            enabled, weight = options.enable_trap_damage.value, 1
        else:
            continue
        if enabled:
            choices += [name] * weight
    return choices or ["Extra Life"] * 4
