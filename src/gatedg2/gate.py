"""Gate selection by minimising the analytic pulse budget."""
from __future__ import annotations

import numpy as np

from .config import Scenario
from .statemodel import predicted_pulses, state_pmf
from .timing import full_window, gate_fractions


def optimise_gate(scn: Scenario, kind: str = "hbt", mode: str = "window"):
    """Return ``(g0, g1, predicted_pulses)`` of the gate with the smallest predicted budget.

    ``mode='window'`` searches start and end; ``mode='delay'`` searches the start only
    (end fixed at the end of the acquisition window). The full ungated window is always a
    candidate, so a gate is never worse than no gate in the analytic budget. The search ignores crosstalk,
    i.e. the gate is designed from the calibrated timing profiles only.
    """
    scn0 = scn.with_(chi=0.0)
    w0, w1 = full_window(scn)
    g0s = np.arange(-1.0, 10.01, 0.25)
    if mode == "delay":
        g1s = np.array([w1])
    elif mode == "window":
        g1s = np.unique(np.concatenate([np.arange(1.0, w1, 0.5), [w1]]))
    else:
        raise ValueError(mode)
    a, b = np.meshgrid(g0s, g1s, indexing="ij")
    ok = b - a >= 0.5
    a, b = np.append(a[ok], w0), np.append(b[ok], w1)  # the ungated window is always a candidate
    f_s, f_b = gate_fractions(scn0, a, b)
    m = predicted_pulses(state_pmf(scn0, f_s, f_b), kind)
    i = int(np.argmin(m))
    return float(a[i]), float(b[i]), float(m[i])
