# RHEED cinematic / kinematic scattering conditions.
# Transcribed from Edgar's notes. No extra algebra beyond what was written.
#
# La esfera tiene radio |K|. Los rods viven en un plano que corta la esfera.
# En general la ecuación a resolver es:
#     K - K' = g_{h,k} + λ_k
# Las condiciones son que |K| = |K'|.

from __future__ import annotations

import sympy as sp

# --- Vectores (página de la esfera de Ewald) ---
K_x, K_y, K_z = sp.symbols("K_x K_y K_z", real=True)
Kp_x, Kp_y, Kp_z = sp.symbols("K'_x K'_y K'_z", real=True)
g_x, g_y, g_z = sp.symbols("g_x g_y g_z", real=True)
lam_x, lam_y, lam_z = sp.symbols("lambda_x lambda_y lambda_z", real=True)

K = sp.Matrix([K_x, K_y, K_z])
Kp = sp.Matrix([Kp_x, Kp_y, Kp_z])
g_hk = sp.Matrix([g_x, g_y, g_z])
lambda_k_vec = sp.Matrix([lam_x, lam_y, lam_z])

# K - K' = g_{h,k} + λ_k
scattering_eq = sp.Eq(K - Kp, g_hk + lambda_k_vec)

# |K| = |K'|
elastic_eq = sp.Eq(K.norm(), Kp.norm())

# |K| = |K - g_{h,k} + λ_k|
elastic_on_sphere_eq = sp.Eq(K.norm(), (K - g_hk + lambda_k_vec).norm())

# --- Expansión escalar (segunda página) ---
# [(k · k)]^{1/2} = [(k - g_{h,k} + λ_k) · (k - g_{h,k} + λ_k)]^{1/2}
k_mag = sp.Symbol("|k|", nonnegative=True)
g_mag = sp.Symbol("|g_{h,k}|", nonnegative=True)
lam_mag = sp.Symbol("|lambda_k|", nonnegative=True)
theta = sp.Symbol("theta", real=True)

lhs_sqrt = sp.sqrt(k_mag**2)
rhs_dot = K - g_hk + lambda_k_vec
# La forma escrita con el producto punto:
sqrt_dot_eq = sp.Eq(
    sp.sqrt(K.dot(K)),
    sp.sqrt(rhs_dot.dot(rhs_dot)),
)

# |k|^2 = |k|^2 - 2 |g_{h,k}| |k| cos θ + |g_{h,k}|^2 + λ_k^2
expanded_eq = sp.Eq(
    k_mag**2,
    k_mag**2 - 2 * g_mag * k_mag * sp.cos(theta) + g_mag**2 + lam_mag**2,
)

# |k|^2 se cancela en ambos lados:
# |λ_k|^2 - 2 |g_{h,k}| |k| cos θ + |g_{h,k}|^2 = 0
cancelled_eq = sp.Eq(
    lam_mag**2 - 2 * g_mag * k_mag * sp.cos(theta) + g_mag**2,
    0,
)


def cancelled_left_hand_side() -> sp.Expr:
    """Left-hand side of the last written equation, after cancelling |k|^2."""
    return cancelled_eq.lhs


if __name__ == "__main__":
    print("1. scattering")
    print("   ", scattering_eq)
    print("2. elastic")
    print("   ", elastic_eq)
    print("3. on the sphere")
    print("   ", elastic_on_sphere_eq)
    print("4. sqrt of dots")
    print("   ", sqrt_dot_eq)
    print("5. expanded (as written)")
    print("   ", expanded_eq)
    print("6. after cancelling |k|^2")
    print("   ", cancelled_eq)
    leftover = sp.simplify(expanded_eq.rhs - expanded_eq.lhs)
    print("   leftover from (5):", leftover)
    print("   leftover set to 0:", sp.Eq(leftover, 0))
