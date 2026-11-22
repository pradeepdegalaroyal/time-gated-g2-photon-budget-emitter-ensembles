"""Photon-level time-tag simulation used to validate the analytic state model."""
from __future__ import annotations

import numpy as np

from .config import Scenario
from .timing import full_window


def _background_times(scn: Scenario, n: int, rng: np.random.Generator, w0: float, w1: float) -> np.ndarray:
    comp = rng.choice(3, size=n, p=[scn.w_prompt, scn.w_auto, scn.w_flat])
    t = np.empty(n)
    for c in range(3):
        idx = comp == c
        k = int(idx.sum())
        if c == 0:
            t[idx] = rng.normal(0, scn.sigma, k)
        elif c == 1:
            t[idx] = rng.exponential(scn.tau_a, k) + rng.normal(0, scn.sigma, k)
        else:
            t[idx] = rng.uniform(w0, w1, k)
    return t


def simulate_g2(scn: Scenario, gate: tuple[float, float], m_pulses: int, rng: np.random.Generator) -> dict:
    """Simulate time-tagged photons, apply the gate and return gated HBT statistics.

    Returns the gated second-order correlation estimate and the empirical gate
    fractions of signal and background photons.
    """
    w0, w1 = full_window(scn)
    g0, g1 = gate
    n_sig = rng.binomial(scn.n_emit, scn.q, size=m_pulses)
    n_bg = rng.poisson(scn.beta0, size=m_pulses)
    ns, nb = int(n_sig.sum()), int(n_bg.sum())
    t_s = rng.exponential(scn.tau_s, ns) + rng.normal(0, scn.sigma, ns)
    t_b = _background_times(scn, nb, rng, w0, w1)
    pulse_s = np.repeat(np.arange(m_pulses), n_sig)
    pulse_b = np.repeat(np.arange(m_pulses), n_bg)
    keep_s = (t_s >= g0) & (t_s <= g1)
    keep_b = (t_b >= g0) & (t_b <= g1)
    pulses = np.concatenate([pulse_s[keep_s], pulse_b[keep_b]])
    det = rng.integers(0, 2, size=pulses.size)
    n_a = np.bincount(pulses[det == 0], minlength=m_pulses).astype(float)
    n_b = np.bincount(pulses[det == 1], minlength=m_pulses).astype(float)
    if scn.chi > 0:
        n_a, n_b = (n_a + rng.binomial(n_b.astype(int), scn.chi),
                    n_b + rng.binomial(n_a.astype(int), scn.chi))
    g2 = (n_a * n_b).mean() / (n_a.mean() * n_b.mean())
    return {
        "g2": float(g2),
        "f_signal": float(keep_s.sum() / max(ns, 1)),
        "f_background": float(keep_b.sum() / max(nb, 1)),
    }
