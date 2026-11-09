"""Generation smoke tests for the Spyro Reignited Trilogy world.

Runs real Archipelago generation (Fill, reachability, beatability) for each game
alone and all three together, and pins the slot-data contract the client mod
resolves names and options against. Run from an Archipelago checkout with this
world placed at worlds/reignited:

    python -m pytest worlds/reignited/test
"""
import inspect
import unittest
from argparse import Namespace
from typing import Set

from BaseClasses import CollectionState, MultiWorld
from test.bases import WorldTestBase
from test.general import gen_steps
from worlds import AutoWorld
from worlds.AutoWorld import call_all
from worlds.reignited import SpyroReignitedWorld


def ut_regen_world(game: str, slot_data: dict):
    """Build a world the way Universal Tracker does on connect: default options
    plus the seed's slot data, with no YAML."""
    multiworld = MultiWorld(1)
    multiworld.game[1] = game
    multiworld.player_name = {1: "Tester"}
    multiworld.set_seed()
    multiworld.generation_is_fake = True
    multiworld.re_gen_passthrough = {game: slot_data}
    args = Namespace()
    world_type = AutoWorld.AutoWorldRegister.world_types[game]
    for name, option in world_type.options_dataclass.type_hints.items():
        setattr(args, name, {1: option.from_any(option.default)})
    multiworld.set_options(args)
    multiworld.state = CollectionState(multiworld)
    world = multiworld.worlds[1]
    for step in gen_steps:
        call_all(multiworld, step)
    return world


class SRTTestBase(WorldTestBase):
    """One Spyro Reignited Trilogy world under the options each subclass sets."""

    game = "Spyro Reignited Trilogy"

    def assert_slot_data_contract(self, games: Set[str]) -> None:
        """Pin the top-level slot-data shape the client depends on."""
        sd = self.world.fill_slot_data()
        self.assertEqual(set(sd["included_games"]), games)
        self.assertTrue(set(sd["required_games"]) <= games)
        self.assertEqual(set(sd["games"]), games)
        for key in ("death_link", "enable_filler_extra_lives",
                    "enable_filler_color_change", "enable_trap_damage"):
            self.assertIn(key, sd["options"])
        name_to_id = self.world.location_name_to_id
        self.assertTrue(sd["locationNameToId"], "slot data carries no locations")
        for name, address in sd["locationNameToId"].items():
            self.assertEqual(name_to_id.get(name), address, f"{name} id mismatch")
            self.assertIsInstance(address, int)
        for key in games:
            for field in ("options", "level_keys", "goal_location"):
                self.assertIn(field, sd["games"][key], f"{key} slot data lacks {field}")
        ids = list(name_to_id.values())
        self.assertEqual(len(ids), len(set(ids)), "duplicate location ids in the slot")


class TestSpyro1Only(SRTTestBase):
    options = {"included_games": ["Spyro 1"]}

    def test_slot_data(self) -> None:
        self.assert_slot_data_contract({"spyro1"})
        # Spyro 1 alone carries the balloonist gates the mod re-tunes.
        sd = self.world.fill_slot_data()
        self.assertIn("gate_requirements", sd["games"]["spyro1"])


class TestSpyro1AllDragonsGoal(TestSpyro1Only):
    """All Dragons must report a goal location so the slot can finish at all
    (the 80-dragon count is enforced at generation, not by the client)."""

    options = {"included_games": ["Spyro 1"], "spyro1_goal": "all_dragons"}

    def test_goal_location_is_reportable(self) -> None:
        sd = self.world.fill_slot_data()
        goal_location = sd["games"]["spyro1"]["goal_location"]
        self.assertTrue(goal_location, "all_dragons slot emits no goal location")
        self.assertEqual(
            goal_location,
            self.world.location_name_to_id["Spyro 1: Gnasty Gnorc Defeated"],
        )


class TestSpyro2Only(SRTTestBase):
    options = {"included_games": ["Spyro 2"], "spyro2_goal": "Ripto"}

    def test_slot_data(self) -> None:
        self.assert_slot_data_contract({"spyro2"})


