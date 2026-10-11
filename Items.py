# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

"""Items shared by every game: filler and traps.

They take effect in whichever game is being played, so they carry no game
prefix. IDs sit in the shared block below the games (0xxxxx; game N owns
N00000-N99999). The shared FILLER name itself (core.py) is a location-table
sentinel only — it is not a registered item and never enters a pool.
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
    """Weighted filler/trap names allowed by the slot's shared item-pool options."""
    choices: List[str] = []
    for data in _shared_items:
        name = data.name
        if name == "Extra Life" and options.enable_filler_extra_lives.value:
            choices += [name] * 8
        elif name.startswith("Turn Spyro ") and options.enable_filler_color_change.value:
            choices.append(name)
        elif name in ("Big Head Mode", "Flat Spyro Mode") and options.enable_filler_color_change.value:
            choices += [name] * 3
        elif name == "Damage Trap" and options.enable_trap_damage.value:
            choices.append(name)
        elif name == "Extra Life":
            # Fallback filler when everything else is disabled
            choices += [name] * 4
    return choices
