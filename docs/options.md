# Slot Options

The options as grouped on the Archipelago settings page. Per-game options carry their game prefix in the YAML key.

## Games

| Option | Choices | Default | Description |
|---|---|---|---|
| Included Games |  | frozenset({'Spyro 1'}) | Games whose locations and items are in this slot. |
| Required Games |  | frozenset() | Games you must complete, each by its own goal option, to finish the slot. Every required game must also be included. Empty means every included game that can be required. Spyro 2 is requirable with spyro2_goal = Ripto; Spyro 3 with spyro3_goal = Sorceress. |

## Spyro 1: Goal & Progression

| Option | Choices | Default | Description |
|---|---|---|---|
| Completion Goal | gnasty, gnastys_loot, all_dragons | 0 | Choose the Spyro 1 completion goal. Gnasty Gnorc - Defeat Gnasty Gnorc. Gnasty's Loot - Enter Gnasty's Loot and collect its 2000 gems (requires near-100%). All Dragons - Rescue all 80 dragons and defeat Gnasty Gnorc. |
| Balloonist Gates | vanilla, shuffled | 0 | Rules for unlocking each homeworld via the balloonists. Vanilla: Marco needs 10 dragons, Gosnold 1200 gems, Tuco 5 eggs, Cray 50 dragons, Amos 6000 gems. Shuffled: Raises the gem/egg/dragon thresholds by up to 12%; the in-game balloonists ask for the shuffled numbers. |
| Dragon Shuffle | vanilla, dragonsanity | 1 | Vanilla: Dragons are not items; all 80 dragons are vanilla checks that don't gate anything. Dragonsanity: Each rescued dragon releases a shuffled 'Spyro 1: Dragon' item into the pool, and homeworld gates require Dragon items. |
| Shuffle Dragon Eggs | false, true | True | If on, each of the 12 dragon eggs releases a shuffled 'Spyro 1: Dragon Egg' item into the pool. If off, eggs are vanilla collectibles and don't gate progression (except Beast Makers gate). |
| Level Locks | false, true | False | Every Spyro 1 level portal is locked until its "Spyro 1: <Level> Key" item is found. |
| Starting Unlocked Levels |  | 1 | When Level Locks is on, this many random levels from Artisans start unlocked. They are chosen from Stone Hill, Dark Hollow, Town Square and Sunny Flight (Toasty is excluded because it is a boss). |

## Spyro 1: Checks

| Option | Choices | Default | Description |
|---|---|---|---|
| Enable Gem Checks | false, true | True | Adds percentage-based gem checks (25/50/75/100%) per level to the pool. Recommended: provides enough locations to house the shuffled items. |
| Enable Skill Point Checks | false, true | 1 | Adds the 14 Spyro 1 skill points as checks. They release items but gate nothing (skill points serve no purpose outside of being collected). |
| Enable Flight Set Checks | false, true | 1 | Adds a randomized check for each of the 5 flight levels, cleared when all 4 of the flight's target sets are done. It needs only access to the flight. |

## Spyro 2: Checks

| Option | Choices | Default | Description |
|---|---|---|---|
| Enable Gem Checks | false, true | 1 | Adds Spyro 2 gem checks at 25/50/75/100% of the 21 gem-bearing levels' 400 gems (speedways/bosses/Dragon Shores have no save-recorded gems). |
| Enable Skill Point Checks | false, true | 1 | Adds the 16 Spyro 2 skill points as checks. They release items but gate nothing (skill points serve no purpose outside of being collected). |

## Spyro 2: Progression

| Option | Choices | Default | Description |
|---|---|---|---|
| Moneybags Abilities | vanilla, sanity | 0 | The three Money Bags purchases (Swim 500 in Summer Forest, Climb 500 in Autumn Plains, Headbash 1000 in Winter Tundra) are checks either way. Vanilla: the abilities are the game's own progression; paying Money Bags just sends the check. Sanity: Swim, Climb and Headbash are shuffled "Spyro 2: ... Ability" items; paying Money Bags sends the check, but the ability only works once you have received the matching item. |
| Spyro 2 Goal | none, ripto | 0 | Spyro 2 completion goal. None - Spyro 2 cannot be required; its checks are optional side content. Ripto - Defeat Ripto: crush and Gulp fall first, the castle door needs 40 orbs, and (with Moneybags Abilities shuffled) Headbash opens the gate. |
| Level Locks | false, true | False | The portals out of the 3 homeworlds are locked until the target level's "Spyro 2: <Level> Key" item is found. The homeworlds themselves stay open (the game's own Crush/Gulp talisman doors gate them) and Dragon Shores (post-game, no checks) is never locked. Glimmer, the spawn level, gets its key immediately; the other 24 keys are shuffled into the item pool. |

## Spyro 3: Checks

| Option | Choices | Default | Description |
|---|---|---|---|
| Enable Gem Checks | false, true | 1 | Adds Spyro 3 gem checks at 25/50/75/100% of the 29 gem-bearing levels' totals (speedways and the boss/challenge dungeons hold no save-recorded gems). |
| Enable Skill Point Checks | false, true | 1 | Adds the 20 Spyro 3 skill points as checks. They release items but gate nothing (skill points serve no purpose outside of being collected). |
| Enable Sparx Power Checks | false, true | 1 | Adds the 3 Sparx power checks: completing the Sparx realms Crawdad Farm, Starfish Reef and Bugbot Factory (the last opens after the Sorceress falls) grants Sparx a power, and those completions are checks. The powers arrive as useful items that gate nothing; the 4th power's radar (GemFinder) ships default-on in Reignited and is not randomized. |

## Spyro 3: Progression

| Option | Choices | Default | Description |
|---|---|---|---|
| Spyro 3 Goal | none, sorceress | 0 | Spyro 3 completion goal. None - Spyro 3 cannot be required; its checks are optional side content. Sorceress - Defeat the Sorceress in Sorceress Lair: Buzz, Spike and Scorch fall first, and each boss's fall opens the next homeworld (the game's own chain). |
| Level Locks | false, true | False | The portals out of the 4 homeworlds are locked until the target level's "Spyro 3: <Level> Key" item is found. The homeworlds themselves stay open (the game's own boss-chain + egg-gate progression gates them — the balloonist analogy) and no key is precollected: the spawn level, Sunrise Spring, is a homeworld, so all 33 sub-level keys are shuffled into the item pool. |

## Spyro 3: Eggs

| Option | Choices | Default | Description |
|---|---|---|---|
| Shuffle Dragon Eggs | false, true | True | If on, each of the 150 named dragon eggs releases a shuffled 'Spyro 3: Dragon Egg' item into the pool. If off, eggs are vanilla collectibles that release nothing (the egg locations stay checks either way). |

## Item Pool

| Option | Choices | Default | Description |
|---|---|---|---|
| Enable Extra Lives Filler | false, true | 1 | Adds extra lives to the item pool. |
| Enable Color Change Filler | false, true | 0 | Adds changing Spyro's color and Big Head/Flat Spyro modes to the item pool. |
| Enable Damage Traps | false, true | 0 | Adds damage traps to the item pool: one hit worth of damage when received (Spyro's health tier drops, like getting caught by an enemy). |

## Multiplayer

| Option | Choices | Default | Description |
|---|---|---|---|
| DeathLink | false, true | 0 | When you die, everyone dies. When anyone dies, you die. (Implemented in the Reignited client mod; the apworld only carries the option and slot data.) |
