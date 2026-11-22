## Ablation (N = 3, rho = 2): pulses for 80 % power, mean ± std over seeds

| Method | Gate (ns) | Signal kept | Background kept | Expected g2 | Pulses (Monte Carlo) | Pulses (analytic) |
|---|---|---|---|---|---|---|
| Single-channel pair statistic, ungated | [-1.00, 24.00] | 1.000 | 1.000 | 0.9630 | 2.80e+07 ± 1.70e+06 | 2.75e+07 |
| Two-detector HBT, ungated | [-1.00, 24.00] | 1.000 | 1.000 | 0.9630 | 5.58e+07 ± 2.79e+06 | 5.50e+07 |
| Two-detector HBT, delay-only gate | [0.25, 24.00] | 0.918 | 0.571 | 0.9338 | 3.48e+07 ± 2.41e+06 | 3.61e+07 |
| Two-detector HBT, optimised gate | [0.25, 12.50] | 0.903 | 0.479 | 0.9215 | 3.09e+07 ± 1.66e+06 | 3.13e+07 |
| Single-channel pair statistic, optimised gate | [0.25, 12.50] | 0.903 | 0.479 | 0.9215 | 1.62e+07 ± 8.39e+05 | 1.57e+07 |

## Scaling with N, fixed background: pulses for 80 % power

| N | Single-channel pair statistic, ungated | Two-detector HBT, ungated | Two-detector HBT, optimised gate | Single-channel pair statistic, optimised gate |
|---|---|---|---|---|
| 1 | 1.52e+08 ± 6.70e+06 | 2.95e+08 ± 1.32e+07 | 1.27e+08 ± 4.53e+06 | 6.30e+07 ± 4.24e+06 |
| 2 | 4.73e+07 ± 1.79e+06 | 9.59e+07 ± 3.18e+06 | 4.81e+07 ± 2.26e+06 | 2.52e+07 ± 1.35e+06 |
| 3 | 2.68e+07 ± 1.24e+06 | 5.37e+07 ± 2.15e+06 | 3.10e+07 ± 1.03e+06 | 1.67e+07 ± 9.80e+05 |
| 4 | 1.86e+07 ± 1.07e+06 | 3.85e+07 ± 2.95e+06 | 2.45e+07 ± 1.12e+06 | 1.20e+07 ± 6.00e+05 |
| 6 | 1.24e+07 ± 6.79e+05 | 2.43e+07 ± 1.80e+06 | 1.76e+07 ± 8.40e+05 | 8.71e+06 ± 5.03e+05 |
| 8 | 9.33e+06 ± 4.16e+05 | 1.85e+07 ± 8.45e+05 | 1.48e+07 ± 7.97e+05 | 7.27e+06 ± 3.85e+05 |

## Scaling with N, proportional background: pulses for 80 % power

| N | Single-channel pair statistic, ungated | Two-detector HBT, ungated | Two-detector HBT, optimised gate | Single-channel pair statistic, optimised gate |
|---|---|---|---|---|
| 1 | 2.61e+07 ± 6.74e+05 | 5.24e+07 ± 3.45e+06 | 3.05e+07 ± 1.82e+06 | 1.48e+07 ± 5.38e+05 |
| 2 | 2.72e+07 ± 7.44e+05 | 5.70e+07 ± 4.00e+06 | 2.99e+07 ± 1.28e+06 | 1.54e+07 ± 4.03e+05 |
| 3 | 2.68e+07 ± 1.24e+06 | 5.37e+07 ± 2.15e+06 | 3.10e+07 ± 1.03e+06 | 1.67e+07 ± 9.80e+05 |
| 4 | 2.83e+07 ± 2.18e+06 | 5.77e+07 ± 1.41e+06 | 3.13e+07 ± 1.24e+06 | 1.60e+07 ± 5.78e+05 |
| 6 | 2.88e+07 ± 8.12e+05 | 5.38e+07 ± 2.72e+06 | 3.19e+07 ± 1.52e+06 | 1.60e+07 ± 7.49e+05 |
| 8 | 2.88e+07 ± 1.95e+06 | 5.75e+07 ± 3.74e+06 | 3.16e+07 ± 1.26e+06 | 1.58e+07 ± 1.06e+06 |

## Gating gain (ungated / gated pulses), mean ± std over seeds

| rho \ sigma (ns) | 0.05 | 0.1 | 0.2 | 0.5 | 1 | 2 |
|---|---|---|---|---|---|---|
| 0.5 | 1.20 ± 0.07 | 1.20 ± 0.07 | 1.18 ± 0.08 | 1.10 ± 0.18 | 1.05 ± 0.03 | 0.99 ± 0.08 |
| 1 | 1.56 ± 0.09 | 1.55 ± 0.09 | 1.38 ± 0.07 | 1.24 ± 0.07 | 1.10 ± 0.07 | 0.99 ± 0.06 |
| 2 | 1.92 ± 0.15 | 1.89 ± 0.06 | 1.73 ± 0.12 | 1.40 ± 0.05 | 1.18 ± 0.09 | 1.08 ± 0.08 |
| 4 | 2.24 ± 0.11 | 2.29 ± 0.10 | 2.14 ± 0.06 | 1.68 ± 0.08 | 1.29 ± 0.06 | 1.09 ± 0.07 |
| 8 | 3.08 ± 0.09 | 3.00 ± 0.19 | 2.63 ± 0.21 | 2.05 ± 0.05 | 1.55 ± 0.09 | 1.25 ± 0.09 |

