# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

# Spyro Reignited Trilogy Archipelago World
#
# While it would be much more simple to treat the games as individual
# my wife provided the insight that certain things might be more fun
# if the games were unified. Sharing cosmetics, traps, and in the future
# maybe some collectibles would all just be a neat change from the
# classics. As such this root init is about unifying all the of the
# games that you're including. You're free to pick and choose, with the
# root Reignited AP safely combining the selected games. For specifics
# look at the spyro1, spyro2 and spyro3 directories.
from typing import ClassVar, Dict, List

from BaseClasses import Item, Region, Tutorial
from Options import Accessibility, OptionError

from worlds.AutoWorld import World, WebWorld

from .core import GAME, SRTItem
from .Items import (
    filler_choices,
    shared_classification,
    shared_item_name_to_id,
    shared_item_table,
)
from .Options import GAME_KEYS, SRTOptions, option_groups
from .spyro1 import Items as S1Items
from .spyro1 import Locations as S1Locations
from .spyro1.Game import Spyro1Game
from .spyro2 import Items as S2Items
from .spyro2 import Locations as S2Locations
from .spyro2.Game import Spyro2Game
from .spyro3 import Items as S3Items
from .spyro3 import Locations as S3Locations
from .spyro3.Game import Spyro3Game

GAME_CLASSES = {game.key: game for game in (Spyro1Game, Spyro2Game, Spyro3Game)}


def _merge_ids(*tables: Dict[str, int]) -> Dict[str, int]:
    """Union of name -> id tables; a repeated name or id is a data error."""
    merged: Dict[str, int] = {}
    seen_ids = set()
    for table in tables:
        for name, code in table.items():
            if name in merged or code in seen_ids:
                raise ValueError(f"{GAME}: duplicate name or id: {name!r} = {code}")
            merged[name] = code
            seen_ids.add(code)
    return merged


class SRTWeb(WebWorld):
    bug_report_page = "https://github.com/THarrisonDev/reignited-ap/issues"
    theme = "stone"
    option_groups = option_groups
    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the Archipelago Spyro randomizer on your computer.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Tim Harrison"],
    )
    game_info_languages = ["en"]
    tutorials = [setup_en]


