"""Fast unit tests for the gated second-order correlation study."""
import numpy as np

from gatedg2 import (Scenario, exgauss_cdf, full_window, g2_expected, gate_fractions, mc_m80,
                     optimise_gate, predicted_pulses, state_pmf)
from gatedg2.certify import mc_z
from gatedg2.timetag import simulate_g2


def test_exgauss_cdf_limits_and_monotone():
    t = np.linspace(-5, 60, 400)
    c = exgauss_cdf(t, 3.0, 0.3)
    assert c[0] < 1e-6 and c[-1] > 1 - 1e-6
    assert np.all(np.diff(c) >= -1e-12)
    # no jitter: plain exponential
    assert abs(float(exgauss_cdf(3.0, 3.0, 1e-9)) - (1 - np.exp(-1))) < 1e-6


def test_state_pmf_normalised_and_closed_form_g2():
    scn = Scenario(n_emit=4, q=1e-3, rho=1.5)
    p = state_pmf(scn, np.array([1.0]), np.array([1.0]))
    assert abs(p.sum() - 1.0) < 1e-12
    g, _, _ = g2_expected(p, "hbt")
    expected = 1 - 1 / (4 * (1 + 1.5) ** 2)
    assert abs(g[0] - expected) < 1e-4
    g1, _, _ = g2_expected(p, "single")
    assert abs(g1[0] - expected) < 1e-4


def test_pure_poisson_has_unit_g2_and_calibrated_null():
    null = Scenario(n_emit=0, beta_override=0.02)
    p = state_pmf(null, np.array([1.0]), np.array([1.0]))
    assert abs(g2_expected(p, "hbt")[0][0] - 1.0) < 1e-4
    rng = np.random.default_rng(1)
    z, _ = mc_z(p[0], "hbt", 2e6, 1500, rng)
    assert 0.02 < np.mean(z < -1.645) < 0.09
    assert abs(np.std(z) - 1.0) < 0.1


def test_optimised_gate_never_worse_and_helps_with_prompt_background():
    scn = Scenario(rho=4.0, sigma=0.1)
    g0, g1, m_gate = optimise_gate(scn)
    f_s, f_b = gate_fractions(scn, *full_window(scn))
    m_ungated = predicted_pulses(state_pmf(scn, f_s, f_b), "hbt")[0]
    assert m_gate <= m_ungated + 1
    assert m_ungated / m_gate > 1.5
    assert g1 > g0


def test_identical_background_profile_gives_no_gain():
    scn = Scenario(tau_a=3.0, w_prompt=0.0, w_auto=1.0, w_flat=0.0)
    _, _, m_gate = optimise_gate(scn)
    f_s, f_b = gate_fractions(scn, *full_window(scn))
    m_ungated = predicted_pulses(state_pmf(scn, f_s, f_b), "hbt")[0]
    assert m_ungated / m_gate < 1.1


def test_crosstalk_makes_certification_impossible():
    scn = Scenario(chi=2e-3)
    f_s, f_b = gate_fractions(scn, *full_window(scn))
    p = state_pmf(scn, f_s, f_b)
    assert g2_expected(p, "hbt")[0][0] > 1.0
    assert np.isinf(predicted_pulses(p, "hbt")[0])


def test_monte_carlo_budget_matches_analytic_prediction():
    scn = Scenario()
    f_s, f_b = gate_fractions(scn, *full_window(scn))
    p = state_pmf(scn, f_s, f_b)
    m_pred = float(predicted_pulses(p, "hbt")[0])
    m_mc = mc_m80(p[0], "hbt", m_pred, 400, np.random.default_rng(3))
    assert 0.75 < m_mc / m_pred < 1.3


def test_timetag_simulation_matches_state_model():
    scn = Scenario(q=0.02)
    gate = (0.25, 12.5)
    f_s, f_b = gate_fractions(scn, *gate)
    g_an = g2_expected(state_pmf(scn, f_s, f_b), "hbt")[0][0]
    out = simulate_g2(scn, gate, 400_000, np.random.default_rng(5))
    assert abs(out["f_signal"] - float(f_s)) < 0.01
    assert abs(out["f_background"] - float(f_b)) < 0.01
    assert abs(out["g2"] - g_an) < 0.04
