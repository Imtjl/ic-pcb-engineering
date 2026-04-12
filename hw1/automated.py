#!/usr/bin/env python3
"""
Universal thin-film hybrid IC (GIS) calculator.
Supports arbitrary resistor/capacitor sets from the ITMO textbook.

Usage: Edit the VARIANT section at the bottom, then run.
"""

import math
import sys
from dataclasses import dataclass

# ─── Material databases ───────────────────────────────────────────

RESISTIVE_MATERIALS = [
    {"name": "Сплав РС-3001",  "rho_min": 800,  "rho_max": 3000,  "R_min": 50,  "R_max": 30000,  "W0": 2},
    {"name": "Сплав РС-3710",  "rho_min": 100,  "rho_max": 2000,  "R_min": 10,  "R_max": 20000,  "W0": 2},
    {"name": "Кермет К-50С",   "rho_min": 1000, "rho_max": 10000, "R_min": 100, "R_max": 100000, "W0": 2},
    {"name": "Спец. сплав №3", "rho_min": 350,  "rho_max": 500,   "R_min": 100, "R_max": 50000,  "W0": 2},
    {"name": "Тантал ТВЧ",     "rho_min": 10,   "rho_max": 100,   "R_min": 1,   "R_max": 1000,   "W0": 3},
    {"name": "Нихром",         "rho_min": 50,   "rho_max": 300,   "R_min": 5,   "R_max": 3000,   "W0": 1},
    {"name": "Хром",           "rho_min": 500,  "rho_max": 500,   "R_min": 50,  "R_max": 30000,  "W0": 1},
]

DIELECTRIC_MATERIALS = [
    {"name": "Пятиокись тантала", "plates": "Тантал ТВЧ", "C0_min": 60000, "C0_max": 200000, "V_min": 10, "V_max": 15, "eps": 23},
]

@dataclass
class Resistor:
    name: str
    R: float; delta: float; W: float
    kf: float = 0.0; b: float = 0.0; l: float = 0.0
    form: str = ""; R_actual: float = 0.0; delta_actual: float = 0.0

@dataclass
class Capacitor:
    name: str; C: float
    S: float = 0.0; side: float = 0.0; construction: str = ""

@dataclass
class NavesElement:
    name: str; width: float = 1.0; height: float = 1.0


