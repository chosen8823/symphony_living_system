import numpy as np


class KuramotoEngine:
    def __init__(self, n_oscillators: int = 12, K: float = 0.5):
        self.n = n_oscillators
        self.K = K
        self.phases = np.random.uniform(0, 2 * np.pi, n_oscillators)
        self.freqs = np.random.normal(1.0, 0.1, n_oscillators)

    def step(self, dt: float = 0.01) -> float:
        """Returns order parameter r (coherence level)."""
        dtheta = self.freqs + (self.K / self.n) * np.sum(
            np.sin(self.phases[:, None] - self.phases[None, :]), axis=1
        )
        self.phases += dtheta * dt
        r = float(np.abs(np.mean(np.exp(1j * self.phases))))
        # adaptive K: increases as coherence improves
        self.K += 0.01 * r
        return r

    def order_parameter(self) -> float:
        return float(np.abs(np.mean(np.exp(1j * self.phases))))
