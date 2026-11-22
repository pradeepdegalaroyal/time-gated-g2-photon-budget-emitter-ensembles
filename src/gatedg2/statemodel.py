"""Exact per-pulse joint photon-count distribution on the two Hanbury Brown-Twiss (HBT) detectors.

For one gate, per pulse: signal photons ~ Binomial(n_emit, q f_s), background
photons ~ Poisson(beta0 f_b); a 50/50 beam splitter routes each photon to
detector A or B; optional crosstalk makes every count on one detector spawn a
spurious count on the other with probability ``chi``.
"""
from __future__ import annotations

from math import comb

import numpy as np
from scipy.stats import binom, poisson

from .config import Scenario

KMAX = 6  # truncation of the photon number per pulse
Z_ALPHA = 1.6448536269514722  # one-sided 5 % level
Z_POWER = 0.8416212335729143  # 80 % power
MIN_NULL_PAIRS = 20.0  # minimum expected accidental pairs required to run the test


def state_pmf(scn: Scenario, f_s, f_b) -> np.ndarray:
    """Joint pmf over ``(n_A, n_B)`` for a batch of gates.

    ``f_s`` and ``f_b`` are 1-D arrays of signal/background gate fractions.
    Returns an array of shape ``(G, S, S)`` that sums to one over the last two axes.
    """
    f_s = np.atleast_1d(np.asarray(f_s, dtype=float))
    f_b = np.atleast_1d(np.asarray(f_b, dtype=float))
    g = f_s.size
    k = np.arange(KMAX + 1)
    qg = np.clip(scn.q * f_s, 0.0, 1.0)
    beta = scn.beta0 * f_b
    sig = binom.pmf(k[None, :], scn.n_emit, qg[:, None])
    bg = poisson.pmf(k[None, :], beta[:, None])
    pk = np.zeros((g, KMAX + 1))
    for i in range(KMAX + 1):
        pk[:, i:] += sig[:, i : i + 1] * bg[:, : KMAX + 1 - i]
    pk[:, 0] += np.clip(1.0 - pk.sum(axis=1), 0.0, None)  # truncated tail into the vacuum state
    p = np.zeros((g, KMAX + 1, KMAX + 1))
    for kk in range(KMAX + 1):
        for a in range(kk + 1):
            p[:, a, kk - a] += pk[:, kk] * comb(kk, a) / 2.0**kk
    if scn.chi > 0:
        p = _crosstalk(p, scn.chi)
    return p


def _crosstalk(p: np.ndarray, chi: float) -> np.ndarray:
    g, s, _ = p.shape
    out = np.zeros((g, 2 * s - 1, 2 * s - 1))
    w = np.zeros((s, s))
    for a in range(s):
        w[a, : a + 1] = binom.pmf(np.arange(a + 1), a, chi)
    for a in range(s):
        for b in range(s):
            base = p[:, a, b]
            for i in range(a + 1):
                for j in range(b + 1):
                    out[:, a + j, b + i] += base * w[a, i] * w[b, j]
    return out


def _features(kind: str, s: int) -> np.ndarray:
    a = np.arange(s, dtype=float)[:, None] * np.ones((1, s))
    b = a.T
    if kind == "hbt":
        return np.stack([a * b, a, b])
    if kind == "single":
        kk = a + b
        return np.stack([kk * (kk - 1.0), kk])
    raise ValueError(f"unknown estimator kind {kind!r}")


def _g_and_grad(kind: str, m: np.ndarray):
    if kind == "hbt":
        g = m[:, 0] / (m[:, 1] * m[:, 2])
        grad = np.stack([1 / (m[:, 1] * m[:, 2]), -g / m[:, 1], -g / m[:, 2]], axis=1)
        s0 = 1.0 / (m[:, 1] * m[:, 2])
    else:
        g = m[:, 0] / m[:, 1] ** 2
        grad = np.stack([1 / m[:, 1] ** 2, -2 * g / m[:, 1]], axis=1)
        s0 = 2.0 / m[:, 1] ** 2
    return g, grad, s0


def g2_expected(p: np.ndarray, kind: str = "hbt"):
    """Expected value of the second-order correlation estimator, per gate.

    Also returns the per-pulse delta-method variance under the true state (``v1``) and
    the per-pulse variance under the classical null (``s0``).
    """
    s = p.shape[-1]
    f = _features(kind, s)
    m = np.einsum("gst,fst->gf", p, f)
    second = np.einsum("gst,fst,hst->gfh", p, f, f)
    cov = second - m[:, :, None] * m[:, None, :]
    g, grad, s0 = _g_and_grad(kind, m)
    v1 = np.einsum("gf,gfh,gh->g", grad, cov, grad)
    return g, np.maximum(v1, 0.0), s0


def predicted_pulses(p: np.ndarray, kind: str = "hbt") -> np.ndarray:
    """Analytic pulses needed for 80 % power at the 5 % one-sided level (``inf`` if unreachable)."""
    g, v1, s0 = g2_expected(p, kind)
    with np.errstate(divide="ignore", invalid="ignore"):
        m_stat = ((Z_ALPHA * np.sqrt(s0) + Z_POWER * np.sqrt(v1)) / (1.0 - g)) ** 2
        m_floor = MIN_NULL_PAIRS * s0
        out = np.where(g < 1.0, np.maximum(m_stat, m_floor), np.inf)
    return np.nan_to_num(out, nan=np.inf, posinf=np.inf)
