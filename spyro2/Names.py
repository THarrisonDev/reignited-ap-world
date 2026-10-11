# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

"""Every Spyro 2 location, item, event, region and group name carries this prefix."""
PREFIX = "Spyro 2: "


def s2(name: str) -> str:
    return PREFIX + name