class TestSpyro3Only(SRTTestBase):
    options = {"included_games": ["Spyro 3"], "spyro3_goal": "Sorceress"}

    def test_slot_data(self) -> None:
        self.assert_slot_data_contract({"spyro3"})


class TestAllGames(SRTTestBase):
    options = {
        "included_games": ["Spyro 1", "Spyro 2", "Spyro 3"],
        "spyro2_goal": "Ripto",
        "spyro3_goal": "Sorceress",
    }

    def test_slot_data(self) -> None:
        self.assert_slot_data_contract({"spyro1", "spyro2", "spyro3"})
        sd = self.world.fill_slot_data()
        self.assertEqual(set(sd["required_games"]), {"spyro1", "spyro2", "spyro3"})

    def test_shuffle_options_are_ints(self) -> None:
        """The mod reads these as ordinals; a string would silently disarm it."""
        games = self.world.fill_slot_data()["games"]
        self.assertIsInstance(games["spyro1"]["options"]["dragon_shuffle"], int)
        self.assertIsInstance(games["spyro2"]["options"]["orb_shuffle"], int)
        self.assertIsInstance(games["spyro3"]["options"]["egg_shuffle"], int)


class TestShuffledGates(SRTTestBase):
    """spyro1_balloonist_gates = shuffled re-rolls each balloonist between its
    vanilla number and the most of that collectible obtainable before it."""

    options = {"included_games": ["Spyro 1"], "spyro1_balloonist_gates": "shuffled"}

    VANILLA = {
        "Peace Keepers": 10,
        "Magic Crafters": 1200,
        "Beast Makers": 5,
        "Dream Weavers": 50,
        "Gnorc Gnexus": 6000,
    }
    CEILING = {
        "Peace Keepers": ("dragons", 16),
        "Magic Crafters": ("gems", 3000),
        "Beast Makers": ("eggs", 12),
        "Dream Weavers": ("dragons", 58),
        "Gnorc Gnexus": ("gems", 10500),
    }

    def test_requirements_stay_between_vanilla_and_ceiling(self) -> None:
        gates = self.world.fill_slot_data()["games"]["spyro1"]["gate_requirements"]
        for homeworld, (kind, ceiling) in self.CEILING.items():
            with self.subTest(homeworld=homeworld):
                req = gates[homeworld]
                self.assertEqual(req["type"], kind)
                self.assertGreaterEqual(req["needed"], self.VANILLA[homeworld])
                self.assertLessEqual(req["needed"], ceiling)

    def test_ceilings_are_the_obtainable_maximum(self) -> None:
        """Pin the derived ceiling per gate (independent of any roll)."""
        spyro1 = next(game for game in self.world.games if game.key == "spyro1")
        ceilings = spyro1._gate_ceilings()
        for homeworld, (_kind, ceiling) in self.CEILING.items():
            with self.subTest(homeworld=homeworld):
                self.assertEqual(ceilings[homeworld], ceiling)

    def test_shuffled_gates_fill_across_seeds(self) -> None:
        """Real Fill per seed: a raised gate must still leave a solvable seed."""
        for seed in range(1, 6):
            with self.subTest(seed=seed):
                self.world_setup(seed=seed)
                self.test_fill()


class TestShuffledGatesWithLocks(TestShuffledGates):
    """The ceiling counts every earlier level, but level locks turn those levels
    into key items, so the combination must still fill."""

    options = {
        "included_games": ["Spyro 1"],
        "spyro1_balloonist_gates": "shuffled",
        "spyro1_level_locks": True,
    }


class TestExtraLivesDisabled(SRTTestBase):
    """With Extra Lives off but colour change on, no Extra Life may reach the pool."""

    options = {
        "included_games": ["Spyro 1"],
        "enable_filler_extra_lives": False,
        "enable_filler_color_change": True,
    }

    def test_no_extra_lives_in_pool(self) -> None:
        pool = [item.name for item in self.multiworld.itempool]
        self.assertNotIn("Extra Life", pool)
        self.assertIn("Turn Spyro Red", pool)


