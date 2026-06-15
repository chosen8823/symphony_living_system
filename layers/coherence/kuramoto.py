"""
Kuramoto oscillator model — nested 8x8x8x8 grid.
Each layer uses N=8 coupled oscillators with adaptive coupling strength.
"""

import numpy as np


class KuramotoOscillator:
    """Kuramoto-model oscillator bank with adaptive coupling."""

    def __init__(self, N: int = 8, K: float = 0.5):
        self.N = N
        self.K = K
        self.phases: np.ndarray = np.random.uniform(0.0, 2.0 * np.pi, size=(N,))
        self.natural_frequencies: np.ndarray = self._lorentzian_sample(N)

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _lorentzian_sample(n: int, gamma: float = 0.5, center: float = 1.0) -> np.ndarray:
        """Draw natural frequencies from a Lorentzian (Cauchy) distribution."""
        return center + gamma * np.tan(np.pi * (np.random.uniform(size=(n,)) - 0.5))

    # ------------------------------------------------------------------
    # Dynamics
    # ------------------------------------------------------------------

    def step(self, dt: float = 0.01) -> float:
        """Advance phases by one timestep using the Kuramoto equation.

        dtheta_i/dt = omega_i + (K/N) * sum_j sin(theta_j - theta_i)

        Returns the order parameter r after the update.
        """
        coupling = np.zeros(self.N)
        for i in range(self.N):
            coupling[i] = np.sum(np.sin(self.phases - self.phases[i]))
        dtheta = self.natural_frequencies + (self.K / self.N) * coupling
        self.phases += dtheta * dt
        self.phases %= 2.0 * np.pi
        return self.order_parameter()

    def order_parameter(self) -> float:
        """Kuramoto order parameter r = |sum exp(i*theta_j)| / N."""
        return float(np.abs(np.sum(np.exp(1j * self.phases))) / self.N)

    def adapt_K(self) -> None:
        """Adaptive coupling: increase K when coherent, decrease when disordered."""
        r = self.order_parameter()
        if r > 0.8:
            self.K += 0.05
        elif r < 0.3:
            self.K = max(0.0, self.K - 0.02)
