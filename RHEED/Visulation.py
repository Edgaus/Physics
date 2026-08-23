# This code is to simulate RHEED, using kinematic theory.
# Physics only — the phosphor UI lives in UI_RHEED.py

import numpy as np

ANGSTROM_PER_CM = 1.0e8


def compute_spots(
    a=3.61,
    Volt=10000,
    angle_razante=2.5,
    phi_deg=45.0,
    L_cm=30.0,
    h_max=10,
):
    """
    Allowed (h,k) rods → phosphor coordinates (v, z) in cm.

    Crystal FCC / zinc-blende (001) is fixed. Beam + screen rotate with phi.
    Returns dict with spots, eta_array, v_array, z_array, and metadata.
    """
    # --- real / reciprocal surface net (FCC(001) primitives) ---
    a1 = 0.5 * a * np.array([1.0, 1.0, 0.0])
    a2 = 0.5 * a * np.array([-1.0, 1.0, 0.0])
    n = np.array([0.0, 0.0, 1.0])

    A = np.dot(a1, np.cross(a2, n))  # a^2 / 2
    a_recip = 2 * np.pi * np.cross(a2, n) / A
    b_recip = 2 * np.pi * np.cross(n, a1) / A

    # --- electron wavevector (lambda in Angstroms, Mahan form) ---
    lambda_e = 12.3 / np.sqrt(Volt * (1 + Volt * 1.95e-6))
    ki = 2 * np.pi / lambda_e

    theta = angle_razante * (np.pi / 180)
    phi_rad = phi_deg * (np.pi / 180)

    # beam and screen co-rotate: k_parallel || t
    t = np.array([np.cos(phi_rad), np.sin(phi_rad), 0.0])
    v_hat = np.cross(t, n)

    ki_par = ki * np.cos(theta) * t
    L = L_cm * ANGSTROM_PER_CM

    eta_array = []
    v_array = []
    z_array = []
    spots = []

    for h in range(-h_max, h_max + 1):
        for k in range(-h_max, h_max + 1):
            G_hk = h * a_recip + k * b_recip
            eta2 = (ki * np.sin(theta)) ** 2 + 2.0 * np.dot(ki_par, G_hk) - np.dot(G_hk, G_hk)

            if eta2 < 0.0:
                continue

            eta = np.sqrt(eta2)
            eta_array.append([h, k, eta])

            k_hk = ki_par - G_hk + eta * n

            if np.dot(k_hk, t) <= 0:
                continue

            r_k = L * k_hk / np.dot(k_hk, t)
            v_cm = float(np.dot(r_k, v_hat) / ANGSTROM_PER_CM)
            z_cm = float(np.dot(r_k, n) / ANGSTROM_PER_CM)

            v_array.append(v_cm)
            z_array.append(z_cm)
            spots.append(
                {
                    "h": h,
                    "k": k,
                    "v_cm": v_cm,
                    "z_cm": z_cm,
                    "eta": float(eta),
                    "specular": h == 0 and k == 0,
                }
            )

    return {
        "spots": spots,
        "eta_array": eta_array,
        "v_array": v_array,
        "z_array": z_array,
        "L_cm": L_cm,
        "theta_deg": angle_razante,
        "phi_deg": phi_deg,
        "z_specular_cm": float(L_cm * np.tan(theta)),
        "n_spots": len(spots),
    }


if __name__ == "__main__":
    # Default run: Cu(001)-like mesh, [110] azimuth (phi = 45 deg)
    data = compute_spots()
    print("n_spots =", data["n_spots"])
    print("z_specular_cm =", data["z_specular_cm"])
    for spot in data["spots"]:
        print(
            spot["h"],
            spot["k"],
            spot["eta"],
            spot["v_cm"],
            spot["z_cm"],
        )
