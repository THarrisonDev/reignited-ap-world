# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

"""Types shared by every game in the Spyro Reignited Trilogy world."""

from BaseClasses import Item, Location

GAME = "Spyro Reignited Trilogy"
# Default item of checks that hold no specific vanilla item.
FILLER = "Filler"


class SRTItem(Item):
    game: str = GAME


class SRTLocation(Location):
    game: str = GAME
