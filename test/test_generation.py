"""Generation smoke tests for the Spyro Reignited Trilogy world.

Runs real Archipelago generation (Fill, reachability, beatability) for each game
alone and all three together, and pins the slot-data contract the client mod
resolves names and options against. Run from an Archipelago checkout with this
world placed at worlds/reignited:

    python -m pytest worlds/reignited/test
"""
from typing import Set

from test.bases import WorldTestBase


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
