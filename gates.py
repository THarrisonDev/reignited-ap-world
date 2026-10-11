# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

"""Game gates for the tabular games (Spyro 2/3), read from data/<game>.json.

The JSON describes what the game demands; this module turns it into
Archipelago rules. Spyrosim reads the same fields, so the logic and the
simulated player always agree on a gate.

The JSON holds: `homeworlds` (play order), `payments` (Money Bags purchases in
play order, each with a price, region, and optional check), `gates` (level
entry), `checkGates` (single checks), and `gemGates` (per-level gem tiers,
where each tier needs its gate and every lower tier's).

A gate lists conditions that must all hold: bosses, abilities, levels,
payments, or counts of talismans, orbs, eggs, and gems. Counts come from
reachable checks; gems come from reachable levels at their highest open tier.
A payment needs its region and a gem total covering every price up to it in
play order, which stays affordable whatever order the player really pays in.

A game can override a kind's counting source via `item_counts` (kind to
callable returning an int or None). Spyro 2 orbs and Spyro 3 eggs use this to
read received items when shuffled.

Evaluation runs in layers so no rule reads itself: payments grow to a fixpoint
first, then counts use those payments, and a count-gated check is judged
against the count of checks without count gates. Gates read both.
"""
from enum import Enum
from typing import Dict, List, Set

EGG_KINDS = ("egg", "boss")
COUNT_KINDS = {"talismans": ("talisman",), "orbs": ("orb",), "eggs": EGG_KINDS}
class Tier(Enum):
    """Gem tiers, in the order they open. Tier(t) validates the JSON's percent strings."""
    T25 = 25
    T50 = 50
    T75 = 75
    T100 = 100
READS_REGIONS = ("talismans", "orbs", "eggs", "gems", "payments", "levels")


class _Eval:
    """One rule evaluation against one state, with memoized payments and counts."""

    def __init__(self, gates: "Gates", state):
        self.gates = gates
        self.state = state
        self._paid = None
        self._counts: Dict[str, int] = {}
        self._base: Dict[str, int] = {}
        self._tiers: Dict[str, int] = {}
        self._gems = None
        self._reach: Dict[str, bool] = {}

    @property
    def paid(self) -> Set[str]:
        """Grown to a fixpoint on first use; while growing, it is the set so far."""
        if self._paid is None:
            self._paid = set()
            self._grow()
        return self._paid

    def reach(self, level: str) -> bool:
        if level not in self._reach:
            self._reach[level] = self.state.can_reach_region(self.gates.prefix + level, self.gates.player)
        return self._reach[level]

    def _grow(self):
        g = self.gates
        grew = True
        while grew:
            grew = False
            self._counts.clear()
            self._base.clear()
            self._tiers.clear()
            self._gems = None
            gems = self.gems()
            for payment in g.payments:
                name = payment["name"]
                if name not in self._paid and gems >= g.running_total[name] and self.reach(payment["region"]):
                    self._paid.add(name)
                    grew = True

    def simple(self, gate: dict) -> bool:
        if not gate:
            return True
        p, player, state = self.gates.prefix, self.gates.player, self.state
        return (all(state.has(p + boss, player) for boss in gate.get("bosses", ()))
                and all(state.has(f"{p}{a} Ability", player) for a in gate.get("abilities", ()))
                and all(name in self.paid for name in gate.get("payments", ()))
                and all(self.reach(level) for level in gate.get("levels", ())))

    def _counted(self, kind: str, with_counts: bool) -> int:
        g = self.gates
        override = getattr(g, "item_counts", None)
        if override is not None and kind in override:
            n = override[kind](self.state)
            if n is not None:
                return n
        n = 0
        for level, ungated, gated in g.count_plan[kind]:
            if not self.reach(level):
                continue
            n += ungated
            for name in gated:
                gate = g.check_gates[name]
                if not self.simple(gate):
                    continue
                if any(k in gate for k in COUNT_KINDS):
                    if with_counts and all(self._base_count(k) >= gate[k] for k in COUNT_KINDS if k in gate):
                        n += 1
                else:
                    n += 1
        return n

    def _base_count(self, kind: str) -> int:
        if kind not in self._base:
            self._base[kind] = self._counted(kind, False)
        return self._base[kind]

    def count(self, kind: str) -> int:
        if kind not in self._counts:
            self._counts[kind] = self._counted(kind, True)
        return self._counts[kind]

    def met(self, gate: dict) -> bool:
        if not self.simple(gate):
            return False
        if "gems" in gate and self.gems() < gate["gems"]:
            return False
        return all(self.count(kind) >= gate[kind] for kind in COUNT_KINDS if kind in gate)

    def tier(self, level: str) -> int:
        """The highest gem tier open in the level, or 0 if none are open."""
        if level not in self._tiers:
            self._tiers[level] = self._tier(level)
        return self._tiers[level]

    def _tier(self, level: str) -> int:
        tiers = self.gates.gem_gates.get(level)
        if not tiers:
            return 100
        best = 0
        for t in Tier:
            gate = tiers.get(str(t.value), {})
            if not self.simple(gate):
                break
            if any(k in gate for k in COUNT_KINDS) and \
                    not all(self._base_count(k) >= gate[k] for k in COUNT_KINDS if k in gate):
                break
            best = t.value
        return best

    def gems(self) -> int:
        if self._gems is None:
            self._gems = sum(total * self.tier(level) // 100
                             for level, total in self.gates.gem_totals.items()
                             if total and self.reach(level))
        return self._gems


