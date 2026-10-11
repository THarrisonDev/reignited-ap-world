# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

"""Spyro 3 options. The slot's options dataclass (../Options.py) exposes them as spyro3_*."""
from Options import Choice, DefaultOnToggle, OptionGroup, Toggle


class GoalOptions:
    NONE = 0
    SORCERESS = 1


class GemChecksOption(DefaultOnToggle):
    """Adds Spyro 3 gem checks at 25/50/75/100% of the 29 gem-bearing levels'
    totals (speedways and the boss/challenge dungeons hold no save-recorded
    gems)."""
    display_name = "Enable Gem Checks"


class SkillPointChecksOption(DefaultOnToggle):
    """Adds the 20 Spyro 3 skill points as checks. They release items but gate
    nothing (skill points serve no purpose outside of being collected)."""
    display_name = "Enable Skill Point Checks"


class SparxPowerChecksOption(DefaultOnToggle):
    """Adds the 3 Sparx power checks: completing the Sparx realms Crawdad Farm,
    Starfish Reef and Bugbot Factory (the last opens after the Sorceress falls)
    grants Sparx a power, and those completions are checks. The powers arrive as
    useful items that gate nothing; the 4th power's radar (GemFinder) ships
    default-on in Reignited and is not randomized."""
    display_name = "Enable Sparx Power Checks"


class LevelLocksOption(Toggle):
    """The portals out of the 4 homeworlds are locked until the target level's
    "Spyro 3: <Level> Key" item is found. The homeworlds themselves stay open
    (the game's own boss-chain + egg-gate progression gates them — the
    balloonist analogy) and no key is precollected: the spawn level, Sunrise
    Spring, is a homeworld, so all 33 sub-level keys are shuffled into the item
    pool."""
    display_name = "Level Locks"
    default = False


class EggShuffleOption(Toggle):
    """If on, each of the 150 named dragon eggs releases a shuffled 'Spyro 3:
    Dragon Egg' item into the pool. If off, eggs are vanilla collectibles that
    release nothing (the egg locations stay checks either way)."""
    display_name = "Shuffle Dragon Eggs"
    default = True


class GoalOption(Choice):
    """Spyro 3 completion goal.
    None - Spyro 3 cannot be required; its checks are optional side content.
    Sorceress - Defeat the Sorceress in Sorceress Lair: Buzz, Spike and Scorch
    fall first, and each boss's fall opens the next homeworld (the game's own
    chain)."""
    display_name = "Spyro 3 Goal"
    default = GoalOptions.NONE
    option_none = GoalOptions.NONE
    option_sorceress = GoalOptions.SORCERESS


option_groups = [
    OptionGroup("Spyro 3: Checks", [
        GemChecksOption,
        SkillPointChecksOption,
        SparxPowerChecksOption,
    ], True),
    OptionGroup("Spyro 3: Progression", [
        GoalOption,
        LevelLocksOption,
    ], False),
    OptionGroup("Spyro 3: Eggs", [
        EggShuffleOption,
    ], False),
]