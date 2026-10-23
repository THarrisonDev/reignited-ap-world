# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

"""Every Spyro 3 location, item, event, region and group name carries this prefix."""
from ..data import load

PREFIX = load("spyro3").prefix


def s3(name: str) -> str:
    return PREFIX + name