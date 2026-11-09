# Vertical RHEED streaks from finite rod width (domain / terrace size).
# Does not change Visulation.py — reuses the same kinematic geometry.
#
# Ideal infinitely thin rods → one eta → one point (compute_spots).
# Finite lateral coherence D → rod diameter ~ 2π/D → Ewald cuts a chord
# that projects mostly as a vertical line on the phosphor (streak).

import numpy as np

from Visulation import ANGSTROM_PER_CM, compute_spots


def compute_streaks(
    a=3.61,
    Volt=10000,
    angle_razante=2.5,
    phi_deg=45.0,
    L_cm=30.0,
    h_max=10,
    D_A=80.0,
    n_beam=17,
    n_side=5,
):
    """
    Same inputs as compute_spots, plus:
      D_A: average domain/terrace size (Angstrom). Larger D → thinner rods → shorter streaks.
      n_beam, n_side: samples of Delta-G along beam (t) and across (v).

    Returns centers from compute_spots plus one polyline per (h,k) streak.
    """
    centers = compute_spots(
        a=a,
        Volt=Volt,
        angle_razante=angle_razante,
        phi_deg=phi_deg,
        L_cm=L_cm,
        h_max=h_max,
    )

    # Rebuild lattice / beam (same as Visulation) so streaks stay consistent
    a1 = 0.5 * a * np.array([1.0, 1.0, 0.0])
    a2 = 0.5 * a * np.array([-1.0, 1.0, 0.0])
    n = np.array([0.0, 0.0, 1.0])
    A = np.dot(a1, np.cross(a2, n))
    a_recip = 2 * np.pi * np.cross(a2, n) / A
    b_recip = 2 * np.pi * np.cross(n, a1) / A

    lambda_e = 12.3 / np.sqrt(Volt * (1 + Volt * 1.95e-6))
    ki = 2 * np.pi / lambda_e
    theta = angle_razante * (np.pi / 180)
    phi_rad = phi_deg * (np.pi / 180)
    t = np.array([np.cos(phi_rad), np.sin(phi_rad), 0.0])
    v_hat = np.cross(t, n)
    ki_par = ki * np.cos(theta) * t
    L = L_cm * ANGSTROM_PER_CM

    # Rod half-width in reciprocal space (Angstrom^-1)
    delta_G = 2.0 * np.pi / max(D_A, 1.0)

    streaks = []
    for spot in centers["spots"]:
        h, k = spot["h"], spot["k"]
        G0 = h * a_recip + k * b_recip
        pts = []

        for eps_t in np.linspace(-delta_G, delta_G, n_beam):
            for eps_v in np.linspace(-0.35 * delta_G, 0.35 * delta_G, n_side):
                G = G0 + eps_t * t + eps_v * v_hat
                eta2 = (ki * np.sin(theta)) ** 2 + 2.0 * np.dot(ki_par, G) - np.dot(G, G)
                if eta2 < 0.0:
                    continue
                eta = np.sqrt(eta2)
                k_prime = ki_par - G + eta * n
                denom = np.dot(k_prime, t)
                if denom <= 0.0:
                    continue
                r = L * k_prime / denom
                v_cm = float(np.dot(r, v_hat) / ANGSTROM_PER_CM)
                z_cm = float(np.dot(r, n) / ANGSTROM_PER_CM)
                if z_cm < 0.0:
                    continue
                pts.append((v_cm, z_cm))

        if not pts:
            continue

        # Sort along z so the UI can draw a continuous vertical-ish polyline
        pts = sorted(pts, key=lambda p: p[1])
        vs = [p[0] for p in pts]
        zs = [p[1] for p in pts]
        streaks.append(
            {
                "h": h,
                "k": k,
                "specular": spot["specular"],
                "v_cm": spot["v_cm"],
                "z_cm": spot["z_cm"],
                "points": pts,
                "v_min": float(min(vs)),
                "v_max": float(max(vs)),
                "z_min": float(min(zs)),
                "z_max": float(max(zs)),
            }
        )

    return {
        **centers,
        "streaks": streaks,
        "D_A": D_A,
        "delta_G": float(delta_G),
        "n_streaks": len(streaks),
    }


if __name__ == "__main__":
    data = compute_streaks(D_A=80.0)
    print("n_streaks", data["n_streaks"], "delta_G", data["delta_G"])
    for s in data["streaks"][:5]:
        print(s["h"], s["k"], "z:", round(s["z_min"], 3), "->", round(s["z_max"], 3), "cm")
