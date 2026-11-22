# Research gap: how many pulses does it take to certify non-classical light from a few fluorescent emitters?

## State of the art (from the supplied literature)

The literature brief contains nine papers in two roles (four *recent*, five *adjacent*). It has no *landmark* or *review* role, so the baseline methods used here (the ungated Hanbury Brown–Twiss (HBT) coincidence test and a single-channel pair statistic) are standard measurement practice and are **not** attributed to any listed paper.

* Photon-correlation records can expose quantum coherence directly: Mavrogordatos (2027, Digital Object Identifier (DOI) 10.1016/j.optcom.2026.133903) read an operational coherence record from photodetection of macroscopic quantum jumps and relate current statistics to cavity field correlations.
* Detector physics sets the timing and efficiency budget: Azmoun et al. (2027, DOI 10.1016/j.nima.2026.172216) characterise a High-Rate Picosecond Photodetector (HRPPD), a pixelated microchannel-plate (MCP) device with picosecond-class timing and single-photon sensitivity, and show its gain and efficiency can be recovered under tilted magnetic fields.
* Bounded estimates are valued: Masajada et al. (2027, DOI 10.1016/j.cpc.2026.110479) release a toolkit that returns lower and upper bounds on geometric entanglement together with an estimation error.
* Single emitters are the hard case: Chen et al. (2026, DOI 10.1016/j.nanoen.2026.112511) note that chiral emission has mostly been studied at the ensemble level and that individual single-photon sources are scarce.

## Related work

| Paper | Year | Role | What it does | What it does NOT cover |
|---|---|---|---|---|
| Mavrogordatos (DOI 10.1016/j.optcom.2026.133903) | 2027 | recent | Photodetection and heterodyne/homodyne records of quantum jumps in a bistable cavity | Photon budget or false-alarm control of a certification test with background light |
| Azmoun et al. (DOI 10.1016/j.nima.2026.172216) | 2027 | recent | HRPPD gain and single-photon efficiency vs field and tilt | Correlation statistics; crosstalk between pixels as a limit on pair tests |
| Masajada et al. (DOI 10.1016/j.cpc.2026.110479) | 2027 | recent | Entanglement estimates with rigorous lower/upper bounds | Photon-counting data; finite-sample certification from detector clicks |
| Kim et al. (DOI 10.1016/j.snb.2026.141183) | 2027 | recent | Long-path terahertz time-domain spectroscopy (THz-TDS) with a detection limit across a pressure range | Quantum-light statistics; time gating of emitter vs background photons |
| Chen et al. (DOI 10.1016/j.nanoen.2026.112511) | 2026 | adjacent | Circularly polarised single-photon emission from individual perovskite quantum dots | How the antibunching dip dilutes when several emitters share the detection volume |
| Sa et al. (DOI 10.1007/s44214-026-00110-1) | 2026 | adjacent (review article) | Rare-earth-doped crystal quantum memories, coherence times, dynamical decoupling | Optical certification of the emitted light from living-cell emitters |
| Zhou et al. (DOI 10.1007/978-981-95-9514-3_21) | 2027 | adjacent | Watermarking quantum neural networks (QNNs) with grouped and paired training | Light–matter experiments; useful only as a reminder that claims need verification protocols |
| Uddin et al. (DOI 10.1016/j.nxmate.2026.103861) | 2027 | adjacent | Dual-core waveguide for mid-infrared supercontinuum | Single-photon detection or correlation tests |
| Yang et al. (DOI 10.15302/frontphys.2027.012301) | 2027 | adjacent (review article) | Enhancing on-chip stimulated Brillouin scattering (SBS) | Photon-correlation measurements |

## The gap

An experiment that measures photon correlations from fluorescent proteins expressed in living bacteria faces three facts that the papers above treat separately: (i) several emitters share the detection volume, so the antibunching dip of an ideal single emitter, measured by the second-order correlation function at zero delay, g(2)(0), is diluted to g(2)(0) = 1 − 1/N for N emitters; (ii) cells add background light (scatter, autofluorescence, stray light) that fills the dip further; and (iii) pixelated, picosecond-class detectors have finite timing jitter and some inter-pixel crosstalk. Nobody in the brief answers the practical planning question: **how many excitation pulses (a proxy for the bleaching budget of the proteins) are needed to certify, at a fixed false-alarm rate and power, that the light is non-classical, and how much of that budget can time gating of the arrival times win back?** Equally open is where the test breaks down altogether.

**Novelty (one sentence).** This project gives an exact, validated pulse-budget model for gated pair-correlation certification of an N-emitter sample with background and crosstalk, and uses it to show where time gating helps, where it does not, and which hardware imperfection is the real limit.

## Testable hypotheses and success metric

* **H1 (gating helps).** At a background-to-signal photon ratio rho ≥ 2 and detector jitter sigma ≤ 0.2 ns, an optimised arrival-time gate cuts the pulses needed for 80 % power by at least a factor 1.5 relative to the ungated two-detector HBT test.
* **H2 (gating is not free).** The gain falls to ≤ 1.1 when the background has the same time profile as the emitter, and when sigma is comparable to the emitter lifetime at low rho.
* **H3 (crosstalk is the wall).** Above a crosstalk probability chi* of order q / (4 (1 + rho)), where q is the per-emitter detection probability per pulse, the expected pair statistic exceeds one and certification is impossible at any budget.
* **H4 (emitter number).** With a fixed cell background, the budget falls with N; with a background proportional to the signal, it is flat in N.
* **Success metric.** Pulses for 80 % power at a 5 % one-sided false-alarm level (mean ± standard deviation over five seeds), plus a type-I error check under a Poisson null (target 0.05).

The hypothesis thresholds were fixed after a pilot run of the smoke-test configuration, so they are not blind predictions. Everything is a simulation at the scale of one detection volume with up to eight emitters; no real data are used, and the timing parameters are assumptions, not measurements.
