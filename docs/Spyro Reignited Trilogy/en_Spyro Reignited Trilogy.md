# Spyro Reignited Trilogy

A multiworld randomizer for Spyro Reignited Trilogy (PC).

## Games in this world

One slot can include several of the trilogy's games (**Included Games**) and requires
some of them for completion (**Required Games**, each finished by its own goal option).
**Spyro 1** (Spyro the Dragon) and **Spyro 2** (Ripto's Rage!) are fully randomized;
**Spyro 3** (Year of the Dragon) is available as optional content (it can be required
with its **Spyro 3 Goal** set to Sorceress).

Every location, item and region of a game carries that game's name, e.g.
**Spyro 1: Artisans: Free Nestor** or **Spyro 1: Stone Hill Key**. Filler and traps
(Extra Life, color changes, Damage Trap, …) work in whichever game you are playing and
have no prefix.

The full list of slot options (with choices and defaults) is in the
[options reference](../player-options) — the same options you'll see on the
Archipelago settings page when generating your game.

## What is randomized? (Spyro 1)

The game's collectibles are shuffled into the Archipelago item pool:

- **80 dragons** — freeing any dragon can give you someone else's Dragon item (or another
  player's item entirely)
- **12 dragon eggs** — thief chases become checks
- **Gem milestones** — 25/50/75/100% of the gems in each non-flight level; a boss
  level carries only the All Gems milestone (flight levels' gems are challenge
  rewards with no save-recorded gem counters)
- **Flight levels** — clearing all 4 target sets in each of the 5 flight levels is a
  check that holds a randomized item (option `spyro1_enable_flight_checks`, on by
  default)
- **Level completions and boss defeats** — tracked as progress (they open the boss
  portals and finish the goal) but hold no randomized item

## What is not randomized?

Level layout, gem *values*, enemy placement, and the world map are untouched. The
randomization is item/progression-based, in the same style as the Spyro 2 and Spyro 3
randomizers.

## Progression

You travel through the 6 homeworlds using the balloonists. Depending on your settings,
the balloonist requirements are vanilla or randomized (raised thresholds).

### Level Locks

With **Level Locks** on, every level portal in the homeworlds is locked until you find
its key item, named after the level: **Spyro 1: Stone Hill Key**, **Spyro 1: Doctor Shemp
Key**, **Spyro 1: Gnasty Gnorc Key**, and so on (the Gnasty's Loot key only exists when
Gnasty's Loot is the goal).
Level keys are shuffled into the item pool like any other progression item.

So you are never stuck at the start, **Starting Unlocked Levels** (1–4, default 1) picks
that many random Artisans levels (Stone Hill, Dark Hollow, Town Square, Sunny Flight) and
gives you their keys right away. Toasty is never picked because it is a boss.

Level Locks is off by default. Balloonist requirements still apply on top of it, so a key
for a level in a homeworld you can't reach yet won't open that level until you get there.

## Spyro 1 goals

- **Gnasty Gnorc** — the default goal: reach and defeat Gnasty Gnorc
- **Gnasty's Loot** — unlock the bonus level (all dragons, all eggs, 12,000 gems) and
  collect all of its gems
- **All Dragons** — rescue all 80 dragons and defeat Gnasty Gnorc

> **Note:** *All Dragons* is reported complete when Gnasty Gnorc is defeated —
> the 80-dragon requirement is checked at generation time, not by the in-game
> client.

## Spyro 2 (Ripto's Rage!)

### What is randomized? (Spyro 2)

- **64 orbs** — each of the game's orb challenges is a check named after its on-screen
  text, e.g. **Spyro 2: Glimmer: Lizard hunt** or **Spyro 2: Metropolis: Ox bombing**.
  Shuffled by default: each releases a **Spyro 2: Orb** item into the pool, and the
  game's orb doors (Ocean Speedway 3, Metro Speedway 6, Cloud Temples 15, Metropolis
  25, the Autumn Plains professor door 8, Ripto's Arena 40) open on received Orb
  items — the mod keeps the game's orb counter in sync with them
- **14 talismans** — collectibles like the Magic Pick and the Volcano Idol are checks
- **Gem milestones** — 25/50/75/100% of the 400 gems in each of the 21 gem-bearing
  levels (the 4 speedways, the 3 boss dungeons and Dragon Shores have no
  save-recorded gems and get none)
- **Money Bags abilities** — Swim (Summer Forest), Climb (Autumn Plains) and
  Headbash (Winter Tundra) purchases are checks
- **Bosses** — defeating Crush, Gulp and Ripto are checks

### Moneybags Abilities (Spyro 2)

- **Vanilla** (default) — the abilities are the game's own progression: paying Money
  Bags works as normal and sends the check.
- **Sanity** — the three abilities are shuffled progression items (**Spyro 2: Swim
  Ability**, **Spyro 2: Climb Ability**, **Spyro 2: Headbash Ability**). The game's
  purchases are neutralized: paying before you have received the item revokes the
  ability, and receiving the item grants it. Sanity also adds ability logic — several
  levels and challenges genuinely need an ability in Reignited (for example,
  **Glimmer: All Gems requires Climb**, which contradicts the PS1 guides), so without
  the item those checks stay out of logic.

### Spyro 2 goal

- **None** — Spyro 2 cannot be a required game; its checks are optional side content.
- **Ripto** — Spyro 2 becomes requirable: Crush, Gulp and Ripto must fall. With
  Moneybags Abilities shuffled, reaching Ripto's Arena itself needs the Headbash
  item (the castle gate is Headbash-gated in Reignited). The boss doors' talisman
  counters (6 Summer Forest talismans for Crush's Dungeon, all 14 for Gulp's
  Overlook) stay the game's own progression — they are not shuffled; the orb
  doors follow Orb items (above).
## Spyro 3 (Year of the Dragon)

### What is randomized? (Spyro 3)

- **Gem milestones** — 25/50/75/100% of the gems in each of the 29 gem-bearing
  levels (the 4 speedways and the boss/challenge dungeons have no save-recorded
  gems and get none). Names use the on-screen level text, e.g.
  **Spyro 3: Sunrise Spring: 25% Gems** or **Spyro 3: Super Bonus Round: All Gems**.
- **Dragon eggs** — all 150 eggs are checks, named after the dragon inside,
  e.g. **Spyro 3: Sunny Villa: Sanders** or **Spyro 3: Midnight Mountain: Al**
  (Al is the Moneybags chase egg). The egg *checks* cannot be turned off;
  whether they release items is the **Shuffle Dragon Eggs** option below.
- **Skill points** — the 20 skill points are checks named after their task,
  e.g. **Spyro 3: Sunny Villa: Flame all trees (Skill Point)**.
- **Sparx powers** — with **Enable Sparx Power Checks** on, completing each of
  the 3 Sparx realms (Crawdad Farm, Starfish Reef and Bugbot Factory — the last
  opens after the Sorceress falls) is an ordinary check: **Spyro 3: Crawdad
  Farm: Sparx Gem Collect Range (Power)**, **Spyro 3: Starfish Reef: Sparx
  Extra Hit Point (Power)** and **Spyro 3: Bugbot Factory: Sparx Chest
  Breaking (Power)**. The three Sparx power items are shuffled useful items in
  the pool, not tied to their realm; the powers themselves gate nothing. The
  4th Sparx power's gem radar is not randomized because Reignited ships it
  default-on.

### Shuffle Dragon Eggs (Spyro 3)

- **On** (default) — each of the 146 egg checks releases a shuffled
  **Spyro 3: Dragon Egg** item into the pool (the 4 boss-dungeon eggs are
  boss-defeat checks and release nothing).
- **Off** — the eggs are vanilla collectibles: the egg locations stay checks
  but release nothing.

### Level Locks (Spyro 3)

With **Level Locks** on, every level portal in the 4 homeworlds (Sunrise Spring,
Midday Gardens, Evening Lake, Midnight Mountain) is locked until you find its key
item: **Spyro 3: Sunny Villa Key**, **Spyro 3: Dino Mines Key**, and so on (all 33
sub-levels, no spawn key — the spawn level is a homeworld). The homeworlds
themselves stay open: reaching the next homeworld is the game's own progression
(defeat Buzz, Spike and Scorch), exactly like the game's vanilla flow.

Skill points never gate anything — no skill-point item opens a door, and no
check requires one. Eggs do gate: the 14 egg portals (which need 10/20/30/…/140
eggs) count received **Spyro 3: Dragon Egg** items when **Shuffle Dragon Eggs**
is on.
