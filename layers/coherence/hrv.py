"""
Heart-rate variability (HRV) coherence engine.
Computes HRV coherence ratio via PSD (Welch's method) and detects
optimal breathing rate (~0.1 Hz respiratory sinus arrhythmia).
"""

from typing import List

import numpy as np
from scipy.signal import welch


class HRVEngine:
    """HRV coherence monitor — maps biophysical rhythm to system coherence."""

    MAX_BUFFER = 300

    def __init__(self) -> None:
        self.rr_intervals: List[float] = []

    # ------------------------------------------------------------------
    # Data ingestion
    # ------------------------------------------------------------------

    def add_interval(self, rr_ms: float) -> None:
        """Append an RR interval (milliseconds) to the buffer."""
        self.rr_intervals.append(rr_ms)
        if len(self.rr_intervals) > self.MAX_BUFFER:
            self.rr_intervals = self.rr_intervals[-self.MAX_BUFFER:]

    # ------------------------------------------------------------------
    # Spectral analysis
    # ------------------------------------------------------------------

    def _psd(self) -> tuple:
        """Return (frequencies, power) via Welch's method on the RR series."""
        if len(self.rr_intervals) < 8:
            return np.array([]), np.array([])
        rr = np.array(self.rr_intervals)
        fs = 1000.0 / np.mean(rr)  # approximate sampling frequency in Hz
        nperseg = min(len(rr), 256)
        freqs, power = welch(rr, fs=fs, nperseg=nperseg)
        return freqs, power

    def coherence_ratio(self) -> float:
        """Power in 0.04-0.15 Hz band / total power. Returns 0.0-1.0."""
        freqs, power = self._psd()
        if len(freqs) == 0:
            return 0.0
        total = float(np.sum(power))
        if total == 0.0:
            return 0.0
        mask = (freqs >= 0.04) & (freqs <= 0.15)
        band_power = float(np.sum(power[mask]))
        return min(1.0, max(0.0, band_power / total))

    def breathing_rate_hz(self) -> float:
        """Peak frequency in 0.1-0.4 Hz band (respiratory sinus arrhythmia)."""
        freqs, power = self._psd()
        if len(freqs) == 0:
            return 0.0
        mask = (freqs >= 0.1) & (freqs <= 0.4)
        if not np.any(mask):
            return 0.0
        peak_idx = np.argmax(power[mask])
        return float(freqs[mask][peak_idx])

    def is_optimal(self) -> bool:
        """True if breathing rate ~ 0.1 Hz (+/- 0.02) AND coherence > 0.7."""
        br = self.breathing_rate_hz()
        return abs(br - 0.1) <= 0.02 and self.coherence_ratio() > 0.7

    # ------------------------------------------------------------------
    # Testing helper
    # ------------------------------------------------------------------

    def simulate_rr(self, n: int = 60) -> List[float]:
        """Generate synthetic RR intervals for testing.

        Gaussian noise around 800 ms mean, std 50 ms.
        """
        rng = np.random.default_rng()
        intervals = rng.normal(loc=800.0, scale=50.0, size=n).tolist()
        for rr in intervals:
            self.add_interval(rr)
        return intervals
