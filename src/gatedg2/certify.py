"""Monte Carlo certification test and pulse-budget (power) search.

The test certifies non-classical (sub-Poissonian pair) statistics when the
observed accidental-corrected pair excess is significantly below zero:
``z0 = (g2_hat - 1) / se0 < -1.645`` with the null standard error ``se0``
evaluated for independent Poisson counts.
"""
from __future__ import annotations

import numpy as np

from .statemodel import MIN_NULL_PAIRS, Z_ALPHA, _features

PRACTICAL_LIMIT = 1e13  # pulses; about three days of acquisition at 40 MHz


def z_statistics(counts: np.ndarray, kind: str, m_pulses: float, s: int):
    """Null-calibrated z statistic and expected accidental pairs from state counts.

    ``counts`` has shape ``(reps, s*s)``.
    """
    f = _features(kind, s).reshape(-1, s * s)
    mean = counts @ f.T / m_pulses
    with np.errstate(divide="ignore", invalid="ignore"):
        if kind == "hbt":
            e0 = m_pulses * mean[:, 1] * mean[:, 2]
            g = mean[:, 0] / (mean[:, 1] * mean[:, 2])
        else:
            e0 = m_pulses * mean[:, 1] ** 2 / 2.0
            g = mean[:, 0] / mean[:, 1] ** 2
        z = (g - 1.0) * np.sqrt(e0)
    return z, e0


def mc_z(p1: np.ndarray, kind: str, m_pulses: float, reps: int, rng: np.random.Generator):
    """Draw ``reps`` experiments of ``m_pulses`` pulses and return ``(z, e0)``."""
    s = p1.shape[-1]
    pv = p1.ravel() / p1.sum()
    m = int(m_pulses)
    counts = rng.multinomial(m, pv, size=reps).astype(float)
    return z_statistics(counts, kind, float(m), s)


def mc_power(p1: np.ndarray, kind: str, m_pulses: float, reps: int, rng: np.random.Generator) -> float:
    """Fraction of simulated experiments that certify non-classicality."""
    z, e0 = mc_z(p1, kind, m_pulses, reps, rng)
    hit = (z < -Z_ALPHA) & (e0 >= MIN_NULL_PAIRS)
    return float(np.mean(hit))


def mc_m80(p1: np.ndarray, kind: str, m_pred: float, reps: int, rng: np.random.Generator,
           target: float = 0.8) -> float:
    """Pulses for ``target`` power by Monte Carlo, bracketed around the analytic prediction.

    Returns ``inf`` when the analytic budget exceeds ``PRACTICAL_LIMIT`` pulses (including the
    case where the expected estimator is not below one).
    """
    if not np.isfinite(m_pred) or m_pred > PRACTICAL_LIMIT:
        return float("inf")
    mult = np.array([0.4, 0.6, 0.8, 1.0, 1.25, 1.6, 2.2])
    ms = m_pred * mult
    pw = np.array([mc_power(p1, kind, m, reps, rng) for m in ms])
    for _ in range(6):
        if pw[-1] >= target:
            break
        ms = np.concatenate([ms, [ms[-1] * 2.0]])
        pw = np.append(pw, mc_power(p1, kind, ms[-1], reps, rng))
    for _ in range(6):
        if pw[0] <= target:
            break
        ms = np.concatenate([[ms[0] * 0.5], ms])
        pw = np.concatenate([[mc_power(p1, kind, ms[0], reps, rng)], pw])
    pw = np.maximum.accumulate(pw)
    if pw[-1] < target:
        return float("inf")
    j = int(np.argmax(pw >= target))
    if j == 0:
        return float(ms[0])
    x0, x1 = np.log(ms[j - 1]), np.log(ms[j])
    y0, y1 = pw[j - 1], pw[j]
    t = 0.0 if y1 == y0 else (target - y0) / (y1 - y0)
    return float(np.exp(x0 + t * (x1 - x0)))
