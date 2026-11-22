"""Scenario description: emitters, background, detector timing and crosstalk."""
from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Scenario:
    """Pulsed-excitation photon-correlation scenario.

    Times are in nanoseconds. Per excitation pulse each of ``n_emit`` emitters
    contributes at most one detected photon with probability ``q`` (excitation
    probability times collection-and-detection efficiency). Background photons
    are Poisson distributed with mean ``rho * n_emit * q`` per pulse (before any
    time gate) and are a mixture of a prompt component (scattered or leaked
    excitation, Gaussian instrument response), a slow autofluorescence
    component (exponential decay ``tau_a``) and a flat component (dark counts,
    stray light).
    """

    n_emit: int = 3
    q: float = 2e-3
    rho: float = 2.0
    tau_s: float = 3.0
    tau_a: float = 1.5
    w_prompt: float = 0.4
    w_auto: float = 0.4
    w_flat: float = 0.2
    sigma: float = 0.2
    period: float = 25.0
    chi: float = 0.0
    beta_override: float | None = None

    def __post_init__(self) -> None:
        total = self.w_prompt + self.w_auto + self.w_flat
        if abs(total - 1.0) > 1e-9:
            raise ValueError("background weights must sum to one")

    @property
    def beta0(self) -> float:
        """Mean background photons per pulse before gating."""
        if self.beta_override is not None:
            return self.beta_override
        return self.rho * self.n_emit * self.q

    def with_(self, **kw) -> "Scenario":
        """Return a modified copy."""
        return replace(self, **kw)
