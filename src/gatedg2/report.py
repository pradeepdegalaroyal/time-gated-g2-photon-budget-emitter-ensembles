"""Aggregate raw per-seed CSVs into the mean +- std tables quoted in the README."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

NAMES = {
    "single_ungated": "Single-channel pair statistic, ungated",
    "hbt_ungated": "Two-detector HBT, ungated",
    "hbt_delay": "Two-detector HBT, delay-only gate",
    "hbt_window": "Two-detector HBT, optimised gate",
    "single_window": "Single-channel pair statistic, optimised gate",
}


def _ms(x: pd.Series, fmt: str = "{:.2e}") -> str:
    v = x.replace(np.inf, np.nan)
    if v.isna().all():
        return "not certifiable"
    return (fmt + " ± " + fmt).format(v.mean(), v.std(ddof=1) if len(v) > 1 else 0.0)


def build(res: Path) -> str:
    out = []
    ab = pd.read_csv(res / "ablation.csv")
    out.append("## Ablation (N = 3, rho = 2): pulses for 80 % power, mean ± std over seeds\n")
    out.append("| Method | Gate (ns) | Signal kept | Background kept | Expected g2 | Pulses (Monte Carlo) | Pulses (analytic) |")
    out.append("|---|---|---|---|---|---|---|")
    for m, d in ab.groupby("method", sort=False):
        r = d.iloc[0]
        out.append(f"| {NAMES[m]} | [{r.gate_start_ns:.2f}, {r.gate_end_ns:.2f}] | {r.f_signal:.3f} | {r.f_background:.3f} | "
                   f"{r.g2_expected:.4f} | {_ms(d.m80_mc)} | {r.m80_pred:.2e} |")
    sc = pd.read_csv(res / "scaling.csv")
    for mode in ("fixed", "proportional"):
        out.append(f"\n## Scaling with N, {mode} background: pulses for 80 % power\n")
        d = sc[sc.background == mode]
        ms = list(NAMES)
        ms = [m for m in ms if m in d.method.unique()]
        out.append("| N | " + " | ".join(NAMES[m] for m in ms) + " |")
        out.append("|---|" + "---|" * len(ms))
        for n, dn in d.groupby("n_emit"):
            out.append(f"| {n} | " + " | ".join(_ms(dn[dn.method == m].m80_mc) for m in ms) + " |")
    gm = pd.read_csv(res / "gain_map.csv")
    out.append("\n## Gating gain (ungated / gated pulses), mean ± std over seeds\n")
    sig = sorted(gm.sigma_ns.unique())
    out.append("| rho \\ sigma (ns) | " + " | ".join(f"{s:g}" for s in sig) + " |")
    out.append("|---|" + "---|" * len(sig))
    for rho, d in gm.groupby("rho"):
        out.append(f"| {rho:g} | " + " | ".join(
            f"{d[d.sigma_ns == s].gain.mean():.2f} ± {d[d.sigma_ns == s].gain.std(ddof=1):.2f}" for s in sig) + " |")
    xt = pd.read_csv(res / "crosstalk.csv")
    out.append("\n## Crosstalk sweep: pulses for 80 % power\n")
    ms = ["single_ungated", "hbt_ungated", "hbt_window"]
    out.append("| chi | expected g2 (HBT ungated) | " + " | ".join(NAMES[m] for m in ms) + " |")
    out.append("|---|---|" + "---|" * len(ms))
    for chi, d in xt.groupby("chi"):
        g = d[d.method == "hbt_ungated"].g2_expected.iloc[0]
        out.append(f"| {chi:g} | {g:.4f} | " + " | ".join(_ms(d[d.method == m].m80_mc) for m in ms) + " |")
    thr = json.loads((res / "crosstalk_threshold.json").read_text())
    out.append("\nCrosstalk threshold chi* (expected g2 reaches 1): " + ", ".join(f"{NAMES[k]} {v:.2e}" for k, v in thr.items()))
    lf = pd.read_csv(res / "lifetime_mismatch.csv")
    out.append("\n## Background-lifetime mismatch: gating gain, mean ± std over seeds\n")
    out.append("| Case | tau_a / tau_s | Gate re-optimised | Gate fixed at 0.5 |")
    out.append("|---|---|---|---|")
    for (case, r), d in lf.groupby(["case", "tau_ratio"]):
        fx = "n/a" if d.gain_fixed.isna().all() else f"{d.gain_fixed.mean():.2f} ± {d.gain_fixed.std(ddof=1):.2f}"
        out.append(f"| {case} | {r:g} | {d.gain_oracle.mean():.2f} ± {d.gain_oracle.std(ddof=1):.2f} | {fx} |")
    dq = pd.read_csv(res / "detection_probability.csv")
    out.append("\n## Per-emitter detection probability q: pulses for 80 % power\n")
    ms = ["hbt_ungated", "hbt_window", "single_window"]
    out.append("| q | " + " | ".join(NAMES[m] for m in ms) + " |")
    out.append("|---|" + "---|" * len(ms))
    for q, d in dq.groupby("q"):
        out.append(f"| {q:g} | " + " | ".join(_ms(d[d.method == m].m80_mc) for m in ms) + " |")
    s, c = np.polyfit(np.log(dq[dq.method == "hbt_window"].groupby("q").m80_mc.mean().index.values.astype(float)),
                      np.log(dq[dq.method == "hbt_window"].groupby("q").m80_mc.mean().values), 1)
    out.append(f"\nLog-log slope of pulses vs q (HBT, optimised gate): {s:.2f}")
    nl = pd.read_csv(res / "null_calibration.csv")
    out.append("\n## Type-I error under a Poisson null (nominal 0.05), mean ± std over seeds\n")
    out.append("| Method | expected accidental pairs | type-I error |")
    out.append("|---|---|---|")
    for (m, e0), d in nl.groupby(["method", "e0_target"], sort=False):
        out.append(f"| {NAMES[m]} | {e0} | {d.type1.mean():.3f} ± {d.type1.std(ddof=1):.3f} |")
    va = pd.read_csv(res / "timetag_validation.csv")
    out.append("\n## Photon-level time-tag simulation vs analytic model (q = 0.02)\n")
    out.append("| Case | g2 time-tag (mean ± std) | g2 analytic | signal kept (time-tag / analytic) | background kept (time-tag / analytic) |")
    out.append("|---|---|---|---|---|")
    for c_, d in va.groupby("case", sort=False):
        out.append(f"| {c_} | {d.g2_timetag.mean():.4f} ± {d.g2_timetag.std(ddof=1):.4f} | {d.g2_analytic.iloc[0]:.4f} | "
                   f"{d.f_signal_timetag.mean():.4f} / {d.f_signal_analytic.iloc[0]:.4f} | "
                   f"{d.f_background_timetag.mean():.4f} / {d.f_background_analytic.iloc[0]:.4f} |")
    # agreement of the analytic budget with Monte Carlo over all cells
    frames = [sc[["m80_pred", "m80_mc"]], ab[["m80_pred", "m80_mc"]],
              gm.rename(columns={"m80_pred_gated": "m80_pred", "m80_gated": "m80_mc"})[["m80_pred", "m80_mc"]],
              xt[["m80_pred", "m80_mc"]]]
    allf = pd.concat(frames)
    allf = allf[np.isfinite(allf.m80_pred) & np.isfinite(allf.m80_mc)]
    ratio = allf.m80_mc / allf.m80_pred
    out.append(f"\nMonte Carlo / analytic budget over {len(allf)} finite cells: median {ratio.median():.3f}, "
               f"5th-95th percentile {ratio.quantile(0.05):.3f}-{ratio.quantile(0.95):.3f}")
    return "\n".join(out) + "\n"


def write(res: Path) -> None:
    (res / "tables.md").write_text(build(res), encoding="utf-8")
