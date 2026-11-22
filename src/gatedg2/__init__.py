"""gatedg2: photon budget of time-gated second-order correlation tests for emitter ensembles."""
from .config import Scenario
from .timing import exgauss_cdf, gate_fractions, full_window
from .statemodel import state_pmf, g2_expected, predicted_pulses
from .gate import optimise_gate
from .certify import mc_power, mc_m80

__all__ = [
    "Scenario", "exgauss_cdf", "gate_fractions", "full_window", "state_pmf",
    "g2_expected", "predicted_pulses", "optimise_gate", "mc_power", "mc_m80",
]
__version__ = "0.1.0"
