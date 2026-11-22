# Method

## Model

The target quantity is the second-order correlation function at zero delay, g(2)(0): it equals 1 for classical (Poissonian or coherent) light and is below 1 for non-classical sub-Poissonian light; N ideal single-photon emitters give 1 − 1/N.

A pulsed laser excites N independent fluorescent emitters every repetition period T = 25 ns (40 MHz). Per pulse each emitter yields at most one detected photon with probability q (excitation probability times collection and detection efficiency; nominal q = 0.002). A 50/50 beam splitter sends each photon to detector A or B (the Hanbury Brown–Twiss (HBT) layout); pixelated detectors can register more than one photon per pulse.

* **Signal arrival time:** exponential decay with lifetime tau_s = 3.0 ns convolved with a Gaussian instrument response function (IRF) of width sigma (nominal 0.2 ns).
* **Background photons:** Poisson with mean rho · N · q per pulse (nominal rho = 2) before gating, split into three components with weights 0.4 / 0.4 / 0.2: *prompt* (scatter, leakage; IRF-shaped), *autofluorescence* (decay lifetime tau_a = 1.5 ns), and *flat* (dark counts, stray light; uniform in time).
* **Crosstalk:** every count on one detector spawns a spurious count on the other with probability chi (nominal 0).
* **Gate:** only photons with time tags in [g0, g1] are used. The ungated acquisition is the whole period.

All timing values and rates are assumptions chosen for a plausible regime; they are swept, not claimed as measurements.

## Exact state model

For a given gate the joint distribution of the photon numbers (n_A, n_B) per pulse is computed exactly (signal binomial convolved with background Poisson, binomial beam-splitter routing, optional crosstalk; photon number truncated at six). This gives the expected second-order correlation estimate, its delta-method variance, and the analytic pulse budget. A photon-level time-tag simulation validates the state model.

## Estimators (one classical baseline, one standard quantum-optics baseline, one proposal)

| Name | Statistic | Role |
|---|---|---|
| Single-channel pair statistic | g(2) from the total count per pulse, sum of K(K−1) over pulses divided by M times the squared mean count (M pulses); needs photon-number resolution | classical-statistics baseline (Mandel-type excess of pair events over Poisson) |
| Two-detector HBT, ungated | cross-correlation of detector A and B counts in the same pulse divided by the accidental level from the singles rates | standard quantum-optics baseline |
| Two-detector HBT, optimised gate | same statistic after an arrival-time gate designed from the calibrated profiles by minimising the analytic pulse budget | proposed |

**Certification rule.** Declare the light non-classical when z = (g2_hat − 1) / se0 < −1.645, where se0 is the standard error under independent Poisson counts (for the HBT estimator, z = (C − E0)/sqrt(E0) with C the coincidences and E0 = S_A S_B / M the accidental level). At least 20 expected accidental pairs are required for a decision.

**Pulse budget.** The number of pulses giving 80 % power at the 5 % level, found by Monte Carlo (300 repetitions per setting, interpolated on a pulse grid) and compared with the analytic prediction: sqrt(M) = (1.645 sqrt(s0) + 0.842 sqrt(v1)) / (1 − g), with s0 and v1 the per-pulse null and true variances. Budgets above 1e13 pulses are reported as not certifiable.

## Metrics

Pulses for 80 % power (primary); gating gain = pulses ungated / pulses gated; type-I error under a Poisson null; crosstalk threshold chi* where the expected estimator reaches one.

## Ablation

Estimator (single-channel vs two-detector) × gate (none, delay-only, delay plus end) at nominal parameters.

## Noise and robustness sweeps

* Background-to-signal ratio rho ∈ {0.5, 1, 2, 4, 8} × detector jitter sigma ∈ {0.05, 0.1, 0.2, 0.5, 1, 2} ns (heat map of gating gain).
* Crosstalk probability chi from 0 to 1e-3.
* Background lifetime tau_a / tau_s from 0.1 to 2, with the gate either re-optimised or fixed at the tau_a / tau_s = 0.5 design; plus a negative control with a background identical to the emitter profile.
* Emitter number N from 1 to 8 under a fixed or a signal-proportional background; per-emitter detection probability q from 0.001 to 0.02.

## Seeds and compute

Five seeds (independent Monte Carlo streams) for every study; the whole run takes under one minute on a laptop central processing unit (CPU); no graphics processor is used.

## Limitations of the model

Independent emitters, no photobleaching or blinking dynamics, no afterpulsing or dead time, gate optimised with known profiles, crosstalk modelled as instantaneous and per count. See the README for discussion.
