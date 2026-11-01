"""Names vulture must not report as dead (read by `make deadcode`).

Archipelago and the data engine reach into this package by name — through
`world.options.*`, option metaclass attributes, enum values it iterates, and
the World methods it calls on the class it loads from `archipelago.json` — so a
static reference exists for none of them. Add a name here only when the caller
lives outside this package or is generated; a name unused even by those belongs
deleted, not whitelisted.
"""

# The World class and the methods Archipelago calls on it.
SpyroReignitedWorld
create_items
get_filler_item_name

# World class attributes read by the AP launcher / WebHost.
bug_report_page
data_version
game_info_languages
options_dataclass
required_client_version
theme
topology_present
tutorials
web

# Universal Tracker's regeneration surface: the flag it checks, the hook it
# calls, and the MultiWorld attribute it sets before generating.
ut_can_gen_without_yaml
interpret_slot_data
generation_is_fake

# Option metaclass fields and members: `options_dataclass` turns each option
# class into an `options_<snake_case_name>` attribute at world-build time.
accessibility
option_all_dragons
option_dragonsanity
option_gnastys_loot
option_gnasty
option_none
option_ripto
option_sanity
option_shuffled
option_sorceress
option_vanilla
range_end
range_start
valid_keys

# Enum members compared in bulk or reached through Enum(value) only.
NORMAL
T25
T50
T75
T100
