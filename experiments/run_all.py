"""Reproduce every result and figure: ``python experiments/run_all.py`` (add ``--quick`` for a smoke run)."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gatedg2 import plots, report, studies  # noqa: E402


def _fit_slope(df, method, mode):
    d = df[(df.method == method) & (df.background == mode)].groupby("n_emit").m80_mc.mean()
    s, c = np.polyfit(np.log(d.index.values.astype(float)), np.log(d.values), 1)
    return float(s)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="small smoke run (< 1 minute)")
    ap.add_argument("--out", default=None, help="output root (default: repository root)")
    a = ap.parse_args()
    out = Path(a.out) if a.out else ROOT
    res, fig = out / "results", out / "figures"
    res.mkdir(parents=True, exist_ok=True); fig.mkdir(parents=True, exist_ok=True)
    b = studies.Budget(seeds=2 if a.quick else 5, reps=80 if a.quick else 300, quick=a.quick,
                       rep_null=300 if a.quick else 2000)
    t0 = time.time()

    def tick(name):
        print(f"[{time.time() - t0:6.1f}s] {name}", flush=True)

    scaling = studies.study_scaling(b); scaling.to_csv(res / "scaling.csv", index=False); tick("scaling")
    gain = studies.study_gain_map(b); gain.to_csv(res / "gain_map.csv", index=False); tick("gain map")
    abl = studies.study_ablation(b); abl.to_csv(res / "ablation.csv", index=False); tick("ablation")
    xt = studies.study_crosstalk(b); xt.to_csv(res / "crosstalk.csv", index=False); tick("crosstalk")
    thr = studies.crosstalk_threshold(b); (res / "crosstalk_threshold.json").write_text(json.dumps(thr, indent=2))
    life = studies.study_lifetime(b); life.to_csv(res / "lifetime_mismatch.csv", index=False); tick("lifetime")
    det = studies.study_detection_probability(b); det.to_csv(res / "detection_probability.csv", index=False); tick("q sweep")
    null, zs = studies.study_null(b); null.to_csv(res / "null_calibration.csv", index=False); tick("null")
    val = studies.study_validation(b); val.to_csv(res / "timetag_validation.csv", index=False); tick("validation")

    plots.fig_scaling(scaling, fig / "fig1_scaling.png")
    plots.fig_gain_map(gain, fig / "fig2_gain_map.png")
    plots.fig_ablation(abl, fig / "fig3_ablation.png")
    plots.fig_robustness(xt, life, fig / "fig4_robustness.png")
    plots.fig_null(zs, fig / "fig5_null_calibration.png")
    gain2 = gain.rename(columns={"m80_pred_gated": "m80_pred", "m80_gated": "m80_mc"})
    plots.fig_model_check([scaling, gain2, abl, xt.replace(np.inf, np.nan).dropna()],
                          fig / "fig6_model_check.png")
    tick("figures")

    summary = {
        "quick": a.quick, "seeds": b.seeds, "reps": b.reps,
        "scaling_loglog_slope": {mode: {m: _fit_slope(scaling, m, mode) for m in scaling.method.unique()}
                                 for mode in ("fixed", "proportional")},
        "crosstalk_threshold": thr,
        "runtime_s": round(time.time() - t0, 1),
    }
    (res / "summary.json").write_text(json.dumps(summary, indent=2))
    report.write(res)
    tick("done")


if __name__ == "__main__":
    main()
