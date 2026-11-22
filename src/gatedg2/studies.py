"""Experiment definitions: every study returns a pandas DataFrame of raw per-seed results."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .certify import mc_m80, mc_z
from .config import Scenario
from .gate import optimise_gate
from .statemodel import Z_ALPHA, g2_expected, predicted_pulses, state_pmf
from .timetag import simulate_g2
from .timing import full_window, gate_fractions

# method name -> (estimator kind, gate mode or None for the ungated acquisition window)
METHODS = {
    "single_ungated": ("single", None),
    "hbt_ungated": ("hbt", None),
    "hbt_delay": ("hbt", "delay"),
    "hbt_window": ("hbt", "window"),
    "single_window": ("single", "window"),
}


@dataclass
class Budget:
    """Size of the study: seeds, Monte Carlo repetitions and grid density."""

    seeds: int = 5
    reps: int = 300
    quick: bool = False
    rep_null: int = 2000
    base: Scenario = field(default_factory=Scenario)


def _p1(scn: Scenario, gate) -> np.ndarray:
    f_s, f_b = gate_fractions(scn, gate[0], gate[1])
    return state_pmf(scn, f_s, f_b)[0]


def design_gate(scn: Scenario, method: str):
    """Gate used by ``method`` for ``scn`` (full window when ungated)."""
    kind, mode = METHODS[method]
    if mode is None:
        return full_window(scn)
    g0, g1, _ = optimise_gate(scn, kind, mode)
    return g0, g1


def measure(scn: Scenario, method: str, rng: np.random.Generator, reps: int, gate=None) -> dict:
    """Pulse budget (Monte Carlo and analytic) of ``method`` in scenario ``scn``."""
    kind, _ = METHODS[method]
    if gate is None:
        gate = design_gate(scn, method)
    p1 = _p1(scn, gate)
    g, v1, s0 = g2_expected(p1[None], kind)
    m_pred = float(predicted_pulses(p1[None], kind)[0])
    f_s, f_b = gate_fractions(scn, gate[0], gate[1])
    return {
        "method": method,
        "gate_start_ns": float(gate[0]),
        "gate_end_ns": float(gate[1]),
        "f_signal": float(f_s),
        "f_background": float(f_b),
        "g2_expected": float(g[0]),
        "m80_pred": m_pred,
        "m80_mc": mc_m80(p1, kind, m_pred, reps, rng),
    }


def _rng(study: int, seed: int) -> np.random.Generator:
    return np.random.default_rng(10_000 * study + seed)


def study_scaling(b: Budget) -> pd.DataFrame:
    """Pulse budget versus emitter number for two background models.

    ``proportional``: background scales with the signal (rho fixed).
    ``fixed``: background rate is that of the nominal three-emitter cell and does not grow with N.
    """
    ns = [1, 3, 6] if b.quick else [1, 2, 3, 4, 6, 8]
    methods = ["single_ungated", "hbt_ungated", "hbt_window", "single_window"]
    rows = []
    for mode in ("proportional", "fixed"):
        for n in ns:
            scn = b.base.with_(n_emit=n)
            if mode == "fixed":
                scn = scn.with_(beta_override=b.base.beta0)
            gates = {m: design_gate(scn, m) for m in methods}
            for seed in range(b.seeds):
                rng = _rng(1, seed)
                for m in methods:
                    rows.append({"background": mode, "n_emit": n, "seed": seed,
                                 **measure(scn, m, rng, b.reps, gates[m])})
    return pd.DataFrame(rows)


def study_gain_map(b: Budget) -> pd.DataFrame:
    rhos = [1, 4] if b.quick else [0.5, 1, 2, 4, 8]
    sigmas = [0.1, 1.0] if b.quick else [0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
    rows = []
    for rho in rhos:
        for sg in sigmas:
            scn = b.base.with_(rho=rho, sigma=sg)
            gates = {m: design_gate(scn, m) for m in ("hbt_ungated", "hbt_window")}
            for seed in range(b.seeds):
                rng = _rng(2, seed)
                u = measure(scn, "hbt_ungated", rng, b.reps, gates["hbt_ungated"])
                g = measure(scn, "hbt_window", rng, b.reps, gates["hbt_window"])
                rows.append({"rho": rho, "sigma_ns": sg, "seed": seed, "m80_ungated": u["m80_mc"],
                             "m80_gated": g["m80_mc"], "gain": u["m80_mc"] / g["m80_mc"],
                             "gain_pred": u["m80_pred"] / g["m80_pred"],
                             "gate_start_ns": g["gate_start_ns"], "gate_end_ns": g["gate_end_ns"],
                             "m80_pred_gated": g["m80_pred"], "m80_pred_ungated": u["m80_pred"]})
    return pd.DataFrame(rows)


def study_ablation(b: Budget) -> pd.DataFrame:
    scn = b.base
    gates = {m: design_gate(scn, m) for m in METHODS}
    rows = []
    for seed in range(b.seeds):
        rng = _rng(3, seed)
        for m in METHODS:
            rows.append({"seed": seed, **measure(scn, m, rng, b.reps, gates[m])})
    return pd.DataFrame(rows)


def study_crosstalk(b: Budget) -> pd.DataFrame:
    chis = [0.0, 1e-4, 1e-3] if b.quick else [0.0, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3]
    methods = ["single_ungated", "hbt_ungated", "hbt_window"]
    gates = {m: design_gate(b.base, m) for m in methods}
    rows = []
    for chi in chis:
        scn = b.base.with_(chi=chi)
        for seed in range(b.seeds):
            rng = _rng(4, seed)
            for m in methods:
                rows.append({"chi": chi, "seed": seed, **measure(scn, m, rng, b.reps, gates[m])})
    return pd.DataFrame(rows)


def crosstalk_threshold(b: Budget) -> dict:
    """Largest crosstalk probability for which the expected estimator stays below one (bisection)."""
    out = {}
    for m in ("single_ungated", "hbt_ungated", "hbt_window"):
        kind, _ = METHODS[m]
        gate = design_gate(b.base, m)

        def g_of(chi: float) -> float:
            return float(g2_expected(_p1(b.base.with_(chi=chi), gate)[None], kind)[0][0])

        lo, hi = 1e-9, 0.5
        for _ in range(40):
            mid = np.sqrt(lo * hi)
            lo, hi = (mid, hi) if g_of(mid) < 1.0 else (lo, mid)
        out[m] = float(np.sqrt(lo * hi))
    return out


def study_lifetime(b: Budget) -> pd.DataFrame:
    ratios = [0.25, 1.0, 2.0] if b.quick else [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
    nominal_gate = design_gate(b.base.with_(tau_a=0.5 * b.base.tau_s), "hbt_window")
    rows = []
    for r in ratios:
        scn = b.base.with_(tau_a=r * b.base.tau_s)
        gate_o = design_gate(scn, "hbt_window")
        gate_u = full_window(scn)
        for seed in range(b.seeds):
            rng = _rng(5, seed)
            u = measure(scn, "hbt_ungated", rng, b.reps, gate_u)
            o = measure(scn, "hbt_window", rng, b.reps, gate_o)
            f = measure(scn, "hbt_window", rng, b.reps, nominal_gate)
            rows.append({"tau_ratio": r, "seed": seed, "case": "mixed", "m80_ungated": u["m80_mc"],
                         "m80_oracle": o["m80_mc"], "m80_fixed": f["m80_mc"],
                         "gain_oracle": u["m80_mc"] / o["m80_mc"], "gain_fixed": u["m80_mc"] / f["m80_mc"]})
    # negative control: purely autofluorescent background with the emitter's own lifetime
    ctrl = b.base.with_(tau_a=b.base.tau_s, w_prompt=0.0, w_auto=1.0, w_flat=0.0)
    gate_o, gate_u = design_gate(ctrl, "hbt_window"), full_window(ctrl)
    for seed in range(b.seeds):
        rng = _rng(5, 100 + seed)
        u = measure(ctrl, "hbt_ungated", rng, b.reps, gate_u)
        o = measure(ctrl, "hbt_window", rng, b.reps, gate_o)
        rows.append({"tau_ratio": 1.0, "seed": seed, "case": "control_identical_profile",
                     "m80_ungated": u["m80_mc"], "m80_oracle": o["m80_mc"], "m80_fixed": np.nan,
                     "gain_oracle": u["m80_mc"] / o["m80_mc"], "gain_fixed": np.nan})
    return pd.DataFrame(rows)


def study_detection_probability(b: Budget) -> pd.DataFrame:
    """Sensitivity to the per-emitter detection probability ``q`` (excitation x collection)."""
    qs = [2e-3, 1e-2] if b.quick else [1e-3, 2e-3, 5e-3, 1e-2, 2e-2]
    methods = ["hbt_ungated", "hbt_window", "single_window"]
    rows = []
    for q in qs:
        scn = b.base.with_(q=q)
        gates = {m: design_gate(scn, m) for m in methods}
        for seed in range(b.seeds):
            rng = _rng(6, seed)
            for m in methods:
                rows.append({"q": q, "seed": seed, **measure(scn, m, rng, b.reps, gates[m])})
    return pd.DataFrame(rows)


def study_null(b: Budget):
    """Type-I error under a Poisson (classical) null with the same mean count rate."""
    targets = [50, 500] if b.quick else [50, 500, 5000]
    gate_nom = design_gate(b.base, "hbt_window")
    f_s, f_b = gate_fractions(b.base, *gate_nom)
    nominal_means = {
        "single_ungated": b.base.n_emit * b.base.q + b.base.beta0,
        "hbt_ungated": b.base.n_emit * b.base.q + b.base.beta0,
        "hbt_window": b.base.n_emit * b.base.q * float(f_s) + b.base.beta0 * float(f_b),
    }
    rows, zs = [], []
    for seed in range(b.seeds):
        rng = _rng(7, seed)
        for m, mean in nominal_means.items():
            kind, _ = METHODS[m]
            null = b.base.with_(n_emit=0, beta_override=mean)
            p1 = state_pmf(null, np.array([1.0]), np.array([1.0]))[0]
            for e0 in targets:
                m_pulses = e0 / (mean / 2) ** 2 if kind == "hbt" else 2 * e0 / mean**2
                z, _ = mc_z(p1, kind, m_pulses, b.rep_null, rng)
                rows.append({"method": m, "e0_target": e0, "seed": seed, "type1": float(np.mean(z < -Z_ALPHA)),
                             "z_mean": float(np.mean(z)), "z_std": float(np.std(z))})
                if e0 == 500:
                    zs.extend({"method": m, "seed": seed, "z": float(v)} for v in z[:400])
    return pd.DataFrame(rows), pd.DataFrame(zs)


def study_validation(b: Budget) -> pd.DataFrame:
    """Photon-level time-tag simulation versus the analytic state model."""
    scn = b.base.with_(q=0.02)
    m_pulses = 300_000 if b.quick else 1_500_000
    cases = {
        "ungated": (scn, full_window(scn)),
        "delay_gate": (scn, design_gate(scn, "hbt_delay")),
        "window_gate": (scn, design_gate(scn, "hbt_window")),
        "window_gate_chi1e-2": (scn.with_(chi=1e-2), design_gate(scn, "hbt_window")),
    }
    rows = []
    for name, (s, gate) in cases.items():
        f_s, f_b = gate_fractions(s, *gate)
        g_an = float(g2_expected(state_pmf(s, f_s, f_b), "hbt")[0][0])
        for seed in range(b.seeds):
            r = simulate_g2(s, gate, m_pulses, _rng(8, seed))
            rows.append({"case": name, "seed": seed, "g2_timetag": r["g2"], "g2_analytic": g_an,
                         "f_signal_timetag": r["f_signal"], "f_signal_analytic": float(f_s),
                         "f_background_timetag": r["f_background"], "f_background_analytic": float(f_b)})
    return pd.DataFrame(rows)