class TestAllFillersDisabled(SRTTestBase):
    """Every filler and trap off must still leave something to fill the pool."""

    options = {
        "included_games": ["Spyro 1"],
        "enable_filler_extra_lives": False,
        "enable_filler_color_change": False,
        "enable_trap_damage": False,
    }

    def test_fallback_filler_used(self) -> None:
        pool = [item.name for item in self.multiworld.itempool]
        self.assertIn("Extra Life", pool)
        self.assertNotIn("Damage Trap", pool)


class TestUTRegen(SRTTestBase):
    """Universal Tracker regenerates this slot from its slot data alone, so the
    regenerated options, locations and balloonist gates must match the seed."""

    options = {
        "included_games": ["Spyro 1", "Spyro 2"],
        "spyro2_goal": "Ripto",
        "spyro1_balloonist_gates": "shuffled",
        "spyro1_level_locks": True,
    }

    def test_regen_from_slot_data(self) -> None:
        seed_slot_data = self.world.fill_slot_data()
        regen_slot_data = ut_regen_world(self.game, seed_slot_data).fill_slot_data()

        self.assertEqual(
            regen_slot_data["included_games"], seed_slot_data["included_games"]
        )
        self.assertEqual(
            regen_slot_data["required_games"], seed_slot_data["required_games"]
        )
        self.assertEqual(set(regen_slot_data["games"]), set(seed_slot_data["games"]))
        self.assertEqual(
            set(regen_slot_data["locationNameToId"].items()),
            set(seed_slot_data["locationNameToId"].items()),
        )
        self.assertEqual(
            regen_slot_data["games"]["spyro1"]["gate_requirements"],
            seed_slot_data["games"]["spyro1"]["gate_requirements"],
        )
        for key in seed_slot_data["games"]:
            with self.subTest(game=key):
                self.assertEqual(
                    regen_slot_data["games"][key]["options"],
                    seed_slot_data["games"][key]["options"],
                )
        seed_slot_data.pop("seed")
        regen_slot_data.pop("seed")
        self.assertEqual(regen_slot_data, seed_slot_data)


class TestOpenWorldSlotData(SRTTestBase):
    """Open World frees hub travel; the client marks homeworlds visited."""

    options = {
        "included_games": ["Spyro 1", "Spyro 2", "Spyro 3"],
        "spyro2_goal": "Ripto",
        "spyro3_goal": "Sorceress",
        "open_world": True,
    }

    def test_slot_data_marks_open_world(self) -> None:
        sd = self.world.fill_slot_data()
        self.assertEqual(sd["options"]["open_world"], 1)
        for game in ("spyro1", "spyro2", "spyro3"):
            with self.subTest(game=game):
                self.assertEqual(sd["games"][game]["options"]["open_world"], 1)
                self.assertNotIn("open_world_regions", sd["games"][game])

    def test_only_the_homeworld_chain_is_waived(self) -> None:
        spyro2 = next(game for game in self.world.games if game.key == "spyro2")
        self.assertNotIn("bosses", spyro2.gates.gates["Autumn Plains"])
        self.assertNotIn("bosses", spyro2.gates.gates["Winter Tundra"])
        # Boss arenas and levels keep everything they had.
        self.assertIn("talismans", spyro2.gates.gates["Crush's Dungeon"])
        self.assertIn("orbs", spyro2.gates.gates["Gulp's Overlook"])
        self.assertIn("orbs", spyro2.gates.gates["Ocean Speedway"])
        self.assertIn("payments", spyro2.gates.gates["Zephyr"])
        spyro3 = next(game for game in self.world.games if game.key == "spyro3")
        for hub in ("Midday Gardens", "Evening Lake", "Midnight Mountain"):
            with self.subTest(hub=hub):
                self.assertNotIn("bosses", spyro3.gates.gates[hub])
        for level, keys in (
            ("Molten Crater", ("eggs",)),
            ("Buzz's Dungeon", ("levels", "payments")),
            ("Sorceress Lair", ("eggs",)),
            ("Super Bonus Round", ("eggs", "gems", "levels")),
        ):
            with self.subTest(level=level):
                for key in keys:
                    self.assertIn(key, spyro3.gates.gates[level])

    def test_regenerated_slot_matches(self) -> None:
        """Universal Tracker regenerates an Open World slot from slot data alone."""
        seed = self.world.fill_slot_data()
        regen = ut_regen_world(self.game, seed).fill_slot_data()
        seed.pop("seed")
        regen.pop("seed")
        self.assertEqual(regen, seed)

    def test_egg_gates_survive_the_waiver(self) -> None:
        """The mod needs the vanilla egg numbers for the egg-gate lever."""
        sd = self.world.fill_slot_data()["games"]["spyro3"]
        self.assertEqual(sd["egg_gates"]["Molten Crater"], 10)
        self.assertEqual(sd["egg_gates"]["Sorceress Lair"], 100)


