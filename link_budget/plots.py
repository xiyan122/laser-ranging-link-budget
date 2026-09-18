"""Three required trade-off figures (task book A-1)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .budget import sweep_aperture, sweep_distance, sweep_filter_bandwidth

# Compact scientific style
plt.rcParams.update(
    {
        "figure.dpi": 140,
        "savefig.dpi": 160,
        "font.size": 10,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "legend.fontsize": 9,
        "figure.facecolor": "white",
    }
)


def _annotate_snr_threshold(ax, snr: np.ndarray, x: np.ndarray, threshold: float = 1.0) -> None:
    """Mark where SNR crosses threshold (first crossing from above)."""
    idx = np.where(snr <= threshold)[0]
    if len(idx) == 0:
        return
    i = int(idx[0])
    if i == 0:
        return
    ax.axvline(x[i], color="crimson", ls="--", lw=1, alpha=0.8)
    ax.axhline(threshold, color="crimson", ls=":", lw=1, alpha=0.6)
    ax.annotate(
        f"SNR=1 @ {x[i]:.3g}",
        xy=(x[i], threshold),
        xytext=(x[i], threshold * 3),
        fontsize=8,
        color="crimson",
        ha="left",
    )


def plot_snr_vs_range(out_dir: Path, alpha_per_km: float = 0.1, d_r: float = 0.10) -> Path:
    distances = np.linspace(500, 10000, 200)
    data = sweep_distance(distances, alpha_per_km=alpha_per_km, d_r=d_r)

    fig, ax1 = plt.subplots(figsize=(7.2, 4.4))
    ax1.semilogy(data["distance_m"] / 1e3, data["snr"], "b-", lw=1.8, label=f"SNR (D_r={d_r*100:.0f} cm, α={alpha_per_km}/km)")
    _annotate_snr_threshold(ax1, data["snr"], data["distance_m"] / 1e3, 1.0)
    ax1.set_xlabel("Range R (km)")
    ax1.set_ylabel("SNR (shot-noise limited)")
    ax1.set_title("Task A Fig.1 — SNR vs Range (Gaussian beam + atmosphere)")

    ax2 = ax1.twinx()
    ax2.semilogy(data["distance_m"] / 1e3, data["p_r"], "g--", lw=1.4, label="P_r")
    ax2.set_ylabel("Received power P_r (W)", color="g")
    ax2.tick_params(axis="y", labelcolor="g")
    ax2.grid(False)

    ax1.legend(loc="upper right")
    fig.tight_layout()
    path = out_dir / "fig1_snr_vs_range.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_snr_vs_aperture(out_dir: Path, alpha_per_km: float = 0.1, distance: float = 5000.0) -> Path:
    diameters = np.linspace(0.05, 0.30, 60)
    data = sweep_aperture(diameters, alpha_per_km=alpha_per_km, distance=distance)

    fig, ax1 = plt.subplots(figsize=(7.2, 4.4))
    ax1.plot(data["diameter_m"] * 100, data["snr"], "b-", lw=1.8, label="SNR")
    # Reference: background-limited scaling SNR ∝ D_r  (i_s∝A_r, i_bg∝A_r → SNR∝√A_r∝D)
    snr0 = data["snr"][0]
    d0 = data["diameter_m"][0]
    snr_sqrt = snr0 * (data["diameter_m"] / d0)  # BLIP: ∝ D
    snr_lin = snr0 * (data["diameter_m"] / d0) ** 2  # dark/signal-only idealized ∝ A_r∝D^2
    ax1.plot(data["diameter_m"] * 100, snr_sqrt, "k:", lw=1.2, label="∝ D_r (background-limited)")
    ax1.plot(data["diameter_m"] * 100, snr_lin, "m:", lw=1.2, label="∝ D_r² (dark-limited ideal)")
    ax1.set_xlabel("Receiver aperture D_r (cm)")
    ax1.set_ylabel("SNR")
    ax1.set_title(
        f"Task A Fig.2 — Aperture–SNR Trade-off @ R={distance/1000:.1f} km, α={alpha_per_km}/km"
    )

    ax2 = ax1.twinx()
    ax2.plot(data["diameter_m"] * 100, data["p_bg"] * 1e9, "r--", lw=1.2, label="P_bg")
    ax2.set_ylabel("Background power P_bg (nW)", color="r")
    ax2.tick_params(axis="y", labelcolor="r")
    ax2.grid(False)

    ax1.legend(loc="upper left")
    fig.tight_layout()
    path = out_dir / "fig2_snr_vs_aperture.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_background_vs_bandwidth(out_dir: Path, alpha_per_km: float = 0.1, d_r: float = 0.10) -> Path:
    dlam = np.linspace(0.1, 20.0, 80)  # nm
    data = sweep_filter_bandwidth(dlam, alpha_per_km=alpha_per_km, d_r=d_r)

    fig, ax1 = plt.subplots(figsize=(7.2, 4.4))
    ax1.semilogy(data["delta_lambda_nm"], data["p_bg"] * 1e9, "r-", lw=1.8, label="P_bg")
    ax1.set_xlabel("Optical filter bandwidth Δλ (nm)")
    ax1.set_ylabel("Background power P_bg (nW)", color="r")
    ax1.tick_params(axis="y", labelcolor="r")
    ax1.set_title("Task A Fig.3 — Background Noise vs Filter Bandwidth")

    ax2 = ax1.twinx()
    ax2.plot(data["delta_lambda_nm"], data["snr"], "b-", lw=1.8, label="SNR")
    ax2.set_ylabel("SNR (signal fixed on laser line)", color="b")
    ax2.tick_params(axis="y", labelcolor="b")
    ax2.grid(False)

    # Mark typical narrowband filter (1 nm)
    ax1.axvline(1.0, color="gray", ls="--", lw=1, alpha=0.7)
    ax1.annotate(
        "1 nm narrowband (standard)",
        xy=(1.0, data["p_bg"].max() * 0.3 * 1e9),
        fontsize=8,
        rotation=90,
        va="top",
        color="gray",
    )

    ax1.legend(loc="upper left")
    fig.tight_layout()
    path = out_dir / "fig3_background_vs_bandwidth.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def generate_all(out_dir: Path, alpha_per_km: float = 0.1) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        plot_snr_vs_range(out_dir, alpha_per_km=alpha_per_km),
        plot_snr_vs_aperture(out_dir, alpha_per_km=alpha_per_km),
        plot_background_vs_bandwidth(out_dir, alpha_per_km=alpha_per_km),
    ]
    return paths