class GISCalculator:
    def __init__(self, resistors, capacitors, naves=None, H=0.1):
        self.resistors = resistors
        self.capacitors = capacitors
        self.naves = naves or []
        self.H = H
        self.rho_sq = 0; self.W0 = 0; self.C0 = 0
        self.material_name = ""; self.cap_material_name = ""

    def calculate_all(self):
        self._calc_rho_optimal()
        self._select_material()
        self._calc_form_coefficients()
        self._check_meanders()
        self._calc_resistors()
        self._calc_capacitors()
        self._print_summary()

    def _calc_rho_optimal(self):
        s = sum(r.R for r in self.resistors)
        si = sum(1.0 / r.R for r in self.resistors)
        raw = math.sqrt(s / si)
        self.rho_sq = round(raw / 100) * 100 or 100
        print("=" * 60)
        print("1. РАСЧЁТ ρ□")
        print(f"   ρ_опт = {raw:.3f} → ρ□ = {self.rho_sq} Ом/□")

    def _select_material(self):
        def centrality(m):
            span = m["rho_max"] - m["rho_min"]
            if span == 0: return 0
            pos = (self.rho_sq - m["rho_min"]) / span
            return 1.0 - abs(pos - 0.5) * 2

        candidates = [m for m in RESISTIVE_MATERIALS
                       if m["rho_min"] <= self.rho_sq <= m["rho_max"]
                       and all(m["R_min"] <= r.R <= m["R_max"] for r in self.resistors)]

        if candidates:
            chosen = max(candidates, key=lambda m: (centrality(m), m["W0"]))
        else:
            def dist(m):
                if self.rho_sq < m["rho_min"]: return m["rho_min"] - self.rho_sq
                if self.rho_sq > m["rho_max"]: return self.rho_sq - m["rho_max"]
                return 0
            chosen = min(RESISTIVE_MATERIALS, key=dist)
            print(f"   ⚠ Нет точного попадания, ближайший: {chosen['name']}")

        self.material_name = chosen["name"]
        self.W0 = chosen["W0"]
        print(f"   Материал: {self.material_name} "
              f"({chosen['rho_min']}–{chosen['rho_max']} Ом/□, W₀={self.W0})")

    def _calc_form_coefficients(self):
        print("\n" + "=" * 60)
        print("2. КОЭФФИЦИЕНТЫ ФОРМЫ")
        for r in self.resistors:
            r.kf = r.R / self.rho_sq
            if r.kf < 1:   r.form = "rect (l < b)"
            elif r.kf <= 10: r.form = "rect (l > b)"
            else:           r.form = "МЕАНДР"
            print(f"   {r.name}: kф = {r.kf:.3f} → {r.form}")

    def _check_meanders(self):
        bad = [r for r in self.resistors if r.kf >= 10]
        if bad:
            print("\n" + "!" * 60)
            print("!!! МЕАНДР ОБНАРУЖЕН! НЕ ПОДДЕРЖИВАЕТСЯ! !!!")
            for r in bad: print(f"!!!   {r.name}: kф = {r.kf:.3f}")
            print("!" * 60)
            sys.exit(1)

    def _calc_resistors(self):
        print("\n" + "=" * 60)
        print("3. РАЗМЕРЫ РЕЗИСТОРОВ")
        for r in self.resistors:
            b_prec = 0.3 if r.delta <= 10 else 0.2
            b_w = math.sqrt(self.rho_sq * r.W / (r.R * self.W0)) * 10

            r.b = math.ceil(max(b_prec, b_w) / self.H) * self.H
            r.b = round(r.b, 1)

            for _ in range(50):
                r.l = round(round(r.kf * r.b / self.H) * self.H, 1)
                if r.l < 0.5: r.l = 0.5
                r.R_actual = self.rho_sq * r.l / r.b
                r.delta_actual = abs(r.R - r.R_actual) / r.R * 100
                if r.delta_actual <= r.delta / 2:
                    break
                r.b = round(r.b + self.H, 1)

            ok = "✅" if r.delta_actual <= r.delta else "⚠️"
            print(f"   {r.name}: b={r.b}, l={r.l}  |  "
                  f"bw={b_w:.3f}, bт={b_prec}  |  "
                  f"R'={r.R_actual:.1f}, ΔR'={r.delta_actual:.1f}% {ok}")

    def _calc_capacitors(self):
        if not self.capacitors: return
        print("\n" + "=" * 60)
        print("4. КОНДЕНСАТОРЫ")
        chosen = DIELECTRIC_MATERIALS[0]  # Пятиокись тантала
        self.C0 = chosen["C0_max"]
        self.cap_material_name = chosen["name"]
        print(f"   Материал: {chosen['name']}, C₀={self.C0} пФ/см²")

        for c in self.capacitors:
            c.S = c.C / self.C0 * 100
            c.side = round(math.sqrt(c.S), 2)
            if c.S >= 5:   c.construction = "4.7а"
            elif c.S >= 1: c.construction = "4.7б"
            else:          c.construction = "4.7в"
            print(f"   {c.name}: S={c.S:.3f} мм² → {c.side}×{c.side}  ({c.construction})")

    def _print_summary(self):
        print("\n" + "=" * 60)
        print("ИТОГО")
        print(f"{'Эл-т':<8}{'l мм':>6}{'b мм':>7}  Материал")
        print("-" * 45)
        for r in self.resistors:
            print(f"{r.name:<8}{r.l:>6}{r.b:>7}  {self.material_name}")
        for c in self.capacitors:
            print(f"{c.name:<8}{c.side:>6}{c.side:>7}  {self.cap_material_name}")
        for n in self.naves:
            print(f"{n.name:<8}{n.width:>6}{n.height:>7}  навесной")

        S_R = sum(r.l * r.b for r in self.resistors)
        S_C = sum(c.S for c in self.capacitors)
        S_nav = sum(n.width * n.height for n in self.naves)
        S_K = (len(self.naves) * 3 + 4) * 0.49
        S = (S_R + S_C + S_K + S_nav) / 0.5
        print(f"\n   Подложка ≈ {S:.0f} мм² (~{math.sqrt(S):.0f}×{math.sqrt(S):.0f} мм)")

if __name__ == "__main__":
    resistors = [
        Resistor("R1", R=520,  delta=10, W=0.01),
        Resistor("R2", R=800,  delta=10, W=0.01),
        Resistor("R3", R=7000, delta=10, W=0.005),
        Resistor("R4", R=4300, delta=10, W=0.01),
        Resistor("R5", R=4300, delta=20, W=0.005),
    ]
    capacitors = [Capacitor("C1", C=6300)]
    naves = [NavesElement("VT1"), NavesElement("VT2")]

    GISCalculator(resistors, capacitors, naves).calculate_all()
