"""Generate the three required figures. Usage: python make_plots.py."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from link_budget.plots import generate_all


def main() -> int:
    out = ROOT / "figures"
    paths = generate_all(out, alpha_per_km=0.1)
    print("Figures:")
    for p in paths:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
