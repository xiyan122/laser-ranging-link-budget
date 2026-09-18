"""CLI entry: python link_budget.py  (or python run_link_budget.py)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as script from project root
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from link_budget import link_budget_from_defaults  # noqa: E402
from link_budget.formulas import alpha_per_km_to_visibility  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Laser ranging link budget: P_r and SNR from textbook models."
    )
    p.add_argument("--p-t", type=float, default=2.0, help="Transmit peak power [W]")
    p.add_argument("--d-r", type=float, default=0.10, help="Receiver diameter [m]")
    p.add_argument("--R", type=float, default=5000.0, help="Range [m]")
    p.add_argument("--alpha", type=float, default=0.1, help="Atmospheric extinction [/km]")
    p.add_argument("--w0", type=float, default=3e-3, help="Beam waist radius [m]")
    p.add_argument("--rho", type=float, default=0.1, help="Target reflectance")
    p.add_argument("--dlam-nm", type=float, default=1.0, help="Filter bandwidth [nm]")
    p.add_argument("--apd", action="store_true", help="Enable APD excess-noise (F=4)")
    p.add_argument("--plots", action="store_true", help="Also regenerate the three figures")
    p.add_argument("--out", type=str, default="figures", help="Output dir for figures")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    F_apd = 4.0 if args.apd else 1.0
    result = link_budget_from_defaults(
        alpha_per_km=args.alpha,
        d_r=args.d_r,
        distance=args.R,
        p_t=args.p_t,
        w0=args.w0,
        rho=args.rho,
        delta_lambda=args.dlam_nm * 1e-9,
        excess_noise_factor=F_apd,
    )
    print(result.summary())
    vis = alpha_per_km_to_visibility(args.alpha)
    print(f"\nKoschmieder visibility (approx) ≈ {vis:.0f} m ({vis/1000:.1f} km) at λ=1064 nm")
    print(f"Airy radius λf/D ≈ N/A here — see Task C for imaging case.")

    if args.plots:
        from link_budget.plots import generate_all

        out = Path(args.out)
        if not out.is_absolute():
            out = ROOT / out
        paths = generate_all(out, alpha_per_km=args.alpha)
        print("\nFigures written:")
        for p in paths:
            print(f"  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
