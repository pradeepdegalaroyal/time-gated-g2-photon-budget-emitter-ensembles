"""Greyscale figures (markers and line styles carry the distinctions)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

DPI = 200
LABELS = {
    "single_ungated": "Single-channel pair statistic, ungated",
    "hbt_ungated": "Two-detector HBT, ungated",
    "hbt_delay": "Two-detector HBT, delay-only gate",
    "hbt_window": "Two-detector HBT, optimised gate",
    "single_window": "Single-channel pair statistic, optimised gate",
}
STYLE = {
    "single_ungated": dict(color="0.55", ls=":", marker="s"),
    "hbt_ungated": dict(color="0.25", ls="--", marker="o"),
    "hbt_delay": dict(color="0.4", ls="-.", marker="^"),
    "hbt_window": dict(color="black", ls="-", marker="D"),
    "single_window": dict(color="0.4", ls=(0, (5, 1, 1, 1)), marker="v"),
}


def _save(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def _band(ax, x, df, col, label, key):
    g = df.groupby(x)[col].agg(["mean", "std"]).reset_index()
    st = STYLE[key]
    ax.plot(g[x], g["mean"], label=label, color=st["color"], ls=st["ls"], marker=st["marker"], ms=6, lw=1.6)
    ax.fill_between(g[x], g["mean"] - g["std"].fillna(0), g["mean"] + g["std"].fillna(0), color=st["color"], alpha=0.15, lw=0)


def fig_scaling(df: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), sharey=True)
    titles = {"fixed": "(a) Fixed background (cell autofluorescence does not scale with N)",
              "proportional": "(b) Background proportional to signal (rho = 2)"}
    for ax, mode in zip(axes, ["fixed", "proportional"]):
        d = df[df.background == mode]
        for m in ["single_ungated", "hbt_ungated", "hbt_window", "single_window"]:
            _band(ax, "n_emit", d[d.method == m], "m80_mc", LABELS[m], m)
        ax.set_xscale("log"); ax.set_yscale("log")
        ns = sorted(d.n_emit.unique())
        ax.set_xticks(ns); ax.set_xticklabels([str(n) for n in ns]); ax.minorticks_off()
        ax.set_xlabel("Number of emitters in the detection volume, N")
        ax.set_title(titles[mode], fontsize=9.5)
        ax.grid(True, which="both", color="0.9")
    axes[0].set_ylabel("Excitation pulses for 80 % power (5 % level)")
    axes[0].legend(fontsize=7, frameon=False, loc="lower left")
    _save(fig, path)


def fig_gain_map(df: pd.DataFrame, path: Path) -> None:
    rhos, sigmas = sorted(df.rho.unique()), sorted(df.sigma_ns.unique())
    gain = df.groupby(["rho", "sigma_ns"]).gain.mean().unstack().loc[rhos, sigmas]
    m80 = df.groupby(["rho", "sigma_ns"]).m80_gated.mean().unstack().loc[rhos, sigmas]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    for ax, data, title, fmt, cbl in [
        (axes[0], gain, "Pulse saving of gating (ungated / gated)", "{:.2f}", "Budget ratio"),
        (axes[1], np.log10(m80), "Gated pulse budget (log10 pulses)", "{:.2f}", "log10 pulses"),
    ]:
        im = ax.imshow(data.values, cmap="Greys", aspect="auto", origin="lower")
        ax.set_xticks(range(len(sigmas))); ax.set_xticklabels([f"{s:g}" for s in sigmas])
        ax.set_yticks(range(len(rhos))); ax.set_yticklabels([f"{r:g}" for r in rhos])
        lo, hi = np.nanmin(data.values), np.nanmax(data.values)
        for i in range(len(rhos)):
            for j in range(len(sigmas)):
                v = data.values[i, j]
                dark = (v - lo) / (hi - lo + 1e-12) > 0.55
                ax.text(j, i, fmt.format(v), ha="center", va="center", fontsize=8, color="white" if dark else "black")
        ax.set_xlabel("Detector timing jitter, sigma (ns)")
        ax.set_ylabel("Background-to-signal photon ratio, rho")
        ax.set_title(title, fontsize=10)
        fig.colorbar(im, ax=ax, label=cbl)
    _save(fig, path)


def fig_ablation(df: pd.DataFrame, path: Path) -> None:
    order = ["single_ungated", "hbt_ungated", "hbt_delay", "hbt_window", "single_window"]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    data = [df[df.method == m].m80_mc.values for m in order]
    bp = ax.boxplot(data, positions=range(len(order)), widths=0.5, showfliers=False, patch_artist=True)
    for patch in bp["boxes"]:
        patch.set(facecolor="0.9", edgecolor="black")
    for med in bp["medians"]:
        med.set(color="black", lw=2)
    rng = np.random.default_rng(0)
    for i, d in enumerate(data):
        ax.scatter(i + rng.uniform(-0.12, 0.12, len(d)), d, color="black", marker=STYLE[order[i]]["marker"], s=24, zorder=3)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(["Single-channel\nungated", "HBT\nungated", "HBT\ndelay gate", "HBT\nwindow gate", "Single-channel\nwindow gate"], fontsize=8)
    ax.set_yscale("log")
    ax.set_ylabel("Excitation pulses for 80 % power")
    ax.set_title("Ablation of estimator and gate (N = 3, rho = 2); dots are seeds")
    ax.grid(True, axis="y", which="both", color="0.9")
    _save(fig, path)


def fig_robustness(chi: pd.DataFrame, life: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
    ax = axes[0]
    chis = sorted(chi.chi.unique())
    xs = {c: i for i, c in enumerate(chis)}
    top = np.nanmax(chi.m80_mc.replace(np.inf, np.nan))
    for off, m in zip([-0.12, 0.0, 0.12], ["single_ungated", "hbt_ungated", "hbt_window"]):
        d = chi[chi.method == m].copy()
        d["x"] = d.chi.map(xs)
        fin = d.replace(np.inf, np.nan)
        _band(ax, "x", fin.dropna(subset=["m80_mc"]), "m80_mc", LABELS[m], m)
        bad = d[~np.isfinite(d.m80_mc)].x.unique()
        for x in bad:
            ax.scatter([x + off], [top * 3], marker="x", color=STYLE[m]["color"], s=60, zorder=4)
    ax.set_yscale("log")
    ax.set_xticks(range(len(chis))); ax.set_xticklabels(["0" if c == 0 else f"{c:g}" for c in chis])
    ax.set_xlabel("Inter-detector crosstalk probability per count, chi")
    ax.set_ylabel("Excitation pulses for 80 % power")
    ax.set_title("(a) Crosstalk; crosses mark non-certifiable settings", fontsize=10)
    ax.grid(True, which="both", color="0.9"); ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax = axes[1]
    mixed = life[life.case == "mixed"]
    for col, lab, key in [("gain_oracle", "Gate re-optimised for each background lifetime", "hbt_window"),
                          ("gain_fixed", "Gate fixed at tau_a / tau_s = 0.5", "hbt_delay")]:
        _band(ax, "tau_ratio", mixed, col, lab, key)
    ax.axhline(1.0, color="0.5", lw=1, ls=":")
    ax.set_xlabel("Autofluorescence lifetime / emitter lifetime, tau_a / tau_s")
    ax.set_ylabel("Pulse saving of gating (ungated / gated)")
    ax.set_title("(b) Background-lifetime mismatch", fontsize=10)
    ax.grid(True, color="0.9"); ax.legend(fontsize=7.5, frameon=False)
    _save(fig, path)


def fig_null(zs: pd.DataFrame, path: Path) -> None:
    order = ["single_ungated", "hbt_ungated", "hbt_window"]
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    data = [zs[zs.method == m].z.values for m in order]
    parts = ax.violinplot(data, positions=range(3), showextrema=False, widths=0.8)
    for b in parts["bodies"]:
        b.set(facecolor="0.8", edgecolor="black", alpha=1)
    for i, m in enumerate(order):
        means = zs[zs.method == m].groupby("seed").z.mean().values
        ax.scatter(np.full(len(means), i) + np.linspace(-0.1, 0.1, len(means)), means, color="black", marker=STYLE[m]["marker"], s=30, zorder=3)
    ax.axhline(-1.6449, color="black", ls="--", lw=1)
    ax.text(2.45, -1.6449 + 0.1, "decision threshold", ha="right", fontsize=7)
    ax.set_xticks(range(3)); ax.set_xticklabels(["Single-channel\nungated", "HBT\nungated", "HBT\noptimised gate"], fontsize=8)
    ax.set_ylabel("Test statistic z under a Poisson (classical) null")
    ax.set_title("Null calibration: z is standard normal; dots are per-seed means")
    ax.grid(True, axis="y", color="0.9")
    _save(fig, path)


def fig_model_check(frames: list[pd.DataFrame], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    mk = ["o", "s", "^", "D"]
    for f, m, lab in zip(frames, mk, ["Scaling", "Gain map", "Ablation", "Robustness"]):
        ax.scatter(f["m80_pred"], f["m80_mc"], marker=m, facecolor="none" if m in "os" else "0.4", edgecolor="black", s=22, label=lab)
    lo = min(f["m80_pred"].min() for f in frames) * 0.5
    hi = max(f["m80_pred"].replace(np.inf, np.nan).max() for f in frames) * 2
    ax.plot([lo, hi], [lo, hi], color="black", lw=1, ls="--", label="1 : 1")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel("Analytic prediction of pulse budget")
    ax.set_ylabel("Monte Carlo pulse budget")
    ax.set_title("Analytic budget vs Monte Carlo")
    ax.grid(True, which="both", color="0.9"); ax.legend(fontsize=8, frameon=False)
    _save(fig, path)