class SpyroReignitedWorld(World):
    """
    Unified Archipelago world for the Spyro Reignited Trilogy (remakes of the first
    three Spyro games). This class delegates to one sub-game instance per game the
    slot includes (Spyro1Game/Spyro2Game/Spyro3Game), merging their items, locations,
    and regions into a single slot. The included_games and required_games options
    control which games appear and which of those must be finished to complete the slot.
    """

    game: ClassVar[str] = GAME
    options_dataclass = SRTOptions
    options: SRTOptions  # pyright: ignore[reportIncompatibleVariableOverride]
    topology_present: bool = False
    web = SRTWeb()
    data_version = 0
    # Minimum version the game client must report at ConnectSlot (the srt_bridge
    # mod reports {0, 6, 7}). Distinct from archipelago.json's minimum_ap_version
    # (0.6.1), which gates the AP server itself.
    required_client_version = (0, 5, 0)
    # Keep in sync with archipelago.json world_version.
    ap_world_version = "0.28.0"
    item_name_to_id = _merge_ids(
        shared_item_name_to_id,
        S1Items.item_name_to_id,
        S2Items.item_name_to_id,
        S3Items.item_name_to_id,
    )
    location_name_to_id = _merge_ids(
        S1Locations.get_name_to_id(),
        S2Locations.get_name_to_id(),
        S3Locations.get_name_to_id(),
    )
    item_name_groups = {
        **S1Items.item_name_groups,
        **S2Items.item_name_groups,
        **S3Items.item_name_groups,
    }
    location_name_groups = {
        **S1Locations.location_name_groups,
        **S2Locations.location_name_groups,
        **S3Locations.location_name_groups,
    }

    def __init__(self, multiworld, player: int):
        super().__init__(multiworld, player)
        self.games: List = []
        self.required_games: List = []

    # ------------------------------------------------------------------
    # Option handling
    # ------------------------------------------------------------------
    def generate_early(self):
        included = set(self.options.included_games.value)
        if not included:
            raise OptionError(
                f"{GAME}: included_games is empty; include at least one game."
            )
        required = set(self.options.required_games.value)
        missing = sorted(required - included)
        if missing:
            raise OptionError(
                f"{GAME}: required_games {missing} must also be in included_games."
            )

        self.games = [GAME_CLASSES[GAME_KEYS[name]](self) for name in sorted(included)]
        for game in self.games:
            game.generate_early()
        if required:
            self.required_games = [game for game in self.games if game.name in required]
            for game in self.required_games:
                if not getattr(game, "requirable", True):
                    raise OptionError(
                        f"{GAME}: {game.name} needs its goal option set to be required "
                        f"(e.g. spyro2_goal = Ripto, spyro3_goal = Sorceress)."
                    )
        else:
            self.required_games = [
                game for game in self.games if getattr(game, "requirable", True)
            ]
            if not self.required_games:
                raise OptionError(
                    f"{GAME}: no included game can be required; include Spyro 1 or "
                    f"set spyro2_goal = Ripto / spyro3_goal = Sorceress."
                )

        # Full accessibility always makes sense here: everything is reachable,
        # the only question is in what order.
        self.options.accessibility = Accessibility(0)  # Full

    # ------------------------------------------------------------------
    # Regions
    # ------------------------------------------------------------------
    def create_regions(self):
        menu = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu)
        for game in self.games:
            game.create_regions(menu)

    # ------------------------------------------------------------------
    # Items
    # ------------------------------------------------------------------
    def create_items(self):
        open_locations = sum(
            1
            for location in self.multiworld.get_locations(self.player)
            if location.item is None
        )
        names: List[str] = []
        for game in self.games:
            names += game.create_pool()

        remaining = open_locations - len(names)
        if remaining < 0:
            raise OptionError(
                f"{GAME}: too many progression items ({len(names)}) for the number of "
                f"available locations ({open_locations}). Enable more checks (e.g. Spyro 1 "
                f"gem checks), or turn off Level Locks (each locked level adds a Key item "
                f"to the pool)."
            )
        choices = filler_choices(self.options)
        names += [self.multiworld.random.choice(choices) for _ in range(remaining)]
        self.multiworld.random.shuffle(names)
        self.multiworld.itempool += [self.create_item(name) for name in names]

    def create_item(self, name: str) -> Item:
        if name in shared_item_table:
            classification = shared_classification(name)
        elif name in S2Items.item_table:
            classification = S2Items.classification(name)
        elif name in S3Items.item_table:
            classification = S3Items.classification(name)
        else:
            classification = S1Items.classification(name)
        return SRTItem(name, classification, self.item_name_to_id[name], self.player)

    def get_filler_item_name(self) -> str:
        return "Extra Life"

    # ------------------------------------------------------------------
    # Rules / logic
    # ------------------------------------------------------------------
    def set_rules(self) -> None:
        for game in self.games:
            game.set_rules()
        required = self.required_games
        self.multiworld.completion_condition[self.player] = lambda state: all(
            game.is_complete(state) for game in required
        )

    # ------------------------------------------------------------------
    # Slot data for the client
    # ------------------------------------------------------------------
    def fill_slot_data(self) -> dict:
        options = self.options
        locations = [
            location
            for location in self.multiworld.get_locations(self.player)
            if location.address is not None
        ]
        return {
            "included_games": [game.key for game in self.games],
            "required_games": [game.key for game in self.required_games],
            "options": {
                "death_link": options.death_link.value,
                "enable_filler_extra_lives": options.enable_filler_extra_lives.value,
                "enable_filler_color_change": options.enable_filler_color_change.value,
                "enable_trap_damage": options.enable_trap_damage.value,
            },
            "games": {game.key: game.slot_data() for game in self.games},
            "seed": self.multiworld.seed_name,
            "slot": self.multiworld.player_name[self.player],
            "locationNameToId": {
                location.name: location.address for location in locations
            },
            "apworldVersion": self.ap_world_version,
        }
