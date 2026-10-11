# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

"""Slot options: which games are in the slot, which complete it, and the
item-pool/multiplayer settings shared by every game. Per-game options carry the
game's prefix (spyro1_*)."""
from dataclasses import dataclass

from Options import DeathLink, DefaultOnToggle, OptionGroup, OptionSet, PerGameCommonOptions, Toggle

from .spyro1 import Options as S1
from .spyro2 import Options as S2
from .spyro3 import Options as S3

# YAML game name -> internal game key (slot data, per-game modules)
GAME_KEYS = {"Spyro 1": "spyro1", "Spyro 2": "spyro2", "Spyro 3": "spyro3"}
# Games with a goal the client can report; only these can be required.
REQUIRABLE_GAMES = frozenset({"Spyro 1", "Spyro 2", "Spyro 3"})


class IncludedGames(OptionSet):
    """Games whose locations and items are in this slot."""
    display_name = "Included Games"
    valid_keys = frozenset(GAME_KEYS)
    default = frozenset({"Spyro 1"})


class RequiredGames(OptionSet):
    """Games you must complete, each by its own goal option, to finish the slot.
    Every required game must also be included. Empty means every included game that
    can be required. Spyro 2 is requirable with spyro2_goal = Ripto; Spyro 3 with
    spyro3_goal = Sorceress."""
    display_name = "Required Games"
    valid_keys = REQUIRABLE_GAMES
    default = frozenset()


class EnableFillerExtraLives(DefaultOnToggle):
    """Adds extra lives to the item pool."""
    display_name = "Enable Extra Lives Filler"


class EnableFillerColorChange(Toggle):
    """Adds changing Spyro's color and Big Head/Flat Spyro modes to the item pool."""
    display_name = "Enable Color Change Filler"


class EnableTrapDamage(Toggle):
    """Adds damage traps to the item pool: one hit worth of damage when received
    (Spyro's health tier drops, like getting caught by an enemy)."""
    display_name = "Enable Damage Traps"


class EnableDeathLink(DeathLink):
    """When you die, everyone dies. When anyone dies, you die.
    (Implemented in the Reignited client mod; the apworld only carries the option and slot data.)"""
    display_name = "DeathLink"


@dataclass
class SRTOptions(PerGameCommonOptions):
    included_games: IncludedGames
    required_games: RequiredGames
    spyro1_goal: S1.GoalOption
    spyro1_balloonist_gates: S1.BalloonistGateOption
    spyro1_dragon_shuffle: S1.DragonShuffleOption
    spyro1_egg_shuffle: S1.EggShuffleOption
    spyro1_level_locks: S1.LevelLocksOption
    spyro1_starting_unlocked_levels: S1.StartingUnlockedLevelsOption
    spyro1_enable_gem_checks: S1.GemsanityLiteOption
    spyro1_enable_skillpoint_checks: S1.SkillPointChecksOption
    spyro1_enable_flight_checks: S1.FlightChecksOption
    spyro2_enable_gem_checks: S2.GemChecksOption
    spyro2_enable_skillpoint_checks: S2.SkillPointChecksOption
    spyro2_orb_shuffle: S2.OrbShuffleOption
    spyro2_moneybags_abilities: S2.AbilitiesShuffleOption
    spyro2_goal: S2.GoalOption
    spyro2_level_locks: S2.LevelLocksOption
    spyro3_enable_gem_checks: S3.GemChecksOption
    spyro3_enable_skillpoint_checks: S3.SkillPointChecksOption
    spyro3_sparx_powers: S3.SparxPowerChecksOption
    spyro3_goal: S3.GoalOption
    spyro3_level_locks: S3.LevelLocksOption
    spyro3_egg_shuffle: S3.EggShuffleOption
    enable_filler_extra_lives: EnableFillerExtraLives
    enable_filler_color_change: EnableFillerColorChange
    enable_trap_damage: EnableTrapDamage
    death_link: EnableDeathLink


option_groups = [
    OptionGroup("Games", [
        IncludedGames,
        RequiredGames,
    ], False),
    *S1.option_groups,
    *S2.option_groups,
    *S3.option_groups,
    OptionGroup("Item Pool", [
        EnableFillerExtraLives,
        EnableFillerColorChange,
        EnableTrapDamage,
    ], True),
    OptionGroup("Multiplayer", [
        EnableDeathLink,
    ], True),
]