class Gates:
    def __init__(self, data, player: int):
        raw = data.raw
        self.prefix = data.prefix
        self.player = player
        self.order: List[str] = list(raw["regions"])
        self.homeworlds: List[str] = raw["homeworlds"]
        self.gem_totals: Dict[str, int] = {
            level: int(r.get("gemTotal", 0)) for level, r in raw["regions"].items()}
        self.payments: List[dict] = raw["payments"]
        self.running_total: Dict[str, int] = {}
        total = 0
        for payment in self.payments:
            total += payment["price"]
            self.running_total[payment["name"]] = total
        self.gates: Dict[str, dict] = raw["gates"]
        self.check_gates: Dict[str, dict] = raw["checkGates"]
        self.gem_gates: Dict[str, dict] = raw["gemGates"]
        # kind -> [(level, checks without a gate, gated check names)]
        self.count_plan: Dict[str, list] = {}
        for kind, kinds in COUNT_KINDS.items():
            plan = []
            for level, rows in data.regions.items():
                names = [row["plain"] for row in rows if row["kind"].value in kinds]
                gated = [name for name in names if name in self.check_gates]
                if names:
                    plan.append((level, len(names) - len(gated), gated))
            self.count_plan[kind] = plan
        self._check_names(data)

    def _check_names(self, data):
        payments = {p["name"] for p in self.payments}
        gates = [*self.gates.values(), *self.check_gates.values()]
        gates += [g for tiers in self.gem_gates.values() for g in tiers.values()]
        levels = [*self.gates, *self.gem_gates, *self.homeworlds,
                  *(level for g in gates for level in g.get("levels", ())),
                  *(p["region"] for p in self.payments)]
        unknown = [level for level in levels if level not in self.order]
        unknown += [name for g in gates for name in g.get("payments", ()) if name not in payments]
        names = {row["plain"] for rows in data.regions.values() for row in rows}
        unknown += [name for name in self.check_gates if name not in names]
        unknown += [p["location"] for p in self.payments if "location" in p and p["location"] not in names]
        unknown += [t for tiers in self.gem_gates.values() for t in tiers
                    if t not in {str(tier.value) for tier in Tier}]
        if unknown:
            raise ValueError(f"{self.prefix}gate data names unknown levels, payments, checks or tiers: {unknown}")

    def homeworld_of(self, level: str) -> str:
        return [hub for hub in self.order[:self.order.index(level) + 1] if hub in self.homeworlds][-1]

    def is_homeworld(self, level: str) -> bool:
        return level in self.homeworlds

    @staticmethod
    def reads_regions(gate: dict) -> bool:
        """Whether the gate reads other regions. Such an entrance needs every region as an indirect condition."""
        return any(key in gate for key in READS_REGIONS)

    def evaluate(self, state) -> _Eval:
        """The state's evaluation, reused while items and reachable regions are unchanged."""
        key = (frozenset(state.prog_items[self.player].items()),
               len(state.reachable_regions[self.player]))
        cache = state.__dict__.setdefault("_srt_gates", {})
        hit = cache.get(self.prefix)
        if hit is None or hit[0] != key:
            hit = cache[self.prefix] = (key, _Eval(self, state))
        return hit[1]

    def rule(self, gate: dict):
        if not gate:
            return lambda state: True
        return lambda state: self.evaluate(state).met(gate)

    def payment_rule(self, name: str):
        return lambda state: name in self.evaluate(state).paid

    def gem_rule(self, level: str, threshold: int):
        return lambda state: self.evaluate(state).tier(level) >= threshold