class TestOpenWorldSpyro1(SRTTestBase):
    options = {"included_games": ["Spyro 1"], "open_world": True}

    def test_every_homeworld_reachable_at_start(self) -> None:
        for homeworld in ("Peace Keepers", "Magic Crafters", "Beast Makers",
                          "Dream Weavers", "Gnorc Gnexus"):
            with self.subTest(homeworld=homeworld):
                self.assertTrue(
                    self.can_reach_region(f"Spyro 1: {homeworld}"),
                    f"{homeworld} still needs a balloonist requirement",
                )


class TestClosedWorldSpyro1(SRTTestBase):
    """Control: without the option the balloonists still gate the homeworlds."""

    options = {"included_games": ["Spyro 1"]}

    def test_balloonist_still_gates_peace_keepers(self) -> None:
        self.assertFalse(self.can_reach_region("Spyro 1: Peace Keepers"))


class TestOpenWorldSpyro2(SRTTestBase):
    options = {"included_games": ["Spyro 2"], "spyro2_goal": "Ripto",
               "open_world": True}

    def test_homeworlds_reachable_but_arenas_keep_their_counts(self) -> None:
        self.assertTrue(self.can_reach_region("Spyro 2: Autumn Plains"))
        self.assertTrue(self.can_reach_region("Spyro 2: Winter Tundra"))
        # Crush's Dungeon keeps Swim + its talisman count; with Swim held the
        # Summer Forest talismans become obtainable, which is the vanilla rule.
        self.assertFalse(self.can_reach_region("Spyro 2: Crush's Dungeon"))
        self.collect(self.world.create_item("Spyro 2: Swim Ability"))
        self.assertTrue(self.can_reach_region("Spyro 2: Crush's Dungeon"))


class TestOpenWorldSpyro3(SRTTestBase):
    options = {"included_games": ["Spyro 3"], "spyro3_goal": "Sorceress",
               "open_world": True}

    def test_homeworlds_reachable_but_levels_keep_their_gates(self) -> None:
        for hub in ("Midday Gardens", "Evening Lake", "Midnight Mountain"):
            with self.subTest(hub=hub):
                self.assertTrue(self.can_reach_region(f"Spyro 3: {hub}"))
        self.assertFalse(self.can_reach_region("Spyro 3: Molten Crater"))
        self.assertFalse(self.can_reach_region("Spyro 3: Buzz's Dungeon"))
        self.assertFalse(self.can_reach_region("Spyro 3: Super Bonus Round"))


class TestOpenWorldWithLevelLocks(SRTTestBase):
    """Open World frees hubs; Level Locks gate the level portals. They combine."""

    options = {"included_games": ["Spyro 1"], "open_world": True,
               "spyro1_level_locks": True}

    def test_both_options_generate_and_fill(self) -> None:
        sd = self.world.fill_slot_data()
        self.assertEqual(sd["options"]["open_world"], 1)
        self.assertEqual(sd["games"]["spyro1"]["options"]["level_locks"], 1)
        self.assertGreater(len(sd["games"]["spyro1"]["level_keys"]), 0)


class TestUTContract(unittest.TestCase):
    """The contract Universal Tracker checks before taking the regeneration path."""

    def test_regeneration_hooks(self) -> None:
        self.assertIs(SpyroReignitedWorld.ut_can_gen_without_yaml, True)
        self.assertIsInstance(
            inspect.getattr_static(SpyroReignitedWorld, "interpret_slot_data"),
            staticmethod,
        )
