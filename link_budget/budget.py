"""Laser ranging link-budget pipeline: one call -> P_r and SNR."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from . import formulas as F


@dataclass
class LinkBudgetResult:
    distance_m: float
    p_r: float  # W
    p_bg: float  # W
    snr: float
    i_s: float
    i_bg: float
    i_noise: float
    eta_geo: float
    tau_atm: float
    w_at_r: float
    theta_div: float
    zr: float
    a_r: float
    omega_fov: float

    def as_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        lines = [
            "=== Laser ranging link budget ===",
            f"Distance R          = {self.distance_m:.1f} m ({self.distance_m/1000:.2f} km)",
            f"Beam radius w(R)    = {self.w_at_r*1e3:.3f} mm",
            f"Divergence half-ang = {self.theta_div*1e3:.3f} mrad",
            f"Rayleigh range zR   = {self.zr:.3f} m",
            f"Aperture area A_r   = {self.a_r*1e4:.2f} cm^2",
            f"Geometric eta_geo   = {self.eta_geo:.4e}",
            f"Atm. tau_atm(1-way) = {self.tau_atm:.4e}",
            f"FOV solid angle     = {self.omega_fov:.3e} sr",
            f"Received power P_r  = {self.p_r:.4e} W",
            f"Background P_bg     = {self.p_bg:.4e} W",
            f"Signal current i_s  = {self.i_s:.4e} A",
            f"Background current  = {self.i_bg:.4e} A",
            f"Noise current       = {self.i_noise:.4e} A",
            f"SNR                 = {self.snr:.3f} ({20*np.log10(max(self.snr,1e-30)):.1f} dB)",
        ]
        return "\n".join(lines)


def link_budget(
    p_t: float,
    w0: float,
    wavelength: float,
    d_r: float,
    distance: float,
    alpha: float,
    rho: float,
    delta_lambda: float,
    l_sun: float,
    theta_fov: float,
    responsivity: float,
    i_d: float,
    bandwidth: float,
    eta_tx: float = 0.8,
    tau_rx: float = 0.7,
    excess_noise_factor: float = 1.0,
) -> LinkBudgetResult:
    """Compute received power and shot-noise-limited SNR.

    Parameters
    ----------
    alpha : float
        Atmospheric extinction in **1/m** (task-book table uses /km — divide by 1000).
    delta_lambda : float
        Filter bandwidth in **m** (e.g. 1e-9 for 1 nm). Background model also
        expects L_sun in W/(m^2 sr nm), so convert Delta_lambda to nm internally
        for that product if needed — see notes in README.
    l_sun : float
        Solar spectral radiance in W/(m^2 · sr · nm).
    """
    # Background formula in the task book: P_bg = L_sun * A_r * Omega * Delta_lambda * tau_rx
    # with L_sun in W/(m^2 sr nm) and Delta_lambda in nm (same spectral unit).
    delta_lambda_nm = delta_lambda * 1e9

    zr = F.rayleigh_range(w0, wavelength)
    theta_div = F.divergence_half_angle(w0, wavelength)
    w_r = F.beam_radius(distance, w0, wavelength)
    a_r = F.aperture_area(d_r)
    eta_geo = F.geometric_capture(d_r, w_r)
    tau_atm = F.atmospheric_transmittance(alpha, distance)
    p_r = F.receiver_power(p_t, eta_tx, eta_geo, rho, tau_atm, tau_rx)

    omega = F.fov_solid_angle(theta_fov)
    p_bg = F.background_power(l_sun, a_r, omega, delta_lambda_nm, tau_rx)

    i_s = F.photocurrent(responsivity, p_r)
    i_bg = F.photocurrent(responsivity, p_bg)
    i_noise = F.shot_noise_current(i_s, i_bg, i_d, bandwidth)
    snr = F.snr_shot(i_s, i_noise, excess_noise_factor)

    return LinkBudgetResult(
        distance_m=distance,
        p_r=p_r,
        p_bg=p_bg,
        snr=snr,
        i_s=i_s,
        i_bg=i_bg,
        i_noise=i_noise,
        eta_geo=eta_geo,
        tau_atm=tau_atm,
        w_at_r=w_r,
        theta_div=theta_div,
        zr=zr,
        a_r=a_r,
        omega_fov=omega,
    )


def link_budget_from_defaults(
    alpha_per_km: float = 0.1,
    d_r: float = 0.10,
    distance: float = 5000.0,
    **overrides,
) -> LinkBudgetResult:
    """Convenience wrapper using the A-4 typical parameter table."""
    p = F.default_params(alpha_per_km=alpha_per_km, d_r=d_r, distance=distance)
    kw = asdict(p)
    kw.update(overrides)
    return link_budget(**kw)


def sweep_distance(
    distances_m: np.ndarray,
    alpha_per_km: float = 0.1,
    d_r: float = 0.10,
    **overrides,
) -> dict[str, np.ndarray]:
    """SNR / P_r vs range for a fixed aperture."""
    p = F.default_params(alpha_per_km=alpha_per_km, d_r=d_r)
    kw = asdict(p)
    kw.update(overrides)
    w0, wavelength = kw["w0"], kw["wavelength"]
    alpha = kw["alpha"]
    zr = F.rayleigh_range(w0, wavelength)
    a_r = F.aperture_area(kw["d_r"])
    omega = F.fov_solid_angle(kw["theta_fov"])
    p_bg = F.background_power(
        kw["l_sun"], a_r, omega, kw["delta_lambda"] * 1e9, kw["tau_rx"]
    )
    i_bg = F.photocurrent(kw["responsivity"], p_bg)

    p_r_list, snr_list, eta_list = [], [], []
    for r in distances_m:
        w_r = F.beam_radius(float(r), w0, wavelength)
        eta_geo = F.geometric_capture(kw["d_r"], w_r)
        tau = F.atmospheric_transmittance(alpha, float(r))
        p_r = F.receiver_power(
            kw["p_t"], kw["eta_tx"], eta_geo, kw["rho"], tau, kw["tau_rx"]
        )
        i_s = F.photocurrent(kw["responsivity"], p_r)
        snr = F.snr_array_form(
            np.array(i_s), np.array(i_bg), kw["i_d"], kw["bandwidth"], kw["excess_noise_factor"]
        ).item()
        p_r_list.append(p_r)
        snr_list.append(snr)
        eta_list.append(eta_geo)

    return {
        "distance_m": np.asarray(distances_m, dtype=float),
        "p_r": np.asarray(p_r_list),
        "snr": np.asarray(snr_list),
        "eta_geo": np.asarray(eta_list),
        "p_bg": np.full_like(distances_m, p_bg, dtype=float),
        "zr": zr,
    }


def sweep_aperture(
    diameters_m: np.ndarray,
    alpha_per_km: float = 0.1,
    distance: float = 5000.0,
    **overrides,
) -> dict[str, np.ndarray]:
    """SNR / P_r vs receiving aperture at fixed range.

    Teaching point: both i_s and i_bg scale with A_r under background-limited
    conditions, so SNR ~ sqrt(A_r) ~ D_r; under signal+dark limited conditions
    the gain is closer to linear in A_r.
    """
    p = F.default_params(alpha_per_km=alpha_per_km, distance=distance)
    kw = asdict(p)
    kw.update(overrides)
    w0, wavelength = kw["w0"], kw["wavelength"]
    w_r = F.beam_radius(distance, w0, wavelength)
    tau = F.atmospheric_transmittance(kw["alpha"], distance)
    omega = F.fov_solid_angle(kw["theta_fov"])

    p_r_list, snr_list, p_bg_list, i_s_list, i_bg_list = [], [], [], [], []
    for d in diameters_m:
        a_r = F.aperture_area(float(d))
        eta_geo = F.geometric_capture(float(d), w_r)
        p_r = F.receiver_power(
            kw["p_t"], kw["eta_tx"], eta_geo, kw["rho"], tau, kw["tau_rx"]
        )
        p_bg = F.background_power(
            kw["l_sun"], a_r, omega, kw["delta_lambda"] * 1e9, kw["tau_rx"]
        )
        i_s = F.photocurrent(kw["responsivity"], p_r)
        i_bg = F.photocurrent(kw["responsivity"], p_bg)
        snr = F.snr_array_form(
            np.array(i_s), np.array(i_bg), kw["i_d"], kw["bandwidth"], kw["excess_noise_factor"]
        ).item()
        p_r_list.append(p_r)
        snr_list.append(snr)
        p_bg_list.append(p_bg)
        i_s_list.append(i_s)
        i_bg_list.append(i_bg)

    return {
        "diameter_m": np.asarray(diameters_m, dtype=float),
        "p_r": np.asarray(p_r_list),
        "snr": np.asarray(snr_list),
        "p_bg": np.asarray(p_bg_list),
        "i_s": np.asarray(i_s_list),
        "i_bg": np.asarray(i_bg_list),
        "w_at_r": w_r,
        "distance_m": distance,
    }


def sweep_filter_bandwidth(
    delta_lambda_nm: np.ndarray,
    alpha_per_km: float = 0.1,
    d_r: float = 0.10,
    distance: float = 5000.0,
    **overrides,
) -> dict[str, np.ndarray]:
    """Background power vs optical filter bandwidth (signal fixed by laser line)."""
    p = F.default_params(alpha_per_km=alpha_per_km, d_r=d_r, distance=distance)
    kw = asdict(p)
    kw.update(overrides)
    w0, wavelength = kw["w0"], kw["wavelength"]
    w_r = F.beam_radius(distance, w0, wavelength)
    eta_geo = F.geometric_capture(kw["d_r"], w_r)
    tau = F.atmospheric_transmittance(kw["alpha"], distance)
    p_r = F.receiver_power(
        kw["p_t"], kw["eta_tx"], eta_geo, kw["rho"], tau, kw["tau_rx"]
    )
    a_r = F.aperture_area(kw["d_r"])
    omega = F.fov_solid_angle(kw["theta_fov"])
    i_s = F.photocurrent(kw["responsivity"], p_r)

    p_bg_list, snr_list = [], []
    for dlam_nm in delta_lambda_nm:
        p_bg = F.background_power(kw["l_sun"], a_r, omega, float(dlam_nm), kw["tau_rx"])
        i_bg = F.photocurrent(kw["responsivity"], p_bg)
        snr = F.snr_array_form(
            np.array(i_s), np.array(i_bg), kw["i_d"], kw["bandwidth"], kw["excess_noise_factor"]
        ).item()
        p_bg_list.append(p_bg)
        snr_list.append(snr)

    return {
        "delta_lambda_nm": np.asarray(delta_lambda_nm, dtype=float),
        "p_bg": np.asarray(p_bg_list),
        "snr": np.asarray(snr_list),
        "p_r": p_r,
        "i_s": i_s,
        "distance_m": distance,
        "d_r": d_r,
    }