## Crosstalk sweep: pulses for 80 % power

| chi | expected g2 (HBT ungated) | Single-channel pair statistic, ungated | Two-detector HBT, ungated | Two-detector HBT, optimised gate |
|---|---|---|---|---|
| 0 | 0.9630 | 2.76e+07 ± 1.66e+06 | 5.39e+07 ± 2.71e+06 | 3.10e+07 ± 1.29e+06 |
| 1e-05 | 0.9652 | 2.88e+07 ± 1.33e+06 | 6.35e+07 ± 5.09e+06 | 3.49e+07 ± 1.65e+06 |
| 3e-05 | 0.9696 | 3.26e+07 ± 1.48e+06 | 8.07e+07 ± 3.13e+06 | 4.23e+07 ± 1.16e+06 |
| 0.0001 | 0.9852 | 5.53e+07 ± 3.92e+06 | 3.58e+08 ± 1.12e+07 | 1.09e+08 ± 4.52e+06 |
| 0.0003 | 1.0296 | 2.82e+09 ± 1.61e+08 | not certifiable | not certifiable |
| 0.001 | 1.1848 | not certifiable | not certifiable | not certifiable |

Crosstalk threshold chi* (expected g2 reaches 1): Single-channel pair statistic, ungated 3.33e-04, Two-detector HBT, ungated 1.67e-04, Two-detector HBT, optimised gate 2.19e-04

## Background-lifetime mismatch: gating gain, mean ± std over seeds

| Case | tau_a / tau_s | Gate re-optimised | Gate fixed at 0.5 |
|---|---|---|---|
| control_identical_profile | 1 | 0.97 ± 0.05 | n/a |
| mixed | 0.1 | 3.19 ± 0.18 | 2.40 ± 0.17 |
| mixed | 0.25 | 2.22 ± 0.23 | 1.92 ± 0.11 |
| mixed | 0.5 | 1.71 ± 0.13 | 1.83 ± 0.14 |
| mixed | 0.75 | 1.64 ± 0.13 | 1.68 ± 0.14 |
| mixed | 1 | 1.63 ± 0.12 | 1.64 ± 0.12 |
| mixed | 1.5 | 1.67 ± 0.08 | 1.69 ± 0.12 |
| mixed | 2 | 1.80 ± 0.08 | 1.71 ± 0.15 |

## Per-emitter detection probability q: pulses for 80 % power

| q | Two-detector HBT, ungated | Two-detector HBT, optimised gate | Single-channel pair statistic, optimised gate |
|---|---|---|---|
| 0.001 | 2.28e+08 ± 1.05e+07 | 1.28e+08 ± 4.89e+06 | 6.10e+07 ± 3.13e+06 |
| 0.002 | 5.39e+07 ± 1.01e+06 | 3.16e+07 ± 1.11e+06 | 1.55e+07 ± 7.98e+05 |
| 0.005 | 8.74e+06 ± 4.71e+05 | 4.82e+06 ± 1.65e+05 | 2.54e+06 ± 1.53e+05 |
| 0.01 | 2.14e+06 ± 1.20e+05 | 1.30e+06 ± 7.95e+04 | 6.31e+05 ± 4.45e+04 |
| 0.02 | 5.37e+05 ± 3.09e+04 | 3.18e+05 ± 7.20e+03 | 1.58e+05 ± 1.06e+04 |

Log-log slope of pulses vs q (HBT, optimised gate): -2.00

## Type-I error under a Poisson null (nominal 0.05), mean ± std over seeds

| Method | expected accidental pairs | type-I error |
|---|---|---|
| Single-channel pair statistic, ungated | 50 | 0.046 ± 0.006 |
| Single-channel pair statistic, ungated | 500 | 0.050 ± 0.004 |
| Single-channel pair statistic, ungated | 5000 | 0.047 ± 0.007 |
| Two-detector HBT, ungated | 50 | 0.044 ± 0.006 |
| Two-detector HBT, ungated | 500 | 0.047 ± 0.006 |
| Two-detector HBT, ungated | 5000 | 0.050 ± 0.006 |
| Two-detector HBT, optimised gate | 50 | 0.046 ± 0.006 |
| Two-detector HBT, optimised gate | 500 | 0.051 ± 0.007 |
| Two-detector HBT, optimised gate | 5000 | 0.051 ± 0.005 |

## Photon-level time-tag simulation vs analytic model (q = 0.02)

| Case | g2 time-tag (mean ± std) | g2 analytic | signal kept (time-tag / analytic) | background kept (time-tag / analytic) |
|---|---|---|---|---|
| ungated | 0.9611 ± 0.0110 | 0.9630 | 0.9997 / 0.9997 | 1.0000 / 1.0000 |
| delay_gate | 0.9318 ± 0.0056 | 0.9338 | 0.9187 / 0.9183 | 0.5704 / 0.5710 |
| window_gate | 0.9220 ± 0.0135 | 0.9215 | 0.9036 / 0.9031 | 0.4784 / 0.4789 |
| window_gate_chi1e-2 | 1.2728 ± 0.0182 | 1.2727 | 0.9036 / 0.9031 | 0.4784 / 0.4789 |

Monte Carlo / analytic budget over 480 finite cells: median 1.000, 5th-95th percentile 0.926-1.093
