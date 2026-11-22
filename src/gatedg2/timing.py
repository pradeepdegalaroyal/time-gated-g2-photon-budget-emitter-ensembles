"""Arrival-time profiles and gate fractions (exponentially modified Gaussian model)."""
from __future__ import annotations

import numpy as np
from scipy.special import ndtr

from .config import Scenario


def exgauss_cdf(t, tau: float, sigma: float):
    """CDF at time ``t`` of an exponential decay (lifetime ``tau``) convolved with a Gaussian response."""
    t = np.asarray(t, dtype=float)
    sigma = max(float(sigma), 1e-6)
    v = sigma / tau
    with np.errstate(over="ignore", invalid="ignore"):
        out = ndtr(t / sigma) - np.exp(-t / tau + 0.5 * v * v) * ndtr(t / sigma - v)
    return np.clip(np.nan_to_num(out, nan=0.0), 0.0, 1.0)


def full_window(scn: Scenario) -> tuple[float, float]:
    """The ungated acquisition window: one repetition period starting just before the pulse."""
    start = -max(5.0 * scn.sigma, 0.5)
    return start, start + scn.period


def gate_fractions(scn: Scenario, g0, g1):
    """Fractions of signal and background photons whose time tag falls in ``[g0, g1]``.

    Returns ``(f_signal, f_background)``; both broadcast over array-valued gates.
    """
    g0 = np.asarray(g0, dtype=float)
    g1 = np.asarray(g1, dtype=float)
    sig = max(scn.sigma, 1e-6)
    f_s = exgauss_cdf(g1, scn.tau_s, sig) - exgauss_cdf(g0, scn.tau_s, sig)
    f_p = ndtr(g1 / sig) - ndtr(g0 / sig)
    f_a = exgauss_cdf(g1, scn.tau_a, sig) - exgauss_cdf(g0, scn.tau_a, sig)
    f_f = (g1 - g0) / scn.period
    f_b = scn.w_prompt * f_p + scn.w_auto * f_a + scn.w_flat * f_f
    return np.clip(f_s, 0, 1), np.clip(f_b, 0, 1)
