"""Hand-checked unit tests for textbook formulas (task book A-2 Day 1)."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from link_budget import formulas as F
from link_budget.budget import link_budget_from_defaults


class TestGaussianBeam(unittest.TestCase):
    def test_rayleigh_range(self):
        # w0=3mm, lambda=1064nm -> zR = pi*(0.003)^2/1.064e-6
        zr = F.rayleigh_range(3e-3, 1064e-9)
        expected = math.pi * (0.003) ** 2 / 1.064e-6
        self.assertAlmostEqual(zr, expected, places=9)
        self.assertAlmostEqual(zr, 26.5736, places=3)  # m

    def test_divergence(self):
        th = F.divergence_half_angle(3e-3, 1064e-9)
        self.assertAlmostEqual(th, 1064e-9 / (math.pi * 3e-3), places=12)
        self.assertAlmostEqual(th * 1e3, 0.1129, places=3)  # mrad

    def test_beam_radius_at_zr(self):
        w0 = 3e-3
        lam = 1064e-9
        zr = F.rayleigh_range(w0, lam)
        w = F.beam_radius(zr, w0, lam)
        self.assertAlmostEqual(w, w0 * math.sqrt(2), places=12)

    def test_beam_radius_at_zero(self):
        self.assertAlmostEqual(F.beam_radius(0.0, 2e-3, 1e-6), 2e-3, places=12)


class TestApertureAndCapture(unittest.TestCase):
    def test_aperture_area(self):
        a = F.aperture_area(0.10)
        self.assertAlmostEqual(a, math.pi * 0.05**2, places=12)
        self.assertAlmostEqual(a * 1e4, math.pi * 25, places=6)  # cm^2

    def test_eta_geo_bounds(self):
        # If receiver equals footprint, eta=1
        w = 0.05
        eta = F.geometric_capture(2 * w, w)
        self.assertAlmostEqual(eta, 1.0, places=12)
        eta_small = F.geometric_capture(0.02, w)
        self.assertLess(eta_small, 1.0)
        self.assertGreater(eta_small, 0.0)


class TestAtmosphere(unittest.TestCase):
    def test_transmittance(self):
        # alpha=0.1/km = 1e-4 /m, R=5 km -> exp(-0.5)
        tau = F.atmospheric_transmittance(1e-4, 5000.0)
        self.assertAlmostEqual(tau, math.exp(-0.5), places=12)

    def test_koschmieder_roundtrip(self):
        v = 10000.0  # 10 km visibility
        alpha = F.visibility_to_alpha(v)
        v2 = F.alpha_per_km_to_visibility(alpha * 1000.0)
        self.assertAlmostEqual(v2, v, delta=1.0)


class TestBackgroundAndSNR(unittest.TestCase):
    def test_omega_fov(self):
        omega = F.fov_solid_angle(1e-3)
        self.assertAlmostEqual(omega, math.pi * (0.5e-3) ** 2, places=15)

    def test_background_linear_in_bandwidth(self):
        p1 = F.background_power(0.05, 0.01, 1e-6, 1.0, 0.7)
        p2 = F.background_power(0.05, 0.01, 1e-6, 2.0, 0.7)
        self.assertAlmostEqual(p2 / p1, 2.0, places=12)

    def test_shot_noise_and_snr(self):
        i_s, i_bg, i_d, B = 1e-6, 1e-7, 1e-8, 1e7
        n = F.shot_noise_current(i_s, i_bg, i_d, B)
        expected = math.sqrt(2 * 1.6e-19 * (i_s + i_bg + i_d) * B)
        self.assertAlmostEqual(n, expected, places=15)
        snr = F.snr_shot(i_s, n)
        self.assertAlmostEqual(snr, i_s / n, places=12)
        snr_apd = F.snr_shot(i_s, n, excess_noise_factor=4.0)
        self.assertAlmostEqual(snr_apd, snr / 2.0, places=12)

    def test_snr_decreases_with_range(self):
        r_near = link_budget_from_defaults(distance=2000.0)
        r_far = link_budget_from_defaults(distance=8000.0)
        self.assertGreater(r_near.snr, r_far.snr)
        self.assertGreater(r_near.p_r, r_far.p_r)

    def test_snr_increases_with_aperture_bg_limited(self):
        # Background-dominated day scene: larger D raises SNR (roughly ∝ D)
        a_small = link_budget_from_defaults(d_r=0.05, distance=5000.0)
        a_large = link_budget_from_defaults(d_r=0.20, distance=5000.0)
        self.assertGreater(a_large.snr, a_small.snr)
        # P_bg grows linearly with A_r ∝ D^2
        ratio_d2 = (0.20 / 0.05) ** 2
        self.assertAlmostEqual(a_large.p_bg / a_small.p_bg, ratio_d2, places=6)

    def test_narrowband_reduces_background(self):
        wide = link_budget_from_defaults(delta_lambda=10e-9, distance=5000.0)
        narrow = link_budget_from_defaults(delta_lambda=1e-9, distance=5000.0)
        self.assertAlmostEqual(wide.p_bg / narrow.p_bg, 10.0, places=6)
        self.assertGreater(narrow.snr, wide.snr)


class TestTypicalCase(unittest.TestCase):
    def test_daylight_5km_order_of_magnitude(self):
        r = link_budget_from_defaults(alpha_per_km=0.1, d_r=0.10, distance=5000.0)
        self.assertGreater(r.p_r, 0.0)
        self.assertGreater(r.snr, 0.0)
        # Sanity: at 5 km, clear-ish air, 10 cm aperture — SNR should not be absurd
        self.assertLess(r.snr, 1e8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
