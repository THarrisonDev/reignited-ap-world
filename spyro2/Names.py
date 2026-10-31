# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-23

"""Every Spyro 2 location, item, event, region and group name carries this prefix."""
from ..data import load

PREFIX = load("spyro2").prefix


def s2(name: str) -> str:
    return PREFIX + name
