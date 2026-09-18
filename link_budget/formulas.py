"""Public textbook formulas for laser ranging link budget.

References
----------
[1] Saleh & Teich, Fundamentals of Photonics (Gaussian beams; photodetection noise).
[2] Typical Chinese lidar textbooks, link-budget chapters (propagation + ranging).
All quantities are SI unless noted. Units appear in each docstring.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

# Physical constants
E_CHARGE = 1.6e-19  # C


def rayleigh_range(w0: float, wavelength: float) -> float:
    """zR = pi * w0^2 / lambda  [m].  w0: beam waist radius [m]."""
    return math.pi * w0**2 / wavelength


def divergence_half_angle(w0: float, wavelength: float) -> float:
    """theta = lambda / (pi * w0)  [rad], far-field half-angle."""
    return wavelength / (math.pi * w0)


def beam_radius(z: float, w0: float, wavelength: float) -> float:
    """w(z) = w0 * sqrt(1 + (z/zR)^2)  [m].  z: distance from waist [m]."""
    zr = rayleigh_range(w0, wavelength)
    return w0 * math.sqrt(1.0 + (z / zr) ** 2)


def aperture_area(diameter: float) -> float:
    """A_r = pi * (D_r/2)^2  [m^2]."""
    return math.pi * (diameter / 2.0) ** 2


def geometric_capture(d_r: float, w_at_r: float) -> float:
    """eta_geo = A_r / (pi * w(R)^2): receiver share of the footprint."""
    a_r = aperture_area(d_r)
    footprint = math.pi * w_at_r**2
    return a_r / footprint


def atmospheric_transmittance(alpha: float, distance: float) -> float:
    """tau_atm = exp(-alpha * R): one-way.  Ranging uses tau_atm^2."""
    return math.exp(-alpha * distance)


def receiver_power(
    p_t: float,
    eta_tx: float,
    eta_geo: float,
    rho: float,
    tau_atm: float,
    tau_rx: float,
) -> float:
    """P_r = P_t * eta_tx * eta_geo * rho * tau_atm^2 * tau_rx  [W]."""
    return p_t * eta_tx * eta_geo * rho * (tau_atm**2) * tau_rx


def fov_solid_angle(theta_fov: float) -> float:
    """Omega_FOV = pi * (theta_FOV/2)^2  [sr], theta_fov in rad."""
    return math.pi * (theta_fov / 2.0) ** 2


def background_power(
    l_sun: float,
    a_r: float,
    omega_fov: float,
    delta_lambda: float,
    tau_rx: float,
) -> float:
    """P_bg = L_sun * A_r * Omega_FOV * Delta_lambda * tau_rx  [W]."""
    return l_sun * a_r * omega_fov * delta_lambda * tau_rx


def photocurrent(responsivity: float, optical_power: float) -> float:
    """i = R_lambda * P  [A]."""
    return responsivity * optical_power


def shot_noise_current(
    i_s: float,
    i_bg: float,
    i_d: float,
    bandwidth: float,
) -> float:
    """i_noise = sqrt(2 e (i_s + i_bg + i_d) B)  [A], shot-noise limited."""
    return math.sqrt(2.0 * E_CHARGE * (i_s + i_bg + i_d) * bandwidth)


def snr_shot(i_s: float, i_noise: float, excess_noise_factor: float = 1.0) -> float:
    """SNR = i_s / (i_noise * sqrt(F)).  F=1 for PIN; F>1 for APD."""
    return i_s / (i_noise * math.sqrt(excess_noise_factor))


def visibility_to_alpha(visibility_m: float, wavelength_m: float = 1064e-9) -> float:
    """Koschmieder: alpha [1/m] ≈ 3.912 / V * (lambda/550nm)^(-q), q≈1.3.

    Returns extinction coefficient in 1/m for use in exp(-alpha*R).
    """
    # q≈1.3 classic; lambda in nm for the ratio
    lam_nm = wavelength_m * 1e9
    q = 1.3
    alpha_m = (3.912 / visibility_m) * (lam_nm / 550.0) ** (-q)
    return alpha_m


def alpha_per_km_to_visibility(alpha_per_km: float, wavelength_m: float = 1064e-9) -> float:
    """Invert Koschmieder for documentation / interview tables. V in meters."""
    alpha_m = alpha_per_km / 1000.0  # /km -> /m
    lam_nm = wavelength_m * 1e9
    q = 1.3
    # alpha = 3.912/V * (lam/550)^(-q)  =>  V = 3.912/alpha * (lam/550)^(-q)
    return (3.912 / alpha_m) * (lam_nm / 550.0) ** (-q)


@dataclass(frozen=True)
class DefaultParams:
    """Typical open-literature magnitudes (see task book A-4). Generic only."""

    p_t: float = 2.0  # W, peak
    w0: float = 3e-3  # m
    wavelength: float = 1064e-9  # m
    d_r: float = 0.10  # m
    distance: float = 5000.0  # m
    alpha: float = 0.1  # 1/m  -- note: table says 0.1~1.0 /km; convert below
    rho: float = 0.1
    delta_lambda: float = 1e-9  # m
    l_sun: float = 0.05  # W/(m^2 sr nm)
    theta_fov: float = 0.5e-3  # rad
    responsivity: float = 0.4  # A/W
    i_d: float = 10e-9  # A
    bandwidth: float = 10e6  # Hz
    eta_tx: float = 0.8
    tau_rx: float = 0.7
    excess_noise_factor: float = 1.0  # set ~4 for APD demo


def default_params(alpha_per_km: float = 0.1, d_r: float = 0.10, distance: float = 5000.0) -> DefaultParams:
    """Build defaults with alpha in 1/km (as in the task-book table)."""
    p = DefaultParams()
    return DefaultParams(
        p_t=p.p_t,
        w0=p.w0,
        wavelength=p.wavelength,
        d_r=d_r,
        distance=distance,
        alpha=alpha_per_km / 1000.0,  # convert /km -> /m
        rho=p.rho,
        delta_lambda=p.delta_lambda,
        l_sun=p.l_sun,
        theta_fov=p.theta_fov,
        responsivity=p.responsivity,
        i_d=p.i_d,
        bandwidth=p.bandwidth,
        eta_tx=p.eta_tx,
        tau_rx=p.tau_rx,
        excess_noise_factor=p.excess_noise_factor,
    )


def snr_array_form(
    i_s: np.ndarray,
    i_bg: np.ndarray,
    i_d: float,
    bandwidth: float,
    excess_noise_factor: float = 1.0,
) -> np.ndarray:
    """Vectorized SNR for sweeps."""
    i_noise = np.sqrt(2.0 * E_CHARGE * (i_s + i_bg + i_d) * bandwidth)
    return i_s / (i_noise * math.sqrt(excess_noise_factor))
