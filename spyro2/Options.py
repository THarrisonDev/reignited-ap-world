"""Spyro 2 options. The slot's options dataclass (../Options.py) exposes them as spyro2_*."""
from Options import Choice, DefaultOnToggle, OptionGroup, Toggle


class GemChecksOption(DefaultOnToggle):
    """Adds Spyro 2 gem checks at 25/50/75/100% of the 21 gem-bearing levels'
    400 gems (speedways/bosses/Dragon Shores have no save-recorded gems)."""
    display_name = "Enable Gem Checks"


class SkillPointChecksOption(DefaultOnToggle):
    """Adds the 16 Spyro 2 skill points as checks. They release items but gate
    nothing (skill points serve no purpose outside of being collected)."""
    display_name = "Enable Skill Point Checks"


class MoneybagsAbilitiesOptions:
    VANILLA = 0
    SANITY = 1


class S2GoalOptions:
    NONE = 0
    RIPTO = 1


class AbilitiesShuffleOption(Choice):
    """The three Money Bags purchases (Swim 500 in Summer Forest, Climb 500 in
    Autumn Plains, Headbash 1000 in Winter Tundra) are checks either way.
    Vanilla: the abilities are the game's own progression; paying Money Bags
    just sends the check.
    Sanity: Swim, Climb and Headbash are shuffled "Spyro 2: ... Ability" items;
    paying Money Bags sends the check, but the ability only works once you have
    received the matching item."""
    display_name = "Moneybags Abilities"
    default = MoneybagsAbilitiesOptions.VANILLA
    option_vanilla = MoneybagsAbilitiesOptions.VANILLA
    option_sanity = MoneybagsAbilitiesOptions.SANITY


class GoalOption(Choice):
    """Spyro 2 completion goal.
    None - Spyro 2 cannot be required; its checks are optional side content.
    Ripto - Defeat Ripto: crush and Gulp fall first, the castle door needs
    40 orbs, and (with Moneybags Abilities shuffled) Headbash opens the gate."""
    display_name = "Spyro 2 Goal"
    default = S2GoalOptions.NONE
    option_none = S2GoalOptions.NONE
    option_ripto = S2GoalOptions.RIPTO


class LevelLocksOption(Toggle):
    """The portals out of the 3 homeworlds are locked until the target level's
    "Spyro 2: <Level> Key" item is found. The homeworlds themselves stay open
    (the game's own Crush/Gulp talisman doors gate them) and Dragon Shores
    (post-game, no checks) is never locked. Glimmer, the spawn level, gets its
    key immediately; the other 24 keys are shuffled into the item pool."""
    display_name = "Level Locks"
    default = False


option_groups = [
    OptionGroup("Spyro 2: Checks", [
        GemChecksOption,
        SkillPointChecksOption,
    ], True),
    OptionGroup("Spyro 2: Progression", [
        AbilitiesShuffleOption,
        GoalOption,
        LevelLocksOption,
    ], False),
]
