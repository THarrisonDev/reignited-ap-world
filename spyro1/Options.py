# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

"""Spyro 1 options. The slot's options dataclass (../Options.py) exposes them as spyro1_*."""
from Options import Choice, DefaultOnToggle, OptionGroup, Range, Toggle


class GoalOptions:
    GNASTY = 0
    GNASTYS_LOOT = 1
    ALL_DRAGONS = 2


class DragonShuffleOptions:
    VANILLA = 0
    DRAGONSANITY = 1


class GoalOption(Choice):
    """Choose the Spyro 1 completion goal.
    Gnasty Gnorc - Defeat Gnasty Gnorc.
    Gnasty's Loot - Enter Gnasty's Loot and collect its 2000 gems (requires near-100%).
    All Dragons - Rescue all 80 dragons and defeat Gnasty Gnorc."""
    display_name = "Completion Goal"
    default = GoalOptions.GNASTY
    option_gnasty = GoalOptions.GNASTY
    option_gnastys_loot = GoalOptions.GNASTYS_LOOT
    option_all_dragons = GoalOptions.ALL_DRAGONS


class BalloonistGateOptions:
    VANILLA = 0
    SHUFFLED = 1


class BalloonistGateOption(Choice):
    """Rules for unlocking each homeworld via the balloonists.
    Vanilla: Marco needs 10 dragons, Gosnold 1200 gems, Tuco 5 eggs,
    Cray 50 dragons, Amos 6000 gems.
    Shuffled: each balloonist asks for a random number between its vanilla
    value and the most of that collectible obtainable before you reach it, so
    the seed is always beatable."""
    display_name = "Balloonist Gates"
    default = BalloonistGateOptions.VANILLA
    option_vanilla = BalloonistGateOptions.VANILLA
    option_shuffled = BalloonistGateOptions.SHUFFLED


class DragonShuffleOption(Choice):
    """Vanilla: Dragons are not items; all 80 dragons are vanilla checks that don't gate anything.
    Dragonsanity: Each rescued dragon releases a shuffled 'Spyro 1: Dragon' item into the pool,
    and homeworld gates require Dragon items."""
    display_name = "Dragon Shuffle"
    default = DragonShuffleOptions.DRAGONSANITY
    option_vanilla = DragonShuffleOptions.VANILLA
    option_dragonsanity = DragonShuffleOptions.DRAGONSANITY


class EggShuffleOption(Toggle):
    """If on, each of the 12 dragon eggs releases a shuffled 'Spyro 1: Dragon
    Egg' item into the pool.
    If off, eggs are vanilla collectibles and don't gate progression (except Beast Makers gate)."""
    display_name = "Shuffle Dragon Eggs"
    default = True


class LevelLocksOption(Toggle):
    """Every Spyro 1 level portal is locked until its "Spyro 1: <Level> Key" item is found."""
    display_name = "Level Locks"
    default = False


class StartingUnlockedLevelsOption(Range):
    """When Level Locks is on, this many random levels from Artisans start unlocked.
    They are chosen from Stone Hill, Dark Hollow, Town Square and Sunny Flight
    (Toasty is excluded because it is a boss)."""
    display_name = "Starting Unlocked Levels"
    range_start = 1
    range_end = 4
    default = 1


class GemsanityLiteOption(Toggle):
    """Adds percentage-based gem checks (25/50/75/100%) per level to the pool; a
    boss level carries only the All Gems milestone. Recommended: provides enough
    locations to house the shuffled items."""
    display_name = "Enable Gem Checks"
    default = True


class SkillPointChecksOption(DefaultOnToggle):
    """Adds the 14 Spyro 1 skill points as checks. They release items but gate
    nothing (skill points serve no purpose outside of being collected)."""
    display_name = "Enable Skill Point Checks"


class FlightChecksOption(DefaultOnToggle):
    """Adds a randomized check for each of the 5 flight levels, cleared when all
    4 of the flight's target sets are done. It needs only access to the flight."""
    display_name = "Enable Flight Set Checks"


option_groups = [
    OptionGroup("Spyro 1: Goal & Progression", [
        GoalOption,
        BalloonistGateOption,
        DragonShuffleOption,
        EggShuffleOption,
        LevelLocksOption,
        StartingUnlockedLevelsOption,
    ], False),
    OptionGroup("Spyro 1: Checks", [
        GemsanityLiteOption,
        SkillPointChecksOption,
        FlightChecksOption,
    ], True),
]
