"""Smoke-check that the RHEED kinematic-model environment is ready.

This script does not implement diffraction or reconstruction maths.
It only verifies that the scientific Python stack imports and can write
a headless plot, which is the path later phosphor-screen figures will use.
"""

from __future__ import annotations

import os
import sys

os.environ.setdefault("MPLBACKEND", "Agg")


def main() -> int:
    import numpy as np
    import scipy
    import sympy as sp
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd
    import ipykernel
    from PIL import Image

    versions = {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "sympy": sp.__version__,
        "matplotlib": matplotlib.__version__,
        "pandas": pd.__version__,
        "ipykernel": ipykernel.__version__,
        "pillow": getattr(Image, "__version__", "ok"),
        "backend": matplotlib.get_backend(),
    }

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.set_facecolor("black")
    ax.plot([0.0, 1.0], [0.0, 1.0], color="lime", linewidth=1.0)
    ax.set_title("RHEED env smoke")
    smoke_path = "/tmp/rheed_env_smoke.png"
    fig.savefig(smoke_path, dpi=80)
    plt.close(fig)

    if not os.path.isfile(smoke_path) or os.path.getsize(smoke_path) == 0:
        print("RHEED environment check failed: smoke plot was not written", file=sys.stderr)
        return 1

    print("RHEED environment OK")
    for name, value in versions.items():
        print(f"  {name}: {value}")
    print(f"  smoke_plot: {smoke_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
